import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import TercerosView from '@/views/terceros/TercerosView.vue'
import { createTestingPinia } from '@pinia/testing'
import { useTercerosStore } from '@/stores/terceros'
import { useAuthStore } from '@/stores/auth'

describe('TercerosView.vue', () => {
  let wrapper: any

  const setupComponent = (rolUsuario: string) => {
    const pinia = createTestingPinia({ stubActions: false, createSpy: vi.fn })
    const authStore = useAuthStore()
    const tercerosStore = useTercerosStore()

    // Configuramos el rol del usuario
    authStore.user = { rol: rolUsuario } as any
    // Configuramos datos iniciales de la tabla
    tercerosStore.lista = [
      { id: 1, razon_social: 'MINERA SUR', ruc: '20123456789', activo: true },
      { id: 2, razon_social: 'LOGISTICA NORTE', ruc: '20987654321', activo: false }
    ] as any

    return mount(TercerosView, {
      global: { plugins: [pinia] }
    })
  }

  it('permite ver los botones de creación y edición si es Admin', async () => {
    wrapper = setupComponent('Admin')

    const tercerosStore = useTercerosStore()
    tercerosStore.cargando = false

    await wrapper.vm.$nextTick()

    // El botón "+ Registrar" debe existir
    expect(wrapper.find('button.btn-primary').exists()).toBe(true)
    // El botón de editar debe existir en la tabla
    expect(wrapper.find('button.btn-accion[title="Editar"]').exists()).toBe(true)
  })

  it('oculta los botones de creación si el rol es solo Lector/Operador', async () => {
    wrapper = setupComponent('Operador')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('button.btn-primary').exists()).toBe(false)
    expect(wrapper.find('button.btn-accion[title="Editar"]').exists()).toBe(false)
  })

  it('filtra correctamente los resultados al escribir en el buscador', async () => {
    wrapper = setupComponent('Admin')

    const tercerosStore = useTercerosStore()
    tercerosStore.cargando = false

    await wrapper.vm.$nextTick()

    const inputBusqueda = wrapper.find('.filtro-busqueda input')
    await inputBusqueda.setValue('MINERA')

    // Debería mostrar MINERA SUR pero no LOGISTICA NORTE
    expect(wrapper.text()).toContain('MINERA SUR')
    expect(wrapper.text()).not.toContain('LOGISTICA NORTE')
  })
})
