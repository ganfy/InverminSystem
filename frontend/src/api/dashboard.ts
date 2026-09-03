import api from './axios'
import type { LiquidacionResumenOut } from './liquidaciones'

export interface DashboardKPIs {
    au_real_100: number
    au_real_rec: number
    tmh_stock: number
    tms_stock: number
    oz_stock: number
    oz_habilitados: number
    valor_compra_total: number
    valor_compra_promedio: number
    rec_liq_promedio: number
    rec_planta_promedio: number
    inter_usd_promedio: number
    au_comprado: number
}

interface AcopiadorTMH {
    acopiador: string;
    enero: number;
    febrero: number;
    marzo: number;
    abril: number;
    mayo: number;
    junio: number;
    julio: number;
    agosto: number;
    septiembre: number;
    octubre: number;
    noviembre: number;
    diciembre: number;
    total: number;
}

export interface LoteDashboard {
    ip: string
    tmh: number
    tms: number | null
    h2o_porc: number | null
    proveedor: string
    ruc: string | null
    ley_avg: number | null
    rec_porc: number | null
    acopiador: string | null
    estado: string
    estado_analisis: string  // SIN_DATOS | EN_LAB | FALTA_REC | LISTO
    habilitado_ruma: boolean
    volado: boolean
    dirimencia: boolean
    dias_almacen: number
    tiene_rec_pendiente: boolean
}

export interface AnalisisConteo {
    listo: number; falta_rec: number; falta_ley: number; falta_muestreo: number; sin_datos: number
}

export interface AcopiadorStats {
    acopiador: string; lotes: number; tms: number; oz: number; ley_prom: number | null
}

export interface ResumenPagosBloque {
    tms_total: number
    tms_pagado: number
    tms_sin_pagar: number
    gr_recuperable_total: number
    gr_recuperable_pagado: number
    gr_recuperable_sin_pagar: number
    total_usd_total: number
    total_usd_pagado: number
    total_usd_sin_pagar: number
}

export interface ProfitAgregado {
    profit_maquila: number
    profit_rec: number
    profit_consumo: number
    profit_leyes: number
    profit_total: number
    profit_rc: number
    profit_terminos: number
    au_comprado: number
    valor_compra_total: number
}

export interface DashboardResponse {
    kpis: DashboardKPIs
    resumen_pagos: ResumenPagosBloque
    profit: ProfitAgregado
    lotes: LoteDashboard[]
    acopiadores_tmh: AcopiadorTMH[]
    analisis_conteo: AnalisisConteo
    acopiadores_stats: AcopiadorStats[]
    liquidaciones: LiquidacionResumenOut[]
}

//Alertas
export interface AlertaItem {
    tipo: 'VOLADO_STOCK' | 'RETRASO_MUESTREO' | ' RETRASO_LEY' | 'RETRASO_RECUPERACIÓN'
    severidad: 'CRITICA' | 'ALTA' | 'MEDIA'
    ip: string
    proveedor: string
    acopiador: string | null
    horas_retraso: number
    descripcion: string
    fecha_ref: string
}

export interface AlertasConfig {
    horas_pesado_muestreo: number
    horas_muestreo_ley: number
    horas_ley_recuperacion: number
    dias_volado_stock: number
}

export interface AlertasResponse {
    alertas: AlertaItem[]
    config: AlertasConfig
    total_criticas: number
    total_altas: number
    total_medias: number
}

export const dashboardApi = {
    getResumen: (desde?: string, hasta?: string, filtro_estado?: string) => {
        const params: Record<string, string> = {}
        if (desde) params.desde = desde
        if (hasta) params.hasta = hasta
        if (filtro_estado) params.filtro_estado = filtro_estado
        return api.get<DashboardResponse>('/dashboard/resumen', { params }).then(r => r.data)
    },

    async exportar(tipo: 'lotes' | 'acopiadores', clave: string, desde?: string, hasta?: string, filtro_estado?: string): Promise<void> {
        const payload: Record<string, any> = { tipo, clave }
        if (desde) payload.desde = desde
        if (hasta) payload.hasta = hasta
        if (filtro_estado) payload.filtro_estado = filtro_estado
        const res = await api.post(
            '/dashboard/exportar',
            payload,
            { responseType: 'blob' },
        )
        const url = URL.createObjectURL(res.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `${tipo}_paititi_${new Date().toISOString().slice(0, 10)}.xlsx`
        a.click()
        URL.revokeObjectURL(url)
    },

    getAlertas: () =>
        api.get<AlertasResponse>('/dashboard/alertas').then(r => r.data),

    updateAlertasConfig: (config: AlertasConfig) =>
        api.put<AlertasConfig>('/dashboard/alertas/config', config).then(r => r.data),

    guardarObservacion: (tipo: string, ip: string, observacion: string) =>
        api.post('/dashboard/alertas/observacion', { tipo, ip, observacion }).then(r => r.data),

    getTrazabilidad: (ip: string) =>
        api.get<TrazabilidadLoteResponse>(`/dashboard/lotes/${ip}/trazabilidad`, { params: { _t: new Date().getTime() } }).then(r => r.data),
}

// =============================================================================
// TRAZABILIDAD
// =============================================================================

export interface UsuarioResumen {
    id: number
    nombre_completo: string
    rol: string
}

export interface AccionRegistro {
    por: UsuarioResumen | null
    fecha: string | null
}

export interface TrazabilidadSesion {
    id: number
    placa: string | null
    carreta: string | null
    conductor: string | null
    transportista: string | null
    guia_remision: string | null
    guia_transporte: string | null
    registro: AccionRegistro
}

export interface TrazabilidadPesaje {
    numero_ticket: string | null
    sacos: number | null
    granel: boolean
    peso_inicial: number
    peso_final: number
    peso_neto: number
    fecha_inicio: string | null
    fecha_fin: string | null
    es_manual: boolean
    justificacion_manual: string | null
    registro: AccionRegistro
}

export interface TrazabilidadMuestreo {
    intento: number
    peso_humedo: number
    peso_seco: number
    porcentaje_humedad: number | null
    tms_calculado: number | null
    observaciones: string | null
    registro: AccionRegistro
}

export interface TrazabilidadPrueba {
    cip: string | null
    fecha_ingreso: string | null
    fecha_salida: string | null
    malla_porcentaje: number | null
    porcentaje_nacn: number | null
    ph_inicial: number | null
    ph_final: number | null
    adicion_nacn: number | null
    adicion_naoh: number | null
    gasto_agno3: number | null
    registro: AccionRegistro
}

export interface TrazabilidadAnalisisLey {
    id: number
    cip: string | null
    laboratorio: string
    tipo_analisis: string
    material: string
    ley_final: number | null
    ley_gr_tm: number | null
    origen_datos: string
    fecha_analisis: string | null
    certificado_url: string | null
    vigente: boolean
    descarte: AccionRegistro | null
    justificacion_descarte: string | null
    registro: AccionRegistro
}

export interface TrazabilidadAnalisisRec {
    id: number
    cip: string | null
    laboratorio: string
    ley_cabeza: number | null
    ley_cola: number | null
    ley_liquido: number | null
    recuperacion: number | null
    estado: string
    origen_datos: string
    fecha_analisis: string | null
    certificado_url: string | null
    vigente: boolean
    descarte: AccionRegistro | null
    justificacion_descarte: string | null
    registro: AccionRegistro
}

export interface TrazabilidadRuma {
    codigo: string
    estado: string
    fecha_creacion: string | null
    campana: string | null
}

export interface TrazabilidadLiquidacion {
    id: number
    numero_liquidacion: string | null
    estado: string
    precio_oro_usd: number | null
    valor_total_usd: number | null
    fino_recuperable: number | null
    ley_comercial: number | null
    usa_dirimencia: boolean
    generacion: AccionRegistro
    cierre: AccionRegistro | null
}

export interface TrazabilidadAuditoria {
    registro_lote: AccionRegistro
    habilitacion_ruma: AccionRegistro
    cambio_estado: AccionRegistro
}

export interface TrazabilidadMapeoCIP {
    id: number
    codigo_cip: string
    laboratorio: string | null
    fecha_envio: string | null
    tipo_muestra: string | null
}

export interface TrazabilidadLoteResponse {
    ip: string
    estado: string
    tipo_material: string | null
    volado: boolean
    dirimencia: boolean
    habilitado_ruma: boolean
    proveedor: string
    ruc_proveedor: string | null
    acopiador: string | null
    sesion: TrazabilidadSesion
    pesajes: TrazabilidadPesaje[]
    muestreos: TrazabilidadMuestreo[]
    prueba_metalurgica: TrazabilidadPrueba | null
    analisis_ley: TrazabilidadAnalisisLey[]
    analisis_recuperacion: TrazabilidadAnalisisRec[]
    ruma: TrazabilidadRuma | null
    liquidacion: TrazabilidadLiquidacion | null
    auditoria: TrazabilidadAuditoria
    mapeos_cip: TrazabilidadMapeoCIP[]
}
