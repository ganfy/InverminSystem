import api from './axios'
import type { LoginRequest, TokenResponse, UsuarioMe } from '@/types/auth'

export const authApi = {
  login(data: LoginRequest): Promise<TokenResponse> {
    return api.post('/auth/login', data).then((r) => r.data)
  },

  logout(): Promise<void> {
    return api.post('/auth/logout').then(() => undefined)
  },

  refresh(refreshToken: string): Promise<TokenResponse> {
    return api.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data)
  },

  me(): Promise<UsuarioMe> {
    return api.get('/auth/me').then((r) => r.data)
  },
}
