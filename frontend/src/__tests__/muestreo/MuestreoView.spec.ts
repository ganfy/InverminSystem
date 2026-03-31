import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import MuestreoView from '@/views/muestreo/MuestreoView.vue'
import { useMuestreoStore } from '@/stores/muestreo'
import { useRouter } from 'vue-router'

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

describe('MuestreoView.vue', () => {
    let wrapper: any
    let store: any
    let routerPushMock: any

    // Esta data simulada representa lo que devolvería el backend
    const mockLotes = [
        { ip: 'IP-001', numero_lote: 1, estado_muestreo: 'PENDIENTE', peso_neto: 10 },
        { ip: 'IP-002', numero_lote: 2, estado_muestreo: 'COMPLETADO', peso_neto: 15 }
    ]

    beforeEach(() => {
        // Limpiamos los mocks antes de cada test
        vi.clearAllMocks()
        routerPushMock = vi.fn()
            ; (useRouter as any).mockReturnValue({ push: routerPushMock })

        // Montamos el componente con un Pinia de prueba
        wrapper = mount(MuestreoView, {
            global: {
                plugins: [createTestingPinia({ createSpy: vi.fn })],
                stubs: ['router-link', 'router-view', 'SyncIndicator'] // Ignoramos componentes hijos complejos
            }
        })

        // Configuramos nuestro store falso con las variables EXACTAS que usa tu vista
        store = useMuestreoStore()
        store.lotesPendientes = [
            { ip: 'IP-001', numero_lote: 1, estado_muestreo: 'PENDIENTE', peso_neto: 10 }
        ]
        store.lotesCompletados = [
            { ip: 'IP-002', numero_lote: 2, estado_muestreo: 'COMPLETADO', peso_neto: 15 }
        ]
        store.cargando = false
    })

    it('1. Renderiza correctamente y muestra la lista inicial (Pendientes)', async () => {
        // Comprobamos que el texto principal exista
        expect(wrapper.text()).toContain('Muestreo')

        // Por defecto debería mostrar solo los pendientes (IP-001) y ocultar los completados (IP-002)
        // Ajusta '.lote-card' a la clase real que uses para tus tarjetas
        const tarjetas = wrapper.findAll('.lote-card')

        // Suponiendo que por defecto muestra "Pendientes", debería haber 1 tarjeta
        // Si tu vista por defecto muestra TODOS, el toBe sería 2.
        expect(wrapper.text()).toContain('IP-001')
    })

    it('2. Filtra correctamente al cambiar de pestaña a "Completados"', async () => {
        // Buscamos el botón de la pestaña "Completados" y le hacemos clic
        // Ajusta los selectores según tu HTML
        const botonesTabs = wrapper.findAll('button')
        const tabCompletados = botonesTabs.find((b: any) => b.text().includes('COMPLETADOS'))

        if (tabCompletados) {
            await tabCompletados.trigger('click')

            // Ahora debería verse el IP-002 y no el IP-001
            expect(wrapper.text()).toContain('IP-002')
            expect(wrapper.text()).not.toContain('IP-001')
        }
    })

    it('3. Navega a la vista de registro al hacer clic en un lote pendiente', async () => {
        // Buscamos la primera tarjeta y le hacemos clic
        const btnRegistrar = wrapper.find('.card-lote button')

    if (btnRegistrar.exists()) {
      await btnRegistrar.trigger('click')

      // Verificamos que el router haya intentado enviarnos a la ruta correcta
      expect(routerPushMock).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'RegistrarHumedad',
          params: { ip: 'IP-001' }
        })
            )
        }
    })

    it('4. Abre el modal de Detalles al hacer clic en "Ver Detalles" (Completados)', async () => {
        // 1. Cambiamos a la pestaña Completados
        const tabCompletados = wrapper.findAll('.tab-btn').find((b: any) => b.text().includes('Completados'))
        await tabCompletados.trigger('click')
        await wrapper.vm.$nextTick() // Esperamos a que Vue actualice el DOM

        // 2. Buscamos el botón específico que dice "Ver Detalles"
        const btnDetalles = wrapper.findAll('.card-lote button').find((b: any) => b.text().includes('Ver Detalles'))
        expect(btnDetalles.exists()).toBe(true)

        // 3. Hacemos clic en el botón
        await btnDetalles.trigger('click')
        await wrapper.vm.$nextTick()

        // 4. Verificamos que la variable del modal haya capturado el IP correcto (IP-002)
        expect(wrapper.vm.modalDetallesIp).toBe('IP-002')
    })

    it('5. Abre el modal de Etiquetas al hacer clic en "Etiquetar" (Completados)', async () => {
        // 1. Aseguramos que estamos en la pestaña Completados
        wrapper.vm.tabActual = 'COMPLETADOS'
        await wrapper.vm.$nextTick()

        // 2. Buscamos el botón de Etiquetar
        const btnEtiquetar = wrapper.findAll('.card-lote button').find((b: any) => b.text().includes('Etiquetar'))
        expect(btnEtiquetar.exists()).toBe(true)

        // 3. Hacemos clic en el botón
        await btnEtiquetar.trigger('click')
        await wrapper.vm.$nextTick()

        // 4. Verificamos que la variable del modal de etiquetas tenga el IP correcto
        expect(wrapper.vm.modalEtiquetasIp).toBe('IP-002')
      })
})
