import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { laboratorioApi } from '@/api/laboratorio'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import type {
    AnalisisLeyCreate,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    CIPAnalisisOut,
    CompletarRecuperacionRequest,
    EnviarRecuperacionInternaRequest,
    LoteLabOut,
    AnalisisLeyOut,
} from '@/types/laboratorio'
import { useSync } from '@/composables/useSync'
import { encolarAnalisisLey } from '@/composables/useOfflineQueue'

export const useLaboratorioStore = defineStore('laboratorio', () => {
    const ui = useUiStore()
    const auth = useAuthStore()

    const cips = ref<CIPAnalisisOut[]>([])
    const lotes = ref<LoteLabOut[]>([])
    const cargando = ref(false)

    const puedeVerIP = computed(() => {
        const r = auth.user?.rol ?? ''
        return ['Admin', 'Gerencia', 'Comercial'].includes(r)
    })

    const esLaboratorista = computed(() => auth.user?.rol === 'Laboratorista')

    const puedeImportarCert = computed(() => {
        const r = auth.user?.rol ?? ''
        return ['Admin', 'Gerencia', 'Comercial'].includes(r)
    })

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

    // ── Análisis de Ley ───────────────────────────────────────────────────────
    async function registrarLey(
        datos: AnalisisLeyCreate,
        archivo?: File | null,
    ): Promise<AnalisisLeyOut | null> {
        const { online } = useSync()

        // Si hay conexion: flujo normal
        if (online.value) {
            try {
                const nuevo = await laboratorioApi.registrarLey(datos)
                if (archivo) await laboratorioApi.subirCertificadoLey(nuevo.id, archivo)
                return nuevo
            } catch (e: any) {
                ui.toast(e?.response?.data?.detail ?? 'Error al registrar analisis de ley', 'error')
                return null
            }
        }

        // Sin conexion: encolar en IndexedDB
        // El certificado NO puede guardarse offline - se avisa al usuario
        if (archivo) {
            ui.toast('Sin conexion: el analisis se guardara pero el certificado no podra adjuntarse hasta reconectar.', 'warning')
        }
        try {
            const offline_id = crypto.randomUUID()
            await encolarAnalisisLey({
                offline_id,
                datos: {
                    cip: datos.cip,
                    laboratorio: datos.laboratorio,
                    tipo_analisis: datos.tipo_analisis,
                    material: datos.material ?? 'Au',
                    ley_fino: datos.ley_fino,
                    ley_grueso: datos.ley_grueso,
                    origen_datos: datos.origen_datos ?? 'manual',
                    fecha_analisis:
                        datos.fecha_analisis ??
                        new Date().toISOString().slice(0, 10),
                },
            })
            ui.toast('Analisis guardado localmente. Se sincronizara al recuperar conexion.', 'info')
            // Retornar objeto optimista para que la UI pueda mostrar algo
            return null
        } catch {
            ui.toast('Error al guardar analisis offline', 'error')
            return null
        }
    }

    // ── Flujo recuperación interna ────────────────────────────────────────────
    // Comercial crea el pending con snapshot de ley_cabeza
    async function enviarRecuperacion(
        ip: string,
        datos: EnviarRecuperacionInternaRequest = {},
    ): Promise<AnalisisRecuperacionOut | null> {
        try {
            const nuevo = await laboratorioApi.enviarRecuperacion(ip, datos)
            ui.toast('Enviado a laboratorio para análisis de recuperación', 'success')
            return nuevo
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al enviar a recuperación', 'error')
            return null
        }
    }

    // Laboratorista completa el pending
    async function completarRecuperacion(
        analisisId: number,
        datos: CompletarRecuperacionRequest,
        archivo?: File | null,
    ): Promise<AnalisisRecuperacionOut | null> {
        try {
            const resultado = await laboratorioApi.completarRecuperacion(analisisId, datos)
            if (archivo) await laboratorioApi.subirCertificadoRecuperacion(resultado.id, archivo)
            return resultado
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al completar recuperación', 'error')
            return null
        }
    }

    // Registro directo COMPLETADO (externo via certificado)
    async function registrarRecuperacion(
        datos: AnalisisRecuperacionCreate,
        archivo?: File | null,
    ): Promise<boolean> {
        try {
            const nuevo = await laboratorioApi.registrarRecuperacion(datos)
            if (archivo) await laboratorioApi.subirCertificadoRecuperacion(nuevo.id, archivo)
            ui.toast('Análisis de recuperación registrado', 'success')
            return true
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al registrar análisis de recuperación', 'error')
            return false
        }
    }

    // ── Descartar ─────────────────────────────────────────────────────────────
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

    // ── Eliminar (soft delete) ─────────────────────────────────────────────────
    async function eliminarLey(analisisId: number): Promise<boolean> {
        const ok = await ui.showConfirm({
            title: 'Eliminar analisis',
            message:
                'Esto ocultara el analisis de todas las vistas. El registro permanece en la base de datos. Esta accion no se puede deshacer desde la interfaz.',
            confirmLabel: 'Eliminar',
            danger: true,
        })
        if (!ok) return false
        try {
            await laboratorioApi.eliminarLey(analisisId)
            ui.toast('Analisis eliminado', 'success')
            return true
        } catch {
            ui.toast('Error al eliminar analisis', 'error')
            return false
        }
    }

    async function eliminarRecuperacion(analisisId: number): Promise<boolean> {
        const ok = await ui.showConfirm({
            title: 'Eliminar analisis',
            message:
                'Esto ocultara el analisis de todas las vistas. El registro permanece en la base de datos. Esta accion no se puede deshacer desde la interfaz.',
            confirmLabel: 'Eliminar',
            danger: true,
        })
        if (!ok) return false
        try {
            await laboratorioApi.eliminarRecuperacion(analisisId)
            ui.toast('Analisis eliminado', 'success')
            return true
        } catch {
            ui.toast('Error al eliminar analisis', 'error')
            return false
        }
    }

    // ── Certificados ──────────────────────────────────────────────────────────
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

    async function generarCertificadoLeyInterno(analisisId: number) {
        try {
            await laboratorioApi.generarCertificadoLeyInterno(analisisId)
            ui.toast('Certificado generado y adjuntado', 'success')
            return true
        } catch {
            ui.toast('Error al generar certificado', 'error')
            return false
        }
    }

    async function generarCertificadoRecInterno(analisisId: number) {
        try {
            await laboratorioApi.generarCertificadoRecInterno(analisisId)
            ui.toast('Certificado generado y adjuntado', 'success')
            return true
        } catch {
            ui.toast('Error al generar certificado', 'error')
            return false
        }
    }

    return {
        cips, lotes, cargando,
        puedeVerIP, esLaboratorista,
        cargarCips, cargarLotes, cargarDetalleLote,
        registrarLey,
        enviarRecuperacion, completarRecuperacion, registrarRecuperacion,
        descartarLey, descartarRecuperacion,
        eliminarLey, eliminarRecuperacion,
        subirCertificadoLey, subirCertificadoRecuperacion,
        puedeImportarCert,
        generarCertificadoLeyInterno, generarCertificadoRecInterno,
    }
})
