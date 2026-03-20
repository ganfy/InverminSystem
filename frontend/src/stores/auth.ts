import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UsuarioMe, TokenResponse } from '@/types/auth'
import { authApi } from '@/api/auth'

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
    const tokens = await authApi.login({ username, password })
    setTokens(tokens)
    await fetchMe()
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (error) {
      // Si estamos offline o el backend no responde, ignoramos el error. De todas formas, vamos a limpiar la sesión local.
      console.warn('Error al hacer logout en el servidor. Limpiando sesión local...', error)
    } finally {
      clearTokens()
    }
  }

  async function fetchMe() {
    user.value = await authApi.me()
  }

  async function refresh() {
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
