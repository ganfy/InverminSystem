export type TipoAnalisis = 'planta' | 'externo' | 'minero' | 'dirimencia' | 'comercial'
export type OrigenDatos = 'manual' | 'certificado'
export type EstadoRecuperacion = 'PENDIENTE' | 'COMPLETADO' | 'CERT_COMERCIAL'
export type TipoMuestra = 'Laboratorio' | 'RecuperacionInterno' | 'RecuperacionExterno'

// ── Análisis de Ley ───────────────────────────────────────────────────────────
export interface AnalisisLeyCreate {
    cip: string
    laboratorio: string
    tipo_analisis: TipoAnalisis
    material?: string
    ley_fino: number
    ley_grueso: number
    origen_datos?: OrigenDatos
    fecha_analisis?: string
}

export interface AnalisisLeyOut {
    id: number
    lote_id: number
    lote_ip?: string | null
    cip: string | null
    laboratorio: string
    tipo_analisis: TipoAnalisis
    material: string
    ley_fino: number
    ley_grueso: number
    ley_final: number
    ley_gr_tm: number
    vigente: boolean
    fecha_analisis?: string | null
    certificado_url?: string | null
    creado_por_nombre?: string | null   // laboratorista responsable
    descartado_por?: number | null
    fecha_descarte?: string | null
    justificacion_descarte?: string | null
    eliminado: boolean
    eliminado_en?: string | null
    eliminado_por?: number | null
}

// ── Análisis de Recuperación ──────────────────────────────────────────────────
export interface AnalisisRecuperacionCreate {
    cip: string
    laboratorio: string
    ley_cabeza: number
    ley_cola: number
    ley_liquido?: number | null
    origen_datos?: OrigenDatos
    fecha_analisis?: string
}

export interface CompletarRecuperacionRequest {
    ley_cola: number
    ley_liquido?: number | null
    fecha_analisis?: string
}

export interface EnviarRecuperacionInternaRequest {
    cip?: string | null   // null → sistema elige el único RecuperacionInterno
    laboratorio?: string
    ley_cabeza?: number | null
}

export interface AnalisisRecuperacionOut {
    id: number
    lote_id: number
    lote_ip?: string | null
    cip: string | null
    laboratorio: string
    ley_cabeza: number
    ley_cola: number | null
    ley_liquido?: number | null
    solucion_ag_g_m3?: number | null
    recuperacion?: number | null
    estado: EstadoRecuperacion
    vigente: boolean
    fecha_analisis?: string | null
    certificado_url?: string | null
    creado_por_nombre?: string | null   // laboratorista responsable
    descartado_por?: number | null
    fecha_descarte?: string | null
    eliminado: boolean
    eliminado_en?: string | null
    eliminado_por?: number | null
}

// ── Vista Laboratorista: por CIP ──────────────────────────────────────────────
export interface CIPAnalisisOut {
    cip: string
    lote_id: number
    lote_ip?: string | null
    fecha_envio?: string | null
    tipo_muestra?: TipoMuestra | null
    laboratorio_destino?: string | null
    estado_ley: 'PENDIENTE' | 'COMPLETADO'
    estado_recuperacion: 'PENDIENTE' | 'COMPLETADO' | 'SIN_DATOS'
    analisis_ley: AnalisisLeyOut[]
    analisis_recuperacion: AnalisisRecuperacionOut[]
}

// ── Vista Comercial: por Lote/IP ──────────────────────────────────────────────
export interface CIPResumen {
    codigo_cip: string
    tipo_muestra?: TipoMuestra | null
    laboratorio?: string | null
}

export interface LoteLabOut {
    ip: string
    lote_id: number
    proveedor: string
    material?: string | null
    fecha_recepcion?: string | null
    cips: string[]
    cips_detalle: CIPResumen[]
    ley_planta?: number | null
    ley_minero?: number | null
    analisis_ley: AnalisisLeyOut[]
    analisis_recuperacion: AnalisisRecuperacionOut[]
    tiene_dirimencia: boolean
    tiene_prueba_pendiente: boolean
    tiene_cip_listo_sin_enviar: boolean
    cert_ley_url?: string | null
    cert_rec_url?: string | null
    cert_reconocimiento_url?: string | null
    // Plata
    ley_ag_gr_tm?: number | null
    ley_ag_oz_tc?: number | null
}

// ── Acciones ──────────────────────────────────────────────────────────────────
export interface DescartarRequest {
    justificacion: string
}

// ── Sync Offline ──────────────────────────────────────────────────────────────
export interface AnalisisLeyOfflineItem {
    offline_id: string
    datos: AnalisisLeyCreate
}

export interface AnalisisRecuperacionOfflineItem {
    offline_id: string
    analisis_id?: number | null
    datos: AnalisisRecuperacionCreate | CompletarRecuperacionRequest
}

export interface SyncLaboratorioRequest {
    analisis_ley: AnalisisLeyOfflineItem[]
    analisis_recuperacion: AnalisisRecuperacionOfflineItem[]
}

export interface SyncResultado {
    offline_id: string
    server_id: number | null
    error: string | null
}

export interface SyncLaboratorioResponse {
    resultados_ley: SyncResultado[]
    resultados_recuperacion: SyncResultado[]
}
