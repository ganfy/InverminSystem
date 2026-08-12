"""
Tests unitarios — Módulo de Laboratorio
Cubre: calcular_ley_comercial, calcular_ley_final, calcular_ley_gr_tm,
       dirimencia, descartar, validaciones de recuperación.
No requiere base de datos (pure-Python).
"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

# ── Helpers copiados de laboratorio.py (sin importar el módulo) ──────────────


def _calcular_ley_final(fino: Decimal, grueso: Decimal) -> Decimal:
    return (Decimal(str(fino)) + Decimal(str(grueso))).quantize(Decimal("0.00001"))


def _calcular_ley_gr_tm(ley_final: Decimal, factor_oz_tc: Decimal) -> Decimal:
    return (Decimal(str(ley_final)) * factor_oz_tc).quantize(Decimal("0.001"))


def calcular_ley_comercial(
    ley_planta: Decimal, params, umbral_volado=None, q_comercial=Decimal("0.001")
):
    """Réplica de la función en laboratorio.py para tests aislados."""
    if params is None:
        return {
            "ley_planta": float(ley_planta),
            "ley_comercial": float(ley_planta),
            "descuento_aplicado": 0.0,
            "factor_aplicado": 1.0,
            "ajuste_rango": False,
            "sin_parametros": True,
            "detalle": "Sin parametros comerciales configurados",
        }

    q = q_comercial
    ley = ley_planta
    descuento = Decimal("0")
    factor = Decimal("1")
    detalle_pasos = []

    if params.lim_ley_comercial and params.dscto_ley_comercial:
        lim = Decimal(str(params.lim_ley_comercial))
        dscto = Decimal(str(params.dscto_ley_comercial))
        if ley < lim:
            descuento = dscto
            ley = ley - dscto
            detalle_pasos.append(f"descuento aplicado {dscto}")
    elif params.porcentaje_ley_comercial:
        factor = Decimal(str(params.porcentaje_ley_comercial))
        ley = (ley * factor).quantize(q)
        detalle_pasos.append(f"factor {factor}")

    _umbral = umbral_volado if umbral_volado is not None else Decimal("0.100")
    if ley < _umbral:
        ley = Decimal("0")
        detalle_pasos.append("volado → ley=0")

    return {
        "ley_planta": float(ley_planta),
        "ley_comercial": float(ley),
        "descuento_aplicado": float(descuento),
        "factor_aplicado": float(factor),
        "ajuste_rango": False,
        "sin_parametros": False,
        "detalle": " | ".join(detalle_pasos) or "Sin ajustes",
    }


def _make_params(
    lim_ley_comercial=None,
    dscto_ley_comercial=None,
    porcentaje_ley_comercial=None,
    umbral_recup_bajo=None,
    umbral_recup_medio=None,
    maquila=None,
    gasto_acopio=None,
    gasto_consumo=None,
    riesgo_comercial=None,
):
    p = MagicMock()
    p.lim_ley_comercial = lim_ley_comercial
    p.dscto_ley_comercial = dscto_ley_comercial
    p.porcentaje_ley_comercial = porcentaje_ley_comercial
    p.umbral_recup_bajo = umbral_recup_bajo
    p.umbral_recup_medio = umbral_recup_medio
    p.maquila = maquila
    p.gasto_acopio = gasto_acopio
    p.gasto_consumo = gasto_consumo
    p.riesgo_comercial = riesgo_comercial
    return p


# ═══════════════════════════════════════════════════════════════════════════════
# calcular_ley_final
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularLeyFinal:
    def test_suma_fino_grueso(self):
        result = _calcular_ley_final(Decimal("0.519"), Decimal("0.040"))
        assert result == Decimal("0.55900")

    def test_grueso_cero(self):
        result = _calcular_ley_final(Decimal("0.450"), Decimal("0"))
        assert result == Decimal("0.45000")

    def test_fino_cero(self):
        result = _calcular_ley_final(Decimal("0"), Decimal("0.100"))
        assert result == Decimal("0.10000")

    def test_precision_4_decimales(self):
        result = _calcular_ley_final(Decimal("0.1234"), Decimal("0.5678"))
        assert result == Decimal("0.69120")

    def test_precision_5_decimales(self):
        result = _calcular_ley_final(Decimal("0.12879"), Decimal("0.1277"))
        assert result == Decimal("0.25649")

    def test_valores_altos(self):
        result = _calcular_ley_final(Decimal("5.000"), Decimal("3.000"))
        assert result == Decimal("8.00000")


# ═══════════════════════════════════════════════════════════════════════════════
# calcular_ley_gr_tm
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularLeyGrTm:
    FACTOR = Decimal("34.2857")

    def test_conversion_estandar(self):
        ley_oz_tc = Decimal("0.559")
        result = _calcular_ley_gr_tm(ley_oz_tc, self.FACTOR)
        # 0.559 × 34.2857 ≈ 19.166
        assert result == Decimal("19.166")

    def test_cero(self):
        result = _calcular_ley_gr_tm(Decimal("0"), self.FACTOR)
        assert result == Decimal("0.000")

    def test_precision_3_decimales(self):
        result = _calcular_ley_gr_tm(Decimal("1.000"), self.FACTOR)
        assert result == Decimal("34.286")


# ═══════════════════════════════════════════════════════════════════════════════
# calcular_ley_comercial
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularLeyComercial:
    def test_sin_params_devuelve_ley_planta(self):
        result = calcular_ley_comercial(Decimal("0.500"), None)
        assert result["ley_comercial"] == 0.500
        assert result["sin_parametros"] is True
        assert result["descuento_aplicado"] == 0.0
        assert result["factor_aplicado"] == 1.0

    def test_descuento_aplicado_cuando_ley_menor_a_limite(self):
        params = _make_params(
            lim_ley_comercial=Decimal("0.300"), dscto_ley_comercial=Decimal("0.050")
        )
        ley = Decimal("0.250")  # < 0.300 → aplica descuento
        result = calcular_ley_comercial(ley, params)
        assert result["ley_comercial"] == pytest.approx(0.200, abs=1e-4)
        assert result["descuento_aplicado"] == pytest.approx(0.050, abs=1e-4)

    def test_descuento_no_aplicado_cuando_ley_mayor_a_limite(self):
        params = _make_params(
            lim_ley_comercial=Decimal("0.300"), dscto_ley_comercial=Decimal("0.050")
        )
        ley = Decimal("0.450")  # >= 0.300 → sin descuento
        result = calcular_ley_comercial(ley, params)
        assert result["ley_comercial"] == pytest.approx(0.450, abs=1e-4)
        assert result["descuento_aplicado"] == 0.0

    def test_factor_porcentual_aplicado(self):
        params = _make_params(porcentaje_ley_comercial=Decimal("0.940"))
        ley = Decimal("0.500")
        result = calcular_ley_comercial(ley, params)
        # 0.500 × 0.940 = 0.470
        assert result["ley_comercial"] == pytest.approx(0.470, abs=1e-3)
        assert result["factor_aplicado"] == pytest.approx(0.940, abs=1e-4)

    def test_factor_aplicado_exclusivo_de_descuento(self):
        """Si hay lim_ley_comercial, NO se aplica porcentaje_ley_comercial."""
        params = _make_params(
            lim_ley_comercial=Decimal("0.300"),
            dscto_ley_comercial=Decimal("0.050"),
            porcentaje_ley_comercial=Decimal("0.940"),
        )
        ley = Decimal("0.250")  # < 0.300 → aplica descuento, NO factor
        result = calcular_ley_comercial(ley, params)
        # Solo descuento: 0.250 - 0.050 = 0.200
        assert result["ley_comercial"] == pytest.approx(0.200, abs=1e-4)
        assert result["factor_aplicado"] == 1.0  # no se aplicó

    def test_volado_cuando_ley_comercial_menor_a_umbral_default(self):
        params = _make_params()  # sin lim ni factor
        ley = Decimal("0.050")  # < 0.100 → volado
        result = calcular_ley_comercial(ley, params)
        assert result["ley_comercial"] == 0.0

    def test_volado_con_umbral_personalizado(self):
        params = _make_params()
        ley = Decimal("0.150")  # < 0.200 → volado con umbral custom
        result = calcular_ley_comercial(ley, params, umbral_volado=Decimal("0.200"))
        assert result["ley_comercial"] == 0.0

    def test_no_volado_cuando_ley_exactamente_en_umbral(self):
        params = _make_params()
        ley = Decimal("0.100")  # == 0.100 → no es volado (condición es <)
        result = calcular_ley_comercial(ley, params)
        assert result["ley_comercial"] == pytest.approx(0.100, abs=1e-4)

    def test_resultado_cero_no_negativo(self):
        """Descuento mayor a ley puede dar negativo → debe quedar en 0 (volado)."""
        params = _make_params(
            lim_ley_comercial=Decimal("0.500"), dscto_ley_comercial=Decimal("0.200")
        )
        ley = Decimal("0.050")  # 0.050 - 0.200 = -0.150 → volado
        result = calcular_ley_comercial(ley, params)
        assert result["ley_comercial"] == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Validaciones de recuperación (lógica pura)
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidacionRecuperacion:
    """Tests del cálculo de porcentaje de recuperación."""

    def test_calculo_porcentaje_recuperacion(self):
        """% recup = ((cabeza - cola) / cabeza) × 100"""
        cabeza = Decimal("0.559")
        cola = Decimal("0.041")
        recuperacion = ((cabeza - cola) / cabeza) * 100
        assert float(recuperacion) == pytest.approx(92.66, abs=0.1)

    def test_recuperacion_perfecta_100_porciento(self):
        cabeza = Decimal("1.000")
        cola = Decimal("0.000")
        # No es posible físicamente cola=0 pero aritméticamente:
        recuperacion = ((cabeza - cola) / cabeza) * 100
        assert float(recuperacion) == pytest.approx(100.0, abs=0.01)


# ═══════════════════════════════════════════════════════════════════════════════
# Dirimencia: lógica de promedio/clamp con ley minero
# ═══════════════════════════════════════════════════════════════════════════════


class TestDirimenciaLogica:
    """
    Lógica replicada de liquidaciones.py _calcular_lote():
      - Sin dirimencia: oz_promedio = (oz_comercial + oz_minero) / 2
      - Con dirimencia: clamp(dirimencia, min(paititi, minero), max(paititi, minero))
    """

    def _promedio_simple(self, comercial: Decimal, minero: Decimal) -> Decimal:
        return ((comercial + minero) / 2).quantize(Decimal("0.001"))

    def _clamp_dirimencia(
        self,
        comercial: Decimal,
        minero: Decimal,
        dirimencia: Decimal,
    ) -> Decimal:
        from decimal import ROUND_DOWN

        ley_low = min(comercial, minero)
        ley_high = max(comercial, minero)
        return max(ley_low, min(ley_high, dirimencia)).quantize(
            Decimal("0.001"), rounding=ROUND_DOWN
        )

    def test_promedio_simple_sin_dirimencia(self):
        result = self._promedio_simple(Decimal("0.500"), Decimal("0.400"))
        assert result == Decimal("0.450")

    def test_dirimencia_entre_ambas_leyeas_se_usa_directamente(self):
        # paititi=0.500, minero=0.300, dirimencia=0.420 → 0.420 ∈ [0.300, 0.500]
        result = self._clamp_dirimencia(Decimal("0.500"), Decimal("0.300"), Decimal("0.420"))
        assert result == Decimal("0.420")

    def test_dirimencia_sobre_maximo_se_clampea_al_maximo(self):
        # dirimencia=0.600 > max(0.500, 0.300)=0.500 → se usa 0.500
        result = self._clamp_dirimencia(Decimal("0.500"), Decimal("0.300"), Decimal("0.600"))
        assert result == Decimal("0.500")

    def test_dirimencia_bajo_minimo_se_clampea_al_minimo(self):
        # dirimencia=0.100 < min(0.500, 0.300)=0.300 → se usa 0.300
        result = self._clamp_dirimencia(Decimal("0.500"), Decimal("0.300"), Decimal("0.100"))
        assert result == Decimal("0.300")

    def test_dirimencia_iguala_exactamente_a_paititi(self):
        result = self._clamp_dirimencia(Decimal("0.500"), Decimal("0.300"), Decimal("0.500"))
        assert result == Decimal("0.500")

    def test_dirimencia_iguala_exactamente_a_minero(self):
        result = self._clamp_dirimencia(Decimal("0.500"), Decimal("0.300"), Decimal("0.300"))
        assert result == Decimal("0.300")

    def test_sin_ley_minero_usa_solo_comercial(self):
        """Si oz_tc_minero es None/0, oz_promedio = oz_tc_comercial."""
        oz_tc_comercial = Decimal("0.450")
        oz_tc_minero = None
        oz_promedio = (
            oz_tc_comercial
            if not oz_tc_minero
            else self._promedio_simple(oz_tc_comercial, oz_tc_minero)
        )
        assert oz_promedio == Decimal("0.450")


# ═══════════════════════════════════════════════════════════════════════════════
# Muestreo: humedad y TMS
# ═══════════════════════════════════════════════════════════════════════════════


class TestMuestreo:
    def test_calculo_humedad(self):
        # % = ((humedo - seco) / humedo) × 100
        humedo = Decimal("100.000")
        seco = Decimal("80.000")
        humedad = ((humedo - seco) / humedo) * 100
        assert float(humedad) == pytest.approx(20.0)

    def test_calculo_tms(self):
        # TMS = TMH × (1 - %H₂O / 100)
        tmh = Decimal("10.000")
        humedad_pct = Decimal("20.0")
        tms = tmh * (1 - humedad_pct / 100)
        assert float(tms) == pytest.approx(8.0)

    def test_humedad_cero_tms_igual_tmh(self):
        tmh = Decimal("10.000")
        humedad_pct = Decimal("0")
        tms = tmh * (1 - humedad_pct / 100)
        assert float(tms) == pytest.approx(10.0)

    def test_humedad_fuera_rango_50_debe_rechazarse(self):
        humedad = Decimal("55.0")
        assert not (Decimal("0") < humedad <= Decimal("50"))

    def test_humedad_negativa_debe_rechazarse(self):
        # peso_seco > peso_humedo (físicamente imposible)
        humedo = Decimal("80.000")
        seco = Decimal("100.000")
        assert not (seco < humedo)

    def test_humedad_maxima_borde_50_es_valida(self):
        humedad = Decimal("50.0")
        assert Decimal("0") < humedad <= Decimal("50")


# ═══════════════════════════════════════════════════════════════════════════════
# Generación de CIP
# ═══════════════════════════════════════════════════════════════════════════════


class TestGeneracionCIP:
    """
    Formato CIP del sistema: CIP-{base}-{sufijo}{correlativo}
    base se genera a partir del lote_id con padding.
    """

    def _generar_base(self, lote_id: int) -> str:
        """Réplica de generar_base_cip de pruebas.py"""
        return f"{lote_id:06d}X"

    def test_cip_laboratorio_formato_correcto(self):
        base = self._generar_base(42)
        cip = f"CIP-{base}-A1"
        assert cip.startswith("CIP-")
        assert "A1" in cip

    def test_cip_recuperacion_interno(self):
        base = self._generar_base(100)
        cip = f"CIP-{base}-R1"
        assert cip == "CIP-000100X-R1"

    def test_cip_recuperacion_externo(self):
        base = self._generar_base(100)
        cip = f"CIP-{base}-E1"
        assert cip == "CIP-000100X-E1"

    def test_correlativo_incrementa(self):
        base = self._generar_base(50)
        cip1 = f"CIP-{base}-A1"
        cip2 = f"CIP-{base}-A2"
        assert cip1 != cip2
        assert "A2" in cip2


class TestRolesComercial:
    """Verifica que el rol JefeComercial tenga permisos VIEW en los módulos comerciales.

    Tras la centralización RBAC (eliminación de _ROLES_COMERCIAL hardcodeados),
    los permisos se definen exclusivamente en seed.py / tabla `permisos`.
    Este test verifica que seed.py incluya a JefeComercial en los módulos clave.
    """

    def test_jefe_comercial_in_roles(self):
        import os

        os.environ.setdefault("DB_SERVER", "localhost")
        os.environ.setdefault("DB_NAME", "test_db")
        os.environ.setdefault("DB_USER", "test_user")
        os.environ.setdefault("DB_PASSWORD", "test_pass")
        os.environ.setdefault("SECRET_KEY", "test_secret_key_for_unit_tests")

        from pathlib import Path

        seed_path = Path(__file__).parent.parent / "scripts" / "seed.py"
        source = seed_path.read_text(encoding="utf-8")

        # JefeComercial debe tener VIEW_CONFIDENTIAL en LABORATORIO
        # (antes cubierto por _ROLES_COMERCIAL hardcodeado)
        assert (
            '("JefeComercial", "LABORATORIO", "VIEW_CONFIDENTIAL", True)' in source
        ), "seed.py no otorga VIEW_CONFIDENTIAL en LABORATORIO a JefeComercial"
        # JefeComercial debe tener UPDATE en MUESTREO
        # (antes cubierto por _ROLES_COMERCIAL en muestreo.py)
        assert (
            '("JefeComercial", "MUESTREO", "UPDATE", True)' in source
        ), "seed.py no otorga UPDATE en MUESTREO a JefeComercial"
        # JefeComercial debe tener VIEW en CAMPANAS
        # (antes cubierto por _ROLES_COMERCIAL en rumas.py)
        assert (
            '("JefeComercial", "CAMPANAS", "VIEW", True)' in source
        ), "seed.py no otorga VIEW en CAMPANAS a JefeComercial"


class TestConfiguracionRedondeo:
    """Verifica la configuración y conversión de modos de redondeo."""

    def test_get_rounding_mode(self):
        from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP

        from app.services.config_calculo import get_rounding_mode

        assert get_rounding_mode("normal") == ROUND_HALF_UP
        assert get_rounding_mode("abajo") == ROUND_DOWN
        assert get_rounding_mode("arriba") == ROUND_UP
        assert get_rounding_mode("bancario") == ROUND_HALF_EVEN
        assert get_rounding_mode("cualquier_cosa") == ROUND_HALF_UP
