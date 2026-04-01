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

export interface LoteMuestreo {
    ip: string
    fecha_recepcion: string | null
    fecha_muestreo: string | null
    peso_neto: number
    sacos: number | null
    proveedor_razon_social: string
    estado_muestreo: 'PENDIENTE' | 'COMPLETADO'
    cantidad_intentos_previos: number
    tiene_humedad: boolean
    etiquetado: boolean
    fecha_ingreso_prueba: string | null
    sla_config: {
        h_min: number
        h_max: number
    }
    pendiente_sla: boolean
}

export const muestreoApi = {
    /**
     * Registra un muestreo individual estando online.
     */
    async registrarMuestreo(ipLote: string, datos: MuestreoCreate): Promise<MuestreoOut> {
        const response = await api.post<MuestreoOut>(`/muestreo/lotes/${ipLote}`, datos)
        return response.data
    },

    /**
     * Sincroniza un bloque de muestreos guardados offline.
     */
    async syncBatch(muestreos: MuestreoOfflineItem[]): Promise<SyncMuestreosResponse> {
        const response = await api.post<SyncMuestreosResponse>('/muestreo/sync', { muestreos })
        return response.data
    },

    /**
     * Genera los códigos CIP (Muestreo Ciego) para el laboratorio.
     */
    async generarCips(ipLote: string, cantidad: number = 2): Promise<MapeoCIPOut[]> {
        const response = await api.post<MapeoCIPOut[]>(`/muestreo/lotes/${ipLote}/etiquetas`, {
            cantidad,
            laboratorio: 'Por definir'
        })
        return response.data
    },

    /**
     * Obtiene la lista de lotes que requieren muestreo.
     */
    async obtenerLotes(): Promise<LoteMuestreo[]> {
        // Ajusta la ruta según tu backend real
        const response = await api.get<LoteMuestreo[]>('/muestreo/lotes')
        return response.data
    },

    /**
     * Obtiene las etiquetas CIP generadas para un lote específico.
     */
    async obtenerEtiquetas(ipLote: string): Promise<MapeoCIPOut[]> {
        const response = await api.get<MapeoCIPOut[]>(`/muestreo/lotes/${ipLote}/etiquetas`)
        return response.data
    },
}
