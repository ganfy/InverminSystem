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
        // Sin red: solo cargar contadores locales, no intentar requests
        if (!isOnline()) {
            await actualizarContadores()
            return
        }

        try {
            // 1. Reservar bloque IP si el actual está agotado o no existe
            if (await bloqueAgotado()) {
                await renovarBloqueIP()
            }

            // 2. Cachear provacops actualizados
            await actualizarCacheProvacops()

            // 3. Sincronizar pendientes de sesiones anteriores
            await sincronizar()

        } catch (err) {
            // Red disponible pero servidor falló — no bloquear la app
            console.warn('[useSync] Error en inicialización:', err)
            await actualizarContadores()
        }
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

    async function sincronizar(): Promise<void> {
        if (sincronizando.value || !isOnline()) return

        const sesiones = await obtenerSesionesPendientes()
        if (sesiones.length === 0) {
            await actualizarContadores()
            return
        }

        sincronizando.value = true
        errorSync.value = null

        try {
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

            // Renovar bloque si se agotó durante el turno offline
            if (await bloqueAgotado()) await renovarBloqueIP()

        } catch (err: any) {
            errorSync.value = err?.message ?? 'Error de sincronización'
            console.error('[useSync] Error en sync batch:', err)
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

        inicializar,
        sincronizar,
        renovarBloqueIP,
        actualizarContadores,
    }
}
