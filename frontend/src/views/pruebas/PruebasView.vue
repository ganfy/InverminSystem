<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-title-row">
        <Beaker class="header-icon" :size="26" />
        <div>
          <h1 class="page-title">Pruebas Metalúrgicas</h1>
          <p class="page-subtitle">Gestión y registro de análisis de preparación</p>
        </div>
      </div>
      <div style="display:flex;gap:0.5rem;align-items:center">
        <button
          class="btn-secondary"
          style="font-size:0.78rem;padding:0.4rem 0.9rem"
          @click="router.push('/pruebas/recuperaciones')"
        >
          Ver Recuperaciones →
        </button>
        <button
          class="btn-refresh"
          @click="cargarDatos"
          :disabled="cargando"
          title="Actualizar datos"
        >
          <RefreshCw :size="20" :class="{ 'spinning': cargando }" />
        </button>
      </div>
    </header>

    <AlertasBanner modulo="PRUEBAS" con-observaciones />

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
        <select class="field-select field-sm field-sm field-input" v-model="filtroEstado">
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
            <th>ADIC. NaCN</th>
            <th>ADIC. NaOH</th>
            <th>CIP RECUPERACIÓN</th>
            <th>ESTADO</th>
            <th>ACCIONES</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="prueba in pruebasFiltradas"
            :key="prueba.ip + (prueba.fecha_ingreso ?? '')"
            :class="{ 'fila-descartada': prueba.descartado }"
          >
            <td class="td-mono" style="color:var(--color-gold)">{{ prueba.ip }}</td>
            <td class="td-fecha">{{ fmt(prueba.fecha_recepcion) }}</td>
            <td class="td-fecha">{{ fmt(prueba.fecha_ingreso) }}</td>
            <td class="td-mono" style="color:var(--color-gold-light)">
              {{ fmt(prueba.fecha_salida) }}
            </td>
            <td class="td-mono">{{ prueba.malla_porcentaje?.toFixed(1) ?? '---' }}</td>
            <!-- Columnas de adición acumulada -->
            <td class="td-mono">
              <span v-if="prueba.adicion_nacn != null" class="adicion-badge">{{ prueba.adicion_nacn.toFixed(2) }}g</span>
              <span v-else class="td-mono" style="color:var(--color-text-faint)">—</span>
            </td>
            <td class="td-mono">
              <span v-if="prueba.adicion_naoh != null" class="adicion-badge">{{ prueba.adicion_naoh.toFixed(2) }}g</span>
              <span v-else class="td-mono" style="color:var(--color-text-faint)">—</span>
            </td>
            <!-- CIP de recuperación -->
            <td>
              <span v-if="prueba.cip_asignado" class="td-mono" style="color:var(--color-gold);font-size:0.8rem">
                {{ prueba.cip_asignado }}
              </span>
              <span v-else class="badge-estado pendiente" style="font-size:0.65rem">Sin CIP</span>
            </td>
            <td>
              <template v-if="prueba.descartado">
                <span class="badge-estado descartado" :title="prueba.motivo_descarte ?? ''">
                  DESCARTADO
                </span>
              </template>
              <template v-else>
                <span class="badge-estado" :class="estadoClase(prueba.estado)">
                  {{ prueba.estado }}
                </span>
              </template>
            </td>
            <td class="td-acciones">
              <template v-if="!prueba.descartado">
                <!-- Registrar / Ver prueba -->
                <button
                  class="btn-primary"
                  style="font-size:0.75rem;padding:0.3rem 0.75rem"
                  :disabled="estadoBotonRegistrar(prueba).disabled"
                  @click="irARegistrar(prueba.ip)"
                >
                  {{ estadoBotonRegistrar(prueba).texto }}
                </button>

                <!-- Adición: solo cuando EN PROCESO (rodando) -->
                <button
                  v-if="prueba.estado === 'EN PROCESO'"
                  class="btn-adicion"
                  style="font-size:0.75rem;padding:0.3rem 0.75rem"
                  @click="abrirModalAdicion(prueba)"
                >
                  + Adición
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
                  <Tag :size="14" /> Reimprimir
                </button>

                <!-- Descartar: disponible para pruebas activas -->
                <button
                  class="btn-descartar"
                  style="font-size:0.72rem;padding:0.25rem 0.6rem"
                  @click="abrirModalDescartar(prueba.ip)"
                  title="Descartar prueba (envase roto, etc.)"
                >
                  Descartar
                </button>
              </template>
              <template v-else>
                <span class="td-mono" style="font-size:0.72rem;color:var(--color-text-faint)">
                  {{ prueba.motivo_descarte }}
                </span>
              </template>
            </td>
          </tr>
          <tr v-if="pruebasFiltradas.length === 0">
            <td colspan="10" class="estado-tabla sin-datos">Sin pruebas registradas</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal etiqueta CIP (impresión) -->
    <div v-if="etiquetaModal" class="modal-overlay" @click.self="etiquetaModal = null">
      <div class="modal modal-md">
        <div class="modal-header">
          <h2>Etiqueta CIP Recuperación</h2>
          <button class="btn-cerrar" @click="etiquetaModal = null">×</button>
        </div>
        <div class="modal-body" style="text-align:center">
          <p class="field-label" style="margin-bottom:0.5rem">LOTE: {{ etiquetaModal.ip }}</p>
          <div class="etiqueta-cip">
            <span class="etiqueta-title">INVERMIN PAITITI S.A.C. - RECUPERACIÓN</span>
            <svg id="barcode-prueba" class="barcode-container"></svg>
            <span class="etiqueta-codigo">{{ etiquetaModal.cip }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="etiquetaModal = null">Cerrar</button>
          <button class="btn-primary" @click="imprimirEtiqueta(etiquetaModal)">Imprimir</button>
        </div>
      </div>
    </div>

    <!-- Modal Descartar Prueba -->
    <div v-if="modalDescartar" class="modal-overlay" @click.self="modalDescartar = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Descartar Prueba</h2>
          <button class="btn-cerrar" @click="modalDescartar = null">×</button>
        </div>
        <div class="modal-body">
          <p style="font-size:0.85rem;color:var(--color-text-muted);margin-bottom:1rem">
            Esta prueba será descartada (ej: envase roto, derrame, etc.).<br>
            El registro se conserva para <strong>seguimiento de insumos gastados</strong>,
            pero <strong>no se tomará para etiquetado ni análisis</strong>.
          </p>
          <div class="field">
            <label class="field-label">MOTIVO DEL DESCARTE (obligatorio):</label>
            <textarea
              class="field-input"
              v-model="motivoDescarte"
              rows="3"
              placeholder="Ej: Se rompió el envase durante el transporte"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalDescartar = null">Cancelar</button>
          <button
            class="btn-danger"
            :disabled="!motivoDescarte.trim() || descartando"
            @click="confirmarDescartar"
          >
            <span v-if="descartando" class="spinner" style="margin-right:0.3rem"></span>
            Confirmar Descarte
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Adición (NaCN / NaOH) -->
    <div v-if="modalAdicion" class="modal-overlay" @click.self="modalAdicion = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Registrar Adición</h2>
          <button class="btn-cerrar" @click="modalAdicion = null">×</button>
        </div>
        <div class="modal-body">
          <p style="font-size:0.85rem;color:var(--color-text-muted);margin-bottom:0.75rem">
            Lote <strong style="font-family:var(--font-mono);color:var(--color-gold)">{{ modalAdicion.ip }}</strong>
            — Los valores se <strong>suman</strong> al acumulado existente.
          </p>

          <div v-if="modalAdicion.adicion_nacn != null || modalAdicion.adicion_naoh != null"
            class="adicion-acumulado-info"
          >
            <span>Acumulado actual:</span>
            <span v-if="modalAdicion.adicion_nacn != null">NaCN: <strong>{{ modalAdicion.adicion_nacn.toFixed(2) }}g</strong></span>
            <span v-if="modalAdicion.adicion_naoh != null">NaOH: <strong>{{ modalAdicion.adicion_naoh.toFixed(2) }}g</strong></span>
          </div>

          <div class="form-grid" style="grid-template-columns:1fr 1fr;gap:0.75rem">
            <div class="field">
              <label class="field-label">ADICIÓN NaCN (g)</label>
              <input
                type="number"
                class="field-input"
                v-model.number="formAdicion.adicion_nacn"
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
            <div class="field">
              <label class="field-label">ADICIÓN NaOH (g)</label>
              <input
                type="number"
                class="field-input"
                v-model.number="formAdicion.adicion_naoh"
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalAdicion = null">Cancelar</button>
          <button
            class="btn-primary"
            :disabled="(!formAdicion.adicion_nacn && !formAdicion.adicion_naoh) || registrandoAdicion"
            @click="confirmarAdicion"
          >
            <span v-if="registrandoAdicion" class="spinner" style="margin-right:0.3rem"></span>
            Registrar Adición
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import AlertasBanner from '@/components/AlertasBanner.vue'
import { pruebasApi, type LotePruebaList } from '@/api/pruebas'
import { useSync } from '@/composables/useSync'
import { obtenerPruebasPendientes, type PruebaQueueData } from '@/composables/useOfflineQueue'
import { WifiOff, Tag, RefreshCw, Beaker } from 'lucide-vue-next'
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

// ── Descartar prueba ──────────────────────────────────────────────────────────
const modalDescartar  = ref<string | null>(null)  // IP de la prueba a descartar
const motivoDescarte  = ref('')
const descartando     = ref(false)

// ── Adición modal ─────────────────────────────────────────────────────────────
const modalAdicion = ref<LotePruebaList | null>(null)
const formAdicion  = ref({ adicion_nacn: null as number | null, adicion_naoh: null as number | null })
const registrandoAdicion = ref(false)

const estadosPrueba = [
  { id: 'PENDIENTE', nombre: 'Pendiente' },
  { id: 'EN PROCESO', nombre: 'En Proceso' }, // Cambiado de EN_PROCESO a EN PROCESO
  { id: 'COMPLETADO', nombre: 'Completado' }
];

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
watch(etiquetaModal, async (val) => {
  if (!val) return
  await nextTick()
  try {
    JsBarcode(`#barcode-prueba`, val.cip, {
      format: 'CODE128',
      displayValue: false,
      width: 2,
      height: 45,
      margin: 0,
      background: 'transparent',
      lineColor: '#000000',
    })
  } catch (e) {
    console.error('Error dibujando barcode prueba:', e)
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
  // 1. Filtrar IPs que están en cola offline para no duplicar
  const estaOffline = new Set(pruebasOffline.value.map(p => p.ip));

  return pruebas.value.filter(p => {
    // Regla 1: Ocultar si está en cola de subida
    if (estaOffline.has(p.ip)) return false;

    // Regla 2: Filtro de Estado (EL PUNTO CRÍTICO)
    // Forzamos comparación limpia de strings
    if (filtroEstado.value && filtroEstado.value !== 'Todos') {
      if (p.estado.trim() !== filtroEstado.value.trim()) {
        return false;
      }
    }

    // Regla 3: Búsqueda por IP o CIP_ASIGNADO
    const q = filtroBusqueda.value.trim().toLowerCase();
    if (q) {
      const coincideIP = (p.ip || '').toLowerCase().includes(q);
      const coincideCIP = (p.cip_asignado || '').toLowerCase().includes(q);

      if (!coincideIP && !coincideCIP) return false;
    }

    return true;
  });
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(d: string | null | undefined) {
  if (!d) return '---'
  const hasTz = d.endsWith('Z') || /([+-]\d{2}:\d{2})$/.test(d)
  // Si es "ingenuo" (sin zona), forzamos que lo interprete como hora de Lima (-05:00)
  const iso = hasTz ? d : d + '-05:00'
  return new Date(iso).toLocaleString('es-PE', {
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
    const restante = obtenerTiempoRestante(p.fecha_ingreso)

    if (restante.terminado) {
      return { texto: 'Ver / Editar', disabled: false }
    } else {
      // Formateador dinámico: Muestra "2h 15m rest." o solo "45min rest."
      const textoTiempo = restante.horas > 0
        ? `${restante.horas}h ${restante.minutos}m rest.`
        : `${restante.minutos}min rest.`

      return { texto: `Rodando... (${textoTiempo})`, disabled: true }
    }
  }
  return { texto: 'Ver / Editar', disabled: false }
}

function obtenerTiempoRestante(fechaIngreso: string) {
  const hasTz = fechaIngreso.endsWith('Z') || /([+-]\d{2}:\d{2})$/.test(fechaIngreso)
  const isoString = hasTz ? fechaIngreso : fechaIngreso + '-05:00'

  const msIngreso = new Date(isoString).getTime()
  const msSalida = msIngreso + (48 * 60 * 60 * 1000) // Sumamos 48 horas en milisegundos
  const msAhora = new Date().getTime()

  const msRestantes = msSalida - msAhora

  // Si ya pasó la hora
  if (msRestantes <= 0) {
    return { horas: 0, minutos: 0, terminado: true }
  }

  // Calcular horas y minutos restantes
  const horas = Math.floor(msRestantes / (1000 * 60 * 60))
  const minutos = Math.floor((msRestantes % (1000 * 60 * 60)) / (1000 * 60))

  return { horas, minutos, terminado: false }
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

// ── Descartar ─────────────────────────────────────────────────────────────────
function abrirModalDescartar(ip: string) {
  modalDescartar.value = ip
  motivoDescarte.value = ''
}

async function confirmarDescartar() {
  if (!modalDescartar.value || !motivoDescarte.value.trim()) return
  descartando.value = true
  try {
    await pruebasApi.descartar(modalDescartar.value, motivoDescarte.value.trim())
    ui.toast('Prueba descartada. El registro se conserva para trazabilidad.', 'success')
    modalDescartar.value = null
    await cargarDatos()
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al descartar la prueba', 'error')
  } finally {
    descartando.value = false
  }
}

// ── Adición ───────────────────────────────────────────────────────────────────
function abrirModalAdicion(prueba: LotePruebaList) {
  modalAdicion.value = prueba
  formAdicion.value = { adicion_nacn: null, adicion_naoh: null }
}

async function confirmarAdicion() {
  if (!modalAdicion.value) return
  registrandoAdicion.value = true
  try {
    await pruebasApi.registrarAdicion(modalAdicion.value.ip, {
      adicion_nacn: formAdicion.value.adicion_nacn,
      adicion_naoh: formAdicion.value.adicion_naoh,
    })
    ui.toast('Adición registrada correctamente', 'success')
    modalAdicion.value = null
    await cargarDatos()
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al registrar adición', 'error')
  } finally {
    registrandoAdicion.value = false
  }
}

function imprimirEtiqueta(e: { ip: string; cip: string }) {
  const svgEl = document.querySelector<SVGElement>('#barcode-prueba')
  const svgHtml = svgEl ? svgEl.outerHTML : ''

  const css = `
    body { font-family: monospace; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0; }
    .et { border:2px dashed #333; border-radius:8px; padding:12px 18px; text-align:center; width:220px; }
    .et-title { font-size:0.65rem; font-weight:900; letter-spacing:.1em; display:block; margin-bottom:4px; }
    .et-sub { font-size:0.55rem; border-bottom:1px solid #000; padding-bottom:4px; display:block; width:100%; text-align:center; margin-bottom:8px; }
    svg { width:100%; height:45px; margin:6px 0; }
    .et-code { font-size:1.6rem; font-weight:900; margin-top:8px; display:block; letter-spacing:0.05em; }
  `
  const html = `<!DOCTYPE html><html><head><style>${css}</style></head><body>
    <div class="et">
      <span class="et-title">INVERMIN PAITITI S.A.C.</span>
      <span class="et-sub">RECUPERACIÓN</span>
      ${svgHtml}
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
.descartado  { background: rgba(120,120,120,.15); color: var(--color-text-muted); border: 1px solid rgba(120,120,120,.3); }

/* ── Fila descartada ─────────────────────────────────── */
.fila-descartada {
  opacity: 0.55;
  text-decoration: line-through;
  text-decoration-color: rgba(255,255,255,0.2);
}
.fila-descartada .td-mono,
.fila-descartada .td-fecha { text-decoration: line-through; }
.fila-descartada .badge-estado { text-decoration: none; }
.fila-descartada .td-acciones { text-decoration: none; }

/* ── Adición badge ───────────────────────────────────── */
.adicion-badge {
  display: inline-block;
  background: rgba(34,197,94,0.12);
  color: #4ade80;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
}

.adicion-acumulado-info {
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.75rem;
  display: flex;
  gap: 0.75rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}
.adicion-acumulado-info strong {
  color: #4ade80;
}

/* ── Botón descartar ─────────────────────────────────── */
.btn-descartar {
  background: transparent;
  border: 1px solid rgba(220,60,60,.3);
  color: var(--color-error);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-main);
  font-weight: 600;
  transition: all 0.2s;
}
.btn-descartar:hover {
  background: rgba(220,60,60,.1);
  border-color: rgba(220,60,60,.5);
}

/* ── Botón adición ───────────────────────────────────── */
.btn-adicion {
  background: rgba(34,197,94,0.1);
  border: 1px solid rgba(34,197,94,.3);
  color: #4ade80;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-main);
  font-weight: 600;
  transition: all 0.2s;
}
.btn-adicion:hover {
  background: rgba(34,197,94,0.18);
  border-color: rgba(34,197,94,.5);
}

/* ── Botón danger (modal) ────────────────────────────── */
.btn-danger {
  background: rgba(220,60,60,.15);
  border: 1px solid rgba(220,60,60,.4);
  color: #f87171;
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-md);
  font-family: var(--font-main);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-danger:hover:not(:disabled) {
  background: rgba(220,60,60,.25);
}
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

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

.btn-refresh {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-gold);
  padding: 0.5rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(212, 175, 55, 0.1);
  border-color: var(--color-gold);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animación de rotación para el icono */
.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Ajuste opcional para el layout del header */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
</style>
