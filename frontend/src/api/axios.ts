import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Inyectar token en cada request
api.interceptors.request.use((config) => {
  const store = useAuthStore()
  if (store.accessToken) {
    config.headers.Authorization = `Bearer ${store.accessToken}`
  }
  return config
})

// Refresh automático si el token expiró
let isRefreshing = false
let queue: Array<(token: string) => void> = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }

    original._retry = true

    if (isRefreshing) {
      // Encolar requests mientras se refresca
      return new Promise((resolve) => {
        queue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(api(original))
        })
      })
    }

    isRefreshing = true

    try {
      const store = useAuthStore()
      await store.refresh()
      const newToken = store.accessToken!

      queue.forEach((cb) => cb(newToken))
      queue = []

      original.headers.Authorization = `Bearer ${newToken}`
      return api(original)
    } catch {
      // Refresh falló — limpiar sesión y redirigir a login
      const store = useAuthStore()
      store.clearTokens()
      window.location.href = '/login'
      return Promise.reject(error)
    } finally {
      isRefreshing = false
    }
  }
)

export default api
