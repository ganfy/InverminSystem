<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Pruebas Metalúrgicas</h1>
        <p class="page-subtitle">Gestión y registro de análisis de preparación</p>
      </div>
    </header>

    <!-- Offline queue -->
    <div v-if="pruebasOffline.length > 0" class="offline-section">
      <div class="offline-section-header">
        <span class="offline-section-titulo">
          <WifiOff :size="20" style="vertical-align:middle;margin-right:5px" /> SIN SINCRONIZAR
        </span>
        <span class="offline-section-count">{{ pruebasOffline.length }} prueba(s) local(es)</span>
      </div>
      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>IP</th>
              <th>Fecha Registro Local</th>
              <th>Malla (%)</th>
              <th>Gasto AgNO3</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pruebasOffline" :key="p.offline_id" class="fila-offline">
              <td class="td-mono" style="color:var(--color-gold)">{{ p.ip }}</td>
              <td class="td-fecha">{{ fmtLocal(p.datos.fecha_ingreso) }}</td>
              <td class="td-mono">{{ p.datos.malla_porcentaje?.toFixed(3) ?? '---' }}</td>
              <td class="td-mono">{{ p.datos.gasto_agno3?.toFixed(3) ?? '---' }}</td>
              <td>
                <span class="badge-estado pendiente">PENDIENTE</span>
                <span class="badge-local" v-if="p.sync_error" :title="p.sync_error" style="color:#dc3c3c">ERROR</span>
                <span class="badge-local" v-else>LOCAL</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filtros-bar">
      <div class="field" style="min-width:180px">
        <label class="field-label">Estado</label>
        <select class="field-select field-sm field-input" v-model="filtroEstado">
          <option value="Todos">Todos los estados</option>
          <option value="PENDIENTE">PENDIENTE</option>
          <option value="EN PROCESO">EN PROCESO</option>
          <option value="COMPLETADO">COMPLETADO</option>
        </select>
      </div>
      <div class="field" style="flex:1">
        <label class="field-label">Búsqueda</label>
        <input type="text" class="field-input" v-model="filtroBusqueda" placeholder="Buscar por IP, CIP..." />
      </div>
    </div>

    <!-- Tabla principal -->
    <div v-if="cargando && pruebas.length === 0" class="estado-tabla">
      <span class="spinner"></span> Cargando pruebas metalúrgicas...
    </div>
    <div v-else class="tabla-wrapper">
      <table class="tabla">
        <thead>
          <tr>
            <th>IP</th>
            <th>FECHA RECEPCIÓN</th>
            <th>INGRESO A RODILLOS</th>
            <th>FIN PROYECTADO</th>
            <th>MALLA (%)</th>
            <th>CIP RECUPERACIÓN</th>
            <th>ESTADO</th>
            <th>ACCIONES</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="prueba in pruebasFiltradas" :key="prueba.ip">
            <td class="td-mono" style="color:var(--color-gold)">{{ prueba.ip }}</td>
            <td class="td-fecha">{{ fmt(prueba.fecha_recepcion) }}</td>
            <td class="td-fecha">{{ fmt(prueba.fecha_ingreso) }}</td>
            <td class="td-mono" style="color:var(--color-gold-light)">
              {{ fmt(prueba.fecha_salida) }}
            </td>
            <td class="td-mono">{{ prueba.malla_porcentaje?.toFixed(1) ?? '---' }}</td>
            <!-- CIP de recuperación -->
            <td>
              <span v-if="prueba.cip_asignado" class="td-mono" style="color:var(--color-gold);font-size:0.8rem">
                {{ prueba.cip_asignado }}
              </span>
              <span v-else class="badge-estado pendiente" style="font-size:0.65rem">Sin CIP</span>
            </td>
            <td>
              <span class="badge-estado" :class="estadoClase(prueba.estado)">
                {{ prueba.estado }}
              </span>
            </td>
            <td class="td-acciones">
              <!-- Registrar / Ver prueba -->
              <button
                class="btn-primary"
                style="font-size:0.75rem;padding:0.3rem 0.75rem"
                :disabled="estadoBotonRegistrar(prueba).disabled"
                @click="irARegistrar(prueba.ip)"
              >
                {{ estadoBotonRegistrar(prueba).texto }}
              </button>

              <!-- Etiquetar: solo cuando COMPLETADO y sin CIP aún -->
              <button
                v-if="prueba.estado === 'COMPLETADO' && !prueba.etiquetado"
                class="btn-secondary"
                style="font-size:0.75rem;padding:0.3rem 0.75rem"
                :disabled="etiquetando === prueba.ip"
                @click="etiquetar(prueba.ip)"
                title="Generar CIP de recuperación para laboratorio"
              >
                <span v-if="etiquetando === prueba.ip" class="spinner" style="margin-right:0.3rem"></span>
                Etiquetar
              </button>

              <!-- Ver CIP (ya etiquetado) -->
              <button
                v-if="prueba.etiquetado"
                class="btn-secondary"
                style="font-size:0.75rem;padding:0.3rem 0.75rem"
                @click="verEtiqueta(prueba)"
                title="Ver etiqueta CIP"
              >
                🏷 Reimprimir
              </button>
            </td>
          </tr>
          <tr v-if="pruebasFiltradas.length === 0">
            <td colspan="8" class="estado-tabla sin-datos">Sin pruebas registradas</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal etiqueta CIP (impresión) -->
    <div v-if="etiquetaModal" class="modal-overlay" @click.self="etiquetaModal = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Etiqueta CIP Recuperación</h2>
          <button class="btn-cerrar" @click="etiquetaModal = null">×</button>
        </div>
        <div class="modal-body" style="text-align:center">
          <p class="field-label" style="margin-bottom:0.5rem">LOTE: {{ etiquetaModal.ip }}</p>
          <div class="etiqueta-cip">
            <span class="etiqueta-title">INVERMIN PAITITI S.A.C. — RECUPERACIÓN</span>
            <div :id="`barcode-prueba`" class="barcode-container"></div>
            <span class="etiqueta-codigo">{{ etiquetaModal.cip }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="etiquetaModal = null">Cerrar</button>
          <button class="btn-primary" @click="imprimirEtiqueta(etiquetaModal)">Imprimir</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { pruebasApi, type LotePruebaList } from '@/api/pruebas'
import { useSync } from '@/composables/useSync'
import { obtenerPruebasPendientes, type PruebaQueueData } from '@/composables/useOfflineQueue'
import { WifiOff } from 'lucide-vue-next'
import JsBarcode from 'jsbarcode'

const router  = useRouter()
const ui      = useUiStore()
const { pendientes, online, ultimoSync } = useSync()

const pruebas       = ref<LotePruebaList[]>([])
const pruebasOffline = ref<PruebaQueueData[]>([])
const cargando      = ref(false)
const etiquetando   = ref<string | null>(null)   // IP en proceso de etiquetado
const etiquetaModal = ref<{ ip: string; cip: string } | null>(null)

const filtroEstado   = ref('Todos')
const filtroBusqueda = ref('')

// ── Watchers ──────────────────────────────────────────────────────────────────
watch(pendientes, async (nuevo, viejo) => {
  await cargarOffline()
  if (nuevo === 0 && (viejo ?? 0) > 0) await cargarDatos()
})
watch(ultimoSync, async () => {
  await cargarDatos()
  await cargarOffline()
})
watch(online, async (isOnline) => {
  if (isOnline) {
    await new Promise(r => setTimeout(r, 300))
    const hay = (await obtenerPruebasPendientes()).length
    if (hay === 0) { await cargarDatos(); await cargarOffline() }
  } else {
    await cargarOffline()
  }
})

// ── Carga ─────────────────────────────────────────────────────────────────────
async function cargarOffline() {
  try {
    const pend = await obtenerPruebasPendientes()
    pruebasOffline.value = pend.filter(p => !p.synced)
  } catch { /* silencioso */ }
}

async function cargarDatos() {
  if (cargando.value) return
  cargando.value = true
  try {
    const data = await pruebasApi.obtenerListaPruebas()
    pruebas.value = Array.isArray(data) ? data : []
  } catch (err: any) {
    console.error('Error cargando pruebas:', err)
    if (online.value && err?.response?.status !== 403) ui.toast('Error al conectar con el servidor', 'error')
    pruebas.value = []
  } finally {
    cargando.value = false
  }
}

onMounted(async () => {
  await cargarDatos()
  await cargarOffline()
})

// ── Filtros ───────────────────────────────────────────────────────────────────
const pruebasFiltradas = computed(() => {
  const estaOffline = new Set(pruebasOffline.value.map(p => p.ip))
  return pruebas.value.filter(p => {
    if (estaOffline.has(p.ip)) return false
    if (filtroEstado.value !== 'Todos' && p.estado !== filtroEstado.value) return false
    const q = filtroBusqueda.value.toLowerCase()
    if (q && !p.ip.toLowerCase().includes(q) && !(p.cip_asignado ?? '').toLowerCase().includes(q)) return false
    return true
  })
})

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(d: string | null | undefined) {
  if (!d) return '---'
  const utc = (d.includes('+') || d.endsWith('Z')) ? d : d + 'Z'
  return new Date(utc).toLocaleString('es-PE', {
    timeZone: 'America/Lima', day: '2-digit', month: '2-digit',
    year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function fmtLocal(d: string) {
  try { return new Date(d).toLocaleString('es-PE', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) }
  catch { return '---' }
}

function estadoClase(estado: string) {
  return { PENDIENTE: 'pendiente', 'EN PROCESO': 'en-proceso', COMPLETADO: 'completo' }[estado] ?? ''
}

function estadoBotonRegistrar(p: LotePruebaList) {
  if (!p.fecha_ingreso) return { texto: 'Iniciar Prueba', disabled: false }
  if (p.estado === 'EN PROCESO') {
    const h = calcularHorasRestantes(p.fecha_ingreso)
    return { texto: `Rodando... (${h}h rest.)`, disabled: true }
  }
  return { texto: 'Ver / Editar', disabled: false }
}

function calcularHorasRestantes(fechaIngreso: string): number {
  const utc = (fechaIngreso.includes('+') || fechaIngreso.endsWith('Z')) ? fechaIngreso : fechaIngreso + 'Z'
  const salida = new Date(new Date(utc).getTime() + 48 * 3600000)
  return Math.max(0, Math.ceil((salida.getTime() - Date.now()) / 3600000))
}

// ── Acciones ──────────────────────────────────────────────────────────────────
function irARegistrar(ip: string) {
  router.push({ name: 'RegistrarPrueba', params: { ip } })
}

async function etiquetar(ip: string) {
  if (!online.value) {
    ui.toast('Se requiere conexión para generar la etiqueta CIP', 'warning')
    return
  }
  etiquetando.value = ip
  try {
    const resultado = await pruebasApi.etiquetar(ip)
    ui.toast(`CIP ${resultado.cip} generado para ${ip}`, 'success')
    // Actualizar la lista localmente
    const p = pruebas.value.find(x => x.ip === ip)
    if (p) { p.cip_asignado = resultado.cip; p.etiquetado = true }
    // Mostrar modal de etiqueta
    etiquetaModal.value = { ip, cip: resultado.cip }
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al etiquetar', 'error')
  } finally {
    etiquetando.value = null
  }
}

function verEtiqueta(prueba: LotePruebaList) {
  if (prueba.cip_asignado) {
    etiquetaModal.value = { ip: prueba.ip, cip: prueba.cip_asignado }
  }
}

function imprimirEtiqueta(e: { ip: string; cip: string }) {
  const css = `
    body { font-family: monospace; display:flex; align-items:center; }
    .et { border:2px dashed #333; border-radius:8px; padding:12px 18px; text-align:center; width:80%; }
    .et-title { font-size:0.65rem; font-weight:900; letter-spacing:.1em; display:block; margin-bottom:4px; }
    .et-sub { font-size:0.55rem; border-bottom:1px solid #000; padding-bottom:4px; display:block; width:100%; text-align:center; }
    .et-code { font-size:2rem; font-weight:900; margin-top:8px; display:block; }
  `
  const html = `<!DOCTYPE html><html><head><style>${css}</style></head><body>
    <div class="et">
      <span class="et-title">INVERMIN PAITITI S.A.C.</span>
      <span class="et-sub">RECUPERACIÓN</span>
      <span class="et-code">${e.cip}</span>
    </div>
    <script>window.addEventListener('load',()=>setTimeout(()=>window.print(),200))<\/script>
  </body></html>`
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 60000)
}
</script>

<style scoped>
.filtros-bar {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

/* ── Offline section ─────────────────────────────────── */
.offline-section {
  border: 1px solid rgba(245,158,11,.4);
  border-radius: var(--radius-md);
  margin-bottom: 1.25rem;
  overflow: hidden;
}
.offline-section-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: .55rem 1rem;
  background: rgba(245,158,11,.1);
  border-bottom: 1px solid rgba(245,158,11,.3);
}
.offline-section-titulo { font-family: var(--font-mono); font-size: var(--text-sm); letter-spacing: .18em; color: #f59e0b; }
.offline-section-count  { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted); }
.fila-offline { background: rgba(245,158,11,.04); }
.badge-local {
  font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: .1em;
  background: rgba(245,158,11,.15); color: #f59e0b;
  border: 1px solid rgba(245,158,11,.3); border-radius: 3px;
  padding: 1px 5px; margin-left: .4rem; vertical-align: middle;
}

/* ── Badges ──────────────────────────────────────────── */
.badge-estado { padding: .25rem .6rem; border-radius: var(--radius-sm); font-size: var(--text-xs); font-weight: bold; font-family: var(--font-mono); letter-spacing: .05em; text-transform: uppercase; white-space: nowrap; }
.pendiente   { background: rgba(220,60,60,.1);  color: var(--color-error);   border: 1px solid rgba(220,60,60,.3); }
.en-proceso  { background: rgba(220,160,20,.1); color: var(--color-warning); border: 1px solid rgba(220,160,20,.3); }
.completo    { background: rgba(60,180,80,.1);  color: var(--color-success); border: 1px solid rgba(60,180,80,.3); }

/* ── Etiqueta CIP (modal) ────────────────────────────── */
.etiqueta-cip {
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: #fff;
  color: #000;
  min-width: 200px;
}
.etiqueta-title { font-size: 0.6rem; font-weight: 900; letter-spacing: .1em; }
.etiqueta-codigo { font-family: var(--font-mono); font-size: 1.1rem; font-weight: 900; }
.barcode-container { height: 40px; }
</style>
