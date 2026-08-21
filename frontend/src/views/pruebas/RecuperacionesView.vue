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
    <!-- Grid de recuperaciones (Reemplaza tabla) -->
    <div v-else class="rec-grid">
      <div v-if="filtrados.length === 0" class="estado-tabla sin-datos" style="grid-column: 1 / -1">
        {{ busqueda ? 'Sin resultados para "' + busqueda + '"' : 'Sin recuperaciones registrados' }}
      </div>
      
      <div
        v-for="item in filtrados"
        :key="(item.ip ?? '') + (item.cip ?? '')"
        class="rec-card"
        :class="{ 'card-sin-rec': item.recuperacion == null }"
      >
        <!-- Card Header -->
        <div class="rc-header">
          <div class="rc-ip-prov">
            <span class="rc-ip">{{ item.ip }}</span>
            <span class="rc-prov">{{ item.proveedor }}</span>
          </div>
          <div class="rc-badges">
            <span class="rc-fecha">{{ fmt(item.fecha_analisis) }}</span>
            <span
              v-if="item.recuperacion != null"
              class="rec-badge"
              :class="recClass(item.recuperacion)"
            >
              {{ Number(item.recuperacion).toFixed(1) }}%
            </span>
            <span v-else class="rc-no-rec">—</span>
          </div>
        </div>

        <!-- Card Body -->
        <div class="rc-body">
          <div class="rc-col">
            <!-- Au -->
            <div class="rc-item">
              <span class="rc-lbl">LEY COLA Au</span>
              <span class="rc-val gold">{{ fmtD(item.ley_cola_au_gr_tm) ?? '—' }} <small>g/TM</small></span>
              <span class="rc-subval">{{ fmtD(item.ley_cola_au_oz_tc) ?? '—' }} <small>oz/TC</small></span>
            </div>
            <div class="rc-item">
              <span class="rc-lbl">SOLUCIÓN Au</span>
              <span class="rc-val">{{ fmtD(item.solucion_au_g_m3) ?? '—' }} <small>g/m³</small></span>
              <span class="rc-subval">{{ item.solucion_au_g_m3 != null ? fmtD(item.solucion_au_g_m3 / 34.2857) : '—' }} <small>oz/TC</small></span>
            </div>
          </div>
          <div class="rc-col">
            <!-- Ag -->
            <div class="rc-item">
              <span class="rc-lbl">LEY COLA Ag</span>
              <span class="rc-val blue">{{ fmtD(item.ley_cola_ag_gr_tm) ?? '—' }} <small>g/TM</small></span>
              <span class="rc-subval">{{ item.ley_cola_ag_gr_tm != null ? fmtD(item.ley_cola_ag_gr_tm / 34.2857) : '—' }} <small>oz/TC</small></span>
            </div>
            <div class="rc-item">
              <span class="rc-lbl">SOLUCIÓN Ag</span>
              <span class="rc-val blue">{{ fmtD(item.solucion_ag_g_m3) ?? '—' }} <small>g/m³</small></span>
              <span class="rc-subval">{{ item.solucion_ag_g_m3 != null ? fmtD(item.solucion_ag_g_m3 / 34.2857) : '—' }} <small>oz/TC</small></span>
            </div>
          </div>
        </div>

        <!-- Card Footer (Acciones) -->
        <div class="rc-footer" v-if="item.recuperacion != null && Number(item.recuperacion) < 70">
          <button
            class="btn-remuestreo"
            :disabled="remuestreando === item.ip"
            @click="mandarARemuestreo(item.ip)"
            title="Recuperación baja — crear nueva prueba metalúrgica"
          >
            <span v-if="remuestreando === item.ip" class="spinner" style="margin-right:0.3rem"></span>
            Enviar Reensayo
          </button>
        </div>
      </div>
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
import { useUiStore } from '@/stores/ui'

const router  = useRouter()
const ui      = useUiStore()
const items   = ref<RecuperacionItem[]>([])
const cargando = ref(false)
const busqueda = ref('')
const remuestreando = ref<string | null>(null)

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

async function mandarARemuestreo(ip: string) {
  const ok = await ui.showConfirm({
    title: 'Enviar Reensayo',
    message: `Recuperación baja detectada para ${ip}. Se creará una nueva prueba metalúrgica. ¿Confirmar?`,
    confirmLabel: 'Confirmar Reensayo',
  })
  if (!ok) return
  remuestreando.value = ip
  try {
    await pruebasApi.solicitarRemuestreo(ip)
    ui.toast(`Reensayo solicitado para ${ip}. Nueva prueba creada en Pruebas Metalúrgicas.`, 'success')
    await cargar()
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al solicitar reensayo', 'error')
  } finally {
    remuestreando.value = null
  }
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
.rec-baja { background: rgba(220, 38, 38, 0.1); color: var(--color-error); }

/* Rec Cards Grid (Compact) */
.rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}
.rec-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.rec-card:hover {
  border-color: var(--color-gold);
  box-shadow: 0 2px 8px rgba(179,144,40,0.1);
}
.card-sin-rec {
  opacity: 0.85;
}
.rc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px dashed var(--color-border);
  padding-bottom: 0.5rem;
}
.rc-ip-prov {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.rc-ip {
  font-family: var(--font-mono);
  color: var(--color-gold);
  font-weight: 700;
  font-size: var(--text-base);
}
.rc-prov {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
}
.rc-badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}
.rc-fecha {
  font-size: var(--text-xs);
  color: var(--color-text-dim);
}
.rc-no-rec {
  color: var(--color-text-faint);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}
.rc-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.rc-col {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.rc-item {
  display: flex;
  flex-direction: column;
}
.rc-lbl {
  font-size: var(--text-xs);
  color: var(--color-text-dim);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.15rem;
}
.rc-val {
  font-size: var(--text-sm);
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--color-text);
}
.rc-subval {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  color: var(--color-text-muted);
}
.rc-val small, .rc-subval small {
  font-size: var(--text-xs);
  color: var(--color-text-faint);
  font-weight: normal;
  opacity: 0.8;
}
.gold { color: var(--color-gold); }
.blue { color: #38bdf8; }
.rc-footer {
  margin-top: 0.25rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255,255,255,0.03);
}

/* Leyenda */
.rec-leyenda {
  display: flex; gap: 1rem; padding: 0.75rem 0; margin-top: 0.5rem;
}
.leyenda-item {
  font-size: 0.7rem; font-family: var(--font-mono);
  padding: 2px 8px; border-radius: 3px;
}

/* Botón remuestreo */
.btn-remuestreo {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,.3);
  color: #f87171;
  padding: 0.3rem 0.7rem;
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  font-family: var(--font-main);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-remuestreo:hover:not(:disabled) {
  background: rgba(239,68,68,0.2);
  border-color: rgba(239,68,68,.5);
}
.btn-remuestreo:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
