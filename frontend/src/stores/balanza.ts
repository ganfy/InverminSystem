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
import { useAuthStore } from '@/stores/auth'
import {
  siguienteIP,
  bloqueAgotado,
  encolarSesion,
  siguienteTK,
  bloqueTKAgotado,
  obtenerProvacops,
  obtenerSesionesPendientes,
  encolarLoteOnline,
  contarLotesOnlinePendientes,
  obtenerLotesOnlinePendientes,
  obtenerTodosLotesOnline,
  eliminarLoteOnline,
  limpiarLotesOnlineSynced,
  encolarFinalizacion,
  type SesionOfflineData,
  type LoteOfflineData,
  type LoteOnlineData,
} from '@/composables/useOfflineQueue'
import { _TICKET_CSS, _TICKET_CSS_MULTI } from './_TICKET_CSS'

const FORCE_OFFLINE = import.meta.env.VITE_FORCE_OFFLINE === 'true'

// ── Helpers privados ───────────────────────────────────────

function esOfflineId(id: number | string): boolean {
  return typeof id === 'string' && id.startsWith('offline-')
}

function estamosOffline(): boolean {
  return FORCE_OFFLINE || !navigator.onLine
}

function loteOfflineADetalle(lote: LoteOfflineData): LoteDetalle {
  const pesoNeto = lote.pesaje.peso_inicial - lote.pesaje.peso_final
  return {
    id: -1,
    ip: lote.ip,
    numero_lote: lote.numero_lote,
    tipo_material: lote.tipo_material,
    estado: 'RECEPCIONADO',
    volado: false,
    eliminado: false,
    habilitado_ruma: false,
    peso_neto: pesoNeto,
    pesaje: {
      id: -1,
      peso_inicial: lote.pesaje.peso_inicial,
      peso_final: lote.pesaje.peso_final,
      peso_neto: pesoNeto,
      sacos: lote.pesaje.sacos,
      granel: lote.pesaje.granel,
      numero_ticket: lote.numero_ticket,
      fecha_inicio: lote.pesaje.fecha_inicio,
      fecha_fin: lote.pesaje.fecha_fin,
    },
    fecha_pesaje: null,
    fecha_habilitacion: null,
  }
}

function loteOnlineADetalle(lote: LoteOnlineData): LoteDetalle {
  const pesoNeto = lote.pesaje.peso_inicial - lote.pesaje.peso_final
  return {
    id: -1,
    ip: lote.ip,
    numero_lote: lote.numero_lote,
    tipo_material: lote.tipo_material,
    estado: 'RECEPCIONADO',
    volado: false,
    eliminado: false,
    habilitado_ruma: false,
    peso_neto: pesoNeto,
    pesaje: {
      id: -1,
      peso_inicial: lote.pesaje.peso_inicial,
      peso_final: lote.pesaje.peso_final,
      peso_neto: pesoNeto,
      sacos: lote.pesaje.sacos,
      granel: lote.pesaje.granel,
      numero_ticket: lote.numero_ticket,
      fecha_inicio: lote.pesaje.fecha_inicio,
      fecha_fin: lote.pesaje.fecha_fin,
    },
    fecha_pesaje: null,
    fecha_habilitacion: null,
    local_only: !lote.synced,
  }
}

// ── Ticket HTML — replica ticket_balanza.html del servidor ─

function _fmtPeso(v: number | null | undefined): string {
  return v != null ? Number(v).toFixed(3) : '-'
}

function _fmtFecha(iso: string | null | undefined): string {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  }).replace(',', '')
}

function _ticketCuerpo(lote: LoteDetalle, s: SesionDetalle): string {
  const obs = [
    lote.ip,
    `LOTE-${lote.numero_lote}`,
    lote.pesaje?.granel
      ? 'GRANEL'
      : (lote.pesaje?.sacos ? `${lote.pesaje.sacos} SACOS` : ''),
  ].filter(Boolean).join(' | ')

  const acopHtml = (!s.es_propio && s.acopiador_razon_social)
    ? `<tr><td class="lbl">Acopiador</td><td class="sep">:</td><td>${s.acopiador_razon_social}</td></tr>`
    : ''

  return `<div class="ticket-page">
<div class="emp-nombre">INVERMIN PAITITI S.A.C.</div>
<div class="emp-sub">Planta El Dorado</div>
<div class="emp-sub">R.U.C. 20601910587</div>
<div class="hr"></div>
<table class="fila-placa"><tr>
  <td class="td-placa">Placa : ${s.placa} &nbsp;&nbsp; Carreta : ${s.carreta || '0'}</td>
  <td class="td-ticket">Ticket : ${lote.pesaje?.numero_ticket ?? lote.ip}</td>
</tr></table>
<div class="hr"></div>
<table class="datos">
  <tr><td class="lbl">Conductor</td><td class="sep">:</td><td>${s.conductor || '-'}</td></tr>
  <tr><td class="lbl">Transportista</td><td class="sep">:</td><td>${s.transportista || '-'}</td></tr>
  <tr><td class="lbl">Razon Social</td><td class="sep">:</td><td>${s.razon_social || s.proveedor_razon_social || '-'}</td></tr>
  ${acopHtml}
  <tr><td class="lbl">Producto</td><td class="sep">:</td><td>${lote.tipo_material?.toUpperCase() ?? '-'}</td></tr>
  <tr><td class="lbl">Documento</td><td class="sep">:</td><td>${s.guia_remision || s.guia_transporte || '-'}</td></tr>
  <tr><td class="lbl">Observaciones</td><td class="sep">:</td><td>${obs}</td></tr>
</table>
<div class="hr"></div>
<table class="seccion"><tr>
  <td class="col-fechas">
    <table class="datos">
      <tr><td class="lbl">Fecha Inicial</td><td class="sep">:</td><td>${_fmtFecha(lote.pesaje?.fecha_inicio)}</td></tr>
      <tr><td class="lbl">Fecha Final</td><td class="sep">:</td><td>${_fmtFecha(lote.pesaje?.fecha_fin)}</td></tr>
    </table>
  </td>
  <td class="col-pesos">
    <table class="tabla-pesos">
      <tr><td>Peso Bruto</td><td class="p-sep">:</td><td class="p-val">${_fmtPeso(lote.pesaje?.peso_inicial)}</td><td class="p-unit">TM</td></tr>
      <tr><td>Peso Tara</td><td class="p-sep">:</td><td class="p-val">${_fmtPeso(lote.pesaje?.peso_final)}</td><td class="p-unit">TM</td></tr>
      <tr><td>Peso Neto</td><td class="p-sep">:</td><td class="p-val p-neto">${_fmtPeso(lote.peso_neto)}</td><td class="p-unit">TM</td></tr>
    </table>
  </td>
</tr></table>
</div>`
}


function _abrirVentana(html: string) {
  const blob = new Blob([html], { type: 'text/html; charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const win = window.open(url, '_blank', 'width=950,height=680')
  if (!win) {
    window.open(url, '_blank')
  }
  setTimeout(() => URL.revokeObjectURL(url), 120_000)
}

// ── Store ──────────────────────────────────────────────────

export const useBalanzaStore = defineStore('balanza', () => {
  const ui = useUiStore()
  const auth = useAuthStore()

  const sesiones = ref<SesionLista[]>([])
  const sesionActual = ref<SesionDetalle | null>(null)
  const provacops = ref<ProvAcopDropdown[]>([])
  const loading = ref(false)
  const loadingSesion = ref(false)
  const guardando = ref(false)
  const lotesHybridPendientes = ref<number>(0) //lotes offline de sesiones online

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

  // ── Sesiones online ────────────────────────────────────────
  async function cargarSesiones(params?: SesionesParams) {
    if (estamosOffline()) return  // ← sin red: mantener lo que hay, sin toast de error
    loading.value = true
    try {
      sesiones.value = await balanzaApi.listarSesiones(params)
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al cargar sesiones', 'error')
    } finally {
      loading.value = false
    }
  }

  async function cargarSesion(id: number) {
    loadingSesion.value = true
    try {
      const sesion = await balanzaApi.obtenerSesion(id)
      const ipsServidor = new Set(sesion.lotes.map(l => l.ip))

      // Leer TODOS los lotes locales de esta sesión (synced o no)
      const todosLocales = await obtenerTodosLotesOnline()
      const deEstaSesion = todosLocales.filter(l => l.sesion_id === id)

      for (const lote of deEstaSesion) {
        if (ipsServidor.has(lote.ip)) {
          // El servidor ya lo tiene — limpiar IndexedDB
          await eliminarLoteOnline(lote.offline_id)
        } else {
          // El servidor aún no lo tiene — mostrar como local_only
          sesion.lotes.push(loteOnlineADetalle(lote))
        }
      }

      // Ordenar por numero_lote para presentación consistente
      sesion.lotes.sort((a, b) => a.numero_lote - b.numero_lote)

      sesionActual.value = sesion
      await actualizarLotesHybridPendientes(id)
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al cargar sesión', 'error')
    } finally {
      loadingSesion.value = false
    }
  }

  // ── Sesiones offline ───────────────────────────────────────

  async function cargarSesionOffline(offlineId: string) {
    loadingSesion.value = true
    try {
      // Si ya está en memoria (navegación inmediata post-creación) no releer
      if (sesionActual.value?.offline_id === offlineId) return

      const pendientes = await obtenerSesionesPendientes()
      const sesionLocal = pendientes.find(s => s.offline_id === offlineId)
      if (!sesionLocal) {
        ui.toast('Sesión offline no encontrada', 'error')
        return
      }

      const cache = await obtenerProvacops()
      const provacop = cache.find(p => p.provacop_id === sesionLocal.provacop_id)

      sesionActual.value = {
        id: -1,
        offline_id: offlineId,
        provacop_id: sesionLocal.provacop_id,
        proveedor_razon_social: provacop?.proveedor_razon_social ?? '(sin caché)',
        proveedor_ruc: provacop?.proveedor_ruc ?? '',
        acopiador_razon_social: provacop?.acopiador_razon_social ?? '',
        acopiador_ruc: provacop?.acopiador_ruc ?? null,
        es_propio: provacop?.es_propio ?? false,
        placa: sesionLocal.placa,
        carreta: sesionLocal.carreta,
        conductor: sesionLocal.conductor,
        transportista: sesionLocal.transportista,
        razon_social: sesionLocal.razon_social,
        guia_remision: sesionLocal.guia_remision,
        guia_transporte: sesionLocal.guia_transporte,
        estado: sesionLocal.estado as SesionDetalle['estado'],
        fecha_ingreso: sesionLocal.creado_en,
        lotes: sesionLocal.lotes.map(loteOfflineADetalle),
        proveedor_id: 0,
        acopiador_id: 0,
      }
    } catch (e) {
      console.error('cargarSesionOffline:', e)
      ui.toast('Error al cargar sesión offline', 'error')
    } finally {
      loadingSesion.value = false
    }
  }

  // ── Crear sesión (online/offline) ──────────────────────────
  async function crearSesion(datos: SesionCrear): Promise<SesionDetalle | null> {
    // Online
    if (!estamosOffline()) {
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

    // Offline
    const cache = await obtenerProvacops()
    const provacop = cache.find(p => p.provacop_id === datos.provacop_id)
    if (!provacop) {
      ui.toast('Sin caché de proveedor. Conecta al menos una vez antes de operar offline.', 'error')
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

    const sesionOptimista: SesionDetalle = {
      id: -1,
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
      acopiador_id: 0,
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
    // Verificar lotes híbridos pendientes
    if (!estamosOffline()) {
      const pendientesHybrid = await contarLotesOnlinePendientes(id)
      if (pendientesHybrid > 0) {
        ui.toast(
          `Hay ${pendientesHybrid} lote(s) sin sincronizar. Reconecta para finalizar.`,
          'error'
        )
        return
      }
    }

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

  async function finalizarSesionOffline(sesionIdRaw: string) {
    guardando.value = true
    try {
      if (esOfflineId(sesionIdRaw)) {
        // Sesión 100% offline — marcar en sesiones_q
        const pendientes = await obtenerSesionesPendientes()
        const sesionLocal = pendientes.find(s => s.offline_id === sesionIdRaw)
        if (!sesionLocal) { ui.toast('Sesión offline no encontrada', 'error'); return }
        sesionLocal.estado = 'COMPLETO'
        await encolarSesion(sesionLocal)
        if (sesionActual.value?.offline_id === sesionIdRaw) {
          sesionActual.value = { ...sesionActual.value, estado: 'COMPLETO' }
        }
        ui.toast('Sesión finalizada localmente. Se sincronizará al reconectar.', 'warning')
      } else {
        // Sesión híbrida (ID real, lotes offline) — marcar en memoria + cola
        const sesionId = Number(sesionIdRaw)
        await encolarFinalizacion(sesionId, {
          placa: sesionActual.value?.placa ?? '',
          proveedor_razon_social: sesionActual.value?.proveedor_razon_social ?? '',
          total_lotes: sesionActual.value?.lotes.filter(l => !l.eliminado).length ?? 0,
        })
        if (sesionActual.value) {
          sesionActual.value = { ...sesionActual.value, estado: 'COMPLETO' }
        }
        ui.toast('Sesión finalizada localmente. Se completará en el servidor al reconectar.', 'warning')
      }
    } catch (e) {
      console.error('finalizarSesionOffline:', e)
      ui.toast('Error al finalizar sesión offline', 'error')
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
    sesionId: number | string,
    datos: LoteCrear,
  ): Promise<LoteDetalle | null> {
    const offline = estamosOffline() || esOfflineId(sesionId)

    // Online
    if (!offline) {
      guardando.value = true
      try {
        const lote = await balanzaApi.agregarLote(sesionId as number, datos)
        if (sesionActual.value) sesionActual.value.lotes.push(lote)
        return lote
      } catch (err: any) {
        ui.toast(err?.response?.data?.detail ?? 'Error al agregar lote', 'error')
        return null
      } finally {
        guardando.value = false
      }
    }

    // Offline
    const agotadoIP = await bloqueAgotado()
    if (agotadoIP) {
      ui.toast('Bloque de IPs agotado. Necesitas conexión para renovar.', 'error')
      return null
    }
    const agotadoTK = await bloqueTKAgotado()
    if (agotadoTK) {
      ui.toast('Bloque de tickets agotado. Necesitas conexión para renovar.', 'error')
      return null
    }

    const ip = await siguienteIP()
    if (!ip) { ui.toast('No hay IPs disponibles offline.', 'error'); return null }

    const numeroTicket = await siguienteTK()
    if (!numeroTicket) { ui.toast('No hay tickets disponibles offline.', 'error'); return null }

    const offlineId = generarOfflineId()
    const ahora = new Date().toISOString()
    const numeroLote = (sesionActual.value?.lotes.filter(l => !l.eliminado).length ?? 0) + 1

    const loteOffline: LoteOfflineData = {
      offline_id: offlineId,
      ip,
      numero_lote: numeroLote,
      tipo_material: datos.tipo_material,
      numero_ticket: numeroTicket,    // ← NUEVO
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

    // Persistir en IndexedDB
    const sesionOfflineId = esOfflineId(sesionId)
      ? (sesionId as string)
      : sesionActual.value?.offline_id

    if (sesionOfflineId) {
      const pendientes = await obtenerSesionesPendientes()
      const sesionLocal = pendientes.find(s => s.offline_id === sesionOfflineId)
      if (sesionLocal) {
        sesionLocal.lotes.push(loteOffline)
        await encolarSesion(sesionLocal)
      }
    } else if (typeof sesionId === 'number' && sesionId > 0) {
      // Sesión híbrida: tiene ID real pero estamos offline
      const loteOnline: LoteOnlineData = {
        offline_id: offlineId,
        sesion_id: sesionId,
        tipo_material: datos.tipo_material,
        ip,
        numero_lote: numeroLote,
        numero_ticket: numeroTicket,
        pesaje: {
          peso_inicial: datos.pesaje.peso_inicial,
          peso_final: datos.pesaje.peso_final,
          sacos: datos.pesaje.sacos ?? null,
          granel: datos.pesaje.granel ?? false,
          fecha_inicio: datos.pesaje.fecha_inicio ?? ahora,
          fecha_fin: ahora,
        },
        creado_en: ahora,
        synced: false,
        sync_error: null,
      }
      await encolarLoteOnline(loteOnline)
      await actualizarLotesHybridPendientes(sesionId)
    }

    const loteOptimista = loteOfflineADetalle(loteOffline)
    if (sesionActual.value) sesionActual.value.lotes.push(loteOptimista)

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

  async function eliminarLote(
    sesionId: number,
    loteId: number,
    motivo: string,
  ): Promise<boolean> {
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

  // ── Helper para actualizar el contador
  async function actualizarLotesHybridPendientes(sesionId?: number) {
    lotesHybridPendientes.value = await contarLotesOnlinePendientes(sesionId)
  }

  // ── Tickets online ─────────────────────────────────────────
  async function descargarTicket(sesionId: number, loteId: number, ip: string) {
    try {
      const blob = await balanzaApi.ticketBlob(sesionId, loteId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `ticket-${ip}.pdf`
      document.body.appendChild(a); a.click()
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
      a.href = url; a.download = `tickets-sesion-${sesionId}.pdf`
      document.body.appendChild(a); a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch {
      ui.toast('Error al generar PDF de tickets', 'error')
    }
  }

  // ── Helper HTML de ticket ──────────────────────────────────
  function _buildTicketHtml(css: string, cuerpo: string, titulo: string, autoPrint: boolean): string {
    const script = autoPrint
      ? `<script>window.addEventListener('load',function(){setTimeout(function(){window.print()},250)})<\/script>`
      : ''
    return `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"/><title>${titulo}</title><style>${css}</style></head><body>${cuerpo}${script}</body></html>`
  }

  // ── Tickets unificados (online + offline) ──────────────────

  /** Abre previsualización sin auto-print (botón "Ver") */
  function verTicket(lote: LoteDetalle) {
    if (!sesionActual.value) { ui.toast('No hay sesión activa', 'error'); return }
    _abrirVentana(_buildTicketHtml(_TICKET_CSS, _ticketCuerpo(lote, sesionActual.value), `Ticket ${lote.ip}`, false))
  }

  /** Abre ticket con auto-print (botón "Imprimir") */
  function imprimirTicket(lote: LoteDetalle) {
    if (!sesionActual.value) { ui.toast('No hay sesión activa', 'error'); return }
    _abrirVentana(_buildTicketHtml(_TICKET_CSS, _ticketCuerpo(lote, sesionActual.value), `Ticket ${lote.ip}`, true))
  }

  /** Abre todos los tickets de la sesión en A4 portrait (2 por hoja) con auto-print */
  function imprimirTicketsSesion() {
    const s = sesionActual.value
    if (!s) { ui.toast('No hay sesión activa', 'error'); return }
    const lotes = s.lotes.filter(l => !l.eliminado)
    if (!lotes.length) { ui.toast('Sin lotes para imprimir', 'warning'); return }
    const cuerpos = lotes.map(l => `<div class="ticket">${_ticketCuerpo(l, s)}</div>`).join('\n')
    _abrirVentana(_buildTicketHtml(_TICKET_CSS_MULTI, cuerpos, `Tickets sesión — ${lotes.length} lote(s)`, true))
  }

  // ── Tickets offline ────────────────────────────────────────
  // El HTML replica ticket_balanza.html del servidor (mismo CSS, misma estructura).
  // El IP del bloque reservado es real; el número de ticket usa el IP como
  // referencia hasta que el servidor asigne el TK definitivo al sincronizar.

  function imprimirTicketOffline(lote: LoteDetalle) {
    if (!sesionActual.value) { ui.toast('No hay sesión activa', 'error'); return }
    const html = `<!DOCTYPE html><html lang="es"><head>
    <meta charset="UTF-8"/>
    <title>Ticket ${lote.ip}</title>
    <style>${_TICKET_CSS}</style></head><body>
    ${_ticketCuerpo(lote, sesionActual.value)}
    <script>
      window.addEventListener('load', function() {
        setTimeout(function() { window.print() }, 250)
      })
    <\/script>
    </body></html>`
      _abrirVentana(html)
  }

  function previsualizarTicketOffline(lote: LoteDetalle) {
    if (!sesionActual.value) { ui.toast('No hay sesión activa', 'error'); return }
    // Sin script de print — el usuario lo lanza con Ctrl+P o el botón del navegador
    const html = `<!DOCTYPE html><html lang="es"><head>
    <meta charset="UTF-8"/>
    <title>Preview — Ticket ${lote.ip}</title>
    <style>${_TICKET_CSS}</style></head><body>
    ${_ticketCuerpo(lote, sesionActual.value)}
    </body></html>`
      _abrirVentana(html)
  }

  function imprimirTicketsSesionOffline() {
    const s = sesionActual.value
    if (!s) { ui.toast('No hay sesión activa', 'error'); return }

    const lotes = s.lotes.filter(l => !l.eliminado)
    if (!lotes.length) { ui.toast('Sin lotes para imprimir', 'warning'); return }

    // Los estilos de page-break ya están en _TICKET_CSS bajo @media print
    const cuerpos = lotes.map(l =>
      `<div class="ticket">${_ticketCuerpo(l, s)}</div>`
    )

    const html = `<!DOCTYPE html><html lang="es"><head>
      <meta charset="UTF-8"/>
      <title>Tickets sesión — ${lotes.length} lote(s)</title>
      <style>${_TICKET_CSS}</style></head><body>
      ${cuerpos.join('\n')}
      <script>
        window.addEventListener('load', function() {
          // Pequeño delay para que el navegador termine de renderizar
          setTimeout(function() { window.print() }, 250)
        })
      <\/script>
      </body></html>`
      _abrirVentana(html)
  }

  return {
    // Estado
    sesiones, sesionActual, provacops,
    loading, loadingSesion, guardando,
    lotesHybridPendientes,
    // Autocomplete
    cargarProvacops,
    // Sesiones
    cargarSesiones,
    cargarSesion,
    cargarSesionOffline,
    crearSesion,
    editarSesion,
    finalizarSesion,
    finalizarSesionOffline,
    pausarSesion,
    reanudarSesion,
    // Lotes
    agregarLote,
    editarLote,
    eliminarLote,
    // Tickets
    descargarTicket,
    descargarTicketsSesion,
    imprimirTicketOffline,
    imprimirTicketsSesionOffline,
    previsualizarTicketOffline,
    verTicket,
    imprimirTicket,
    imprimirTicketsSesion,
  }
})
