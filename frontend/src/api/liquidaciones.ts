import api from './axios'

export interface LotePreviewInput {
    ip: string
    bono?: number
    rec_liq_override?: number | null
}

export interface LiquidacionPreviewRequest {
    provacop_id: number
    lotes: LotePreviewInput[]
    spot_usd: number
    fecha_liquidacion?: string | null
}

export interface AlertaLote {
    tipo: string
    mensaje: string
    critico: boolean
}

export interface LoteFinancieroOut {
    ip: string
    fecha_recepcion: string | null
    tmh: number
    pct_humedad: number
    tms: number
    sacos: number | null
    oz_tc_planta: number
    oz_tc_comercial: number
    oz_tc_minero: number
    oz_tc_promedio: number
    pct_rec_liq: number
    pct_rec_planta: number | null
    maquila: number
    riesgo: number
    spot_usd: number
    insumos_acopio: number
    insumos_consumo: number
    insumos_total: number
    bono: number
    factor: number
    precio_x_tms: number
    total_usd: number
    fino_recuperable: number
    usa_dirimencia: boolean
    alertas: AlertaLote[]
}

export interface LiquidacionPreviewOut {
    provacop_id: number
    proveedor_razon_social: string
    proveedor_ruc: string | null
    acopiador_nombre: string
    spot_usd: number
    lotes: LoteFinancieroOut[]
    total_usd: number
    total_tms: number
    total_tmh: number
    total_oz_compradas: number
    count_lotes: number
    alertas_globales: AlertaLote[]
    puede_generar: boolean
}

export interface LiquidacionCreate {
    provacop_id: number
    lotes: LotePreviewInput[]
    spot_usd: number
    fecha_liquidacion?: string | null
    numero_liquidacion?: string | null
}

export interface LiquidacionResumenOut {
    id: number
    numero_liquidacion: string
    estado: string
    provacop_id: number
    proveedor_razon_social: string
    proveedor_ruc: string | null
    acopiador_nombre: string
    spot_usd: number
    total_usd: number
    count_lotes: number
    fecha_creacion: string
}

export interface LoteDisponible {
    ip: string
    tipo_material: string
    fecha_recepcion: string | null
    dias_almacen: number
    tms: number | null
    tmh: number | null
    sacos: number | null
    volado: boolean
    alerta_vencimiento: boolean
}

export interface LiquidacionLoteOut extends LoteFinancieroOut {
    liquidacion_id: number
    fecha_emision: string | null
}

export interface LiquidacionDetalleOut extends LiquidacionResumenOut {
    lotes: LiquidacionLoteOut[]
    pdf_url: string | null
    fecha_cierre: string | null
}

// ── API calls ──────────────────────────────────────────────────────────────────

export function getLotesDisponibles(provacop_id: number) {
    return api.get<LoteDisponible[]>('/liquidaciones/lotes-disponibles', {
        params: { provacop_id },
    })
}

export function previewLiquidacion(req: LiquidacionPreviewRequest) {
    return api.post<LiquidacionPreviewOut>('/liquidaciones/preview', req)
}

export function getLiquidaciones(params?: { provacop_id?: number; estado?: string }) {
    return api.get<LiquidacionResumenOut[]>('/liquidaciones/', { params })
}

export function getLiquidacion(id: number) {
    return api.get<LiquidacionDetalleOut>(`/liquidaciones/${id}`)
}

export function crearLiquidacion(req: LiquidacionCreate) {
    return api.post<LiquidacionDetalleOut>('/liquidaciones/', req)
}

export function cambiarEstadoLiquidacion(id: number, estado: string) {
    return api.patch<LiquidacionDetalleOut>(`/liquidaciones/${id}/estado`, { estado })
}

export function getPdfLiquidacion(id: number): string {
    const base = api.defaults.baseURL ?? ''
    return `${base}/liquidaciones/${id}/pdf`
}
