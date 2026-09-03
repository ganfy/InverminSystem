from decimal import Decimal
from typing import Any

from app.models.models import Lote
from app.services.liquidaciones import _calcular_lote, resolver_overrides_desde_snapshot
from sqlalchemy.orm import Session


def obtener_snapshot_financiero_lote(db: Session, lote: Lote) -> dict[str, Any] | None:
    """
    Snapshot financiero de un lote para reporting (dashboard), sin crear ni
    modificar ninguna liquidación.

    - Si el lote tiene una LiquidacionLote asociada activa (estado de la
      liquidación != 'ANULADA'), reutiliza los valores CONGELADOS de esa fila como
      overrides vía resolver_overrides_desde_snapshot() — determinista,
      cero drift respecto al módulo de liquidaciones.
    - Si no tiene liquidación, calcula un preview en vivo (mismos defaults
      que preview_liquidacion: todos los overrides en None).
    - Retorna None si _calcular_lote no puede calcular (alertas críticas:
      SIN_MUESTREO, SIN_PARAMS, SIN_LEY_PLANTA, SIN_RECUPERACION). El lote
      simplemente no contribuye a los agregados financieros — es correcto,
      no se puede valorizar sin esos datos.
    """
    liq_lote = next(
        (
            ll
            for ll in lote.liquidaciones_lotes
            if getattr(ll.liquidacion, "estado", "") != "ANULADA"
        ),
        None,
    )

    if liq_lote:
        overrides = resolver_overrides_desde_snapshot(liq_lote)
        snap, alertas = _calcular_lote(db, lote, **overrides)
    else:
        snap, alertas = _calcular_lote(
            db,
            lote,
            spot_usd_override=None,
            bono=Decimal("0"),
            rec_liq_override=None,
            gasto_acopio_override=None,
            gasto_consumo_override=None,
            spot_ag_usd_override=None,
            maquila_override=None,
            valorizar_volado=bool(lote.volado),
        )

    if any(a.critico for a in alertas) or not snap:
        return None

    return snap
