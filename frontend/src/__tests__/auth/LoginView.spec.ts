import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createTestingPinia } from '@pinia/testing'
import { useRouter } from 'vue-router'
import LoginView from '@/views/auth/LoginView.vue'
import { useAuthStore } from '@/stores/auth'

// Simulamos Vue Router
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

describe('LoginView.vue', () => {
    let wrapper: any
    let routerPushMock: any

    beforeEach(() => {
        routerPushMock = vi.fn()
            ; (useRouter as any).mockReturnValue({ push: routerPushMock })

        wrapper = mount(LoginView, {
            global: {
                plugins: [createTestingPinia({ stubActions: false, createSpy: vi.fn })],
            }
              })
    })

    it('muestra un error si los campos están vacíos', async () => {
        await wrapper.find('form').trigger('submit.prevent')
        expect(wrapper.text()).toContain('Ingrese usuario y contraseña')
    })

    it('llama a authStore.login y redirige en un login exitoso', async () => {
        const authStore = useAuthStore()
        // Simulamos que el login funciona correctamente
        vi.spyOn(authStore, 'login').mockResolvedValue()

        await wrapper.find('input[type="text"]').setValue('admin')
        await wrapper.find('input[type="password"]').setValue('123456')
        await wrapper.find('form').trigger('submit.prevent')

        expect(authStore.login).toHaveBeenCalledWith('admin', '123456')
        expect(routerPushMock).toHaveBeenCalledWith('/')
    })

    it('muestra un mensaje de error si el login falla', async () => {
        const authStore = useAuthStore()
        // Simulamos un error de la API
        vi.spyOn(authStore, 'login').mockRejectedValue({
            response: { data: { detail: 'Credenciales inválidas' } }
        })

        await wrapper.find('input[type="text"]').setValue('admin')
        await wrapper.find('input[type="password"]').setValue('mala_pass')
        await wrapper.find('form').trigger('submit.prevent')

        // Esperamos a que el DOM se actualice tras la promesa rechazada
        await wrapper.vm.$nextTick()

        expect(wrapper.text()).toContain('Credenciales inválidas')
    })
})
