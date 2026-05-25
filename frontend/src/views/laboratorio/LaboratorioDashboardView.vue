<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">
          <FlaskConical class="lucide" :size="24" style="margin-right:0.5rem" />
          Laboratorio
        </h1>
        <p class="page-subtitle">
          {{ store.puedeVerIP ? 'Gestión de Lotes y Leyes' : (tabActual === 'ley' ? 'Análisis de Ley' : 'Análisis de Recuperación') }}
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="recargar" :disabled="store.cargando || cargandoLotes">
          <RefreshCw :size="16" :class="{ spinner: store.cargando || cargandoLotes }" style="margin-right:0.4rem" />
          ACTUALIZAR
        </button>
      </div>
    </header>

    <!-- ── [OFFLINE] Análisis pendientes de sincronizar (solo Laboratorista) ── -->
    <div
      v-if="!store.puedeVerIP && analisisOfflinePendientes.length > 0"
      class="offline-section"
    >
      <div class="offline-section-header">
        <span class="offline-section-titulo">
          <WifiOff :size="16" style="margin-right:0.4rem;vertical-align:middle" />
          SIN SINCRONIZAR
        </span>
        <span class="offline-section-count">
          {{ analisisOfflinePendientes.length }} análisis local(es)
        </span>
      </div>
      <div style="padding:0.75rem 1rem">
        <div
          v-for="item in analisisOfflinePendientes"
          :key="item.offline_id"
          class="pendiente-item"
        >
          <span class="pendiente-cip">{{ item.datos.cip }}</span>
          <span class="pendiente-tipo">Análisis de ley · {{ item.datos.tipo_analisis }}</span>
          <span v-if="item.error" class="pendiente-error" :title="item.error">⚠ Error sync</span>
          <span v-else class="badge-local">LOCAL</span>
        </div>
      </div>
    </div>

    <template v-if="store.puedeVerIP">
      <div class="filtros-bar">
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <input type="text" class="field-input" v-model="filtroBusquedaLotes" placeholder="IP o Proveedor" />
        </div>
      </div>

      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>IP</th>
              <th>PROVEEDOR</th>
              <th>MATERIAL</th>
              <th>FECHA RECEPCIÓN</th>
              <th>LEY PLANTA</th>
              <th>LEY MINERO</th>
              <th>ESTADO LEYES</th>
              <th>ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargandoLotes">
              <td colspan="8" class="estado-tabla">
                <span class="spinner" style="margin-right:0.5rem"></span> Cargando lotes...
              </td>
            </tr>
            <template v-else>
              <tr v-if="lotesFiltrados.length === 0">
                <td colspan="8" class="estado-tabla sin-datos">Sin registros</td>
              </tr>
              <tr v-for="lote in lotesFiltrados" :key="lote.ip">
                <td class="td-mono" style="color:var(--color-gold)">{{ lote.ip }}</td>
                <td>{{ lote.proveedor }}</td>
                <td>{{ lote.material || '-' }}</td>
                <td class="td-fecha">{{ fmt(lote.fecha_recepcion) }}</td>
                <td class="td-mono">{{ lote.ley_planta ?? '-' }}</td>
                <td class="td-mono">{{ lote.ley_minero ?? '-' }}</td>
                <td>
                  <span class="badge-estado">{{ lote.analisis_ley.length }} análisis</span>
                </td>
                <td class="td-acciones">
                  <button class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irADetalleLote(lote.ip)">
                    Gestionar Leyes
                  </button>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </template>

    <template v-else>
      <div class="tabs-lab">
        <button class="tab-lab-btn" :class="{ active: tabActual === 'ley' }" @click="tabActual = 'ley'">
          Análisis de Ley Newmont
          <span v-if="pendientesLey > 0" class="badge-count">{{ pendientesLey }}</span>
          <span class="tab-lab-toggle">{{ tabActual === 'ley' ? '︿' : '︾' }}</span>
        </button>
        <button class="tab-lab-btn" :class="{ active: tabActual === 'rec' }" @click="tabActual = 'rec'">
          Análisis de Reconocimientos
          <span v-if="pendientesRec > 0" class="badge-count">{{ pendientesRec }}</span>
          <span class="tab-lab-toggle">{{ tabActual === 'rec' ? '︿' : '︾' }}</span>
        </button>
      </div>

      <div class="filtros-bar">
        <div class="field" style="min-width:180px">
          <label class="field-label">ESTADO</label>
          <select class="field-select field-sm field-input" v-model="filtroEstado">
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="COMPLETADO">Completado</option>
          </select>
        </div>
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <input type="text" class="field-input" v-model="filtroBusqueda" placeholder="CIP" />
        </div>
      </div>

      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>CIP</th>
              <th>FECHA ENVÍO</th>
              <template v-if="tabActual === 'ley'">
                <th>MALLA +140</th>
                <th>MALLA -140</th>
                <th>AU OZ/TC</th>
                <th>AU GR/TM</th>
              </template>
              <template v-else>
                <th>LEY CABEZA</th>
                <th>LEY COLA</th>
                <th>LEY LÍQUIDO</th>
                <th>% RECUPERACIÓN</th>
              </template>
              <th>ESTADO</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.cargando">
              <td :colspan="tabActual === 'ley' ? 8 : 8" class="estado-tabla">
                <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
              </td>
            </tr>
            <template v-else>
              <tr v-if="filasMostrar.length === 0">
                <td :colspan="tabActual === 'ley' ? 8 : 8" class="estado-tabla sin-datos">Sin registros</td>
              </tr>

              <template v-if="tabActual === 'ley'">
                <tr v-for="fila in filasMostrar" :key="fila.cip">
                  <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                  <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                  <td>{{ fila.leyMas ?? '-' }}</td>
                  <td>{{ fila.leyMenos ?? '-' }}</td>
                  <td class="td-mono" style="color:var(--color-gold-light)">{{ fila.ozTc ?? '-' }}</td>
                  <td class="td-mono">{{ fila.grTm ?? '-' }}</td>
                  <td>
                    <span class="badge-estado" :class="badgeClass(fila.estado)">{{ fila.estado }}</span>
                  </td>
                  <td class="td-acciones">
                    <button v-if="fila.estado === 'PENDIENTE'" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irARegistrarLey(fila.cip)">Registrar</button>
                    <button v-if="fila.estado === 'COMPLETADO' && !fila.certificadoUrl" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="generarCertLey(fila)">Generar cert.</button>
                    <button v-if="fila.certificadoUrl" class="btn-secondary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="verCertificado(fila.certificadoUrl)">Ver cert.</button>
                  </td>
                </tr>
              </template>

              <template v-if="tabActual === 'rec'">
                <tr v-for="fila in filasMostrar" :key="fila.cip">
                  <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                  <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                  <td>{{ fila.leyCabeza ?? '-' }}</td>
                  <td>{{ fila.leyCola ?? '-' }}</td>
                  <td>{{ fila.leyLiquido ?? '-' }}</td>
                  <td class="td-mono" style="color:var(--color-gold-light)">
                    {{ fila.recuperacion != null ? fila.recuperacion + '%' : '-' }}
                  </td>
                  <td>
                    <span class="badge-estado" :class="badgeClass(fila.estado)">{{ fila.estado }}</span>
                  </td>
                  <td class="td-acciones">
                    <button v-if="fila.estado === 'PENDIENTE'" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irARegistrarRecuperacion(fila.cip)">Registrar</button>
                    <button v-if="fila.estado === 'COMPLETADO' && !fila.certificadoUrl" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="generarCertRec(fila)">Generar cert.</button>
                    <button v-if="fila.certificadoUrl" class="btn-secondary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="verCertificado(fila.certificadoUrl)">Ver cert.</button>
                  </td>
                </tr>
              </template>
            </template>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FlaskConical, RefreshCw, WifiOff } from 'lucide-vue-next'
import { useUiStore } from '@/stores/ui'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { laboratorioApi } from '@/api/laboratorio'
import type { CIPAnalisisOut, LoteLabOut } from '@/types/laboratorio'
import { useSync } from '@/composables/useSync'
import { obtenerAnalisisLeyPendientes, type AnalisisLeyOfflineItem } from '@/composables/useOfflineQueue'

const router = useRouter()
const store  = useLaboratorioStore()
const ui     = useUiStore()
const {
  online,
  pendientes: pendientesSync,
  ultimoSync,
  sincronizar,
} = useSync()

const tabActual      = ref<'ley' | 'rec'>('ley')
const filtroEstado   = ref('')
const filtroBusqueda = ref('')
const filtroBusquedaLotes = ref('')

const lotes = ref<LoteLabOut[]>([])
const cargandoLotes = ref(false)

// Análisis encolados offline para mostrar al laboratorista
const analisisOfflinePendientes = ref<AnalisisLeyOfflineItem[]>([])

async function cargarAnalisisOffline() {
  try {
    analisisOfflinePendientes.value = await obtenerAnalisisLeyPendientes()
  } catch {
    analisisOfflinePendientes.value = []
  }
}

async function cargarDatos() {
  if (store.puedeVerIP) {
    cargandoLotes.value = true
    try {
      lotes.value = await laboratorioApi.listarLotes()
    } catch (e) {
      console.error(e)
    } finally {
      cargandoLotes.value = false
    }
  } else {
    await store.cargarCips()
    await cargarAnalisisOffline()
  }
}

onMounted(() => cargarDatos())
function recargar() { cargarDatos() }

// ── Recargar datos cuando el sync completa ──────────────────────────────
watch(ultimoSync, async () => {
  await cargarDatos()
})

// ── Recargar cuando vuelve la conexión ──────────────────────────────────
watch(online, async (ahoraOnline) => {
  if (ahoraOnline) {
    // Pequeño delay para que el sync arranque primero
    await new Promise(r => setTimeout(r, 300))
    if (pendientesSync.value === 0) {
      // Sin pendientes: recargar directo (watch(ultimoSync) no disparará)
      await cargarDatos()
    }
    // Con pendientes: watch(ultimoSync) recargará cuando el sync termine
  } else {
    // Al desconectarse: actualizar sección de pendientes offline
    await cargarAnalisisOffline()
  }
})

// ── Actualizar pendientes offline cuando cambia el count global ─────────
watch(pendientesSync, () => {
  if (!store.puedeVerIP) cargarAnalisisOffline()
})

const pendientesLey = computed(() =>
  store.cips.filter(c => c.tipo_muestra === 'Laboratorio' && c.estado_ley === 'PENDIENTE').length
)

const pendientesRec = computed(() =>
  store.cips.filter(c =>
    (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno') &&
    c.estado_recuperacion === 'PENDIENTE'
  ).length
)

function mapearCIP(c: CIPAnalisisOut) {
  if (tabActual.value === 'ley') {
    const vigente = c.analisis_ley.find(x => x.vigente)
    const ultimo = c.analisis_ley[c.analisis_ley.length - 1]
    const a = vigente ?? ultimo
    return {
      id: a?.id,
      cip: c.cip,
      fecha_envio: c.fecha_envio,
      estado: c.estado_ley,
      leyMas:  (a?.ley_grueso ?? null) ,
      leyMenos:  (a?.ley_fino   ?? null) ,
      ozTc:     (a?.ley_final   ?? null) ,
      grTm:    (a?.ley_gr_tm   ?? null) ,
      certificadoUrl: a?.certificado_url ?? null,
    }
  } else {
    const pending   = c.analisis_recuperacion.find(x => x.estado === 'PENDIENTE'  && x.vigente)
    const completado = c.analisis_recuperacion.find(x => x.estado === 'COMPLETADO' && x.vigente)
    const vigente   = pending ?? completado
    const ultimo    = c.analisis_recuperacion[c.analisis_recuperacion.length - 1]
    const a         = vigente ?? ultimo
    return {
      id: a?.id,
      cip: c.cip,
      fecha_envio: c.fecha_envio,
      estado: c.estado_recuperacion,
      leyCabeza:   vigente ? (vigente.ley_cabeza   ?? null) : null,
      leyCola:     vigente ? (vigente.ley_cola     ?? null) : null,
      leyLiquido:  vigente ? (vigente.ley_liquido  ?? null) : null,
      recuperacion: vigente ? (vigente.recuperacion ?? null) : null,
      certificadoUrl: a?.certificado_url ?? null,
    }
  }
}

const filasMostrar = computed(() => {
  // CIPs con análisis ya registrado offline → aparecen en la sección superior
  const cipsConAnalisisOffline = new Set(
    analisisOfflinePendientes.value.map(a => a.datos.cip)
  )

  const cipsFiltrados = store.cips.filter(c => {
    if (tabActual.value === 'ley') {
      if (c.tipo_muestra !== 'Laboratorio') return false
      if (cipsConAnalisisOffline.has(c.cip)) return false  // excluir si ya está en sección offline
      return true
    }
    return c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno'
  })

  return cipsFiltrados.map(mapearCIP).filter(f => {
    if (filtroEstado.value && f.estado !== filtroEstado.value) return false
    if (filtroBusqueda.value && !f.cip.toLowerCase().includes(filtroBusqueda.value.toLowerCase())) return false
    return true
  })
})

const lotesFiltrados = computed(() => {
  if (!filtroBusquedaLotes.value) return lotes.value
  const q = filtroBusquedaLotes.value.toLowerCase()
  return lotes.value.filter(l => l.ip.toLowerCase().includes(q) || (l.proveedor || '').toLowerCase().includes(q))
})

function fmt(d?: string | null | Date) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function badgeClass(estado: string) {
  return estado === 'COMPLETADO' ? 'completo' : estado === 'PENDIENTE' ? 'pendiente' : 'parcial'
}

async function verCertificado(ruta: string) {
  try {
    const url = await laboratorioApi.obtenerUrlArchivoVirtual(ruta)
    window.open(url, '_blank')
  } catch { ui.toast('Error al abrir certificado', 'error') }
}

function irARegistrarLey(cip: string)          { router.push(`/laboratorio/ley/${cip}`) }
function irARegistrarRecuperacion(cip: string) { router.push(`/laboratorio/recuperacion/${cip}`) }
function irADetalleLote(ip: string) { router.push(`/laboratorio/lote/${ip}`) }

const descargando = ref<string | null>(null)

async function descargarInforme(cip: string) {
  descargando.value = cip
  try {
    await laboratorioApi.descargarCertificadoEnsayo(cip)
  } catch {
    ui.toast('Error al generar informe de ensayo', 'error')
  } finally {
    descargando.value = null
  }
}

async function generarCertLey(fila: any) {
    if (!fila.id) return
    await store.generarCertificadoLeyInterno(fila.id)
    recargar()
}

async function generarCertRec(fila: any) {
    if (!fila.id) return
    await store.generarCertificadoRecInterno(fila.id)
    recargar()
}
</script>

<style scoped>
.tabs-lab { display: flex; gap: 0; margin-bottom: 1.25rem; border-bottom: 1px solid var(--color-border); }
.tab-lab-btn { background: transparent; border: none; color: var(--color-text-muted); padding: 0.6rem 1.25rem; font-size: var(--text-md); font-family: var(--font-mono); cursor: pointer; border-bottom: 2px solid transparent; transition: color 0.15s, border-color 0.15s; display: flex; align-items: center; gap: 0.5rem; }
.tab-lab-btn.active { color: var(--color-gold); border-bottom-color: var(--color-gold); }
.badge-count { background: var(--color-error, #ef4444); color: #fff; font-size: 0.65rem; padding: 0.1rem 0.4rem; border-radius: 999px; min-width: 1.2rem; text-align: center; }
.filtros-bar { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }

/* ── Sección offline pendientes ──────────────────────────── */
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
.offline-section-titulo {
  font-family: var(--font-mono); font-size: var(--text-sm);
  letter-spacing: .18em; color: #f59e0b;
}
.offline-section-count {
  font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted);
}
.pendiente-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: var(--text-sm);
}
.pendiente-item:last-child { border-bottom: none; }
.pendiente-cip {
  font-family: var(--font-mono); color: var(--color-gold);
  min-width: 120px;
}
.pendiente-tipo { color: var(--color-text-muted); flex: 1; }
.pendiente-error { color: var(--color-error); font-size: 0.7rem; }
.badge-local {
  font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: .1em;
  background: rgba(245,158,11,.15); color: #f59e0b;
  border: 1px solid rgba(245,158,11,.3); border-radius: 3px;
  padding: 1px 5px;
}
</style>
