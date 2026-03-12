import api from './axios'

// ── Tipos ─────────────────────────────────────────────────────────────────────

export interface ProvAcopDropdown {
  provacop_id: number
  proveedor_id: number
  proveedor_razon_social: string
  proveedor_ruc: string | null
  acopiador_id: number
  acopiador_razon_social: string
  acopiador_ruc: string | null
  es_propio: boolean
}

export interface PesajeCrear {
  peso_inicial: number   // BRUTO — camión cargado (primer pesaje)
  peso_final: number     // TARA  — camión vacío   (segundo pesaje tras descarga)
  sacos?: number | null
  granel?: boolean
  fecha_inicio?: string | null
}

export interface PesajeDetalle {
  id: number
  peso_inicial: number   // BRUTO
  peso_final: number     // TARA
  peso_neto: number      // BRUTO - TARA = peso_inicial - peso_final
  sacos: number | null
  granel: boolean
  numero_ticket: string
  fecha_inicio: string | null
  fecha_fin: string | null
}

export interface LoteCrear {
  tipo_material: string
  pesaje: PesajeCrear
}

export interface LoteEditar {
  tipo_material?: string
  peso_inicial?: number   // BRUTO
  peso_final?: number     // TARA
  sacos?: number | null
  granel?: boolean
}

export interface LoteDetalle {
  id: number
  ip: string
  numero_lote: number
  tipo_material: string | null
  estado: string
  volado: boolean
  peso_neto: number | null
  fecha_pesaje: string | null
  eliminado: boolean
  habilitado_ruma: boolean
  fecha_habilitacion: string | null
  pesaje: PesajeDetalle | null
}

export interface SesionCrear {
  provacop_id: number
  placa: string
  carreta?: string | null
  conductor?: string | null
  transportista?: string | null
  razon_social?: string | null
  guia_remision?: string | null
  guia_transporte?: string | null
}

export interface SesionEditar {
  provacop_id?: number | null
  placa?: string | null
  carreta?: string | null
  conductor?: string | null
  transportista?: string | null
  razon_social?: string | null
  guia_remision?: string | null
  guia_transporte?: string | null
}

export interface SesionLista {
  id: number
  fecha_ingreso: string
  proveedor_razon_social: string
  acopiador_razon_social: string
  es_propio: boolean
  placa: string
  guia_remision: string | null
  total_lotes: number
  lotes_activos: number
  estado: string
}

export interface SesionDetalle {
  id: number
  provacop_id: number
  proveedor_id: number
  proveedor_razon_social: string
  proveedor_ruc: string | null
  acopiador_id: number
  acopiador_razon_social: string
  acopiador_ruc: string | null
  es_propio: boolean
  placa: string
  carreta: string | null
  conductor: string | null
  transportista: string | null
  razon_social: string | null
  guia_remision: string | null
  guia_transporte: string | null
  estado: string
  fecha_ingreso: string
  lotes: LoteDetalle[]
}

export interface SesionesParams {
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  busqueda?: string
}

export interface EliminarLoteRequest {
  motivo: string
}

// ── Llamadas ──────────────────────────────────────────────────────────────────

export const balanzaApi = {
  // Autocomplete para el formulario nueva sesión
  provacops(busqueda?: string): Promise<ProvAcopDropdown[]> {
    return api.get('/balanza/provacop', { params: busqueda ? { busqueda } : {} }).then(r => r.data)
  },

  // Sesiones
  listarSesiones(params?: SesionesParams): Promise<SesionLista[]> {
    return api.get('/balanza', { params }).then(r => r.data)
  },
  crearSesion(datos: SesionCrear): Promise<SesionDetalle> {
    return api.post('/balanza', datos).then(r => r.data)
  },
  obtenerSesion(id: number): Promise<SesionDetalle> {
    return api.get(`/balanza/${id}`).then(r => r.data)
  },
  editarSesion(id: number, datos: SesionEditar): Promise<SesionDetalle> {
    return api.patch(`/balanza/${id}`, datos).then(r => r.data)
  },
  finalizarSesion(id: number): Promise<SesionDetalle> {
    return api.patch(`/balanza/${id}/finalizar`).then(r => r.data)
  },
  pausarSesion(id: number): Promise<SesionDetalle> {
    return api.patch(`/balanza/${id}/pausar`).then(r => r.data)
  },
  reanudarSesion(id: number): Promise<SesionDetalle> {
    return api.patch(`/balanza/${id}/reanudar`).then(r => r.data)
  },

  // Lotes
  agregarLote(sesionId: number, datos: LoteCrear): Promise<LoteDetalle> {
    return api.post(`/balanza/${sesionId}/lotes`, datos).then(r => r.data)
  },
  editarLote(sesionId: number, loteId: number, datos: LoteEditar): Promise<LoteDetalle> {
    return api.patch(`/balanza/${sesionId}/lotes/${loteId}`, datos).then(r => r.data)
  },
  eliminarLote(sesionId: number, loteId: number, datos: EliminarLoteRequest): Promise<void> {
    return api.delete(`/balanza/${sesionId}/lotes/${loteId}`, { data: datos }).then(() => undefined)
  },

  // Ticket PDF — retorna Blob para descarga con auth
  async ticketBlob(sesionId: number, loteId: number): Promise<Blob> {
    const r = await api.get(`/balanza/${sesionId}/lotes/${loteId}/ticket`, {
      responseType: 'blob',
    })
    return r.data
  },

  async ticketsSesionBlob(sesionId: number): Promise<Blob> {
    const r = await api.get(`/balanza/${sesionId}/tickets`, { responseType: 'blob' })
    return r.data
    },

  async ticketPreviewBlob(sesionId: number, loteId: number): Promise<string> {
    // Descarga el HTML autenticado y retorna un object URL para abrir en pestaña
    const r = await api.get(`/balanza/${sesionId}/lotes/${loteId}/ticket/preview`, {
      responseType: 'blob',
    })
    return URL.createObjectURL(new Blob([r.data], { type: 'text/html' }))
    },
}
