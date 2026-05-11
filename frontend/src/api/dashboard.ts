import api from './axios'

export interface DashboardKPIs {
    au_real_100: number
    au_real_rec: number
    tmh_stock: number
    tms_stock: number
    oz_stock: number
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
}

export interface DashboardResponse {
    kpis: DashboardKPIs
    lotes: LoteDashboard[]
}

export const dashboardApi = {
    getResumen: () => api.get<DashboardResponse>('/dashboard/resumen').then(r => r.data)
}
