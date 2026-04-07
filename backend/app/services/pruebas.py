import logging
from datetime import datetime, timedelta

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
            PruebaMetalurgica.fecha_ingreso,
            PruebaMetalurgica.malla_porcentaje,
            PruebaMetalurgica.gasto_agno3,
            PruebaMetalurgica.id.label("prueba_id"),
        )
        .outerjoin(PruebaMetalurgica, PruebaMetalurgica.lote_id == Lote.id)
        .filter(or_(~Lote.eliminado, Lote.eliminado.is_(None)))
        .all()
    )

    lista = []
    ahora = datetime.now()

    for r in resultados:
        estado = "PENDIENTE"
        fecha_salida_calc = None

        if r.prueba_id and r.fecha_ingreso:
            fecha_salida_calc = r.fecha_ingreso + timedelta(hours=48)

            # Si ya pasaron las 48 horas:
            if ahora >= fecha_salida_calc:
                estado = "COMPLETADO"
            # Si todavía estamos dentro de las 48 horas:
            else:
                estado = "EN PROCESO"

        lista.append(
            {
                "ip": r.ip,
                "fecha_recepcion": r.fecha_recepcion,
                "fecha_ingreso": r.fecha_ingreso,
                "fecha_salida": fecha_salida_calc,
                "malla_porcentaje": r.malla_porcentaje,
                "gasto_agno3": r.gasto_agno3,
                "estado": estado,
            }
        )

    lista.sort(key=lambda x: x["ip"], reverse=True)
    return lista


def registrar_prueba(db: Session, ip_lote: str, datos: PruebaMetalurgicaCreate, usuario_id: int):
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        raise ValueError(f"El lote con IP {ip_lote} no existe.")

    warning_msg = None
    if datos.malla_porcentaje is not None:
        if datos.malla_porcentaje < 88 or datos.malla_porcentaje > 94:
            warning_msg = (
                "WARNING: El porcentaje de malla está fuera del rango aceptable (88% - 94%)."
            )

    prueba_existente = (
        db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()
    )

    if prueba_existente:
        if datos.malla_porcentaje is not None:
            prueba_existente.malla_porcentaje = datos.malla_porcentaje
        if datos.porcentaje_nacn is not None:
            prueba_existente.porcentaje_nacn = datos.porcentaje_nacn
        if datos.ph_inicial is not None:
            prueba_existente.ph_inicial = datos.ph_inicial
        if datos.ph_final is not None:
            prueba_existente.ph_final = datos.ph_final
        if datos.adicion_nacn is not None:
            prueba_existente.adicion_nacn = datos.adicion_nacn
        if datos.adicion_naoh is not None:
            prueba_existente.adicion_naoh = datos.adicion_naoh
        if datos.gasto_agno3 is not None:
            prueba_existente.gasto_agno3 = datos.gasto_agno3

        prueba_existente.modificado_por = usuario_id

        prueba = prueba_existente
    else:
        prueba = PruebaMetalurgica(
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
        db.add(prueba)

    db.commit()
    db.refresh(prueba)

    return prueba, warning_msg


def obtener_prueba_por_ip(db: Session, ip_lote: str):
    lote = db.query(Lote).filter(Lote.ip == ip_lote).first()
    if not lote:
        return None
    return db.query(PruebaMetalurgica).filter(PruebaMetalurgica.lote_id == lote.id).first()


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
