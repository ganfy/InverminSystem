import api from './axios'

export interface DashboardKPIs {
    au_real_100: number
    au_real_rec: number
    tmh_stock: number
    tms_stock: number
    oz_stock: number
    oz_habilitados: number
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

export interface DashboardResponse {
    kpis: DashboardKPIs
    lotes: LoteDashboard[]
    acopiadores_tmh: AcopiadorTMH[]
    analisis_conteo: AnalisisConteo
    acopiadores_stats: AcopiadorStats[]
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
    getResumen: () => api.get<DashboardResponse>('/dashboard/resumen').then(r => r.data),

    async exportar(tipo: 'lotes' | 'acopiadores', clave: string): Promise<void> {
        const res = await api.post(
            '/dashboard/exportar',
            { tipo, clave },
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
}
