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
} from '@/api/balanza'
import { useUiStore } from '@/stores/ui'

export const useBalanzaStore = defineStore('balanza', () => {
  const ui = useUiStore()

  const sesiones      = ref<SesionLista[]>([])
  const sesionActual  = ref<SesionDetalle | null>(null)
  const provacops     = ref<ProvAcopDropdown[]>([])
  const loading       = ref(false)
  const loadingSesion = ref(false)
  const guardando     = ref(false)

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
    guardando.value = true
    try {
      const sesion = await balanzaApi.crearSesion(datos)
      ui.toast('Sesión creada', 'success')
      return sesion
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al crear sesión', 'error')
      return null
    } finally {
      guardando.value = false
    }
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
  async function agregarLote(sesionId: number, datos: LoteCrear): Promise<boolean> {
    guardando.value = true
    try {
      const lote = await balanzaApi.agregarLote(sesionId, datos)
      await cargarSesion(sesionId)
      ui.toast(`Lote ${lote.ip} registrado`, 'success')
      return true
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al agregar lote', 'error')
      return false
    } finally {
      guardando.value = false
    }
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
