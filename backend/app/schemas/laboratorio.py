from datetime import date, datetime
from decimal import Decimal

from app.models.enums import OrigenDatos, TipoAnalisis
from pydantic import BaseModel, Field, model_validator

# ── Análisis de Ley (Fire Assay triple sampling) ──────────────────────────────

model_config = {"from_attributes": True, "json_encoders": {Decimal: float}}


class NewmontMuestraIn(BaseModel):
    """
    Datos crudos de una muestra del triple sampling Newmont.
    Campo opcional en AnalisisLeyCreate para poblar analisis_detalle.
    """

    peso_g: Decimal = Field(..., gt=0)
    au_mg: Decimal = Field(..., ge=0)
    ley_oz_tc: Decimal = Field(..., ge=0, description="Ley calculada en frontend (Oz/TC)")


class AnalisisDetalleOut(BaseModel):
    id: int
    origen: str  # FINO1 | FINO2 | GRUESO | AU1 | AU2 | AU_AG
    peso: Decimal | None
    mineral_mg: Decimal | None
    ley: Decimal | None
    numero_ensayo: int

    model_config = {"from_attributes": True}


class AnalisisLeyCreate(BaseModel):
    cip: str = Field(
        ..., description="Código de la muestra (CIP de lote o código libre de Proceso)"
    )
    laboratorio: str = Field(..., description="Nombre del laboratorio")
    tipo_analisis: TipoAnalisis = Field(..., description="planta | externo | minero | dirimencia")
    material: str = Field("Au", description="Au | Ag")
    ley_fino: float = Field(..., ge=0, description="Oz/TC fracción -140 (Au) o ley Ag")
    ley_grueso: float = Field(0.0, ge=0, description="Oz/TC fracción +140 (Au). 0 para Ag")
    punto: str | None = Field(None, description="Ag: CABEZA | COLA | LIQUIDO")
    origen_datos: str = OrigenDatos.MANUAL
    muestras_detalle: list[NewmontMuestraIn] | None = None
    fecha_analisis: date | None = None
    descripcion_pdf: str | None = Field(
        None,
        description="Descripción para el campo 'Descripción' del certificado PDF. "
        "Valores sugeridos: PROCESO, LAB. METAL\u00daRGICO, RECONOCIMIENTO, LOTE. "
        "Si no se envía, se usa el default del template.",
    )
    es_edicion: bool = Field(
        False, description="Indica si es una edición/corrección. Invalida registros anteriores."
    )

    @model_validator(mode="after")
    def validar_segun_material(self) -> "AnalisisLeyCreate":
        if self.material == "Au":
            if self.ley_fino <= 0:
                raise ValueError("ley_fino debe ser > 0 para Au")
            if self.ley_grueso <= 0:
                raise ValueError("ley_grueso debe ser > 0 para Au")
        elif self.material == "Ag":
            if self.ley_fino <= 0:
                raise ValueError("ley_fino (ley Ag oz/TC) debe ser > 0")
            self.ley_grueso = 0.0  # garantizar
            if not self.punto:
                raise ValueError("punto (CABEZA/COLA/LIQUIDO) es requerido para Ag")
        return self


class AnalisisLeyPorIPCreate(BaseModel):
    tipo_analisis: TipoAnalisis = Field(..., description="minero | dirimencia")
    laboratorio: str = Field(..., description="Nombre del laboratorio o minero")
    ley_fino: float = Field(..., ge=0, description="Oz/TC malla fina (Au) o ley Ag")
    ley_grueso: float = Field(0.0, ge=0, description="Oz/TC malla gruesa. 0 para Ag")
    material: str = Field("Au", description="Au | Ag")
    punto: str | None = Field(None, description="Ag: CABEZA | COLA | LIQUIDO")
    origen_datos: str = OrigenDatos.MANUAL
    fecha_analisis: date | None = None

    @model_validator(mode="after")
    def validar_segun_material(self) -> "AnalisisLeyPorIPCreate":
        if self.material == "Ag":
            self.ley_grueso = 0.0
            if not self.punto:
                raise ValueError("punto es requerido para Ag")
        return self


class AnalisisLeyOut(BaseModel):
    id: int
    lote_id: int | None = None  # None para análisis de Proceso (sin lote)
    lote_ip: str | None = None
    cip: str | None
    laboratorio: str
    tipo_analisis: str
    material: str
    ley_fino: Decimal
    ley_grueso: Decimal
    ley_final: Decimal
    ley_gr_tm: Decimal
    vigente: bool
    fecha_analisis: date | None
    certificado_url: str | None
    creado_por_nombre: str | None = None  # nombre del laboratorista que registró
    descartado_por: int | None = None
    fecha_descarte: datetime | None = None
    justificacion_descarte: str | None = None
    eliminado: bool = False
    eliminado_en: datetime | None = None
    eliminado_por: int | None = None
    detalles: list[AnalisisDetalleOut] = []

    model_config = {"from_attributes": True}


# ── Análisis de Plata (Ag) ────────────────────────────────────────────────────


class AnalisisAgCreate(BaseModel):
    """
    Ingreso de señal combinada Au+Ag para calcular ley de plata.
    Blank correction fija: 0.1444 (no editable por usuario).
    ley_ag_gr_tm = ((au_ag_mg - au_mg - 0.1444) * 1000) / peso_muestra
    ley_ag_oz_tc = ley_ag_gr_tm / 34.2857
    """

    au_ag_mg: float = Field(..., gt=0, description="Señal combinada Au+Ag (mg)")
    au_mg: float = Field(..., ge=0, description="Señal Au pura (mg)")
    peso_muestra: float = Field(..., gt=0, description="Peso de la muestra (g)")
    laboratorio: str = Field(..., description="Nombre del laboratorio")
    fecha_analisis: date | None = None


class AnalisisAgOut(BaseModel):
    id: int
    lote_id: int | None = None  # None para Proceso
    lote_ip: str | None = None
    laboratorio: str
    ley_ag_gr_tm: Decimal
    ley_ag_oz_tc: Decimal
    fecha_analisis: date | None
    vigente: bool
    creado_por: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# ── Análisis de Recuperación ──────────────────────────────────────────────────


class AnalisisRecuperacionCreate(BaseModel):
    """Para registro manual directo (laboratorio externo via certificado, o lab propio sin pending)."""

    cip: str
    laboratorio: str
    ley_cabeza: Decimal | None = Field(None, ge=0)
    ley_cola: Decimal | None = None
    ley_liquido: Decimal | None = None
    origen_datos: str = OrigenDatos.MANUAL
    fecha_analisis: date | None = None
    descripcion_pdf: str | None = Field(
        None,
        description="Descripción para el PDF. Sugeridos: PROCESO, LAB. METAL\u00daRGICO, RECONOCIMIENTO, LOTE.",
    )
    sub_tipo: str | None = Field(None, description="SOLIDOS | SOLUCION | None")
    ley_cola_ag: Decimal | None = Field(
        None, description="Ley Ag g/TM (opcional, para crear el registro de plata automáticamente)"
    )
    muestras: list["MuestraReconocimientoIn"] | None = Field(
        default=None, description="Muestras de reconocimiento opcionales para creación directa."
    )
    es_edicion: bool = Field(
        False, description="Indica si es una edición/corrección. Invalida registros anteriores."
    )


class EnviarRecuperacionInternaRequest(BaseModel):
    """
    Comercial crea un registro pendiente de recuperación para el laboratorio interno.
    El CIP debe ser de tipo RecuperacionInterno.
    Si el lote tiene solo 1 CIP interno, se puede omitir (se usa automáticamente).
    sub_tipos: lista de sub-tipos a crear ('SOLIDOS', 'SOLUCION' o ambos). Default: ambos.
    """

    cip: str | None = None  # None → sistema elige el único RecuperacionInterno del lote
    laboratorio: str | None = None
    ley_cabeza: Decimal | None = None
    sub_tipos: list[str] = Field(
        default=["SOLIDOS", "SOLUCION"], description="Sub-tipos de análisis a crear"
    )


class AnalisisRecuperacionOut(BaseModel):
    id: int
    lote_id: int | None = None  # None para análisis de Proceso (sin lote)
    lote_ip: str | None = None
    cip: str | None
    laboratorio: str
    ley_cabeza: Decimal | None = None
    ley_cola: Decimal | None = None
    ley_liquido: Decimal | None = None  # solución Au
    recuperacion: Decimal | None = None
    solucion_ag_g_m3: Decimal | None = None  # Ag en solución (g/m³)
    # ── Detalles por muestra (solo se incluyen cuando se piden explícitamente) ─
    detalles: list[AnalisisDetalleOut] = []
    # ── Sub-tipo Reconocimiento ────────────────────────────────────────
    sub_tipo: str | None = None  # 'SOLIDOS' | 'SOLUCION' | null
    # ── Estado y trazabilidad ──────────────────────────────────────
    estado: str
    vigente: bool
    fecha_analisis: date | None
    certificado_url: str | None
    creado_por_nombre: str | None = None
    descartado_por: int | None = None
    fecha_descarte: datetime | None = None
    eliminado: bool = False
    eliminado_en: datetime | None = None
    eliminado_por: int | None = None

    model_config = {"from_attributes": True}


class MuestraReconocimientoIn(BaseModel):
    """
    Una muestra física del reconocimiento de pulpa (sala de metalurgia).
    Cada lote produce 3 filas en analisis_detalle:
      - origen AU1  : peso + mineral_mg=Au1_mg → ley Au1 (Gr/TM)
      - origen AU2  : peso + mineral_mg=Au2_mg → ley Au2 (Gr/TM)
      - origen AU_AG: peso + mineral_mg=AuAg_mg → ley Ag (Gr/TM)
    La ley Au final de esta muestra = avg(ley_au1, ley_au2).
    numero_ensayo: 1 normal, 2 = remuestreo.
    """

    peso_g: Decimal = Field(..., gt=0, description="Peso de muestra sólida (g)")
    au1_mg: Decimal = Field(..., ge=0, description="Señal Au primera lectura (mg)")
    au2_mg: Decimal = Field(..., ge=0, description="Señal Au segunda lectura (mg)")
    au_ag_mg: Decimal = Field(..., ge=0, description="Señal Au+Ag combinada (mg)")
    numero_ensayo: int = Field(default=1, ge=1, le=10)


class CompletarRecuperacionRequest(BaseModel):
    """
    Para que laboratorista complete un PENDIENTE.

    Flujo A (reconocimiento de planta): proveer muestras[].
    El service calcula ley_cola y ley_cola_ag automáticamente.
    Flujo B (fallback / certificado externo): proveer ley_cola directo.
    """

    # Flujo A — muestras crudas
    muestras: list[MuestraReconocimientoIn] | None = Field(
        default=None,
        description="Muestras de reconocimiento. Si se proveen, ley_cola se calcula automáticamente.",
    )
    # Flujo B — fallback
    ley_cola: Decimal | None = Field(
        default=None, description="Ley cola directa (Oz/TC). Solo si no hay muestras."
    )
    # Solución (líquido)
    ley_liquido: Decimal | None = Field(default=None, description="Ley líquido Au (Oz/TC).")
    solucion_ag_g_m3: Decimal | None = Field(
        default=None, description="Concentración Ag en solución (g/m³)."
    )
    fecha_analisis: date | None = None


# ── Acciones de Comercial ─────────────────────────────────────────────────────


class DescartarRequest(BaseModel):
    justificacion: str


# ── Vista Laboratorista: por CIP ──────────────────────────────────────────────


class CIPAnalisisOut(BaseModel):
    cip: str
    lote_id: int | None = None  # None para CIPs de Proceso (sin lote)
    lote_ip: str | None = None  # None para Laboratorista, IP real para Comercial
    fecha_envio: date | None
    tipo_muestra: str | None
    laboratorio_destino: str | None
    estado_ley: str  # PENDIENTE | COMPLETADO (para CIPs tipo Laboratorio)
    estado_recuperacion: str  # PENDIENTE | COMPLETADO (para CIPs tipo Recuperacion*)
    analisis_ley: list[AnalisisLeyOut] = []
    analisis_recuperacion: list[AnalisisRecuperacionOut] = []


# ── Vista Comercial: por Lote/IP ──────────────────────────────────────────────


class CIPResumen(BaseModel):
    """Resumen de un CIP con su tipo para la vista de Comercial."""

    codigo_cip: str
    tipo_muestra: str | None
    laboratorio: str | None


class LoteLabOut(BaseModel):
    ip: str
    lote_id: int
    proveedor: str
    material: str | None
    fecha_recepcion: datetime | None
    cips: list[str]  # todos los CIPs del lote (compatibilidad)
    cips_detalle: list[CIPResumen] = []  # CIPs con tipo para UI
    ley_planta: float | None = None  # calculada on-the-fly
    ley_minero: float | None = None  # del análisis tipo minero vigente
    analisis_ley: list[AnalisisLeyOut]
    analisis_recuperacion: list[AnalisisRecuperacionOut]
    tiene_dirimencia: bool
    tiene_prueba_pendiente: bool = False
    cert_ley_url: str | None = None
    cert_rec_url: str | None = None
    cert_reconocimiento_url: str | None = None
    ley_ag_gr_tm: float | None = None  # ley de plata vigente (g/TM), None si no hay
    ley_ag_oz_tc: float | None = None
    # Alerta: diferencia entre análisis de lab > umbral → recomendar enviar otra muestra
    alerta_diferencia_analisis: float | None = None  # valor de la diferencia; None = sin alerta
    alerta_diferencia_ree: float | None = None  # valor de la diferencia para el umbral REE


# ── Sync Offline ──────────────────────────────────────────────────────────────


class AnalisisLeyOfflineItem(BaseModel):
    offline_id: str
    datos: AnalisisLeyCreate


class AnalisisRecuperacionOfflineItem(BaseModel):
    offline_id: str
    datos: AnalisisRecuperacionCreate


class SyncLaboratorioRequest(BaseModel):
    analisis_ley: list[AnalisisLeyOfflineItem] = []
    analisis_recuperacion: list[AnalisisRecuperacionOfflineItem] = []


class SyncResultado(BaseModel):
    offline_id: str
    server_id: int | None
    error: str | None


class SyncLaboratorioResponse(BaseModel):
    resultados_ley: list[SyncResultado] = []
    resultados_recuperacion: list[SyncResultado] = []
