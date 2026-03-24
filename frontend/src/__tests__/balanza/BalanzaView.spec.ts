import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BalanzaView from '@/views/balanza/BalanzaView.vue'
import { createTestingPinia } from '@pinia/testing'
import { useBalanzaStore } from '@/stores/balanza'
import { ref } from 'vue'

// Simulamos los composables de Sync y Offline Queue
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

// Mock básico del router
vi.mock('vue-router', () => ({
    useRouter: vi.fn(() => ({ push: vi.fn() }))
}))

describe('BalanzaView.vue', () => {
    it('renderiza la lista de sesiones desde el store (Modo Online)', async () => {
        const wrapper = mount(BalanzaView, {
            global: { plugins: [createTestingPinia({ createSpy: vi.fn })] }
        })

        const store = useBalanzaStore()
        // Inyectamos sesiones mockeadas
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

    // Nota: Para probar completamente el estado offline, sobreescribir los
    // mocks de vi.mock('@/composables/useOfflineQueue') para que devuelvan arrays
    // con datos y validar que el bloque `<div class="offline-section">` se renderice.
})
