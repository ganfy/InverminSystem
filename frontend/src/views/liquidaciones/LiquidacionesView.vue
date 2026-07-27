<template>
  <div class="page-container">

    <!-- ── Header ─────────────────────────────────────────────── -->
    <header class="page-header">
      <div class="header-title-row">
        <FileText class="header-icon" :size="26" />
        <div>
          <h1 class="page-title">Liquidaciones</h1>
          <p class="page-subtitle">
            Gestión comercial de lotes
          </p>
        </div>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
          <button class="btn-secondary btn-con-icono" @click="handleExportarPL">
            <Download :size="16" /> Exportar PL
          </button>
        <button class="btn-primary btn-con-icono" @click="router.push('/liquidaciones/nueva')">
          <Plus :size="16" /> Nueva Liquidación
        </button>
      </div>
    </header>

    <!-- ── Precio oro ──────────────────────────────────────────── -->
    <div class="precio-bar">
      <span class="precio-dot" />
      <span class="precio-label">Precio Au:</span>
      <span class="precio-valor">
        {{ cargandoPrecio ? 'Cargando…' : precioOro != null ? `$${fmtNum(precioOro, 2)}` : '—' }}
      </span>
      <button
            type="button"
            @click="cargarPrecioOro"
            :disabled="cargandoPrecio"
            class="filtro-btn"
          >
            {{ cargandoPrecio ? '...' : 'Actualizar Valor' }}
          </button>
    </div>

    <!-- ── KPIs ────────────────────────────────────────────────── -->
    <div class="kpi-grid">
      <div class="kpi-card kpi-accent">
        <div class="kpi-label">Borradores</div>
        <div class="kpi-val kpi-gold">{{ store.kpis?.borradores ?? '—' }}</div>
        <div class="kpi-sub">pendientes de emitir</div>
        <span v-if="(store.kpis?.borradores ?? 0) > 0" class="kpi-badge badge-warn">Acción requerida</span>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Generadas sin facturar</div>
        <div class="kpi-val">{{ store.kpis?.generadas ?? '—' }}</div>
        <div class="kpi-sub">esperan comprobante</div>
        <span v-if="(store.kpis?.generadas ?? 0) > 0" class="kpi-badge badge-warn">Pendiente</span>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Lotes liquidables</div>
        <div class="kpi-val">{{ countLotesLiquidables }}</div>
        <div class="kpi-sub">con análisis completos</div>
        <span v-if="(store.kpis?.lotes_liquidables ?? 0) > 0" class="kpi-badge badge-ok">Disponibles</span>
      </div>
      <div class="kpi-card kpi-accent">
        <div class="kpi-label">Valor pendiente cobro</div>
        <div class="kpi-val kpi-gold">${{ fmtNum(store.kpis?.valor_pendiente_usd, 0) }}</div>
        <div class="kpi-sub">USD · generadas + facturadas</div>
      </div>
    </div>

    <!-- ── Panel principal ────────────────────────────────────── -->
    <div class="panel">

      <!-- Tabs -->
      <div class="tabs-row">
        <button
          class="tab-btn"
          :class="{ active: tab === 'liquidaciones' }"
          @click="tab = 'liquidaciones'"
        >
          Liquidaciones
          <span class="tab-count">{{ listaFiltrada.length }}</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: tab === 'lotes' }"
          @click="tab = 'lotes'; cargarLotesLiquidables()"
        >
          Lotes liquidables
          <span class="tab-count tab-count-ok">{{ countLotesLiquidables }}</span>
        </button>
      </div>

      <!-- ── TAB: Liquidaciones ─────────────────────────────────── -->
      <template v-if="tab === 'liquidaciones'">

        <!-- Filtros -->
        <div class="filtros-row">
          <input
            class="filtro-input"
            placeholder="Buscar N° liq, proveedor…"
            v-model="filtroTexto"
          />
          <select class="field-select filtro-select" v-model="filtroEstado">
            <option value="">Todos los estados</option>
            <option value="BORRADOR">Borrador</option>
            <option value="GENERADA">Generada</option>
            <option value="FACTURADA">Facturada</option>
            <option value="PAGADA">Pagada</option>
          </select>
          <button class="filtro-btn" @click="aplicarFiltros">Filtrar</button>
        </div>

        <!-- Loading -->
        <div v-if="store.cargando" class="estado-cargando">
          <span class="spinner-sm" /> Cargando…
        </div>

        <!-- Tabla liquidaciones -->
        <div v-else-if="listaFiltrada.length" class="tabla-wrapper">
          <table class="tabla">
            <thead>
              <tr>
                <th>N° LIQUIDACIÓN</th>
                <th>PROVEEDOR</th>
                <th>ACOPIADOR</th>
                <th class="col-r">LOTES</th>
                <th class="col-r">SPOT</th>
                <th class="col-r">TOTAL USD</th>
                <th>ESTADO</th>
                <th>FECHA</th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="liq in listaFiltrada"
                :key="liq.id"
                class="tabla-row"
                @click="router.push(`/liquidaciones/${liq.id}`)"
                style="cursor:pointer"
              >
                <td class="td-mono td-gold">{{ liq.numero_liquidacion || '—' }}</td>
                <td class="td-truncate">{{ liq.proveedor_razon_social }}</td>
                <td class="td-muted td-truncate">{{ liq.acopiador_nombre }}</td>
                <td class="col-r td-mono td-muted">{{ liq.count_lotes }}</td>
                <td class="col-r td-mono td-muted">${{ fmtNum(liq.spot_usd, 2) }}</td>
                <td class="col-r td-mono td-bold">${{ fmtNum(liq.total_usd, 2) }}</td>
                <td><span class="badge-estado" :class="badgeClass(liq.estado)">{{ liq.estado }}</span></td>
                <td class="td-fecha td-muted">{{ fmtDate(liq.fecha_creacion) }}</td>
                <td class="col-acciones" @click.stop>
                  <div class="acciones">
                    <button class="accion-btn" @click="router.push(`/liquidaciones/${liq.id}`)">
                      Ver
                    </button>
                    <button
                      v-if="liq.estado === 'BORRADOR'"
                      class="accion-btn accion-gold"
                      @click="emitirLiquidacion(liq)"
                    >
                      Emitir
                    </button>
                    <button
                      v-if="liq.estado === 'GENERADA'"
                      class="accion-btn"
                      @click="cambiarEstadoRapido(liq, 'FACTURADA')"
                    >
                      Facturar
                    </button>
                    <button
                      v-if="liq.estado === 'FACTURADA'"
                      class="accion-btn"
                      @click="cambiarEstadoRapido(liq, 'PAGADA')"
                    >
                      Registrar pago
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="estado-vacio">
          Sin liquidaciones{{ filtroEstado ? ` con estado ${filtroEstado}` : '' }}
        </div>

      </template>

      <!-- ── TAB: Lotes liquidables ─────────────────────────────── -->
      <template v-else-if="tab === 'lotes'">

        <div v-if="cargandoLotes" class="estado-cargando">
          <span class="spinner-sm" /> Cargando lotes…
        </div>

        <div v-else-if="!lotesLiquidables.length" class="estado-vacio">
          No hay lotes con análisis de ley y recuperación completos
        </div>

        <!-- Agrupado por provacop -->
        <template v-else>
          <div
            v-for="grupo in lotesAgrupados"
            :key="grupo.provacop_label"
            class="grupo-provacop"
          >
            <!-- Header del grupo -->
            <div class="grupo-header">
              <div>
                <span class="grupo-nombre">{{ grupo.proveedor }}</span>
                <span class="grupo-sep">→</span>
                <span class="grupo-acop">{{ grupo.acopiador }}</span>
                <span class="grupo-meta">
                  {{ grupo.lotes.length }} lote{{ grupo.lotes.length > 1 ? 's' : '' }} ·
                  {{ fmtNum(grupo.tms_total, 3) }} TMS ·
                  Ley prom. {{ fmtNum(grupo.ley_prom, 4) }} oz/tc
                </span>
              </div>
              <button
                class="btn-primary btn-sm"
                @click="irACrearConProvacop(grupo)"
              >
                Crear liquidación →
              </button>
            </div>

            <!-- Tabla de lotes del grupo (Reemplaza grid) -->
            <div class="tabla-wrapper">
              <table class="tabla">
                <thead>
                  <tr>
                    <th>IP</th>
                    <th>MATERIAL</th>
                    <th>RECEPCIÓN</th>
                    <th class="col-r">TMS</th>
                    <th class="col-r">LEY PLANTA</th>
                    <th class="col-r">LEY MINERO</th>
                    <th class="col-r">LEY COMERC.</th>
                    <th class="col-r">% REC</th>
                    <th>ESTADO</th>
                    <th class="col-r">DÍAS</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="lote in grupo.lotes"
                    :key="lote.ip"
                    class="tabla-row"
                    :class="{ 'fila-volado': lote.volado, 'fila-vencimiento': lote.alerta_vencimiento && !lote.volado }"
                  >
                    <td class="td-mono" style="color:var(--color-gold)">{{ lote.ip }}</td>
                    <td class="td-muted">{{ lote.tipo_material || '—' }}</td>
                    <td class="td-fecha">{{ fmtDate(lote.fecha_recepcion) }}</td>
                    <td class="col-r td-mono">{{ fmtNum(lote.tms, 3) }}</td>
                    <td class="col-r td-mono td-muted">{{ fmtLey(lote.oz_tc_planta) }}</td>
                    <td class="col-r td-mono td-muted">{{ fmtLey(lote.oz_tc_minero) }}</td>
                    <td class="col-r td-mono" style="color:var(--color-gold)">{{ fmtLey(lote.ley_comercial) }}</td>
                    <td class="col-r td-mono">{{ fmtNum(lote.porcentaje_rec, 1) }}%</td>
                    <td>
                      <span v-if="lote.usa_dirimencia" class="alerta-tag alerta-dirim">DIRIM</span>
                      <span v-else-if="lote.volado" class="alerta-tag alerta-volado">VOLADO</span>
                      <span v-else-if="lote.alerta_vencimiento" class="alerta-tag alerta-venc">{{ lote.dias_almacen }}D</span>
                    </td>
                    <td class="col-r">
                      <span class="dias-badge" :class="{'dias-warn':lote.alerta_vencimiento,'dias-danger':lote.dias_almacen>=30}">
                        {{ lote.dias_almacen }}d
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>

      </template>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FileText, Download, Plus } from 'lucide-vue-next'
import { useLiquidacionesStore } from '@/stores/liquidaciones'
import { useUiStore } from '@/stores/ui'
import api from '@/api/axios'
import type { LoteDisponible, LiquidacionResumenOut } from '@/api/liquidaciones'
import { obtenerPrecioOro, exportarPL } from '@/api/liquidaciones'

const router = useRouter()
const store  = useLiquidacionesStore()
const ui     = useUiStore()

// ── Estado ──────────────────────────────────────────────────────────────────

const tab           = ref<'liquidaciones' | 'lotes'>('liquidaciones')
const filtroTexto   = ref('')
const filtroEstado  = ref('')
const cargandoLotes = ref(false)
const cargandoPrecio = ref(false)

// En la sección de Estado
const yaCargoLotes = ref(false)

// Lotes liquidables agrupados por provacop (cargados bajo demanda)
interface GrupoProvacop {
  provacop_id: number
  proveedor: string
  acopiador: string
  provacop_label: string
  lotes: LoteDisponible[]
  tms_total: number
  ley_prom: number
}
const lotesLiquidables = ref<LoteDisponible[]>([])

const precioOro = ref<number | null>(null)

// ── Computed ─────────────────────────────────────────────────────────────────

const listaFiltrada = computed(() => {
  let res = store.lista
  if (filtroEstado.value) res = res.filter(l => l.estado === filtroEstado.value)
  if (filtroTexto.value) {
    const q = filtroTexto.value.toLowerCase()
    res = res.filter(l =>
      (l.numero_liquidacion ?? '').toLowerCase().includes(q) ||
      l.proveedor_razon_social.toLowerCase().includes(q) ||
      l.acopiador_nombre.toLowerCase().includes(q)
    )
  }
  return res
})

const countLotesLiquidables = computed(() => {
  if (yaCargoLotes.value) return lotesLiquidables.value.length
  return store.kpis?.lotes_liquidables ?? 0
})

const lotesAgrupados = computed<GrupoProvacop[]>(() => {
  const map = new Map<number, GrupoProvacop>()  // keyed por provacop_id
  for (const lote of lotesLiquidables.value) {
    if (!map.has(lote.provacop_id)) {
      map.set(lote.provacop_id, {
        provacop_id: lote.provacop_id,
        proveedor: lote.proveedor,
        acopiador: lote.acopiador,
        provacop_label: `${lote.proveedor}|${lote.acopiador}`,
        lotes: [],
        tms_total: 0,
        ley_prom: 0,
      })
    }
    map.get(lote.provacop_id)!.lotes.push(lote)
    map.get(lote.provacop_id)!.tms_total += lote.tms ?? 0
  }
  for (const g of map.values()) {
    const totalTms = g.lotes.reduce((s, l) => s + (l.tms ?? 0), 0)
    if (totalTms > 0) {
      g.ley_prom = g.lotes.reduce((s, l) => s + (l.ley_comercial ?? 0) * (l.tms ?? 0), 0) / totalTms
    }
    g.lotes.sort((a, b) => {
      // Sort lotes by IP descending (e.g. L-100 before L-99)
      return b.ip.localeCompare(a.ip)
    })
  }
  const grupos = [...map.values()]
  grupos.sort((a, b) => {
    const provCmp = (a.proveedor || '').localeCompare(b.proveedor || '')
    if (provCmp !== 0) return provCmp
    return (a.acopiador || '').localeCompare(b.acopiador || '')
  })
  return grupos
})

const cargarPrecioOro = async () => {
  cargandoPrecio.value = true
  try {
    precioOro.value = await obtenerPrecioOro()
  } catch {
    ui.toast('Error al obtener precio del oro', 'error')
  } finally {
    cargandoPrecio.value = false
  }
}
// ── Métodos ──────────────────────────────────────────────────────────────────

async function cargarLotesLiquidables() {
  if (yaCargoLotes.value) return  // ya cargado en esta sesión
  cargandoLotes.value = true
  try {
    // Obtener todos los provacops con lotes recepcionados y pedir sus lotes disponibles
    const provacops = await api.get<{ id: number }[]>('/terceros/provacop')
    const todos: LoteDisponible[] = []
    await Promise.all(
      provacops.data.map(async (p) => {
        try {
          const r = await api.get<LoteDisponible[]>('/liquidaciones/lotes-disponibles', {
            params: { provacop_id: p.id }
          })
          // Solo los listos para liquidar
          todos.push(...r.data.filter(l => l.listo_para_liquidar))
        } catch { /* provacop sin lotes */ }
      })
    )
    lotesLiquidables.value = todos
    yaCargoLotes.value = true
  } catch {
    ui.toast('Error al cargar lotes liquidables', 'error')
  } finally {
    cargandoLotes.value = false
  }
}

function aplicarFiltros() {
  store.cargarLista({
    estado: filtroEstado.value || undefined,
  })
}

function irACrearConProvacop(grupo: GrupoProvacop) {
  // Navegar al wizard con provacop pre-seleccionado via query param
  router.push({
    path: '/liquidaciones/nueva',
    query: { proveedor: grupo.proveedor, acopiador: grupo.acopiador }
  })
}

async function emitirLiquidacion(liq: LiquidacionResumenOut) {
  const ok = await ui.showConfirm({
    title: 'Emitir Liquidación',
    message: `¿Emitir ${liq.numero_liquidacion}? Los lotes pasarán a estado LIQUIDADO y se generará el PDF.`,
    confirmLabel: 'Emitir',
    danger: false,
  })
  if (!ok) return
  const exito = await store.emitir(liq.id)
  if (exito) {
    ui.toast('Liquidación emitida correctamente', 'success')
    await store.cargarKPIs()
  } else {
    ui.toast(store.error ?? 'Error al emitir', 'error')
  }
}

async function cambiarEstadoRapido(liq: LiquidacionResumenOut, nuevoEstado: string) {
  const labels: Record<string, string> = { FACTURADA: 'facturar', PAGADA: 'marcar como pagada' }
  const ok = await ui.showConfirm({
    title: 'Cambiar estado',
    message: `¿Desea ${labels[nuevoEstado] ?? nuevoEstado} la liquidación ${liq.numero_liquidacion}?`,
    confirmLabel: 'Confirmar',
    danger: nuevoEstado === 'PAGADA',
  })
  if (!ok) return
  const exito = await store.cambiarEstado(liq.id, nuevoEstado)
  if (exito) {
    ui.toast(`Estado actualizado a ${nuevoEstado}`, 'success')
    await store.cargarKPIs()
    // Si ya cargamos lotes, refrescar también ese listado
    if (yaCargoLotes.value) {
      yaCargoLotes.value = false
      await cargarLotesLiquidables()
    }
  }
  else ui.toast(store.error ?? 'Error al cambiar estado', 'error')
}

// ── Formatters ────────────────────────────────────────────────────────────────

function fmtNum(v: number | null | undefined, d = 2) {
  if (v == null) return '—'
  return Number(v).toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
}
function fmtLey(v: number | string | null | undefined) {
  if (v == null) return '—'
  const n = Number(v)
  if (isNaN(n)) return '—'
  return n.toString()
}
function fmtDate(s: string | null | undefined) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
function badgeClass(estado: string) {
  return {
    BORRADOR:  'badge-borrador',
    GENERADA:  'badge-generada',
    FACTURADA: 'badge-facturada',
    PAGADA:    'badge-pagada',
  }[estado] ?? 'badge-generada'
}

// ── Init ──────────────────────────────────────────────────────────────────────

onMounted(async () => {
  await cargarPrecioOro()
  await Promise.all([
    store.cargarLista(),
    store.cargarKPIs(),
  ])
})

async function handleExportarPL() {
  const clave = await ui.showPrompt({
    title: 'Exportar PL',
    message: 'Ingrese una contraseña segura para cifrar el archivo Excel (mínimo 4 caracteres).',
    inputType: 'password'
  })
  
  if (!clave) return
  
  if (clave.length < 4) {
    ui.toast('La contraseña debe tener al menos 4 caracteres', 'error')
    return
  }
  
  try {
    await exportarPL(clave)
    ui.toast('Archivo descargado con éxito', 'success')
  } catch (err: any) {
    console.error(err)
    ui.toast(err?.response?.data?.detail || 'Error al exportar', 'error')
  }
}
</script>

<style scoped>
@import '@/assets/base.css';

.page-subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-top: 0.2rem;
  font-family: var(--font-mono);
}

/* ── Precio bar ──────────────────────────────────────────────────── */
.precio-bar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 1rem;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 1.25rem;
  font-size: var(--text-sm);
}
.precio-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--color-success); flex-shrink: 0;
}
.precio-label { color: var(--color-text-muted); }
.precio-valor { font-family: var(--font-mono); font-size: var(--text-md); color: var(--color-gold); font-weight: 600; }
.precio-meta  { color: var(--color-text-faint); font-size: var(--text-xs); margin-left: 0.25rem; }

/* ── KPIs ────────────────────────────────────────────────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}
.kpi-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 1rem 1.1rem;
  position: relative;
}
.kpi-card.kpi-accent { border-left: 2px solid var(--color-gold); }
.kpi-label { font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: 0.12em; text-transform: uppercase; color: var(--color-text-muted); margin-bottom: 0.4rem; }
.kpi-val   { font-family: var(--font-mono); font-size: 1.6rem; font-weight: 700; color: var(--color-text); line-height: 1.1; }
.kpi-val.kpi-gold { color: var(--color-gold); }
.kpi-sub   { font-size: var(--text-xs); color: var(--color-text-faint); margin-top: 0.3rem; }
.kpi-badge { position: absolute; top: 0.75rem; right: 0.75rem; font-family: var(--font-mono); font-size: 0.65rem; padding: 0.15rem 0.5rem; border-radius: 2px; letter-spacing: 0.08em; }
.badge-warn { background: var(--color-warning-bg); color: var(--color-warning); border: 1px solid rgba(207,151,61,0.35); }
.badge-ok   { background: var(--color-success-bg); color: var(--color-success); border: 1px solid rgba(81,161,85,0.35); }

/* ── Panel + tabs ────────────────────────────────────────────────── */
.panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.tabs-row {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  padding: 0 0.5rem;
}
.tab-btn {
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 0.8rem 1rem;
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  letter-spacing: 0.05em;
  transition: color 0.15s, border-color 0.15s;
}
.tab-btn.active { color: var(--color-gold); border-bottom-color: var(--color-gold); }
.tab-count {
  font-size: 0.65rem;
  background: rgba(255,255,255,0.07);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  padding: 0.05rem 0.4rem;
  border-radius: 2px;
}
.tab-count-ok {
  background: var(--color-success-bg);
  color: var(--color-success);
  border-color: rgba(81,161,85,0.3);
}

/* ── Filtros ─────────────────────────────────────────────────────── */
.filtros-row {
  display: flex;
  gap: 0.65rem;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
}
.filtro-input {
  padding: 0.45rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-family: var(--font-sans);
  min-width: 200px;
}
.filtro-select {
  padding: 0.45rem 0.75rem;
  font-size: var(--text-sm);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-family: var(--font-mono);
  cursor: pointer;
}
.filtro-btn {
  padding: 0.45rem 1rem;
  font-size: var(--text-sm);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  transition: all 0.15s;
}
.filtro-btn:hover { border-color: var(--color-gold); color: var(--color-gold); }

/* ── Tabla ───────────────────────────────────────────────────────── */
.tabla-wrapper { overflow-x: auto; border: 1px solid var(--color-border); border-radius: var(--radius-sm); }
.tabla { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
.tabla thead tr { background: rgba(179,144,40,0.05); border-bottom: 1px solid var(--color-border); }
.tabla th {
  padding: 0.6rem 0.8rem;
  font-family: var(--font-mono); font-size: var(--text-xs);
  letter-spacing: 0.12em; color: var(--color-text-muted);
  text-transform: uppercase; white-space: nowrap; text-align: left;
}
.tabla td { padding: 0.65rem 0.8rem; color: var(--color-text); vertical-align: middle; white-space: nowrap; }
.tabla-row { border-bottom: 1px solid rgba(58,58,40,0.4); transition: background 0.1s; }
.tabla-row:hover { background: rgba(179,144,40,0.04); }
.fila-volado { background: rgba(207,151,61,0.05) !important; }
.fila-alerta { background: rgba(245,158,11,0.03) !important; }

th.col-r, td.col-r { text-align: right !important; }
.col-acciones { text-align: right; white-space: nowrap; }
.td-mono    { font-family: var(--font-mono); }
.td-gold    { color: var(--color-gold); }
.td-muted   { color: var(--color-text-dim); }
.td-fecha   { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-dim); }
.td-bold    { font-weight: 600; }
.td-truncate { max-width: 160px; overflow: hidden; text-overflow: ellipsis; }

/* ── Botones de acción inline ────────────────────────────────────── */
.acciones    { display: flex; gap: 0.35rem; justify-content: flex-end; }
.accion-btn  {
  background: transparent; border: 1px solid var(--color-border);
  border-radius: 4px; padding: 0.25rem 0.6rem;
  font-size: var(--text-xs); font-family: var(--font-mono); letter-spacing: 0.05em;
  color: var(--color-text-muted); cursor: pointer; transition: all 0.12s;
}
.accion-btn:hover  { border-color: var(--color-text-dim); color: var(--color-text); }
.accion-btn.accion-gold { border-color: rgba(179,144,40,0.4); color: var(--color-gold); }
.accion-btn.accion-gold:hover { background: rgba(179,144,40,0.1); }

/* ── Grupo provacop (tab lotes) ──────────────────────────────────── */
.grupo-provacop { border-bottom: 1px solid var(--color-border); }
.grupo-provacop:last-child { border-bottom: none; }
.grupo-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.85rem 1rem;
  background: rgba(179,144,40,0.04);
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap; gap: 0.75rem;
}
.grupo-nombre { font-size: var(--text-md); font-weight: 600; color: var(--color-text); }
.grupo-sep    { color: var(--color-text-faint); margin: 0 0.35rem; }
.grupo-acop   { font-size: var(--text-md); color: var(--color-text-muted); }
.grupo-meta   {
  display: block; font-family: var(--font-mono); font-size: var(--text-xs);
  color: var(--color-text-faint); margin-top: 0.2rem; letter-spacing: 0.05em;
}
.btn-sm { padding: 0.4rem 0.9rem; font-size: var(--text-sm); white-space: nowrap; }

/* ── Chips ────────────────────────────────────────────────────────── */
.chip {
  display: inline-block; font-family: var(--font-mono); font-size: 0.65rem;
  padding: 0.12rem 0.5rem; border-radius: 2px; letter-spacing: 0.06em; white-space: nowrap;
}
.chip-ok    { background: var(--color-success-bg); color: var(--color-success); border: 1px solid rgba(81,161,85,0.3); }
.chip-dirim { background: rgba(179,144,40,0.12); color: var(--color-gold); border: 1px solid rgba(179,144,40,0.3); }

/* ── Días badge ──────────────────────────────────────────────────── */
.dias-badge {
  font-family: var(--font-mono); font-size: var(--text-xs);
  padding: 0.1rem 0.4rem; border-radius: 2px;
  background: rgba(255,255,255,0.04); border: 1px solid var(--color-border);
}
.dias-badge.dias-warn    { background: var(--color-warning-bg); border-color: rgba(207,151,61,0.4); color: var(--color-warning); }
.dias-badge.dias-peligro { background: var(--color-error-bg);   border-color: rgba(165,71,61,0.4);  color: var(--color-error); }

/* ── Estados vacíos / cargando ───────────────────────────────────── */
.estado-vacio   { padding: 3rem; text-align: center; font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-faint); }
.estado-cargando {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 2rem 1rem; font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted);
}
.spinner-sm {
  display: inline-block; width: 14px; height: 14px;
  border: 1.5px solid var(--color-border); border-top-color: var(--color-gold);
  border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.btn-con-icono { display: flex; align-items: center; gap: 0.4rem; }
/* Lotes Cards Compact Layout */
.lotes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
  background: var(--color-bg);
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  border: 1px solid var(--color-border);
  border-top: none;
}
.lote-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: all 0.2s ease;
}
.lote-card:hover {
  border-color: var(--color-gold);
  box-shadow: 0 2px 8px rgba(179,144,40,0.1);
}
.card-volado {
  background: rgba(var(--color-gold-rgb), 0.03);
  border-left: 3px solid var(--color-gold);
}
.card-alerta {
  background: rgba(220, 38, 38, 0.03);
  border-left: 3px solid var(--color-error);
}
.lc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed var(--color-border);
  padding-bottom: 0.5rem;
}
.lc-ip {
  font-family: var(--font-mono);
  color: var(--color-gold);
  font-weight: 700;
  font-size: var(--text-base);
}
.lc-body {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}
.lc-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.lc-full {
  grid-column: span 3;
  margin-top: 0.25rem;
  padding-top: 0.25rem;
  border-top: 1px solid rgba(255,255,255,0.03);
}
.lc-lbl {
  font-size: var(--text-xs);
  color: var(--color-text-dim);
  font-family: var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.lc-val {
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  font-weight: 500;
  color: var(--color-text);
}
.text-gold { color: var(--color-gold); }
.text-muted { color: var(--color-text-muted); }
</style>
