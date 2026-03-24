import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BalanzaView from '@/views/balanza/BalanzaView.vue'
import { createTestingPinia } from '@pinia/testing'
import { useBalanzaStore } from '@/stores/balanza'
import { ref } from 'vue'
import { obtenerSesionesPendientes, obtenerProvacops } from '@/composables/useOfflineQueue'

vi.mock('@/composables/useSync', () => ({
    useSync: () => ({
        pendientes: ref(false),
        online: ref(true),
        ultimoSync: ref(Date.now()),
        sesionRecargada: ref(null),
        limpiarSesionRecargada: vi.fn()
    })
}))

vi.mock('@/composables/useOfflineQueue', () => ({
    obtenerSesionesPendientes: vi.fn(() => Promise.resolve([])),
    obtenerProvacops: vi.fn(() => Promise.resolve([])),
    obtenerFinalizacionesPendientes: vi.fn(() => Promise.resolve([])),
    obtenerLotesOnlinePendientes: vi.fn(() => Promise.resolve([])),
    contarPendientes: vi.fn(() => Promise.resolve(0)),
    contarLotesOnlinePendientes: vi.fn(() => Promise.resolve(0))
}))

vi.mock('vue-router', async (importOriginal) => {
    const actual = await importOriginal<typeof import('vue-router')>()
    return {
        ...actual,
        useRouter: vi.fn(() => ({
            push: vi.fn()
        })),
        useRoute: vi.fn(() => ({
            params: {},
            query: {}
        }))
    }
})

describe('BalanzaView.vue', () => {
    it('renderiza la lista de sesiones desde el store (Modo Online)', async () => {
        const wrapper = mount(BalanzaView, {
            global: { plugins: [createTestingPinia({ createSpy: vi.fn })] }
        })

        const store = useBalanzaStore()
        store.sesiones = [
            {
                id: 1,
                proveedor_razon_social: 'PROVEEDOR ONLINE',
                placa: 'ABC-123',
                estado: 'EN_PROCESO',
                fecha_ingreso: '2023-10-01T12:00:00Z',
                es_propio: false,
                lotes_activos: 1,
                total_lotes: 1
            } as any
          ]
        store.loading = false

        await wrapper.vm.$nextTick()

        expect(wrapper.text()).toContain('Balanza')
        expect(wrapper.text()).toContain('PROVEEDOR ONLINE')
        expect(wrapper.text()).toContain('ABC-123')
    })

    it('renderiza el bloque de sesiones offline si existen pendientes en IndexedDB', async () => {
        vi.mocked(obtenerSesionesPendientes).mockResolvedValueOnce([
            {
                offline_id: 'off-1',
                provacop_id: 1,
                placa: 'OFF-999',
                estado: 'EN_PROCESO',
                creado_en: '2023-10-01T12:00:00Z',
                lotes: []
            } as any
        ])

        vi.mocked(obtenerProvacops).mockResolvedValueOnce([
            { provacop_id: 1, proveedor_razon_social: 'MINERA OFFLINE' } as any
        ])

        const wrapper = mount(BalanzaView, {
            global: { plugins: [createTestingPinia({ createSpy: vi.fn })] }
        })

        await flushPromises()
        await wrapper.vm.$nextTick()

        expect(wrapper.text()).toContain('OFF-999')
        expect(wrapper.text()).toContain('MINERA OFFLINE')
    })
})
