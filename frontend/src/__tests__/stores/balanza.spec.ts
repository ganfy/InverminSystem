import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBalanzaStore } from '@/stores/balanza'
import { balanzaApi } from '@/api/balanza'
import {
    guardarBloqueIP,
    guardarBloqueTK,
    obtenerTodosLotesOnline,
    obtenerSesionesPendientes,
    type LoteOnlineData
} from '@/composables/useOfflineQueue'

// Interceptor para limpiar la BD
let dbRef: IDBDatabase | null = null
const originalOpen = indexedDB.open.bind(indexedDB)
indexedDB.open = function (name: string, version?: number) {
    const req = originalOpen(name, version)
    req.addEventListener('success', function (this: IDBOpenDBRequest) { dbRef = this.result })
    return req
}

describe('Store: Balanza (Flujo Híbrido y Offline)', () => {
    let store: ReturnType<typeof useBalanzaStore>

    beforeEach(async () => {
        setActivePinia(createPinia())
        store = useBalanzaStore()

        // 1. Limpiar IndexedDB
        if (dbRef) {
            const stores = ['ip_block', 'provacops', 'sesiones_q', 'tk_block', 'lotes_online_q', 'finalizaciones_q', 'sesiones_cache']
            const storesToClear = stores.filter(s => dbRef!.objectStoreNames.contains(s))
            if (storesToClear.length > 0) {
                const tx = dbRef!.transaction(storesToClear, 'readwrite')
                storesToClear.forEach(s => tx.objectStore(s).clear())
                await new Promise<void>((resolve) => { tx.oncomplete = () => resolve() })
            }
        }

        // 2. Preparar el terreno: Darle a la BD local bloques válidos para operar offline
        await guardarBloqueIP({ desde: 1, hasta: 1000, anio: 2026 })
        await guardarBloqueTK({ desde: 1, hasta: 1000 })

        // 3. Forzar que el navegador empiece "Online"
        vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(true)
    })

    afterEach(() => {
        vi.restoreAllMocks()
    })

    describe('Escenario 2: Creación Híbrida', () => {
        it('debe agregar un lote offline a una sesión online si se cae la red', async () => {
            // 1. Simulamos que la API crea la sesión exitosamente en el servidor
            const sesionMock = {
                id: 99,
                estado: 'EN_PROCESO',
                placa: 'ABC-123',
                lotes: []
            }
            vi.mocked(balanzaApi.crearSesion).mockResolvedValueOnce(sesionMock as any)

            // 2. Creamos la sesión estando ONLINE
            await store.crearSesion({ provacop_id: 1, placa: 'ABC-123' } as any)
            expect(store.sesionActual?.id).toBe(99)

            // 3. ¡SE CAE LA RED! Simulamos desconexión
            vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false)

            // 4. Intentamos agregar un lote. Como no hay red, debe ir a 'lotes_online_q'
            const loteAgregado = await store.agregarLote(99, {
                tipo_material: 'cobre',
                pesaje: { peso_inicial: 30, peso_final: 10 }
            } as any)

            // Verificaciones:
            expect(loteAgregado).not.toBeNull()
            expect(loteAgregado?.local_only).toBe(true) // Bandera visual de "No sincronizado"
            expect(loteAgregado?.ip).toBe('IP-0001') // Tomó el primero del bloque IP
            expect(loteAgregado?.pesaje?.numero_ticket).toBe('TK-00001')

            // Verificar que se guardó en la cola híbrida (IndexedDB)
            const lotesEnCola = await obtenerTodosLotesOnline()
            expect(lotesEnCola).toHaveLength(1)
            expect(lotesEnCola[0].sesion_id).toBe(99)
            expect(lotesEnCola[0].ip).toBe('IP-0001')
            expect(store.lotesHybridPendientes).toBe(1) // El UI debe saber que hay 1 lote pendiente
        })
    })

    describe('Escenario 3: Edición Offline', () => {
        it('debe permitir editar los pesos de un lote híbrido (offline en sesión online)', async () => {
            // 1. Simulamos que ya estamos en una sesión (id: 99)
            store.sesionActual = {
                id: 99,
                estado: 'EN_PROCESO',
                lotes: []
            } as any

            // 2. Sin red, agregamos el lote
            vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false)
            const lote = await store.agregarLote(99, {
                tipo_material: 'zinc',
                pesaje: { peso_inicial: 40, peso_final: 15 }
            } as any)

            expect(lote?.ip).toBeDefined()

            // 3. Editamos el peso final de ese lote offline
            const exito = await store.editarLote(99, lote!.ip, {
                peso_final: 20
            } as any)

            expect(exito).toBe(true)

            // Verificamos que se actualizó en la BD de IndexedDB
            const lotesEnCola = await obtenerTodosLotesOnline()
            const loteEditadoDB = lotesEnCola.find(l => l.ip === lote!.ip)

            expect(loteEditadoDB?.pesaje.peso_final).toBe(20) // ¡Se actualizó en la BD local!
        })
    })

    describe('Escenario 6: Flujo 100% Offline (Creación, Lotes y Finalización)', () => {
        it('debe permitir crear una sesión entera desde cero sin internet y guardarla en sesiones_q', async () => {
            // 1. Apagamos el internet desde el inicio
            vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false)

            // 2. Preparamos la caché local
            const { guardarProvacops, obtenerSesionesPendientes } = await import('@/composables/useOfflineQueue')
            await guardarProvacops([{
                provacop_id: 1,
                proveedor_razon_social: 'Minera Offline S.A.',
                proveedor_ruc: '20123456789',
                acopiador_razon_social: '',
                es_propio: true
            } as any])

            // 3. Crear Sesión 100% Offline
            const sesion = await store.crearSesion({ provacop_id: 1, placa: 'OFF-001' } as any)

            expect(sesion).not.toBeNull()
            expect(sesion!.offline_id).toContain('offline-')
            expect(sesion!.estado).toBe('EN_PROCESO')

            let pendientes = await obtenerSesionesPendientes()
            expect(pendientes).toHaveLength(1)
            expect(pendientes[0].placa).toBe('OFF-001')

            // 4. Agregamos un lote a esta sesión local
            const lote = await store.agregarLote(sesion!.offline_id, {
                tipo_material: 'plomo',
                pesaje: { peso_inicial: 50, peso_final: 20 }
            } as any)

            expect(lote).not.toBeNull()
            expect(lote!.ip).toBe('IP-0001')

            pendientes = await obtenerSesionesPendientes()
            expect(pendientes[0].lotes).toHaveLength(1)
            expect(pendientes[0].lotes[0].ip).toBe('IP-0001')

            // 5. Finalizamos la sesión localmente
            await store.finalizarSesionOffline(sesion!.offline_id)

            pendientes = await obtenerSesionesPendientes()
            expect(pendientes[0].estado).toBe('COMPLETO')
            expect(store.sesionActual?.estado).toBe('COMPLETO')
        })
    })
})
