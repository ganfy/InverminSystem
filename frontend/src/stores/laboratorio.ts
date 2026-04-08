import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { laboratorioApi } from '@/api/laboratorio'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import type {
    CIPAnalisisOut,
    LoteLabOut,
    AnalisisLeyCreate,
    AnalisisRecuperacionCreate,
} from '@/types/laboratorio'

export const useLaboratorioStore = defineStore('laboratorio', () => {
    const ui = useUiStore()
    const auth = useAuthStore()

    // ── Estado ────────────────────────────────────────────────────────────────
    const cips = ref<CIPAnalisisOut[]>([])
    const lotes = ref<LoteLabOut[]>([])
    const cargando = ref(false)

    // ── Permiso de ver IP (rol-aware) ─────────────────────────────────────────
    const puedeVerIP = computed(() => {
        const r = auth.user?.rol ?? ''
        return ['Admin', 'Gerencia', 'Comercial'].includes(r)
    })

    const esLaboratorista = computed(() => auth.user?.rol === 'Laboratorista')

    // ── Carga ─────────────────────────────────────────────────────────────────
    async function cargarCips() {
        cargando.value = true
        try {
            cips.value = await laboratorioApi.listarCips()
        } catch {
            ui.toast('Error al cargar CIPs de laboratorio', 'error')
        } finally {
            cargando.value = false
        }
    }

    async function cargarLotes() {
        cargando.value = true
        try {
            lotes.value = await laboratorioApi.listarLotes()
        } catch {
            ui.toast('Error al cargar lotes de laboratorio', 'error')
        } finally {
            cargando.value = false
        }
    }

    async function cargarDetalleLote(ip: string): Promise<LoteLabOut | null> {
        try {
            return await laboratorioApi.detalleLote(ip)
        } catch {
            ui.toast(`Error al cargar lote ${ip}`, 'error')
            return null
        }
    }

    // ── Registro de análisis ──────────────────────────────────────────────────
    async function registrarLey(
        datos: AnalisisLeyCreate,
        archivo?: File | null,
    ): Promise<boolean> {
        try {
            const nuevo = await laboratorioApi.registrarLey(datos)
            if (archivo) {
                await laboratorioApi.subirCertificadoLey(nuevo.id, archivo)
            }
            ui.toast('Análisis de ley registrado', 'success')
            return true
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al registrar análisis de ley', 'error')
            return false
        }
    }

    async function registrarRecuperacion(
        datos: AnalisisRecuperacionCreate,
        archivo?: File | null,
    ): Promise<boolean> {
        try {
            const nuevo = await laboratorioApi.registrarRecuperacion(datos)
            if (archivo) {
                await laboratorioApi.subirCertificadoRecuperacion(nuevo.id, archivo)
            }
            ui.toast('Análisis de recuperación registrado', 'success')
            return true
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al registrar análisis de recuperación', 'error')
            return false
        }
    }

    // ── Descartar análisis ────────────────────────────────────────────────────
    async function descartarLey(analisisId: number, justificacion: string): Promise<boolean> {
        const ok = await ui.showConfirm({
            title: 'Descartar análisis',
            message: '¿Confirmar el descarte de este análisis de ley?',
            confirmLabel: 'Descartar',
            danger: true,
        })
        if (!ok) return false
        try {
            await laboratorioApi.descartarLey(analisisId, { justificacion })
            ui.toast('Análisis descartado', 'success')
            return true
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al descartar', 'error')
            return false
        }
    }

    async function descartarRecuperacion(analisisId: number, justificacion: string): Promise<boolean> {
        const ok = await ui.showConfirm({
            title: 'Descartar análisis',
            message: '¿Confirmar el descarte de este análisis de recuperación?',
            confirmLabel: 'Descartar',
            danger: true,
        })
        if (!ok) return false
        try {
            await laboratorioApi.descartarRecuperacion(analisisId, { justificacion })
            ui.toast('Análisis descartado', 'success')
            return true
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al descartar', 'error')
            return false
        }
    }

    // ── Subir certificado ─────────────────────────────────────────────────────
    async function subirCertificadoLey(analisisId: number, archivo: File): Promise<boolean> {
        try {
            await laboratorioApi.subirCertificadoLey(analisisId, archivo)
            ui.toast('Certificado adjuntado', 'success')
            return true
        } catch {
            ui.toast('Error al subir certificado', 'error')
            return false
        }
    }

    async function subirCertificadoRecuperacion(analisisId: number, archivo: File): Promise<boolean> {
        try {
            await laboratorioApi.subirCertificadoRecuperacion(analisisId, archivo)
            ui.toast('Certificado adjuntado', 'success')
            return true
        } catch {
            ui.toast('Error al subir certificado', 'error')
            return false
        }
    }

    return {
        cips, lotes, cargando,
        puedeVerIP, esLaboratorista,
        cargarCips, cargarLotes, cargarDetalleLote,
        registrarLey, registrarRecuperacion,
        descartarLey, descartarRecuperacion,
        subirCertificadoLey, subirCertificadoRecuperacion,
    }
})
