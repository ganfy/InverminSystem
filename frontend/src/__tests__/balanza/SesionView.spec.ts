import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createTestingPinia } from '@pinia/testing'
import { ref } from 'vue'
import SesionView from '@/views/balanza/SesionView.vue'
import { useBalanza } from '@/composables/useBalanza'

// 1. Mockear dependencias del Router
vi.mock('vue-router', async (importOriginal) => {
    const actual = await importOriginal<typeof import('vue-router')>()
    return {
        ...actual,
        useRoute: () => ({
            params: { id: '1' },
            name: 'SesionBalanza'
        }),
        useRouter: () => ({
            push: vi.fn(),
            replace: vi.fn()
        })
    }
})

// 2. Mockear el Composable de Sincronización
vi.mock('@/composables/useSync', () => ({
    useSync: () => ({
        online: ref(true),
        sesionRecargada: ref(null),
        limpiarSesionRecargada: vi.fn(),
        sesionOfflineSincronizada: ref(null),
        limpiarSesionOfflineSincronizada: vi.fn(),
        ultimoSync: ref(null)
    })
}))

// 3. Mockear el Composable de la Balanza (El "Dummy" del script)
vi.mock('@/composables/useBalanza', () => ({
    useBalanza: vi.fn()
}))

describe('SesionView.vue - Lógica de Balanza y Justificación', () => {
    let mockBalanza: any

    beforeEach(() => {
        // Estado inicial simulando que el script .bat/.exe está funcionando perfecto
        mockBalanza = {
            peso: ref(0),
            pesoDisplay: ref('0.000'),
            unidad: ref('TM'),
            estable: ref(true),
            conectado: ref(true),       // Puerto serial de la balanza responde
            wsConectado: ref(true),     // Script de Python conectado por WebSocket
            error: ref(null),
            config: ref({ puerto: 'COM3' }),
            capturar: vi.fn().mockResolvedValue({ peso: 15.500, estable: true })
        }
            ; (useBalanza as any).mockReturnValue(mockBalanza)
    })

    it('no pide justificación si el peso se captura automáticamente de la balanza', async () => {
        const wrapper = mount(SesionView, {
            global: {
                plugins: [createTestingPinia({
                    createSpy: vi.fn,
                    initialState: {
                        balanza: {
                            sesionActual: { id: 1, estado: 'EN_PROCESO', lotes: [] }
                        }
                    }
                })],
                stubs: ['BalanzaIndicator'] // Evitamos renderizar componentes visuales hijos
            }
        })

        // Seleccionamos tipo de material para cumplir validaciones
        await wrapper.find('select.header-select').setValue('Mineral')

        // Clic en "Capturar" BRUTO (Simula lectura automática del script)
        const btnCapturarBruto = wrapper.findAll('.btn-capturar')[0]
        await btnCapturarBruto.trigger('click')

        // Clic en "Capturar" TARA (Cambiamos el dummy y capturamos)
        mockBalanza.capturar.mockResolvedValueOnce({ peso: 5.500, estable: true })
        const btnCapturarTara = wrapper.findAll('.btn-capturar')[1]
        await btnCapturarTara.trigger('click')

        // Verificamos que NO aparece la advertencia de justificación
        expect(wrapper.text()).not.toContain('Justificación requerida')
        expect(wrapper.find('.form-faltantes').exists()).toBe(false)
    })

    it('exige justificación si la balanza está conectada pero el usuario ingresa el peso manualmente', async () => {
        const wrapper = mount(SesionView, {
            global: {
                plugins: [createTestingPinia({
                    createSpy: vi.fn,
                    initialState: { balanza: { sesionActual: { id: 1, estado: 'EN_PROCESO', lotes: [] } } }
                })],
                stubs: ['BalanzaIndicator']
            }
        })

        await wrapper.find('select.header-select').setValue('Mineral')

        // El usuario ignora el botón capturar e ingresa el peso tecleando (Registro Manual)
        const inputsPeso = wrapper.findAll('input[type="number"][step="0.001"]')
        await inputsPeso[0].setValue(20.000) // Bruto
        await inputsPeso[1].setValue(10.000) // Tara

        // La UI debe detectar la anomalía y exigir justificación
        expect(wrapper.text()).toContain('⚠ Ingreso Manual: Justificación requerida')

        // Si intenta registrar, debe bloquearlo indicando el faltante
        await wrapper.find('.btn-registrar').trigger('click')
        expect(wrapper.text()).toContain('Falta: justificación manual')

        // El usuario ingresa la justificación
        await wrapper.find('textarea').setValue('Balanza descalibrada temporalmente.')
        await wrapper.vm.$nextTick()

        // Intenta registrar de nuevo y la restricción debe desaparecer
        await wrapper.find('.btn-registrar').trigger('click')
        expect(wrapper.text()).not.toContain('Falta: justificación manual')
    })
})
