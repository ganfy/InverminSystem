<template>
  <div class="balanza-page">
    <div class="page-header">
      <h1 class="page-title">Balanza</h1>
      <button class="btn-primary ready" @click="router.push({ name: 'RegistrarCamion' })">
        + Nuevo pesaje
      </button>
    </div>

    <!-- ── [OFFLINE] Sesiones pendientes de sincronizar ──── -->
    <div v-if="sesionesOffline.length > 0" class="offline-section">
      <div class="offline-section-header">
        <span class="offline-section-titulo">⚡ SIN SINCRONIZAR</span>
        <span class="offline-section-count">{{ sesionesOffline.length }} sesión(es) local(es)</span>
      </div>
      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>Fecha / Hora</th>
              <th>Proveedor</th>
              <th>Placa</th>
              <th>Lotes</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in sesionesOffline"
              :key="s.offline_id"
              class="fila-sesion fila-offline"
              @click="router.push({ name: 'SesionBalanza', params: { id: s.offline_id } })"
            >
              <td class="td-mono">{{ formatFechaLocal(s.creado_en) }}</td>
              <td>{{ s.proveedor_razon_social || '(sin caché)' }}</td>
              <td class="td-mono td-placa">{{ s.placa }}</td>
              <td class="td-mono">{{ s.lotes.length }}</td>
              <td>
                <span class="badge-estado" :class="estadoClass(s.estado)">
                  {{ estadoLabel(s.estado) }}
                </span>
                <span class="badge-local">LOCAL</span>
              </td>
              <td class="td-acciones" @click.stop>
                <button
                  class="btn-icon"
                  @click="router.push({ name: 'SesionBalanza', params: { id: s.offline_id } })"
                >✎</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Filtros ────────────────────────────────────────── -->
    <div class="filtros">
      <select class="field-input filtro-sm field-select" v-model="filtros.estado" @change="aplicarFiltros">
        <option value="">Todos los estados</option>
        <option value="EN_PROCESO">En proceso</option>
        <option value="PAUSADO">Pausado</option>
        <option value="COMPLETO">Completo</option>
      </select>
      <input class="field-input filtro-sm" type="date" v-model="filtros.fecha_desde" @change="aplicarFiltros" title="Desde" />
      <input class="field-input filtro-sm" type="date" v-model="filtros.fecha_hasta" @change="aplicarFiltros" title="Hasta" />
      <input class="field-input filtro-busq" v-model="filtros.busqueda" placeholder="IP, Proveedor, Placa, GRE..." @input="onBusquedaInput" />
      <button class="btn-secondary" @click="limpiarFiltros">Limpiar</button>
    </div>

    <div class="tabla-wrapper">
      <div v-if="store.loading" class="estado-tabla">Cargando...</div>
      <table v-else class="tabla">
        <thead>
          <tr>
            <th>Fecha / Hora</th>
            <th>Proveedor</th>
            <th>Acopiador</th>
            <th>Placa</th>
            <th>GRE</th>
            <th>Lotes</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.sesiones.length === 0">
            <td colspan="8" class="sin-datos">Sin sesiones registradas</td>
          </tr>
          <tr
            v-for="s in store.sesiones" :key="s.id"
            class="fila-sesion"
            @click="router.push({ name: 'SesionBalanza', params: { id: s.id } })"
          >
            <td class="td-mono">{{ formatFecha(s.fecha_ingreso) }}</td>
            <td>{{ s.proveedor_razon_social }}</td>
            <td class="td-muted">{{ s.es_propio ? '—' : s.acopiador_razon_social }}</td>
            <td class="td-mono td-placa">{{ s.placa }}</td>
            <td class="td-mono td-muted">{{ s.guia_remision || '—' }}</td>
            <td class="td-mono">
              <span :class="s.lotes_activos < s.total_lotes ? 'lotes-parcial' : ''">{{ s.lotes_activos }}</span>
              <span class="td-muted"> / {{ s.total_lotes }}</span>
            </td>
            <td>
              <span class="badge-estado" :class="estadoClass(s.estado)">{{ estadoLabel(s.estado) }}</span>
            </td>
            <td class="td-acciones" @click.stop>
              <button class="btn-icon" @click="router.push({ name: 'SesionBalanza', params: { id: s.id } })">✎</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBalanzaStore } from '@/stores/balanza'
import { obtenerSesionesPendientes, obtenerProvacops, obtenerFinalizacionesPendientes } from '@/composables/useOfflineQueue'
import type { SesionOfflineData } from '@/composables/useOfflineQueue'
import { watch } from 'vue'
import { useSync } from '@/composables/useSync'

const router = useRouter()
const store  = useBalanzaStore()

const { pendientes } = useSync()

watch(pendientes, () => {
  cargarSesionesOffline()
})

// ── [OFFLINE] Sesiones locales ────────────────────────────
// Enriquecemos SesionOfflineData con el nombre del proveedor (de la caché)
interface SesionOfflineVista extends SesionOfflineData {
  proveedor_razon_social: string
}

const sesionesOffline = ref<SesionOfflineVista[]>([])

async function cargarSesionesOffline() {
  try {
    const [pendientes, cache, finalizaciones] = await Promise.all([
      obtenerSesionesPendientes(),
      obtenerProvacops(),
      obtenerFinalizacionesPendientes(),  // para refrescar estado de sesiones con finalización pendiente
    ])
    // Excluir las ya sincronizadas
    sesionesOffline.value = pendientes
      .filter(s => !s.synced)
      .map(s => ({
        ...s,
        proveedor_razon_social:
          cache.find(p => p.provacop_id === s.provacop_id)?.proveedor_razon_social
          ?? '(sin caché)',
      }))

    // Aplicar estados locales de finalizaciones híbridas sobre la lista del servidor
    if (finalizaciones.length > 0) {
      const idsFinalizados = new Set(finalizaciones.map(f => f.sesion_id))
      store.sesiones = store.sesiones.map(s =>
        idsFinalizados.has(s.id) ? { ...s, estado: 'COMPLETO' } : s
      )
    }
  } catch (e) {
    console.error('cargarSesionesOffline:', e)
  }
}

// ── Filtros online ────────────────────────────────────────
const filtros = reactive({ estado: '', fecha_desde: '', fecha_hasta: '', busqueda: '' })
let timer: ReturnType<typeof setTimeout> | null = null

function aplicarFiltros() {
  store.cargarSesiones({
    estado:      filtros.estado      || undefined,
    fecha_desde: filtros.fecha_desde || undefined,
    fecha_hasta: filtros.fecha_hasta || undefined,
    busqueda:    filtros.busqueda    || undefined,
  })
}
function onBusquedaInput() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(aplicarFiltros, 350)
}
function limpiarFiltros() {
  Object.assign(filtros, { estado: '', fecha_desde: '', fecha_hasta: '', busqueda: '' })
  aplicarFiltros()
}

// ── Formato fechas ────────────────────────────────────────
function formatFecha(iso: string) {
  const utc = (iso.includes('+') || iso.endsWith('Z')) ? iso : iso + 'Z'
  return new Date(utc).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
function formatFechaLocal(iso: string) {
  // Las fechas offline son locales (sin sufijo Z) — no convertir TZ
  return new Date(iso).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function estadoClass(e: string) {
  return { EN_PROCESO: 'en-proceso', PAUSADO: 'pausado', COMPLETO: 'completo' }[e] ?? ''
}
function estadoLabel(e: string) {
  return { EN_PROCESO: 'EN PROCESO', PAUSADO: 'PAUSADO', COMPLETO: 'COMPLETO' }[e] ?? e
}

onMounted(async() => {
  aplicarFiltros()
  await store.cargarSesiones()
  await cargarSesionesOffline()
})
</script>

<style scoped>
/* ── [OFFLINE] Sección sin sincronizar ───────────────────── */
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
  font-family: var(--font-mono); font-size: .72rem;
  letter-spacing: .18em; color: #f59e0b;
}
.offline-section-count {
  font-family: var(--font-mono); font-size: .7rem; color: var(--color-text-muted);
}
.fila-offline { background: rgba(245,158,11,.04); }
.fila-offline:hover { background: rgba(245,158,11,.09) !important; }
.badge-local {
  font-family: var(--font-mono); font-size: .6rem; letter-spacing: .1em;
  background: rgba(245,158,11,.15); color: #f59e0b;
  border: 1px solid rgba(245,158,11,.3); border-radius: 3px;
  padding: 1px 5px; margin-left: .4rem; vertical-align: middle;
}

/* ── Resto (sin cambios respecto al original) ────────────── */
.filtros     { display: flex; gap: 0.6rem; margin-bottom: 1.25rem; flex-wrap: wrap; align-items: center; }
.filtro-sm   { width: 160px; }
.filtro-busq { flex: 1; min-width: 220px; }
.fila-sesion { cursor: pointer; }
.td-muted    { color: var(--color-text-muted); }
.td-placa    { letter-spacing: 0.05em; }
.lotes-parcial { color: var(--color-warning); }
.sin-datos   { text-align: center; padding: 2rem; color: var(--color-text-muted); }
</style>
