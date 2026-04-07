import os
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.models.enums import TipoAnalisis
from app.models.models import AnalisisLey, AnalisisRecuperacion, MapeoCIP
from app.schemas.laboratorio import AnalisisLeyCreate, AnalisisRecuperacionCreate
from fastapi import UploadFile
from sqlalchemy.orm import Session

# Constante de conversión: 1 Oz/TC = 34.2857 gr/TM
FACTOR_OZ_TC = Decimal("34.2857")
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
TIPOS_PERMITIDOS = {"pdf", "jpg", "jpeg", "png"}


def _calcular_ley_final(ley_fino: Decimal, ley_grueso: Decimal) -> Decimal:
    """Regla de negocio: ley_final = ley_fino + ley_grueso"""
    return ley_fino + ley_grueso


def _calcular_oz_tc(ley_final: Decimal) -> Decimal:
    """Convierte la ley final a Oz/TC"""
    if ley_final == 0:
        return Decimal("0.000")
    return (ley_final / FACTOR_OZ_TC).quantize(Decimal("0.001"))


def registrar_analisis_ley(db: Session, datos: AnalisisLeyCreate, usuario_id: int) -> AnalisisLey:
    # 1. Buscar a qué lote pertenece este CIP
    mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == datos.cip).first()
    if not mapeo:
        raise ValueError(f"El código CIP {datos.cip} no existe en el sistema.")

    # 2. Lógica de Dirimencia
    if datos.tipo_analisis == TipoAnalisis.DIRIMENCIA:
        # Desactivamos todos los análisis previos vigentes de ESTE lote
        analisis_previos = (
            db.query(AnalisisLey)
            .filter(AnalisisLey.lote_id == mapeo.lote_id, AnalisisLey.vigente.is_(True))
            .all()
        )

        for ant in analisis_previos:
            ant.vigente = False
            ant.descartado_por = usuario_id
            ant.fecha_descarte = datetime.now()
            ant.justificacion_descarte = (
                "Reemplazado automáticamente por ingreso de análisis de Dirimencia."
            )

    # 3. Cálculos Agnósticos (Python)
    ley_final_calc = _calcular_ley_final(datos.ley_fino, datos.ley_grueso)
    ley_gr_tm_calc = _calcular_oz_tc(ley_final_calc)

    # 4. Crear el registro
    nuevo_analisis = AnalisisLey(
        lote_id=mapeo.lote_id,
        cip=datos.cip,
        laboratorio=datos.laboratorio,
        tipo_analisis=datos.tipo_analisis,
        material=datos.material,
        ley_fino=datos.ley_fino,
        ley_grueso=datos.ley_grueso,
        ley_final=ley_final_calc,
        ley_gr_tm=ley_gr_tm_calc,
        origen_datos=datos.origen_datos,
        fecha_analisis=datos.fecha_analisis or datetime.now().date(),
        creado_por=usuario_id,
        vigente=True,
    )

    db.add(nuevo_analisis)
    db.commit()
    db.refresh(nuevo_analisis)
    return nuevo_analisis


def registrar_analisis_recuperacion(
    db: Session, datos: AnalisisRecuperacionCreate, usuario_id: int
) -> AnalisisRecuperacion:
    # 1. Validaciones físicas
    if datos.ley_cabeza <= datos.ley_cola:
        raise ValueError(
            "Error Físico: La Ley de Cabeza debe ser estrictamente mayor a la Ley de Cola."
        )

    mapeo = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == datos.cip).first()
    if not mapeo:
        raise ValueError(f"El código CIP {datos.cip} no existe en el sistema.")

    # Recuperación calculada en models.py por Computed, pero si fallara en SQL Server,
    # la podríamos calcular aquí como: recuperacion = ((cabeza - cola) / cabeza) * 100

    nuevo_analisis = AnalisisRecuperacion(
        lote_id=mapeo.lote_id,
        cip=datos.cip,
        laboratorio=datos.laboratorio,
        ley_cabeza=datos.ley_cabeza,
        ley_cola=datos.ley_cola,
        ley_liquido=datos.ley_liquido,
        origen_datos=datos.origen_datos,
        fecha_analisis=datos.fecha_analisis or datetime.now().date(),
        creado_por=usuario_id,
        vigente=True,
    )

    db.add(nuevo_analisis)
    db.commit()
    db.refresh(nuevo_analisis)
    return nuevo_analisis


def subir_certificado(db: Session, analisis_id: int, archivo: UploadFile, tipo: str) -> str:
    """Guarda el certificado físico y actualiza la URL en la BD."""
    contenido = archivo.file.read()
    if len(contenido) > MAX_FILE_SIZE:
        raise ValueError("El archivo supera los 10 MB permitidos")

    ext = Path(archivo.filename or "").suffix.lstrip(".").lower()
    if ext not in TIPOS_PERMITIDOS:
        raise ValueError(f"Tipo no permitido: .{ext}. Solo PDF o Imágenes.")

    # Buscar el registro dependiendo del tipo
    if tipo == "ley":
        analisis = db.query(AnalisisLey).filter(AnalisisLey.id == analisis_id).first()
    else:
        analisis = (
            db.query(AnalisisRecuperacion).filter(AnalisisRecuperacion.id == analisis_id).first()
        )

    if not analisis:
        raise ValueError("Análisis no encontrado.")

    # Guardar en disco: /storage/certificados/{año}/{mes}/{cip}_{uuid}.pdf
    ahora = datetime.utcnow()
    carpeta = STORAGE_PATH / "certificados" / str(ahora.year) / f"{ahora.month:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre_guardado = f"{analisis.cip}_{uuid.uuid4().hex[:8]}.{ext}"
    ruta_fisica = carpeta / nombre_guardado
    ruta_fisica.write_bytes(contenido)

    # Actualizar BD (Guardamos la ruta relativa para el frontend)
    ruta_relativa = f"/certificados/{ahora.year}/{ahora.month:02d}/{nombre_guardado}"
    analisis.certificado_url = ruta_relativa

    analisis.modificado_por = analisis.creado_por
    analisis.modificado_en = ahora
    db.commit()

    return ruta_relativa


def sincronizar_batch(db: Session, payload, usuario_id: int):
    """Procesa la cola offline de Laboratorio intentando no romper el batch entero por un error."""
    resultados = []

    for item in payload.analisis_ley:
        try:
            nuevo = registrar_analisis_ley(db, item.datos, usuario_id)
            resultados.append({"offline_id": item.offline_id, "server_id": nuevo.id, "error": None})
        except Exception as e:
            db.rollback()
            resultados.append({"offline_id": item.offline_id, "server_id": None, "error": str(e)})

    return {"resultados_ley": resultados}


def obtener_muestras_laboratorio(db: Session):
    """Lista todos los códigos CIP generados y verifica si ya tienen análisis."""
    # Obtenemos los CIPs ordenados por el más reciente
    cips = db.query(MapeoCIP).order_by(MapeoCIP.id.desc()).all()

    resultados = []
    for c in cips:
        # Verificamos si existe un análisis vigente para este CIP
        ley = (
            db.query(AnalisisLey)
            .filter(AnalisisLey.cip == c.codigo_cip, AnalisisLey.vigente)
            .first()
        )

        recuperacion = (
            db.query(AnalisisRecuperacion)
            .filter(AnalisisRecuperacion.cip == c.codigo_cip, AnalisisRecuperacion.vigente)
            .first()
        )

        resultados.append(
            {
                "cip": c.codigo_cip,
                "fecha_envio": c.fecha_envio,
                "tipo_muestra": c.tipo_muestra,
                "estado_ley": "COMPLETADO" if ley else "PENDIENTE",
                "estado_recuperacion": "COMPLETADO" if recuperacion else "PENDIENTE",
            }
        )

    return resultados
