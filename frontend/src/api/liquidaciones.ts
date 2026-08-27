import type { ScriptElementKindModifier } from 'typescript'
import api from './axios'

// ── Requests ──────────────────────────────────────────────────────────────────

export interface LotePreviewInput {
    ip: string
    bono?: number | null
    rec_liq_override?: number | null
    gasto_acopio_override?: number | null
    gasto_consumo_override?: number | null
    spot_usd_override?: number | null
    spot_ag_usd_override?: number | null
}

export interface LiquidacionPreviewRequest {
    provacop_id: number
    lotes: LotePreviewInput[]
    spot_usd?: number | null
    spot_ag_usd?: number | null
    fecha_liquidacion?: string | null
}

export interface LiquidacionCreate {
    provacop_id: number
    lotes: LotePreviewInput[]
    spot_usd?: number | null
    spot_ag_usd?: number | null
    fecha_liquidacion?: string | null
    numero_liquidacion?: string | null
    como_borrador?: boolean
}

export interface LiquidacionEstadoUpdate {
    estado: string
}

// ── Responses ─────────────────────────────────────────────────────────────────

export interface AlertaLote {
    tipo: string
    mensaje: string
    critico: boolean
}

export interface LoteFinancieroOut {
    ip: string
    proveedor?: string | null
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
    // Plata (Ag) — opcionales
    ley_ag_gr_tm?: number | null
    ley_ag_oz_tc?: number | null
    spot_ag_usd?: number | null
    valor_ag_usd?: number | null
    aplica_ag?: boolean
    // Spot histórico por IP
    fecha_spot_efectiva?: string | null     // fecha LBMA Fix usada
    spot_desde_historico?: boolean          // true = histórico, false = fallback manual
}

export interface LiquidacionPreviewOut {
    provacop_id: number
    proveedor_razon_social: string
    proveedor_ruc: string | null
    acopiador_nombre: string
    spot_usd?: number | null
    lotes: LoteFinancieroOut[]
    total_usd: number
    total_tms: number
    total_tmh: number
    total_oz_compradas: number
    count_lotes: number
    alertas_globales: AlertaLote[]
    puede_generar: boolean
    total_ag_usd: number
    hay_ag: boolean
}

export interface LoteDisponible {
    ip: string
    tipo_material: string | null
    fecha_recepcion: string | null
    dias_almacen: number
    tms: number | null
    tmh: number | null
    sacos: number | null
    volado: boolean
    alerta_vencimiento: boolean
    ley_comercial: number | null
    oz_tc_planta: number | null
    oz_tc_minero: number | null
    porcentaje_rec: number | null
    usa_dirimencia: boolean
    listo_para_liquidar: boolean
    liquidacion_id?: number | null
    numero_liquidacion?: string | null
    // identificación de acopiador y proveedor para agrupar
    provacop_id: number
    proveedor: string
    acopiador: string
}

export interface LiquidacionesKPI {
    borradores: number
    generadas: number
    lotes_liquidables: number
    valor_pendiente_usd: number
}

export interface LiquidacionLoteOut extends LoteFinancieroOut {
    liquidacion_id: number
    fecha_emision: string | null
}

export interface LiquidacionResumenOut {
    id: number
    numero_liquidacion: string
    estado: string
    provacop_id: number
    proveedor_razon_social: string
    proveedor_ruc: string | null
    acopiador_nombre: string
    spot_usd?: number | null
    total_usd: number
    count_lotes: number
    fecha_creacion: string
}

export interface LiquidacionDetalleOut extends LiquidacionResumenOut {
    lotes: LiquidacionLoteOut[]
    pdf_url: string | null
    fecha_cierre: string | null
    hay_ag?: boolean
    total_ag_usd?: number | null
}

export interface LiquidacionLoteParamsUpdate {
    bono?: number | null
    rec_liq_override?: number | null
    riesgo_override?: number | null
    maquila_override?: number | null
    gasto_acopio_override?: number | null
    gasto_consumo_override?: number | null
    spot_usd_override?: number | null
    spot_ag_usd_override?: number | null
}

// ── Edición de Parámetros de Lote ──────────────────────────────────────────────
/** Todos los overrides son por IP para permitir configuración independiente por lote */
export interface EditOverrides {
    gasto_acopio: Record<string, number | null>
    gasto_consumo: Record<string, number | null>
    bono: Record<string, number | null>
    rec_liq: Record<string, number | null>
    spot_usd: Record<string, number | null>
    spot_ag_usd: Record<string, number | null>
}

// ── Spot Histórico ─────────────────────────────────────────────────────────────

export interface SpotHistoricoOut {
    id: number
    fecha: string
    precio_au_usd: number
    precio_ag_usd: number | null
    fuente: string
}

export interface SpotHistoricoIn {
    fecha: string
    precio_au_usd: number
    precio_ag_usd?: number | null
    fuente?: string
}

// ── API calls ──────────────────────────────────────────────────────────────────
/**
 * Obtiene el precio diario del oro (London Fix PM).
 * Si guardar=true, también lo guarda en el histórico para hoy.
 * Retorna un number o null si no se pudo obtener.
 */
export const obtenerPrecioOro = async (guardar = false): Promise<number | null> => {
    const response = await api.get('/liquidaciones/precio-oro', { params: { guardar } });
    return response.data;
};

/**
 * Obtiene el precio diario de la plata (London Fix Noon)
 * Retorna un number o null si no se pudo obtener.
 */
export const obtenerPrecioPlata = async (): Promise<number | null> => {
    const response = await api.get('/liquidaciones/precio-plata');
    return response.data;
};

// Spot histórico CRUD
export function getSpotHistorico(params?: { desde?: string; hasta?: string; limit?: number }) {
    return api.get<SpotHistoricoOut[]>('/liquidaciones/spot-historico', { params })
}

export function crearSpotHistorico(data: SpotHistoricoIn) {
    return api.post<SpotHistoricoOut>('/liquidaciones/spot-historico', data)
}

export function eliminarSpotHistorico(id: number) {
    return api.delete(`/liquidaciones/spot-historico/${id}`)
}

export function getSpotPorFecha(fecha: string) {
    return api.get<SpotHistoricoOut | null>(`/liquidaciones/spot-historico/fecha/${fecha}`)
}


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

export function getLiquidacionesKPIs() {
    return api.get<LiquidacionesKPI>('/liquidaciones/kpis')
}

export async function descargarPDF(id: string) : Promise<void> {
    const response = await api.get(`/liquidaciones/${id}/pdf`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.download = `Liquidacion_${id}.pdf`;
    link.click();
    URL.revokeObjectURL(url);
}

export function editarParamsLote(liquidacionId: number, ip: string, body: LiquidacionLoteParamsUpdate) {
    return api.patch<LiquidacionDetalleOut>(`/liquidaciones/${liquidacionId}/lotes/${ip}/parametros`, body)
}

export function emitirLiquidacion(id: number) {
    return api.post<LiquidacionDetalleOut>(`/liquidaciones/${id}/emitir`)
}

export async function exportarPL(clave: string) : Promise<void> {
    const response = await api.post('/liquidaciones/exportar-pl', { clave }, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.download = `Liquidaciones_PL.xlsx`;
    link.click();
    URL.revokeObjectURL(url);
}
