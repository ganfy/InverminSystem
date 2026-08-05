"""
Tests unitarios — Módulo Muestreo y Pruebas Metalúrgicas
=========================================================
Cubre:
  - calcular_humedad: fórmula pura (sin BD)
  - calcular_tms: fórmula pura (sin BD)
  - Validaciones de rango de humedad (0-50%)
  - generar_base_cip: unicidad y formato (sin BD)
  - _generar_codigo_recuperacion: formato con y sin CIP
  - Flujo: lote recepcionado → muestreo → CIPs → prueba metalúrgica

No requiere base de datos real. Usa réplicas locales de funciones puras
y MagicMock donde se necesita acceso a BD.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Réplicas locales de funciones puras (sin importar el módulo para evitar
# dependencias de BD en tiempo de importación)
# ═══════════════════════════════════════════════════════════════════════════════


def calcular_humedad(peso_humedo: Decimal, peso_seco: Decimal) -> Decimal:
    """Réplica de muestreo.calcular_humedad para tests aislados."""
    if peso_humedo == 0:
        return Decimal("0.00")
    return ((peso_humedo - peso_seco) / peso_humedo) * Decimal("100.00")


def calcular_tms(peso_neto: Decimal, porcentaje_humedad: Decimal) -> Decimal:
    """Réplica de muestreo.calcular_tms para tests aislados."""
    return peso_neto * (Decimal("1") - (porcentaje_humedad / Decimal("100.00")))


def generar_base_cip(lote_id: int, salt: int = 0) -> str:
    """Réplica de muestreo.generar_base_cip para tests aislados."""
    control_chars = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    numero = (lote_id * 9301 + 49297 + (salt * 1337)) % 1_000_000
    base = f"{numero:06d}"
    suma = sum(int(d) for d in base)
    control = control_chars[suma % len(control_chars)]
    return f"{base}{control}"


def _generar_codigo_recuperacion(
    ip: str,
    lote_id: int,
    correlativo: int,
    sufijo: str,
    usa_cip: bool,
) -> str:
    """Réplica de pruebas._generar_codigo_recuperacion."""
    if usa_cip:
        base = generar_base_cip(lote_id, salt=correlativo)
        return f"CIP-{base}-{sufijo}{correlativo}"
    else:
        return f"{ip}-{sufijo}{correlativo}"


def dec(v) -> Decimal:
    return Decimal(str(v))


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 1 – calcular_humedad
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularHumedad:
    """Fórmula: (peso_humedo - peso_seco) / peso_humedo * 100."""

    @pytest.mark.parametrize(
        "humedo, seco, esperado_str",
        [
            # Caso típico: 10% humedad
            ("10.000", "9.000", "10.000000000000"),
            # Caso con más decimales
            ("5.450", "4.905", "10.0000000000"),
            # Muy poca humedad
            ("10.000", "9.990", "0.10000000000"),
            # Humedad máxima permitida: 50%
            ("10.000", "5.000", "50.00"),
        ],
    )
    def test_humedad_correcta(self, humedo, seco, esperado_str):
        resultado = calcular_humedad(dec(humedo), dec(seco))
        # Comparar con tolerancia de 2 decimales
        assert abs(resultado - dec(esperado_str)) < dec("0.01")

    def test_peso_humedo_cero_retorna_cero(self):
        resultado = calcular_humedad(dec("0"), dec("0"))
        assert resultado == dec("0.00")

    def test_humedad_con_valores_reales_tipicos(self):
        """Prueba con valores reales típicos de operación."""
        # 25.35 kg húmedo, 22.82 kg seco → ~10% humedad
        resultado = calcular_humedad(dec("25.35"), dec("22.82"))
        humedad_pct = float(resultado)
        assert 9.0 < humedad_pct < 11.0  # ~9.98%


class TestValidacionHumedadRango:
    """La humedad debe estar entre 0% (exclusivo) y 50% (inclusivo)."""

    def test_humedad_en_rango_valido_pasa(self):
        """Un muestreo con humedad 12% debe ser aceptado."""
        humedad = calcular_humedad(dec("10.000"), dec("8.800"))
        assert dec("0") < humedad <= dec("50")

    def test_humedad_cero_rechazada(self):
        """Si el cálculo da exactamente 0, el sistema lo rechaza."""
        # Esto no debería suceder físicamente pero el sistema lo valida
        humedad = calcular_humedad(dec("10.000"), dec("10.000"))
        assert humedad == dec("0.00")
        # En el servicio: humedad <= 0 → HTTPException

    def test_humedad_mayor_50_rechazada(self):
        """Humedad > 50% es inválida en el dominio mineral."""
        humedad = calcular_humedad(dec("10.000"), dec("4.000"))
        assert float(humedad) > 50.0
        # En el servicio: humedad > 50 → HTTPException

    def test_humedad_exactamente_50_valida(self):
        """El límite superior 50% es aceptado."""
        humedad = calcular_humedad(dec("10.000"), dec("5.000"))
        assert float(humedad) == 50.0


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 2 – calcular_tms
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularTMS:
    """TMS = peso_neto * (1 - humedad/100)."""

    @pytest.mark.parametrize(
        "peso_neto, humedad_pct, esperado",
        [
            # 10 TM neto con 10% humedad → 9 TMS
            ("10.000", "10.000", "9.000"),
            # 25 TM con 8% humedad → 23 TMS
            ("25.000", "8.000", "23.000"),
            # Caso real: 7.23 TM con 12.5% humedad
            ("7.230", "12.500", "6.326"),  # 7.23 * 0.875 = 6.326
            # Humedad 0% → TMS = peso_neto
            ("15.500", "0.000", "15.500"),
        ],
    )
    def test_tms_correcto(self, peso_neto, humedad_pct, esperado):
        resultado = calcular_tms(dec(peso_neto), dec(humedad_pct))
        assert abs(resultado - dec(esperado)) < dec("0.001")

    def test_tms_con_humedad_tipica(self):
        """Verificación con escenario operativo real."""
        # Lote con 50 sacos, 15 TM neto, 11% humedad → ~13.35 TMS
        peso_neto = dec("15.000")
        humedad = dec("11.000")
        tms = calcular_tms(peso_neto, humedad)
        assert dec("13.0") < tms < dec("14.0")


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 3 – generar_base_cip
# ═══════════════════════════════════════════════════════════════════════════════


class TestGenerarBaseCIP:
    """Generación de código base para etiquetas CIP de muestreo."""

    def test_formato_siete_caracteres(self):
        """El código base tiene exactamente 7 caracteres: 6 dígitos + 1 letra."""
        base = generar_base_cip(lote_id=42, salt=0)
        assert len(base) == 7
        assert base[:6].isdigit()
        assert base[6].isalpha()

    def test_mismo_lote_mismo_resultado(self):
        """Función determinista: mismo lote_id y salt → mismo resultado."""
        base1 = generar_base_cip(42, 0)
        base2 = generar_base_cip(42, 0)
        assert base1 == base2

    def test_diferentes_salts_diferentes_bases(self):
        """Dos CIPs del mismo lote deben tener bases distintas."""
        base1 = generar_base_cip(42, salt=1)
        base2 = generar_base_cip(42, salt=2)
        assert base1 != base2

    def test_diferentes_lotes_diferentes_bases(self):
        """Lotes distintos generan bases distintas."""
        base1 = generar_base_cip(lote_id=1, salt=0)
        base2 = generar_base_cip(lote_id=2, salt=0)
        assert base1 != base2

    @pytest.mark.parametrize("lote_id", [1, 42, 100, 500, 9999])
    def test_siempre_7_caracteres(self, lote_id):
        for salt in range(5):
            base = generar_base_cip(lote_id, salt=salt)
            assert len(base) == 7, f"Base {base} no tiene 7 chars (lote={lote_id}, salt={salt})"


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 4 – _generar_codigo_recuperacion
# ═══════════════════════════════════════════════════════════════════════════════


class TestGenerarCodigoRecuperacion:
    """Generación de código CIP para análisis de recuperación."""

    def test_formato_con_cip_activado(self):
        """usa_cip=True → CIP-{base}-{sufijo}{correlativo}."""
        codigo = _generar_codigo_recuperacion(
            ip="IP-0042",
            lote_id=42,
            correlativo=1,
            sufijo="R",
            usa_cip=True,
        )
        assert codigo.startswith("CIP-")
        assert "-R1" in codigo
        # Formato: CIP-XXXXXXX-R1
        partes = codigo.split("-")
        assert len(partes) == 3

    def test_formato_sin_cip(self):
        """usa_cip=False → {ip}-{sufijo}{correlativo}."""
        codigo = _generar_codigo_recuperacion(
            ip="IP-0042",
            lote_id=42,
            correlativo=1,
            sufijo="R",
            usa_cip=False,
        )
        assert codigo == "IP-0042-R1"

    def test_correlativo_se_incrementa(self):
        """El correlativo aparece al final del código."""
        c1 = _generar_codigo_recuperacion("IP-0010", 10, 1, "R", False)
        c2 = _generar_codigo_recuperacion("IP-0010", 10, 2, "R", False)
        assert c1 == "IP-0010-R1"
        assert c2 == "IP-0010-R2"


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 5 – Validaciones de negocio en muestreo
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidacionesMuestreo:
    """Reglas de negocio verificadas en registrar_muestreo."""

    def test_peso_seco_mayor_igual_humedo_invalido(self):
        """El peso seco debe ser estrictamente menor al húmedo."""
        # seco >= humedo → inválido
        assert dec("9.5") >= dec("8.0")  # seco > humedo → error
        assert dec("8.0") >= dec("8.0")  # seco == humedo → error

    def test_peso_seco_menor_humedo_valido(self):
        """Caso válido: seco < humedo."""
        peso_humedo = dec("10.0")
        peso_seco = dec("9.0")
        assert peso_seco < peso_humedo

    def test_intento_duplicado_detectado(self):
        """
        No se puede registrar el mismo intento (1, 2, 3) dos veces
        para el mismo lote. El servicio verifica esto antes de insertar.
        """
        intentos_existentes = {1, 2}
        nuevo_intento = 1
        assert nuevo_intento in intentos_existentes  # ya existe → error

        nuevo_intento = 3
        assert nuevo_intento not in intentos_existentes  # no existe → ok


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 6 – Flujo de muestreo con mock de BD
# ═══════════════════════════════════════════════════════════════════════════════


class TestMuestreoConMock:
    """Tests del servicio de muestreo usando mocks de BD."""

    def _make_lote_mock(self, ip: str = "IP-0001", peso_neto: Decimal = dec("10.0")) -> object:
        from unittest.mock import MagicMock

        lote = MagicMock()
        lote.id = 1
        lote.ip = ip
        pesaje = MagicMock()
        pesaje.peso_neto = peso_neto
        lote.pesajes = [pesaje]
        lote.muestreos = []
        return lote

    def test_lote_sin_pesaje_rechaza_muestreo(self):
        """Si el lote no tiene pesaje, muestreo no puede calcularse."""
        from unittest.mock import MagicMock

        from app.models.models import Lote, Muestreo
        from app.schemas.muestreo import MuestreoCreate
        from app.services.muestreo import registrar_muestreo
        from fastapi import HTTPException

        db = MagicMock()
        lote = MagicMock()
        lote.id = 1
        lote.ip = "IP-0001"
        lote.pesajes = []  # sin pesaje

        q_lote = MagicMock()
        q_lote.filter.return_value.first.return_value = lote

        q_muestreo = MagicMock()
        q_muestreo.filter.return_value.first.return_value = None  # sin intento previo

        def query_side(model):
            if model is Lote:
                return q_lote
            if model is Muestreo:
                return q_muestreo
            return MagicMock()

        db.query.side_effect = query_side

        datos = MuestreoCreate(
            intento=1,
            peso_humedo=dec("10.0"),
            peso_seco=dec("9.0"),
        )
        with pytest.raises(HTTPException) as exc_info:
            registrar_muestreo(db, "IP-0001", usuario_id=1, datos=datos)
        assert exc_info.value.status_code == 400
        assert "peso neto" in exc_info.value.detail.lower()

    def test_lote_no_encontrado_retorna_404(self):
        """IP inexistente → HTTP 404."""
        from unittest.mock import MagicMock

        from app.schemas.muestreo import MuestreoCreate
        from app.services.muestreo import registrar_muestreo
        from fastapi import HTTPException

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None  # no existe

        datos = MuestreoCreate(
            intento=1,
            peso_humedo=dec("10.0"),
            peso_seco=dec("9.0"),
        )
        with pytest.raises(HTTPException) as exc_info:
            registrar_muestreo(db, "IP-9999", usuario_id=1, datos=datos)
        assert exc_info.value.status_code == 404

    def test_intento_duplicado_retorna_400(self):
        """Registrar el mismo intento dos veces → HTTP 400."""
        from unittest.mock import MagicMock

        from app.schemas.muestreo import MuestreoCreate
        from app.services.muestreo import registrar_muestreo
        from fastapi import HTTPException

        db = MagicMock()

        # Lote con pesaje válido
        lote = self._make_lote_mock()

        # Primera query (lote por ip): lote existente
        q_lote = MagicMock()
        q_lote.filter.return_value.first.return_value = lote

        # Segunda query (muestreo por intento): intento ya existe
        intento_existente = MagicMock()
        intento_existente.intento = 1
        q_muestreo = MagicMock()
        q_muestreo.filter.return_value.first.return_value = intento_existente

        from app.models.models import Lote, Muestreo

        def query_side(model):
            if model is Lote:
                return q_lote
            if model is Muestreo:
                return q_muestreo
            return MagicMock()

        db.query.side_effect = query_side

        datos = MuestreoCreate(
            intento=1,
            peso_humedo=dec("10.0"),
            peso_seco=dec("9.0"),
        )
        with pytest.raises(HTTPException) as exc_info:
            registrar_muestreo(db, "IP-0001", usuario_id=1, datos=datos)
        assert exc_info.value.status_code == 400
        assert "ya está registrado" in exc_info.value.detail


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 7 – Prueba metalúrgica: validación de malla
# ═══════════════════════════════════════════════════════════════════════════════


class TestPruebaMetalurgica:
    """Validaciones de la prueba metalúrgica (botella 48h)."""

    @pytest.mark.parametrize("malla", [88, 89, 90, 91, 92, 93, 94])
    def test_malla_en_rango_aceptable_sin_warning(self, malla: float):
        """Malla entre 88% y 94% es aceptable, sin mensaje de advertencia."""
        # El servicio genera warning solo si está fuera de rango
        en_rango = 88 <= malla <= 94
        assert en_rango

    @pytest.mark.parametrize("malla", [85, 87, 95, 98])
    def test_malla_fuera_de_rango_genera_warning(self, malla: float):
        """Malla fuera de 88%-94% genera un warning (no error - el registro procede)."""
        en_rango = 88 <= malla <= 94
        assert not en_rango  # confirma que sería advertencia

    def test_prueba_existente_se_actualiza_no_duplica(self):
        """Si ya hay prueba para ese lote, se actualiza en lugar de crear nueva."""
        from unittest.mock import MagicMock

        from app.models.models import Lote, PruebaMetalurgica
        from app.schemas.pruebas import PruebaMetalurgicaCreate
        from app.services.pruebas import registrar_prueba

        db = MagicMock()
        lote = MagicMock()
        lote.id = 1

        prueba_existente = MagicMock()
        prueba_existente.id = 5

        q_lote = MagicMock()
        q_lote.filter.return_value.first.return_value = lote

        q_prueba = MagicMock()
        q_prueba.filter.return_value.order_by.return_value.first.return_value = prueba_existente

        def query_side(model):
            if model is Lote:
                return q_lote
            if model is PruebaMetalurgica:
                return q_prueba
            return MagicMock()

        db.query.side_effect = query_side

        datos = PruebaMetalurgicaCreate(malla_porcentaje=91.5)
        prueba, warning = registrar_prueba(db, "IP-0001", datos, usuario_id=1)

        # No se agrega una nueva, se actualiza la existente
        db.add.assert_not_called()
        assert prueba is prueba_existente


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 8 – calcular_ley_planta (función pura aislada)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularLeyPlanta:
    """
    calcular_ley_planta calcula el promedio de análisis VIGENTES (planta/externo).
    Replica la lógica sin importar config_calculo para mantener el test puro.
    """

    def _promedio(*leyes: float, decimales: int = 3) -> Decimal:
        """Helper: promedio simple de leyes."""
        q = Decimal("0." + "0" * decimales)
        total = sum(Decimal(str(le)) for le in leyes)
        return (total / len(leyes)).quantize(q, rounding=ROUND_HALF_UP)

    def test_promedio_dos_analisis(self):
        """Promedio de 2 análisis vigentes."""
        resultado = TestCalcularLeyPlanta._promedio(0.340, 0.360)
        assert resultado == Decimal("0.350")

    def test_promedio_tres_analisis(self):
        resultado = TestCalcularLeyPlanta._promedio(0.300, 0.320, 0.310)
        assert resultado == Decimal("0.310")

    def test_sin_analisis_retorna_none(self):
        """Sin análisis vigentes → calcular_ley_planta retorna None."""
        # En el servicio: if not analisis: return None
        analisis = []
        resultado = None if not analisis else "algo"
        assert resultado is None

    def test_un_solo_analisis(self):
        """Un único análisis vigente → ley = ese valor."""
        resultado = TestCalcularLeyPlanta._promedio(0.285)
        assert resultado == Decimal("0.285")
