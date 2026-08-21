from datetime import datetime, timedelta
from decimal import Decimal

from app.models.enums import EstadoSesion
from app.models.models import (
    Configuracion,
    Lote,
    MapeoCIP,
    Muestreo,
    SesionDescarga,
)
from app.schemas.muestreo import MuestreoCreate, MuestreoUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload


def calcular_humedad(peso_humedo: Decimal, peso_seco: Decimal) -> Decimal:
    """Calcula el % de humedad."""
    if peso_humedo == 0:
        return Decimal("0.00")
    return ((peso_humedo - peso_seco) / peso_humedo) * Decimal("100.00")


def calcular_tms(peso_neto: Decimal, porcentaje_humedad: Decimal) -> Decimal:
    """Calcula Toneladas Métricas Secas (TMS)."""
    return peso_neto * (Decimal("1") - (porcentaje_humedad / Decimal("100.00")))


def registrar_muestreo(
    db: Session, ip_lote: str, usuario_id: int, datos: MuestreoCreate
) -> Muestreo:
    """
    Registra un intento de humedad. Valida que el % esté entre 0 y 50.
    """
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Lote {ip_lote} no encontrado."
        )

    # 1. Validar que no exista ya ese intento
    intento_previo = (
        db.query(Muestreo)
        .filter(Muestreo.lote_id == lote.id, Muestreo.intento == datos.intento)
        .first()
    )
    if intento_previo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El intento {datos.intento} ya está registrado para este lote.",
        )

    if datos.peso_seco >= datos.peso_humedo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El peso seco debe ser estrictamente menor al peso húmedo.",
        )

    # 2. Calcular humedad manualmente para validar reglas de negocio antes de guardar
    humedad = calcular_humedad(datos.peso_humedo, datos.peso_seco)
    if humedad <= 0 or humedad > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Humedad fuera de rango permitido (0-50%). Valor calculado: {humedad:.2f}%",
        )

    # 3. Obtener peso neto del lote (viene de los pesajes)
    pesaje = lote.pesajes[0] if lote.pesajes else None
    if not pesaje or not pesaje.peso_neto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El lote no tiene un peso neto válido en balanza.",
        )

    tms = calcular_tms(pesaje.peso_neto, humedad)

    # 4. Crear registro
    nuevo_muestreo = Muestreo(
        lote_id=lote.id,
        intento=datos.intento,
        peso_humedo=datos.peso_humedo,
        peso_seco=datos.peso_seco,
        tms_calculado=tms,
        observaciones=datos.observaciones,
        creado_en=datos.fecha_muestreo or datetime.now(),
        creado_por=usuario_id,
    )

    db.add(nuevo_muestreo)
    db.commit()
    db.refresh(nuevo_muestreo)

    return nuevo_muestreo


def actualizar_muestreo(
    db: Session, muestreo_id: int, usuario_id: int, datos: MuestreoUpdate
) -> Muestreo:
    """
    Actualiza un registro de humedad dentro de la ventana de 1 hora
    y solo si el lote está en estado RECEPCIONADO.
    """
    from app.models.enums import EstadoLote

    muestreo = (
        db.query(Muestreo)
        .options(joinedload(Muestreo.lote))
        .filter(Muestreo.id == muestreo_id)
        .first()
    )
    if not muestreo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Muestreo con id {muestreo_id} no encontrado.",
        )

    lote = muestreo.lote
    if lote.estado != EstadoLote.RECEPCIONADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede editar: el lote se encuentra en estado {lote.estado}.",
        )

    # Validar ventana de 1 hora
    if muestreo.creado_en:
        if datetime.now() > muestreo.creado_en + timedelta(hours=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede editar: ya expiró la ventana de 1 hora permitida.",
            )

    if datos.peso_seco >= datos.peso_humedo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El peso seco debe ser estrictamente menor al peso húmedo.",
        )

    humedad = calcular_humedad(datos.peso_humedo, datos.peso_seco)
    if humedad <= 0 or humedad > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Humedad fuera de rango permitido (0-50%). Valor calculado: {humedad:.2f}%",
        )

    pesaje = lote.pesajes[0] if lote.pesajes else None
    if not pesaje or not pesaje.peso_neto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El lote no tiene un peso neto válido en balanza.",
        )

    tms = calcular_tms(pesaje.peso_neto, humedad)

    # Actualizar valores
    muestreo.peso_humedo = datos.peso_humedo
    muestreo.peso_seco = datos.peso_seco
    muestreo.observaciones = datos.observaciones
    muestreo.tms_calculado = tms

    # Al estar usando AuditMixin, también podemos usar los campos de auditoría.
    muestreo.modificado_por = usuario_id
    muestreo.modificado_en = datetime.now()

    db.commit()
    db.refresh(muestreo)

    return muestreo


def registrar_muestreo_batch(
    db: Session, ip_lote: str, usuario_id: int, datos_list: list[MuestreoCreate]
) -> list[Muestreo]:
    """Registra múltiples intentos de muestreo en una sola transacción."""
    lote = (
        db.query(Lote)
        .options(joinedload(Lote.pesajes))
        .filter(Lote.ip == ip_lote, Lote.eliminado == False)  # noqa: E712
        .first()
    )
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Lote con IP {ip_lote} no encontrado."
        )

    pesaje = lote.pesajes[0] if lote.pesajes else None
    if not pesaje or not pesaje.peso_neto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El lote no tiene un peso neto válido en balanza.",
        )

    nuevos = []
    intentos_existentes = {m.intento for m in lote.muestreos}

    for datos in datos_list:
        if datos.intento in intentos_existentes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El intento {datos.intento} ya está registrado para este lote.",
            )
        intentos_existentes.add(datos.intento)

        if datos.peso_seco >= datos.peso_humedo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El peso seco debe ser estrictamente menor al peso húmedo.",
            )

        humedad = calcular_humedad(datos.peso_humedo, datos.peso_seco)
        if humedad <= 0 or humedad > 50:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Humedad fuera de rango permitido (0-50%). Valor calculado: {humedad:.2f}%",
            )

        tms = calcular_tms(pesaje.peso_neto, humedad)

        nuevo_muestreo = Muestreo(
            lote_id=lote.id,
            intento=datos.intento,
            peso_humedo=datos.peso_humedo,
            peso_seco=datos.peso_seco,
            tms_calculado=tms,
            observaciones=datos.observaciones,
            creado_en=datos.fecha_muestreo or datetime.now(),
            creado_por=usuario_id,
        )
        db.add(nuevo_muestreo)
        nuevos.append(nuevo_muestreo)

    db.commit()
    for n in nuevos:
        db.refresh(n)

    return nuevos


def generar_base_cip(lote_id: int, salt: int = 0) -> str:
    """
    Genera un código base de 7 caracteres para un lote:
    6 dígitos + 1 letra de control. (Ej: 058598D)
    Al pasar un 'salt', se altera el resultado para que CIPs del mismo lote
    tengan bases totalmente diferentes.
    """
    control_chars = "ABCDEFGHJKLMNPQRSTUVWXYZ"

    # Lógica LCG
    numero = (lote_id * 9301 + 49297 + (salt * 1337)) % 1_000_000
    base = f"{numero:06d}"  # Rellena con ceros a la izquierda si es necesario

    # Cálculo del dígito de control
    suma = sum(int(digito) for digito in base)
    control = control_chars[suma % len(control_chars)]

    return f"{base}{control}"


def generar_cips_para_lote(db: Session, ip_lote: str, cantidad: int = 5) -> list[MapeoCIP]:
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")

    cips_existentes = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).count()

    nuevos_cips = []

    # Asignamos los sufijos para las bolsas de laboratorio
    for i in range(cantidad):
        correlativo = cips_existentes + i + 1

        # Generamos la base única y ofuscada para cada CIP, usando el correlativo como salt
        base_ofuscada = generar_base_cip(lote.id, salt=correlativo)

        # Resultado final: Ej. CIP-058598D-A1
        codigo_final = f"CIP-{base_ofuscada}-A{correlativo}"

        # Asignar Paititi a los 2 primeros CIPs, el resto queda Por definir
        laboratorio = "Paititi" if correlativo <= 2 else "Por definir"

        nuevo_cip = MapeoCIP(
            lote_id=lote.id,
            codigo_cip=codigo_final,
            laboratorio=laboratorio,
            tipo_muestra="Laboratorio",
            fecha_envio=datetime.now().date(),
        )
        db.add(nuevo_cip)
        nuevos_cips.append(nuevo_cip)

    db.commit()
    for cip in nuevos_cips:
        db.refresh(cip)

    return nuevos_cips


def obtener_lotes_para_muestreo(db: Session):
    config_horas = (
        db.query(Configuracion)
        .filter(Configuracion.clave.in_(["sla_metalurgia_horas", "sla_limite_plazo_horas"]))
        .all()
    )

    # Valores por defecto si no existen en la BD
    sla_map = {c.clave: int(c.valor) for c in config_horas}
    h_min = sla_map.get("sla_metalurgia_horas", 48)
    h_max = sla_map.get("sla_limite_plazo_horas", 72)

    lotes_db = (
        db.query(Lote)
        .join(Lote.sesion)
        .filter(
            SesionDescarga.estado == EstadoSesion.COMPLETO,
            ~Lote.eliminado,
            Lote.tipo_material.in_(["Mineral", "Llampo", "M.Llampo"]),
            Lote.ip.like("IP-%"),
        )
        .all()
    )

    resultado = []

    for lote in lotes_db:
        pesaje = lote.pesajes[0] if lote.pesajes else None
        peso_neto = pesaje.peso_neto if pesaje else 0.0
        sacos = pesaje.sacos if pesaje else None

        proveedor_nombre = "Desconocido"
        if lote.sesion and lote.sesion.provacop and lote.sesion.provacop.proveedor:
            proveedor_nombre = lote.sesion.provacop.proveedor.razon_social

        # Historial de Muestreos (Humedad)
        intentos = (
            db.query(Muestreo)
            .filter(Muestreo.lote_id == lote.id)
            .order_by(Muestreo.intento.desc())
            .all()
        )
        intentos_previos = len(intentos)
        fecha_ultimo_muestreo = (
            intentos[0].creado_en.isoformat() if intentos and intentos[0].creado_en else None
        )

        # ETIQUETAS Y ESTADOS
        tiene_etiquetas = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).first() is not None
        estado_muestreo = "COMPLETADO" if intentos_previos > 0 else "PENDIENTE"

        # SLA Logic
        pendiente_sla = (estado_muestreo == "COMPLETADO") and (not tiene_etiquetas)

        humedad_minima = None
        if lote.sesion and lote.sesion.provacop and lote.sesion.provacop.parametros:
            if lote.sesion.provacop.parametros.humedad_minima is not None:
                humedad_minima = float(lote.sesion.provacop.parametros.humedad_minima)

        resultado.append(
            {
                "lote_id": lote.id,
                "ip": lote.ip,
                "fecha_recepcion": lote.creado_en.isoformat() if lote.creado_en else None,
                "fecha_muestreo": fecha_ultimo_muestreo,
                "peso_neto": float(peso_neto),
                "sacos": sacos,
                "proveedor_razon_social": proveedor_nombre,
                "estado_muestreo": estado_muestreo,
                "cantidad_intentos_previos": intentos_previos,
                "tiene_humedad": intentos_previos > 0,
                "etiquetado": tiene_etiquetas,
                "sla_config": {"h_min": h_min, "h_max": h_max},
                "pendiente_sla": pendiente_sla,
                "humedad_minima": humedad_minima,
            }
        )

    return resultado


def crear_cip_ensayo_extra(db: Session, cip_origen: str) -> MapeoCIP:
    """
    Crea un CIP de re-ensayo (sufijo REE) para el mismo lote del CIP de origen.
    El código generado conserva la misma base ofuscada que el CIP original:
        CIP-{base_ofuscada}-REE{n}
    donde n = número de CIPs REE ya existentes para ese lote + 1.

    Este nuevo CIP tendrá fecha_envio = hoy (para que aparezca correctamente
    en los certificados de laboratorio).
    """
    import re as _re

    # 1. Buscar el CIP origen
    mapeo_origen = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == cip_origen).first()
    if not mapeo_origen:
        from fastapi import HTTPException
        from fastapi import status as http_status

        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail=f"CIP '{cip_origen}' no encontrado."
        )

    lote_id = mapeo_origen.lote_id
    if not lote_id:
        from fastapi import HTTPException
        from fastapi import status as http_status

        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="El CIP de origen no está asociado a un lote.",
        )

    # 2. Extraer la base ofuscada del CIP origen (ej: "058598D" de "CIP-058598D-A1")
    match = _re.match(r"^CIP-([A-Z0-9]+)-", cip_origen)
    if not match:
        from fastapi import HTTPException
        from fastapi import status as http_status

        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de CIP no reconocido: '{cip_origen}'",
        )
    base_ofuscada = match.group(1)

    # 3. Encontrar el número máximo de REE para esta base de CIP
    cips_ree_existentes = (
        db.query(MapeoCIP.codigo_cip)
        .filter(MapeoCIP.codigo_cip.like(f"CIP-{base_ofuscada}-REE%"))
        .all()
    )

    max_n = 0
    for (codigo,) in cips_ree_existentes:
        match_ree = _re.search(r"-REE(\d+)$", codigo)
        if match_ree:
            n = int(match_ree.group(1))
            if n > max_n:
                max_n = n

    n_ree = max_n + 1

    # 4. Construir código final: CIP-{base}-REEn
    codigo_ree = f"CIP-{base_ofuscada}-REE{n_ree}"

    # Verificar que no exista ya (idempotencia)
    existente = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == codigo_ree).first()
    if existente:
        return existente

    # 5. Crear el nuevo MapeoCIP
    nuevo_cip = MapeoCIP(
        lote_id=lote_id,
        codigo_cip=codigo_ree,
        laboratorio=mapeo_origen.laboratorio or "Paititi",
        tipo_muestra="Laboratorio",
        fecha_envio=datetime.now().date(),  # fecha de ingreso del re-ensayo
    )
    db.add(nuevo_cip)
    db.commit()
    db.refresh(nuevo_cip)

    return nuevo_cip
