<template>
  <div class="terceros-page">

    <!-- ── Encabezado ──────────────────────────────────────── -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Terceros</h1>
        <p class="page-subtitle">Proveedores y acopiadores registrados</p>
      </div>
      <button
        v-if="puedeCrear"
        class="btn-primary ready"
        @click="abrirCrear"
      >
      <PlusCircle :size="18" /> Registrar
      </button>
    </div>

    <!-- ── Filtros ─────────────────────────────────────────── -->
    <div class="filtros-bar">
      <div class="field filtro-estado">
        <select v-model="filtroActivo" class="field-input field-select" @change="cargar">
          <option :value="undefined">Todos</option>
          <option :value="true">Activos</option>
          <option :value="false">Inactivos</option>
        </select>
      </div>

      <div class="field filtro-busqueda">
        <Search :size="18" />
        <input
          v-model="busqueda"
          class="field-input"
          placeholder="Buscar por nombre, RUC, referencia…"
        />
      </div>

      <button class="btn-secondary btn-refresh" @click="cargar" title="Actualizar">
        <span :class="['refresh-icon', { spinning: store.cargando }]">⟳</span>
      </button>
    </div>

    <!-- ── Estado de carga / error ────────────────────────── -->
    <div v-if="store.cargando" class="estado-carga">
      <span class="spinner-lg" />
      <span>Cargando terceros…</span>
    </div>

    <div v-else-if="store.error" class="estado-error">
      <span><X :size="18" /> {{ store.error }}</span>
      <button class="btn-link" @click="cargar">Reintentar</button>
    </div>

    <!-- ── Tabla ───────────────────────────────────────────── -->
    <template v-else>
      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>Razón Social</th>
              <th>RUC</th>
              <th>Referencia</th>
              <th>Acopiador</th>
              <th>Estado</th>
              <th class="col-acciones">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="listaFiltrada.length === 0">
              <td colspan="6" class="tabla-vacia">
                <CircleX :size="32" class="tabla-vacia-icon" />
                <span>{{ busqueda ? 'Sin resultados para esa búsqueda' : 'No hay terceros registrados' }}</span>
              </td>
            </tr>
            <tr
              v-for="t in listaFiltrada"
              :key="t.id"
              class="tabla-row"
              :class="{ inactivo: !t.activo }"
            >
              <td class="col-nombre">
                <span class="nombre-text">{{ t.razon_social }}</span>
              </td>
              <td class="col-mono">{{ t.ruc ?? '—' }}</td>
              <td class="col-ref">{{ t.referencia ?? '—' }}</td>
              <td class="col-acopiador">
                <span v-if="t.acopiador" class="acopiador-tag">{{ t.acopiador }}</span>
                <span v-else class="texto-vacio">—</span>
              </td>
              <td>
                <span class="badge-estado" :class="t.activo ? 'activo' : 'inactivo'">
                  {{ t.activo ? 'ACTIVO' : 'INACTIVO' }}
                </span>
              </td>
              <td class="col-acciones">
                <div class="acciones-grupo">
                  <!-- Editar -->
                  <button
                    v-if="puedeEditar"
                    class="btn-accion"
                    title="Editar"
                    @click="abrirEditar(t.id)"
                  ><Edit3 :size="16" /></button>

                  <!-- Activar / Desactivar -->
                  <button
                    v-if="puedeDesactivar"
                    class="btn-accion"
                    :class="t.activo ? 'accion-warn' : 'accion-ok'"
                    :title="t.activo ? 'Desactivar' : 'Activar'"
                    @click="toggleEstado(t)"
                  >
                    <PowerOff v-if="t.activo" :size="16" />
                    <Power v-else :size="16" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pie de tabla -->
      <div class="tabla-footer">
        <span class="tabla-count">
          {{ listaFiltrada.length }} de {{ store.lista.length }} registros
        </span>
      </div>
    </template>

    <!-- ── Modal Form ──────────────────────────────────────── -->
    <TerceroFormModal
      :visible="modalVisible"
      :tercero-id="terceroEditandoId"
      @cerrar="cerrarModal"
      @guardado="onGuardado"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTercerosStore } from '@/stores/terceros'
import { useAuthStore }     from '@/stores/auth'
import { useUiStore }       from '@/stores/ui'
import TerceroFormModal     from './TerceroFormModal.vue'
import type { TerceroLista, TerceroRespuesta } from '@/api/terceros'
import {
  Power,
  PowerOff,
  Edit3,
  CircleX,
  X,
  Search,
  PlusCircle
} from 'lucide-vue-next'
// ── Stores ────────────────────────────────────────────────────────────────────
const store = useTercerosStore()
const auth  = useAuthStore()
const ui    = useUiStore()

// ── RBAC ──────────────────────────────────────────────────────────────────────
const rol        = computed(() => auth.user?.rol ?? '')
const puedeCrear = computed(() => ['Admin', 'Gerencia', 'Comercial'].includes(rol.value))
const puedeEditar     = computed(() => ['Admin', 'Gerencia', 'Comercial'].includes(rol.value))
const puedeDesactivar = computed(() => ['Admin', 'Gerencia', 'Comercial'].includes(rol.value))

// ── State ─────────────────────────────────────────────────────────────────────
const filtroActivo        = ref<boolean | undefined>(true) // por defecto: activos
const busqueda            = ref('')
const modalVisible        = ref(false)
const terceroEditandoId   = ref<number | null>(null)

// ── Computed ──────────────────────────────────────────────────────────────────
const listaFiltrada = computed<TerceroLista[]>(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (!q) return store.lista
  return store.lista.filter(t =>
    t.razon_social.toLowerCase().includes(q) ||
    (t.ruc?.includes(q) ?? false) ||
    (t.referencia?.toLowerCase().includes(q) ?? false) ||
    (t.acopiador?.toLowerCase().includes(q) ?? false)
  )
})

// ── Actions ───────────────────────────────────────────────────────────────────
async function cargar() {
  try {
    await store.cargar(filtroActivo.value)
  } catch {
    // el error ya está en store.error
  }
}

function abrirCrear() {
  terceroEditandoId.value = null
  modalVisible.value      = true
}

function abrirEditar(id: number) {
  terceroEditandoId.value = id
  modalVisible.value      = true
}

function cerrarModal() {
  modalVisible.value = false
}

function onGuardado(_tercero: TerceroRespuesta) {
  cerrarModal()
  // La lista ya se actualiza en el store, no hace falta reload
}

async function toggleEstado(t: TerceroLista) {
  const accion   = t.activo ? 'desactivar' : 'activar'
  const confirmed = await ui.showConfirm({
    title:        t.activo ? 'Desactivar tercero' : 'Activar tercero',
    message:      t.activo
      ? `¿Desactivar a ${t.razon_social}? Dejará de estar disponible en operaciones.`
      : `¿Reactivar a ${t.razon_social}?`,
    confirmLabel: t.activo ? 'Desactivar' : 'Activar',
    danger:       t.activo,
  })
  if (!confirmed) return

  try {
    await store.toggleEstado(t.id, !t.activo)
    ui.toast(
      `${t.razon_social} ${t.activo ? 'desactivado' : 'activado'}`,
      t.activo ? 'warning' : 'success',
    )
    // Si el filtro está en "activos", refrescar para que desaparezca
    if (filtroActivo.value !== undefined) await cargar()
  } catch {
    ui.toast('Error al cambiar estado', 'error')
  }
}

onMounted(cargar)
</script>

<style scoped>
/* ── Header ─────────────────────────────────────────────────── */
.page-subtitle {
font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-top: 0.25rem;
  font-family: var(--font-mono);
  letter-spacing: 0.06em;
}

/* ── Filtros ─────────────────────────────────────────────────── */
.filtros-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filtro-estado   { width: 150px; flex-shrink: 0; }
.filtro-busqueda { flex: 1; min-width: 220px; }

.btn-refresh {
  padding: 0.6rem 0.85rem;
  min-height: 42px;
  font-size: var(--text-base);
  line-height: 1;
}

.refresh-icon { display: inline-block; transition: transform 0.4s; }
.refresh-icon.spinning { animation: spin 0.8s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Carga / error ───────────────────────────────────────────── */
.estado-carga,
.estado-error {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  font-family: var(--font-mono);
  font-size: var(--text-md);
  color: var(--color-text-muted);
}

.estado-error { color: var(--color-error); }

.spinner-lg {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-gold);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-gold);
  font-family: var(--font-mono);
  font-size: var(--text-md);
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

/* ── Tabla ───────────────────────────────────────────────────── */
.tabla-wrapper {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
}

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-md);
}

.tabla thead tr {
  background: rgba(179, 144, 40, 0.06);
  border-bottom: 1px solid var(--color-border);
}

.tabla th {
  padding: 0.7rem 1rem;
  text-align: left;
  font-family: var(--font-mono);
font-size: var(--text-xs);
  letter-spacing: 0.15em;
  color: var(--color-text-muted);
  text-transform: uppercase;
  white-space: nowrap;
}

.tabla-row {
  border-bottom: 1px solid rgba(58, 58, 40, 0.5);
  transition: background 0.1s;
}

.tabla-row:hover { background: rgba(179, 144, 40, 0.04); }

.tabla-row.inactivo { opacity: 0.5; }
.tabla-row.inactivo:hover { opacity: 0.7; }

.tabla td {
  padding: 0.75rem 1rem;
  color: var(--color-text);
  vertical-align: middle;
}

.col-nombre .nombre-text {
  font-weight: 600;
  color: var(--color-text);
}

.col-mono {
  font-family: var(--font-mono);
  font-size: var(--text-md);
  color: var(--color-text-muted);
}

.col-ref {
  font-size: var(--text-md);
  color: var(--color-text-dim);
}

.acopiador-tag {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background: rgba(179, 144, 40, 0.1);
  border: 1px solid rgba(179, 144, 40, 0.25);
  border-radius: 2px;
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  color: var(--color-gold);
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.texto-vacio { color: var(--color-text-faint); }

/* ── Badges ──────────────────────────────────────────────────── */
.badge-estado {
  display: inline-block;
  padding: 0.18rem 0.55rem;
  border-radius: 2px;
  font-family: var(--font-mono);
font-size: var(--text-xs);
  letter-spacing: 0.12em;
  font-weight: 700;
}

.badge-estado.activo {
  background: var(--color-success-bg);
  color: #4ade80;
  border: 1px solid rgba(81, 161, 85, 0.3);
}

.badge-estado.inactivo {
  background: rgba(100, 100, 80, 0.15);
  color: var(--color-text-dim);
  border: 1px solid var(--color-border);
}

/* ── Acciones ────────────────────────────────────────────────── */
.col-acciones { width: 90px; }

.acciones-grupo {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.btn-accion {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-base);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  font-family: var(--font-mono);
}

.btn-accion:hover          { border-color: var(--color-gold); color: var(--color-gold); }
.btn-accion.accion-warn:hover { border-color: var(--color-warning); color: var(--color-warning); }
.btn-accion.accion-ok:hover   { border-color: var(--color-success); color: var(--color-success); }

/* ── Vacío / footer ──────────────────────────────────────────── */
.tabla-vacia {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
  font-size: var(--text-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.tabla-vacia-icon {
  font-size: var(--text-xl);
  color: var(--color-border);
}

.tabla-footer {
  display: flex;
  justify-content: flex-end;
  padding: 0.6rem 1rem;
  border-top: 1px solid var(--color-border);
}

.tabla-count {
  font-family: var(--font-mono);
font-size: var(--text-sm);
  color: var(--color-text-faint);
  letter-spacing: 0.08em;
}
</style>
