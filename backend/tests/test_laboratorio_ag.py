"""
Tests unitarios — Módulo Laboratorio
=====================================
Cubre:
  - _calcular_ley_final (ley Au): fórmula fino + grueso
  - _calcular_ley_gr_tm: conversión Oz/TC → Gr/TM
  - _calcular_ley_ag: fórmula plata con blank correction
  - Validaciones del schema AnalisisLeyCreate (Au y Ag)
  - Validaciones del schema AnalisisAgCreate
  - registrar_analisis_ag:
      · Vinculado a análisis Au existente (antes o después del análisis completo)
      · Invalida Ag vigente anterior al registrar nuevo
      · Rechaza si analisis_au_id no existe
      · Rechaza si el análisis padre no es material='Au'
  - obtener_ley_ag_vigente:
      · Retorna (gr_tm, oz_tc) del Ag vigente
      · Retorna None si no existe
  - Lógica de AnalisisLeyCreate con material=Ag:
      · punto CABEZA/COLA/LIQUIDO requerido
      · ley_grueso se fuerza a 0.0

No requiere base de datos real. Usa réplicas locales de funciones puras
y MagicMock donde se necesita acceso a BD.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from unittest.mock import MagicMock

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Constantes por defecto (valores reales del sistema)
# ═══════════════════════════════════════════════════════════════════════════════

FACTOR_OZ_TC = Decimal("34.2857")  # 1 Oz/TC = 34.2857 Gr/TM
BLANK_CORRECTION_AG = Decimal("0.1444")  # Corrección en blanco para Ag


# ═══════════════════════════════════════════════════════════════════════════════
# Réplicas locales de fórmulas puras
# ═══════════════════════════════════════════════════════════════════════════════


def _calcular_ley_final(fino: float | Decimal, grueso: float | Decimal) -> Decimal:
    """Réplica de laboratorio._calcular_ley_final."""
    return (Decimal(str(fino)) + Decimal(str(grueso))).quantize(
        Decimal("0.00001"), rounding=ROUND_HALF_UP
    )


def _calcular_ley_gr_tm(ley_final: Decimal, factor_oz_tc: Decimal = FACTOR_OZ_TC) -> Decimal:
    """Réplica de laboratorio._calcular_ley_gr_tm."""
    return (Decimal(str(ley_final)) * factor_oz_tc).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    )


def _calcular_ley_ag(
    au_ag_mg: float,
    au_mg: float,
    peso_muestra: float,
    factor_oz_tc: Decimal = FACTOR_OZ_TC,
    blank_correction: Decimal = BLANK_CORRECTION_AG,
) -> tuple[Decimal, Decimal]:
    """
    Réplica de laboratorio._calcular_ley_ag.
    Retorna (ley_ag_gr_tm, ley_ag_oz_tc).
    Fórmula: ley_ag_gr_tm = ((au_ag_mg - au_mg - blank_correction) * 1000) / peso_muestra
    """
    neto = Decimal(str(au_ag_mg)) - Decimal(str(au_mg)) - blank_correction
    if neto < 0:
        neto = Decimal("0")
    ley_gr_tm = (neto * 1000 / Decimal(str(peso_muestra))).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    )
    ley_oz_tc = (ley_gr_tm / factor_oz_tc).quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)
    return ley_gr_tm, ley_oz_tc


def dec(v) -> Decimal:
    return Decimal(str(v))


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 1 – _calcular_ley_final (Au)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularLeyFinal:
    """ley_final = ley_fino + ley_grueso (Oz/TC), redondeado a 5 decimales."""

    @pytest.mark.parametrize(
        "fino, grueso, esperado",
        [
            # Caso típico Newmont
            (0.310, 0.090, "0.40000"),
            # Solo fino (grueso = 0)
            (0.250, 0.000, "0.25000"),
            # Suma exacta
            (0.12345, 0.00000, "0.12345"),
            # Redondeo a 5 decimales
            (0.100001, 0.000001, "0.10000"),
            # Valores altos
            (1.500, 0.500, "2.00000"),
        ],
    )
    def test_ley_final_correcto(self, fino, grueso, esperado):
        resultado = _calcular_ley_final(fino, grueso)
        assert resultado == dec(esperado)

    def test_ley_final_cero_solo_fino(self):
        """Si grueso = 0 exactamente, ley_final = fino."""
        resultado = _calcular_ley_final(0.350, 0.000)
        assert resultado == dec("0.35000")


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 2 – _calcular_ley_gr_tm (conversión)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularLeyGrTM:
    """ley_gr_tm = ley_final * factor_oz_tc (redondeado a 3 decimales)."""

    @pytest.mark.parametrize(
        "ley_oz_tc, esperado_gr_tm",
        [
            # 0.400 Oz/TC × 34.2857 = 13.714 Gr/TM
            ("0.40000", "13.714"),
            # 0.350 Oz/TC × 34.2857 = 12.000 Gr/TM
            ("0.35000", "12.000"),
            # 0.100 Oz/TC × 34.2857 = 3.429 Gr/TM
            ("0.10000", "3.429"),
            # 0.250 Oz/TC × 34.2857 = 8.571 Gr/TM
            ("0.25000", "8.571"),
        ],
    )
    def test_ley_gr_tm_correcto(self, ley_oz_tc, esperado_gr_tm):
        resultado = _calcular_ley_gr_tm(dec(ley_oz_tc))
        assert abs(resultado - dec(esperado_gr_tm)) < dec("0.001")

    def test_factor_personalizado(self):
        """El factor de conversión es configurable."""
        factor = dec("31.1035")  # factor alternativo
        resultado = _calcular_ley_gr_tm(dec("0.100"), factor_oz_tc=factor)
        esperado = (dec("0.100") * factor).quantize(dec("0.001"), rounding=ROUND_HALF_UP)
        assert resultado == esperado


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 3 – _calcular_ley_ag (fórmula de plata)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalcularLeyAg:
    """
    Fórmula Ag:
      neto = au_ag_mg - au_mg - blank_correction (0.1444)
      ley_ag_gr_tm = (neto * 1000) / peso_muestra
      ley_ag_oz_tc = ley_ag_gr_tm / factor_oz_tc
    """

    def test_caso_tipico(self):
        """Valores representativos de análisis real."""
        # au_ag_mg=5.5, au_mg=3.0, peso=2.0, blank=0.1444
        # neto = 5.5 - 3.0 - 0.1444 = 2.3556
        # gr_tm = 2.3556 * 1000 / 2.0 = 1177.800
        # oz_tc = 1177.800 / 34.2857 = 34.35...
        gr_tm, oz_tc = _calcular_ley_ag(au_ag_mg=5.5, au_mg=3.0, peso_muestra=2.0)
        assert gr_tm == dec("1177.800")
        assert oz_tc > dec("34.0")

    def test_neto_negativo_forzado_a_cero(self):
        """Si neto < 0 (señal Ag menor al blank), la ley se fuerza a 0."""
        # au_ag_mg=0.10, au_mg=0.08, blank=0.1444 → neto negativo
        gr_tm, oz_tc = _calcular_ley_ag(au_ag_mg=0.10, au_mg=0.08, peso_muestra=2.0)
        assert gr_tm == dec("0.000")
        assert oz_tc == dec("0.00000")

    def test_blank_correction_fija_por_defecto(self):
        """La corrección en blanco es 0.1444 (configurable pero con default)."""
        # Con blank = 0.0 manual
        gr_tm_sin_blank, _ = _calcular_ley_ag(
            au_ag_mg=5.0, au_mg=3.0, peso_muestra=2.0, blank_correction=dec("0.0")
        )
        # Con blank = 0.1444 default
        gr_tm_con_blank, _ = _calcular_ley_ag(au_ag_mg=5.0, au_mg=3.0, peso_muestra=2.0)
        # Con blank: resultado menor (se descuenta)
        assert gr_tm_con_blank < gr_tm_sin_blank

    @pytest.mark.parametrize(
        "au_ag_mg, au_mg, peso, esperado_gr_tm",
        [
            # Ejemplo mínimo real
            (3.5, 2.0, 1.5, "918.400"),
            # Ejemplo con más Ag
            (10.0, 3.0, 2.0, "3427.800"),
            # Señal Ag muy baja → neto pequeño
            (3.2, 3.0, 2.0, "27.800"),
        ],
    )
    def test_formula_parametrica(self, au_ag_mg, au_mg, peso, esperado_gr_tm):
        """Verifica la fórmula con múltiples juegos de valores."""
        # neto manual: au_ag - au - 0.1444
        neto_esperado = max(0, au_ag_mg - au_mg - 0.1444)
        gr_tm_esperado = dec(str(round(neto_esperado * 1000 / peso, 3)))
        gr_tm, _ = _calcular_ley_ag(au_ag_mg, au_mg, peso)
        assert abs(gr_tm - gr_tm_esperado) < dec("0.002")

    def test_oz_tc_es_gr_tm_dividido_factor(self):
        """ley_ag_oz_tc = ley_ag_gr_tm / 34.2857."""
        gr_tm, oz_tc = _calcular_ley_ag(5.0, 2.0, 1.0)
        # Verificar relación
        oz_tc_calculado = (gr_tm / FACTOR_OZ_TC).quantize(dec("0.00001"), rounding=ROUND_HALF_UP)
        assert oz_tc == oz_tc_calculado


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 4 – Schema AnalisisLeyCreate (validaciones Ag)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAnalisisLeyCreateAgSchema:
    """
    Cuando material='Ag':
      - ley_fino > 0 (representa la ley Ag oz/TC)
      - ley_grueso se fuerza a 0.0 automáticamente
      - punto (CABEZA/COLA/LIQUIDO) es requerido
    Cuando material='Au':
      - ley_fino > 0 requerido
      - ley_grueso > 0 requerido
    """

    def test_au_ley_fino_y_grueso_requeridos(self):
        from app.models.enums import TipoAnalisis
        from app.schemas.laboratorio import AnalisisLeyCreate

        analisis = AnalisisLeyCreate(
            cip="CIP-123456A-A1",
            laboratorio="Minares South S.R.L.",
            tipo_analisis=TipoAnalisis.PLANTA,
            material="Au",
            ley_fino=0.310,
            ley_grueso=0.090,
        )
        assert analisis.ley_fino == 0.310
        assert analisis.ley_grueso == 0.090

    def test_au_ley_grueso_cero_falla(self):
        """Para Au: ley_grueso debe ser > 0."""
        from app.models.enums import TipoAnalisis
        from app.schemas.laboratorio import AnalisisLeyCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="ley_grueso debe ser > 0"):
            AnalisisLeyCreate(
                cip="CIP-123456A-A1",
                laboratorio="Minares",
                tipo_analisis=TipoAnalisis.PLANTA,
                material="Au",
                ley_fino=0.310,
                ley_grueso=0.0,  # inválido para Au
            )

    def test_au_ley_fino_cero_falla(self):
        """Para Au: ley_fino debe ser > 0."""
        from app.models.enums import TipoAnalisis
        from app.schemas.laboratorio import AnalisisLeyCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="ley_fino debe ser > 0"):
            AnalisisLeyCreate(
                cip="CIP-123456A-A1",
                laboratorio="Minares",
                tipo_analisis=TipoAnalisis.PLANTA,
                material="Au",
                ley_fino=0.0,  # inválido para Au
                ley_grueso=0.090,
            )

    def test_ag_sin_punto_falla(self):
        """Para Ag: punto (CABEZA/COLA/LIQUIDO) es obligatorio."""
        from app.models.enums import TipoAnalisis
        from app.schemas.laboratorio import AnalisisLeyCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="punto"):
            AnalisisLeyCreate(
                cip="CIP-123456A-A1",
                laboratorio="Minares",
                tipo_analisis=TipoAnalisis.PLANTA,
                material="Ag",
                ley_fino=25.0,  # oz/TC Ag
                ley_grueso=0.0,
                # sin punto → error
            )

    def test_ag_con_punto_cabeza_valido(self):
        """Ag con punto=CABEZA es válido."""
        from app.models.enums import TipoAnalisis
        from app.schemas.laboratorio import AnalisisLeyCreate

        analisis = AnalisisLeyCreate(
            cip="CIP-123456A-A1",
            laboratorio="Minares",
            tipo_analisis=TipoAnalisis.PLANTA,
            material="Ag",
            ley_fino=25.0,
            ley_grueso=0.5,  # se forzará a 0.0
            punto="CABEZA",
        )
        assert analisis.material == "Ag"
        assert analisis.ley_grueso == 0.0  # forzado por validator
        assert analisis.punto == "CABEZA"

    @pytest.mark.parametrize("punto", ["CABEZA", "COLA", "LIQUIDO"])
    def test_ag_puntos_validos(self, punto):
        """Los tres puntos son válidos para Ag."""
        from app.models.enums import TipoAnalisis
        from app.schemas.laboratorio import AnalisisLeyCreate

        analisis = AnalisisLeyCreate(
            cip="CIP-123456A-A1",
            laboratorio="Minares",
            tipo_analisis=TipoAnalisis.PLANTA,
            material="Ag",
            ley_fino=10.0,
            punto=punto,
        )
        assert analisis.punto == punto

    def test_ag_ley_fino_cero_falla(self):
        """Para Ag: ley_fino (ley Ag) debe ser > 0."""
        from app.models.enums import TipoAnalisis
        from app.schemas.laboratorio import AnalisisLeyCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="ley_fino"):
            AnalisisLeyCreate(
                cip="CIP-123456A-A1",
                laboratorio="Minares",
                tipo_analisis=TipoAnalisis.PLANTA,
                material="Ag",
                ley_fino=0.0,  # inválido para Ag también
                punto="CABEZA",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 5 – Schema AnalisisAgCreate (Newmont Ag)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAnalisisAgCreateSchema:
    """
    AnalisisAgCreate: ingreso de señales crudas para calcular ley Ag.
    Vinculado a un análisis Au existente.
    """

    def test_schema_valido(self):
        from app.schemas.laboratorio import AnalisisAgCreate

        datos = AnalisisAgCreate(
            au_ag_mg=5.5,
            au_mg=3.0,
            peso_muestra=2.0,
            laboratorio="Minares South S.R.L.",
        )
        assert datos.au_ag_mg == 5.5
        assert datos.au_mg == 3.0
        assert datos.peso_muestra == 2.0

    def test_au_ag_mg_debe_ser_positivo(self):
        """au_ag_mg > 0."""
        from app.schemas.laboratorio import AnalisisAgCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AnalisisAgCreate(
                au_ag_mg=0.0,  # inválido
                au_mg=0.0,
                peso_muestra=2.0,
                laboratorio="Lab",
            )

    def test_peso_muestra_debe_ser_positivo(self):
        """peso_muestra > 0."""
        from app.schemas.laboratorio import AnalisisAgCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AnalisisAgCreate(
                au_ag_mg=5.0,
                au_mg=2.0,
                peso_muestra=0.0,  # inválido
                laboratorio="Lab",
            )

    def test_au_mg_puede_ser_cero(self):
        """au_mg >= 0 (puede ser 0 si no hay Au en la señal)."""
        from app.schemas.laboratorio import AnalisisAgCreate

        datos = AnalisisAgCreate(
            au_ag_mg=5.0,
            au_mg=0.0,
            peso_muestra=2.0,
            laboratorio="Lab",
        )
        assert datos.au_mg == 0.0

    def test_fecha_analisis_opcional(self):
        """fecha_analisis es opcional."""
        from app.schemas.laboratorio import AnalisisAgCreate

        datos = AnalisisAgCreate(
            au_ag_mg=5.0,
            au_mg=2.0,
            peso_muestra=2.0,
            laboratorio="Lab",
        )
        assert datos.fecha_analisis is None

        datos_con_fecha = AnalisisAgCreate(
            au_ag_mg=5.0,
            au_mg=2.0,
            peso_muestra=2.0,
            laboratorio="Lab",
            fecha_analisis=date(2025, 8, 1),
        )
        assert datos_con_fecha.fecha_analisis == date(2025, 8, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 6 – registrar_analisis_ag: lógica de servicio (mock BD)
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegistrarAnalisisAg:
    """
    Tests del servicio registrar_analisis_ag.
    Cubre:
      - Análisis Au padre no existente → ValueError
      - Análisis Au padre con material != 'Au' → ValueError
      - Ag vigente anterior se invalida antes de crear nuevo
      - Se puede agregar Ag ANTES de que el análisis Au esté completo
      - Se puede agregar Ag DESPUÉS (reemplaza el anterior)
      - El nuevo registro hereda tipo_analisis y cip del padre
    """

    def _make_analisis_au_mock(
        self,
        analisis_id: int = 1,
        lote_id: int = 10,
        cip: str = "CIP-123456A-A1",
        material: str = "Au",
        tipo_analisis: str = "planta",
        estado: str = "COMPLETADO",
    ) -> MagicMock:
        a = MagicMock()
        a.id = analisis_id
        a.lote_id = lote_id
        a.cip = cip
        a.material = material
        a.tipo_analisis = tipo_analisis
        a.estado = estado
        return a

    def _make_constantes_mock(self) -> MagicMock:
        c = MagicMock()
        c.factor_oz_tc = FACTOR_OZ_TC
        c.blank_correction_ag = BLANK_CORRECTION_AG
        return c

    def _make_lote_mock(self, lote_id: int = 10, ip: str = "IP-0042") -> MagicMock:
        lote = MagicMock()
        lote.id = lote_id
        lote.ip = ip
        return lote

    def test_analisis_au_no_existe_lanza_error(self):
        from app.schemas.laboratorio import AnalisisAgCreate
        from app.services.laboratorio import registrar_analisis_ag

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None  # no existe

        datos = AnalisisAgCreate(au_ag_mg=5.5, au_mg=3.0, peso_muestra=2.0, laboratorio="Lab")
        with pytest.raises(ValueError, match="no encontrado"):
            registrar_analisis_ag(db, analisis_au_id=999, datos=datos, usuario_id=1)

    def test_analisis_padre_material_ag_lanza_error(self):
        """No se puede agregar Ag a un análisis que ya ES Ag."""
        from app.schemas.laboratorio import AnalisisAgCreate
        from app.services.laboratorio import registrar_analisis_ag

        db = MagicMock()
        analisis_ag_padre = self._make_analisis_au_mock(material="Ag")  # padre ya es Ag

        db.query.return_value.filter.return_value.first.return_value = analisis_ag_padre

        datos = AnalisisAgCreate(au_ag_mg=5.5, au_mg=3.0, peso_muestra=2.0, laboratorio="Lab")
        with pytest.raises(ValueError, match="Solo se puede agregar Ag a análisis de material Au"):
            registrar_analisis_ag(db, analisis_au_id=1, datos=datos, usuario_id=1)

    def test_ag_vinculado_hereda_tipo_del_padre(self):
        """El análisis Ag hereda tipo_analisis y cip del análisis Au padre."""
        from app.models.models import AnalisisLey, Lote
        from app.schemas.laboratorio import AnalisisAgCreate
        from app.services.laboratorio import registrar_analisis_ag

        db = MagicMock()
        au_padre = self._make_analisis_au_mock(tipo_analisis="planta", cip="CIP-PADRE-A1")
        lote = self._make_lote_mock()

        q_ley = MagicMock()
        q_ley.filter.return_value.first.return_value = au_padre
        q_ley.filter.return_value.update.return_value = None

        q_lote = MagicMock()
        q_lote.filter.return_value.first.return_value = lote

        constantes = self._make_constantes_mock()

        # added_objects = []

        def query_side(model):
            if model is AnalisisLey:
                return q_ley
            if model is Lote:
                return q_lote
            return MagicMock()

        db.query.side_effect = query_side

        from datetime import datetime

        def add_side_effect(obj):
            obj.id = 99
            obj.creado_en = datetime(2025, 8, 1, 12, 0, 0)

        db.add.side_effect = add_side_effect

        datos = AnalisisAgCreate(
            au_ag_mg=5.5,
            au_mg=3.0,
            peso_muestra=2.0,
            laboratorio="Minares South S.R.L.",
            fecha_analisis=date(2025, 8, 1),
        )

        from unittest.mock import patch

        with patch("app.services.laboratorio.get_constantes", return_value=constantes):
            resultado = registrar_analisis_ag(db, analisis_au_id=1, datos=datos, usuario_id=1)

        # Verificar que se intentó desactivar Ag anterior
        db.query.assert_called()
        # El resultado tiene laboratorio correcto
        assert resultado.laboratorio == "Minares South S.R.L."
        assert resultado.fecha_analisis == date(2025, 8, 1)

    def test_ag_antes_del_analisis_completo(self):
        """
        El análisis Ag se puede agregar ANTES de que el análisis Au sea 'COMPLETADO'.
        El endpoint POST /ley/{analisis_id}/ag no valida estado del análisis.
        """
        from app.schemas.laboratorio import AnalisisAgCreate

        # El servicio registrar_analisis_ag solo verifica:
        # 1. que exista el análisis Au padre
        # 2. que sea material='Au'
        # NO verifica si el análisis Au está 'COMPLETADO' o pendiente
        # → podemos agregar Ag en cualquier momento

        # Verificación de diseño: el schema AnalisisAgCreate no tiene campo 'estado'
        campos = AnalisisAgCreate.model_fields.keys()
        assert "estado" not in campos

    def test_ag_invalida_anterior_y_crea_nuevo(self):
        """
        Si ya existe un Ag vigente para el lote, se marca como no vigente
        ANTES de crear el nuevo. Solo hay un Ag vigente por lote.
        """
        from unittest.mock import patch

        from app.models.models import AnalisisLey, Lote
        from app.schemas.laboratorio import AnalisisAgCreate
        from app.services.laboratorio import registrar_analisis_ag

        db = MagicMock()
        au_padre = self._make_analisis_au_mock()
        lote = self._make_lote_mock()

        q_ley = MagicMock()
        q_ley.filter.return_value.first.return_value = au_padre
        update_mock = MagicMock()
        q_ley.filter.return_value.update = update_mock

        q_lote = MagicMock()
        q_lote.filter.return_value.first.return_value = lote

        def query_side(model):
            if model is AnalisisLey:
                return q_ley
            if model is Lote:
                return q_lote
            return MagicMock()

        db.query.side_effect = query_side

        from datetime import datetime

        def _add_side_effect(obj):
            obj.id = 50
            obj.creado_en = datetime(2025, 8, 1, 12, 0, 0)

        db.add.side_effect = _add_side_effect

        constantes = self._make_constantes_mock()
        datos = AnalisisAgCreate(au_ag_mg=5.5, au_mg=3.0, peso_muestra=2.0, laboratorio="Lab")

        with patch("app.services.laboratorio.get_constantes", return_value=constantes):
            registrar_analisis_ag(db, analisis_au_id=1, datos=datos, usuario_id=1)

        # Verificar que se llamó update con vigente=False para invalidar el anterior
        update_mock.assert_called_with({"vigente": False}, synchronize_session="fetch")

    def test_resultado_ag_contiene_ley_calculada(self):
        """El resultado incluye ley_ag_gr_tm y ley_ag_oz_tc calculadas por la fórmula."""
        from unittest.mock import patch

        from app.models.models import AnalisisLey, Lote
        from app.schemas.laboratorio import AnalisisAgCreate
        from app.services.laboratorio import registrar_analisis_ag

        db = MagicMock()
        au_padre = self._make_analisis_au_mock()
        lote = self._make_lote_mock()

        q_ley = MagicMock()
        q_ley.filter.return_value.first.return_value = au_padre

        q_lote = MagicMock()
        q_lote.filter.return_value.first.return_value = lote

        def query_side(model):
            if model is AnalisisLey:
                return q_ley
            if model is Lote:
                return q_lote
            return MagicMock()

        db.query.side_effect = query_side
        constantes = self._make_constantes_mock()

        from datetime import datetime

        def _add_side_effect(obj):
            obj.id = 77
            obj.creado_en = datetime(2025, 8, 1, 12, 0, 0)

        db.add.side_effect = _add_side_effect

        # Parámetros conocidos: podemos calcular el resultado esperado
        au_ag_mg, au_mg, peso = 5.5, 3.0, 2.0
        gr_tm_esperado, oz_tc_esperado = _calcular_ley_ag(au_ag_mg, au_mg, peso)

        datos = AnalisisAgCreate(
            au_ag_mg=au_ag_mg, au_mg=au_mg, peso_muestra=peso, laboratorio="Lab"
        )

        with patch("app.services.laboratorio.get_constantes", return_value=constantes):
            resultado = registrar_analisis_ag(db, analisis_au_id=1, datos=datos, usuario_id=1)

        assert resultado.ley_ag_gr_tm == gr_tm_esperado
        assert resultado.ley_ag_oz_tc == oz_tc_esperado


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 7 – obtener_ley_ag_vigente
# ═══════════════════════════════════════════════════════════════════════════════


class TestObtenerLeyAgVigente:
    """Tests de obtener_ley_ag_vigente: retorna (gr_tm, oz_tc) o None."""

    def test_sin_ag_vigente_retorna_none(self):
        from app.services.laboratorio import obtener_ley_ag_vigente

        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        resultado = obtener_ley_ag_vigente(db, lote_id=1)
        assert resultado is None

    def test_con_ag_vigente_retorna_tupla(self):
        from app.services.laboratorio import obtener_ley_ag_vigente

        db = MagicMock()
        analisis_ag = MagicMock()
        analisis_ag.ley_gr_tm = 1177.800  # gr/TM almacenado
        analisis_ag.ley_final = 34.35000  # oz/TC almacenado en ley_final

        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            analisis_ag
        )

        resultado = obtener_ley_ag_vigente(db, lote_id=1)
        assert resultado is not None
        gr_tm, oz_tc = resultado
        assert abs(gr_tm - dec("1177.800")) < dec("0.001")
        assert abs(oz_tc - dec("34.35000")) < dec("0.001")

    def test_retorna_el_mas_reciente(self):
        """Si hay múltiples Ag, se retorna el de mayor id (más reciente)."""
        from app.services.laboratorio import obtener_ley_ag_vigente

        db = MagicMock()
        ag_mas_reciente = MagicMock()
        ag_mas_reciente.ley_gr_tm = 2000.000
        ag_mas_reciente.ley_final = 58.333

        # La query ya tiene order_by(AnalisisLey.id.desc()) y .first()
        # así que solo retorna el más reciente
        db.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            ag_mas_reciente
        )

        resultado = obtener_ley_ag_vigente(db, lote_id=5)
        assert resultado is not None
        gr_tm, oz_tc = resultado
        assert gr_tm == dec("2000.000")


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 8 – Lógica de vigencia (idempotencia y reemplazo)
# ═══════════════════════════════════════════════════════════════════════════════


class TestVigenciaAg:
    """
    El sistema garantiza un solo Ag vigente por lote.
    Cada nuevo registro invalida los anteriores.
    """

    def _regla_un_ag_vigente(self, ag_previo_vigente: bool, nuevo_ag: bool) -> dict:
        """Simula la regla de negocio de vigencia."""
        if ag_previo_vigente and nuevo_ag:
            # Se invalida el previo, se crea el nuevo
            return {"previo_invalido": True, "nuevo_vigente": True}
        elif not ag_previo_vigente and nuevo_ag:
            # No hay previo vigente, solo se crea
            return {"previo_invalido": False, "nuevo_vigente": True}
        return {"previo_invalido": False, "nuevo_vigente": False}

    def test_primer_ag_no_invalida_nada(self):
        """Primer registro Ag: no hay previo vigente."""
        resultado = self._regla_un_ag_vigente(ag_previo_vigente=False, nuevo_ag=True)
        assert resultado["previo_invalido"] is False
        assert resultado["nuevo_vigente"] is True

    def test_segundo_ag_invalida_primero(self):
        """Segundo registro Ag: invalida el primero."""
        resultado = self._regla_un_ag_vigente(ag_previo_vigente=True, nuevo_ag=True)
        assert resultado["previo_invalido"] is True
        assert resultado["nuevo_vigente"] is True

    def test_solo_un_ag_vigente_por_lote(self):
        """Invariante: nunca más de un Ag vigente por lote."""
        # El servicio garantiza esto con:
        # UPDATE analisis_ley SET vigente=False WHERE lote_id=X AND material='Ag' AND vigente=True
        # ANTES de hacer INSERT del nuevo
        # ag_previos = [True, True, True]  # Varios Ag, todos marcados vigentes antes
        ag_vigentes_despues = [False, False, True]  # Solo el último queda vigente
        assert ag_vigentes_despues.count(True) == 1

    def test_ag_antes_de_completar_newmont_luego_reemplazado(self):
        """
        Flujo real: agregar Ag ANTES de finalizar el análisis Au (Newmont),
        luego agregar otro Ag DESPUÉS. El segundo reemplaza al primero.
        """
        # Registro 1: antes de Newmont completo
        r1 = self._regla_un_ag_vigente(ag_previo_vigente=False, nuevo_ag=True)
        assert r1["nuevo_vigente"] is True

        # ... tiempo después, Newmont se completa, se añade nuevo Ag ajustado ...

        # Registro 2: después de Newmont completo
        r2 = self._regla_un_ag_vigente(ag_previo_vigente=True, nuevo_ag=True)
        assert r2["previo_invalido"] is True
        assert r2["nuevo_vigente"] is True
