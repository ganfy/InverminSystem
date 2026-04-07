import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { muestreoApi, type LoteMuestreo, type MapeoCIPOut, type MuestreoCreate } from '@/api/muestreo'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'
import {
    encolarMuestreoOffline,
    obtenerMuestreosPendientes ,
    guardarLotesMuestreoCache,
    obtenerLotesMuestreoCache,
} from '@/composables/useOfflineQueue'

export const useMuestreoStore = defineStore('muestreo', () => {
    const ui = useUiStore()
    const sync = useSync()

    // --- Estado ---
    const guardando = ref(false)
    const cargando = ref(false)

    // Aquí guardaremos los lotes que bajen del servidor
    const lotesPendientes = ref<LoteMuestreo[]>([])
    const lotesCompletados = ref<LoteMuestreo[]>([])

    // --- Helpers Matemáticos (Se ejecutan en el cliente para UI rápida) ---

    function calcularHumedad(pesoHumedo: number, pesoSeco: number): number {
        if (!pesoHumedo || pesoHumedo <= 0) return 0
        return Number((((pesoHumedo - pesoSeco) / pesoHumedo) * 100).toFixed(2))
    }

    function validarHumedad(porcentaje: number): boolean {
        return porcentaje > 0 && porcentaje <= 50
    }

    // --- Acciones Principales ---

    /**
     * Registra un intento de humedad. Inteligente: sabe si está online u offline.
     */
    async function registrarHumedad(ipLote: string, datos: MuestreoCreate): Promise<boolean> {
        // 1. Validaciones previas en el cliente
        if (datos.peso_seco >= datos.peso_humedo) {
            ui.toast('El peso seco debe ser menor al húmedo.', 'error')
            return false
        }

        const humedad = calcularHumedad(datos.peso_humedo, datos.peso_seco)
        if (!validarHumedad(humedad)) {
            ui.toast(`Humedad fuera de rango (${humedad}%). Repita el muestreo.`, 'error')
            return false
        }

        guardando.value = true
        try {
            const fechaAhora = new Date().toISOString()

            if (sync.online.value) {
                // ONLINE: Mandar directo al backend
                await muestreoApi.registrarMuestreo(ipLote, datos)
                ui.toast(`Intento ${datos.intento} guardado en el servidor`, 'success')
            } else {
                // OFFLINE: Guardar en IndexedDB
                const offlineId = `muestreo-off-${crypto.randomUUID()}`

                await encolarMuestreoOffline({
                    offline_id: offlineId,
                    ip: ipLote,
                    datos: {
                        ...datos,
                        fecha_muestreo: fechaAhora,
                        observaciones: datos.observaciones ?? null
                    },
                    synced: false,
                    sync_error: null
                })
                ui.toast(`Sin red: Intento ${datos.intento} guardado en la tablet`, 'warning')
            }

            // 1. Buscar el lote en memoria
            const idxPendiente = lotesPendientes.value.findIndex(l => l.ip === ipLote)
            let loteActualizado: LoteMuestreo | null = null

            if (idxPendiente !== -1) {
                // Estaba pendiente, lo movemos a completados
                const lote = lotesPendientes.value[idxPendiente]
                if (lote) {
                    loteActualizado = lote
                    loteActualizado.estado_muestreo = 'COMPLETADO'
                    loteActualizado.fecha_muestreo = fechaAhora
                    loteActualizado.cantidad_intentos_previos = datos.intento
                    lotesPendientes.value.splice(idxPendiente, 1)
                    lotesCompletados.value.unshift(loteActualizado)
                }
            } else {
                // Ya estaba en completados (remuestreo)
                const idxCompletado = lotesCompletados.value.findIndex(l => l.ip === ipLote)
                if (idxCompletado !== -1) {
                    const lote = lotesCompletados.value[idxCompletado]
                    if (lote) {
                        loteActualizado = lote
                        loteActualizado.fecha_muestreo = fechaAhora
                        loteActualizado.cantidad_intentos_previos = datos.intento
                    }
                }
            }

            // 2. Persistir este nuevo estado en IndexedDB para la navegación
            if (loteActualizado) {
                const lotesLimpios = JSON.parse(JSON.stringify([...lotesPendientes.value, ...lotesCompletados.value]))
                await guardarLotesMuestreoCache(lotesLimpios)
            }

            return true

        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al registrar humedad', 'error')
            return false
        } finally {
            guardando.value = false
        }
    }

    /**
     * Genera los códigos de barras CIP para el laboratorio.
     * Por seguridad, esto SOLO se puede hacer con conexión a internet.
     */
    async function generarCodigosCip(ipLote: string, cantidadBolsas: number = 2): Promise<any[] | null> {
        if (!sync.online.value) {
            ui.toast('Necesitas conexión a internet para generar los códigos confidenciales CIP.', 'error')
            return null
        }

        guardando.value = true
        try {
            const cips = await muestreoApi.generarCips(ipLote, cantidadBolsas)
            ui.toast('Códigos CIP generados con éxito', 'success')
            return cips
        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al generar códigos CIP', 'error')
            return null
        } finally {
            guardando.value = false
        }
    }

    /**
     * Obtiene los códigos CIP generados para un lote específico.
     */
    async function obtenerCodigosCip(ipLote: string): Promise<MapeoCIPOut[] | null> {
        try {
            return await muestreoApi.obtenerEtiquetas(ipLote)
        } catch (e: any) {
            console.error(e)
            return null
        }
    }

    // Recuerda exportar `obtenerCodigosCip` en el return final del store.

    /**
     * Calcula qué número de intento le toca a un lote de forma segura.
     */
    async function calcularProximoIntento(ipLote: string): Promise<number> {
        const lote = lotesPendientes.value.find(l => l.ip === ipLote) ||
            lotesCompletados.value.find(l => l.ip === ipLote)

        return (lote?.cantidad_intentos_previos || 0) + 1
    }

    /**
     * Carga los lotes. Estrategia Offline-First.
     */
    async function cargarLotes() {
        cargando.value = true
        try {
            if (sync.online.value) {
                // 1. ONLINE: Descargamos la verdad absoluta del servidor
                const lotesServer = await muestreoApi.obtenerLotes()
                // 2. Guardamos en la tablet para cuando se vaya el internet
                await guardarLotesMuestreoCache(lotesServer)
            }
        } catch (error) {
            console.warn('No se pudo actualizar lotes del servidor. Usando caché local.', error)
        } finally {
            // 3. SIEMPRE leemos de IndexedDB para pintar la UI (Garantiza consistencia)
            const lotesLocal = await obtenerLotesMuestreoCache()

            // Separar en las dos listas
            lotesPendientes.value = lotesLocal.filter(l => l.estado_muestreo === 'PENDIENTE')
            lotesCompletados.value = lotesLocal.filter(l => l.estado_muestreo === 'COMPLETADO')

            cargando.value = false
        }
    }

    return {
        // Estado
        guardando,
        cargando,
        lotesPendientes,
        lotesCompletados,
        // Métodos
        calcularHumedad,
        registrarHumedad,
        generarCodigosCip,
        calcularProximoIntento,
        cargarLotes,
        obtenerCodigosCip
    }
})
