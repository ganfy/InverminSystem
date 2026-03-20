import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UsuarioMe, TokenResponse } from '@/types/auth'
import { authApi } from '@/api/auth'

async function hashearCredenciales(username: string, pass: string): Promise<string> {
  const msgUint8 = new TextEncoder().encode(username.toLowerCase() + ':' + pass)
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken  = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user         = ref<UsuarioMe | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const rol             = computed(() => user.value?.rol ?? null)

  function setTokens(tokens: TokenResponse) {
    accessToken.value  = tokens.access_token
    refreshToken.value = tokens.refresh_token
    localStorage.setItem('access_token',  tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }

  function clearTokens() {
    accessToken.value  = null
    refreshToken.value = null
    user.value         = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login(username: string, password: string) {
    const userKey = username.toLowerCase()

    try {
      // 1. Intento normal (Online)
      const tokens = await authApi.login({ username, password })
      setTokens(tokens)
      await fetchMe()

      // 2. Guardar respaldo para futuros accesos Offline (Diccionario de usuarios)
      const hash = await hashearCredenciales(userKey, password)
      const cachedUsers = JSON.parse(localStorage.getItem('offline_users_dict') || '{}')

      cachedUsers[userKey] = {
        hash: hash,
        perfil: user.value
      }
      localStorage.setItem('offline_users_dict', JSON.stringify(cachedUsers))
      localStorage.setItem('last_offline_user', userKey) // Para saber a quién cargarle el perfil

    } catch (e: any) {
      // 3. Fallback: Modo Offline
      const isNetworkError = !navigator.onLine || e.code === 'ERR_NETWORK' || e.message === 'Network Error' || e.message.toLowerCase().includes('network')

      if (isNetworkError) {
        const cachedUsers = JSON.parse(localStorage.getItem('offline_users_dict') || '{}')
        const userData = cachedUsers[userKey]

        if (!userData) {
          throw new Error(`El usuario "${username}" nunca ha iniciado sesión en este equipo con conexión a internet.`)
        }

        const inputHash = await hashearCredenciales(userKey, password)

        if (userData.hash === inputHash) {
          // Credenciales offline válidas
          user.value = userData.perfil
          localStorage.setItem('last_offline_user', userKey)

          // Inyectamos un token simulado para que el Router nos deje pasar
          accessToken.value = 'offline-token-123'
          localStorage.setItem('access_token', accessToken.value)

          console.warn(`Login offline exitoso para: ${username}`)
          return // Salimos exitosamente
        } else {
          throw new Error('Contraseña incorrecta.')
        }
      }

      // Si no fue error de red (ej. mala contraseña online), lanzamos el error
      throw e
    }
  }

  async function logout() {
    try {
      if (accessToken.value !== 'offline-token-123') {
        await authApi.logout()
      }
    } catch (error) {
      console.warn('Error al hacer logout en el servidor. Limpiando sesión local...', error)
    } finally {
      clearTokens()
    }
  }

  async function fetchMe() {
    if (accessToken.value === 'offline-token-123') {
      const lastUser = localStorage.getItem('last_offline_user')
      if (lastUser) {
        const cachedUsers = JSON.parse(localStorage.getItem('offline_users_dict') || '{}')
        if (cachedUsers[lastUser]) {
          user.value = cachedUsers[lastUser].perfil
          return
        }
      }
    }

    // Flujo normal online
    user.value = await authApi.me()
  }

  async function refresh() {
    if(accessToken.value === 'offline-token-123') return // No se refrescan tokens offline

    if (!refreshToken.value) throw new Error('No refresh token')
    const tokens = await authApi.refresh(refreshToken.value)
    setTokens(tokens)
  }

  return {
    accessToken, refreshToken, user,
    isAuthenticated, rol,
    login, logout, fetchMe, refresh, clearTokens,
  }
})
