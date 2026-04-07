from datetime import datetime
from decimal import Decimal

from app.models.enums import EstadoSesion
from app.models.models import (
    Configuracion,
    Lote,
    MapeoCIP,
    Muestreo,
    PruebaMetalurgica,
    SesionDescarga,
)
from app.schemas.muestreo import MuestreoCreate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


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


def generar_base_cip(lote_id: int) -> str:
    """
    Genera un código base de 6 dígitos + 1 letra de control usando LCG.
    Ej: lote_id=1 -> '058598D'
    """
    control_chars = "ABCDEFGHJKLMNPQRSTUVWXYZ"

    # Lógica LCG
    numero = (lote_id * 9301 + 49297) % 1_000_000
    base = f"{numero:06d}"  # Rellena con ceros a la izquierda si es necesario

    # Cálculo del dígito de control
    suma = sum(int(digito) for digito in base)
    control = control_chars[suma % len(control_chars)]

    return f"{base}{control}"


def generar_cips_para_lote(db: Session, ip_lote: str, cantidad: int = 2) -> list[MapeoCIP]:
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lote no encontrado.")

    cips_existentes = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).count()

    # 1. Generamos la base única y ofuscada para TODO el lote
    base_ofuscada = generar_base_cip(lote.id)

    nuevos_cips = []

    # 2. Asignamos los sufijos para las bolsas de laboratorio
    for i in range(cantidad):
        correlativo = cips_existentes + i + 1

        # Resultado final: Ej. CIP-058598D-A1
        codigo_final = f"CIP-{base_ofuscada}-A{correlativo}"

        nuevo_cip = MapeoCIP(
            lote_id=lote.id,
            codigo_cip=codigo_final,
            laboratorio="Por definir",
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
        # .outerjoin(Lote.prueba_metalurgica) # Opcional, ya que hacemos la consulta abajo
        .filter(SesionDescarga.estado == EstadoSesion.COMPLETO)
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

        # PRUEBAS METALÚRGICAS
        prueba = db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()
        prueba_completada = True if prueba else False
        fecha_ingreso_prueba = (
            prueba.fecha_ingreso.isoformat() if prueba and prueba.fecha_ingreso else None
        )

        # ETIQUETAS Y ESTADOS
        tiene_etiquetas = db.query(MapeoCIP).filter(MapeoCIP.lote_id == lote.id).first() is not None
        estado_muestreo = "COMPLETADO" if intentos_previos > 0 else "PENDIENTE"

        # SLA Logic
        pendiente_sla = prueba_completada and (not tiene_etiquetas)

        resultado.append(
            {
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
                "prueba_completada": prueba_completada,
                "fecha_ingreso_prueba": fecha_ingreso_prueba,
                "sla_config": {"h_min": h_min, "h_max": h_max},
                "pendiente_sla": pendiente_sla,
            }
        )

    return resultado
