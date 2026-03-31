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
import { useUiStore } from '@/stores/ui'
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
    obtenerMuestreosPendientes,
    marcarMuestreoError,
    marcarMuestreoSynced,
    limpiarMuestreosSynced,
    obtenerPruebasPendientes,
    marcarPruebaError,
    marcarPruebaSynced,
    limpiarPruebasSynced,
    type LoteOnlineData,
    siguienteIP,
    encolarSesion,
} from '@/composables/useOfflineQueue'
import { muestreoApi } from '@/api/muestreo'
import { pruebasApi } from '@/api/pruebas'

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
const sesionOfflineSincronizada = ref<{ offline_id: string, server_id: number } | null>(null)

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
        if (!FORCE_OFFLINE) {
            online.value = navigator.onLine
        }
        window.addEventListener('online', onOnline)
        window.addEventListener('offline', onOffline)
        actualizarContadores()
        if (online.value) {
            sincronizar()
        }
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

    async function sincronizarMuestreos(): Promise<void> {
        const pendientes = await obtenerMuestreosPendientes()
        if (pendientes.length === 0) return

        try {
            const resp = await muestreoApi.syncBatch(pendientes)

            for (const resultado of resp.resultados) {
                if (resultado.error) {
                    await marcarMuestreoError(resultado.offline_id, resultado.error)
                    // Podríamos lanzar un toast aquí si queremos avisar al usuario
                } else {
                    await marcarMuestreoSynced(resultado.offline_id)
                }
            }
            await limpiarMuestreosSynced()
        } catch (err) {
            console.error('[useSync] Error sincronizando muestreos:', err)
        }
    }

    async function sincronizarPruebas(): Promise<void> {
        const pendientes = await obtenerPruebasPendientes()
        if (pendientes.length === 0) return

        try {
            const payloadLimpio = pendientes.map(p => {
                const d = p.datos;
                const parseNum = (val: any) => (val === '' || val === null || val === undefined) ? null : Number(val);

                return {
                    offline_id: p.offline_id,
                    ip: p.ip,
                    datos: {
                        malla_porcentaje: parseNum(d.malla_porcentaje),
                        porcentaje_nacn: parseNum(d.porcentaje_nacn),
                        ph_inicial: parseNum(d.ph_inicial),
                        ph_final: parseNum(d.ph_final),
                        adicion_nacn: parseNum(d.adicion_nacn),
                        adicion_naoh: parseNum(d.adicion_naoh),
                        gasto_agno3: parseNum(d.gasto_agno3),
                        fecha_ingreso: d.fecha_ingreso || new Date().toISOString()
                    }
                }
            })

            const resp = await pruebasApi.syncBatch(payloadLimpio)

            for (const resultado of resp.resultados) {
                if (resultado.error) {
                    await marcarPruebaError(resultado.offline_id, resultado.error)
                } else {
                    await marcarPruebaSynced(resultado.offline_id)
                }
            }
            await limpiarPruebasSynced()
        } catch (err) {
            console.error('[useSync] Error sincronizando pruebas metalúrgicas:', err)
        }
    }

    async function sincronizar(): Promise<void> {
        if (sincronizando.value || !isOnline()) return

        sincronizando.value = true
        errorSync.value = null

        // En sincronizar(), reemplazar el bloque completo del try:
        try {
            let sincronizado = false

            // 1. lotes híbridos
            const sesionesConLotesNuevos = await sincronizarLotesOnline()
            if (sesionesConLotesNuevos.length > 0) {
                sincronizado = true
                const ultima = sesionesConLotesNuevos[sesionesConLotesNuevos.length - 1]
                if (ultima !== undefined) sesionRecargada.value = ultima
            }
            await limpiarLotesOnlineSynced()

            // 2. sesiones offline
            const sesiones = await obtenerSesionesPendientes()
            if (sesiones.length > 0) {
                sincronizado = true
                const resp = await balanzaApi.syncBatch({ sesiones })

                const sesionesPostSync = await obtenerSesionesPendientes()
                const ui = useUiStore()

                for (const resultado of resp.resultados) {
                    if (resultado.error) {
                        // DETECCIÓN DE COLISIÓN DE IP
                        if (resultado.error.includes('ERR_IP_COLLISION')) {
                            const match = resultado.error.match(/ERR_IP_COLLISION\|([A-Z0-9-]+)/)
                            const ipEnConflicto = match ? match[1] : 'Desconocido'

                            // Mostrar alerta bloqueante para el usuario
                            const ok = await ui.showConfirm({
                                title: 'Cruce de Tickets Detectado',
                                message: `El ticket ${ipEnConflicto} ya se encuentra registrado en otra sesión (usualmente por cruce de caché).\n\n¿Deseas asignarle un nuevo número correlativo automáticamente para no perder los datos del pesaje? (Ten en cuenta que el ticket físico conservará el número antiguo).`,
                                confirmLabel: 'Sí, reasignar IP',
                            })

                            if (ok) {
                                // Reparar usando memoria local
                                const sesionLocal = sesionesPostSync.find(s => s.offline_id === resultado.offline_id)
                                if (sesionLocal) {
                                    const ipsConocidos = sesionLocal.lotes
                                        .map(l => l.ip)
                                        .filter(Boolean) as string[]

                                    const nuevoIp = await siguienteIP(ipsConocidos)
                                    if (nuevoIp) {
                                        const loteConflicto = sesionLocal.lotes.find(l => l.ip === ipEnConflicto)
                                        if (loteConflicto) {
                                            loteConflicto.ip = nuevoIp
                                            await encolarSesion(sesionLocal)
                                            ui.toast(`Se reasignó a ${nuevoIp}. Reintentando sincronización en segundo plano...`, 'info')

                                            // Programar reintento automático
                                            setTimeout(sincronizar, 2000)
                                            continue // Evita marcar la sesión con error final
                                        }
                                    } else {
                                        ui.toast('No hay IPs disponibles para reasignar. Conéctate para renovar el bloque.', 'error')
                                    }
                                }
                            }

                            // Si hizo clic en "NO" o falló la reasignación, dejamos el error
                            await marcarSesionError(resultado.offline_id, `Cruce de IP: ${ipEnConflicto}. Requiere arreglo manual.`)
                        } else {
                            await marcarSesionError(resultado.offline_id, resultado.error)
                        }
                    } else {
                        const enviada = sesiones.find(s => s.offline_id === resultado.offline_id)
                        const actualLocal = sesionesPostSync.find(s => s.offline_id === resultado.offline_id)

                        // Si la sesión local fue modificada durante el sync (se agregó un lote o cambió el estado), no marcar como sincronizada para evitar perder esos cambios. Se reintentará en el próximo ciclo de sync.
                        if (enviada && actualLocal) {
                            if (actualLocal.lotes.length > enviada.lotes.length || actualLocal.estado !== enviada.estado) {
                                console.warn(`[useSync] Sesión ${resultado.offline_id} modificada durante sync. Reteniendo para próximo ciclo.`)
                                continue
                            }
                        }

                        await marcarSesionSynced(resultado.offline_id, resultado.server_id!)
                        // Disparar evento para que la vista redirija al nuevo ID
                        sesionOfflineSincronizada.value = {
                            offline_id: resultado.offline_id,
                            server_id: resultado.server_id!
                        }
                    }
                }
                await limpiarSynced()
            }

            // 3. finalizaciones híbridas
            await sincronizarFinalizaciones()

            // 4. muestreos offline
            await sincronizarMuestreos()

            // 5. pruebas metalúrgicas offline
            await sincronizarPruebas()

            // Siempre marcar timestamp — es la señal de "sync completó" para los watchers
            ultimoSync.value = new Date().toLocaleString('es-PE')

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
        sesionOfflineSincronizada: computed(() => sesionOfflineSincronizada.value),
        inicializar,
        sincronizar,
        renovarBloqueIP,
        actualizarContadores,
        limpiarSesionRecargada: () => { sesionRecargada.value = null },
        limpiarSesionOfflineSincronizada: () => { sesionOfflineSincronizada.value = null },
    }
}
