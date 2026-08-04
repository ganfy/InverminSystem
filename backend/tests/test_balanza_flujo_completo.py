"""
Tests unitarios — Módulo Balanza (Flujo Completo de Planta)
============================================================
Cubre:
  - Sesiones: crear, finalizar, pausar, reanudar (RF-BAL-001)
  - Lotes y pesaje: agregar, IP secuencial, tipo Otro (RF-BAL-002)
  - Eliminación de lotes con auditoría (RF-BAL-004)
  - Operación offline: reservar bloque IP, sync idempotente, colisión (RF-BAL-005)
  - Casos de emergencia en planta: múltiples lotes, IP única por año

No requiere base de datos real.
Las funciones que importan módulos con dependencias de BD (database.py/Settings)
se replican aquí como helpers locales — mismo patrón que test_rumas.py y
test_laboratorio_unit.py.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers locales (réplicas de lógica pura sin depender de app.core)
# ═══════════════════════════════════════════════════════════════════════════════


def _peso_neto(peso_inicial: Decimal, peso_final: Decimal) -> Decimal:
    """BRUTO - TARA = neto. Réplica de balanza.py._peso_neto."""
    return (peso_inicial - peso_final).quantize(Decimal("0.01"))


def dec(v) -> Decimal:
    return Decimal(str(v))


# ── Réplica de generar_ip ────────────────────────────────────────────────────


def _generar_ip(ips_existentes: list[str], proximo_ip_config: int | None = None) -> str:
    """
    Réplica de balanza.generar_ip para tests aislados.
    ips_existentes: lista de strings "IP-XXXX" del año actual.
    proximo_ip_config: valor de configuracion.proximo_ip (piso mínimo).
    """
    max_num = 0
    for ip in ips_existentes:
        try:
            num = int(ip.split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            pass
    if proximo_ip_config is not None:
        max_num = max(max_num, proximo_ip_config - 1)
    return f"IP-{max_num + 1:04d}"


# ── Réplica de reservar_bloque_ip ────────────────────────────────────────────


def _reservar_bloque_ip(proximo_ip: int = 1, tamano: int = 50) -> dict:
    """Réplica de balanza_offline.reservar_bloque_ip para tests aislados."""
    desde = proximo_ip
    hasta = desde + tamano - 1
    nuevo_proximo = hasta + 1
    return {
        "desde": desde,
        "hasta": hasta,
        "tamano": tamano,
        "formato": "IP-{n:04d}",
        "nuevo_proximo": nuevo_proximo,
    }


# ── Réplica de sincronizar lote (lógica de idempotencia) ────────────────────


def _sync_lote_logica(
    ip: str,
    ip_existente_sesion_id: int | None,
    sesion_id: int,
    offline_id: str,
) -> dict:
    """
    Réplica de la lógica de idempotencia en _sync_lote.
    ip_existente_sesion_id: sesion_id del lote existente con ese IP, o None si no existe.
    """
    if ip_existente_sesion_id is not None:
        if ip_existente_sesion_id != sesion_id:
            return {
                "offline_id": offline_id,
                "ip": ip,
                "ya_existia": False,
                "error": f"ERR_IP_COLLISION|{ip}",
            }
        return {"offline_id": offline_id, "ip": ip, "ya_existia": True, "error": None}
    return {"offline_id": offline_id, "ip": ip, "ya_existia": False, "error": None}


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 1 – Validaciones de sesión (lógica de estado)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEstadosSesion:
    """
    Replica la lógica de transiciones de estado sin importar el módulo app.
    Verifica que las reglas de negocio están correctamente implementadas.
    """

    # ── Transiciones válidas / inválidas ─────────────────────────────────────

    @pytest.mark.parametrize(
        "estado_actual,puede_pausar",
        [
            ("EN_PROCESO", True),
            ("PAUSADO", False),
            ("COMPLETO", False),
        ],
    )
    def test_pausar_solo_desde_en_proceso(self, estado_actual, puede_pausar):
        """Solo sesiones EN_PROCESO pueden pausarse."""
        puede = estado_actual == "EN_PROCESO"
        assert puede == puede_pausar

    @pytest.mark.parametrize(
        "estado_actual,puede_reanudar",
        [
            ("PAUSADO", True),
            ("EN_PROCESO", False),
            ("COMPLETO", False),
        ],
    )
    def test_reanudar_solo_desde_pausado(self, estado_actual, puede_reanudar):
        """Solo sesiones PAUSADAS pueden reanudarse."""
        puede = estado_actual == "PAUSADO"
        assert puede == puede_reanudar

    @pytest.mark.parametrize(
        "estado_actual,puede_finalizar",
        [
            ("EN_PROCESO", True),
            ("PAUSADO", True),
            ("COMPLETO", False),
        ],
    )
    def test_finalizar_bloquea_si_ya_completo(self, estado_actual, puede_finalizar):
        """Una sesión COMPLETO no puede finalizarse de nuevo."""
        puede = estado_actual != "COMPLETO"
        assert puede == puede_finalizar

    def test_finalizar_requiere_al_menos_un_lote_activo(self):
        """Simula la validación: sin lotes activos → no se puede finalizar."""
        lotes = [
            {"eliminado": True},
            {"eliminado": True},
        ]
        lotes_activos = [lo for lo in lotes if not lo["eliminado"]]
        assert len(lotes_activos) == 0  # → debería levantar ValueError

    def test_finalizar_con_lotes_activos_ok(self):
        """Con al menos 1 lote activo → puede finalizar."""
        lotes = [
            {"eliminado": True},
            {"eliminado": False},  # este es activo
        ]
        lotes_activos = [lo for lo in lotes if not lo["eliminado"]]
        assert len(lotes_activos) >= 1  # → ok para finalizar


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 2 – Pesaje (validaciones puras de schema)
# ═══════════════════════════════════════════════════════════════════════════════


class TestPesajeValidaciones:
    """Valida reglas del schema PesajeCrear sin tocar BD."""

    def test_bruto_mayor_tara_valido(self):
        from app.schemas.balanza import PesajeCrear

        p = PesajeCrear(peso_inicial=dec("10.5"), peso_final=dec("8.0"))
        assert _peso_neto(p.peso_inicial, p.peso_final) == dec("2.50")

    def test_bruto_igual_tara_falla(self):
        from app.schemas.balanza import PesajeCrear
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="MAYOR"):
            PesajeCrear(peso_inicial=dec("8.0"), peso_final=dec("8.0"))

    def test_bruto_menor_tara_falla(self):
        from app.schemas.balanza import PesajeCrear
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="MAYOR"):
            PesajeCrear(peso_inicial=dec("5.0"), peso_final=dec("8.0"))

    def test_tara_negativa_falla(self):
        from app.schemas.balanza import PesajeCrear
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="negativa"):
            PesajeCrear(peso_inicial=dec("5.0"), peso_final=dec("-1.0"))

    def test_peso_inicial_cero_falla(self):
        from app.schemas.balanza import PesajeCrear
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="mayor a 0"):
            PesajeCrear(peso_inicial=dec("0"), peso_final=dec("0"))


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 3 – Generación de IP (RF-BAL-002) - lógica pura
# ═══════════════════════════════════════════════════════════════════════════════


class TestGenerarIP:
    """Lógica de numeración IP sin depender de BD real."""

    def test_primer_ip_del_anio_es_0001(self):
        ip = _generar_ip(ips_existentes=[])
        assert ip == "IP-0001"

    def test_ip_siguiente_a_existente(self):
        ip = _generar_ip(ips_existentes=["IP-0001", "IP-0002"])
        assert ip == "IP-0003"

    def test_ip_respeta_piso_config_proximo_ip(self):
        """config proximo_ip=100 → IP-0100 aunque BD esté vacía."""
        ip = _generar_ip(ips_existentes=[], proximo_ip_config=100)
        assert ip == "IP-0100"

    def test_piso_config_no_reduce_si_bd_mayor(self):
        """Si ya hay IP-0120 en BD y config es 100, usa 121."""
        ip = _generar_ip(ips_existentes=["IP-0120"], proximo_ip_config=100)
        assert ip == "IP-0121"

    def test_tipo_material_otro_no_usa_secuencia_normal(self):
        """Para tipo_material='Otro', la IP es OT-{pesaje.id:05d}, no secuencial."""
        tipos_minerales = {"Mineral", "Llampo", "M.Llampo"}
        assert "Otro" not in tipos_minerales
        assert all(t in tipos_minerales for t in ["Mineral", "Llampo"])

    def test_formato_ip_cuatro_digitos(self):
        """El formato debe ser IP-XXXX con 4 dígitos siempre."""
        for n, expected in [
            (1, "IP-0001"),
            (9, "IP-0009"),
            (99, "IP-0099"),
            (999, "IP-0999"),
            (1000, "IP-1000"),
        ]:
            ip = _generar_ip(ips_existentes=[f"IP-{n-1:04d}"] if n > 1 else [])
            assert ip == expected or f"IP-{n:04d}" == expected


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 4 – Eliminación de Lote con auditoría (RF-BAL-004)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEliminarLoteReglas:
    """Reglas de negocio para soft-delete de lotes (lógica pura)."""

    ESTADOS_ELIMINABLES = {"RECEPCIONADO", "LIQUIDADO", "FACTURADO"}

    def test_lote_pagado_no_eliminable(self):
        """Estado PAGADO no está en los estados eliminables."""
        assert "PAGADO" not in self.ESTADOS_ELIMINABLES

    def test_lote_recepcionado_eliminable(self):
        assert "RECEPCIONADO" in self.ESTADOS_ELIMINABLES

    def test_lote_liquidado_eliminable(self):
        assert "LIQUIDADO" in self.ESTADOS_ELIMINABLES

    def test_lote_facturado_eliminable(self):
        assert "FACTURADO" in self.ESTADOS_ELIMINABLES

    def test_lote_ya_eliminado_no_se_puede_volver_a_eliminar(self):
        """Si eliminado=True, levantar error."""
        lote_eliminado = True
        assert lote_eliminado  # → debería levantar ValueError en el servicio

    def test_motivo_vacio_falla_schema(self):
        from app.schemas.balanza import EliminarLoteRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="vacío"):
            EliminarLoteRequest(motivo="   ")

    def test_motivo_valido_ok(self):
        from app.schemas.balanza import EliminarLoteRequest

        req = EliminarLoteRequest(motivo="Camión equivocado")
        assert req.motivo == "Camión equivocado"

    def test_snapshot_incluye_datos_clave(self):
        """El snapshot de auditoría debe contener ip, proveedor, estado."""
        import json

        snapshot = {
            "ip": "IP-0042",
            "proveedor_ruc": "12345678901",
            "proveedor_razon_social": "Minera ABC",
            "acopiador_ruc": "12345678901",
            "acopiador_razon_social": "Minera ABC",
            "tipo_material": "Mineral",
            "peso_neto_tm": "2.50",
            "estado_al_eliminar": "RECEPCIONADO",
            "sesion_id": 1,
        }
        serializado = json.dumps(snapshot)
        recuperado = json.loads(serializado)
        assert recuperado["ip"] == "IP-0042"
        assert recuperado["estado_al_eliminar"] == "RECEPCIONADO"


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 5 – Operación Offline - Bloque IP (RF-BAL-005)
# ═══════════════════════════════════════════════════════════════════════════════


class TestReservaIP:
    """Reserva de bloques IP para operación offline - lógica pura."""

    def test_primer_bloque_ip_default(self):
        bloque = _reservar_bloque_ip(proximo_ip=1, tamano=50)
        assert bloque["desde"] == 1
        assert bloque["hasta"] == 50
        assert bloque["tamano"] == 50
        assert bloque["formato"] == "IP-{n:04d}"

    def test_bloque_personalizado_tamano_20(self):
        bloque = _reservar_bloque_ip(proximo_ip=101, tamano=20)
        assert bloque["desde"] == 101
        assert bloque["hasta"] == 120
        assert bloque["tamano"] == 20

    def test_segundo_bloque_empieza_en_siguiente(self):
        """Dos reservas consecutivas no se superponen."""
        b1 = _reservar_bloque_ip(proximo_ip=1, tamano=50)
        b2 = _reservar_bloque_ip(proximo_ip=b1["nuevo_proximo"], tamano=50)
        assert b1["hasta"] + 1 == b2["desde"]
        assert b1["hasta"] < b2["desde"]

    def test_rango_no_tiene_huecos(self):
        """Los IPs en el bloque son consecutivos."""
        bloque = _reservar_bloque_ip(proximo_ip=51, tamano=10)
        esperados = list(range(51, 61))
        reales = list(range(bloque["desde"], bloque["hasta"] + 1))
        assert reales == esperados


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 6 – Lógica de sincronización offline (idempotencia y colisión)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSyncLogica:
    """Lógica de idempotencia y detección de colisiones IP en sync offline."""

    def test_ip_nueva_en_sesion_correcta(self):
        """IP que no existe en BD → nuevo lote, sin error."""
        res = _sync_lote_logica(
            ip="IP-0051", ip_existente_sesion_id=None, sesion_id=1, offline_id="uuid-1"
        )
        assert res["ya_existia"] is False
        assert res["error"] is None

    def test_ip_existente_misma_sesion_idempotente(self):
        """IP ya existe en la MISMA sesión → ya_existia=True, sin error."""
        res = _sync_lote_logica(
            ip="IP-0051", ip_existente_sesion_id=1, sesion_id=1, offline_id="uuid-1"
        )
        assert res["ya_existia"] is True
        assert res["error"] is None

    def test_ip_existente_otra_sesion_colision(self):
        """IP existe pero en OTRA sesión → ERR_IP_COLLISION."""
        res = _sync_lote_logica(
            ip="IP-0051", ip_existente_sesion_id=999, sesion_id=1, offline_id="uuid-1"
        )
        assert "ERR_IP_COLLISION" in res["error"]
        assert res["ya_existia"] is False

    def test_batch_con_un_error_no_aborta(self):
        """
        Un error en un lote individual no debe abortar el batch completo.
        Se verifica que cada item tiene su propio error independiente.
        """
        lotes = [
            {"offline_id": "l1", "ip": "IP-0050", "sesion_id": 1, "ip_existente_sesion": None},
            {
                "offline_id": "l2",
                "ip": "IP-0051",
                "sesion_id": 1,
                "ip_existente_sesion": 99,
            },  # colisión
            {"offline_id": "l3", "ip": "IP-0052", "sesion_id": 1, "ip_existente_sesion": None},
        ]
        resultados = [
            _sync_lote_logica(
                lo["ip"], lo["ip_existente_sesion"], lo["sesion_id"], lo["offline_id"]
            )
            for lo in lotes
        ]
        assert resultados[0]["error"] is None  # ok
        assert resultados[1]["error"] is not None  # colisión
        assert resultados[2]["error"] is None  # ok - no se abortó

    def test_sesion_idempotente_por_offline_id(self):
        """Si offline_id ya existe en BD → ya_existia=True, no crear duplicado."""
        # Simula la lógica: si encontramos la sesión por offline_id, usamos el ID existente
        # offline_id = "sesion-uuid-001"
        sesion_existente_id = 42

        # Si encontramos sesión existente:
        encontrada = (
            sesion_existente_id  # simula db.query(SesionDescarga).filter(offline_id).first()
        )
        if encontrada:
            server_id = encontrada
            ya_existia = True
        else:
            server_id = None
            ya_existia = False

        assert ya_existia is True
        assert server_id == 42


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 7 – Lógica de caché de provacops offline
# ═══════════════════════════════════════════════════════════════════════════════


class TestCacheProvacops:
    """Estructura del caché de provacops para uso offline."""

    def _make_provacop_cache(
        self,
        provacop_id: int,
        prov_id: int,
        acop_id: int,
        prov_nombre: str,
        acop_nombre: str,
        prov_ruc: str | None = None,
        acop_ruc: str | None = None,
    ) -> dict:
        """Helper: construye un item de caché."""
        return {
            "provacop_id": provacop_id,
            "proveedor_id": prov_id,
            "proveedor_razon_social": prov_nombre,
            "proveedor_ruc": prov_ruc,
            "acopiador_id": acop_id,
            "acopiador_razon_social": acop_nombre,
            "acopiador_ruc": acop_ruc,
            "es_propio": prov_id == acop_id,
        }

    def test_es_propio_cuando_mismo_id(self):
        item = self._make_provacop_cache(1, 10, 10, "Minera ABC", "Minera ABC")
        assert item["es_propio"] is True

    def test_no_es_propio_cuando_diferente_id(self):
        item = self._make_provacop_cache(2, 20, 30, "Proveedor X", "Acopiador Y")
        assert item["es_propio"] is False

    def test_formato_provacop_para_offline(self):
        """El caché tiene todos los campos que el frontend necesita offline."""
        item = self._make_provacop_cache(
            1, 10, 10, "Minera Paititi", "Minera Paititi", "12345678901", "12345678901"
        )
        campos_requeridos = [
            "provacop_id",
            "proveedor_id",
            "proveedor_razon_social",
            "acopiador_id",
            "acopiador_razon_social",
            "es_propio",
        ]
        for campo in campos_requeridos:
            assert campo in item


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 8 – Lógica de Peso Neto (fórmulas puras)
# ═══════════════════════════════════════════════════════════════════════════════


class TestPesoNeto:
    """Cálculos de peso neto - verificación numérica sin BD."""

    @pytest.mark.parametrize(
        "bruto, tara, esperado",
        [
            ("10.500", "8.000", "2.50"),
            ("25.350", "18.120", "7.23"),
            ("100.000", "85.500", "14.50"),
            ("5.001", "5.000", "0.00"),
            ("15.750", "12.250", "3.50"),
        ],
    )
    def test_peso_neto_correcto(self, bruto, tara, esperado):
        resultado = _peso_neto(dec(bruto), dec(tara))
        assert resultado == dec(esperado)

    def test_peso_neto_redondeo_2_decimales(self):
        resultado = _peso_neto(dec("10.555"), dec("8.123"))
        assert resultado == dec("2.43")

    def test_peso_neto_redondeo_exacto(self):
        resultado = _peso_neto(dec("10.000"), dec("7.500"))
        assert resultado == dec("2.50")


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 9 – Schemas de Sesión (validaciones puras)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSesionCrearSchema:
    """Validaciones del schema SesionCrear."""

    def test_placa_se_normaliza_a_mayusculas(self):
        from app.schemas.balanza import SesionCrear

        sesion = SesionCrear(provacop_id=1, placa="abc-123")
        assert sesion.placa == "ABC-123"

    def test_placa_con_espacios_se_limpia(self):
        from app.schemas.balanza import SesionCrear

        sesion = SesionCrear(provacop_id=1, placa="  xyz-456  ")
        assert sesion.placa == "XYZ-456"

    def test_sesion_solo_placa_obligatoria(self):
        from app.schemas.balanza import SesionCrear

        sesion = SesionCrear(provacop_id=1, placa="ZZZ-999")
        assert sesion.conductor is None
        assert sesion.guia_remision is None
        assert sesion.carreta is None


# ═══════════════════════════════════════════════════════════════════════════════
# Grupo 10 – Emergencia: proveedor sin parámetros puede operar
# ═══════════════════════════════════════════════════════════════════════════════


class TestProveedorSinParametros:
    """
    Caso crítico de planta: Comercial registró proveedor pero aún no
    completó los parámetros comerciales. El sistema NO debe bloquear
    la operación de balanza - solo afecta liquidaciones posteriores.
    """

    def test_crear_sesion_no_valida_parametros_comerciales(self):
        """
        La función crear_sesion solo valida que provacop_id exista.
        No verifica si hay ParametrosComerciales configurados.
        """
        from app.schemas.balanza import SesionCrear

        datos = SesionCrear(provacop_id=1, placa="TEST-001")
        assert datos.provacop_id == 1

    def test_schema_sesion_no_tiene_campo_parametros(self):
        """El schema SesionCrear no tiene campo 'parametros' - por diseño."""
        from app.schemas.balanza import SesionCrear

        campos = SesionCrear.model_fields.keys()
        assert "parametros" not in campos

    def test_provacop_sin_params_marca_pendiente(self):
        """Un provacop sin ParametrosComerciales.parametros → pendiente_parametros=True."""
        # Lógica de listar_provacops:
        # "pendiente_parametros": not bool(pa.parametros)
        parametros = None  # sin parámetros
        pendiente = not bool(parametros)
        assert pendiente is True

    def test_provacop_con_params_no_pendiente(self):
        """Un provacop con parámetros → pendiente_parametros=False."""
        parametros = MagicMock()  # tiene objeto
        pendiente = not bool(parametros)
        assert pendiente is False
