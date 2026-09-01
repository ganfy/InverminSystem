<template>
  <div class="page-container">

    <!-- Header -->
    <header class="page-header">
      <div style="display:flex;align-items:center;gap:0.75rem">
        <button class="btn-back" @click="router.back()">
          <ChevronLeft :size="20" />
        </button>
        <div>
          <h1 class="page-title">
            <TrendingUp :size="24" style="margin-right:0.5rem" />
            Histórico de Precios Spot
          </h1>
          <p class="page-subtitle">LBMA Gold PM Fix &amp; Silver Noon Fix — registro diario</p>
        </div>
      </div>
      <div style="display:flex;gap:0.5rem">
        <button class="btn-secondary" @click="fetchHoy" :disabled="cargandoScraping">
          <RefreshCw :size="15" :class="{ 'spin': cargandoScraping }" />
          {{ cargandoScraping ? 'Actualizando…' : 'Actualizar spot' }}
        </button>
        <button class="btn-primary" @click="abrirModalNuevo">
          <Plus :size="16" />
          Registrar spot
        </button>
      </div>
    </header>

    <!-- Indicador de regla fin de semana -->
    <div class="info-banner">
      <Info :size="16" />
      <span>
        <strong>Regla de aplicación:</strong> El spot usado por cada IP es el de su fecha de recepción.
        Si la recepción fue en <strong>sábado</strong>, se aplica el del <strong>viernes anterior</strong>;
        si fue en <strong>domingo</strong>, el del <strong>lunes siguiente</strong>.
      </span>
    </div>

    <!-- Filtros -->
    <div class="filtros-bar">
      <div class="filtro-grupo">
        <label>Desde</label>
        <input type="date" v-model="filtroDesde" class="field-input" @change="cargar" />
      </div>
      <div class="filtro-grupo">
        <label>Hasta</label>
        <input type="date" v-model="filtroHasta" class="field-input" @change="cargar" />
      </div>
      <button class="btn-ghost" @click="limpiarFiltros">Limpiar</button>
    </div>

    <!-- Tabla -->
    <div class="tabla-card">
      <div v-if="cargando" class="estado-vacio">
        <span class="spinner" /> Cargando…
      </div>
      <div v-else-if="spots.length === 0" class="estado-vacio">
        Sin registros. Use "Registrar spot" o "Actualizar spot".
      </div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Día</th>
            <th class="col-r">Au (USD/Oz)</th>
            <th class="col-r">Ag (USD/Oz)</th>
            <th>Fuente</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in spots" :key="s.id" :class="{ 'fila-fin-semana': esFindeSemana(s.fecha) }">
            <td class="mono">{{ fmtFecha(s.fecha) }}</td>
            <td class="dia-semana" :class="claseDia(s.fecha)">{{ nombreDia(s.fecha) }}</td>
            <td class="col-r mono gold">
              <span class="badge-precio">$ {{ fmtNum(s.precio_au_usd, 2) }}</span>
            </td>
            <td class="col-r mono silver">
              {{ s.precio_ag_usd != null ? `$ ${fmtNum(s.precio_ag_usd, 2)}` : '—' }}
            </td>
            <td>
              <span class="badge-fuente" :class="s.fuente === 'SCRAPING' ? 'badge-auto' : 'badge-manual'">
                <Zap v-if="s.fuente === 'SCRAPING'" :size="11" />
                <PenLine v-else :size="11" />
                {{ s.fuente === 'SCRAPING' ? 'Auto' : 'Manual' }}
              </span>
            </td>
            <td>
              <button class="btn-icon-danger" @click="confirmarEliminar(s)" title="Eliminar">
                <Trash2 :size="14" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal: Nuevo Spot -->
    <Teleport to="body">
      <div v-if="modalAbierto" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal-box">
          <div class="modal-header">
            <h2>Registrar Spot</h2>
            <button class="btn-icon" @click="cerrarModal"><X :size="18" /></button>
          </div>
          <div class="modal-body">
            <div class="field">
              <label class="field-label">Fecha</label>
              <input type="date" class="field-input" v-model="form.fecha" />
              <p v-if="form.fecha && esFindeSemana(form.fecha)" class="field-hint warning">
                <AlertTriangle :size="16" style="flex-shrink:0;margin-top:1px" />
                 Esta fecha es fin de semana. El LBMA no publica Fix en fines de semana.
                Para sábado, el sistema usará automáticamente el viernes anterior;
                para domingo, el lunes siguiente.
              </p>
            </div>
            <div class="field">
              <label class="field-label">Precio Au (USD/Oz Troy) <span class="req">*</span></label>
              <input type="number" class="field-input" v-model.number="form.precio_au_usd"
                min="0" step="0.01" placeholder="ej: 2650.00" />
            </div>
            <div class="field">
              <label class="field-label">Precio Ag (USD/Oz Troy) <span class="opt">opcional</span></label>
              <input type="number" class="field-input" v-model.number="form.precio_ag_usd"
                min="0" step="0.01" placeholder="ej: 31.50" />
            </div>
            <p v-if="errorModal" class="error-text">{{ errorModal }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">Cancelar</button>
            <button class="btn-primary" @click="guardarSpot" :disabled="guardando">
              {{ guardando ? 'Guardando…' : 'Guardar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronLeft, TrendingUp, Plus, RefreshCw, Trash2, X, Info, Zap, PenLine, AlertTriangle } from 'lucide-vue-next'
import { useUiStore } from '@/stores/ui'
import {
  getSpotHistorico,
  crearSpotHistorico,
  eliminarSpotHistorico,
  obtenerPrecioOro,
  type SpotHistoricoOut,
} from '@/api/liquidaciones'

const router = useRouter()
const ui = useUiStore()

const spots = ref<SpotHistoricoOut[]>([])
const cargando = ref(false)
const cargandoScraping = ref(false)
const filtroDesde = ref('')
const filtroHasta = ref('')

// Modal
const modalAbierto = ref(false)
const guardando = ref(false)
const errorModal = ref('')
const form = ref({ fecha: '', precio_au_usd: null as number | null, precio_ag_usd: null as number | null })

// ── Helpers de fecha ──────────────────────────────────────────────────────────

function parseDate(d: string): Date {
  const [y, m, day] = d.split('-').map(Number)
  return new Date(y, m - 1, day)
}

function esFindeSemana(fecha: string): boolean {
  const d = parseDate(fecha)
  return d.getDay() === 0 || d.getDay() === 6
}

function nombreDia(fecha: string): string {
  const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
  return dias[parseDate(fecha).getDay()]
}

function claseDia(fecha: string): string {
  const d = parseDate(fecha).getDay()
  if (d === 0 || d === 6) return 'dia-finde'
  return ''
}

function fmtFecha(d: string): string {
  return parseDate(d).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function fmtNum(v: number | null | undefined, d = 2): string {
  if (v == null) return '—'
  return v.toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
}

// ── Carga ─────────────────────────────────────────────────────────────────────

async function cargar() {
  cargando.value = true
  try {
    const res = await getSpotHistorico({
      desde: filtroDesde.value || undefined,
      hasta: filtroHasta.value || undefined,
      limit: 200,
    })
    spots.value = res.data
  } catch {
    ui.toast('Error al cargar el histórico de spots', 'error')
  } finally {
    cargando.value = false
  }
}

function limpiarFiltros() {
  filtroDesde.value = ''
  filtroHasta.value = ''
  cargar()
}

// ── Scraping on-demand ────────────────────────────────────────────────────────

async function fetchHoy() {
  cargandoScraping.value = true
  try {
    const valor = await obtenerPrecioOro(true) // guardar=true
    if (valor) {
      ui.toast(`Precio Au obtenido y guardado: $${valor.toFixed(2)}/Oz`, 'success')
      await cargar()
    } else {
      ui.toast('No se pudo obtener el precio del oro. Verifique la conexión.', 'error')
    }
  } catch {
    ui.toast('Error al obtener precio', 'error')
  } finally {
    cargandoScraping.value = false
  }
}

// ── Modal Nuevo ───────────────────────────────────────────────────────────────

function abrirModalNuevo() {
  // Pre-llenar con hoy
  const hoy = new Date()
  form.value = {
    fecha: hoy.toISOString().split('T')[0],
    precio_au_usd: null,
    precio_ag_usd: null,
  }
  errorModal.value = ''
  modalAbierto.value = true
}

function cerrarModal() {
  modalAbierto.value = false
}

async function guardarSpot() {
  errorModal.value = ''
  if (!form.value.fecha) { errorModal.value = 'Seleccione una fecha'; return }
  if (!form.value.precio_au_usd || form.value.precio_au_usd <= 0) {
    errorModal.value = 'Ingrese el precio del oro (Au)'; return
  }
  guardando.value = true
  try {
    await crearSpotHistorico({
      fecha: form.value.fecha,
      precio_au_usd: form.value.precio_au_usd,
      precio_ag_usd: form.value.precio_ag_usd || null,
      fuente: 'MANUAL',
    })
    ui.toast('Spot registrado correctamente', 'success')
    cerrarModal()
    await cargar()
  } catch (e: any) {
    errorModal.value = e?.response?.data?.detail || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

// ── Eliminar ──────────────────────────────────────────────────────────────────

async function confirmarEliminar(s: SpotHistoricoOut) {
  const ok = await ui.showConfirm({
    title: 'Eliminar Spot',
    message: `¿Eliminar el registro de precio del ${fmtFecha(s.fecha)}? Esto puede afectar liquidaciones futuras.`,
    confirmLabel: 'Eliminar',
    danger: true,
  })
  if (!ok) return
  try {
    await eliminarSpotHistorico(s.id)
    ui.toast('Registro eliminado', 'success')
    await cargar()
  } catch {
    ui.toast('Error al eliminar', 'error')
  }
}

onMounted(cargar)
</script>

<style scoped>
.page-container { padding: 1.5rem; max-width: 900px; margin: 0 auto; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-gold);
  display: flex;
  align-items: center;
}

.page-subtitle { font-size: 0.85rem; color: var(--color-text-muted); margin-top: 0.15rem; }

.btn-back {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.4rem;
  cursor: pointer;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--color-bg-card);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-ghost {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
}

.btn-ghost:hover { background: var(--color-bg-hover); }

/* Info Banner */
.info-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  background: color-mix(in srgb, var(--color-primary) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 0.85rem;
  color: var(--color-text);
  margin-bottom: 1rem;
  line-height: 1.5;
}

/* Filtros */
.filtros-bar {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filtro-grupo { display: flex; flex-direction: column; gap: 0.25rem; }
.filtro-grupo label { font-size: 0.75rem; font-weight: 600; color: var(--color-text-muted); }

/* Tabla */
.tabla-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  overflow: hidden;
}

.tabla { width: 100%; border-collapse: collapse; }
.tabla th {
  background: var(--color-bg-subtle);
  padding: 0.6rem 0.9rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.tabla td {
  padding: 0.65rem 0.9rem;
  font-size: 0.875rem;
  border-bottom: 1px solid var(--color-border-subtle, var(--color-border));
  color: var(--color-text);
}

.tabla tr:last-child td { border-bottom: none; }
.tabla tr:hover td { background: var(--color-bg-hover, rgba(0,0,0,0.02)); }

.fila-fin-semana td { opacity: 0.55; font-style: italic; }

.col-r { text-align: right; }
.mono { font-family: 'Roboto Mono', monospace; }

.gold { color: #b8860b; font-weight: 600; }
.silver { color: #708090; }

.badge-precio {
  background: color-mix(in srgb, #c8a84b 15%, transparent);
  border: 1px solid color-mix(in srgb, #c8a84b 40%, transparent);
  border-radius: 6px;
  padding: 0.15rem 0.5rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #8b6914;
}

.dia-semana { font-weight: 600; font-size: 0.8rem; }
.dia-finde { color: var(--color-text-muted); font-style: italic; }

.badge-fuente {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
}

.badge-auto {
  background: color-mix(in srgb, var(--color-success, #22c55e) 12%, transparent);
  color: var(--color-success, #16a34a);
  border: 1px solid color-mix(in srgb, var(--color-success, #22c55e) 30%, transparent);
}
.badge-manual {
  background: color-mix(in srgb, var(--color-primary) 10%, transparent);
  color: var(--color-primary);
  border: 1px solid color-mix(in srgb, var(--color-primary) 28%, transparent);
}

.btn-icon-danger {
  background: none;
  border: none;
  color: var(--color-danger, #e53935);
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 6px;
  display: flex;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.btn-icon-danger:hover { opacity: 1; background: rgba(229, 57, 53, 0.08); }

/* Estado vacío */
.estado-vacio {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
  padding: 3rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-box {
  background: var(--color-bg-card);
  border-radius: 12px;
  width: 420px;
  max-width: 95vw;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 { font-size: 1rem; font-weight: 700; }

.modal-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
}

.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field-label { font-size: 0.8rem; font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; }
.field-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.9rem;
  background: var(--color-bg);
  color: var(--color-text);
}
.field-input:focus { outline: none; border-color: var(--color-primary); }

.field-hint { font-size: 0.78rem; color: var(--color-text-muted); }
.field-hint.warning { color: #b45309; }

.req { color: var(--color-danger, #e53935); }
.opt { color: var(--color-text-faint); font-size: 0.75rem; font-weight: 400; text-transform: none; }

.error-text { font-size: 0.8rem; color: var(--color-danger, #e53935); }

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-muted);
  padding: 0.25rem;
  border-radius: 4px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
