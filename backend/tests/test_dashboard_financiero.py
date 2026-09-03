from decimal import Decimal

from app.services.dashboard_financiero import obtener_snapshot_financiero_lote
from sqlalchemy.orm import Session


class LoteMock:
    def __init__(self, ip="IP-100", liquidaciones_lotes=None, volado=False):
        self.ip = ip
        self.liquidaciones_lotes = liquidaciones_lotes or []
        self.volado = volado


class LiqLoteMock:
    def __init__(self, estado="GENERADA"):
        self.liquidacion = type("Liq", (), {"estado": estado})
        self.spot_usd_snapshot = Decimal("2400")
        self.bono = Decimal("10")
        self.porcentaje_rec_liquido = Decimal("90")
        self.gasto_acopio_liquidacion = Decimal("5")
        self.insumos_liquidacion = Decimal("15")
        self.spot_ag_snapshot = None
        self.maquila_aplicada = Decimal("100")
        self.lote = LoteMock(ip="IP-100")


def test_lote_con_liquidacion_anulada_hace_preview(mocker):
    # If the lote has only ANULADA liquidations, it should fallback to preview (calling _calcular_lote with overrides=None)
    mock_calc = mocker.patch(
        "app.services.dashboard_financiero._calcular_lote",
        return_value=({"tms": Decimal("10"), "total_usd": Decimal("1000")}, []),
    )

    lote = LoteMock(liquidaciones_lotes=[LiqLoteMock(estado="ANULADA")])
    db = mocker.Mock(spec=Session)

    res = obtener_snapshot_financiero_lote(db, lote)
    assert res is not None

    # Must have been called with None overrides (preview mode)
    mock_calc.assert_called_once_with(
        db,
        lote,
        spot_usd_override=None,
        bono=Decimal("0"),
        rec_liq_override=None,
        gasto_acopio_override=None,
        gasto_consumo_override=None,
        spot_ag_usd_override=None,
        maquila_override=None,
        valorizar_volado=False,
    )


def test_lote_con_liquidacion_activa_usa_overrides(mocker):
    mock_calc = mocker.patch(
        "app.services.dashboard_financiero._calcular_lote",
        return_value=({"tms": Decimal("10")}, []),
    )

    ll = LiqLoteMock(estado="PAGADA")
    lote = LoteMock(liquidaciones_lotes=[ll])
    db = mocker.Mock(spec=Session)

    obtener_snapshot_financiero_lote(db, lote)

    mock_calc.assert_called_once_with(
        db,
        lote,
        spot_usd_override=Decimal("2400"),
        bono=Decimal("10"),
        rec_liq_override=Decimal("90"),
        gasto_acopio_override=Decimal("5"),
        gasto_consumo_override=Decimal("10"),
        spot_ag_usd_override=None,
        maquila_override=Decimal("100"),
        valorizar_volado=False,
    )


def test_lote_sin_muestreo_retorna_none(mocker):
    alerta_critica = type("Alerta", (), {"critico": True, "mensaje": "Sin muestreo"})
    mocker.patch(
        "app.services.dashboard_financiero._calcular_lote", return_value=({}, [alerta_critica])
    )

    lote = LoteMock()
    db = mocker.Mock(spec=Session)

    res = obtener_snapshot_financiero_lote(db, lote)
    assert res is None


def test_lote_con_alertas_no_criticas_retorna_snap(mocker):
    alerta_normal = type("Alerta", (), {"critico": False, "mensaje": "Lote volado"})
    mocker.patch(
        "app.services.dashboard_financiero._calcular_lote",
        return_value=({"tms": Decimal("10")}, [alerta_normal]),
    )

    lote = LoteMock()
    db = mocker.Mock(spec=Session)

    res = obtener_snapshot_financiero_lote(db, lote)
    assert res is not None
    assert res["tms"] == Decimal("10")
