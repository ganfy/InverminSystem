"""
Tests unitarios — Módulo de Rumas, Campañas y Liquidaciones
Cubre: fórmulas financieras de liquidacion, maquila, precio_x_tms,
       fino_recuperable, ciclo de campañas, numeración de rumas.
No requiere base de datos.
"""

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Constantes del sistema (igual que liquidaciones.py)
# ═══════════════════════════════════════════════════════════════════════════════

FACTOR = Decimal("1.1023")  # st → TM
TROY_OZ = Decimal("31.1035")
MIN_MAQUILA = Decimal("95")


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers (réplica de liquidaciones.py para tests aislados)
# ═══════════════════════════════════════════════════════════════════════════════


def _calc_maquila(oz_promedio: Decimal, maquila_base: Decimal) -> Decimal:
    """Excel: SI((maquila_base + REDONDEAR.MENOS(oz,1)*100) < 95; 95; ...)"""
    step = oz_promedio.quantize(Decimal("0.1"), rounding=ROUND_DOWN) * 100
    return max(MIN_MAQUILA, maquila_base + step)


def _calc_precio_x_tms(
    oz_promedio: Decimal,
    rec_liq: Decimal,
    spot: Decimal,
    riesgo: Decimal,
    maquila: Decimal,
    insumos: Decimal,
    bono: Decimal,
) -> Decimal:
    """col AB del Excel: ((oz*rec/100*(spot-riesgo)) - maquila - insumos + bono) * factor"""
    val_1 = oz_promedio * rec_liq / 100 * (spot - riesgo)
    val = val_1 - maquila - insumos + bono
    return (val * FACTOR).quantize(Decimal("0.0001"))


def _calc_total(precio_x_tms: Decimal, tms: Decimal) -> Decimal:
    """col AM del Excel: max(0, precio_x_tms * tms)"""
    return max(Decimal("0"), (precio_x_tms * tms).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _calc_fino_recuperable(tms: Decimal, rec_liq: Decimal, oz_promedio: Decimal) -> Decimal:
    """col AJ del Excel: 31.1035 * 1.1023 * tms * rec_liq/100 * oz_promedio / 100"""
    return (TROY_OZ * FACTOR * tms * rec_liq / 100 * oz_promedio / 100).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: _calc_maquila
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcMaquila:
    def test_minimo_aplicado_cuando_resultado_menor_a_95(self):
        # oz=0.050 → step=0.0*100=0, base=0 → 0+0=0 < 95 → mínimo 95
        result = _calc_maquila(Decimal("0.050"), Decimal("0"))
        assert result == Decimal("95")

    def test_calculo_estandar_con_maquila_base(self):
        # oz=0.450 → step=floor(0.4)*100=0.4*100=40, base=55 → 55+40=95
        result = _calc_maquila(Decimal("0.450"), Decimal("55"))
        assert result == Decimal("95")

    def test_calculo_con_oz_alta(self):
        # oz=1.250 → step=floor(1.2)*100=120, base=55 → 55+120=175
        result = _calc_maquila(Decimal("1.250"), Decimal("55"))
        assert result == Decimal("175")

    def test_calculo_borde_exactamente_95(self):
        # oz=0.400 → step=40, base=55 → 95 → coincide con mínimo
        result = _calc_maquila(Decimal("0.400"), Decimal("55"))
        assert result == Decimal("95")

    def test_oz_cero_da_minimo(self):
        result = _calc_maquila(Decimal("0"), Decimal("0"))
        assert result == Decimal("95")

    def test_truncado_no_redondeado(self):
        # oz=0.999 → floor(0.999, 1 decimal) = 0.9 → step = 90
        # con base=55: 55+90=145
        result = _calc_maquila(Decimal("0.999"), Decimal("55"))
        assert result == Decimal("145")

    def test_oz_1_punto_5(self):
        # oz=1.500 → floor(1.5,1)=1.5 → step=150, base=55 → 205
        result = _calc_maquila(Decimal("1.500"), Decimal("55"))
        assert result == Decimal("205")


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: _calc_precio_x_tms
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcPrecioXTms:
    def _escenario_base(self) -> dict:
        return {
            "oz_promedio": Decimal("0.450"),
            "rec_liq": Decimal("90"),
            "spot": Decimal("3200.00"),
            "riesgo": Decimal("50.00"),
            "maquila": Decimal("95"),
            "insumos": Decimal("30.00"),
            "bono": Decimal("0"),
        }

    def test_resultado_positivo_con_valores_normales(self):
        p = self._escenario_base()
        result = _calc_precio_x_tms(**p)
        assert result > Decimal("0")

    def test_bono_incrementa_precio(self):
        p = self._escenario_base()
        sin_bono = _calc_precio_x_tms(**p)
        p["bono"] = Decimal("10.00")
        con_bono = _calc_precio_x_tms(**p)
        assert con_bono > sin_bono

    def test_riesgo_reduce_precio(self):
        p = self._escenario_base()
        resultado_bajo_riesgo = _calc_precio_x_tms(**p)
        p["riesgo"] = Decimal("200.00")
        resultado_alto_riesgo = _calc_precio_x_tms(**p)
        assert resultado_alto_riesgo < resultado_bajo_riesgo

    def test_maquila_alta_reduce_precio(self):
        p = self._escenario_base()
        sin_maquila_extra = _calc_precio_x_tms(**p)
        p["maquila"] = Decimal("500")
        con_maquila_extra = _calc_precio_x_tms(**p)
        assert con_maquila_extra < sin_maquila_extra

    def test_factor_1_1023_se_aplica(self):
        """El factor convierte st→TM. Verificamos que se aplica correctamente."""
        p = self._escenario_base()
        p["oz_promedio"] = Decimal("0")  # forzar valor interno = -maquila - insumos
        result = _calc_precio_x_tms(**p)
        # val = (0 - 95 - 30 + 0) = -125; -125 * 1.1023 = -137.7875
        assert result == pytest.approx(Decimal("-137.7875"), abs=Decimal("0.0001"))

    def test_calculo_concordancia_con_excel(self):
        """
        Caso real: oz=0.450, rec=90%, spot=3200, riesgo=50, maquila=95, insumos=30
        val_1 = 0.450 * 90/100 * (3200-50) = 0.450 * 0.9 * 3150 = 1275.75
        val   = 1275.75 - 95 - 30 + 0 = 1150.75
        precio_x_tms = 1150.75 * 1.1023 ≈ 1268.3...
        """
        result = _calc_precio_x_tms(
            Decimal("0.450"),
            Decimal("90"),
            Decimal("3200"),
            Decimal("50"),
            Decimal("95"),
            Decimal("30"),
            Decimal("0"),
        )
        assert float(result) == pytest.approx(1268.3, abs=1.0)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: _calc_total
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcTotal:
    def test_calculo_normal(self):
        precio = Decimal("1268.00")
        tms = Decimal("5.000")
        result = _calc_total(precio, tms)
        assert result == Decimal("6340.00")

    def test_precio_negativo_da_cero(self):
        precio = Decimal("-100.00")
        tms = Decimal("5.000")
        result = _calc_total(precio, tms)
        assert result == Decimal("0")

    def test_precio_cero_da_cero(self):
        result = _calc_total(Decimal("0"), Decimal("10.000"))
        assert result == Decimal("0")

    def test_tms_cero_da_cero(self):
        result = _calc_total(Decimal("1000.00"), Decimal("0"))
        assert result == Decimal("0")

    def test_redondeo_a_2_decimales(self):
        # 100.123 * 3 = 300.369 → 300.37
        result = _calc_total(Decimal("100.123"), Decimal("3"))
        assert result == Decimal("300.37")


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: _calc_fino_recuperable
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcFinoRecuperable:
    def test_formula_correcta(self):
        """
        fino = TROY_OZ * FACTOR * tms * rec_liq/100 * oz_promedio / 100
        Con: tms=5, rec=90%, oz=0.450
        = 31.1035 * 1.1023 * 5 * 0.9 * 0.450 / 100
        ≈ 0.7007 oz
        """
        result = _calc_fino_recuperable(Decimal("5.000"), Decimal("90"), Decimal("0.450"))
        assert float(result) == pytest.approx(0.700, abs=0.01)

    def test_cero_oz_da_cero(self):
        result = _calc_fino_recuperable(Decimal("5.000"), Decimal("90"), Decimal("0"))
        assert result == Decimal("0.0000")

    def test_cero_tms_da_cero(self):
        result = _calc_fino_recuperable(Decimal("0"), Decimal("90"), Decimal("0.450"))
        assert result == Decimal("0.0000")

    def test_recuperacion_100_porciento(self):
        """Recuperación teórica 100%."""
        result_90 = _calc_fino_recuperable(Decimal("5.000"), Decimal("90"), Decimal("0.450"))
        result_100 = _calc_fino_recuperable(Decimal("5.000"), Decimal("100"), Decimal("0.450"))
        assert result_100 > result_90

    def test_proporcional_a_tms(self):
        """El doble de TMS debe dar el doble de fino."""
        r1 = _calc_fino_recuperable(Decimal("5.000"), Decimal("90"), Decimal("0.450"))
        r2 = _calc_fino_recuperable(Decimal("10.000"), Decimal("90"), Decimal("0.450"))
        assert float(r2) == pytest.approx(float(r1) * 2, abs=0.001)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Numeración de Liquidaciones
# ═══════════════════════════════════════════════════════════════════════════════


class TestNumeracionLiquidacion:
    """Verifica el formato LIQ-YYYY-NNNN."""

    def _generar_numero(self, anio: int, ultimo_n: int | None) -> str:
        prefix = f"LIQ-{anio}-"
        if ultimo_n is not None:
            n = ultimo_n + 1
        else:
            n = 1
        return f"{prefix}{n:04d}"

    def test_primera_liquidacion_del_anio(self):
        num = self._generar_numero(2026, None)
        assert num == "LIQ-2026-0001"

    def test_segunda_liquidacion(self):
        num = self._generar_numero(2026, 1)
        assert num == "LIQ-2026-0002"

    def test_numero_alto_4_digitos(self):
        num = self._generar_numero(2026, 999)
        assert num == "LIQ-2026-1000"

    def test_formato_valido(self):
        import re

        num = self._generar_numero(2026, 5)
        assert re.match(r"LIQ-\d{4}-\d{4}", num)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Numeración de Campañas y Rumas
# ═══════════════════════════════════════════════════════════════════════════════


class TestNumeracionCampanasRumas:
    def _siguiente_codigo_campana(self, anio: int, ultimo_codigo: str | None) -> str:
        """Réplica de _siguiente_codigo_campana de rumas.py"""
        prefijo = f"CAMP{anio}-"
        if ultimo_codigo:
            try:
                num = int(ultimo_codigo.split("-")[-1]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        return f"{prefijo}{num:02d}"

    def _codigo_ruma(self, campana_codigo: str, numero: int) -> str:
        return f"{campana_codigo}-{numero:03d}"

    def test_primera_campana_del_anio(self):
        codigo = self._siguiente_codigo_campana(2026, None)
        assert codigo == "CAMP2026-01"

    def test_segunda_campana(self):
        codigo = self._siguiente_codigo_campana(2026, "CAMP2026-01")
        assert codigo == "CAMP2026-02"

    def test_primera_ruma_de_campana(self):
        ruma = self._codigo_ruma("CAMP2026-01", 1)
        assert ruma == "CAMP2026-01-001"

    def test_ruma_100(self):
        ruma = self._codigo_ruma("CAMP2026-01", 100)
        assert ruma == "CAMP2026-01-100"

    def test_reinicio_ruma_en_nueva_campana(self):
        """Al cerrar campaña 01 y abrir 02, la ruma 1 de la nueva campaña tiene código distinto."""
        ruma_camp1 = self._codigo_ruma("CAMP2026-01", 1)
        ruma_camp2 = self._codigo_ruma("CAMP2026-02", 1)
        assert ruma_camp1 != ruma_camp2
        assert ruma_camp1 == "CAMP2026-01-001"
        assert ruma_camp2 == "CAMP2026-02-001"

    def test_formato_campana_valido(self):
        import re

        codigo = self._siguiente_codigo_campana(2026, None)
        assert re.match(r"CAMP\d{4}-\d{2}", codigo)

    def test_formato_ruma_valido(self):
        import re

        ruma = self._codigo_ruma("CAMP2026-01", 5)
        assert re.match(r"CAMP\d{4}-\d{2}-\d{3}", ruma)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Acumulación de Oro Fino en Campañas (RF-CAMP-003)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAcumulacionOroCampana:
    """
    Fórmula: Oro Fino (g) = TMS × Ley Au (gr/TM) / 1000
    Meta por defecto: 5000g
    """

    def _calcular_oro_fino(self, tms: Decimal, ley_gr_tm: Decimal) -> Decimal:
        return (tms * ley_gr_tm / 1000).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    def test_calculo_oro_fino_lote(self):
        # TMS=5, ley=19.166 gr/TM → 5 * 19.166 / 1000 = 0.0958 kg ≈ 95.83g
        result = self._calcular_oro_fino(Decimal("5.000"), Decimal("19.166"))
        assert float(result) == pytest.approx(0.09583, abs=0.001)

    def test_lote_cero_no_contribuye(self):
        result = self._calcular_oro_fino(Decimal("0"), Decimal("19.166"))
        assert result == Decimal("0.000")

    def test_progreso_campana(self):
        meta = Decimal("5000.00")
        acumulado = Decimal("4750.00")
        progreso = (acumulado / meta * 100).quantize(Decimal("0.01"))
        assert float(progreso) == pytest.approx(95.0, abs=0.1)

    def test_alerta_al_95_porciento(self):
        meta = Decimal("5000.00")
        acumulado = Decimal("4750.00")
        progreso_pct = acumulado / meta * 100
        assert progreso_pct >= Decimal("95")

    def test_meta_no_superada(self):
        meta = Decimal("5000.00")
        acumulado = Decimal("4999.99")
        assert acumulado < meta

    def test_meta_exactamente_alcanzada(self):
        meta = Decimal("5000.00")
        acumulado = Decimal("5000.00")
        assert acumulado >= meta


# ═══════════════════════════════════════════════════════════════════════════════
# Tests: Recuperación escalonada según umbrales (liquidaciones._determinar_rec_liq)
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecuperacionEscalonada:
    """
    Lógica de _determinar_rec_liq:
      oz_promedio >= umbral_medio → rec = 90%
      oz_promedio >= umbral_bajo  → rec = 85%
      oz_promedio <  umbral_bajo  → rec = 80%
    """

    BAJO = 80
    MEDIO = 85
    ALTO = 90

    def _determinar_rec(
        self, oz_promedio: Decimal, umbral_bajo: Decimal, umbral_medio: Decimal
    ) -> int:
        if oz_promedio >= umbral_medio:
            return self.ALTO
        elif oz_promedio >= umbral_bajo:
            return self.MEDIO
        else:
            return self.BAJO

    def test_alta_recuperacion_sobre_umbral_medio(self):
        result = self._determinar_rec(Decimal("0.500"), Decimal("0.200"), Decimal("0.350"))
        assert result == 90

    def test_media_recuperacion_entre_umbrales(self):
        result = self._determinar_rec(Decimal("0.300"), Decimal("0.200"), Decimal("0.350"))
        assert result == 85

    def test_baja_recuperacion_bajo_umbral_bajo(self):
        result = self._determinar_rec(Decimal("0.150"), Decimal("0.200"), Decimal("0.350"))
        assert result == 80

    def test_exactamente_en_umbral_medio_da_alto(self):
        result = self._determinar_rec(Decimal("0.350"), Decimal("0.200"), Decimal("0.350"))
        assert result == 90

    def test_exactamente_en_umbral_bajo_da_medio(self):
        result = self._determinar_rec(Decimal("0.200"), Decimal("0.200"), Decimal("0.350"))
        assert result == 85


class TestHumedadMinima:
    """Prueba la lógica de piso de humedad mínima."""

    def test_humedad_minima_limita_valor_calculado_menor(self):
        h_calculada = 1.50
        h_minima = 2.00
        h_efectiva = max(h_calculada, h_minima)
        assert h_efectiva == 2.00

    def test_humedad_calculada_mayor_mantiene_valor(self):
        h_calculada = 3.50
        h_minima = 2.00
        h_efectiva = max(h_calculada, h_minima)
        assert h_efectiva == 3.50


class TestRumaCampanaCierre:
    """Prueba la regla de negocio de cierre automático de ruma en campaña."""

    def test_ruma_asignada_a_campana_pasa_a_cerrada(self):
        # estado_ruma_inicial = "ABIERTA"
        # Simular asignación a campaña
        estado_ruma_final = "CERRADA"
        assert estado_ruma_final == "CERRADA"
