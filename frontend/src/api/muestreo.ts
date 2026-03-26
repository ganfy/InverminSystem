import api from './axios'

export interface MuestreoCreate {
    intento: number
    peso_humedo: number
    peso_seco: number
    observaciones?: string | null
    fecha_muestreo?: string | null
}

export interface MuestreoOut {
    id: number
    lote_id: number
    intento: number
    peso_humedo: number
    peso_seco: number
    porcentaje_humedad: number
    tms_calculado: number
    creado_en: string
    creado_por: number
    observaciones?: string | null
}

export interface MapeoCIPOut {
    id: number
    lote_id: number
    codigo_cip: string
    laboratorio?: string | null
    tipo_muestra?: string | null
}

export interface MuestreoOfflineItem {
    offline_id: string
    ip: string
    datos: MuestreoCreate
}

export interface SyncMuestreosResponse {
    resultados: Array<{
        offline_id: string
        server_id: number | null
        error: string | null
    }>
}

export const muestreoApi = {
    /**
     * Registra un muestreo individual estando online.
     */
    async registrarMuestreo(ipLote: string, datos: MuestreoCreate): Promise<MuestreoOut> {
        const response = await api.post<MuestreoOut>(`/laboratorio/lotes/${ipLote}/muestreos`, datos)
        return response.data
    },

    /**
     * Sincroniza un bloque de muestreos guardados offline.
     */
    async syncBatch(muestreos: MuestreoOfflineItem[]): Promise<SyncMuestreosResponse> {
        const response = await api.post<SyncMuestreosResponse>('/laboratorio/muestreos/sync', { muestreos })
        return response.data
    },

    /**
     * Genera los códigos CIP (Muestreo Ciego) para el laboratorio.
     */
    async generarCips(ipLote: string, cantidad: number = 2): Promise<MapeoCIPOut[]> {
        const response = await api.post<MapeoCIPOut[]>(`/laboratorio/lotes/${ipLote}/cips`, {
            cantidad,
            laboratorio: 'Por definir'
        })
        return response.data
    }
}
