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

    async syncBatch(pruebas: PruebaOfflineItem[]): Promise<any> {
        const { data } = await api.post('/pruebas/sync', { pruebas })
        return data
    },
}
