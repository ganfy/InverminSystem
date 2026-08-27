/**
 * useOfflineQueue.ts
 * ==================
 * Gestiona el almacenamiento local offline usando IndexedDB.
 *
 * Stores:
 *   - ip_block      → bloque de IPs reservado { desde, hasta, usado, anio }
 *   - provacops     → caché de relaciones proveedor-acopiador
 *   - sesiones_q    → sesiones pendientes de sync
 *   - lotes_q       → lotes pendientes de sync (agrupados por sesion offline_id)
 *
 * Garantías:
 *   - Un registro offline no se elimina hasta confirmar sync exitoso.
 *   - Re-enviar el mismo batch es seguro (offline_id como clave de idempotencia).
 */

import { ref } from 'vue'
import type { SesionLista, SesionDetalle } from '@/api/balanza'
import type { LoteMuestreo } from '@/api/muestreo'
import type { TipoAnalisis, OrigenDatos } from '@/types/laboratorio'

const DB_NAME = 'invermin_offline'
const DB_VERSION = 14

// ── Tipos ──────────────────────────────────────────────────

export interface IPBlock {
    desde: number
    hasta: number
    usado: number       // cuántos IPs del bloque ya se usaron
    anio: number
    reservado_en: string
}

export interface TKBlock {
    id: 'tk'          // clave fija - un solo registro
    desde: number
    hasta: number
    usado: number
    reservado_en: string
}

export interface ProvAcopCacheItem {
    provacop_id: number
    proveedor_id: number
    proveedor_razon_social: string
    proveedor_ruc: string
    acopiador_id: number
    acopiador_razon_social: string
    acopiador_ruc: string
    es_propio: boolean
}

export interface PesajeOfflineData {
    peso_inicial: number
    peso_final: number
    sacos: number | null
    granel: boolean
    fecha_inicio: string | null
    fecha_fin: string | null
    es_manual: boolean;
    justificacion_manual: string | null;
}

export interface LoteOfflineData {
    offline_id: string      // UUID local
    ip: string              // IP del bloque reservado
    numero_lote: number
    tipo_material: string
    observaciones: string | null  // Solo para tipo 'Otro'
    pesaje: PesajeOfflineData
    creado_en: string
    numero_ticket: string
}

export interface SesionOfflineData {
    offline_id: string      // UUID local, clave primaria en IndexedDB
    provacop_id: number
    placa: string
    carreta: string | null
    conductor: string | null
    transportista: string | null
    razon_social: string | null
    guia_remision: string | null
    guia_transporte: string | null
    sacos_camion: number | null  // Total sacos del camión (no granel)
    estado: 'EN_PROCESO' | 'COMPLETO'
    creado_en: string
    lotes: LoteOfflineData[]
    synced: boolean         // true = confirmado por servidor
    sync_error: string | null
}

export interface LoteOnlineData {
    offline_id: string        // UUID local - clave de idempotencia
    sesion_id: number         // ID real en servidor
    tipo_material: string
    ip: string
    numero_lote: number
    numero_ticket: string
    pesaje: PesajeOfflineData
    creado_en: string
    synced: boolean
    sync_error: string | null
}

export interface FinalizacionPendiente {
    sesion_id: number
    creado_en: string
    placa: string
    proveedor_razon_social: string
    total_lotes: number
}

export type LoteEditable = {
    numero_lote?: number
    tipo_material?: string
    numero_ticket?: string
    ip?: string
  }

export interface MuestreoQueueData {
    offline_id: string
    ip: string
    datos: {
        intento: number
        peso_humedo: number
        peso_seco: number
        observaciones: string | null
        fecha_muestreo: string
    }
    synced: boolean
    sync_error: string | null
}

export interface PruebaQueueData {
    offline_id: string
    ip: string
    datos: {
        malla_porcentaje: number | null
        porcentaje_nacn: number | null
        ph_inicial: number | null
        ph_final: number | null
        adicion_nacn: number | null
        adicion_naoh: number | null
        gasto_agno3: number | null
        fecha_ingreso: string
    }
    synced: boolean
    sync_error: string | null
}

// ── Tipos para offline de laboratorio ────────────────────────────────────────

export interface AnalisisLeyOfflineItem {
    offline_id: string
    datos: {
        cip: string
        laboratorio: string
        tipo_analisis: TipoAnalisis
        material: string
        ley_fino: number
        ley_grueso: number
        origen_datos: OrigenDatos
        fecha_analisis: string
    }
    error?: string
    synced?: boolean
}

export interface AnalisisRecuperacionOfflineItem {
    offline_id: string
    analisis_id: number   // ID real en servidor del registro PENDIENTE
    datos: {
        ley_cola: number
        ley_liquido: number | null
        fecha_analisis: string
    }
    synced?: boolean
    error?: string
}

// ── Tipo para CIPs generados offline (Muestreo Ciego) ────────────────────────

export interface CipOfflineData {
    offline_id: string       // UUID local
    ip: string               // IP del lote (ej: "IP-0042")
    lote_id: number          // ID numérico del lote — necesario para el algoritmo
    codigo_cip: string       // CIP calculado localmente (ej: "CIP-058598D-A1")
    correlativo: number      // Posición: cuántos CIPs ya existían + 1
    laboratorio: string      // 'Paititi' si correlativo <= 2, 'Por definir' en adelante
    tipo_muestra: string     // 'Laboratorio'
    synced: boolean
    sync_error: string | null
}

// ── Tipo para pares CIP de recuperación offline (Pruebas Metalurgicas) ──────────

export interface CipPruebaOfflineData {
    offline_id: string        // UUID local
    ip: string                // IP del lote
    lote_id: number           // ID numérico del lote
    codigo_cip1: string       // CIP principal (se asignará a prueba.cip al sincronizar)
    codigo_cip2: string       // CIP secundario (para repetición)
    correlativo1: number      // Correlativo independiente de CIPs de recuperación
    correlativo2: number
    sufijo: string            // 'R' | 'E'
    tipo: 'RecuperacionInterno' | 'RecuperacionExterno'
    synced: boolean
    sync_error: string | null
}

// ── Tipo para CIPs de reensayo offline (REE) ────────────────────────────────

export interface CipREEOfflineData {
    offline_id: string       // UUID local
    cip_origen: string       // CIP que originó el reensayo (ej: "CIP-058598D-A1")
    codigo_ree: string       // CIP calculado localmente (ej: "CIP-058598D-REE1")
    lote_id: number          // ID numérico del lote
    synced: boolean
    sync_error: string | null
}

// ── Apertura de DB ─────────────────────────────────────────

let _db: IDBDatabase | null = null

async function openDB(): Promise<IDBDatabase> {
    if (_db) return _db

    return new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VERSION)

        req.onupgradeneeded = (e) => {
            const db = (e.target as IDBOpenDBRequest).result
            const oldVersion = e.oldVersion

            if (oldVersion < 1) {
                // stores originales
                db.createObjectStore('ip_block', { keyPath: 'anio' })
                db.createObjectStore('provacops', { keyPath: 'provacop_id' })
                const s = db.createObjectStore('sesiones_q', { keyPath: 'offline_id' })
                s.createIndex('synced', 'synced', { unique: false })
            }

            if (oldVersion < 2) {
                // bloque de tickets - un único registro con keyPath 'id' = 'tk'
                db.createObjectStore('tk_block', { keyPath: 'id' })
            }

            if (oldVersion < 3) {
                db.createObjectStore('lotes_online_q', { keyPath: 'offline_id' })
            }

            if (oldVersion < 4) {
                db.createObjectStore('finalizaciones_q', { keyPath: 'sesion_id' })
            }

            if (oldVersion < 5) {
                db.createObjectStore('sesiones_cache', { keyPath: 'id' })
            }
            if (oldVersion < 6) {
                db.createObjectStore('muestreos_q', { keyPath: 'offline_id' })
                db.createObjectStore('lotes_muestreo_cache', { keyPath: 'ip' }) // Para cachear los lotes pendientes que vienen de balanza
            }
            if (oldVersion < 7) {
                db.createObjectStore('pruebas_q', { keyPath: 'offline_id' })
            }
            if (oldVersion < 8) {
                db.createObjectStore('analisis_lab_q', { keyPath: 'offline_id' })
            }
            if (oldVersion < 9) {
                db.createObjectStore('cips_lab_cache', { keyPath: 'cip' })
                db.createObjectStore('analisis_rec_q', { keyPath: 'offline_id' })
            }
            if (oldVersion < 10) {
                // Cola de CIPs de muestreo generados offline
                db.createObjectStore('cips_muestreo_q', { keyPath: 'offline_id' })
            }
            if (oldVersion < 11) {
                // Cache offline-first de la lista de pruebas metalúrgicas
                db.createObjectStore('pruebas_lista_cache', { keyPath: 'ip' })
            }
            if (oldVersion < 12) {
                // Cola de pares CIP de recuperación generados offline en Pruebas Met.
                db.createObjectStore('cips_pruebas_q', { keyPath: 'offline_id' })
            }
            if (oldVersion < 13) {
                // Cola de CIPs REE (re-ensayo) generados offline
                db.createObjectStore('cips_ree_q', { keyPath: 'offline_id' })
            }
            if (oldVersion < 14) {
                if (db.objectStoreNames.contains('pruebas_lista_cache')) {
                    db.deleteObjectStore('pruebas_lista_cache')
                }
                db.createObjectStore('pruebas_lista_cache', { keyPath: 'prueba_id' })
            }
        }

        req.onsuccess = () => { _db = req.result; resolve(_db) }
        req.onerror = () => reject(req.error)
    })
}

// ── Helpers genéricos ──────────────────────────────────────

async function get<T>(store: string, key: IDBValidKey): Promise<T | null> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction(store, 'readonly')
        const req = tx.objectStore(store).get(key)
        req.onsuccess = () => resolve(req.result ?? null)
        req.onerror = () => reject(req.error)
    })
}

async function put(store: string, value: unknown): Promise<void> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction(store, 'readwrite')
        const req = tx.objectStore(store).put(value)
        req.onsuccess = () => resolve()
        req.onerror = () => reject(req.error)
    })
}

async function getAll<T>(store: string): Promise<T[]> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction(store, 'readonly')
        const req = tx.objectStore(store).getAll()
        req.onsuccess = () => resolve(req.result)
        req.onerror = () => reject(req.error)
    })
}

async function del(store: string, key: IDBValidKey): Promise<void> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction(store, 'readwrite')
        const req = tx.objectStore(store).delete(key)
        req.onsuccess = () => resolve()
        req.onerror = () => reject(req.error)
    })
}

// ── API pública ────────────────────────────────────────────

// -- Bloque IP --

export async function guardarBloqueIP(bloque: Omit<IPBlock, 'usado' | 'reservado_en'>): Promise<void> {
    await put('ip_block', {
        ...bloque,
        usado: 0,
        reservado_en: new Date().toISOString(),
    })
}

export async function obtenerBloqueIP(): Promise<IPBlock | null> {
    const anio = new Date().getFullYear()
    return get<IPBlock>('ip_block', anio)
}

/**
 * Obtiene el siguiente IP disponible del bloque local.
 * Retorna null si el bloque está agotado (necesita reservar uno nuevo).
 */
export async function siguienteIP(ipsConocidos: string[] = []): Promise<string | null> {
    const anio = new Date().getFullYear()
    const bloque = await get<IPBlock>('ip_block', anio)
    if (!bloque) return null

    let maxUsado = bloque.usado

    const lotesOnline = await getAll<LoteOnlineData>('lotes_online_q')
    const sesionesOffline = await getAll<SesionOfflineData>('sesiones_q')

    const extraerNumeroIP = (ipStr: string): number => {
        const match = ipStr.match(/^IP-(\d+)$/)
        if (!match || !match[1]) return -1
        return parseInt(match[1], 10)
    }

    const procesarIP = (ipStr?: string) => {
        if (!ipStr) return
        const numero = extraerNumeroIP(ipStr)
        if (numero >= bloque.desde && numero <= bloque.hasta) {
            const usadoRelativo = numero - bloque.desde + 1
            if (usadoRelativo > maxUsado) {
                maxUsado = usadoRelativo
            }
        }
    }

    // 1. Considerar los IPs que la interfaz online ya sabe que existen
    for (const ip of ipsConocidos) procesarIP(ip)

    // 2. Considerar lo que hay en las colas offline pendientes
    for (const lote of lotesOnline) procesarIP(lote.ip)
    for (const sesion of sesionesOffline) {
        for (const lote of sesion.lotes) procesarIP(lote.ip)
    }

    const nextIpNumero = bloque.desde + maxUsado

    if (nextIpNumero > bloque.hasta) return null

    await put('ip_block', { ...bloque, usado: maxUsado + 1 })

    return `IP-${String(nextIpNumero).padStart(4, '0')}`
}

export async function bloqueAgotado(): Promise<boolean> {
    const bloque = await obtenerBloqueIP()
    if (!bloque) return true
    return (bloque.desde + bloque.usado) > bloque.hasta
}

export async function ipsDisponibles(): Promise<number> {
    const bloque = await obtenerBloqueIP()
    if (!bloque) return 0
    return Math.max(0, bloque.hasta - bloque.desde - bloque.usado + 1)
}

// -- Caché provacops --

export async function guardarProvacops(items: ProvAcopCacheItem[]): Promise<void> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction('provacops', 'readwrite')
        const store = tx.objectStore('provacops')
        store.clear()
        for (const item of items) store.put(item)
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
    })
}

export async function obtenerProvacops(): Promise<ProvAcopCacheItem[]> {
    return getAll<ProvAcopCacheItem>('provacops')
}

// -- Cola de sesiones --

export async function encolarSesion(sesion: SesionOfflineData): Promise<void> {
    await put('sesiones_q', sesion)
}

export async function obtenerSesionesPendientes(): Promise<SesionOfflineData[]> {
    const todas = await getAll<SesionOfflineData>('sesiones_q')
    return todas.filter(s => !s.synced)
}

export async function marcarSesionSynced(offlineId: string, serverId: number): Promise<void> {
    const sesion = await get<SesionOfflineData>('sesiones_q', offlineId)
    if (!sesion) return
    await put('sesiones_q', { ...sesion, synced: true, sync_error: null })
}

export async function marcarSesionError(offlineId: string, error: string): Promise<void> {
    const sesion = await get<SesionOfflineData>('sesiones_q', offlineId)
    if (!sesion) return
    await put('sesiones_q', { ...sesion, sync_error: error })
}

export async function actualizarEstadoSesionLocal(
    offlineId: string,
    estado: 'EN_PROCESO' | 'PAUSADO' | 'COMPLETO'
): Promise<void> {
    const sesion = await get<SesionOfflineData>('sesiones_q', offlineId)
    if (!sesion) return
    await put('sesiones_q', { ...sesion, estado })
  }

/**
 * Elimina sesiones ya sincronizadas de IndexedDB.
 * Solo se llama DESPUÉS de confirmar que el servidor las recibió.
 */
export async function limpiarSynced(): Promise<number> {
    const todas = await getAll<SesionOfflineData>('sesiones_q')
    const synced = todas.filter(s => s.synced)
    for (const s of synced) await del('sesiones_q', s.offline_id)
    return synced.length
}

export async function contarPendientes(): Promise<number> {
    try {
        const [sesiones, lotes, fin, muestreos, pruebas, analisisLab, analisisRec, cips, cipsPruebas, cipsREE] = await Promise.all([
            getAll<SesionOfflineData>('sesiones_q').catch(() => []),
            getAll<LoteOnlineData>('lotes_online_q').catch(() => []),
            getAll<FinalizacionPendiente>('finalizaciones_q').catch(() => []),
            getAll<MuestreoQueueData>('muestreos_q').catch(() => []),
            getAll<PruebaQueueData>('pruebas_q').catch(() => []),
            getAll<AnalisisLeyOfflineItem>('analisis_lab_q').catch(() => []),
            getAll<AnalisisRecuperacionOfflineItem>('analisis_rec_q').catch(() => []),
            getAll<CipOfflineData>('cips_muestreo_q').catch(() => []),
            getAll<CipPruebaOfflineData>('cips_pruebas_q').catch(() => []),
            getAll<CipREEOfflineData>('cips_ree_q').catch(() => []),
        ])
        return (
            sesiones.filter(s => !s.synced).length +
            lotes.filter(l => !l.synced).length +
            fin.length +
            muestreos.filter(m => !m.synced).length +
            pruebas.filter(p => !p.synced).length +
            analisisLab.filter(a => !a.synced).length +
            analisisRec.filter(a => !a.synced).length +
            cips.filter(c => !c.synced).length +
            cipsPruebas.filter(c => !c.synced).length +
            cipsREE.filter(c => !c.synced).length
        )
    } catch {
        return 0
    }
}


// ── Bloque de Tickets ──────────────────────────────────────

export async function guardarBloqueTK(
    bloque: Omit<TKBlock, 'id' | 'usado' | 'reservado_en'>
): Promise<void> {
    await put('tk_block', {
        id: 'tk',
        ...bloque,
        usado: 0,
        reservado_en: new Date().toISOString(),
    })
}

export async function obtenerBloqueTK(): Promise<TKBlock | null> {
    return get<TKBlock>('tk_block', 'tk')
}

/**
 * Retorna el siguiente número de ticket formateado como "TK-XXXXX".
 * Retorna null si el bloque está agotado.
 */
export async function siguienteTK(tksConocidos: string[] = []): Promise<string | null> {
    const bloque = await obtenerBloqueTK()
    if (!bloque) return null

    let maxUsado = bloque.usado

    const lotesOnline = await getAll<LoteOnlineData>('lotes_online_q')
    const sesionesOffline = await getAll<SesionOfflineData>('sesiones_q')

    const extraerNumeroTK = (tkStr: string): number => {
        const match = tkStr.match(/^TK-(\d+)$/)
        if (!match || !match[1]) return -1
        return parseInt(match[1], 10)
    }

    const procesarTK = (tkStr?: string) => {
        if (!tkStr) return
        const numero = extraerNumeroTK(tkStr)
        if (numero >= bloque.desde && numero <= bloque.hasta) {
            const usadoRelativo = numero - bloque.desde + 1
            if (usadoRelativo > maxUsado) {
                maxUsado = usadoRelativo
            }
        }
    }

    // 1. Considerar los tickets de la interfaz online
    for (const tk of tksConocidos) procesarTK(tk)

    // 2. Considerar lo offline
    for (const lote of lotesOnline) procesarTK(lote.numero_ticket)
    for (const sesion of sesionesOffline) {
        for (const lote of sesion.lotes) procesarTK(lote.numero_ticket)
    }

    const nextTkNumero = bloque.desde + maxUsado

    if (nextTkNumero > bloque.hasta) return null

    await put('tk_block', { ...bloque, usado: maxUsado + 1 })

    return `TK-${String(nextTkNumero).padStart(5, '0')}`
}

export async function bloqueTKAgotado(): Promise<boolean> {
    const bloque = await obtenerBloqueTK()
    if (!bloque) return true
    return (bloque.desde + bloque.usado) > bloque.hasta
}

// ── Cola de lotes de sesiones online (modo híbrido) ────────

export async function encolarLoteOnline(lote: LoteOnlineData): Promise<void> {
    await put('lotes_online_q', lote)
}

export async function obtenerLotesOnlinePendientes(): Promise<LoteOnlineData[]> {
    const todos = await getAll<LoteOnlineData>('lotes_online_q')
    return todos.filter(l => !l.synced)
}

export async function marcarLoteOnlineSynced(offlineId: string): Promise<void> {
    const lote = await get<LoteOnlineData>('lotes_online_q', offlineId)
    if (!lote) return
    await put('lotes_online_q', { ...lote, synced: true, sync_error: null })
}

export async function marcarLoteOnlineError(offlineId: string, error: string): Promise<void> {
    const lote = await get<LoteOnlineData>('lotes_online_q', offlineId)
    if (!lote) return
    await put('lotes_online_q', { ...lote, sync_error: error })
}

export async function limpiarLotesOnlineSynced(): Promise<void> {
    const todos = await getAll<LoteOnlineData>('lotes_online_q')
    for (const l of todos.filter(l => l.synced)) {
        await del('lotes_online_q', l.offline_id)
    }
}

export async function eliminarLoteOnline(offlineId: string): Promise<void> {
    await del('lotes_online_q', offlineId)
}

export async function contarLotesOnlinePendientes(sesionId?: number): Promise<number> {
    const pendientes = await obtenerLotesOnlinePendientes()
    if (sesionId !== undefined) return pendientes.filter(l => l.sesion_id === sesionId).length
    return pendientes.length
}

export async function obtenerTodosLotesOnline(): Promise<LoteOnlineData[]> {
    return getAll<LoteOnlineData>('lotes_online_q')
}

export async function encolarFinalizacion(
    sesionId: number,
    display: { placa: string; proveedor_razon_social: string; total_lotes: number }
): Promise<void> {
    await put('finalizaciones_q', {
        sesion_id: sesionId,
        creado_en: new Date().toISOString(),
        ...display,
    })
  }

export async function obtenerFinalizacionesPendientes(): Promise<FinalizacionPendiente[]> {
    return getAll<FinalizacionPendiente>('finalizaciones_q')
}

export async function eliminarFinalizacion(sesionId: number): Promise<void> {
    await del('finalizaciones_q', sesionId)
  }

// ── Funciones para Editar Borradores Offline (Draft Editing) ──────────────

export async function editarSesionOffline(offlineId: string, datos: Partial<SesionOfflineData>): Promise<void> {
    const sesion = await get<SesionOfflineData>('sesiones_q', offlineId)
    if (!sesion) throw new Error('Sesión offline no encontrada')
    await put('sesiones_q', { ...sesion, ...datos })
}

export async function editarLoteOffline(
    ipLote: string,
    datosLote: LoteEditable,
    datosPesaje?: Partial<PesajeOfflineData>
): Promise<void> {
    // 1. Buscar en lotes híbridos (sesión online, lote offline)
    const lotesOnline = await obtenerTodosLotesOnline()
    const loteHibrido = lotesOnline.find(l => l.ip === ipLote)

    if (loteHibrido) {
        if (datosPesaje) loteHibrido.pesaje = { ...loteHibrido.pesaje, ...datosPesaje }
        await put('lotes_online_q', { ...loteHibrido, ...datosLote })
        return
    }

    // 2. Buscar en sesiones 100% offline
    const sesiones = await obtenerSesionesPendientes()

    for (const sesion of sesiones) {
        const index = sesion.lotes.findIndex(l => l.ip === ipLote)
        if (index !== -1) {
            const loteTarget = sesion.lotes[index]

            if (!loteTarget) continue
            if (datosPesaje) loteTarget.pesaje = { ...loteTarget.pesaje, ...datosPesaje }
            sesion.lotes[index] = { ...loteTarget, ...datosLote } as LoteOfflineData
            await put('sesiones_q', sesion)
            return
        }
    }

    throw new Error('Lote offline no encontrado para editar')
}

// ── Caché de Sesiones Activas (Fotografías Online) ──────────────
export async function guardarSesionCache(sesion: SesionDetalle): Promise<void> {
    await put('sesiones_cache', JSON.parse(JSON.stringify(sesion)))
}

export async function obtenerSesionCache(id: number): Promise<SesionDetalle | null> {
    return get<SesionDetalle>('sesiones_cache', id)
}

export async function eliminarSesionCache(id: number): Promise<void> {
    await del('sesiones_cache', id)
}

export async function guardarListaSesionesCache(sesiones: SesionLista[]): Promise<void> {
    await put('sesiones_cache', { id: 'lista_dashboard', data: JSON.parse(JSON.stringify(sesiones)) })
}

export async function obtenerListaSesionesCache(): Promise<SesionLista[]> {
    const cached = await get<{ id: string, data: SesionLista[] }>('sesiones_cache', 'lista_dashboard')
    return cached ? cached.data : []
}

// ==========================================
// MÓDULO: MUESTREO (OFFLINE QUEUE)
// ==========================================

export async function encolarMuestreoOffline(muestreo: MuestreoQueueData): Promise<void> {
    await put('muestreos_q', muestreo)
}

export async function obtenerMuestreosPendientes(): Promise<MuestreoQueueData[]> {
    const todos = await getAll<MuestreoQueueData>('muestreos_q')
    return todos.filter(m => !m.synced)
}

export async function marcarMuestreoSynced(offlineId: string): Promise<void> {
    const m = await get<MuestreoQueueData>('muestreos_q', offlineId)
    if (!m) return
    await put('muestreos_q', { ...m, synced: true, sync_error: null })
}

export async function marcarMuestreoError(offlineId: string, error: string): Promise<void> {
    const m = await get<MuestreoQueueData>('muestreos_q', offlineId)
    if (!m) return
    await put('muestreos_q', { ...m, sync_error: error })
}

export async function limpiarMuestreosSynced(): Promise<void> {
    const todos = await getAll<MuestreoQueueData>('muestreos_q')
    for (const m of todos.filter(x => x.synced)) {
        await del('muestreos_q', m.offline_id)
    }
}

export async function guardarLotesMuestreoCache(lotes: LoteMuestreo[]): Promise<void> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction('lotes_muestreo_cache', 'readwrite')
        const store = tx.objectStore('lotes_muestreo_cache')
        store.clear() // Limpiamos la caché vieja
        for (const lote of lotes) {
            store.put(lote)
        }
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
    })
}

export async function obtenerLotesMuestreoCache(): Promise<LoteMuestreo[]> {
    return getAll<LoteMuestreo>('lotes_muestreo_cache')
}

// ==========================================
// MÓDULO: PRUEBAS METALÚRGICAS (OFFLINE)
// ==========================================

export async function encolarPruebaOffline(prueba: PruebaQueueData): Promise<void> {
    await put('pruebas_q', prueba)
}

export async function obtenerPruebasPendientes(): Promise<PruebaQueueData[]> {
    const todas = await getAll<PruebaQueueData>('pruebas_q')
    return todas.filter(p => !p.synced)
}

export async function marcarPruebaSynced(offlineId: string): Promise<void> {
    const p = await get<PruebaQueueData>('pruebas_q', offlineId)
    if (!p) return
    await put('pruebas_q', { ...p, synced: true, sync_error: null })
}

export async function marcarPruebaError(offlineId: string, error: string): Promise<void> {
    const p = await get<PruebaQueueData>('pruebas_q', offlineId)
    if (!p) return
    await put('pruebas_q', { ...p, sync_error: error })
}

export async function limpiarPruebasSynced(): Promise<void> {
    const todas = await getAll<PruebaQueueData>('pruebas_q')
    for (const p of todas.filter(x => x.synced)) {
        await del('pruebas_q', p.offline_id)
    }
}


// ── CRUD analisis_lab_q ───────────────────────────────────────────────────────

export async function encolarAnalisisLey(item: AnalisisLeyOfflineItem): Promise<void> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_lab_q', 'readwrite')
        tx.objectStore('analisis_lab_q').put(item)
        tx.oncomplete = () => res()
        tx.onerror = () => rej(tx.error)
    })
}

export async function obtenerAnalisisLeyPendientes(): Promise<AnalisisLeyOfflineItem[]> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_lab_q', 'readonly')
        const req = tx.objectStore('analisis_lab_q').getAll()
        req.onsuccess = () => res((req.result as AnalisisLeyOfflineItem[]).filter(x => !x.synced))
        req.onerror = () => rej(req.error)
    })
}

export async function marcarAnalisisLeySynced(offline_id: string): Promise<void> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_lab_q', 'readwrite')
        const store = tx.objectStore('analisis_lab_q')
        const req = store.get(offline_id)
        req.onsuccess = () => {
            if (req.result) { store.put({ ...req.result, synced: true, error: undefined }) }
            res()
        }
        req.onerror = () => rej(req.error)
    })
}

export async function marcarAnalisisLeyError(offline_id: string, error: string): Promise<void> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_lab_q', 'readwrite')
        const store = tx.objectStore('analisis_lab_q')
        const req = store.get(offline_id)
        req.onsuccess = () => {
            if (req.result) { store.put({ ...req.result, error }) }
            res()
        }
        req.onerror = () => rej(req.error)
    })
}

export async function limpiarAnalisisLeySynced(): Promise<void> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_lab_q', 'readwrite')
        const store = tx.objectStore('analisis_lab_q')
        const req = store.getAll()
        req.onsuccess = () => {
            const synced = (req.result as AnalisisLeyOfflineItem[]).filter(x => x.synced)
            synced.forEach(x => store.delete(x.offline_id))
            res()
        }
        req.onerror = () => rej(req.error)
    })
}

// ── Caché de CIPs de laboratorio ─────────────────────────────────────────────

export async function guardarCipsLabCache(cips: object[]): Promise<void> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction('cips_lab_cache', 'readwrite')
        const store = tx.objectStore('cips_lab_cache')
        store.clear()
        for (const cip of cips) store.put(cip)
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
    })
}

export async function obtenerCipsLabCache<T = unknown>(): Promise<T[]> {
    return getAll<T>('cips_lab_cache')
}

// ── Cola de analisis_recuperacion offline ────────────────────────────────────

export async function encolarAnalisisRecuperacion(item: AnalisisRecuperacionOfflineItem): Promise<void> {
    await put('analisis_rec_q', { ...item, synced: false })
}

export async function obtenerAnalisisRecuperacionPendientes(): Promise<AnalisisRecuperacionOfflineItem[]> {
    const todos = await getAll<AnalisisRecuperacionOfflineItem>('analisis_rec_q')
    return todos.filter(x => !x.synced)
}

export async function marcarAnalisisRecuperacionSynced(offline_id: string): Promise<void> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_rec_q', 'readwrite')
        const store = tx.objectStore('analisis_rec_q')
        const req = store.get(offline_id)
        req.onsuccess = () => {
            if (req.result) store.put({ ...req.result, synced: true, error: undefined })
            res()
        }
        req.onerror = () => rej(req.error)
    })
}

export async function marcarAnalisisRecuperacionError(offline_id: string, error: string): Promise<void> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_rec_q', 'readwrite')
        const store = tx.objectStore('analisis_rec_q')
        const req = store.get(offline_id)
        req.onsuccess = () => {
            if (req.result) store.put({ ...req.result, error })
            res()
        }
        req.onerror = () => rej(req.error)
    })
}

export async function limpiarAnalisisRecuperacionSynced(): Promise<void> {
    const db = await openDB()
    return new Promise((res, rej) => {
        const tx = db.transaction('analisis_rec_q', 'readwrite')
        const store = tx.objectStore('analisis_rec_q')
        const req = store.getAll()
        req.onsuccess = () => {
            ; (req.result as AnalisisRecuperacionOfflineItem[])
                .filter(x => x.synced)
                .forEach(x => store.delete(x.offline_id))
            res()
        }
        req.onerror = () => rej(req.error)
    })
}


// ==========================================
// MÓDULO: CIPs DE MUESTREO OFFLINE
// ==========================================

export async function encolarCipOffline(cip: CipOfflineData): Promise<void> {
    await put('cips_muestreo_q', cip)
}

export async function obtenerCipsPendientes(): Promise<CipOfflineData[]> {
    const todos = await getAll<CipOfflineData>('cips_muestreo_q')
    return todos.filter(c => !c.synced)
}

/** Devuelve todos los CIPs (synced o no) para un IP de lote concreto. */
export async function obtenerCipsPorLote(ip: string): Promise<CipOfflineData[]> {
    const todos = await getAll<CipOfflineData>('cips_muestreo_q')
    return todos.filter(c => c.ip === ip)
}

export async function marcarCipSynced(offline_id: string): Promise<void> {
    const cip = await get<CipOfflineData>('cips_muestreo_q', offline_id)
    if (!cip) return
    await put('cips_muestreo_q', { ...cip, synced: true, sync_error: null })
}

export async function marcarCipError(offline_id: string, error: string): Promise<void> {
    const cip = await get<CipOfflineData>('cips_muestreo_q', offline_id)
    if (!cip) return
    await put('cips_muestreo_q', { ...cip, sync_error: error })
}

export async function limpiarCipsSynced(): Promise<void> {
    const todos = await getAll<CipOfflineData>('cips_muestreo_q')
    for (const c of todos.filter(x => x.synced)) {
        await del('cips_muestreo_q', c.offline_id)
    }
}


// ==========================================
// MÓDULO: CACHE OFFLINE-FIRST PRUEBAS
// ==========================================

export async function guardarPruebasListaCache(pruebas: object[]): Promise<void> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pruebas_lista_cache', 'readwrite')
        const store = tx.objectStore('pruebas_lista_cache')
        store.clear()
        for (const p of pruebas) store.put(p)
        tx.oncomplete = () => resolve()
        tx.onerror = () => reject(tx.error)
    })
}

export async function obtenerPruebasListaCache<T = unknown>(): Promise<T[]> {
    return getAll<T>('pruebas_lista_cache')
}


// ==========================================
// MÓDULO: CIPs DE RECUPERACIÓN OFFLINE (Pruebas Metalúrgicas)
// ==========================================

export async function encolarCipPruebaOffline(cip: CipPruebaOfflineData): Promise<void> {
    await put('cips_pruebas_q', cip)
}

export async function obtenerCipsPruebasPendientes(): Promise<CipPruebaOfflineData[]> {
    const todos = await getAll<CipPruebaOfflineData>('cips_pruebas_q')
    return todos.filter(c => !c.synced)
}

/**
 * Cuenta cuántos CIPs de recuperación (synced o no) existen en la cola para un lote.
 * Usado para calcular el correlativo al generar nuevos CIPs offline.
 * Los correlativoss son independientes: R1, R2, R3... sin mezclar con los A de muestreo.
 */
export async function contarCipsPruebasPorLote(ip: string): Promise<number> {
    const todos = await getAll<CipPruebaOfflineData>('cips_pruebas_q')
    // Cada entrada representa un par (cip1 + cip2), por lo tanto son 2 CIPs
    return todos.filter(c => c.ip === ip).length * 2
}

export async function marcarCipPruebaSynced(offline_id: string): Promise<void> {
    const cip = await get<CipPruebaOfflineData>('cips_pruebas_q', offline_id)
    if (!cip) return
    await put('cips_pruebas_q', { ...cip, synced: true, sync_error: null })
}

export async function marcarCipPruebaError(offline_id: string, error: string): Promise<void> {
    const cip = await get<CipPruebaOfflineData>('cips_pruebas_q', offline_id)
    if (!cip) return
    await put('cips_pruebas_q', { ...cip, sync_error: error })
}

export async function limpiarCipsPruebasSynced(): Promise<void> {
    const todos = await getAll<CipPruebaOfflineData>('cips_pruebas_q')
    for (const c of todos.filter(x => x.synced)) {
        await del('cips_pruebas_q', c.offline_id)
    }
}


// ==========================================
// MÓDULO: CIPs REE (RE-ENSAYO) OFFLINE
// ==========================================

export async function encolarCipREE(cip: CipREEOfflineData): Promise<void> {
    await put('cips_ree_q', cip)
}

export async function obtenerCipsREEPendientes(): Promise<CipREEOfflineData[]> {
    const todos = await getAll<CipREEOfflineData>('cips_ree_q')
    return todos.filter(c => !c.synced)
}

/**
 * Devuelve todos los CIPs REE offline (synced o no) para un lote concreto.
 * Útil para calcular el correlativo offline sin colisionar con pendientes.
 */
export async function obtenerCipsREEPorLote(lote_id: number): Promise<CipREEOfflineData[]> {
    const todos = await getAll<CipREEOfflineData>('cips_ree_q')
    return todos.filter(c => c.lote_id === lote_id)
}

export async function marcarCipREESynced(offline_id: string): Promise<void> {
    const cip = await get<CipREEOfflineData>('cips_ree_q', offline_id)
    if (!cip) return
    await put('cips_ree_q', { ...cip, synced: true, sync_error: null })
}

export async function marcarCipREEError(offline_id: string, error: string): Promise<void> {
    const cip = await get<CipREEOfflineData>('cips_ree_q', offline_id)
    if (!cip) return
    await put('cips_ree_q', { ...cip, sync_error: error })
}

export async function limpiarCipsREESynced(): Promise<void> {
    const todos = await getAll<CipREEOfflineData>('cips_ree_q')
    for (const c of todos.filter(x => x.synced)) {
        await del('cips_ree_q', c.offline_id)
    }
}
