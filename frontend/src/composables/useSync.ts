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

import { ref, computed, onMounted, onUnmounted, watch, getCurrentInstance } from 'vue'
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
    encolarAnalisisLey,
    obtenerAnalisisLeyPendientes,
    marcarAnalisisLeySynced,
    marcarAnalisisLeyError,
    limpiarAnalisisLeySynced,
    obtenerAnalisisRecuperacionPendientes,
    marcarAnalisisRecuperacionSynced,
    marcarAnalisisRecuperacionError,
    limpiarAnalisisRecuperacionSynced,
    obtenerCipsPendientes,
    marcarCipSynced,
    marcarCipError,
    limpiarCipsSynced,
    obtenerCipsPruebasPendientes,
    marcarCipPruebaSynced,
    marcarCipPruebaError,
    limpiarCipsPruebasSynced,
    obtenerCipsREEPendientes,
    marcarCipREESynced,
    marcarCipREEError,
    limpiarCipsREESynced,
} from '@/composables/useOfflineQueue'
import { laboratorioApi, crearEnsayoREE } from '@/api/laboratorio'
import { muestreoApi } from '@/api/muestreo'
import { pruebasApi } from '@/api/pruebas'
import type {
    SyncLaboratorioRequest,
    AnalisisLeyCreate,
    AnalisisRecuperacionCreate,
    CompletarRecuperacionRequest,
} from '@/types/laboratorio'

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

// Exportado para que stores (ej. balanza.ts) lean el estado centralizado
// sin necesitar contexto de componente Vue
export { online as networkOnline }

// ── Listeners globales de red (nivel módulo, se registran una sola vez) ───
// Se usan los eventos nativos del navegador Y los eventos personalizados de
// Axios (app-network-offline / app-network-online) para cubrir el caso de
// desconexión física de WiFi donde navigator.onLine puede tardar en actualizarse.

function _onOnline() {
    if (FORCE_OFFLINE) return
    online.value = true
    errorSync.value = null
}

function _onOffline() {
    if (FORCE_OFFLINE) return
    online.value = false
}

if (typeof window !== 'undefined') {
    window.addEventListener('online', _onOnline)
    window.addEventListener('offline', _onOffline)
    // Eventos personalizados emitidos por el interceptor de Axios al detectar
    // errores de red reales (cubre desconexión física de WiFi/cable)
    window.addEventListener('app-network-offline', _onOffline as EventListener)
    window.addEventListener('app-network-online', _onOnline as EventListener)
}

// Watcher a nivel de módulo: al recuperar la red dispara sincronización automática.
// Esto garantiza que tanto el cambio de badge como el sync ocurran correctamente
// independientemente del origen de la detección (DevTools, evento nativo, Axios).
watch(online, async (isOnline) => {
    if (isOnline && !FORCE_OFFLINE) {
        errorSync.value = null
        // Pequeño delay para que el servidor termine de establecer la conexión
        await new Promise(r => setTimeout(r, 300))
        await sincronizar()
        await actualizarContadores()
    } else if (!isOnline) {
        await actualizarContadores()
    }
})

// ── Inicialización (llamar al login) ──────────────────────────────

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

// ── Reserva de bloque IP ────────────────────────────────────

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
        // No propagar - si falla, seguimos con el bloque que había en IndexedDB
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

// ── Caché provacops ────────────────────────────────────────────

async function actualizarCacheProvacops(): Promise<void> {
    try {
        const resp = await balanzaApi.obtenerCacheProvacops()
        await guardarProvacops(resp.items)
    } catch (err) {
        console.warn('[useSync] No se pudo actualizar caché de provacops:', err)
    }
}

// ── Sync batch ─────────────────────────────────────────────────

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

async function sincronizarCips(): Promise<void> {
    const pendientes = await obtenerCipsPendientes()
    if (pendientes.length === 0) return

    try {
        const payload = pendientes.map(c => ({
            offline_id: c.offline_id,
            ip: c.ip,
            codigo_cip: c.codigo_cip,
            correlativo: c.correlativo,
            laboratorio: c.laboratorio,
            tipo_muestra: c.tipo_muestra,
        }))

        const resp = await muestreoApi.syncCips(payload)

        for (const resultado of resp.resultados) {
            if (resultado.error) {
                await marcarCipError(resultado.offline_id, resultado.error)
            } else {
                await marcarCipSynced(resultado.offline_id)
            }
        }
        await limpiarCipsSynced()
    } catch (err) {
        console.error('[useSync] Error sincronizando CIPs offline:', err)
    }
}

async function sincronizarCipsPruebas(): Promise<void> {
    const pendientes = await obtenerCipsPruebasPendientes()
    if (pendientes.length === 0) return

    try {
        const payload = pendientes.map(c => ({
            offline_id: c.offline_id,
            ip: c.ip,
            codigo_cip1: c.codigo_cip1,
            codigo_cip2: c.codigo_cip2,
            correlativo1: c.correlativo1,
            correlativo2: c.correlativo2,
            tipo: c.tipo,
        }))

        const resp = await pruebasApi.syncCipsPruebas(payload)

        for (const resultado of resp.resultados) {
            if (resultado.error) {
                await marcarCipPruebaError(resultado.offline_id, resultado.error)
            } else {
                await marcarCipPruebaSynced(resultado.offline_id)
            }
        }
        await limpiarCipsPruebasSynced()
    } catch (err) {
        console.error('[useSync] Error sincronizando CIPs de pruebas:', err)
    }
}

async function sincronizarREE(): Promise<void> {
    const pendientes = await obtenerCipsREEPendientes()
    if (pendientes.length === 0) return

    for (const cip of pendientes) {
        try {
            // El backend es idempotente: si el REE ya existe, devuelve el mismo.
            await crearEnsayoREE(cip.cip_origen)
            await marcarCipREESynced(cip.offline_id)
        } catch (err: any) {
            const msg = err?.response?.data?.detail ?? err?.message ?? 'Error desconocido'
            await marcarCipREEError(cip.offline_id, msg)
            console.error(`[useSync] Error al sincronizar CIP REE ${cip.codigo_ree}:`, msg)
        }
    }
    await limpiarCipsREESynced()
}

async function sincronizarLaboratorio(): Promise<void> {
    const pendientesLey = await obtenerAnalisisLeyPendientes()
    const pendientesRec = await obtenerAnalisisRecuperacionPendientes()
    if (pendientesLey.length === 0 && pendientesRec.length === 0) return

    try {
        const payload: SyncLaboratorioRequest = {
            analisis_ley: pendientesLey.map(p => ({
                offline_id: p.offline_id,
                datos: p.datos,
            })),

            analisis_recuperacion: pendientesRec.map(p => {
                const d = p.datos as any;

                let datosProcesados: AnalisisRecuperacionCreate | CompletarRecuperacionRequest;

                if (p.analisis_id) {
                    datosProcesados = {
                        ley_cola: Number(d.ley_cola),
                        ley_liquido: d.ley_liquido != null ? Number(d.ley_liquido) : null,
                        fecha_analisis: d.fecha_analisis || new Date().toISOString()
                    };
                } else {
                    datosProcesados = {
                        cip: d.cip,
                        laboratorio: d.laboratorio,
                        ley_cabeza: Number(d.ley_cabeza),
                        ley_cola: Number(d.ley_cola),
                        ley_liquido: d.ley_liquido != null ? Number(d.ley_liquido) : null,
                        origen_datos: d.origen_datos || 'manual',
                        fecha_analisis: d.fecha_analisis || new Date().toISOString()
                    };
                }

                return {
                    offline_id: p.offline_id,
                    analisis_id: p.analisis_id ?? null,
                    datos: datosProcesados
                };
            }),
        }

        const resp = await laboratorioApi.syncLaboratorio(payload)

        for (const resultado of resp.resultados_ley) {
            if (resultado.error) {
                await marcarAnalisisLeyError(resultado.offline_id, resultado.error)
            } else {
                await marcarAnalisisLeySynced(resultado.offline_id)
            }
        }
        await limpiarAnalisisLeySynced()

        for (const resultado of resp.resultados_recuperacion ?? []) {
            if (resultado.error) {
                await marcarAnalisisRecuperacionError(resultado.offline_id, resultado.error)
            } else {
                await marcarAnalisisRecuperacionSynced(resultado.offline_id)
            }
        }
        await limpiarAnalisisRecuperacionSynced()
    } catch (err) {
        console.error('[useSync] Error sincronizando analisis de laboratorio:', err)
    }
}

async function sincronizar(): Promise<void> {
    if (sincronizando.value || !isOnline()) return

    sincronizando.value = true
    errorSync.value = null

    try {
        const sesionesConLotesNuevos = await sincronizarLotesOnline()
        if (sesionesConLotesNuevos.length > 0) {
            const ultima = sesionesConLotesNuevos[sesionesConLotesNuevos.length - 1]
            if (ultima !== undefined) sesionRecargada.value = ultima
        }
        await limpiarLotesOnlineSynced()

        const sesiones = await obtenerSesionesPendientes()
        if (sesiones.length > 0) {
            const resp = await balanzaApi.syncBatch({ sesiones })

            const sesionesPostSync = await obtenerSesionesPendientes()
            const ui = useUiStore()

            for (const resultado of resp.resultados) {
                if (resultado.error) {
                    if (resultado.error.includes('ERR_IP_COLLISION')) {
                        const match = resultado.error.match(/ERR_IP_COLLISION\|([A-Z0-9-]+)/)
                        const ipEnConflicto = match ? match[1] : 'Desconocido'

                        const ok = await ui.showConfirm({
                            title: 'Cruce de Tickets Detectado',
                            message: `El ticket ${ipEnConflicto} ya se encuentra registrado en otra sesión (usualmente por cruce de caché).\n\n¿Deseas asignarle un nuevo número correlativo automáticamente para no perder los datos del pesaje? (Ten en cuenta que el ticket físico conservará el número antiguo).`,
                            confirmLabel: 'Sí, reasignar IP',
                        })

                        if (ok) {
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

                                        setTimeout(sincronizar, 2000)
                                        continue
                                    }
                                } else {
                                    ui.toast('No hay IPs disponibles para reasignar. Conéctate para renovar el bloque.', 'error')
                                }
                            }
                        }

                        await marcarSesionError(resultado.offline_id, `Cruce de IP: ${ipEnConflicto}. Requiere arreglo manual.`)
                    } else {
                        await marcarSesionError(resultado.offline_id, resultado.error)
                    }
                } else {
                    const enviada = sesiones.find(s => s.offline_id === resultado.offline_id)
                    const actualLocal = sesionesPostSync.find(s => s.offline_id === resultado.offline_id)

                    if (enviada && actualLocal) {
                        if (actualLocal.lotes.length > enviada.lotes.length || actualLocal.estado !== enviada.estado) {
                            console.warn(`[useSync] Sesión ${resultado.offline_id} modificada durante sync. Reteniendo para próximo ciclo.`)
                            continue
                        }
                    }

                    await marcarSesionSynced(resultado.offline_id, resultado.server_id!)
                    sesionOfflineSincronizada.value = {
                        offline_id: resultado.offline_id,
                        server_id: resultado.server_id!
                    }
                }
            }
            await limpiarSynced()
        }

        await sincronizarFinalizaciones()
        await sincronizarMuestreos()
        await sincronizarPruebas()
        await sincronizarCips()
        await sincronizarCipsPruebas()
        await sincronizarREE()            // CIPs REE antes que análisis de ley
        await sincronizarLaboratorio()

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

// ── Composable ─────────────────────────────────────────────

export function useSync() {

    if (getCurrentInstance()) {
        onMounted(() => {
            if (!FORCE_OFFLINE) {
                online.value = navigator.onLine
            }
            actualizarContadores()
            if (online.value) {
                sincronizar()
            }
        })
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
