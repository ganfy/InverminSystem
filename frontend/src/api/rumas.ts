import api from './axios'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface CampanaOut {
    id: number
    codigo: string
    meta_oro_fino: number
    fecha_inicio: string
    fecha_cierre: string | null
    estado: 'ACTIVA' | 'CERRADA'
    oro_fino_acumulado: number
    total_lotes: number
    total_toneladas: number
    total_rumas: number
    progreso_pct: number
    dias_transcurridos: number | null
    rumas?: RumaLista[]
}

export interface RumaLista {
    id: number
    codigo: string
    numero_ruma: number
    fecha_creacion: string
    estado: 'ABIERTA' | 'CERRADA'
    total_lotes: number
    total_tms: number
    ley_ponderada: number | null
    rec_promedio: number | null
    pct_llampo: number | null
    asignada: boolean
}

export interface LoteRumaItem {
    ip: string
    proveedor: string
    tmh: number
    tms: number | null
    ley_avg: number | null
    rec_porc: number | null
    tipo_material: string | null
    habilitado_ruma: boolean
    volado: boolean
}

export interface RumaOut extends RumaLista {
    lotes: LoteRumaItem[]
    pct_llampo: number | null
}

export interface LoteDisponibleOut {
    ip: string
    proveedor: string
    acopiador: string | null
    tmh: number
    tms: number | null
    ley_avg: number | null
    rec_porc: number | null
    tipo_material: string | null
    volado: boolean
    dias_almacen: number
}

// ── Campañas ──────────────────────────────────────────────────────────────────

export const getCampanaActiva = () =>
    api.get<CampanaOut>('/campanas/activa')

export const getCampanas = () =>
    api.get<CampanaOut[]>('/campanas')

export const crearCampana = (meta_oro_fino: number) =>
    api.post<CampanaOut>('/campanas', { meta_oro_fino })

export const cerrarCampana = (id: number, meta_oro_fino_nueva: number) =>
    api.patch<CampanaOut>(`/campanas/${id}/cerrar`, { meta_oro_fino_nueva })

export const editarMetaCampana = (id: number, meta_oro_fino: number) =>
    api.patch<CampanaOut>(`/campanas/${id}/meta`, { meta_oro_fino })

// ── Rumas ─────────────────────────────────────────────────────────────────────

export const getRumas = () =>
    api.get<RumaLista[]>('/rumas')

export const crearRuma = () =>
    api.post<RumaOut>('/rumas')

export const getRuma = (id: number) =>
    api.get<RumaOut>(`/rumas/${id}`)

export const getLotesDisponibles = () =>
    api.get<LoteDisponibleOut[]>('/rumas/lotes-disponibles')

export const asignarLotes = (rumaId: number, ips: string[]) =>
    api.put<RumaOut>(`/rumas/${rumaId}/lotes`, { ips })

export const cerrarRuma = (id: number) =>
    api.patch<RumaOut>(`/rumas/${id}/cerrar`)

export const habilitarLote = (ip: string, motivo?: string) =>
    api.patch(`/lotes/${ip}/habilitar-ruma`, { motivo: motivo ?? null })

export function asignarRumaACampana(campanaId: number, rumaId: number) {
    return api.post(`/campanas/${campanaId}/rumas/${rumaId}`)
  }
