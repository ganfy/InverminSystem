"""
app/schemas/balanza_offline.py
================================
Schemas para la operación offline del módulo Balanza (RF-BAL-005).
"""

from datetime import datetime

from pydantic import BaseModel

# ── Bloque de IPs ──────────────────────────────────────────


class BloqueIPRespuesta(BaseModel):
    desde: int  # primer número disponible
    hasta: int  # último número del bloque
    tamano: int  # cantidad de IPs reservados
    formato: str  # "IP-{n:04d}" — el frontend aplica este patrón
    anio: int  # año calendario en curso


# ── Caché provacops ────────────────────────────────────────


class ProvAcopCache(BaseModel):
    provacop_id: int
    proveedor_id: int
    proveedor_razon_social: str
    proveedor_ruc: str
    acopiador_id: int
    acopiador_razon_social: str
    acopiador_ruc: str
    es_propio: bool

    model_config = {"from_attributes": True}


class CacheProvacopsRespuesta(BaseModel):
    total: int
    items: list[ProvAcopCache]
    ts_servidor: str  # ISO timestamp para saber cuándo cachear


# ── Sync batch — request ───────────────────────────────────


class PesajeOffline(BaseModel):
    peso_inicial: float
    peso_final: float
    sacos: int | None = None
    granel: bool = False
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None


class LoteOffline(BaseModel):
    offline_id: str  # UUID generado en frontend, ej: "lote-uuid-xxx"
    ip: str  # IP del bloque reservado, ej: "IP-0051"
    numero_lote: int
    tipo_material: str
    pesaje: PesajeOffline
    creado_en: datetime | None = None
    numero_ticket: str | None = None


class SesionOffline(BaseModel):
    offline_id: str  # UUID generado en frontend, ej: "sesion-uuid-xxx"
    provacop_id: int
    placa: str
    carreta: str | None = None
    conductor: str | None = None
    transportista: str | None = None
    razon_social: str | None = None
    guia_remision: str | None = None
    guia_transporte: str | None = None
    estado: str = "COMPLETO"
    creado_en: datetime | None = None
    lotes: list[LoteOffline] = []


class SyncBatchRequest(BaseModel):
    sesiones: list[SesionOffline]


# ── Sync batch — response ──────────────────────────────────


class SyncItemResultado(BaseModel):
    offline_id: str
    server_id: int | None  # None si hubo error
    ya_existia: bool
    error: str | None
    lotes: list[dict]  # {offline_id, ip, ya_existia, error}


class SyncBatchRespuesta(BaseModel):
    procesados: int
    resultados: list[SyncItemResultado]
    ts_servidor: str


class BloqueTKRespuesta(BaseModel):
    desde: int
    hasta: int
    tamano: int
