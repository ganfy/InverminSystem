import api from './axios'

export interface PruebaMetalurgicaCreate {
    malla_porcentaje: number | null
    porcentaje_nacn: number | null
    ph_inicial: number | null
    ph_final: number | null
    adicion_nacn: number | null
    adicion_naoh: number | null
    gasto_agno3: number | null
    fecha_ingreso: string
}

export interface PruebaMetalurgicaOut extends PruebaMetalurgicaCreate {
    id: number
    lote_id: number
    cip: string | null
    fecha_salida: string | null
}

export interface LotePruebaList {
    prueba_id: number
    lote_id: number
    ip: string
    es_reensayo: boolean
    fecha_recepcion: string | null
    fecha_ingreso: string | null
    fecha_salida: string | null
    malla_porcentaje: number | null
    gasto_agno3: number | null
    estado: 'PENDIENTE' | 'EN PROCESO' | 'COMPLETADO'
    // Etiquetado (nuevo)
    cip_asignado: string | null
    cips_asignados: string[]
    etiquetado: boolean
    // Adiciones acumuladas
    adicion_nacn: number | null
    adicion_naoh: number | null
    // Descarte
    descartado: boolean
    motivo_descarte: string | null
    // Sub-tipos ya enviados al laboratorio (tienen análisis vigente)
    sub_tipos_enviados: string[]
    sub_tipos_enviados_por_cip: Record<string, string[]>
}

export interface EtiquetadoPruebaOut {
    ip: string
    cip: string
    mensaje: string
}

export interface PruebaRecuperacionItem {
    ip: string
    cip: string
    lote_id: number
    proveedor: string
    fecha_salida: string | null
    ley_cabeza: number
    tiene_analisis_recuperacion: boolean
}

export interface RecuperacionItem {
    ip: string
    cip: string | null
    proveedor: string
    fecha_analisis: string | null
    ley_cola_au_oz_tc: number | null
    ley_cola_au_gr_tm: number | null
    ley_cola_ag_gr_tm: number | null
    solucion_au_g_m3: number | null
    solucion_ag_g_m3: number | null
    recuperacion: number | null
    vigente: boolean
}

export interface PruebaOfflineItem {
    offline_id: string
    ip: string
    datos: PruebaMetalurgicaCreate
}

export interface SyncCipPruebaPayload {
    offline_id: string
    ip: string
    codigo_cip1: string
    codigo_cip2: string
    correlativo1: number
    correlativo2: number
    tipo: 'RecuperacionInterno' | 'RecuperacionExterno'
}

export interface SyncCipsPruebasResponse {
    resultados: Array<{
        offline_id: string
        server_id_cip1: number | null
        server_id_cip2: number | null
        error: string | null
    }>
}

export const pruebasApi = {

    async obtenerListaPruebas(): Promise<LotePruebaList[]> {
        const { data } = await api.get('/pruebas/lista')
        return data
    },

    async registrarPrueba(ip: string, datos: PruebaMetalurgicaCreate): Promise<PruebaMetalurgicaOut> {
        const { data } = await api.post(`/pruebas/${ip}`, datos)
        return data
    },

    async obtenerDetallePrueba(ipLote: string): Promise<PruebaMetalurgicaOut | null> {
        try {
            const { data } = await api.get(`/pruebas/${ipLote}`)
            return data
        } catch (e: any) {
            if (e?.response?.status === 404) return null
            throw e
        }
    },

    /** Genera CIP de recuperación para una prueba COMPLETADO */
    async etiquetar(ip: string): Promise<EtiquetadoPruebaOut> {
        const { data } = await api.post(`/pruebas/${ip}/etiquetar`)
        return data
    },

    /** Pruebas COMPLETADO con ley_cabeza disponible para análisis de recuperación */
    async paraRecuperacion(): Promise<PruebaRecuperacionItem[]> {
        const { data } = await api.get('/pruebas/para-recuperacion')
        return data
    },

    /** Leyes de cola + % recuperación para vista de Técnico Pruebas */
    async listarRecuperaciones(): Promise<RecuperacionItem[]> {
        const { data } = await api.get('/pruebas/recuperaciones')
        return data
    },

    async syncBatch(pruebas: PruebaOfflineItem[]): Promise<any> {
        const { data } = await api.post('/pruebas/sync', { pruebas })
        return data
    },

    /** Solicita remuestreo: siempre crea un nuevo registro (auditoría) */
    async solicitarRemuestreo(ip: string): Promise<PruebaMetalurgicaOut> {
        const { data } = await api.post(`/pruebas/${ip}/remuestreo`)
        return data
    },

    /** Descartar prueba (envase roto, etc.) — mantiene registro para trazabilidad */
    async descartar(ip: string, motivo: string): Promise<PruebaMetalurgicaOut> {
        const { data } = await api.post(`/pruebas/${ip}/descartar`, { motivo })
        return data
    },

    /** Registrar adición parcial de NaCN/NaOH (acumulativa a lo existente) */
    async registrarAdicion(ip: string, datos: { adicion_nacn?: number | null, adicion_naoh?: number | null, porcentaje_nacn?: number | null }): Promise<PruebaMetalurgicaOut> {
        const { data } = await api.post(`/pruebas/${ip}/adicion`, datos)
        return data
    },

    /**
     * Envía las muestras de una prueba COMPLETADO al laboratorio interno (Paititi).
     * subTipos: ['SOLIDOS', 'SOLUCION'] para ambos, o solo uno.
     * Crea registros PENDIENTE en análisis_recuperacion para que el laboratorista los complete.
     * Usa permiso PRUEBAS_MET (no requiere rol de Comercial/Laboratorio).
     */
    async enviarALaboratorio(ip: string, subTipos: string[], cip: string | null = null): Promise<any> {
        const payload: any = { sub_tipos: subTipos }
        if (cip) payload.cip = cip
        const { data } = await api.post(`/pruebas/${ip}/enviar-laboratorio`, payload)
        return data
    },

    /** Sincroniza los pares CIP de recuperación generados offline al reconectar. */
    async syncCipsPruebas(cips: SyncCipPruebaPayload[]): Promise<SyncCipsPruebasResponse> {
        const { data } = await api.post<SyncCipsPruebasResponse>('/pruebas/sync-cips', { cips })
        return data
    },

    /** Resta 24 horas a la fecha de ingreso de una prueba EN PROCESO */
    async adelantarFecha(ip: string): Promise<PruebaMetalurgicaOut> {
        const { data } = await api.post(`/pruebas/${ip}/adelantar-fecha`)
        return data
    },
}
