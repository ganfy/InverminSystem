"""
seed_spot_historico.py - Intenta poblar spot_historico via FRED API.

NOTA: FRED requiere parametros especificos por serie. Si el endpoint falla,
use seed_spot_manual.py con los datos copiados de goldsilver.com o LBMA.

Como obtener los datos manualmente:
  1. Ir a https://goldsilver.com/price-charts/historical-london-fix/
  2. Copiar la tabla (Gold PM, Silver Noon) en seed_spot_manual.py
  3. Ejecutar: python scripts/seed_spot_manual.py

Uso de este script (para intentar FRED):
    python scripts/seed_spot_historico.py --dry-run
    python scripts/seed_spot_historico.py --dias 35
"""

import argparse
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from app.core.database import SessionLocal
from app.models.models import SpotHistorico

# ── FRED API (sin API key, endpoint publico) ──────────────────────────────────

FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES_AU = "GOLDPMGBD228NLBM"
SERIES_AG = "SLVPRUSD"

HEADERS = {"User-Agent": ("Mozilla/5.0 (compatible; InverminSystem/1.0)")}


def _fetch_fred(series_id: str, desde: date, hasta: date) -> dict[str, float]:
    """
    Descarga los datos de una serie FRED en CSV para el rango dado.
    Retorna dict {fecha_str: valor} solo para dias con valor valido.
    """
    url = (
        f"https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id={series_id}"
        f"&observation_start={desde.isoformat()}"
        f"&observation_end={hasta.isoformat()}"
    )
    print(f"  Descargando {series_id} desde FRED...")
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    result = {}
    lines = resp.text.strip().split("\n")
    # Primera linea es encabezado: DATE,VALOR
    for line in lines[1:]:
        parts = line.strip().split(",")
        if len(parts) < 2:
            continue
        fecha_str, valor_str = parts[0].strip(), parts[1].strip()
        if valor_str == "." or not valor_str:  # FRED usa "." para sin datos
            continue
        try:
            fecha = date.fromisoformat(fecha_str)
            if fecha < desde or fecha > hasta:
                continue
            result[fecha_str] = float(valor_str)
        except (ValueError, TypeError):
            continue

    return result


# ── Upsert ────────────────────────────────────────────────────────────────────


def upsert_spot(db, fecha: date, au_pm: float, ag_noon: float | None, dry_run: bool) -> str:
    existente = db.query(SpotHistorico).filter(SpotHistorico.fecha == fecha).first()
    if dry_run:
        return "ACTUALIZAR" if existente else "INSERTAR"

    if existente:
        existente.precio_au_usd = Decimal(str(round(au_pm, 2)))
        if ag_noon is not None:
            existente.precio_ag_usd = Decimal(str(round(ag_noon, 4)))
        existente.fuente = "SCRAPING"
        return "ACTUALIZAR"
    else:
        registro = SpotHistorico(
            fecha=fecha,
            precio_au_usd=Decimal(str(round(au_pm, 2))),
            precio_ag_usd=Decimal(str(round(ag_noon, 4))) if ag_noon else None,
            fuente="SCRAPING",
        )
        db.add(registro)
        return "INSERTAR"


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Backfill spot_historico con datos LBMA via FRED.")
    parser.add_argument(
        "--dias", type=int, default=35, help="Dias hacia atras a rellenar (default: 35)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Mostrar que se haria sin guardar nada"
    )
    args = parser.parse_args()

    hoy = date.today()
    desde = hoy - timedelta(days=args.dias)

    tag = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{tag}Rango: {desde} al {hoy} ({args.dias} dias)\n")

    # 1. Descargar series de FRED
    try:
        datos_au = _fetch_fred(SERIES_AU, desde, hoy)
        datos_ag = _fetch_fred(SERIES_AG, desde, hoy)
    except Exception as e:
        print(f"ERROR al obtener datos de FRED: {e}")
        sys.exit(1)

    if not datos_au:
        print("No se encontraron datos de Au en el rango especificado.")
        print("Nota: FRED puede tardar 1-2 dias en publicar el precio mas reciente.")
        sys.exit(1)

    print(f"\nDatos Au obtenidos: {len(datos_au)} dias habiles")
    print(f"Datos Ag obtenidos: {len(datos_ag)} dias habiles\n")

    # 2. Construir lista de fechas a insertar (solo dias habiles con precio Au)
    fechas = sorted(datos_au.keys())

    dias_semana = ["Lun", "Mar", "Mie", "Jue", "Vie"]
    print(f"{'FECHA':<14} {'DIA':<4} {'Au PM (USD/Oz)':>15} {'Ag (USD/Oz)':>13} {'ACCION'}")
    print("-" * 60)

    db = SessionLocal()
    insertar = actualizar = 0

    try:
        for fecha_str in fechas:
            fecha = date.fromisoformat(fecha_str)
            au_pm = datos_au[fecha_str]
            ag_noon = datos_ag.get(fecha_str)
            dia = dias_semana[fecha.weekday()]
            ag_str = f"${ag_noon:.4f}" if ag_noon else "---"
            accion = upsert_spot(db, fecha, au_pm, ag_noon, args.dry_run)
            print(f"{fecha_str:<14} {dia:<4} ${au_pm:>14.2f} {ag_str:>13} [{accion}]")
            if accion == "INSERTAR":
                insertar += 1
            elif accion == "ACTUALIZAR":
                actualizar += 1

        if not args.dry_run:
            db.commit()
            print(f"\nOK: {insertar} nuevos, {actualizar} actualizados.")
        else:
            print(f"\n[DRY RUN] Se insertarian {insertar}, se actualizarian {actualizar}.")

    except Exception as e:
        db.rollback()
        print(f"\nERROR durante el guardado: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
