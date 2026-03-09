/**
 * API service — Módulo Terceros (Proveedores/Acopiadores)
 * Refleja los endpoints de backend/app/routers/entidades.py
 */

import api from '@/api/axios'

// ── Types ─────────────────────────────────────────────────────────────────────

export type TipoAcopiador = 'sin_acopiador' | 'propio' | 'tercero'

export interface ParametrosComerciales {
  umbral_recup_bajo: number | null
  umbral_recup_medio: number | null
  lim_ley_inferior: number | null
  lim_ley_superior: number | null
  gasto_acopio: number | null
  gasto_consumo: number | null
  maquila: number | null
  comision: number | null
  lim_ley_comercial: number | null
  dscto_ley_comercial: number | null
  porcentaje_ley_comercial: number | null
  riesgo_comercial: number | null
}

export interface ParametrosRespuesta extends ParametrosComerciales {
  id: number
  provacop_id: number
}

export interface AcopiadorResumen {
  id: number
  razon_social: string
  ruc: string | null
  es_propio: boolean
}

export interface AcopiadorDropdown {
  id: number
  razon_social: string
  ruc: string | null
}

export interface TerceroLista {
  id: number
  provacop_id: number
  razon_social: string
  ruc: string | null
  referencia: string | null
  activo: boolean
  acopiador: string | null
}

export interface TerceroRespuesta {
  id: number
  razon_social: string
  ruc: string | null
  referencia: string | null
  telefono: string | null
  email: string | null
  activo: boolean
  provacop_id: number | null
  acopiador: AcopiadorResumen | null
  parametros: ParametrosRespuesta | null
}

export interface TerceroCrearPayload {
  razon_social: string
  ruc: string | null
  referencia: string | null
  telefono: string | null
  email: string | null
  tipo_acopiador: TipoAcopiador
  acopiador_id?: number | null
  acopiador_nuevo?: { razon_social: string; ruc?: string | null } | null
  parametros?: Partial<ParametrosComerciales> | null
}

export interface TerceroEditarPayload {
  razon_social?: string
  referencia?: string | null
  telefono?: string | null
  email?: string | null
  parametros?: Partial<ParametrosComerciales> | null
}

// ── Endpoints ─────────────────────────────────────────────────────────────────

const terceros = {
  /** Lista proveedores. activo: undefined = todos, true/false = filtro */
  listar(activo?: boolean): Promise<TerceroLista[]> {
    const params = activo !== undefined ? { activo } : {}
    return api.get('/terceros', { params }).then(r => r.data)
  },

  crear(datos: TerceroCrearPayload): Promise<TerceroRespuesta> {
    return api.post('/terceros', datos).then(r => r.data)
  },

  obtener(id: number): Promise<TerceroRespuesta> {
    return api.get(`/terceros/${id}`).then(r => r.data)
  },

  editar(id: number, datos: TerceroEditarPayload): Promise<TerceroRespuesta> {
    return api.put(`/terceros/${id}`, datos).then(r => r.data)
  },

  activar(id: number): Promise<TerceroRespuesta> {
    return api.patch(`/terceros/${id}/activar`).then(r => r.data)
  },

  desactivar(id: number): Promise<TerceroRespuesta> {
    return api.patch(`/terceros/${id}/desactivar`).then(r => r.data)
  },

  /** Dropdown de acopiadores activos */
  listarAcopiadores(): Promise<AcopiadorDropdown[]> {
    return api.get('/terceros/acopiadores').then(r => r.data)
  },

  /** Pre-llenar parámetros al seleccionar acopiador existente */
  parametrosAcopiador(acopiadorId: number): Promise<ParametrosRespuesta | null> {
    return api.get(`/terceros/acopiadores/${acopiadorId}/parametros`).then(r => r.data)
  },

  eliminar(id: number): Promise<void> {
    return api.delete(`/terceros/${id}`).then(() => undefined)
  },

  cambiarAcopiador(id: number, acopiadorId: number): Promise<TerceroRespuesta> {
    return api.patch(`/terceros/${id}/acopiador`, { acopiador_id: acopiadorId }).then(r => r.data)
  },

  buscarPorRuc(ruc: string): Promise<TerceroRespuesta | null> {
    return api.get(`/terceros/buscar-ruc/${ruc}`).then(r => r.data)
  },
}

export default terceros
