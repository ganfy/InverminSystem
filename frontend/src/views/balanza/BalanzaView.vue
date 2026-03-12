<template>
  <div class="balanza-page">
    <div class="page-header">
      <h1 class="page-title">Balanza</h1>
      <button class="btn-primary ready" @click="router.push({ name: 'RegistrarCamion' })">
        + Nuevo pesaje
      </button>
    </div>

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
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBalanzaStore } from '@/stores/balanza'

const router = useRouter()
const store  = useBalanzaStore()

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
function formatFecha(iso: string) {
  const utc = (iso.includes('+') || iso.endsWith('Z')) ? iso : iso + 'Z'
  return new Date(utc).toLocaleString('es-PE', {
    timeZone: 'America/Lima',
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
function estadoClass(e: string) { return { EN_PROCESO: 'en-proceso', PAUSADO: 'pausado', COMPLETO: 'completo' }[e] ?? '' }
function estadoLabel(e: string) { return { EN_PROCESO: 'EN PROCESO', PAUSADO: 'PAUSADO', COMPLETO: 'COMPLETO' }[e] ?? e }

onMounted(aplicarFiltros)
</script>

<style scoped>
.filtros     { display: flex; gap: 0.6rem; margin-bottom: 1.25rem; flex-wrap: wrap; align-items: center; }
.filtro-sm   { width: 160px; }
.filtro-busq { flex: 1; min-width: 220px; }
.fila-sesion { cursor: pointer; }
.td-muted    { color: var(--color-text-muted); }
.td-placa    { letter-spacing: 0.05em; }
.lotes-parcial { color: var(--color-warning); }
.sin-datos   { text-align: center; padding: 2rem; color: var(--color-text-muted); }
</style>
