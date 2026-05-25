<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">
          {{ form.material === 'Ag' ? 'Registro Análisis Ag' : 'Registro Análisis Newmont' }}
        </h1>
      </div>
      <div style="display:flex;gap:0.75rem">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <button class="btn-primary" @click="guardar" :disabled="guardando">
          <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
          Guardar y Generar Certificado
        </button>
      </div>
    </header>

    <!-- Banner offline -->
    <div v-if="!online" class="offline-banner">
      <WifiOff :size="16" style="margin-right:0.5rem;vertical-align:middle" />
      Sin conexión — el análisis se guardará localmente y se sincronizará al reconectar.
    </div>

    <!-- DATOS DEL LOTE -->
    <section class="card">
      <h2 class="card-titulo">DATOS DEL LOTE</h2>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">CIP:</label>
          <input class="field-input" :value="cipActual" disabled style="color:var(--color-gold);font-family:var(--font-mono)" />
        </div>
        <div class="field">
          <label class="field-label">MATERIAL:</label>
          <input class="field-input" :value="materialInfo" disabled />
        </div>
        <div class="field">
          <label class="field-label">LABORATORIO:</label>
          <input class="field-input" value="Paititi" disabled />
        </div>
        <div class="field">
          <label class="field-label">MINERAL (Au/Ag):</label>
          <select class="field-select field-input field-sm" v-model="form.material" @change="onMaterialChange">
            <option value="Au">Au — Oro</option>
            <option value="Ag">Ag — Plata</option>
          </select>
        </div>
      </div>
    </section>

    <!-- DATOS DEL ENSAYO -->
    <section class="card">
      <h2 class="card-titulo">DATOS DEL ENSAYO</h2>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">FECHA INGRESO:</label>
          <input type="date" class="field-input" v-model="form.fecha_analisis" />
        </div>
        <div class="field">
          <label class="field-label">DESCRIPCIÓN:</label>
          <input class="field-input" v-model="descripcion" placeholder="Polveado" />
        </div>
        <div class="field">
          <label class="field-label">MÉTODO:</label>
          <input :value="form.material === 'Ag' ? 'Absorción Atómica' : 'Newmont'" readonly class="field-input" disabled />
        </div>
        <div class="field">
          <label class="field-label">PUNTO:</label>
          <select class="field-select field-sm field-input" v-model="punto">
            <option value="CABEZA">Cabeza</option>
            <option value="COLA">Cola</option>
            <option value="LIQUIDO">Líquido</option>
          </select>
        </div>
        <div class="field">
          <label class="field-label">SOLICITUD:</label>
          <input class="field-input" :value="'Análisis de sólidos por ' + form.material" disabled />
        </div>
        <div class="field">
          <label class="field-label">TIPO DE ANÁLISIS:</label>
          <input class="field-input"
            :value="form.material === 'Ag' ? 'Absorción Atómica' : 'Fire Assay - Gravimétrico'"
            disabled />
        </div>
      </div>
    </section>

    <!-- ── AU: Triple Sampling ── -->
    <section class="card" v-if="form.material === 'Au'">
      <h2 class="card-titulo">LEYES DE LA MUESTRA (Triple Sampling)</h2>
      <div class="muestras-cards">

        <!-- Card Fino 1 -->
        <div class="muestra-card">
          <h3 class="muestra-card-titulo">MUESTRA FINO 1</h3>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Peso (g)</label>
              <input type="number" class="field-input" v-model.number="pFino1"
                step="0.001" placeholder="0.000" @input="recalc" />
            </div>
            <div class="field">
              <label class="field-label">Au (mg)</label>
              <input type="number" class="field-input" v-model.number="auFino1"
                step="0.0001" placeholder="0.0000" @input="recalc" />
            </div>
          </div>
        </div>

        <!-- Card Fino 2 -->
        <div class="muestra-card">
          <h3 class="muestra-card-titulo">MUESTRA FINO 2</h3>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Peso (g)</label>
              <input type="number" class="field-input" v-model.number="pFino2"
                step="0.001" placeholder="0.000" @input="recalc" />
            </div>
            <div class="field">
              <label class="field-label">Au (mg)</label>
              <input type="number" class="field-input" v-model.number="auFino2"
                step="0.0001" placeholder="0.0000" @input="recalc" />
            </div>
          </div>
        </div>

        <!-- Card Grueso -->
        <div class="muestra-card">
          <h3 class="muestra-card-titulo">MUESTRA GRUESO</h3>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Peso (g)</label>
              <input type="number" class="field-input" v-model.number="pGrueso"
                step="0.001" placeholder="0.000" @input="recalc" />
            </div>
            <div class="field">
              <label class="field-label">Au (mg)</label>
              <input type="number" class="field-input" v-model.number="auGrueso"
                step="0.0001" placeholder="0.0000" @input="recalc" />
            </div>
          </div>
        </div>

        <!-- Card Resultados Au -->
        <div class="muestra-card muestra-card--resultados">
          <h3 class="muestra-card-titulo">RESULTADOS CALCULADOS</h3>
          <div class="resultados-grid">
            <div class="resultado-item">
              <span class="resultado-label">OZ/TC −140 (fino prom.)</span>
              <span class="resultado-valor">{{ fmtNum(ozMenos) }}</span>
            </div>
            <div class="resultado-item resultado-item--sub">
              <span class="resultado-label resultado-label--unit">≡ GR/TM −140</span>
              <span class="resultado-valor resultado-valor--sub">{{ ozMenos != null ? (ozMenos * FACTOR).toFixed(3) : '-' }}</span>
            </div>
            <div class="resultado-item">
              <span class="resultado-label">OZ/TC +140 (grueso)</span>
              <span class="resultado-valor">{{ fmtNum(ozMas) }}</span>
            </div>
            <div class="resultado-item resultado-item--sub">
              <span class="resultado-label resultado-label--unit">≡ GR/TM +140</span>
              <span class="resultado-valor resultado-valor--sub">{{ ozMas != null ? (ozMas * FACTOR).toFixed(3) : '-' }}</span>
            </div>
            <div class="resultado-item resultado-item--gold">
              <span class="resultado-label">LEY AU (OZ/TC)</span>
              <span class="resultado-valor highlight">{{ fmtNum(leyFinal) }}</span>
            </div>
            <div class="resultado-item">
              <span class="resultado-label">LEY AU (GR/TM)</span>
              <span class="resultado-valor" style="color:var(--color-gold)">
                {{ leyGrTm != null ? leyGrTm.toFixed(3) : '-' }}
              </span>
            </div>
          </div>
        </div>

      </div>
      <p v-if="errCalc" class="error-msg" style="margin-top:0.75rem">{{ errCalc }}</p>
    </section>

    <!-- ── AG: Ley directa ── -->
    <section class="card" v-else>
      <h2 class="card-titulo">LEY DE PLATA</h2>
      <div class="form-grid" style="max-width:520px">
        <div class="field">
          <label class="field-label">LEY Ag (Oz/TC) *</label>
          <input type="number" class="field-input" v-model.number="leyAgOzTc"
            step="0.0001" min="0" placeholder="0.0000"
            style="font-family:var(--font-mono);font-size:1.05em" />
        </div>
        <div class="field">
          <label class="field-label">LEY Ag (Gr/TM)</label>
          <input class="field-input" disabled
            :value="leyAgOzTc != null && leyAgOzTc > 0 ? (leyAgOzTc * FACTOR).toFixed(3) : '-'"
            style="font-family:var(--font-mono);color:var(--color-gold)" />
        </div>
      </div>
      <p style="font-size:0.75rem;color:var(--color-text-faint);margin-top:0.5rem">
        Punto de medición: <strong>{{ punto }}</strong> — se registrará en el detalle del análisis.
      </p>
      <p v-if="errCalc" class="error-msg" style="margin-top:0.5rem">{{ errCalc }}</p>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { WifiOff } from 'lucide-vue-next'
import { useLaboratorioStore } from '@/stores/laboratorio'
import type { TipoAnalisis } from '@/types/laboratorio'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'

const router = useRouter()
const route  = useRoute()
const ui     = useUiStore()
const store  = useLaboratorioStore()
const { online } = useSync()

const cipActual    = route.params.cip as string
const guardando    = ref(false)
const errCalc      = ref('')
const materialInfo = ref('Mineral')

// ── Campos del formulario ─────────────────────────────────────────────────────
const descripcion = ref('Polveado')
const punto       = ref<'CABEZA' | 'COLA' | 'LIQUIDO'>('CABEZA')

const form = ref({
  cip:            cipActual,
  laboratorio:    'Paititi',
  tipo_analisis:  ((route.query.tipo as TipoAnalisis | undefined) ?? 'planta'),
  material:       'Au' as 'Au' | 'Ag',
  ley_fino:       0,
  ley_grueso:     0,
  origen_datos:   'manual' as const,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

// ── Constante Newmont ─────────────────────────────────────────────────────────
const FACTOR         = 34.2857
const FACTOR_NEWMONT = 34.285   // constante del laboratorio

// ── Campos de triple sampling (Au) ───────────────────────────────────────────
const pFino1   = ref<number | null>(null)
const auFino1  = ref<number | null>(null)
const pFino2   = ref<number | null>(null)
const auFino2  = ref<number | null>(null)
const pGrueso  = ref<number | null>(null)
const auGrueso = ref<number | null>(null)

// ── Campo Ag ─────────────────────────────────────────────────────────────────
const leyAgOzTc = ref<number | null>(null)

// ── Fórmulas Newmont ──────────────────────────────────────────────────────────
// ozMenos usa auFino1 para el peso de referencia (estándar Excel planta)
const ozMenos = computed(() => {
  if (auFino1.value == null || auFino2.value == null ||
      pFino1.value == null || pGrueso.value == null) return null
  const avgAu = (auFino1.value + auFino2.value) / 2
  return parseFloat(
    (avgAu * (200 - pGrueso.value) / (pFino1.value * 200) * 1000 / FACTOR_NEWMONT).toFixed(4)
  )
})

const ozMas = computed(() => {
  if (auGrueso.value == null) return null
  return parseFloat((auGrueso.value / (200 * FACTOR_NEWMONT / 1000)).toFixed(4))
})

const leyFinal = computed(() => {
  if (ozMenos.value == null || ozMas.value == null) return null
  return parseFloat((ozMenos.value + ozMas.value).toFixed(4))
})

const leyGrTm = computed(() => {
  if (leyFinal.value == null) return null
  return parseFloat((leyFinal.value * FACTOR).toFixed(3))
})

// Leyes individuales por muestra para analisis_detalle
const leyFino1Individual = computed(() => {
  if (auFino1.value == null || pFino1.value == null || pGrueso.value == null) return null
  return parseFloat(
    (auFino1.value * (200 - pGrueso.value) / (pFino1.value * 200) * 1000 / FACTOR_NEWMONT).toFixed(4)
  )
})

const leyFino2Individual = computed(() => {
  // Usa pFino1 como referencia por consistencia con fórmula original del Excel
  if (auFino2.value == null || pFino1.value == null || pGrueso.value == null) return null
  return parseFloat(
    (auFino2.value * (200 - pGrueso.value) / (pFino1.value * 200) * 1000 / FACTOR_NEWMONT).toFixed(4)
  )
})

function recalc() {
  errCalc.value = ''
  if (leyFinal.value != null) {
    form.value.ley_fino   = ozMenos.value ?? 0
    form.value.ley_grueso = ozMas.value   ?? 0
  }
}

function onMaterialChange() {
  errCalc.value = ''
  // Reset campos del otro material
  if (form.value.material === 'Ag') {
    leyAgOzTc.value = null
    form.value.ley_fino   = 0
    form.value.ley_grueso = 0
  } else {
    pFino1.value  = null; auFino1.value = null
    pFino2.value  = null; auFino2.value = null
    pGrueso.value = null; auGrueso.value = null
  }
}

function fmtNum(n: number | null | undefined) {
  if (n == null) return '-'
  return n.toFixed(4)
}

// ── Cargar info del CIP ───────────────────────────────────────────────────────
onMounted(() => {
  const cip = store.cips.find(c => c.cip === cipActual)
  if (cip?.tipo_muestra) materialInfo.value = cip.tipo_muestra
})

// ── Guardar ───────────────────────────────────────────────────────────────────
async function guardar() {
  errCalc.value = ''

  if (form.value.material === 'Au') {
    if (leyFinal.value == null || leyFinal.value <= 0) {
      errCalc.value = 'Ingrese los pesos y valores Au para calcular las leyes'
      return
    }
  } else {
    // Ag
    if (!leyAgOzTc.value || leyAgOzTc.value <= 0) {
      errCalc.value = 'Ingrese la ley Ag en Oz/TC'
      return
    }
    if (!punto.value) {
      errCalc.value = 'Seleccione el punto de medición (Cabeza / Cola / Líquido)'
      return
    }
  }

  const okConf = await ui.showConfirm({
    title:        online.value ? 'Generar Certificado' : 'Guardar sin conexión',
    message:      online.value
      ? 'Al guardar y generar el certificado, el informe será adjuntado automáticamente y los datos no podrán modificarse. ¿Desea continuar?'
      : 'Sin conexión: el análisis se guardará localmente y se sincronizará al reconectar. El certificado se generará después del sync. ¿Continuar?',
    confirmLabel: online.value ? 'Generar y Guardar' : 'Guardar localmente',
  })
  if (!okConf) return

  // Construir payload final
  if (form.value.material === 'Au') {
    form.value.ley_fino   = ozMenos.value ?? 0
    form.value.ley_grueso = ozMas.value   ?? 0
  } else {
    form.value.ley_fino   = leyAgOzTc.value!
    form.value.ley_grueso = 0
  }

  // muestras_detalle solo para Au (triple sampling)
  const muestrasDetalle = form.value.material === 'Au' && leyFino1Individual.value != null
    ? [
        { peso_g: pFino1.value!,  au_mg: auFino1.value!, ley_oz_tc: leyFino1Individual.value! },
        { peso_g: pGrueso.value!, au_mg: auGrueso.value!, ley_oz_tc: ozMas.value! },
        { peso_g: pFino2.value!,  au_mg: auFino2.value!, ley_oz_tc: leyFino2Individual.value! },
      ]
    : undefined

  const payload = {
    ...form.value,
    ...(form.value.material === 'Ag' ? { punto: punto.value } : {}),
    ...(muestrasDetalle ? { muestras_detalle: muestrasDetalle } : {}),
  }

  guardando.value = true
  const result = await store.registrarLey(payload)
  if (result) {
    await store.generarCertificadoLeyInterno(result.id)
    router.push('/laboratorio')
  } else if (!online.value) {
    router.push('/laboratorio')
  }
  guardando.value = false
}
</script>

<style scoped>
.offline-banner {
  background: rgba(245,158,11,.1);
  border: 1px solid rgba(245,158,11,.35);
  border-radius: var(--radius-md);
  color: #f59e0b;
  font-size: var(--text-sm);
  padding: 0.6rem 1rem;
  margin-bottom: 1.25rem;
  font-family: var(--font-mono);
}

.muestras-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}

.muestra-card {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.9rem 1rem;
  background: rgba(255,255,255,0.02);
}

.muestra-card--resultados {
  border-color: rgba(184,151,75,0.3);
  background: rgba(184,151,75,0.04);
}

.muestra-card-titulo {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  color: var(--color-text-faint);
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}

.resultados-grid {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.resultado-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resultado-item--sub {
  margin-top: -0.15rem;
  margin-bottom: 0.2rem;
  opacity: 0.75;
}

.resultado-label {
  font-size: 0.68rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
}

.resultado-label--unit {
  font-size: 0.62rem;
  padding-left: 0.6rem;
}

.resultado-valor {
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  font-size: var(--text-md);
}

.resultado-valor--sub {
  font-size: 0.72rem;
  color: var(--color-text-faint);
}

.resultado-valor.highlight {
  color: var(--color-gold);
  font-size: var(--text-xl);
  font-weight: 700;
}
</style>
