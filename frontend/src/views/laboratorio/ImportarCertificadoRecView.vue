<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Importar Certificado - Análisis Recuperación</h1>
        <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">{{ cipActual }}</p>
      </div>
      <div style="display:flex;gap:0.75rem">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <button v-if="fase === 'form'" class="btn-primary" @click="guardar" :disabled="guardando || !!errCip">
          <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
          Finalizar ✓
        </button>
      </div>
    </header>

    <section class="card">
      <h2 class="card-titulo">DATOS DEL LOTE</h2>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">IP:</label>
          <input class="field-input" :value="loteIp || '-'" disabled />
        </div>
        <div class="field">
          <label class="field-label">CIP ESPERADO:</label>
          <input class="field-input" :value="cipActual" disabled
            style="color:var(--color-gold);font-family:var(--font-mono)" />
        </div>
        <!-- <div class="field">
          <label class="field-label">PROVEEDOR:</label>
          <input class="field-input" :value="loteInfo?.proveedor ?? '-'" disabled />
        </div> -->
      </div>
    </section>

    <section class="card">
      <h2 class="card-titulo">PASO 1 - LABORATORIO</h2>
      <p style="font-size:var(--text-sm);color:var(--color-text-muted);margin-bottom:1rem">
        Ingrese el nombre del laboratorio que emitió el certificado antes de extraer los datos.
      </p>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">NOMBRE DEL LABORATORIO:</label>
          <input
            class="field-input"
            v-model="laboratorio"
            placeholder="Ej: Minares South S.R.L."
            list="labs-sugeridos"
          />
          <datalist id="labs-sugeridos">
            <option value="Minares South S.R.L." />
            <option value="El Dorado - Invermin Paititi" />
            <option value="Otro" />
          </datalist>
        </div>
      </div>
    </section>

    <section class="card">
      <h2 class="card-titulo">PASO 2 - CARGAR CERTIFICADO</h2>
      <div
        class="upload-zone"
        :class="{ 'upload-zone--over': dragOver, 'upload-zone--done': !!archivo }"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <FileText :size="40" style="color:var(--color-text-faint)" />
        <span v-if="archivo" style="color:var(--color-gold)">{{ archivo.name }}</span>
        <span v-else style="color:var(--color-text-faint)">
          Click para subir el certificado en PDF<br/>
          <small>O arrastra y suelta el archivo</small>
        </span>
      </div>
      <input ref="fileInput" type="file" accept="application/pdf" style="display:none" @change="onFileChange" />
      <div style="display:flex;justify-content:center;margin-top:1rem">
        <button class="btn-primary" @click="extraer" :disabled="!archivo || !laboratorio || extrayendo" style="min-width:160px">
          <span v-if="extrayendo" class="spinner" style="margin-right:0.4rem"></span>
          {{ extrayendo ? 'Extrayendo...' : 'Extraer datos' }}
        </button>
      </div>
      <p v-if="!laboratorio && archivo" class="error-msg" style="margin-top:0.5rem;text-align:center">
        Ingrese el nombre del laboratorio antes de extraer
      </p>
      <p v-if="errExtraccion" class="error-msg" style="margin-top:0.75rem;text-align:center">{{ errExtraccion }}</p>

      <div style="text-align:center;margin-top:1rem;padding-top:0.75rem;border-top:1px solid var(--color-border)">
        <p style="font-size:0.78rem;color:var(--color-text-faint);margin-bottom:0.5rem">
          ¿No tiene el certificado disponible o el OCR falla?
        </p>
        <button
          class="btn-secondary"
          style="font-size:0.82rem"
          @click="saltarOcr"
        >
          Ingresar datos manualmente →
        </button>
      </div>
    </section>

    <template v-if="fase === 'form'">
      <section class="card">
        <h2 class="card-titulo">PASO 3 - VERIFICAR DATA EXTRAÍDA</h2>

        <div v-if="errCip" class="alerta-warning" style="margin-bottom:1rem"><AlertTriangle :size="16" /> {{ errCip }}</div>

        <div class="form-grid" style="margin-bottom:1.25rem">
          <div class="field">
            <label class="field-label">CIP DEL CERTIFICADO:</label>
            <input class="field-input" v-model="cipExtraido"
              :class="{ 'field-error': errCip }" @input="validarCip" />
          </div>
          <div class="field">
            <label class="field-label">N° INFORME:</label>
            <input class="field-input" v-model="nInforme" />
          </div>
          <div class="field">
            <label class="field-label">FECHA ANÁLISIS:</label>
            <input type="date" class="field-input" v-model="form.fecha_analisis" />
          </div>
          <div class="field">
            <label class="field-label">MATERIAL:</label>
            <select class="field-select field-input" v-model="material">
              <option value="Au">Au</option>
              <option value="Ag">Ag</option>
            </select>
          </div>
        </div>

        <h3 style="font-family:var(--font-mono);font-size:0.75rem;letter-spacing:0.06em;color:var(--color-text-muted);margin-bottom:0.75rem">
          LEYES DE LA MUESTRA
        </h3>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">LEY CABEZA:</label>
            <input type="number" class="field-input" v-model.number="form.ley_cabeza" step="0.001" @input="recalc" />
          </div>
          <div class="field">
            <label class="field-label">LEY COLA:</label>
            <input type="number" class="field-input" v-model.number="form.ley_cola" step="0.001" @input="recalc" />
          </div>
          <div class="field">
            <label class="field-label">LEY LÍQUIDO:</label>
            <input type="number" class="field-input" v-model.number="form.ley_liquido" step="0.001" />
          </div>
          <div class="field">
            <label class="field-label">% RECUPERACIÓN:</label>
            <input class="field-input"
              :value="recuperacion != null ? recuperacion.toFixed(2) + '%' : '-'"
              disabled style="color:var(--color-gold)" />
          </div>
        </div>

        <p v-if="errCola" class="error-msg" style="margin-top:0.5rem">{{ errCola }}</p>
        <p v-if="errForm" class="error-msg" style="margin-top:0.5rem">{{ errForm }}</p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { FileText } from 'lucide-vue-next'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { laboratorioApi } from '@/api/laboratorio'
import { AlertTriangle } from 'lucide-vue-next'

const router    = useRouter()
const route     = useRoute()
const store     = useLaboratorioStore()
const cipActual = route.params.cip as string

const fase        = ref<'upload' | 'form'>('upload')
const guardando   = ref(false)
const extrayendo  = ref(false)
const dragOver    = ref(false)
const archivo     = ref<File | null>(null)
const fileInput   = ref<HTMLInputElement | null>(null)
const loteIp = ref<string>((route.query.ip as string) ?? '')

const laboratorio   = ref('')
const cipExtraido   = ref('')
const nInforme      = ref('')
const material      = ref('Au')
const errCip        = ref('')
const errCola       = ref('')
const errExtraccion = ref('')
const errForm       = ref('')

const form = ref({
  cip:           cipActual,
  laboratorio:   '',
  ley_cabeza:    null as number | null,
  ley_cola:      null as number | null,
  ley_liquido:   null as number | null,
  origen_datos:  'certificado' as const,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

const recuperacion = computed(() => {
  if (!form.value.ley_cabeza || !form.value.ley_cola) return null
  return ((form.value.ley_cabeza - form.value.ley_cola) / form.value.ley_cabeza) * 100
})

function recalc() {
  errCola.value = ''
}

function validarCip() {
  errCip.value = cipExtraido.value && cipExtraido.value !== cipActual
    ? `CIP del certificado (${cipExtraido.value}) no coincide con el lote (${cipActual}). Verifique antes de continuar.`
    : ''
}

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) { archivo.value = f; fase.value = 'upload'; errExtraccion.value = '' }
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f?.type === 'application/pdf') { archivo.value = f; fase.value = 'upload'; errExtraccion.value = '' }
}

async function extraer() {
  if (!archivo.value || !laboratorio.value) return
  extrayendo.value = true
  errExtraccion.value = ''
  try {
    const datos = await laboratorioApi.extraerCertificadoRecuperacion(archivo.value)
    form.value.laboratorio = laboratorio.value
    if (datos.fecha_analisis) form.value.fecha_analisis = datos.fecha_analisis
    if (datos.n_informe) nInforme.value = datos.n_informe
    if (datos.ley_cabeza != null) form.value.ley_cabeza = datos.ley_cabeza
    if (datos.ley_cola != null) form.value.ley_cola = datos.ley_cola
    if (datos.ley_liquido != null) form.value.ley_liquido = datos.ley_liquido
    cipExtraido.value = datos.cip ?? ''
    validarCip()
    fase.value = 'form'
  } catch {
    errExtraccion.value = 'No se pudo extraer datos del certificado. Complete los campos manualmente.'
    fase.value = 'form'
  } finally {
    form.value.laboratorio = laboratorio.value
    extrayendo.value = false
  }
}

function saltarOcr() {
  form.value.origen_datos  = 'manual'
  form.value.laboratorio   = laboratorio.value
  archivo.value            = null
  cipExtraido.value        = cipActual
  fase.value               = 'form'
}

async function guardar() {
  errForm.value = ''
  if (!form.value.laboratorio) { errForm.value = 'Ingrese el laboratorio'; return }
  if (!form.value.ley_cabeza || !form.value.ley_cola) { errForm.value = 'Ingrese ley cabeza y cola'; return }
  if (errCola.value) return
  guardando.value = true
  const ok = await store.registrarRecuperacion(
    { ...form.value, ley_cabeza: form.value.ley_cabeza!, ley_cola: form.value.ley_cola! },
    archivo.value ?? undefined,
  )
  guardando.value = false
  if (ok) router.push('/laboratorio')
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: 6px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s;
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}
.upload-zone:hover, .upload-zone--over { border-color: var(--color-gold); }
.upload-zone--done { border-color: var(--color-gold); border-style: solid; }
.field-error { border-color: var(--color-error) !important; }
.alerta-warning {
  background: rgba(255, 160, 0, 0.1);
  border: 1px solid rgba(255, 160, 0, 0.4);
  border-radius: 4px;
  padding: 0.6rem 0.9rem;
  color: #ffa000;
  font-size: var(--text-sm);
}
</style>
