<template>
  <div class="page-container">
    <header class="page-header">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
        <div>
          <button
            class="btn-back"
            @click="router.push('/pruebas')"
            style="margin-bottom:0.5rem"
          >← Volver a Pruebas</button>
          <h1 class="page-title">Recuperaciones</h1>
          <p class="page-subtitle">Leyes de cola registradas y porcentaje de recuperación</p>
        </div>
        <button class="btn-refresh" @click="cargar" :disabled="cargando" title="Actualizar">
          <RefreshCw :size="20" :class="{ spinning: cargando }" />
        </button>
      </div>
    </header>

    <!-- Filtro búsqueda -->
    <div class="filtros-bar" style="margin-bottom:1rem">
      <div class="field" style="flex:1;max-width:320px">
        <label class="field-label">Buscar</label>
        <input
          type="text" class="field-input"
          v-model="busqueda"
          placeholder="IP, CIP, proveedor..."
        />
      </div>
    </div>

    <!-- Estado carga -->
    <div v-if="cargando && items.length === 0" class="estado-tabla">
      <span class="spinner"></span> Cargando recuperaciones...
    </div>

    <!-- Tabla -->
    <div v-else class="tabla-wrapper">
      <table class="tabla">
        <thead>
          <tr>
            <th>IP</th>
            <th>PROVEEDOR</th>
            <th>FECHA</th>
            <th class="th-group th-au">LEY COLA Au</th>
            <th class="th-group th-ag">LEY COLA Ag</th>
            <th class="th-group th-liq">SOLUCIÓN Au</th>
            <th class="th-group th-liq">SOLUCIÓN Ag</th>
            <th class="th-group th-rec">% RECUP</th>
          </tr>
          <tr class="thead-units">
            <th colspan="3"></th>
            <th><span class="u-primary gold">g/TM</span><span class="u-sep">/</span><span class="u-secondary">oz/TC</span></th>
            <th><span class="u-primary blue">g/TM</span><span class="u-sep">/</span><span class="u-secondary">oz/TC</span></th>
            <th><span class="u-primary">g/m³</span><span class="u-sep">/</span><span class="u-secondary">oz/TC</span></th>
            <th><span class="u-primary blue">g/m³</span><span class="u-sep">/</span><span class="u-secondary">oz/TC</span></th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filtrados.length === 0">
            <td colspan="8" class="estado-tabla sin-datos">
              {{ busqueda ? 'Sin resultados para "' + busqueda + '"' : 'Sin recuperaciones registrados' }}
            </td>
          </tr>
          <tr
            v-for="item in filtrados"
            :key="(item.ip ?? '') + (item.cip ?? '')"
            :class="{ 'row-sin-rec': item.recuperacion == null }"
          >
            <td class="td-mono" style="color:var(--color-gold)">{{ item.ip }}</td>
            <td class="td-proveedor">{{ item.proveedor }}</td>
            <td class="td-fecha">{{ fmt(item.fecha_analisis) }}</td>

            <!-- Ley cola Au -->
            <td class="td-dual">
              <span class="val-primary gold">{{ fmtD(item.ley_cola_au_gr_tm) ?? '—' }}</span>
              <span class="val-secondary">{{ fmtD(item.ley_cola_au_oz_tc) ?? '—' }}</span>
            </td>

            <!-- Ley cola Ag -->
            <td class="td-dual">
              <span class="val-primary blue">{{ fmtD(item.ley_cola_ag_gr_tm) ?? '—' }}</span>
              <span class="val-secondary">{{ item.ley_cola_ag_gr_tm != null ? fmtD(item.ley_cola_ag_gr_tm / 34.2857) : '—' }}</span>
            </td>

            <!-- Solución Au g/m³ -->
            <td class="td-dual">
              <span class="val-primary">{{ fmtD(item.solucion_au_g_m3) ?? '—' }}</span>
              <span class="val-secondary">{{ item.solucion_au_g_m3 != null ? fmtD(item.solucion_au_g_m3 / 34.2857) : '—' }}</span>
            </td>

            <!-- Solución Ag g/m³ -->
            <td class="td-dual">
              <span class="val-primary blue">{{ fmtD(item.solucion_ag_g_m3) ?? '—' }}</span>
              <span class="val-secondary">{{ item.solucion_ag_g_m3 != null ? fmtD(item.solucion_ag_g_m3 / 34.2857) : '—' }}</span>
            </td>

            <!-- % Recuperación -->
            <td>
              <span
                v-if="item.recuperacion != null"
                class="rec-badge"
                :class="recClass(item.recuperacion)"
              >
                {{ Number(item.recuperacion).toFixed(1) }}%
              </span>
              <span v-else class="td-mono" style="color:var(--color-text-faint)">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Leyenda recuperación -->
    <div class="rec-leyenda">
      <span class="leyenda-item rec-alta">≥ 85% Buena</span>
      <span class="leyenda-item rec-media">70-84% Regular</span>
      <span class="leyenda-item rec-baja">&lt; 70% Baja</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { RefreshCw } from 'lucide-vue-next'
import { pruebasApi, type RecuperacionItem } from '@/api/pruebas'

const router  = useRouter()
const items   = ref<RecuperacionItem[]>([])
const cargando = ref(false)
const busqueda = ref('')

async function cargar() {
  cargando.value = true
  try {
    items.value = await pruebasApi.listarRecuperaciones()
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

const filtrados = computed(() => {
  if (!busqueda.value.trim()) return items.value
  const q = busqueda.value.toLowerCase()
  return items.value.filter(i =>
    i.ip?.toLowerCase().includes(q) ||
    i.cip?.toLowerCase().includes(q) ||
    i.proveedor?.toLowerCase().includes(q)
  )
})

function recClass(v: number | null) {
  if (v == null) return ''
  if (v >= 85) return 'rec-alta'
  if (v >= 70) return 'rec-media'
  return 'rec-baja'
}

function fmt(d?: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function fmtD(v?: number | null, dec = 3) {
  if (v == null) return null
  return Number(v).toFixed(dec)
}
</script>

<style scoped>
.btn-back {
  background: none; border: none; color: var(--color-text-muted);
  font-size: 0.78rem; cursor: pointer; padding: 0;
  font-family: var(--font-mono); letter-spacing: 0.04em;
}
.btn-back:hover { color: var(--color-gold); }

/* Refresh button — igual que PruebasView */
.btn-refresh {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-gold);
  padding: 0.5rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.btn-refresh:hover:not(:disabled) {
  background: rgba(212,175,55,0.1);
  border-color: var(--color-gold);
}
.btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Cabeceras */
.th-group { text-align: center; font-size: 0.7rem; letter-spacing: 0.06em; font-weight: 700; }
.th-au  { color: var(--color-gold); }
.th-ag  { color: #60a5fa; }
.th-liq { color: var(--color-text-muted); }

/* Fila de unidades */
.thead-units th {
  padding-top: 0; padding-bottom: 0.35rem;
  border-top: none; background: transparent;
}
.u-primary   { font-size: 0.6rem; font-weight: 600; font-family: var(--font-mono); }
.u-secondary { font-size: 0.6rem; color: var(--color-text-muted); font-family: var(--font-mono); }
.u-sep       { font-size: 0.6rem; color: var(--color-border); margin: 0 0.2rem; }
.gold { color: var(--color-gold); }
.blue { color: #60a5fa; }

/* Celdas con dos valores */
.td-dual {
  text-align: center; vertical-align: middle;
  font-family: var(--font-mono); padding: 0.55rem 0.75rem;
  white-space: nowrap;
}
.val-primary   { display: inline; font-size: 0.80rem; font-weight: 600; line-height: 1; margin-right: 0.3rem; }
.val-secondary { font-size: 0.80rem; color: var(--color-text-muted); line-height: 1; }

.td-proveedor { font-size: 0.8rem; color: var(--color-text-muted); max-width: 160px; }
.td-rec       { text-align: center; }

/* Recovery badge */
.rec-badge {
  display: inline-block; padding: 3px 10px; border-radius: 5px;
  font-family: var(--font-mono); font-size: 0.85rem; font-weight: 700;
}
.rec-alta  { background: rgba(34,197,94,0.15);  color: #4ade80; }
.rec-media { background: rgba(234,179,8,0.15);   color: #fbbf24; }
.rec-baja  { background: rgba(239,68,68,0.15);   color: #f87171; }

.row-sin-rec { opacity: 0.65; }

/* Leyenda */
.rec-leyenda {
  display: flex; gap: 1rem; padding: 0.75rem 0; margin-top: 0.5rem;
}
.leyenda-item {
  font-size: 0.7rem; font-family: var(--font-mono);
  padding: 2px 8px; border-radius: 3px;
}
</style>
