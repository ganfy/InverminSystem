<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">
          <FlaskConical class="lucide" :size="24" style="margin-right:0.5rem" />
          Laboratorio
        </h1>
        <p class="page-subtitle">
          {{ tabActual === 'ley' ? 'Análisis de Ley' : 'Análisis de Recuperación' }}
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="recargar" :disabled="store.cargando">
          <RefreshCw :size="16" :class="{ spinner: store.cargando }" style="margin-right:0.4rem" />
          ACTUALIZAR
        </button>
      </div>
    </header>

    <div class="tabs-lab">
      <button class="tab-lab-btn" :class="{ active: tabActual === 'ley' }" @click="tabActual = 'ley'">
        Análisis de Ley
        <span class="tab-lab-toggle">{{ tabActual === 'ley' ? '︿' : '︾' }}</span>
      </button>
      <button class="tab-lab-btn" :class="{ active: tabActual === 'rec' }" @click="tabActual = 'rec'">
        Análisis de Recuperación
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
      <div class="field" style="min-width:160px">
        <label class="field-label">FECHA DESDE</label>
        <input type="date" class="field-input" v-model="filtroDesde" />
      </div>
      <div class="field" style="min-width:160px">
        <label class="field-label">FECHA HASTA</label>
        <input type="date" class="field-input" v-model="filtroHasta" />
      </div>
      <div class="field" style="flex:1;min-width:200px">
        <label class="field-label">BÚSQUEDA</label>
        <input type="text" class="field-input" v-model="filtroBusqueda" placeholder="CIP o IP" />
      </div>
    </div>

    <div class="tabla-wrapper">
      <table class="tabla">
        <thead>
          <tr>
            <th>CIP</th>
            <th v-if="store.puedeVerIP">IP</th>
            <th>FECHA ENVÍO</th>
            <template v-if="tabActual === 'ley'">
              <th>LABORATORIO</th>
              <th>MALLA +140</th>
              <th>MALLA -140</th>
              <th>AU OZ/TC</th>
              <th>AU GR/TM</th>
            </template>
            <template v-else>
              <th>LABORATORIO</th>
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
            <td :colspan="colSpan" class="estado-tabla">
              <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
            </td>
          </tr>
          <template v-else>
            <tr v-if="filasMostrar.length === 0">
              <td :colspan="colSpan" class="estado-tabla sin-datos">Sin registros</td>
            </tr>

            <template v-if="tabActual === 'ley'">
              <tr v-for="fila in filasMostrar" :key="fila.cip" :class="{ inactivo: fila.estado === 'DESCARTADO' }">
                <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                <td v-if="store.puedeVerIP" class="td-mono">{{ fila.lote_ip ?? '-' }}</td>
                <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                <td>{{ fila.laboratorio ?? '-' }}</td>
                <td>{{ fila.leyMas ?? '-' }}</td>
                <td>{{ fila.leyMenos ?? '-' }}</td>
                <td class="td-mono" style="color:var(--color-gold-light)">{{ fila.ozTc ?? '-' }}</td>
                <td class="td-mono">{{ fila.grTm ?? '-' }}</td>
                <td>
                  <span class="badge-estado" :class="badgeClass(fila.estado)">{{ fila.estado }}</span>
                </td>
                <!-- AFTER -->
                <td class="td-acciones">
                  <button
                    v-if="store.esLaboratorista && fila.estado === 'PENDIENTE'"
                    class="btn-primary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irARegistrarLey(fila.cip)"
                  >Registrar</button>
                  <button
                    v-if="store.puedeImportarCert && fila.estado === 'PENDIENTE'"
                    class="btn-primary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irAImportarLey(fila.cip)"
                  >Importar cert.</button>
                  <button
                    v-if="store.puedeVerIP && fila.lote_ip && fila.estado === 'COMPLETADO'"
                    class="btn-secondary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irADetalleLote(fila.lote_ip!)"
                  >Detalle</button>
                </td>
              </tr>
            </template>

            <template v-if="tabActual === 'rec'">
              <tr v-for="fila in filasMostrar" :key="fila.cip">
                <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                <td v-if="store.puedeVerIP" class="td-mono">{{ fila.lote_ip ?? '-' }}</td>
                <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                <td>{{ fila.laboratorio ?? '-' }}</td>
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
                  <button
                    v-if="store.esLaboratorista && fila.estado === 'PENDIENTE'"
                    class="btn-primary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irARegistrarRecuperacion(fila.cip)"
                  >Registrar</button>
                  <button
                    v-if="store.puedeImportarCert && fila.estado === 'PENDIENTE'"
                    class="btn-primary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irAImportarRec(fila.cip)"
                  >Importar cert.</button>
                  <button
                    v-if="store.puedeVerIP && fila.lote_ip && fila.estado === 'COMPLETADO'"
                    class="btn-secondary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irADetalleLote(fila.lote_ip!)"
                  >Detalle</button>
                </td>
              </tr>
            </template>

          </template>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FlaskConical, RefreshCw } from 'lucide-vue-next'
import { useLaboratorioStore } from '@/stores/laboratorio'
import type { CIPAnalisisOut } from '@/types/laboratorio'

const router = useRouter()
const store  = useLaboratorioStore()

const tabActual      = ref<'ley' | 'rec'>('ley')
const filtroEstado   = ref('')
const filtroDesde    = ref('')
const filtroHasta    = ref('')
const filtroBusqueda = ref('')

onMounted(() => store.cargarCips())
function recargar() { store.cargarCips() }

const colSpan = computed(() => {
  const base = tabActual.value === 'ley' ? 9 : 9
  return store.puedeVerIP ? base + 1 : base
})

// Cantidad de recuperaciones PENDIENTE (badge en tab)
const pendientesRec = computed(() =>
  store.cips.filter(c =>
    (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno') &&
    c.estado_recuperacion === 'PENDIENTE'
  ).length
)

interface Fila {
  cip: string
  lote_ip?: string | null
  fecha_envio?: string | null
  laboratorio?: string | null
  estado: string
  analisisId?: number | null
  // ley
  leyMas?: number | null
  leyMenos?: number | null
  ozTc?: number | null
  grTm?: number | null
  // rec
  leyCabeza?: number | null
  leyCola?: number | null
  leyLiquido?: number | null
  recuperacion?: number | null
}

function mapearCIP(c: CIPAnalisisOut): Fila {
  if (tabActual.value === 'ley') {
    const a = c.analisis_ley.find(x => x.vigente) ?? c.analisis_ley[0]
    return {
      cip: c.cip,
      lote_ip: c.lote_ip,
      fecha_envio: c.fecha_envio,
      laboratorio: a?.laboratorio ?? c.laboratorio_destino,
      estado: c.estado_ley,
      leyMas: a?.ley_grueso ?? null,
      leyMenos: a?.ley_fino ?? null,
      ozTc: a?.ley_final ?? null,
      grTm: a?.ley_gr_tm ?? null,
    }
  } else {
    // Para rec: tomar el PENDIENTE primero, si no el último COMPLETADO vigente
    const pending = c.analisis_recuperacion.find(x => x.estado === 'PENDIENTE' && x.vigente)
    const completado = c.analisis_recuperacion.find(x => x.estado === 'COMPLETADO' && x.vigente)
    const a = pending ?? completado
    return {
      cip: c.cip,
      lote_ip: c.lote_ip,
      fecha_envio: c.fecha_envio,
      laboratorio: a?.laboratorio ?? c.laboratorio_destino,
      estado: c.estado_recuperacion === 'SIN_DATOS' ? 'SIN DATOS' : c.estado_recuperacion,
      analisisId: pending?.id ?? null,
      leyCabeza: a?.ley_cabeza ?? null,
      leyCola: a?.ley_cola ?? null,
      leyLiquido: a?.ley_liquido ?? null,
      recuperacion: a?.recuperacion ?? null,
    }
  }
}

const filasMostrar = computed(() => {
  // Filtrar CIPs por tipo según tab
  const cipsFiltrados = store.cips.filter(c => {
    if (tabActual.value === 'ley') return c.tipo_muestra === 'Laboratorio'
    return (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno')
  })

  return cipsFiltrados
    .map(mapearCIP)
    .filter(f => {
      if (filtroEstado.value && f.estado !== filtroEstado.value) return false
      if (filtroBusqueda.value) {
        const q = filtroBusqueda.value.toLowerCase()
        if (!f.cip.toLowerCase().includes(q) && !(f.lote_ip ?? '').toLowerCase().includes(q)) return false
      }
      if (filtroDesde.value && f.fecha_envio && f.fecha_envio < filtroDesde.value) return false
      if (filtroHasta.value && f.fecha_envio && f.fecha_envio > filtroHasta.value) return false
      return true
    })
})

function fmt(d?: string | null) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function badgeClass(estado: string) {
  const m: Record<string, string> = {
    COMPLETADO: 'completo',
    PENDIENTE: 'pendiente',
    'SIN DATOS': 'parcial',
  }
  return m[estado] ?? ''
}

function irARegistrarLey(cip: string)          { router.push(`/laboratorio/ley/${cip}`) }
// Laboratorista completa recuperacion: lleva el analisis_id como query param
function irACompletarRecuperacion(cip: string, analisisId: number) {
  router.push(`/laboratorio/recuperacion/${cip}?id=${analisisId}`)
}
function irARegistrarRecuperacion(cip: string) { router.push(`/laboratorio/recuperacion/${cip}`) }
function irADetalleLote(ip: string) { router.push(`/laboratorio/lote/${ip}`) }
function irAImportarLey(cip: string) { router.push(`/laboratorio/importar-ley/${cip}`) }
function irAImportarRec(cip: string) { router.push(`/laboratorio/importar-rec/${cip}`) }

</script>

<style scoped>
.tabs-lab {
  display: flex;
  gap: 0;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.tab-lab-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  padding: 0.6rem 1.25rem;
  font-size: var(--text-md);
  font-family: var(--font-mono);
  cursor: pointer;
  letter-spacing: 0.04em;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-lab-btn.active {
  color: var(--color-gold);
  border-bottom-color: var(--color-gold);
}

.tab-lab-toggle {
  font-size: 0.7rem;
  color: var(--color-text-faint);
}

.badge-count {
  background: var(--color-error, #ef4444);
  color: #fff;
  font-size: 0.65rem;
  font-family: var(--font-mono);
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  min-width: 1.2rem;
  text-align: center;
}

.filtros-bar {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
</style>
