<template>
  <!-- No renderiza nada si no hay alertas para este módulo -->
  <div v-if="alertasModulo.length" class="alertas-banner" :class="`alertas-banner--${maxSeveridad.toLowerCase()}`">
    <div class="ab-header" @click="expandido = !expandido">
      <div class="ab-header-left">
        <AlertTriangle :size="14" class="ab-icon" />
        <span class="ab-titulo">{{ alertasModulo.length }} ALERTA{{ alertasModulo.length !== 1 ? 'S' : '' }}</span>
        <span class="ab-sev-badge" :class="`sev-${maxSeveridad.toLowerCase()}`">{{ maxSeveridad }}</span>
      </div>
      <ChevronDown :size="13" class="ab-chevron" :class="{ 'ab-chevron--up': expandido }" />
    </div>

    <div v-if="expandido" class="ab-lista">
      <div
        v-for="alerta in alertasModulo"
        :key="`${alerta.tipo}-${alerta.ip}`"
        class="ab-item"
        :class="`ab-item--${alerta.severidad.toLowerCase()}`"
      >
        <div class="ab-item-meta">
          <template v-if="modulo !== 'LABORATORIO'">
            <span class="ab-item-ip">{{ alerta.ip }}</span>
          </template>
          <template v-else>
            <span class="ab-item-ip" v-if="alerta.cips && alerta.cips.length">CIP: {{ alerta.cips.join(', ') }}</span>
            <span class="ab-item-ip" style="opacity: 0.6" v-else>CIP: ---</span>
          </template>
          <span class="ab-item-tipo">{{ getTipoLabel(alerta, modulo) }}</span>
          <span class="ab-item-horas">{{ alerta.horas_retraso }}h de retraso</span>
        </div>
        <div class="ab-item-proveedor" v-if="modulo !== 'LABORATORIO'">{{ alerta.proveedor }}<span v-if="alerta.acopiador"> · {{ alerta.acopiador }}</span></div>

        <!-- Campo de observación -->
        <div v-if="conObservaciones" class="ab-obs-wrap">
          <textarea
            v-model="observaciones[`${alerta.tipo}-${alerta.ip}`]"
            class="ab-obs-input"
            :placeholder="`Justificación del retraso (opcional)…`"
            rows="2"
            @blur="guardarObservacion(alerta)"
          />
          <span v-if="guardados[`${alerta.tipo}-${alerta.ip}`]" class="ab-obs-ok">✓ Guardado</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { AlertTriangle, ChevronDown } from 'lucide-vue-next'
import { useUiStore } from '@/stores/ui'
import { dashboardApi } from '@/api/dashboard'

// ── Props ──────────────────────────────────────────────────────────────────────
const props = defineProps<{
  /** Módulo al que pertenecen las alertas: 'MUESTREO' | 'LABORATORIO' | 'PRUEBAS' | 'BALANZA' */
  modulo: string
  /** Si true, muestra campo de observación/justificación por alerta */
  conObservaciones?: boolean
}>()

const TIPO_POR_MODULO: Record<string, string[]> = {
  BALANZA:     ['VOLADO_STOCK'],
  MUESTREO:    ['RETRASO_MUESTREO'],
  LABORATORIO: ['RETRASO_LEY', 'RETRASO_RECUPERACION'],
  PRUEBAS:     ['RETRASO_LEY', 'RETRASO_RECUPERACION'],
}

const TIPO_LABEL: Record<string, string> = {
  VOLADO_STOCK:          'Lote volado en stock',
  RETRASO_MUESTREO:      'Retraso en muestreo',
  RETRASO_LEY:           'Retraso en análisis de ley',
  RETRASO_RECUPERACION:  'Retraso en recuperación',
}

const SEV_ORDER: Record<string, number> = { CRITICA: 3, ALTA: 2, MEDIA: 1 }

function getTipoLabel(alerta: any, modulo: string) {
  if (modulo === 'LABORATORIO') {
    if (alerta.tipo === 'RETRASO_LEY') return 'Retraso en Newmont'
    if (alerta.tipo === 'RETRASO_RECUPERACION') return 'Retraso en Sólidos / Absorciones Atómicas'
  }
  return TIPO_LABEL[alerta.tipo] ?? alerta.tipo
}

// ── Estado ────────────────────────────────────────────────────────────────────
const todasAlertas   = ref<any[]>([])
const expandido      = ref(false)
const observaciones  = ref<Record<string, string>>({})
const guardados      = ref<Record<string, boolean>>({})

const ui = useUiStore()

// ── Computed ──────────────────────────────────────────────────────────────────
const tiposPermitidos = computed(() => TIPO_POR_MODULO[props.modulo] ?? [])

const alertasModulo = computed(() =>
  todasAlertas.value.filter(a => tiposPermitidos.value.includes(a.tipo))
)

const maxSeveridad = computed(() => {
  if (!alertasModulo.value.length) return 'MEDIA'
  return alertasModulo.value.reduce((max, a) =>
    (SEV_ORDER[a.severidad] ?? 0) > (SEV_ORDER[max] ?? 0) ? a.severidad : max
  , 'MEDIA')
})

// ── Fetch ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const res = await dashboardApi.getAlertas()
    todasAlertas.value = res.alertas ?? []
  } catch {
    // silencioso: el banner simplemente no aparece si falla
  }
})

// ── Observaciones ─────────────────────────────────────────────────────────────
async function guardarObservacion(alerta: any) {
  const key = `${alerta.tipo}-${alerta.ip}`
  const texto = observaciones.value[key]?.trim()
  if (!texto) return

  try {
    await dashboardApi.guardarObservacion(alerta.tipo, alerta.ip, texto)
    guardados.value[key] = true
    setTimeout(() => { guardados.value[key] = false }, 3000)
  } catch {
    ui.toast('No se pudo guardar la observación', 'error')
  }
}
</script>

<style scoped>
@import '@/assets/base.css';

.alertas-banner {
  border-radius: var(--radius-sm);
  margin-bottom: 1rem;
  overflow: hidden;
  border-left: 3px solid var(--color-warning);
  background: rgba(234,179,8,0.05);
  border: 1px solid rgba(234,179,8,0.2);
  border-left-width: 3px;
}
.alertas-banner--critica {
  border-color: var(--color-error);
  background: rgba(239,68,68,0.05);
}
.alertas-banner--alta {
  border-color: #f97316;
  background: rgba(249,115,22,0.05);
}
.alertas-banner--media {
  border-color: var(--color-warning);
  background: rgba(234,179,8,0.05);
}

.ab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.85rem;
  cursor: pointer;
  user-select: none;
}
.ab-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.ab-icon { opacity: 0.8; }
.ab-titulo {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  letter-spacing: 0.14em;
  font-weight: 700;
  color: var(--color-text);
}
.ab-sev-badge {
  font-family: var(--font-mono);
  font-size: 9px;
  padding: 1px 6px;
  border-radius: 8px;
  letter-spacing: 0.08em;
}
.sev-critica { background: rgba(239,68,68,0.2);  color: var(--color-error);   }
.sev-alta    { background: rgba(249,115,22,0.2); color: #f97316;              }
.sev-media   { background: rgba(234,179,8,0.2);  color: var(--color-warning); }

.ab-chevron     { color: var(--color-text-muted); transition: transform 0.15s; }
.ab-chevron--up { transform: rotate(180deg); }

.ab-lista { border-top: 1px solid rgba(255,255,255,0.06); }

.ab-item {
  padding: 0.6rem 0.85rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.ab-item:last-child { border-bottom: none; }

.ab-item-meta {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}
.ab-item-ip {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-gold);
  font-weight: 700;
}
.ab-item-tipo {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text);
}
.ab-item-horas {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-error);
  margin-left: auto;
}
.ab-item-proveedor {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* Observación */
.ab-obs-wrap {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  margin-top: 0.25rem;
}
.ab-obs-input {
  flex: 1;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  padding: 0.35rem 0.5rem;
  resize: vertical;
  outline: none;
  transition: border-color 0.15s;
}
.ab-obs-input:focus { border-color: var(--color-gold); }
.ab-obs-ok {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-success);
  align-self: center;
  white-space: nowrap;
}
</style>
