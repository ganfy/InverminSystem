// ── Enums alineados con backend ───────────────────────────────────────────────
export type TipoAnalisis = 'planta' | 'externo' | 'minero' | 'dirimencia'
export type OrigenDatos = 'manual' | 'certificado'

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
    lote_ip?: string | null    // Solo visible para Comercial/Gerencia/Admin
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
    descartado_por?: number | null
    fecha_descarte?: string | null
    justificacion_descarte?: string | null
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

export interface AnalisisRecuperacionOut {
    id: number
    lote_id: number
    lote_ip?: string | null
    cip: string | null
    laboratorio: string
    ley_cabeza: number
    ley_cola: number
    ley_liquido?: number | null
    recuperacion?: number | null
    vigente: boolean
    fecha_analisis?: string | null
    certificado_url?: string | null
    descartado_por?: number | null
    fecha_descarte?: string | null
}

// ── Vista Laboratorista: por CIP ──────────────────────────────────────────────
export interface CIPAnalisisOut {
    cip: string
    lote_id: number
    lote_ip?: string | null
    fecha_envio?: string | null
    tipo_muestra?: string | null
    laboratorio_destino?: string | null
    estado_ley: 'PENDIENTE' | 'COMPLETADO'
    estado_recuperacion: 'PENDIENTE' | 'COMPLETADO'
    analisis_ley: AnalisisLeyOut[]
    analisis_recuperacion: AnalisisRecuperacionOut[]
}

// ── Vista Comercial: por Lote/IP ──────────────────────────────────────────────
export interface LoteLabOut {
    ip: string
    lote_id: number
    proveedor: string
    material?: string | null
    fecha_recepcion?: string | null
    cips: string[]
    analisis_ley: AnalisisLeyOut[]
    analisis_recuperacion: AnalisisRecuperacionOut[]
    tiene_dirimencia: boolean
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
    datos: AnalisisRecuperacionCreate
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
