<template>
    <div class="page-container">

      <header class="page-header">
        <div>
          <h1 class="page-title">Registro Análisis Newmont</h1>
          <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">
            {{ nInforme || '...' }}
          </p>
        </div>
        <div style="display:flex;gap:0.75rem">
          <button class="btn-secondary" @click="router.back()">← Volver</button>
          <button class="btn-primary" @click="guardar" :disabled="guardando">
            <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
            Generar certificado →
          </button>
        </div>
      </header>

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
            <label class="field-label">MATERIAL (Au/Ag):</label>
            <select class="field-select" v-model="form.material">
              <option value="Au">Au</option>
              <option value="Ag">Ag</option>
            </select>
          </div>
        </div>
      </section>

      <!-- DATOS DEL ENSAYO -->
      <section class="card">
        <h2 class="card-titulo">DATOS DEL ENSAYO</h2>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">N° INFORME:</label>
            <input class="field-input" v-model="nInforme" placeholder="Ej: LQ IP202601-0105" />
          </div>
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
            <select class="field-select" v-model="metodo">
              <option>Newmont</option>
              <option>Paititi</option>
              <option>Quantum</option>
              <option>Otro</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">PUNTO:</label>
            <select class="field-select" v-model="punto">
              <option>Cabeza</option>
              <option>Cola</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">SOLICITUD:</label>
            <input class="field-input" :value="'Análisis de sólidos por Au'" disabled />
          </div>
          <div class="field">
            <label class="field-label">TIPO DE ANÁLISIS:</label>
            <input class="field-input" :value="'Fire Assay - Gravimétrico'" disabled />
          </div>
          <div class="field">
            <label class="field-label">TIPO ANÁLISIS (sistema):</label>
            <select class="field-select" v-model="form.tipo_analisis">
              <option value="planta">Planta (Paititi)</option>
              <option value="externo">Externo</option>
              <option value="minero">Minero</option>
              <option value="dirimencia">Dirimencia</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">LABORATORIO:</label>
            <input class="field-input" v-model="form.laboratorio" placeholder="Newmont" />
          </div>
        </div>
      </section>

      <!-- LEYES DE LA MUESTRA (triple sampling) -->
      <section class="card">
        <h2 class="card-titulo">LEYES DE LA MUESTRA</h2>
        <div class="muestras-grid">

          <!-- Fila Fino 1 -->
          <div class="muestra-row">
            <span class="muestra-label">P. MUESTRA FINO 1:</span>
            <input type="number" class="field-input muestra-input" v-model.number="pFino1" step="0.001" placeholder="g" />
            <span class="muestra-label">Au (mg) -:</span>
            <input type="number" class="field-input muestra-input" v-model.number="auFino1" step="0.0001" placeholder="0.0000" @input="recalc" />
            <span class="muestra-label">OZ/TC -140:</span>
            <span class="muestra-calc">{{ fmtNum(ozMenos) }}</span>
            <span class="muestra-label">LEY AU (OZ/TC):</span>
            <span class="muestra-calc highlight">{{ fmtNum(leyFinal) }}</span>
          </div>

          <!-- Fila Fino 2 -->
          <div class="muestra-row">
            <span class="muestra-label">P. MUESTRA FINO 2:</span>
            <input type="number" class="field-input muestra-input" v-model.number="pFino2" step="0.001" placeholder="g" />
            <span class="muestra-label">Au (mg) -:</span>
            <input type="number" class="field-input muestra-input" v-model.number="auFino2" step="0.0001" placeholder="0.0000" @input="recalc" />
            <span class="muestra-label">OZ/TC +140:</span>
            <span class="muestra-calc">{{ fmtNum(ozMas) }}</span>
            <span class="muestra-label">LEY Au g/TM:</span>
            <span class="muestra-calc highlight">{{ fmtNum(leyGrTm) }}</span>
          </div>

          <!-- Fila Grueso -->
          <div class="muestra-row">
            <span class="muestra-label">P. MUESTRA GRUESO:</span>
            <input type="number" class="field-input muestra-input" v-model.number="pGrueso" step="0.001" placeholder="g" />
            <span class="muestra-label">Au (mg) +:</span>
            <input type="number" class="field-input muestra-input" v-model.number="auGrueso" step="0.0001" placeholder="0.0000" @input="recalc" />
          </div>

        </div>

        <p v-if="errCalc" class="error-msg" style="margin-top:0.75rem">{{ errCalc }}</p>
      </section>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useLaboratorioStore } from '@/stores/laboratorio'
  import type { TipoAnalisis } from '@/types/laboratorio'

  const router = useRouter()
  const route  = useRoute()
  const store  = useLaboratorioStore()

  const cipActual  = route.params.cip as string
  const guardando  = ref(false)
  const errCalc    = ref('')
  const materialInfo = ref('Mineral')

  // ── Campos del formulario ─────────────────────────────────────────────────────
  const nInforme   = ref('')
  const descripcion = ref('Polveado')
  const metodo     = ref('Newmont')
  const punto      = ref('Cabeza')

  const form = ref({
    cip: cipActual,
    laboratorio:    'Newmont',
    tipo_analisis:  'externo' as TipoAnalisis,
    material:       'Au',
    ley_fino:       0,
    ley_grueso:     0,
    origen_datos:   'manual' as const,
    fecha_analisis: new Date().toISOString().split('T')[0],
  })

  // ── Campos de triple sampling ─────────────────────────────────────────────────
  // Triple sampling: Fino1 → Grueso → Fino2
  // Ley fino promedio = (auFino1 + auFino2) / 2
  // Ley final = ley_fino_prom + ley_grueso (ambos en oz/tc)
  const FACTOR = 34.2857

  const pFino1  = ref<number | null>(null)
  const auFino1 = ref<number | null>(null)
  const pFino2  = ref<number | null>(null)
  const auFino2 = ref<number | null>(null)
  const pGrueso = ref<number | null>(null)
  const auGrueso = ref<number | null>(null)

  // Conversión mg → oz/tc: (mg / (peso_g * 29.1667))  aproximado
  // Usar fórmula: oz/tc = (Au_mg / peso_g) / 29.1667
  function mgToOzTc(mg: number, pesoG: number): number {
    if (!pesoG || pesoG === 0) return 0
    return mg / pesoG / 29.1667
  }

  const ozMenos = computed(() => {
    if (auFino1.value == null || auFino2.value == null) return null
    // Ley fino = promedio de fino1 y fino2
    const avgMg = (auFino1.value + auFino2.value) / 2
    const avgP  = ((pFino1.value ?? 15) + (pFino2.value ?? 15)) / 2
    return parseFloat(mgToOzTc(avgMg, avgP).toFixed(4))
  })

  const ozMas = computed(() => {
    if (auGrueso.value == null) return null
    return parseFloat(mgToOzTc(auGrueso.value, pGrueso.value ?? 10).toFixed(4))
  })

  const leyFinal = computed(() => {
    if (ozMenos.value == null || ozMas.value == null) return null
    return parseFloat((ozMenos.value + ozMas.value).toFixed(4))
  })

  const leyGrTm = computed(() => {
    if (leyFinal.value == null) return null
    return parseFloat((leyFinal.value * FACTOR).toFixed(3))
  })

  function recalc() {
    errCalc.value = ''
    if (leyFinal.value != null) {
      form.value.ley_fino   = ozMenos.value ?? 0
      form.value.ley_grueso = ozMas.value   ?? 0
    }
  }

  function fmtNum(n: number | null | undefined) {
    if (n == null) return '-'
    return n.toFixed(4)
  }

  // ── Cargar info del CIP si está disponible ────────────────────────────────────
  onMounted(async () => {
    const cip = store.cips.find(c => c.cip === cipActual)
    if (cip?.tipo_muestra) materialInfo.value = cip.tipo_muestra
    if (cip?.laboratorio_destino) form.value.laboratorio = cip.laboratorio_destino
  })

  // ── Guardar ───────────────────────────────────────────────────────────────────
  async function guardar() {
    errCalc.value = ''

    if (!form.value.laboratorio) { errCalc.value = 'Ingrese el laboratorio'; return }
    if (leyFinal.value == null || leyFinal.value <= 0) {
      errCalc.value = 'Ingrese los pesos y valores Au para calcular las leyes'
      return
    }

    form.value.ley_fino   = ozMenos.value ?? 0
    form.value.ley_grueso = ozMas.value   ?? 0

    guardando.value = true
    const ok = await store.registrarLey(form.value)
    guardando.value = false

    if (ok) router.push('/laboratorio')
  }
  </script>

  <style scoped>
  .muestras-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .muestra-row {
    display: grid;
    grid-template-columns: 180px 110px 130px 110px 140px 90px 180px 90px;
    align-items: center;
    gap: 0.5rem;
  }

  @media (max-width: 1100px) {
    .muestra-row {
      grid-template-columns: 1fr 1fr;
    }
  }

  .muestra-label {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    letter-spacing: 0.02em;
  }

  .muestra-input {
    max-width: 110px;
  }

  .muestra-calc {
    font-family: var(--font-mono);
    color: var(--color-text-muted);
    font-size: var(--text-md);
  }

  .muestra-calc.highlight {
    color: var(--color-gold);
    font-size: var(--text-lg);
    font-weight: 600;
  }
  </style>
