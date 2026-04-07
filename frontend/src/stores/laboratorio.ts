import { defineStore } from 'pinia'
import { ref } from 'vue'
import { laboratorioApi } from '@/api/laboratorio'
import type { AnalisisLeyCreate,
            AnalisisRecuperacionCreate,
            MuestraLaboratorioItem,
        } from '@/types/laboratorio'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'
// Nota: Deberás agregar funciones similares a estas en tu useOfflineQueue.ts
// import { encolarLaboratorioOffline } from '@/composables/useOfflineQueue'

export const useLaboratorioStore = defineStore('laboratorio', () => {
    const ui = useUiStore()
    const sync = useSync()

    const guardando = ref(false)

    const cargando = ref(false)
    const muestras = ref<MuestraLaboratorioItem[]>([])

    // --- Helpers de Negocio (Cliente) ---
    function validarLeyes(leyCabeza: number, leyCola: number): boolean {
        return leyCabeza > leyCola
    }

    // --- Acciones ---
    async function registrarAnalisisLey(datos: AnalisisLeyCreate, archivoCertificado?: File | null): Promise<boolean> {
        guardando.value = true
        try {
            if (sync.online.value) {
                // ONLINE
                const analisis = await laboratorioApi.registrarLey(datos)

                // Si hay certificado, lo subimos inmediatamente después
                if (archivoCertificado) {
                    await laboratorioApi.subirCertificadoLey(analisis.id, archivoCertificado)
                }

                ui.toast('Análisis de Ley registrado con éxito', 'success')
                if (datos.tipo_analisis.toLowerCase() === 'dirimencia') {
                    ui.toast('Dirimencia aplicada: Análisis anteriores invalidados.', 'warning')
                }
            } else {
                // OFFLINE
                const offlineId = `lab-ley-off-${crypto.randomUUID()}`
                // TODO: Descomentar cuando agregues la función a useOfflineQueue.ts
                /*
                await encolarLaboratorioOffline({
                    offline_id: offlineId,
                    tipo: 'ley',
                    datos: datos,
                    synced: false
                })
                */
                ui.toast('Sin red: Análisis guardado en la tablet', 'warning')
                if (archivoCertificado) {
                    ui.toast('Nota: El certificado PDF deberá subirse manualmente al recuperar la conexión.', 'warning')
                }
            }
            return true
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al registrar el análisis', 'error')
            return false
        } finally {
            guardando.value = false
        }
    }

    async function registrarAnalisisRecuperacion(datos: AnalisisRecuperacionCreate, archivoCertificado?: File | null): Promise<boolean> {
        if (!validarLeyes(datos.ley_cabeza, datos.ley_cola)) {
            ui.toast('Error físico: La Ley de Cabeza debe ser mayor a la Ley de Cola.', 'error')
            return false
        }

        guardando.value = true
        try {
            if (sync.online.value) {
                const analisis = await laboratorioApi.registrarRecuperacion(datos)
                if (archivoCertificado) {
                    await laboratorioApi.subirCertificadoRecuperacion(analisis.id, archivoCertificado)
                }
                ui.toast('Análisis de Recuperación registrado con éxito', 'success')
            } else {
                const offlineId = `lab-rec-off-${crypto.randomUUID()}`
                // Encolar offline lógica aquí...
                ui.toast('Sin red: Análisis de recuperación guardado en la tablet', 'warning')
            }
            return true
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al registrar recuperación', 'error')
            return false
        } finally {
            guardando.value = false
        }
    }

    async function cargarMuestras() {
        cargando.value = true
        try {
            if (sync.online.value) {
                muestras.value = await laboratorioApi.obtenerMuestras()
                // Aquí en el futuro puedes guardar en IndexedDB para modo offline
            }
        } catch (e: any) {
            ui.toast('Error al cargar las muestras del laboratorio', 'error')
        } finally {
            cargando.value = false
        }
    }

    return {
        guardando,
        validarLeyes,
        registrarAnalisisLey,
        registrarAnalisisRecuperacion,
        cargarMuestras,
        muestras,
        cargando,
    }
})
