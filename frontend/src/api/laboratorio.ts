import api from './axios'
import type {
    AnalisisLeyCreate,
    AnalisisLeyOut,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    CIPAnalisisOut,
    CompletarRecuperacionRequest,
    DescartarRequest,
    EnviarRecuperacionInternaRequest,
    LoteLabOut,
    SyncLaboratorioRequest,
    SyncLaboratorioResponse,
} from '@/types/laboratorio'

export interface ExtraerLeyResult {
    cip: string | null
    n_informe: string | null
    laboratorio: string | null
    fecha_analisis: string | null
    ley_fino: number | null      // malla -140/-150
    ley_grueso: number | null    // malla +140/+150
    ley_final: number | null     // fino + grueso (extraído o calculado)
    ley_gr_tm: number | null     // referencia gr/TM
    texto_raw: string
}

export interface ExtraerRecResult {
    cip: string | null
    n_informe: string | null
    laboratorio: string | null
    fecha_analisis: string | null
    ley_liquido_gm3: number | null  // AAS g/m3
    ley_cola: number | null
    recuperacion: number | null
    texto_raw: string
}

export interface LeyComercialCalc {
    ley_planta: number
    ley_comercial: number
    descuento_aplicado: number
    factor_aplicado: number
    ajuste_rango: boolean
    sin_parametros: boolean
    detalle: string
}

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

    // ── Flujo recuperación interna (Comercial crea pending) ───────────────────
    async enviarRecuperacion(
        ip: string,
        datos: EnviarRecuperacionInternaRequest = {},
    ): Promise<AnalisisRecuperacionOut> {
        const { data } = await api.post(`/laboratorio/lotes/${ip}/enviar-recuperacion`, datos)
        return data
    },

    // ── Laboratorista completa un pending ─────────────────────────────────────
    async completarRecuperacion(
        analisisId: number,
        datos: CompletarRecuperacionRequest,
    ): Promise<AnalisisRecuperacionOut> {
        const { data } = await api.patch(`/laboratorio/recuperacion/${analisisId}/completar`, datos)
        return data
    },

    // ── Registro directo (externo via certificado) ────────────────────────────
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

    async extraerCertificadoRecuperacion(archivo: File): Promise<Record<string, any>> {
        const form = new FormData()
        form.append('archivo', archivo)
        const { data } = await api.post('/laboratorio/certificado/extraer-recuperacion', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return data
    },

    async extraerCertificadoLey(archivo: File, laboratorio: string = ''): Promise<ExtraerLeyResult> {
        const fd = new FormData()
        fd.append('archivo', archivo)
        const params = laboratorio ? `?laboratorio=${encodeURIComponent(laboratorio)}` : ''
        const { data } = await api.post(`/laboratorio/certificado/extraer-ley${params}`, fd, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return data
    },

    async extraerCertificadoRec(archivo: File, laboratorio: string = ''): Promise<ExtraerRecResult> {
        const fd = new FormData()
        fd.append('archivo', archivo)
        const params = laboratorio ? `?laboratorio=${encodeURIComponent(laboratorio)}` : ''
        const { data } = await api.post(`/laboratorio/certificado/extraer-recuperacion${params}`, fd, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        return data
    },

    async getLeyComercial(ip: string): Promise<LeyComercialCalc> {
        const { data } = await api.get(`/laboratorio/lotes/${ip}/ley-comercial`)
        return data
    },

    async descargarCertificadoPdf(ip: string): Promise<void> {
        const response = await api.get(`/laboratorio/lotes/${ip}/certificado-pdf`, {
            responseType: 'blob',
        })
        const url = URL.createObjectURL(response.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `certificado_ley_${ip.replace(/-/g, '_')}.pdf`
        a.click()
        URL.revokeObjectURL(url)
    },

    async descargarCertificadoEnsayo(cip: string): Promise<void> {
        const response = await api.get(`/laboratorio/cips/${encodeURIComponent(cip)}/certificado-ensayo`, {
            responseType: 'blob',
        })
        const url = URL.createObjectURL(response.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `ensayo_${cip.replace(/-/g, '_')}.pdf`
        a.click()
        URL.revokeObjectURL(url)
    },

    async obtenerUrlArchivoVirtual(rutaArchivo: string): Promise<string> {
        const { data } = await api.get(`/laboratorio/archivos/${rutaArchivo}`, { responseType: 'blob' })
        // Crea una URL temporal del archivo blob para previsualizar
        return URL.createObjectURL(data)
    },

    async generarCertificadoLeyInterno(analisisId: number): Promise<AnalisisLeyOut> {
        const { data } = await api.post(`/laboratorio/ley/${analisisId}/generar-certificado`)
        return data
    },
    async generarCertificadoRecInterno(analisisId: number): Promise<AnalisisRecuperacionOut> {
        const { data } = await api.post(`/laboratorio/recuperacion/${analisisId}/generar-certificado`)
        return data
    },

    // ── Sync Offline ──────────────────────────────────────────────────────────
    async sincronizarBatch(payload: SyncLaboratorioRequest): Promise<SyncLaboratorioResponse> {
        const { data } = await api.post('/laboratorio/sync', payload)
        return data
    },
}
