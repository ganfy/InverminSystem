import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import App from '@/App.vue'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createTestingPinia } from '@pinia/testing'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/', component: { template: '<div>Home</div>' } }]
})

describe('App.vue', () => {
  it('mounts renders properly', async () => {
    router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router, createTestingPinia({ stubActions: false, createSpy: vi.fn })]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})
