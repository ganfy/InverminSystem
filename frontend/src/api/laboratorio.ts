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

export interface GuardarCertResult {
    ruta: string
    url: string
}

export interface LeyComercialCalc {
    ley_planta: number              // base para factores = average(planta+externo)
    ley_planta_solo: number | null  // solo lab propio — para display
    ley_externo: number | null      // labs externos — para display
    ley_comercial: number           // ley_base → factores aplicados
    ley_minero: number | null
    ley_promedio: number | null     // (comercial+minero)/2 o clamp dirimencia
    tiene_dirimencia: boolean
    descuento_aplicado: number
    factor_aplicado: number
    ajuste_rango: boolean
    sin_parametros: boolean
    detalle: string
}

export interface SyncLaboratorioItem {
    offline_id: string
    datos: {
        cip: string
        laboratorio: string
        tipo_analisis: string
        material: string
        ley_fino: number
        ley_grueso: number
        origen_datos: string
        fecha_analisis: string
    }
}

export interface SyncResultado {
    offline_id: string
    server_id: number | null
    error: string | null
}

export interface AnalisisAgCreate {
    au_ag_mg: number
    au_mg: number
    peso_muestra: number
    laboratorio: string
    fecha_analisis?: string | null
}

export interface AnalisisAgOut {
    id: number
    lote_id: number
    lote_ip: string | null
    laboratorio: string
    ley_ag_gr_tm: number
    ley_ag_oz_tc: number
    fecha_analisis: string | null
    vigente: boolean
    creado_por: number
    creado_en: string
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

    async detalleLote(ip: string, material?:string): Promise<LoteLabOut> {
        const { data } = await api.get(`/laboratorio/lotes/${ip}`, {
            params: material ? { material } : undefined,
        })
        return data
    },

    // ── Análisis de Ley ───────────────────────────────────────────────────────
    async registrarLey(datos: AnalisisLeyCreate): Promise<AnalisisLeyOut> {
        const { data } = await api.post('/laboratorio/ley', datos)
        return data
    },

    async registrarLeyAg(analisisId: number, datos: AnalisisAgCreate): Promise<AnalisisAgOut> {
        const { data } = await api.post(`/laboratorio/ley/${analisisId}/ag`, datos)
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
        console.log('Enviando recuperación interna con datos:', { ip, datos })
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

    // Soft delete - oculta de todas las vistas (Admin/Gerencia/Comercial)
    async eliminarLey(analisisId: number): Promise<void> {
        await api.delete(`/laboratorio/ley/${analisisId}`)
    },

    async eliminarRecuperacion(analisisId: number): Promise<void> {
        await api.delete(`/laboratorio/recuperacion/${analisisId}`)
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

    // ── Certificado LEY ───────────────────────────────────────────────────────

    /** Abre el cert de ley en nueva pestaña para previsualizar */
    async previewCertificadoLeyPdf(ip: string): Promise<void> {
        const response = await api.get(`/laboratorio/lotes/${ip}/certificado-pdf?inline=true`, {
            responseType: 'blob',
        })
        const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        window.open(url, '_blank')
        setTimeout(() => URL.revokeObjectURL(url), 10_000)
    },

    /** Descarga el cert de ley como archivo */
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

    /** Genera y guarda el cert de ley en storage del servidor */
    async guardarCertificadoLey(ip: string): Promise<GuardarCertResult> {
        const { data } = await api.post(`/laboratorio/lotes/${ip}/guardar-certificado-ley`)
        return data
    },

    // ── Certificado RECUPERACIÓN ──────────────────────────────────────────────

    /** Abre el cert de recuperación en nueva pestaña para previsualizar */
    async previewCertificadoRecPdf(ip: string): Promise<void> {
        const response = await api.get(`/laboratorio/lotes/${ip}/certificado-recuperacion-pdf?inline=true`, {
            responseType: 'blob',
        })
        const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        window.open(url, '_blank')
        setTimeout(() => URL.revokeObjectURL(url), 10_000)
    },

    /** Descarga el cert de recuperación como archivo */
    async descargarCertificadoRecPdf(ip: string): Promise<void> {
        const response = await api.get(`/laboratorio/lotes/${ip}/certificado-recuperacion-pdf`, {
            responseType: 'blob',
        })
        const url = URL.createObjectURL(response.data)
        const a = document.createElement('a')
        a.href = url
        a.download = `certificado_rec_${ip.replace(/-/g, '_')}.pdf`
        a.click()
        URL.revokeObjectURL(url)
    },

    /** Genera y guarda el cert de recuperación en storage del servidor */
    async guardarCertificadoRec(ip: string): Promise<GuardarCertResult> {
        const { data } = await api.post(`/laboratorio/lotes/${ip}/guardar-certificado-recuperacion`)
        return data
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
    async syncLaboratorio(payload: SyncLaboratorioRequest): Promise<SyncLaboratorioResponse> {
        const { data } = await api.post('/laboratorio/sync', payload)
        return data
    },

    async registrarLeyPorIP(
        ip: string,
        datos: {
            tipo_analisis: 'minero' | 'dirimencia'
            laboratorio: string
            ley_fino: number
            ley_grueso: number
            material?: string
            fecha_analisis?: string
        }
    ): Promise<AnalisisLeyOut> {
        const { data } = await api.post(`/laboratorio/lotes/${ip}/ley`, datos)
        return data
    },
}

export async function descargarCertificadoLey(analisisId: number): Promise<void> {
    const response = await api.get(`/laboratorio/ley/${analisisId}/certificado`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `Certificado_Ley_${analisisId}.pdf`
    link.click()
    URL.revokeObjectURL(url)
}

export async function descargarCertificadoRecuperacion(analisisId: number): Promise<void> {
    const response = await api.get(`/laboratorio/recuperacion/${analisisId}/certificado`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `Certificado_Rec_${analisisId}.pdf`
    link.click()
    URL.revokeObjectURL(url)
}
