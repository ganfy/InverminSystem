import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import PruebasView from '@/views/pruebas/PruebasView.vue'
import { useRouter } from 'vue-router'
import { pruebasApi } from '@/api/pruebas'
import { obtenerPruebasPendientes } from '@/composables/useOfflineQueue'
import { ref } from 'vue'

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

vi.mock('@/api/pruebas', () => ({
    pruebasApi: {
        obtenerListaPruebas: vi.fn()
    }
}))

vi.mock('@/composables/useOfflineQueue', () => ({
    obtenerPruebasPendientes: vi.fn()
}))

vi.mock('@/composables/useSync', () => ({
    useSync: () => ({
        pendientes: ref(0),
        online: ref(true),
        ultimoSync: ref(Date.now())
    })
}))

describe('PruebasView.vue', () => {
    let wrapper: any
    let routerPushMock: any

    // Datos simulados (Online)
    const mockLotesOnline = [
        { ip: 'IP-001', fecha_recepcion: '2026-04-01T10:00:00Z', estado: 'PENDIENTE' },
        { ip: 'IP-002', fecha_recepcion: '2026-04-01T11:00:00Z', estado: 'EN PROCESO' },
        { ip: 'IP-003', fecha_recepcion: '2026-04-01T12:00:00Z', estado: 'COMPLETO' }
    ]

    // Datos simulados (Offline / Local)
    const mockLotesOffline = [
        {
            offline_id: 'local-123',
            ip: 'IP-999',
            synced: false,
            datos: { malla_porcentaje: 92.5, gasto_agno3: 12.4 }
        }
    ]

    beforeEach(() => {
        vi.clearAllMocks()
        routerPushMock = vi.fn()
            ; (useRouter as any).mockReturnValue({ push: routerPushMock })

            // Configuramos los retornos por defecto de nuestras funciones mockeadas
            ; (pruebasApi.obtenerListaPruebas as any).mockResolvedValue(mockLotesOnline)
            ; (obtenerPruebasPendientes as any).mockResolvedValue([]) // Por defecto sin datos offline
    })

    const mountView = () => {
        return mount(PruebasView, {
            global: {
                plugins: [createTestingPinia({ createSpy: vi.fn })],
                stubs: ['WifiOff'] // Ignoramos el ícono de Lucide
            }
        })
    }

    it('1. Renderiza correctamente y carga la lista de pruebas del servidor', async () => {
        wrapper = mountView()
        await flushPromises() // Espera a que se resuelvan las promesas de onMounted

        expect(wrapper.text()).toContain('Pruebas Metalúrgicas')
        expect(pruebasApi.obtenerListaPruebas).toHaveBeenCalledTimes(1)

        // Debería mostrar los lotes online
        expect(wrapper.text()).toContain('IP-001')
        expect(wrapper.text()).toContain('IP-002')
    })

    it('2. Muestra la sección "SIN SINCRONIZAR" cuando hay datos locales', async () => {
        // Forzamos a que la función offline devuelva nuestro mock
        ; (obtenerPruebasPendientes as any).mockResolvedValue(mockLotesOffline)

        wrapper = mountView()
        await flushPromises()

        // Verificamos que aparezca el contenedor naranja offline y el lote local
        expect(wrapper.text()).toContain('SIN SINCRONIZAR')
        expect(wrapper.text()).toContain('1 prueba(s) local(es)')
        expect(wrapper.text()).toContain('IP-999') // El IP del dato offline
    })

    it('3. Filtra la tabla correctamente por Estado', async () => {
        wrapper = mountView()
        await flushPromises()

        // 1. Seleccionamos el filtro "EN PROCESO"
        const select = wrapper.find('select')
        await select.setValue('EN PROCESO')
        await wrapper.vm.$nextTick()

        // 2. Solo debe verse el IP-002
        expect(wrapper.text()).toContain('IP-002')
        expect(wrapper.text()).not.toContain('IP-001') // PENDIENTE
        expect(wrapper.text()).not.toContain('IP-003') // COMPLETO
    })

    it('4. Filtra la tabla correctamente por Búsqueda (IP)', async () => {
        wrapper = mountView()
        await flushPromises()

        // 1. Escribimos en el input de búsqueda
        const inputBusqueda = wrapper.find('input[type="text"]')
        await inputBusqueda.setValue('IP-003')
        await wrapper.vm.$nextTick()

        // 2. Solo debe verse el IP-003
        expect(wrapper.text()).toContain('IP-003')
        expect(wrapper.text()).not.toContain('IP-001')
        expect(wrapper.text()).not.toContain('IP-002')
    })

    it('5. Navega a la vista de Registro al hacer clic en un botón de la tabla', async () => {
        wrapper = mountView()
        await flushPromises()

        // Buscamos el primer botón de la tabla principal
        const btnRegistrar = wrapper.find('tbody button.btn-primary')

        expect(btnRegistrar.exists()).toBe(true)
        await btnRegistrar.trigger('click')

        // Verificamos que el router haya empujado la ruta correcta con el IP
        expect(routerPushMock).toHaveBeenCalledWith(
            expect.objectContaining({
                name: 'RegistrarPrueba',
                params: { ip: 'IP-001' } // El primer lote en la tabla
            })
        )
    })
})
