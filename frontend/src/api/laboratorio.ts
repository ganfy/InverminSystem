import api from './axios'
import type {
    AnalisisLeyCreate, AnalisisLeyOut,
    AnalisisRecuperacionCreate, AnalisisRecuperacionOut,
    MuestraLaboratorioItem
} from '@/types/laboratorio'

export const laboratorioApi = {
    // --- LEY (Fire Assay) ---
    async registrarLey(datos: AnalisisLeyCreate): Promise<AnalisisLeyOut> {
        const response = await api.post('/laboratorio/ley', datos)
        return response.data
    },

    async subirCertificadoLey(analisisId: number, archivo: File): Promise<{ mensaje: string, url: string }> {
        const formData = new FormData()
        formData.append('archivo', archivo)

        const response = await api.post(`/laboratorio/ley/${analisisId}/certificado`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return response.data
    },

    // --- RECUPERACIÓN (Botella) ---
    async registrarRecuperacion(datos: AnalisisRecuperacionCreate): Promise<AnalisisRecuperacionOut> {
        const response = await api.post('/laboratorio/recuperacion', datos)
        return response.data
    },

    async subirCertificadoRecuperacion(analisisId: number, archivo: File): Promise<{ mensaje: string, url: string }> {
        const formData = new FormData()
        formData.append('archivo', archivo)

        const response = await api.post(`/laboratorio/recuperacion/${analisisId}/certificado`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        return response.data
    },

    // --- SYNC OFFLINE ---
    async sincronizarBatch(payload: any): Promise<any> {
        const response = await api.post('/laboratorio/offline/sync', payload)
        return response.data
    },


    async obtenerMuestras(): Promise<MuestraLaboratorioItem[]> {
        const response = await api.get('/laboratorio/muestras')
        return response.data
    },
}
