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
    fecha_salida: string | null
}

export interface LotePruebaList {
    ip: string
    fecha_recepcion: string | null
    fecha_salida: string | null
    malla_porcentaje: number | null
    gasto_agno3: number | null
    estado: 'PENDIENTE' | 'EN PROCESO' | 'COMPLETO'
}

export interface PruebaOfflineItem {
    offline_id: string
    ip: string
    datos: PruebaMetalurgicaCreate
}

export const pruebasApi = {
    async obtenerListaPruebas(): Promise<LotePruebaList[]> {
        const response = await api.get<LotePruebaList[]>('/pruebas/lista')
        return response.data
    },

    // Cambiamos el parámetro a 'ip'
    async registrarPrueba(ip: string, datos: PruebaMetalurgicaCreate): Promise<any> {
        const response = await api.post(`/pruebas/${ip}`, datos)
        return response.data
    },

    async syncBatch(pruebas: PruebaOfflineItem[]): Promise<any> {
        const response = await api.post('/pruebas/sync', { pruebas })
        return response.data
    }
}
