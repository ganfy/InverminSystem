import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { muestreoApi, type LoteMuestreo, type MapeoCIPOut, type MuestreoCreate } from '@/api/muestreo'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'
import { generateUUID } from '@/utils/uuid'
import { generarCodigoCip, laboratorioParaCip } from '@/utils/cipGenerator'
import {
    encolarMuestreoOffline,
    obtenerMuestreosPendientes,
    guardarLotesMuestreoCache,
    obtenerLotesMuestreoCache,
    encolarCipOffline,
    obtenerCipsPorLote,
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
                const offlineId = `muestreo-off-${generateUUID()}`

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
     * Registra múltiples ensayos de humedad simultáneamente
     */
    async function registrarHumedadBatch(ipLote: string, datosList: MuestreoCreate[]): Promise<boolean> {
        // Validación de reglas de negocio para todos
        for (const datos of datosList) {
            const humedad = calcularHumedad(datos.peso_humedo, datos.peso_seco)
            if (!validarHumedad(humedad)) {
                ui.toast(`Humedad fuera de rango (${humedad}%) en el intento ${datos.intento}.`, 'error')
                return false
            }
        }

        guardando.value = true
        try {
            const fechaAhora = new Date().toISOString()

            if (sync.online.value) {
                // ONLINE: Mandar directo al backend
                await muestreoApi.registrarMuestreoBatch(ipLote, datosList)
                ui.toast(`Se guardaron ${datosList.length} intentos en el servidor`, 'success')
            } else {
                // OFFLINE: Guardar en IndexedDB
                for (const datos of datosList) {
                    const offlineId = `muestreo-off-${generateUUID()}`
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
                }
                ui.toast(`Sin red: ${datosList.length} intentos guardados en la tablet`, 'warning')
            }

            // 1. Buscar el lote en memoria
            const idxPendiente = lotesPendientes.value.findIndex(l => l.ip === ipLote)
            let loteActualizado: LoteMuestreo | null = null
            
            const maxIntento = Math.max(...datosList.map(d => d.intento))

            if (idxPendiente !== -1) {
                // Estaba pendiente, lo movemos a completados
                const lote = lotesPendientes.value[idxPendiente]
                if (lote) {
                    loteActualizado = lote
                    loteActualizado.estado_muestreo = 'COMPLETADO'
                    loteActualizado.fecha_muestreo = fechaAhora
                    loteActualizado.cantidad_intentos_previos = maxIntento
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
                        loteActualizado.cantidad_intentos_previos = maxIntento
                    }
                }
            }

            // 2. Persistir este nuevo estado en IndexedDB
            if (loteActualizado) {
                const lotesLimpios = JSON.parse(JSON.stringify([...lotesPendientes.value, ...lotesCompletados.value]))
                await guardarLotesMuestreoCache(lotesLimpios)
            }

            return true

        } catch (e: any) {
            ui.toast(e?.response?.data?.detail ?? 'Error al registrar múltiples humedades', 'error')
            return false
        } finally {
            guardando.value = false
        }
    }

    /**
     * Genera los códigos de barras CIP para el laboratorio.
     * - ONLINE: los solicita al servidor (comportamiento original).
     * - OFFLINE: los genera localmente con el mismo algoritmo que el backend
     *            y los encola en IndexedDB para sync posterior.
     *
     * Requiere que el lote esté en cache (lote_id disponible).
     * Si el lote no está en cache y se está offline, bloquea con mensaje claro.
     */
    async function generarCodigosCip(ipLote: string, cantidadBolsas: number = 2): Promise<any[] | null> {
        const todosLotes = [...lotesPendientes.value, ...lotesCompletados.value]
        const lote = todosLotes.find(l => l.ip === ipLote)

        if (!sync.online.value) {
            // Offline: necesitamos lote_id para el algoritmo
            if (!lote?.lote_id) {
                ui.toast(
                    'Sin conexión y sin datos del lote en cache. Carga la lista una vez con red para poder etiquetar offline.',
                    'error'
                )
                return null
            }

            guardando.value = true
            try {
                // Cuántos CIPs ya existen para este lote en la cola offline
                const cipsExistentes = await obtenerCipsPorLote(ipLote)
                const resultados: any[] = []

                for (let i = 0; i < cantidadBolsas; i++) {
                    const correlativo = cipsExistentes.length + i + 1
                    const codigo = generarCodigoCip(lote.lote_id, correlativo)
                    const laboratorio = laboratorioParaCip(correlativo)

                    await encolarCipOffline({
                        offline_id: `cip-off-${generateUUID()}`,
                        ip: ipLote,
                        lote_id: lote.lote_id,
                        codigo_cip: codigo,
                        correlativo,
                        laboratorio,
                        tipo_muestra: 'Laboratorio',
                        synced: false,
                        sync_error: null,
                    })

                    resultados.push({
                        id: -(correlativo),           // ID negativo = generado offline
                        lote_id: lote.lote_id,
                        codigo_cip: codigo,
                        laboratorio,
                        tipo_muestra: 'Laboratorio',
                        tiene_analisis_ley: false,
                        tiene_analisis_recuperacion: false,
                    })
                }

                // Actualizar lote.etiquetado en memoria para que el UI refleje el cambio
                lote.etiquetado = true
                // Guardar lotes actualizados en cache
                const lotesLimpios = JSON.parse(JSON.stringify([...lotesPendientes.value, ...lotesCompletados.value]))
                await guardarLotesMuestreoCache(lotesLimpios)

                ui.toast(
                    `Sin red: ${cantidadBolsas} CIP(s) generados localmente. Se registrarán al reconectar.`,
                    'warning'
                )
                return resultados

            } catch (e: any) {
                ui.toast(e?.message ?? 'Error al generar CIPs offline', 'error')
                return null
            } finally {
                guardando.value = false
            }
        }

        // ONLINE: generar en el servidor (comportamiento original)
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
        registrarHumedadBatch,
        generarCodigosCip,
        calcularProximoIntento,
        cargarLotes,
        obtenerCodigosCip
    }
})
