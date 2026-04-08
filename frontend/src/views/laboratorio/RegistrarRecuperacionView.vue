<template>
    <div class="page-container">

      <header class="page-header">
        <div>
          <h1 class="page-title">Registro Análisis Recuperación</h1>
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
            <select class="field-select" v-model="material">
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
            <input class="field-input" v-model="nInforme" placeholder="Ej: AREC-549" />
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
              <option>Cola</option>
              <option>Cabeza</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">SOLICITUD:</label>
            <input class="field-input" :value="'Análisis de Recuperación'" disabled />
          </div>
          <div class="field">
            <label class="field-label">TIPO DE ANÁLISIS:</label>
            <input class="field-input" :value="'Fire Assay - Gravimétrico'" disabled />
          </div>
          <div class="field">
            <label class="field-label">LABORATORIO:</label>
            <input class="field-input" v-model="form.laboratorio" placeholder="Newmont" />
          </div>
        </div>
      </section>

      <!-- LEYES DE LA MUESTRA -->
      <!-- Muestra principal + hasta 2 reensayos -->
      <section class="card">
        <h2 class="card-titulo" style="display:flex;justify-content:space-between;align-items:center">
          <span>LEYES DE LA MUESTRA</span>
          <button
            v-if="reensayos.length < 2"
            class="btn-secondary"
            style="font-size:0.75rem;padding:0.35rem 0.85rem"
            @click="agregarReensayo"
          >+ Agregar reensayo</button>
        </h2>

        <div class="ensayos-grid">

          <!-- Ensayo principal -->
          <div class="ensayo-col">
            <h3 class="ensayo-titulo">Ensayo principal</h3>
            <div class="field">
              <label class="field-label">LEY CABEZA:</label>
              <input type="number" class="field-input" v-model.number="form.ley_cabeza" step="0.001" @input="calcRec(0)" />
            </div>
            <div class="field">
              <label class="field-label">LEY COLA:</label>
              <input type="number" class="field-input" v-model.number="form.ley_cola" step="0.001" @input="calcRec(0)" />
            </div>
            <div class="field">
              <label class="field-label">LEY LÍQUIDO:</label>
              <input type="number" class="field-input" v-model.number="form.ley_liquido" step="0.001" />
            </div>
            <div class="recup-row" v-if="recuperacionPrincipal != null">
              <span class="field-label">RECUPERACIÓN:</span>
              <span class="recup-valor">{{ recuperacionPrincipal.toFixed(2) }}%</span>
            </div>
          </div>

          <!-- Reensayos dinámicos -->
          <div v-for="(r, i) in reensayos" :key="i" class="ensayo-col">
            <h3 class="ensayo-titulo" style="display:flex;justify-content:space-between">
              <span>Reensayo R{{ i + 1 }}</span>
              <button class="btn-cerrar" @click="reensayos.splice(i, 1)" title="Quitar reensayo">×</button>
            </h3>
            <div class="field">
              <label class="field-label">LEY CABEZA R{{ i + 1 }}:</label>
              <input type="number" class="field-input" v-model.number="r.cabeza" step="0.001" @input="calcRec(i + 1)" />
            </div>
            <div class="field">
              <label class="field-label">LEY COLA R{{ i + 1 }}:</label>
              <input type="number" class="field-input" v-model.number="r.cola" step="0.001" @input="calcRec(i + 1)" />
            </div>
            <div class="field">
              <label class="field-label">LEY LÍQUIDO R{{ i + 1 }}:</label>
              <input type="number" class="field-input" v-model.number="r.liquido" step="0.001" />
            </div>
            <div class="recup-row" v-if="r.recuperacion != null">
              <span class="field-label">RECUPERACIÓN R{{ i + 1 }}:</span>
              <span class="recup-valor">{{ r.recuperacion.toFixed(2) }}%</span>
            </div>
          </div>

        </div>

        <p v-if="errForm" class="error-msg" style="margin-top:0.75rem">{{ errForm }}</p>
      </section>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useLaboratorioStore } from '@/stores/laboratorio'

  const router = useRouter()
  const route  = useRoute()
  const store  = useLaboratorioStore()

  const cipActual    = route.params.cip as string
  const guardando    = ref(false)
  const errForm      = ref('')
  const materialInfo = ref('Mineral')

  const nInforme    = ref('')
  const descripcion = ref('Polveado')
  const metodo      = ref('Newmont')
  const punto       = ref('Cola')
  const material    = ref('Au')

  const form = ref({
    cip:           cipActual,
    laboratorio:   'Newmont',
    ley_cabeza:    null as number | null,
    ley_cola:      null as number | null,
    ley_liquido:   null as number | null,
    fecha_analisis: new Date().toISOString().split('T')[0],
  })

  interface Reensayo {
    cabeza:       number | null
    cola:         number | null
    liquido:      number | null
    recuperacion: number | null
  }

  const reensayos = ref<Reensayo[]>([])

  const recuperacionPrincipal = computed(() => {
    if (!form.value.ley_cabeza || !form.value.ley_cola) return null
    if (form.value.ley_cola >= form.value.ley_cabeza) return null
    return ((form.value.ley_cabeza - form.value.ley_cola) / form.value.ley_cabeza) * 100
  })

  function calcRec(idx: number) {
    if (idx === 0) return // principal se calcula en computed
    const r = reensayos.value[idx - 1]
    if (!r || !r.cabeza || !r.cola || r.cola >= r.cabeza) { if (r) r.recuperacion = null; return }
    r.recuperacion = ((r.cabeza - r.cola) / r.cabeza) * 100
  }

  function agregarReensayo() {
    reensayos.value.push({ cabeza: null, cola: null, liquido: null, recuperacion: null })
  }

  onMounted(() => {
    const cip = store.cips.find(c => c.cip === cipActual)
    if (cip?.tipo_muestra) materialInfo.value = cip.tipo_muestra
    if (cip?.laboratorio_destino) form.value.laboratorio = cip.laboratorio_destino
  })

  async function guardar() {
    errForm.value = ''
    if (!form.value.laboratorio)    { errForm.value = 'Ingrese el laboratorio'; return }
    if (!form.value.ley_cabeza)     { errForm.value = 'Ingrese la ley cabeza'; return }
    if (!form.value.ley_cola)       { errForm.value = 'Ingrese la ley cola'; return }
    if (form.value.ley_cola >= form.value.ley_cabeza) {
      errForm.value = 'La ley cola debe ser menor a la ley cabeza'
      return
    }

    guardando.value = true
    const ok = await store.registrarRecuperacion({
      cip:          form.value.cip,
      laboratorio:  form.value.laboratorio,
      ley_cabeza:   form.value.ley_cabeza!,
      ley_cola:     form.value.ley_cola!,
      ley_liquido:  form.value.ley_liquido,
      origen_datos: 'manual',
      fecha_analisis: form.value.fecha_analisis,
    })
    guardando.value = false
    if (ok) router.push('/laboratorio')
  }
  </script>

  <style scoped>
  .ensayos-grid {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .ensayo-col {
    flex: 1;
    min-width: 260px;
    background: var(--color-surface-alt, rgba(255,255,255,0.03));
    border: 1px solid var(--color-border);
    border-radius: 6px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .ensayo-titulo {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
  }

  .recup-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.25rem;
  }

  .recup-valor {
    font-family: var(--font-mono);
    color: var(--color-gold);
    font-size: var(--text-lg);
    font-weight: 600;
  }
  </style>
