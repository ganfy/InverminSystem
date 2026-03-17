import { defineStore } from 'pinia'
import { ref } from 'vue'
import { balanzaApi } from '@/api/balanza'
import type {
  SesionLista,
  SesionDetalle,
  SesionCrear,
  SesionEditar,
  LoteCrear,
  LoteEditar,
  ProvAcopDropdown,
  SesionesParams,
  LoteDetalle,
} from '@/api/balanza'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'
import {
  siguienteIP,
  bloqueAgotado,
  encolarSesion,
  obtenerProvacops,
  obtenerSesionesPendientes,
  type SesionOfflineData,
  type LoteOfflineData,
} from '@/composables/useOfflineQueue'

const FORCE_OFFLINE = import.meta.env.VITE_FORCE_OFFLINE === 'true'

export const useBalanzaStore = defineStore('balanza', () => {
  const ui = useUiStore()

  const sesiones      = ref<SesionLista[]>([])
  const sesionActual  = ref<SesionDetalle | null>(null)
  const provacops     = ref<ProvAcopDropdown[]>([])
  const loading       = ref(false)
  const loadingSesion = ref(false)
  const guardando     = ref(false)


  function generarOfflineId(): string {
    return `offline-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
  }

  // ── Autocomplete ───────────────────────────────────────────
  async function cargarProvacops(busqueda?: string) {
    try {
      provacops.value = await balanzaApi.provacops(busqueda)
    } catch {
      ui.toast('Error al cargar proveedores', 'error')
    }
  }

  // ── Sesiones ───────────────────────────────────────────────
  async function cargarSesiones(params?: SesionesParams) {
    loading.value = true
    try {
      sesiones.value = await balanzaApi.listarSesiones(params)
    } catch {
      ui.toast('Error al cargar sesiones', 'error')
    } finally {
      loading.value = false
    }
  }

  async function cargarSesion(id: number) {
    loadingSesion.value = true
    try {
      sesionActual.value = await balanzaApi.obtenerSesion(id)
    } catch {
      ui.toast('Error al cargar sesión', 'error')
    } finally {
      loadingSesion.value = false
    }
  }

  async function crearSesion(datos: SesionCrear): Promise<SesionDetalle | null> {
    // ── Online: flujo normal ──────────────────────────────────
    if (!FORCE_OFFLINE && navigator.onLine) {
      guardando.value = true
      try {
        const resp = await balanzaApi.crearSesion(datos)
        sesionActual.value = resp
        return resp
      } catch (err: any) {
        ui.toast(err?.response?.data?.detail ?? 'Error al crear sesión', 'error')
        return null
      } finally {
        guardando.value = false
      }
    }

    // ── Offline: guardar en IndexedDB ─────────────────────────
    // Verificar caché de provacops para validar entidad-rol
    const provacops = await obtenerProvacops()
    const provacop = provacops.find(p => p.provacop_id === datos.provacop_id)
    if (!provacop) {
      ui.toast('No hay datos de proveedor en caché offline. Sincroniza primero.', 'error')
      return null
    }

    const offlineId = generarOfflineId()
    const ahora = new Date().toISOString()

    const sesionOffline: SesionOfflineData = {
      offline_id: offlineId,
      provacop_id: datos.provacop_id,
      placa: datos.placa,
      carreta: datos.carreta ?? null,
      conductor: datos.conductor ?? null,
      transportista: datos.transportista ?? null,
      razon_social: datos.razon_social ?? null,
      guia_remision: datos.guia_remision ?? null,
      guia_transporte: datos.guia_transporte ?? null,
      estado: 'EN_PROCESO',
      creado_en: ahora,
      lotes: [],
      synced: false,
      sync_error: null,
    }

    await encolarSesion(sesionOffline)

    // Construir objeto "optimista" para el UI — sin server_id real
    const sesionOptimista: SesionDetalle = {
      id: -1, // ID temporal, se reemplaza al sync
      offline_id: offlineId,
      provacop_id: datos.provacop_id,
      proveedor_razon_social: provacop.proveedor_razon_social,
      proveedor_ruc: provacop.proveedor_ruc,
      acopiador_razon_social: provacop.acopiador_razon_social,
      acopiador_ruc: provacop.acopiador_ruc,
      es_propio: provacop.es_propio,
      placa: datos.placa,
      carreta: datos.carreta ?? null,
      conductor: datos.conductor ?? null,
      transportista: datos.transportista ?? null,
      razon_social: datos.razon_social ?? null,
      guia_remision: datos.guia_remision ?? null,
      guia_transporte: datos.guia_transporte ?? null,
      estado: 'EN_PROCESO',
      fecha_ingreso: ahora,
      lotes: [],
      proveedor_id: 0,
      acopiador_id: 0
    }

    sesionActual.value = sesionOptimista
    ui.toast('Sin red — sesión guardada localmente. Se sincronizará al reconectar.', 'warning')
    return sesionOptimista
  }

  async function editarSesion(id: number, datos: SesionEditar): Promise<boolean> {
    guardando.value = true
    try {
      sesionActual.value = await balanzaApi.editarSesion(id, datos)
      ui.toast('Sesión actualizada', 'success')
      return true
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al editar sesión', 'error')
      return false
    } finally {
      guardando.value = false
    }
  }

  async function finalizarSesion(id: number) {
    guardando.value = true
    try {
      sesionActual.value = await balanzaApi.finalizarSesion(id)
      ui.toast('Sesión finalizada', 'success')
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al finalizar', 'error')
    } finally {
      guardando.value = false
    }
  }

  async function pausarSesion(id: number) {
    try {
      sesionActual.value = await balanzaApi.pausarSesion(id)
      ui.toast('Sesión pausada', 'warning')
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al pausar', 'error')
    }
  }

  async function reanudarSesion(id: number) {
    try {
      sesionActual.value = await balanzaApi.reanudarSesion(id)
      ui.toast('Sesión reanudada', 'info')
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al reanudar', 'error')
    }
  }

  // ── Lotes ──────────────────────────────────────────────────
  async function agregarLote(
    sesionId: number,
    datos: LoteCrear,
  ): Promise<LoteDetalle | null> {

    // ── Online: flujo normal ──────────────────────────────────
    if (!FORCE_OFFLINE && navigator.onLine && sesionId > 0) {
      guardando.value = true
      try {
        const lote = await balanzaApi.agregarLote(sesionId, datos)
        if (sesionActual.value) {
          sesionActual.value.lotes.push(lote)
        }
        return lote
      } catch (err: any) {
        ui.toast(err?.response?.data?.detail ?? 'Error al agregar lote', 'error')
        return null
      } finally {
        guardando.value = false
      }
    }

    // ── Offline (o sesión offline sin server_id) ──────────────
    const agotado = await bloqueAgotado()
    if (agotado) {
      ui.toast('Bloque de IPs agotado. Necesitas conexión para renovar.', 'error')
      return null
    }

    const ip = await siguienteIP()
    if (!ip) {
      ui.toast('No hay IPs disponibles offline.', 'error')
      return null
    }

    const offlineId = generarOfflineId()
    const ahora = new Date().toISOString()
    const numeroLote = (sesionActual.value?.lotes.filter(l => !l.eliminado).length ?? 0) + 1

    const loteOffline: LoteOfflineData = {
      offline_id: offlineId,
      ip,
      numero_lote: numeroLote,
      tipo_material: datos.tipo_material,
      pesaje: {
        peso_inicial: datos.pesaje.peso_inicial,
        peso_final: datos.pesaje.peso_final,
        sacos: datos.pesaje.sacos ?? null,
        granel: datos.pesaje.granel ?? false,
        fecha_inicio: datos.pesaje.fecha_inicio ?? ahora,
        fecha_fin: ahora,
      },
      creado_en: ahora,
    }

    // Agregar el lote a la sesión offline en IndexedDB
    if (sesionActual.value?.offline_id) {
      const pendientes = await obtenerSesionesPendientes()
      const sesionLocal = pendientes.find(s => s.offline_id === sesionActual.value!.offline_id)
      if (sesionLocal) {
        sesionLocal.lotes.push(loteOffline)
        await encolarSesion(sesionLocal)
      }
    }

    // Objeto optimista para el UI
    const loteOptimista: LoteDetalle = {
      id: -1,
      ip,
      numero_lote: numeroLote,
      tipo_material: datos.tipo_material,
      estado: 'RECEPCIONADO',
      volado: false,
      eliminado: false,
      habilitado_ruma: false,
      peso_neto: datos.pesaje.peso_inicial - datos.pesaje.peso_final,
      pesaje: {
        id: -1,
        peso_inicial: datos.pesaje.peso_inicial,
        peso_final: datos.pesaje.peso_final,
        peso_neto: datos.pesaje.peso_inicial - datos.pesaje.peso_final,
        sacos: datos.pesaje.sacos ?? null,
        granel: datos.pesaje.granel ?? false,
        numero_ticket: `TK-OFFLINE-${ip}`,
        fecha_inicio: ahora,
        fecha_fin: ahora,
      },
      fecha_pesaje: null,
      fecha_habilitacion: null
    }

    if (sesionActual.value) {
      sesionActual.value.lotes.push(loteOptimista)
    }

    ui.toast(`Lote ${ip} guardado localmente — sin red.`, 'warning')
    return loteOptimista
  }

  async function editarLote(
    sesionId: number,
    loteId: number,
    datos: LoteEditar,
  ): Promise<boolean> {
    guardando.value = true
    try {
      await balanzaApi.editarLote(sesionId, loteId, datos)
      await cargarSesion(sesionId)
      ui.toast('Lote actualizado', 'success')
      return true
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al editar lote', 'error')
      return false
    } finally {
      guardando.value = false
    }
  }

  async function eliminarLote(sesionId: number, loteId: number, motivo: string): Promise<boolean> {
    guardando.value = true
    try {
      await balanzaApi.eliminarLote(sesionId, loteId, { motivo })
      await cargarSesion(sesionId)
      ui.toast('Lote eliminado', 'warning')
      return true
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al eliminar lote', 'error')
      return false
    } finally {
      guardando.value = false
    }
  }

  async function descargarTicket(sesionId: number, loteId: number, ip: string) {
    try {
      const blob = await balanzaApi.ticketBlob(sesionId, loteId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ticket-${ip}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch {
      ui.toast('Error al generar ticket PDF', 'error')
    }
  }

   async function descargarTicketsSesion(sesionId: number) {
    try {
      const blob = await balanzaApi.ticketsSesionBlob(sesionId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `tickets-sesion-${sesionId}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch {
      ui.toast('Error al generar PDF de tickets', 'error')
    }
  }

  return {
    sesiones, sesionActual, provacops,
    loading, loadingSesion, guardando,
    cargarProvacops, cargarSesiones, cargarSesion,
    crearSesion, editarSesion,
    finalizarSesion, pausarSesion, reanudarSesion,
    agregarLote, editarLote, eliminarLote, descargarTicket,
    descargarTicketsSesion,
  }
})
