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

// ── Provacop selector (wizard paso 1) ────────────────────────────────────────

export interface ProvacoPSelector {
    id: number
    proveedor: string
    proveedor_ruc: string | null
    acopiador: string
    tiene_parametros: boolean
    maquila: number | null
    comision: number | null
    gasto_acopio: number | null
    gasto_consumo: number | null
    riesgo_comercial: number | null
}

// ── Lote liquidable ───────────────────────────────────────────────────────────

export interface LoteLiquidable {
    lote_id: number
    ip: string
    provacop_id: number
    proveedor: string
    acopiador: string
    ruc_proveedor: string | null
    material: string | null
    estado: string
    fecha_recepcion: string | null
    tms: number | null
    ley_comercial: number | null
    ley_gr_tm: number | null
    usa_dirimencia: boolean
    oz_tc_planta: number | null
    oz_tc_minero: number | null
    porcentaje_rec: number | null
}

// ── Crear liquidación ─────────────────────────────────────────────────────────

export interface LiquidacionCreate {
    provacop_id: number
    precio_oro_usd: number
    lote_ids: number[]
}

// ── Liquidación completa ──────────────────────────────────────────────────────

export interface LiquidacionOut {
    id: number
    numero_liquidacion: string | null
    provacop_id: number
    proveedor: string
    acopiador: string
    ruc_proveedor: string | null
    precio_oro_usd: number | null
    valor_total_usd: number | null
    estado: EstadoLiquidacion
    pdf_url: string | null
    creado_en: string | null
    lotes: LiquidacionLoteOut[]
}

// ── Item de lista (tabla dashboard) ──────────────────────────────────────────

export interface LiquidacionListItem {
    id: number
    numero_liquidacion: string | null
    provacop_id: number
    proveedor: string
    acopiador: string
    num_lotes: number
    tms_total: number | null
    precio_oro_usd: number | null
    valor_total_usd: number | null
    estado: EstadoLiquidacion
    pdf_url: string | null
    creado_en: string | null
}

// ── KPIs ──────────────────────────────────────────────────────────────────────

export interface LiquidacionesKPI {
    borradores: number
    generadas: number
    lotes_liquidables: number
    valor_pendiente_usd: number
}

// ── Estado ────────────────────────────────────────────────────────────────────

export type EstadoLiquidacion = 'BORRADOR' | 'GENERADA' | 'FACTURADA' | 'PAGADA'

export const ESTADO_LABELS: Record<EstadoLiquidacion, string> = {
    BORRADOR: 'Borrador',
    GENERADA: 'Generada',
    FACTURADA: 'Facturada',
    PAGADA: 'Pagada',
}

// ── Cálculo preview wizard paso 3 ────────────────────────────────────────────

export interface LoteCalculo {
    lote_id: number
    ip: string
    tms: number
    ley_comercial: number   // oz/tc
    ley_gr_tm: number
    usa_dirimencia: boolean
    porcentaje_rec: number
    fino_recuperable: number  // oz
    valor_bruto: number       // USD
}

export interface ResumenCalculos {
    lotes: LoteCalculo[]
    total_fino_oz: number
    total_valor_bruto: number
    gasto_acopio_total: number
    gasto_consumo_total: number
    maquila_usd: number
    comision_usd: number
    total_deducciones: number
    valor_neto: number
}

// // ── Lote dentro de liquidación ────────────────────────────────────────────────

// export interface LiquidacionLoteOut {
//     lote_id: number
//     ip: string
//     material: string | null
//     tms: number | null
//     ley_comercial: number | null
//     usa_dirimencia: boolean
//     oz_tc_planta: number | null
//     oz_tc_comercial: number | null
//     oz_tc_minero: number | null
//     oz_tc_promedio: number | null
//     porcentaje_rec_liquido: number | null
//     porcentaje_rec_planta: number | null
//     fino_recuperable: number | null
//     gasto_acopio_liquidacion: number | null
//     bono: number | null
//     insumos_liquidacion: number | null
//}

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
