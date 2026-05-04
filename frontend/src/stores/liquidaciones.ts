import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/liquidaciones'
import type {
    LiquidacionResumenOut,
    LiquidacionDetalleOut,
    LiquidacionPreviewOut,
    LiquidacionPreviewRequest,
    LiquidacionCreate,
    LoteDisponible,
} from '@/api/liquidaciones'

export const useLiquidacionesStore = defineStore('liquidaciones', () => {
    const lista = ref<LiquidacionResumenOut[]>([])
    const detalle = ref<LiquidacionDetalleOut | null>(null)
    const preview = ref<LiquidacionPreviewOut | null>(null)
    const lotesDisponibles = ref<LoteDisponible[]>([])
    const cargando = ref(false)
    const error = ref<string | null>(null)

    async function cargarLista(params?: { provacop_id?: number; estado?: string }) {
        cargando.value = true
        error.value = null
        try {
            const r = await api.getLiquidaciones(params)
            lista.value = r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cargar liquidaciones'
        } finally {
            cargando.value = false
        }
    }

    async function cargarDetalle(id: number) {
        cargando.value = true
        error.value = null
        try {
            const r = await api.getLiquidacion(id)
            detalle.value = r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cargar liquidacion'
        } finally {
            cargando.value = false
        }
    }

    async function cargarLotesDisponibles(provacop_id: number) {
        cargando.value = true
        error.value = null
        try {
            const r = await api.getLotesDisponibles(provacop_id)
            lotesDisponibles.value = r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cargar lotes'
        } finally {
            cargando.value = false
        }
    }

    async function calcularPreview(req: LiquidacionPreviewRequest): Promise<LiquidacionPreviewOut | null> {
        cargando.value = true
        error.value = null
        try {
            const r = await api.previewLiquidacion(req)
            preview.value = r.data
            return r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error calculando preview'
            return null
        } finally {
            cargando.value = false
        }
    }

    async function crear(req: LiquidacionCreate): Promise<LiquidacionDetalleOut | null> {
        cargando.value = true
        error.value = null
        try {
            const r = await api.crearLiquidacion(req)
            lista.value.unshift({
                id: r.data.id,
                numero_liquidacion: r.data.numero_liquidacion,
                estado: r.data.estado,
                provacop_id: r.data.provacop_id,
                proveedor_razon_social: r.data.proveedor_razon_social,
                proveedor_ruc: r.data.proveedor_ruc,
                acopiador_nombre: r.data.acopiador_nombre,
                spot_usd: r.data.spot_usd,
                total_usd: r.data.total_usd,
                count_lotes: r.data.count_lotes,
                fecha_creacion: r.data.fecha_creacion,
            })
            return r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al crear liquidacion'
            return null
        } finally {
            cargando.value = false
        }
    }

    async function cambiarEstado(id: number, estado: string): Promise<boolean> {
        cargando.value = true
        error.value = null
        try {
            const r = await api.cambiarEstadoLiquidacion(id, estado)
            if (detalle.value?.id === id) {
                detalle.value = r.data
            }
            if (Array.isArray(lista.value)) {
                const item = lista.value.find((l) => l.id === id)

                if (item) {
                    item.estado = estado
                }
            }
            return true
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error cambiando estado'
            return false
        } finally {
            cargando.value = false
        }
    }

    function limpiarPreview() {
        preview.value = null
    }

    const kpis = ref<import('@/api/liquidaciones').LiquidacionesKPI | null>(null)

    async function cargarKPIs() {
        try {
            const r = await api.getLiquidacionesKPIs()
            kpis.value = r.data
        } catch { /* silencioso */ }
    }

    return {
        lista, detalle, preview, lotesDisponibles, cargando, error,
        cargarLista, cargarDetalle, cargarLotesDisponibles,
        calcularPreview, crear, cambiarEstado, limpiarPreview,
        kpis, cargarKPIs
    }
})
