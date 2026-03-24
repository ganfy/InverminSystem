import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { mount, flushPromises } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useSync } from '@/composables/useSync'
import { balanzaApi } from '@/api/balanza'
import { useUiStore } from '@/stores/ui'
import {
    encolarSesion,
    guardarBloqueIP,
    obtenerSesionesPendientes,
    type SesionOfflineData
} from '@/composables/useOfflineQueue'

let dbRef: IDBDatabase | null = null
const originalOpen = indexedDB.open.bind(indexedDB)
indexedDB.open = function (name: string, version?: number) {
    const req = originalOpen(name, version)
    req.addEventListener('success', function (this: IDBOpenDBRequest) { dbRef = this.result })
    return req
}

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

describe('useSync - Manager de Sincronización', () => {
    let wrapper: any
    let syncManager: ReturnType<typeof useSync>
    let mockUi: any

    const TestComponent = defineComponent({
        setup() {
            syncManager = useSync()
            return () => null
        }
    })

    beforeEach(async () => {
        setActivePinia(createPinia())

        // 1. FORZAMOS EL SINGLETON: Todos usarán este mismo objeto mockUi
        mockUi = {
            showConfirm: vi.fn(),
            toast: vi.fn()
        }
        vi.mocked(useUiStore).mockReturnValue(mockUi)

        if (dbRef) {
            const stores = ['ip_block', 'provacops', 'sesiones_q', 'tk_block', 'lotes_online_q', 'finalizaciones_q']
            const storesToClear = stores.filter(s => dbRef!.objectStoreNames.contains(s))
            if (storesToClear.length > 0) {
                const tx = dbRef!.transaction(storesToClear, 'readwrite')
                storesToClear.forEach(s => tx.objectStore(s).clear())
                await new Promise<void>(resolve => { tx.oncomplete = () => resolve() })
            }
        }

        vi.clearAllMocks()
    })

    afterEach(() => {
        if (wrapper) wrapper.unmount()
        vi.restoreAllMocks()
    })

    describe('Escenario 4: Recuperación y Sync Automático', () => {
        it('debe enviar la cola pendiente al recuperar la red y limpiar la base de datos', async () => {
            const sesionPendiente: SesionOfflineData = {
                offline_id: 'off-recuperacion', provacop_id: 1, placa: 'XYZ-999',
                carreta: null, conductor: null, transportista: null, razon_social: null,
                guia_remision: null, guia_transporte: null, estado: 'EN_PROCESO',
                creado_en: new Date().toISOString(), synced: false, sync_error: null, lotes: []
            }
            await encolarSesion(sesionPendiente)

            vi.mocked(balanzaApi.syncBatch).mockResolvedValueOnce({
                resultados: [{ offline_id: 'off-recuperacion', server_id: 105, error: null }]
            })
            vi.mocked(balanzaApi.reservarBloqueIP).mockResolvedValue({ desde: 1, hasta: 100, anio: 2026, tamano: 100 })

            vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false)
            wrapper = mount(TestComponent)

            await flushPromises()
            await delay(50)

            expect(syncManager.online.value).toBe(false)
            expect(await obtenerSesionesPendientes()).toHaveLength(1)

            vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(true)
            window.dispatchEvent(new Event('online'))

            await flushPromises()
            await delay(100)
            await flushPromises()

            expect(syncManager.online.value).toBe(true)
            expect(balanzaApi.syncBatch).toHaveBeenCalledTimes(1)

            const pendientesPostSync = await obtenerSesionesPendientes()
            expect(pendientesPostSync).toHaveLength(0)
        })
    })

    describe('Escenario 5: Colisiones Edge Case (ERR_IP_COLLISION)', () => {
        it('debe interceptar el cruce de IP, pedir confirmación y reasignar un nuevo IP localmente', async () => {
            await guardarBloqueIP({ desde: 1, hasta: 10, anio: 2026 })

            const sesionConflicto: SesionOfflineData = {
                offline_id: 'off-colision', provacop_id: 1, placa: 'COL-123',
                carreta: null, conductor: null, transportista: null, razon_social: null,
                guia_remision: null, guia_transporte: null, estado: 'EN_PROCESO',
                creado_en: new Date().toISOString(), synced: false, sync_error: null,
                lotes: [
                    {
                        offline_id: 'lote-1', ip: 'IP-0001', numero_lote: 1, tipo_material: 'plata',
                        numero_ticket: 'TK-00001', pesaje: { peso_inicial: 10, peso_final: 5, granel: true, es_manual: false, justificacion_manual: null, sacos: null, fecha_inicio: null, fecha_fin: null },
                        creado_en: new Date().toISOString()
                    }
                ]
            }
            await encolarSesion(sesionConflicto)

            // 2. USAMOS NUESTRO OBJETO COMPARTIDO PARA SIMULAR EL CLIC EN "SÍ"
            mockUi.showConfirm.mockResolvedValueOnce(true)

            vi.mocked(balanzaApi.syncBatch).mockResolvedValueOnce({
                resultados: [{ offline_id: 'off-colision', server_id: null, error: 'ERR_IP_COLLISION|IP-0001' }]
            })

            vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(true)
            vi.mocked(balanzaApi.syncBatch)
                .mockResolvedValueOnce({ resultados: [{ offline_id: 'off-colision', server_id: null, error: 'ERR_IP_COLLISION|IP-0001' }] }) // La colisión (1er intento)
                .mockResolvedValueOnce({ resultados: [{ offline_id: 'off-colision', server_id: 999, error: null }] }) // El éxito (2do intento automático)
            wrapper = mount(TestComponent)

            await flushPromises()
            await delay(100)
            await flushPromises()

            // Comprobamos la llamada usando el Singleton
            expect(mockUi.showConfirm).toHaveBeenCalled()

            await delay(2100)
            await flushPromises()
            await delay(100)
            await flushPromises()

            const pendientesLocal = await obtenerSesionesPendientes()
            const sesionReparada = pendientesLocal.find(s => s.offline_id === 'off-colision')

            expect(sesionReparada?.lotes[0].ip).toBe('IP-0002')

            // Comprobamos el toast usando el Singleton
            expect(mockUi.toast).toHaveBeenCalledWith(
                expect.stringContaining('Se reasignó a IP-0002'),
                'info'
            )
        }, 10000)
    })
})
