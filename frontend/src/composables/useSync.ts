/**
 * useSync.ts
 * ===========
 * Manager de sincronización offline→online para el módulo Balanza.
 *
 * Responsabilidades:
 *   1. Al login: reservar bloque IP + cachear provacops.
 *   2. Detectar cambio online/offline y actualizar indicador global.
 *   3. Al recuperar red: disparar sync automático sin intervención del usuario.
 *   4. Exponer estado de sync para mostrar en UI.
 *
 * Para testear offline en desarrollo, agregar en .env.local:
 *   VITE_FORCE_OFFLINE=true
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { balanzaApi } from '@/api/balanza'
import {
    guardarBloqueIP,
    guardarProvacops,
    obtenerSesionesPendientes,
    marcarSesionSynced,
    marcarSesionError,
    limpiarSynced,
    contarPendientes,
    bloqueAgotado,
    ipsDisponibles,
    guardarBloqueTK,
    bloqueTKAgotado,
    encolarLoteOnline,
    obtenerFinalizacionesPendientes,
    eliminarFinalizacion,
    obtenerLotesOnlinePendientes,
    marcarLoteOnlineError,
    marcarLoteOnlineSynced,
    limpiarLotesOnlineSynced,
    type LoteOnlineData,
} from '@/composables/useOfflineQueue'

// ── Modo offline forzado (solo desarrollo) ─────────────────
const FORCE_OFFLINE = import.meta.env.VITE_FORCE_OFFLINE === 'true'
const isOnline = () => !FORCE_OFFLINE && navigator.onLine

if (FORCE_OFFLINE) {
    console.warn('[useSync] MODO OFFLINE FORZADO activo (VITE_FORCE_OFFLINE=true)')
}

// ── Estado global singleton ────────────────────────────────
// Los refs viven fuera de la función para compartirse entre
// todos los componentes que llamen useSync()

const online = ref<boolean>(isOnline())
const sincronizando = ref<boolean>(false)
const pendientes = ref<number>(0)
const ultimoSync = ref<string | null>(null)
const errorSync = ref<string | null>(null)
const ipsRestantes = ref<number>(0)
const sesionRecargada = ref<number | null>(null) // ID de sesión que se recargó desde otra pestaña (para evitar recargas infinitas)

// ── Composable ─────────────────────────────────────────────

export function useSync() {

    // ── Listeners de conectividad ────────────────────────────

    function onOnline() {
        if (FORCE_OFFLINE) return
        online.value = true
        errorSync.value = null
        sincronizar()
    }

    function onOffline() {
        if (FORCE_OFFLINE) return
        online.value = false
        actualizarContadores()
    }

    onMounted(() => {
        window.addEventListener('online', onOnline)
        window.addEventListener('offline', onOffline)
        actualizarContadores()
    })

    onUnmounted(() => {
        window.removeEventListener('online', onOnline)
        window.removeEventListener('offline', onOffline)
    })

    // ── Inicialización (llamar al login) ─────────────────────

    async function inicializar(): Promise<void> {
        if (!isOnline()) {
            await actualizarContadores()
            return
        }

        try {
            if (await bloqueAgotado()) await renovarBloqueIP()
        } catch (err) {
            console.warn('[useSync] No se pudo renovar bloque IP:', err)
        }

        try {
            if (await bloqueTKAgotado()) await renovarBloqueTK()
        } catch (err) {
            console.warn('[useSync] No se pudo renovar bloque TK:', err)
        }

        try {
            await actualizarCacheProvacops()
        } catch (err) {
            console.warn('[useSync] No se pudo actualizar caché provacops:', err)
        }

        await sincronizar()
    }

    // ── Reserva de bloque IP ─────────────────────────────────

    async function renovarBloqueIP(): Promise<void> {
        try {
            const bloque = await balanzaApi.reservarBloqueIP()
            await guardarBloqueIP({
                desde: bloque.desde,
                hasta: bloque.hasta,
                anio: bloque.anio,
            })
            ipsRestantes.value = bloque.tamano
        } catch (err) {
            // No propagar — si falla, seguimos con el bloque que había en IndexedDB
            console.warn('[useSync] No se pudo reservar bloque IP:', err)
        }
    }

    async function renovarBloqueTK(): Promise<void> {
        try {
            const bloque = await balanzaApi.reservarBloqueTK()
            await guardarBloqueTK({ desde: bloque.desde, hasta: bloque.hasta })
        } catch (err) {
            console.warn('[useSync] No se pudo reservar bloque TK:', err)
        }
    }

    // ── Caché provacops ──────────────────────────────────────

    async function actualizarCacheProvacops(): Promise<void> {
        try {
            const resp = await balanzaApi.obtenerCacheProvacops()
            await guardarProvacops(resp.items)
        } catch (err) {
            console.warn('[useSync] No se pudo actualizar caché de provacops:', err)
        }
    }

    // ── Sync batch ───────────────────────────────────────────

    /**
 * Sincroniza lotes de sesiones online creados mientras no había conexión.
 * Retorna los IDs de sesión que recibieron lotes nuevos.
 */
    async function sincronizarLotesOnline(): Promise<number[]> {
        const pendientes = await obtenerLotesOnlinePendientes()
        if (pendientes.length === 0) return []

        // Agrupar por sesion_id
        const porSesion = new Map<number, LoteOnlineData[]>()
        for (const lote of pendientes) {
            const grupo = porSesion.get(lote.sesion_id) ?? []
            grupo.push(lote)
            porSesion.set(lote.sesion_id, grupo)
        }

        const sesionesActualizadas: number[] = []

        for (const [sesionId, lotes] of porSesion) {
            // Ordenar por numero_lote para preservar secuencia
            lotes.sort((a, b) => a.numero_lote - b.numero_lote)

            let algunoOk = false
            for (const lote of lotes) {
                try {
                    await balanzaApi.agregarLote(sesionId, {
                        tipo_material: lote.tipo_material,
                        pesaje: {
                            peso_inicial: lote.pesaje.peso_inicial,
                            peso_final: lote.pesaje.peso_final,
                            sacos: lote.pesaje.sacos,
                            granel: lote.pesaje.granel,
                            fecha_inicio: lote.pesaje.fecha_inicio ?? undefined,
                        },
                    })
                    await marcarLoteOnlineSynced(lote.offline_id)
                    algunoOk = true
                } catch (err: any) {
                    const msg = err?.response?.data?.detail ?? err?.message ?? 'Error desconocido'
                    await marcarLoteOnlineError(lote.offline_id, msg)
                    console.error(`[useSync] Error al sincronizar lote ${lote.offline_id}:`, msg)
                }
            }

            if (algunoOk) sesionesActualizadas.push(sesionId)
        }

        await limpiarLotesOnlineSynced()
        return sesionesActualizadas
    }

    async function sincronizarFinalizaciones(): Promise<void> {
        const pendientes = await obtenerFinalizacionesPendientes()
        for (const fin of pendientes) {
            try {
                await balanzaApi.finalizarSesion(fin.sesion_id)
                await eliminarFinalizacion(fin.sesion_id)
            } catch (err: any) {
                // Si ya estaba finalizada, limpiar igual
                const detail = err?.response?.data?.detail ?? ''
                if (detail.includes('ya está completada')) {
                    await eliminarFinalizacion(fin.sesion_id)
                } else {
                    console.error(`[useSync] Error al finalizar sesión ${fin.sesion_id}:`, detail)
                }
            }
        }
      }

    async function sincronizar(): Promise<void> {
        if (sincronizando.value || !isOnline()) return

        sincronizando.value = true
        errorSync.value = null

        try {
            // 1. Primero: lotes de sesiones online creados offline (híbrido)
            const sesionesConLotesNuevos = await sincronizarLotesOnline()
            if (sesionesConLotesNuevos.length > 0) {
                // Notificar a SesionView para auto-reload (última sesión actualizada)
                const ultimaSesion = sesionesConLotesNuevos[sesionesConLotesNuevos.length - 1]
                if (ultimaSesion !== undefined) {
                    sesionRecargada.value = ultimaSesion
                }
            }

            // 2. Luego: sesiones creadas completamente offline
            const sesiones = await obtenerSesionesPendientes()
            if (sesiones.length > 0) {
                const resp = await balanzaApi.syncBatch({ sesiones })
                for (const resultado of resp.resultados) {
                    if (resultado.error) {
                        await marcarSesionError(resultado.offline_id, resultado.error)
                    } else {
                        await marcarSesionSynced(resultado.offline_id, resultado.server_id!)
                    }
                }
                await limpiarSynced()
                ultimoSync.value = new Date().toLocaleString('es-PE')
            }

            await sincronizarFinalizaciones()
            if (await bloqueAgotado()) await renovarBloqueIP()

        } catch (err: any) {
            errorSync.value = err?.message ?? 'Error de sincronización'
            console.error('[useSync] Error en sync:', err)
        } finally {
            sincronizando.value = false
            await actualizarContadores()
        }
    }

    async function actualizarContadores(): Promise<void> {
        pendientes.value = await contarPendientes()
        ipsRestantes.value = await ipsDisponibles()
    }

    // ── Exponer ──────────────────────────────────────────────

    return {
        online: computed(() => online.value),
        sincronizando: computed(() => sincronizando.value),
        pendientes: computed(() => pendientes.value),
        ultimoSync: computed(() => ultimoSync.value),
        errorSync: computed(() => errorSync.value),
        ipsRestantes: computed(() => ipsRestantes.value),
        sesionRecargada: computed(() => sesionRecargada.value),

        inicializar,
        sincronizar,
        renovarBloqueIP,
        actualizarContadores,
        limpiarSesionRecargada: () => { sesionRecargada.value = null },
    }
}
