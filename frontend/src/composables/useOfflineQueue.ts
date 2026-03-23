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

const DB_NAME = 'invermin_offline'
const DB_VERSION = 4

// ── Tipos ──────────────────────────────────────────────────

export interface IPBlock {
    desde: number
    hasta: number
    usado: number       // cuántos IPs del bloque ya se usaron
    anio: number
    reservado_en: string
}

export interface TKBlock {
    id: 'tk'          // clave fija — un solo registro
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
    estado: 'EN_PROCESO' | 'COMPLETO'
    creado_en: string
    lotes: LoteOfflineData[]
    synced: boolean         // true = confirmado por servidor
    sync_error: string | null
}

export interface LoteOnlineData {
    offline_id: string        // UUID local — clave de idempotencia
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
                // bloque de tickets — un único registro con keyPath 'id' = 'tk'
                db.createObjectStore('tk_block', { keyPath: 'id' })
            }

            if (oldVersion < 3) {
                db.createObjectStore('lotes_online_q', { keyPath: 'offline_id' })
            }

            if (oldVersion < 4) {
                db.createObjectStore('finalizaciones_q', { keyPath: 'sesion_id' })
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
    const pendientes = await obtenerSesionesPendientes()
    return pendientes.length
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
