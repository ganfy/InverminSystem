import api from './axios'
import type {
    AnalisisLeyCreate,
    AnalisisLeyOut,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    CIPAnalisisOut,
    LoteLabOut,
    DescartarRequest,
    SyncLaboratorioRequest,
    SyncLaboratorioResponse,
} from '@/types/laboratorio'

export const laboratorioApi = {

    // ── Vista por CIP (Laboratorista + Comercial) ─────────────────────────────
    async listarCips(): Promise<CIPAnalisisOut[]> {
        const { data } = await api.get('/laboratorio/cips')
        return data
    },

    // ── Vista por Lote/IP (solo Comercial/Gerencia/Admin) ─────────────────────
    async listarLotes(): Promise<LoteLabOut[]> {
        const { data } = await api.get('/laboratorio/lotes')
        return data
    },

    async detalleLote(ip: string): Promise<LoteLabOut> {
        const { data } = await api.get(`/laboratorio/lotes/${ip}`)
        return data
    },

    // ── Análisis de Ley ───────────────────────────────────────────────────────
    async registrarLey(datos: AnalisisLeyCreate): Promise<AnalisisLeyOut> {
        const { data } = await api.post('/laboratorio/ley', datos)
        return data
    },

    async descartarLey(analisisId: number, req: DescartarRequest): Promise<AnalisisLeyOut> {
        const { data } = await api.patch(`/laboratorio/ley/${analisisId}/descartar`, req)
        return data
    },

    async subirCertificadoLey(analisisId: number, archivo: File): Promise<{ certificado_url: string }> {
        const form = new FormData()
        form.append('archivo', archivo)
        const { data } = await api.post(`/laboratorio/ley/${analisisId}/certificado`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return data
    },

    // ── Análisis de Recuperación ──────────────────────────────────────────────
    async registrarRecuperacion(datos: AnalisisRecuperacionCreate): Promise<AnalisisRecuperacionOut> {
        const { data } = await api.post('/laboratorio/recuperacion', datos)
        return data
    },

    async descartarRecuperacion(analisisId: number, req: DescartarRequest): Promise<AnalisisRecuperacionOut> {
        const { data } = await api.patch(`/laboratorio/recuperacion/${analisisId}/descartar`, req)
        return data
    },

    async subirCertificadoRecuperacion(analisisId: number, archivo: File): Promise<{ certificado_url: string }> {
        const form = new FormData()
        form.append('archivo', archivo)
        const { data } = await api.post(`/laboratorio/recuperacion/${analisisId}/certificado`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return data
    },

    // ── Sync Offline ──────────────────────────────────────────────────────────
    async sincronizarBatch(payload: SyncLaboratorioRequest): Promise<SyncLaboratorioResponse> {
        const { data } = await api.post('/laboratorio/sync', payload)
        return data
    },
}
