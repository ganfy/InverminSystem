export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  rol: string
  nombre: string
}

export interface UsuarioMe {
  id: number
  username: string
  nombre_completo: string
  rol: string
  email: string | null
}

export type RolSistema =
  | 'Admin'
  | 'Gerencia'
  | 'Comercial'
  | 'Laboratorista'
  | 'OperadorBalanza'
  | 'TécnicoMuestreo'
