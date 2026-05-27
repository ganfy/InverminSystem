import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/api/rumas'
import type { CampanaOut, RumaLista, RumaOut, LoteDisponibleOut, LoteRumaItem } from '@/api/rumas'

export const useRumasStore = defineStore('rumas', () => {
    // ── State ──────────────────────────────────────────────────────────────────
    const campanaActiva = ref<CampanaOut | null>(null)
    const historialCampanas = ref<CampanaOut[]>([])
    const rumas = ref<RumaLista[]>([])
    const rumaDetalle = ref<RumaOut | null>(null)
    const lotesDisponibles = ref<LoteDisponibleOut[]>([])

    const cargando = ref(false)
    const cargandoDetalle = ref(false)
    const error = ref<string | null>(null)

    // ── Computed ───────────────────────────────────────────────────────────────
    /** Suma TMS * ley_avg de un set de ips seleccionados (para preview ruma) */
    function calcularPreviewRuma(ips: string[]): {
        total_tms: number
        ley_ponderada: number | null
        rec_promedio: number | null
        pct_llampo: number | null
    } {
        if (!rumaDetalle.value) return { total_tms: 0, ley_ponderada: null, rec_promedio: null, pct_llampo: null }

        // Lotes del detalle actual + lotes disponibles seleccionados
        const todos: LoteRumaItem[] = [
            ...rumaDetalle.value.lotes,
            ...lotesDisponibles.value
                .filter(l => ips.includes(l.ip))
                .map(l => ({
                    ip: l.ip,
                    proveedor: l.proveedor,
                    tmh: l.tmh,
                    tms: l.tms,
                    ley_avg: l.ley_avg,
                    rec_porc: l.rec_porc,
                    tipo_material: l.tipo_material,
                    habilitado_ruma: true,
                    volado: l.volado,
                })),
        ]
        // Dedup por IP (en caso de lotes ya en ruma que también estén en disponibles)
        const vistos = new Set<string>()
        const filtrados = todos.filter(l => {
            if (vistos.has(l.ip)) return false
            vistos.add(l.ip)
            return ips.includes(l.ip)
        })

        let total_tms = 0, suma_tms_ley = 0, tms_con_ley = 0
        let suma_rec = 0, tms_con_rec = 0, llampo_tms = 0

        for (const l of filtrados) {
            const tms = l.tms ?? 0
            total_tms += tms
            if (l.ley_avg != null && tms > 0) { suma_tms_ley += tms * l.ley_avg; tms_con_ley += tms }
            if (l.rec_porc != null && tms > 0) { suma_rec += tms * l.rec_porc; tms_con_rec += tms }
            if (l.tipo_material?.toLowerCase().includes('llampo')) llampo_tms += tms
        }

        return {
            total_tms: +total_tms.toFixed(3),
            ley_ponderada: tms_con_ley > 0 ? +(suma_tms_ley / tms_con_ley).toFixed(4) : null,
            rec_promedio: tms_con_rec > 0 ? +(suma_rec / tms_con_rec).toFixed(2) : null,
            pct_llampo: total_tms > 0 ? +(llampo_tms / total_tms * 100).toFixed(1) : null,
        }
    }

    // ── Actions: Campañas ──────────────────────────────────────────────────────
    async function cargarCampanaActiva() {
        cargando.value = true; error.value = null
        try {
            const r = await api.getCampanaActiva()
            campanaActiva.value = r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cargar campaña activa'
            campanaActiva.value = null
        } finally { cargando.value = false }
    }

    async function cargarHistorial() {
        cargando.value = true; error.value = null
        try {
            const r = await api.getCampanas()
            historialCampanas.value = r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cargar historial'
        } finally { cargando.value = false }
    }

    async function cerrarCampana(id: number, metaNueva: number): Promise<boolean> {
        cargando.value = true; error.value = null
        try {
            await api.cerrarCampana(id, metaNueva)
            await cargarCampanaActiva()
            await cargarHistorial()
            return true
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cerrar campaña'
            return false
        } finally { cargando.value = false }
    }

    async function editarMeta(id: number, meta: number): Promise<boolean> {
        cargando.value = true; error.value = null
        try {
            const r = await api.editarMetaCampana(id, meta)
            campanaActiva.value = r.data
            return true
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al editar meta'
            return false
        } finally { cargando.value = false }
    }

    // ── Actions: Rumas ─────────────────────────────────────────────────────────
    async function cargarRumas() {
        cargando.value = true; error.value = null
        try {
            const r = await api.getRumas()
            rumas.value = r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cargar rumas'
        } finally { cargando.value = false }
    }

    async function crearRuma(): Promise<RumaOut | null> {
        cargando.value = true; error.value = null
        try {
            const r = await api.crearRuma()
            rumas.value.push(r.data)
            return r.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al crear ruma'
            return null
        } finally { cargando.value = false }
    }

    async function cargarDetalleRuma(id: number) {
        cargandoDetalle.value = true; error.value = null
        try {
            const [rDetalle, rDisp] = await Promise.all([
                api.getRuma(id),
                api.getLotesDisponibles(),
            ])
            rumaDetalle.value = rDetalle.data
            lotesDisponibles.value = rDisp.data
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cargar ruma'
        } finally { cargandoDetalle.value = false }
    }

    async function guardarAsignacion(rumaId: number, ips: string[]): Promise<boolean> {
        cargandoDetalle.value = true; error.value = null
        try {
            const r = await api.asignarLotes(rumaId, ips)
            rumaDetalle.value = r.data
            // Refrescar disponibles (algunos ya no estarán)
            const rd = await api.getLotesDisponibles()
            lotesDisponibles.value = rd.data
            // Actualizar lista resumida
            const idx = rumas.value.findIndex(r2 => r2.id === rumaId)
            if (idx >= 0) {
                const rumaActual = rumas.value[idx]
                if (rumaActual) {
                    rumas.value[idx] = {
                        ...rumaActual,
                        total_lotes: r.data.total_lotes,
                        total_tms: r.data.total_tms,
                        ley_ponderada: r.data.ley_ponderada,
                        rec_promedio: r.data.rec_promedio,
                    }
                }
            }
            return true
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al guardar asignación'
            return false
        } finally { cargandoDetalle.value = false }
    }

    async function cerrarRuma(id: number): Promise<boolean> {
        cargando.value = true; error.value = null
        try {
            const r = await api.cerrarRuma(id)
            if (rumaDetalle.value?.id === id) rumaDetalle.value = r.data
            const idx = rumas.value.findIndex(r2 => r2.id === id)
            if (idx >= 0 && rumas.value[idx]) rumas.value[idx].estado = 'CERRADA'
            return true
        } catch (e: any) {
            error.value = e?.response?.data?.detail ?? 'Error al cerrar ruma'
            return false
        } finally { cargando.value = false }
    }

    function limpiarDetalle() {
        rumaDetalle.value = null
        lotesDisponibles.value = []
    }

    return {
        campanaActiva, historialCampanas, rumas, rumaDetalle, lotesDisponibles,
        cargando, cargandoDetalle, error,
        calcularPreviewRuma,
        cargarCampanaActiva, cargarHistorial, cerrarCampana, editarMeta,
        cargarRumas, crearRuma, cargarDetalleRuma, guardarAsignacion, cerrarRuma, limpiarDetalle,
    }
})
