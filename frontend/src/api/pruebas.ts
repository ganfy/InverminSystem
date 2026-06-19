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
    ip: string
    fecha_recepcion: string | null
    fecha_ingreso: string | null
    fecha_salida: string | null
    malla_porcentaje: number | null
    gasto_agno3: number | null
    estado: 'PENDIENTE' | 'EN PROCESO' | 'COMPLETADO'
    // Etiquetado (nuevo)
    cip_asignado: string | null
    etiquetado: boolean
    // Adiciones acumuladas
    adicion_nacn: number | null
    adicion_naoh: number | null
    // Descarte
    descartado: boolean
    motivo_descarte: string | null
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
}
