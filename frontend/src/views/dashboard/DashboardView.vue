<template>
  <div class="dashboard-page">

    <!-- ── Header ─────────────────────────────────────────────── -->
    <header class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <span class="last-sync" v-if="lastUpdate">Actualizado {{ lastUpdate }}</span>
      </div>
      <button class="btn-secondary btn-refresh" @click="recargar" :disabled="cargando">
        <RefreshCw :size="16" :class="{ spinner: cargando }" style="margin-right:0.4rem" />
        ACTUALIZAR
      </button>
    </header>

    <!-- ── KPIs ────────────────────────────────────────────────── -->
    <section class="kpi-grid">
      <div class="kpi-card gold-accent">
        <div class="kpi-info">
          <span class="kpi-label">Au Real 100%</span>
          <span class="kpi-value">{{ data?.kpis.au_real_100.toLocaleString('es-PE') }}g</span>
        </div>
        <Zap class="kpi-icon" :size="32" />
      </div>
      <div class="kpi-card gold-accent">
        <div class="kpi-info">
          <span class="kpi-label">Au Real Rec.</span>
          <span class="kpi-value">{{ data?.kpis.au_real_rec.toLocaleString('es-PE') }}g</span>
        </div>
        <TrendingUp class="kpi-icon" :size="32" />
      </div>
      <div class="kpi-card">
        <div class="kpi-info">
          <span class="kpi-label">TMH en Stock</span>
          <span class="kpi-value highlight">{{ data?.kpis.tmh_stock.toFixed(2) }} TM</span>
        </div>
        <Scale class="kpi-icon" :size="32" />
      </div>
      <div class="kpi-card">
        <div class="kpi-info">
          <span class="kpi-label">TMS en Stock</span>
          <span class="kpi-value">{{ data?.kpis.tms_stock.toFixed(2) }} TM</span>
        </div>
        <Database class="kpi-icon" :size="32" />
      </div>
      <div class="kpi-card">
        <div class="kpi-info">
          <span class="kpi-label">Oz en Stock</span>
          <span class="kpi-value">{{ data?.kpis.oz_stock.toFixed(2) }} oz</span>
        </div>
        <Coins class="kpi-icon" :size="32" />
      </div>
    </section>

    <!-- ── Tabs ────────────────────────────────────────────────── -->
    <div class="tabs-bar">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: tabActual === tab.key }"
        @click="tabActual = tab.key"
      >
        <component :is="tab.icon" :size="15" style="margin-right:0.35rem" />
        {{ tab.label }}
        <span v-if="tab.count != null" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem" /> Cargando…
    </div>

    <!-- ══════════════════════════════════════════════════════════
         TAB: LOTES
    ══════════════════════════════════════════════════════════ -->
    <template v-else-if="tabActual === 'lotes'">
      <div class="filtros-bar">
        <div class="field" style="width:160px">
          <label class="field-label">ESTADO</label>
          <select class="field-input field-select" v-model="filtroEstadoLote">
            <option value="">Todos</option>
            <option value="RECEPCIONADO">Recepcionado</option>
            <option value="ASIGNADO_RUMA">Asignado Ruma</option>
            <option value="LIQUIDADO">Liquidado</option>
            <option value="FACTURADO">Facturado</option>
            <option value="PAGADO">Pagado</option>
          </select>
        </div>
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <div class="search-wrapper">
            <Search :size="15" class="search-icon" />
            <input
              type="text"
              class="field-input search-input"
              v-model="busquedaLote"
              placeholder="IP, proveedor…"
            />
          </div>
        </div>
      </div>

      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>LOTE</th>
              <th class="align-right">TMH</th>
              <th class="align-right">TMS</th>
              <th class="align-right">%H₂O</th>
              <th>PROVEEDOR</th>
              <th>RUC</th>
              <th class="align-right">LEY PROM.</th>
              <th class="align-right">% REC.</th>
              <th>ACOPIADOR</th>
              <th class="align-center">ESTADO LOTE</th>
              <th class="align-center">ESTADO</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="lotesFiltrados.length === 0">
              <td colspan="11" class="empty-state">Sin lotes para los filtros seleccionados.</td>
            </tr>
            <tr v-for="lote in lotesFiltrados" :key="lote.ip" class="tabla-row">
              <td class="td-mono gold">{{ lote.ip }}</td>
              <td class="align-right td-mono">{{ lote.tmh.toFixed(3) }}</td>
              <td class="align-right td-mono">{{ lote.tms?.toFixed(3) ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.h2o_porc != null ? lote.h2o_porc + '%' : '—' }}</td>
              <td class="td-truncate" :title="lote.proveedor">{{ lote.proveedor }}</td>
              <td class="td-mono td-muted">{{ lote.ruc ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.ley_avg?.toFixed(4) ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.rec_porc != null ? lote.rec_porc + '%' : '—' }}</td>
              <td class="td-truncate td-muted" :title="lote.acopiador || ''">{{ lote.acopiador || '—' }}</td>
              <td class="align-center">
                <span class="badge-estado-lote" :class="badgeEstadoLote(lote.estado_lote)">
                  {{ lote.estado_lote }}
                </span>
              </td>
              <td class="align-center">
                <span class="badge-estado" :class="badgeLote(lote.estado)">{{ lote.estado }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span class="table-count">{{ lotesFiltrados.length }} de {{ data?.lotes.length ?? 0 }} lotes</span>
      </div>
    </template>

    <!-- ══════════════════════════════════════════════════════════
         TAB: LIQUIDACIONES
    ══════════════════════════════════════════════════════════ -->
    <template v-else-if="tabActual === 'liquidaciones'">
      <div class="filtros-bar">
        <div class="field" style="width:160px">
          <label class="field-label">ESTADO</label>
          <select class="field-input field-select" v-model="filtroEstadoLiq">
            <option value="">Todos</option>
            <option value="GENERADA">Generada</option>
            <option value="FACTURADA">Facturada</option>
            <option value="PAGADA">Pagada</option>
          </select>
        </div>
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <div class="search-wrapper">
            <Search :size="15" class="search-icon" />
            <input
              type="text"
              class="field-input search-input"
              v-model="busquedaLiq"
              placeholder="N° liquidación, proveedor…"
            />
          </div>
        </div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn-primary ready btn-con-icono" @click="router.push('/liquidaciones/nueva')">
            <PlusCircle :size="16" />
            Nueva
          </button>
        </div>
      </div>

      <div v-if="liqStore.cargando" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando liquidaciones…
      </div>
      <div class="table-wrapper" v-else>
        <table class="data-table">
          <thead>
            <tr>
              <th>N° LIQUIDACIÓN</th>
              <th>PROVEEDOR</th>
              <th>ACOPIADOR</th>
              <th class="align-center">LOTES</th>
              <th class="align-right">SPOT USD</th>
              <th class="align-right">TOTAL USD</th>
              <th class="align-center">ESTADO</th>
              <th>FECHA</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="liquidacionesFiltradas.length === 0">
              <td colspan="9" class="empty-state">Sin liquidaciones registradas.</td>
            </tr>
            <tr
              v-for="liq in liquidacionesFiltradas"
              :key="liq.id"
              class="tabla-row clickable"
              @click="router.push(`/liquidaciones/${liq.id}`)"
            >
              <td class="td-mono" style="color:var(--color-gold)">{{ liq.numero_liquidacion }}</td>
              <td>
                <span class="nombre-bold">{{ liq.proveedor_razon_social }}</span>
                <span v-if="liq.proveedor_ruc" class="ruc-sub">{{ liq.proveedor_ruc }}</span>
              </td>
              <td class="td-muted">{{ liq.acopiador_nombre }}</td>
              <td class="align-center">
                <span class="badge-count-sm">{{ liq.count_lotes }}</span>
              </td>
              <td class="align-right td-mono">${{ fmtNum(liq.spot_usd) }}</td>
              <td class="align-right td-mono" style="color:var(--color-gold);font-weight:700">
                ${{ fmtNum(liq.total_usd) }}
              </td>
              <td class="align-center">
                <span class="badge-estado" :class="badgeLiq(liq.estado)">{{ liq.estado }}</span>
              </td>
              <td class="td-mono td-muted" style="font-size:var(--text-sm)">{{ fmtDate(liq.fecha_creacion) }}</td>
              <td @click.stop>
                <button
                  class="btn-accion"
                  title="Descargar PDF"
                  @click="descargarPDF(liq.id.toString())"
                >
                  <Download :size="14" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span class="table-count">{{ liquidacionesFiltradas.length }} de {{ liqStore.lista.length }} liquidaciones</span>
      </div>
    </template>

    <!-- ══════════════════════════════════════════════════════════
         TAB: RESUMEN (default)
    ══════════════════════════════════════════════════════════ -->
    <template v-else>
      <div class="filtros-bar">
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA RÁPIDA</label>
          <div class="search-wrapper">
            <Search :size="15" class="search-icon" />
            <input
              type="text"
              class="field-input search-input"
              v-model="busquedaLote"
              placeholder="IP, proveedor…"
            />
          </div>
        </div>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>LOTE</th>
              <th class="align-right">TMH</th>
              <th class="align-right">TMS</th>
              <th class="align-right">%H₂O</th>
              <th>PROVEEDOR</th>
              <th>RUC</th>
              <th class="align-right">LEY PROM.</th>
              <th class="align-right">% REC.</th>
              <th>ACOPIADOR</th>
              <th class="align-center">ESTADO</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="lotesFiltrados.length === 0">
              <td colspan="10" class="empty-state">No hay lotes registrados.</td>
            </tr>
            <tr v-for="lote in lotesFiltrados.slice(0, 25)" :key="lote.ip" class="tabla-row">
              <td class="td-mono gold">{{ lote.ip }}</td>
              <td class="align-right td-mono">{{ lote.tmh.toFixed(3) }}</td>
              <td class="align-right td-mono">{{ lote.tms?.toFixed(3) ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.h2o_porc != null ? lote.h2o_porc + '%' : '—' }}</td>
              <td class="td-truncate" :title="lote.proveedor">{{ lote.proveedor }}</td>
              <td class="td-mono td-muted">{{ lote.ruc ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.ley_avg?.toFixed(4) ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.rec_porc != null ? lote.rec_porc + '%' : '—' }}</td>
              <td class="td-truncate td-muted" :title="lote.acopiador || ''">{{ lote.acopiador || '—' }}</td>
              <td class="align-center">
                <span class="badge-estado" :class="badgeLote(lote.estado)">{{ lote.estado }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer" v-if="(data?.lotes.length ?? 0) > 25">
        <span class="table-count">Mostrando 25 de {{ data?.lotes.length }} — usa la pestaña Lotes para ver todos</span>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import {
  Zap, TrendingUp, Scale, Database, Coins, Search,
  RefreshCw, Layers, FileText, PlusCircle, Download, LayoutDashboard,
} from 'lucide-vue-next'
import { dashboardApi, type DashboardResponse } from '@/api/dashboard'
import { useLiquidacionesStore } from '@/stores/liquidaciones'
import { useUiStore } from '@/stores/ui'
import { descargarPDF } from '@/api/liquidaciones'

const router   = useRouter()
const liqStore = useLiquidacionesStore()
const ui       = useUiStore()

// ── Data ─────────────────────────────────────────────────────────────
const data       = ref<DashboardResponse | null>(null)
const cargando   = ref(true)
const lastUpdate = ref<string | null>(null)

// ── Tabs ──────────────────────────────────────────────────────────────
type TabKey = 'resumen' | 'lotes' | 'liquidaciones'
const tabActual = ref<TabKey>('resumen')

const tabs = computed(() => [
  { key: 'resumen'        as TabKey, label: 'Resumen',       icon: markRaw(LayoutDashboard), count: null },
  { key: 'lotes'          as TabKey, label: 'Lotes',         icon: markRaw(Layers),           count: data.value?.lotes.length ?? 0 },
  { key: 'liquidaciones'  as TabKey, label: 'Liquidaciones', icon: markRaw(FileText),          count: liqStore.lista.length || null },
])

// ── Filtros ───────────────────────────────────────────────────────────
const busquedaLote     = ref('')
const filtroEstadoLote = ref('')
const busquedaLiq      = ref('')
const filtroEstadoLiq  = ref('')

// ── Computed ──────────────────────────────────────────────────────────
const lotesFiltrados = computed(() => {
  if (!data.value) return []
  return data.value.lotes.filter(l => {
    if (filtroEstadoLote.value && l.estado !== filtroEstadoLote.value) return false
    const q = busquedaLote.value.toLowerCase()
    if (!q) return true
    return l.ip.toLowerCase().includes(q) || l.proveedor.toLowerCase().includes(q)
  })
})

const liquidacionesFiltradas = computed(() => {
  const q = busquedaLiq.value.trim().toLowerCase()
  return liqStore.lista.filter(l => {
    if (filtroEstadoLiq.value && l.estado !== filtroEstadoLiq.value) return false
    if (!q) return true
    return (
      l.numero_liquidacion.toLowerCase().includes(q) ||
      l.proveedor_razon_social.toLowerCase().includes(q) ||
      (l.proveedor_ruc?.includes(q) ?? false)
    )
  })
})

// ── Actions ───────────────────────────────────────────────────────────
async function cargarDashboard() {
  cargando.value = true
  try {
    data.value   = await dashboardApi.getResumen()
    lastUpdate.value = new Date().toLocaleTimeString('es-PE')
  } catch (e) {
    console.error('Error cargando dashboard', e)
  } finally {
    cargando.value = false
  }
}

async function recargar() {
  await Promise.all([cargarDashboard(), liqStore.cargarLista()])
}

// ── Formatters ────────────────────────────────────────────────────────
function fmtNum(v: number, d = 2) {
  return Number(v).toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
}
function fmtDate(s: string) {
  if (!s) return '-'
  return new Date(s).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function badgeLote(estado: string) {
  const m: Record<string, string> = {
    RECEPCIONADO: 'en-proceso', ASIGNADO_RUMA: 'parcial',
    LIQUIDADO: 'completado', FACTURADO: 'pendiente', PAGADO: 'pagado',
  }
  return m[estado] ?? 'en-proceso'
}
function badgeLiq(estado: string) {
  return { GENERADA: 'parcial', FACTURADA: 'pendiente', PAGADA: 'pagado' }[estado] ?? 'parcial'
}
function badgeEstadoLote(estado: string) {
  return {
    'badge-completo':   estado === 'COMPLETO',
    'badge-habilitado': estado === 'HABILITADO',
    'badge-dirimencia': estado === 'DIRIMENCIA',
    'badge-volado':     estado === 'VOLADO',
    'badge-proceso':    estado === 'EN_PROCESO',
  }
}

onMounted(() => {
  cargarDashboard()
  liqStore.cargarLista()
})
</script>

<style scoped>
.dashboard-page {
  padding: var(--page-padding);
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Header ── */
.page-header { display: flex; justify-content: space-between; align-items: flex-end; }
.last-sync { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted); }
.btn-refresh { display: flex; align-items: center; }

/* ── KPIs ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.kpi-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.15s, box-shadow 0.15s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.gold-accent { border-left: 3px solid var(--color-gold); }
.kpi-info { display: flex; flex-direction: column; gap: 0.25rem; }
.kpi-label {
  font-family: var(--font-main); font-size: var(--text-xs); font-weight: 700;
  color: var(--color-text-muted); letter-spacing: 0.08em; text-transform: uppercase;
}
.kpi-value { font-family: var(--font-mono); font-size: var(--text-xl); font-weight: 700; color: var(--color-text); }
.kpi-value.highlight { color: var(--color-gold); }
.kpi-icon { color: var(--color-text-muted); opacity: 0.3; }

/* ── Tabs ── */
.tabs-bar {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  gap: 0;
}
.tab-btn {
  display: flex; align-items: center;
  background: transparent; border: none;
  color: var(--color-text-muted);
  padding: 0.6rem 1.25rem;
  font-size: var(--text-md); font-family: var(--font-mono);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  letter-spacing: 0.06em;
}
.tab-btn.active { color: var(--color-gold); border-bottom-color: var(--color-gold); }
.tab-btn:hover:not(.active) { color: var(--color-text); }
.tab-count {
  margin-left: 0.4rem;
  background: rgba(179,144,40,0.15); border: 1px solid rgba(179,144,40,0.3);
  color: var(--color-gold); font-size: var(--text-xs);
  padding: 0.05rem 0.45rem; border-radius: 999px; font-family: var(--font-mono);
}

/* ── Filtros ── */
.filtros-bar { display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-end; }
.search-wrapper { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--color-text-muted); pointer-events: none; }
.search-input { padding-left: 32px; }
.btn-con-icono { display: flex; align-items: center; gap: 0.4rem; padding: 0.6rem 1rem; min-height: 40px; }

/* ── Tabla ── */
.table-wrapper { overflow-x: auto; border: 1px solid var(--color-border); border-radius: var(--radius-sm); }
.data-table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
.data-table thead tr { background: rgba(179,144,40,0.06); border-bottom: 1px solid var(--color-border); }
.data-table th {
  padding: 0.65rem 1rem; text-align: left;
  font-family: var(--font-mono); font-size: var(--text-xs);
  letter-spacing: 0.12em; color: var(--color-text-muted); text-transform: uppercase; white-space: nowrap;
}
.data-table td { padding: 0.7rem 1rem; border-bottom: 1px solid rgba(58,58,40,0.4); color: var(--color-text); }
.tabla-row { transition: background 0.1s; }
.tabla-row:hover { background: rgba(179,144,40,0.04); }
.tabla-row.clickable { cursor: pointer; }

.td-mono   { font-family: var(--font-mono); }
.td-muted  { color: var(--color-text-muted); }
.td-truncate { max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gold { color: var(--color-gold); font-weight: bold; }
.align-right  { text-align: right !important; }
.align-center { text-align: center !important; }

.nombre-bold { display: block; font-weight: 600; }
.ruc-sub     { display: block; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-dim); }

/* ── Badges estado ── */
.badge-estado {
  padding: 0.2rem 0.55rem; border-radius: 2px;
  font-size: var(--text-xs); font-weight: 700; font-family: var(--font-mono);
  letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap;
}
.en-proceso  { background: var(--color-warning-bg);  color: var(--color-warning);  border: 1px solid rgba(207,151,61,0.3); }
.parcial     { background: var(--color-gold-bg);      color: var(--color-gold);     border: 1px solid rgba(179,144,40,0.3); }
.completado  { background: var(--color-success-bg);   color: #4ade80;               border: 1px solid rgba(81,161,85,0.3); }
.pagado      { background: var(--color-success-bg);   color: #4ade80;               border: 1px solid rgba(81,161,85,0.3); }
.pendiente   { background: var(--color-error-bg);     color: var(--color-error);    border: 1px solid rgba(165,71,61,0.3); }

.badge-estado-lote {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-family: var(--font-mono);
  font-weight: 600;
  letter-spacing: 0.05em;
}
.badge-completo   { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.badge-habilitado { background: rgba(234, 179, 8, 0.15);  color: #eab308; }
.badge-dirimencia { background: rgba(168, 85, 247, 0.15); color: #a855f7; }
.badge-volado     { background: rgba(239, 68, 68, 0.15);  color: #ef4444; }
.badge-proceso    { background: rgba(148, 163, 184, 0.12); color: var(--color-text-muted); }
.badge-count-sm {
  display: inline-block; padding: 0.1rem 0.5rem;
  background: rgba(179,144,40,0.1); border: 1px solid rgba(179,144,40,0.25);
  border-radius: 2px; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-gold);
}

.btn-accion {
  background: transparent; border: 1px solid var(--color-border);
  color: var(--color-text-muted); width: 28px; height: 28px;
  border-radius: var(--radius-sm); cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; transition: all 0.15s;
}
.btn-accion:hover { border-color: var(--color-gold); color: var(--color-gold); }

/* ── Footer tabla ── */
.table-footer { display: flex; justify-content: flex-end; padding: 0.5rem 1rem; border-top: 1px solid var(--color-border); }
.table-count  { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-faint); }

/* ── Empty / loading ── */
.estado-tabla { text-align: center; padding: 3rem; font-family: var(--font-mono); font-size: var(--text-md); color: var(--color-text-muted); display: flex; align-items: center; justify-content: center; }
.empty-state  { text-align: center; padding: 2.5rem; color: var(--color-text-faint); font-family: var(--font-mono); font-size: var(--text-md); font-style: italic; }

.spinner { animation: spin 0.8s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
