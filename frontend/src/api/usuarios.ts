import api from './axios'

export interface UsuarioListItem {
  id:               number
  username:         string
  nombre_completo:  string
  rol:              string
  email:            string | null
  activo:           boolean
  creado_en:        string
}

export interface UsuarioCrear {
  username:        string
  password:        string
  nombre_completo: string
  rol:             string
  email?:          string
}

export interface UsuarioEditar {
  nombre_completo?: string
  rol?:             string
  email?:           string
}

export const usuariosApi = {
  listar(): Promise<UsuarioListItem[]> {
    return api.get('/admin/usuarios').then(r => r.data)
  },
  crear(data: UsuarioCrear): Promise<UsuarioListItem> {
    return api.post('/admin/usuarios', data).then(r => r.data)
  },
  editar(id: number, data: UsuarioEditar): Promise<UsuarioListItem> {
    return api.put(`/admin/usuarios/${id}`, data).then(r => r.data)
  },
  activar(id: number): Promise<void> {
    return api.patch(`/admin/usuarios/${id}/activar`).then(() => undefined)
  },
  desactivar(id: number): Promise<void> {
    return api.patch(`/admin/usuarios/${id}/desactivar`).then(() => undefined)
  },
  resetPassword(id: number, password: string): Promise<void> {
    return api.patch(`/admin/usuarios/${id}/reset-password`, { nueva_password: password }).then(() => undefined)
  },
}
