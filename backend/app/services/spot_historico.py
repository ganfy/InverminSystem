"""
Service: Histórico de precios spot del oro (Au) y plata (Ag) — LBMA Fix.

Lógica de fecha efectiva para fines de semana:
  - Sábado (weekday=5) → viernes anterior (el último día hábil registrado)
  - Domingo (weekday=6) → lunes siguiente (se registrará ese día)
  - Lunes–Viernes → misma fecha

El scraper se ejecuta diariamente (lunes–viernes) desde scheduler_loop_spots().
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta
from decimal import Decimal

from app.core.database import SessionLocal
from app.models.models import SpotHistorico
from app.services.liquidaciones_ag import obtener_ultimo_valor_plata_noon
from app.services.liquidaciones_au import obtener_ultimo_valor_oro_pm
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ── Estado en memoria para el scheduler ──────────────────────────────────────
_ultimo_scraping: date | None = None


# ── Helpers de fecha ─────────────────────────────────────────────────────────


def fecha_efectiva_spot(fecha: date) -> date:
    """
    Devuelve la fecha hábil cuyo spot aplica para una fecha de recepción dada.

    Regla:
      - Lunes–Viernes  → misma fecha
      - Sábado (5)     → viernes anterior
      - Domingo (6)    → lunes siguiente

    Nota: LBMA no publica Fix en fines de semana, por lo que no existe un
    spot propio para sábados ni domingos.
    """
    wd = fecha.weekday()
    if wd == 5:  # sábado
        return fecha - timedelta(days=1)  # viernes
    if wd == 6:  # domingo
        return fecha + timedelta(days=1)  # lunes
    return fecha


# ── CRUD ─────────────────────────────────────────────────────────────────────


def guardar_spot(
    db: Session,
    fecha: date,
    precio_au_usd: Decimal,
    precio_ag_usd: Decimal | None = None,
    fuente: str = "MANUAL",
) -> SpotHistorico:
    """
    Inserta o actualiza el spot para una fecha determinada.
    Si ya existe un registro para esa fecha, actualiza los precios.
    """
    registro = db.query(SpotHistorico).filter(SpotHistorico.fecha == fecha).first()
    if registro:
        registro.precio_au_usd = precio_au_usd
        if precio_ag_usd is not None:
            registro.precio_ag_usd = precio_ag_usd
        registro.fuente = fuente
    else:
        registro = SpotHistorico(
            fecha=fecha,
            precio_au_usd=precio_au_usd,
            precio_ag_usd=precio_ag_usd,
            fuente=fuente,
        )
        db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def get_spot_para_fecha(
    db: Session,
    fecha_recepcion: date,
) -> SpotHistorico | None:
    """
    Retorna el SpotHistorico correspondiente a una fecha de recepción,
    aplicando la regla de fin de semana (fecha_efectiva_spot).
    Retorna None si no hay registro para esa fecha efectiva.
    """
    fe = fecha_efectiva_spot(fecha_recepcion)
    return db.query(SpotHistorico).filter(SpotHistorico.fecha == fe).first()


def listar_spots(
    db: Session,
    desde: date | None = None,
    hasta: date | None = None,
    limit: int = 100,
) -> list[SpotHistorico]:
    """Lista spots ordenados por fecha DESC, opcionalmente filtrados por rango."""
    q = db.query(SpotHistorico).order_by(SpotHistorico.fecha.desc())
    if desde:
        q = q.filter(SpotHistorico.fecha >= desde)
    if hasta:
        q = q.filter(SpotHistorico.fecha <= hasta)
    return q.limit(limit).all()


def eliminar_spot(db: Session, spot_id: int) -> bool:
    """Elimina un registro del histórico. Retorna True si existía."""
    registro = db.query(SpotHistorico).filter(SpotHistorico.id == spot_id).first()
    if not registro:
        return False
    db.delete(registro)
    db.commit()
    return True


# ── Scraper on-demand ─────────────────────────────────────────────────────────


def scrape_y_guardar_hoy(db: Session) -> SpotHistorico | None:
    """
    Ejecuta el scraper de LBMA, guarda el resultado para el día de hoy
    (si es día hábil) y retorna el registro guardado.
    Retorna None si el scraper falla o si hoy es fin de semana.
    """
    hoy = date.today()
    if hoy.weekday() >= 5:
        logger.info("spot_historico: hoy es fin de semana, no hay LBMA Fix.")
        return None

    precio_au = obtener_ultimo_valor_oro_pm()
    if not precio_au:
        logger.warning("spot_historico: scraper Au falló, no se guardó.")
        return None

    precio_ag_raw = obtener_ultimo_valor_plata_noon()
    precio_ag = Decimal(str(precio_ag_raw)) if precio_ag_raw else None

    registro = guardar_spot(
        db,
        fecha=hoy,
        precio_au_usd=Decimal(str(precio_au)),
        precio_ag_usd=precio_ag,
        fuente="SCRAPING",
    )
    logger.info(f"spot_historico: guardado Au={precio_au} Ag={precio_ag} para {hoy}")
    return registro


# ── Scheduler asíncrono ───────────────────────────────────────────────────────


async def scheduler_loop_spots() -> None:
    """
    Corre en background (asyncio task). Intenta guardar el spot una vez
    al día, a las 18:00 (hora del servidor, después del cierre de LBMA).
    Solo ejecuta en días hábiles (lunes–viernes).
    """
    global _ultimo_scraping

    while True:
        await asyncio.sleep(60)  # revisar cada minuto

        from datetime import datetime

        ahora = datetime.now()
        hoy = ahora.date()

        # Solo ejecutar en días hábiles
        if hoy.weekday() >= 5:
            continue

        # Solo ejecutar a partir de las 18:00 y si no se ejecutó hoy ya
        if ahora.hour < 18:
            continue
        if _ultimo_scraping == hoy:
            continue

        logger.info("spot_historico: ejecutando scraper diario...")
        db = SessionLocal()
        try:
            resultado = scrape_y_guardar_hoy(db)
            if resultado:
                _ultimo_scraping = hoy
        except Exception as e:
            logger.error(f"spot_historico: error en scheduler: {e}")
        finally:
            db.close()
