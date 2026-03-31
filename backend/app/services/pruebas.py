import logging

from app.models.models import Lote, PruebaMetalurgica
from app.schemas.pruebas import PruebaMetalurgicaCreate, PruebaOfflineItem
from sqlalchemy import or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def obtener_lista_pruebas(db: Session):
    """
    Lista todos los lotes activos y su estado en pruebas metalúrgicas basándose solo en el IP.
    """
    # Consulta súper rápida: Solo cruzamos Lote y PruebaMetalurgica
    resultados = (
        db.query(
            Lote.ip,
            Lote.creado_en.label("fecha_recepcion"),
            PruebaMetalurgica.fecha_salida,
            PruebaMetalurgica.malla_porcentaje,
            PruebaMetalurgica.gasto_agno3,
            PruebaMetalurgica.id.label("prueba_id"),
        )
        .outerjoin(PruebaMetalurgica, PruebaMetalurgica.lote_id == Lote.id)
        .filter(or_(Lote.eliminado.is_(False), Lote.eliminado.is_(None)))
        .all()
    )

    lista = []
    for r in resultados:
        estado = "PENDIENTE"
        if r.prueba_id:
            estado = "COMPLETO" if r.fecha_salida else "EN PROCESO"

        lista.append(
            {
                "ip": r.ip,
                "fecha_recepcion": r.fecha_recepcion,
                "fecha_salida": r.fecha_salida,
                "malla_porcentaje": r.malla_porcentaje,
                "gasto_agno3": r.gasto_agno3,
                "estado": estado,
            }
        )

    lista.sort(key=lambda x: x["ip"], reverse=True)
    return lista


def registrar_prueba(db: Session, ip_lote: str, datos: PruebaMetalurgicaCreate, usuario_id: int):
    # Buscamos el Lote por su IP
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"El lote con IP {ip_lote} no existe.")

    warning_msg = None
    if datos.malla_porcentaje is not None:
        if datos.malla_porcentaje < 88 or datos.malla_porcentaje > 94:
            warning_msg = (
                "WARNING: El porcentaje de malla está fuera del rango aceptable (88% - 94%)."
            )

    # Guardamos usando directamente el ID del lote
    nueva_prueba = PruebaMetalurgica(
        lote_id=lote.id,
        fecha_ingreso=datos.fecha_ingreso,
        malla_porcentaje=datos.malla_porcentaje,
        porcentaje_nacn=datos.porcentaje_nacn,
        ph_inicial=datos.ph_inicial,
        ph_final=datos.ph_final,
        adicion_nacn=datos.adicion_nacn,
        adicion_naoh=datos.adicion_naoh,
        gasto_agno3=datos.gasto_agno3,
        creado_por=usuario_id,
    )

    db.add(nueva_prueba)
    db.commit()
    db.refresh(nueva_prueba)

    return nueva_prueba, warning_msg


def sync_batch(db: Session, pruebas_offline: list[PruebaOfflineItem], usuario_id: int):
    resultados = []
    for item in pruebas_offline:
        try:
            nueva_prueba, _ = registrar_prueba(db, item.ip, item.datos, usuario_id)
            resultados.append(
                {"offline_id": item.offline_id, "server_id": nueva_prueba.id, "error": None}
            )
        except Exception as e:
            logger.error(f"Error sincronizando prueba {item.offline_id}: {str(e)}")
            resultados.append({"offline_id": item.offline_id, "server_id": None, "error": str(e)})
            db.rollback()

    return {"resultados": resultados}
