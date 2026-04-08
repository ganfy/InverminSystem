<template>
  <div class="page-container">

    <!-- Header -->
    <header class="page-header">
      <div>
        <h1 class="page-title">
          <FlaskConical class="lucide" :size="24" style="margin-right:0.5rem" />
          Laboratorio
        </h1>
        <p class="page-subtitle">
          {{ tabActual === 'ley' ? 'Análisis de Ley de Newmont' : 'Análisis de Recuperación' }}
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="recargar" :disabled="store.cargando">
          <RefreshCw :size="16" :class="{ spinner: store.cargando }" style="margin-right:0.4rem" />
          ACTUALIZAR
        </button>
      </div>
    </header>

    <!-- Tabs: toggle Ley / Recuperación -->
    <div class="tabs-lab">
      <button
        class="tab-lab-btn"
        :class="{ active: tabActual === 'ley' }"
        @click="tabActual = 'ley'"
      >
        Análisis de Ley de Newmont
        <span class="tab-lab-toggle">{{ tabActual === 'ley' ? '︿' : '︾' }}</span>
      </button>
      <button
        class="tab-lab-btn"
        :class="{ active: tabActual === 'rec' }"
        @click="tabActual = 'rec'"
      >
        Análisis de Recuperación
        <span class="tab-lab-toggle">{{ tabActual === 'rec' ? '︿' : '︾' }}</span>
      </button>
    </div>

    <!-- Filtros -->
    <div class="filtros-bar">
      <div class="field" style="min-width:180px">
        <label class="field-label">ESTADO</label>
        <select class="field-select" v-model="filtroEstado">
          <option value="">Todos los estados</option>
          <option value="PENDIENTE">Pendiente</option>
          <option value="COMPLETADO">Completado</option>
          <option value="PARCIAL">Parcial</option>
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
        <input type="text" class="field-input" v-model="filtroBusqueda" placeholder="CIP" />
      </div>
    </div>

    <!-- Tabla -->
    <div class="tabla-wrapper">
      <table class="tabla">
        <thead>
          <tr>
            <th>LOTE (CIP)</th>
            <!-- IP solo si puede verlo (Comercial/Admin/Gerencia) -->
            <th v-if="store.puedeVerIP">IP</th>
            <th>FECHA RECEP.</th>
            <!-- Columnas según tab -->
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
            <td :colspan="colSpan" class="estado-tabla">
              <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
            </td>
          </tr>
          <template v-else>
            <tr v-if="filasMostrar.length === 0">
              <td :colspan="colSpan" class="estado-tabla sin-datos">Sin registros</td>
            </tr>

            <!-- ── Tab LEY ────────────────────────────────────────────── -->
            <template v-if="tabActual === 'ley'">
              <tr v-for="fila in filasMostrar" :key="fila.cip" :class="{ inactivo: fila.estadoLey === 'DESCARTADO' }">
                <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                <td v-if="store.puedeVerIP" class="td-mono">{{ fila.lote_ip ?? '-' }}</td>
                <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                <td>{{ fila.leyMasNum ?? '-' }}</td>
                <td>{{ fila.leyMenosNum ?? '-' }}</td>
                <td class="td-mono" style="color:var(--color-gold-light)">{{ fila.ozTc ?? '-' }}</td>
                <td class="td-mono">{{ fila.grTm ?? '-' }}</td>
                <td>
                  <span class="badge-estado" :class="badgeClass(fila.estadoLey)">
                    {{ fila.estadoLey }}
                  </span>
                </td>
                <td class="td-acciones">
                  <button
                    v-if="fila.estadoLey === 'PENDIENTE'"
                    class="btn-primary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irARegistrarLey(fila.cip)"
                    title="Registrar ley"
                  >Registrar</button>
                  <!-- Ver detalle: solo Comercial+ que ve IP -->
                  <button
                    v-if="store.puedeVerIP && fila.lote_ip"
                    class="btn-secondary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irADetalleLote(fila.lote_ip!)"
                    title="Ver detalle del lote"
                  >Detalle</button>
                </td>
              </tr>
            </template>

            <!-- ── Tab RECUPERACIÓN ──────────────────────────────────── -->
            <template v-if="tabActual === 'rec'">
              <tr v-for="fila in filasMostrar" :key="fila.cip">
                <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                <td v-if="store.puedeVerIP" class="td-mono">{{ fila.lote_ip ?? '-' }}</td>
                <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                <td>{{ fila.leyCabeza ?? '-' }}</td>
                <td>{{ fila.leyCola ?? '-' }}</td>
                <td>{{ fila.leyLiquido ?? '-' }}</td>
                <td class="td-mono" style="color:var(--color-gold-light)">
                  {{ fila.recuperacion != null ? fila.recuperacion + '%' : '-' }}
                </td>
                <td>
                  <span class="badge-estado" :class="badgeClass(fila.estadoRec)">
                    {{ fila.estadoRec }}
                  </span>
                </td>
                <td class="td-acciones">
                  <button
                    v-if="fila.estadoRec === 'PENDIENTE'"
                    class="btn-primary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irARegistrarRecuperacion(fila.cip)"
                    title="Registrar recuperación"
                  >Registrar</button>
                  <button
                    v-if="store.puedeVerIP && fila.lote_ip"
                    class="btn-secondary"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    @click="irADetalleLote(fila.lote_ip!)"
                    title="Ver detalle del lote"
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

const tabActual     = ref<'ley' | 'rec'>('ley')
const filtroEstado  = ref('')
const filtroDesde   = ref('')
const filtroHasta   = ref('')
const filtroBusqueda = ref('')

onMounted(() => store.cargarCips())

function recargar() { store.cargarCips() }

// ── Columnas dinámicas ────────────────────────────────────────────────────────
const colSpan = computed(() => {
  const base = tabActual.value === 'ley' ? 7 : 7
  return store.puedeVerIP ? base + 1 : base
})

// ── Filas con datos calculados ────────────────────────────────────────────────
interface FilaLey {
  cip: string
  lote_ip?: string | null
  fecha_envio?: string | null
  // ley
  leyMasNum?: number | null
  leyMenosNum?: number | null
  ozTc?: number | null
  grTm?: number | null
  estadoLey: string
  // rec
  leyCabeza?: number | null
  leyCola?: number | null
  leyLiquido?: number | null
  recuperacion?: number | null
  estadoRec: string
}

function mapCIP(c: CIPAnalisisOut): FilaLey {
  // Tomar el primer análisis vigente de ley/rec
  const ley = c.analisis_ley.find(a => a.vigente)
  const rec = c.analisis_recuperacion.find(a => a.vigente)

  const estadoLey = c.analisis_ley.length === 0 ? 'PENDIENTE'
    : ley ? 'COMPLETADO' : 'PARCIAL'

  const estadoRec = c.analisis_recuperacion.length === 0 ? 'PENDIENTE'
    : rec ? 'COMPLETADO' : 'PARCIAL'

  return {
    cip: c.cip,
    lote_ip: c.lote_ip,
    fecha_envio: c.fecha_envio,
    leyMasNum:  ley?.ley_grueso ?? null,
    leyMenosNum: ley?.ley_fino ?? null,
    ozTc: ley?.ley_final ?? null,
    grTm: ley?.ley_gr_tm ?? null,
    estadoLey,
    leyCabeza: rec?.ley_cabeza ?? null,
    leyCola:   rec?.ley_cola ?? null,
    leyLiquido: rec?.ley_liquido ?? null,
    recuperacion: rec?.recuperacion ?? null,
    estadoRec,
  }
}

const filasMostrar = computed(() => {
  return store.cips
    .map(mapCIP)
    .filter(f => {
      if (filtroEstado.value) {
        const estado = tabActual.value === 'ley' ? f.estadoLey : f.estadoRec
        if (estado !== filtroEstado.value) return false
      }
      if (filtroBusqueda.value) {
        const q = filtroBusqueda.value.toLowerCase()
        if (!f.cip.toLowerCase().includes(q) && !(f.lote_ip ?? '').toLowerCase().includes(q)) return false
      }
      if (filtroDesde.value && f.fecha_envio && f.fecha_envio < filtroDesde.value) return false
      if (filtroHasta.value && f.fecha_envio && f.fecha_envio > filtroHasta.value) return false
      return true
    })
})

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(d?: string | null) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('es-PE', { day:'2-digit', month:'2-digit', year:'numeric' })
}

function badgeClass(estado: string) {
  const m: Record<string, string> = {
    COMPLETADO: 'completo',
    PENDIENTE:  'pendiente',
    PARCIAL:    'parcial',
  }
  return m[estado] ?? ''
}

function irARegistrarLey(cip: string)         { router.push(`/laboratorio/ley/${cip}`) }
function irARegistrarRecuperacion(cip: string) { router.push(`/laboratorio/recuperacion/${cip}`) }
function irADetalleLote(ip: string)            { router.push(`/laboratorio/lote/${ip}`) }
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

.filtros-bar {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
</style>
