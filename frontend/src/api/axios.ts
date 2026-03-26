import axios from 'axios'
import router from '@/router'
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
// frontend/src/api/axios.ts

let isRefreshing = false
let queue: Array<(token: string) => void> = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Si el backend dice "Prohibido" (El usuario no tiene el rol necesario)
    if (error.response?.status === 403) {
      router.push({ name: 'Unauthorized' })
      return Promise.reject(error)
    }

    // Si es un 401 (No autorizado / Token expirado) y NO hemos reintentado ya esta petición
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      // Si el request fallido fue el intento de hacer refresh, significa que el refresh token
      // expiró o es inválido. Aquí SÍ debemos cerrar sesión definitivamente.
      if (originalRequest.url.includes('/auth/refresh')) {
        const authStore = useAuthStore()
        authStore.clearTokens()
        router.push({ name: 'Login' })
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // Si ya hay un refresh en curso, encolamos las demás peticiones que vayan llegando
        return new Promise((resolve) => {
          queue.push((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      isRefreshing = true

      try {
        const store = useAuthStore()
        // Intentar renovar los tokens silenciosamente
        await store.refresh()
        const newToken = store.accessToken!

        // Ejecutar las peticiones encoladas con el nuevo token
        queue.forEach((cb) => cb(newToken))
        queue = []

        // Reintentar la petición original que falló con el 401
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)

      } catch (refreshError) {
        // Si el refresh() lanza error (ej. refresh token vencido), limpiamos y mandamos al login
        const store = useAuthStore()
        store.clearTokens()
        queue = []
        router.push({ name: 'Login' })
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Si es cualquier otro error, simplemente lo devolvemos
    return Promise.reject(error)
  }
)

export default api
