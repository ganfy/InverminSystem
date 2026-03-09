/**
 * Store Pinia — Módulo Terceros
 * Gestiona estado de lista, carga y operaciones CRUD de proveedores.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import tercerosApi, {
  type AcopiadorDropdown,
  type TerceroCrearPayload,
  type TerceroEditarPayload,
  type TerceroLista,
  type TerceroRespuesta,
} from '@/api/terceros'

export const useTercerosStore = defineStore('terceros', () => {
  // ── State ───────────────────────────────────────────────────────
  const lista        = ref<TerceroLista[]>([])
  const acopiadores  = ref<AcopiadorDropdown[]>([])
  const cargando     = ref(false)
  const error        = ref<string | null>(null)

  // ── Actions ─────────────────────────────────────────────────────
  async function cargar(activo?: boolean) {
    cargando.value = true
    error.value    = null
    try {
      lista.value = await tercerosApi.listar(activo)
    } catch (e: unknown) {
      error.value = (e as Error).message ?? 'Error al cargar terceros'
      throw e
    } finally {
      cargando.value = false
    }
  }

  async function cargarAcopiadores() {
    try {
      acopiadores.value = await tercerosApi.listarAcopiadores()
    } catch {
      // silencioso — no bloquea UI
    }
  }

  async function obtener(id: number): Promise<TerceroRespuesta> {
    return tercerosApi.obtener(id)
  }

  async function crear(datos: TerceroCrearPayload): Promise<TerceroRespuesta> {
    const nuevo = await tercerosApi.crear(datos)
    // Refrescar lista localmente
    lista.value.unshift({
        id:           nuevo.id,
        provacop_id:  nuevo.provacop_id ?? 0,
        razon_social: nuevo.razon_social,
        ruc:          nuevo.ruc,
        referencia:   nuevo.referencia,
        activo:       nuevo.activo,
        acopiador:    nuevo.acopiador?.razon_social ?? null,
        })
    return nuevo
  }

  async function editar(id: number, datos: TerceroEditarPayload): Promise<TerceroRespuesta> {
    const actualizado = await tercerosApi.editar(id, datos)
    const idx = lista.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      lista.value[idx] = {
        ...lista.value[idx],
        id:           actualizado.id,
        provacop_id:  actualizado.provacop_id ?? 0,
        razon_social: actualizado.razon_social,
        ruc:          actualizado.ruc,
        referencia:   actualizado.referencia,
        activo:       actualizado.activo,
        acopiador:    actualizado.acopiador?.razon_social ?? null,
      }
    }
    return actualizado
  }


    async function toggleEstado(id: number, activo: boolean): Promise<TerceroRespuesta> {
        const resultado = activo
            ? await tercerosApi.activar(id)
            : await tercerosApi.desactivar(id)

        const idx = lista.value.findIndex(t => t.id === id)
        if (idx !== -1) {
            const item = lista.value[idx]
            if (item) {
                item.activo = resultado.activo !== undefined ? resultado.activo : activo
            }
        }
        return resultado

    }

  async function parametrosAcopiador(acopiadorId: number) {
    return tercerosApi.parametrosAcopiador(acopiadorId)
  }

   async function eliminar(id: number): Promise<void> {
    await tercerosApi.eliminar(id)
    lista.value = lista.value.filter(t => t.id !== id)
  }

  async function actualizarEnLista(actualizado: TerceroRespuesta) {
    const idx = lista.value.findIndex(t => t.id === actualizado.id)
    if (idx !== -1) {
      lista.value[idx] = {
        ...lista.value[idx],
        id:           actualizado.id,
        provacop_id:  actualizado.provacop_id ?? 0,
        razon_social: actualizado.razon_social,
        ruc:          actualizado.ruc,
        referencia:   actualizado.referencia,
        activo:       actualizado.activo,
        acopiador:    actualizado.acopiador?.razon_social ?? null,
      }
    }
  }

  return {
    lista, acopiadores, cargando, error,
    cargar, cargarAcopiadores, obtener,
    crear, editar, toggleEstado, parametrosAcopiador,
  }
})
