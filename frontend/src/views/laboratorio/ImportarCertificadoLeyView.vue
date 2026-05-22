<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Importar Certificado - Análisis de Ley</h1>
        <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">{{ cipActual }}</p>
      </div>
      <div style="display:flex;gap:0.75rem">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <button v-if="fase === 'form'" class="btn-primary" @click="guardar" :disabled="guardando">
          <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
          Finalizar ✓
        </button>
      </div>
    </header>

    <!-- DATOS DEL LOTE -->
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
      </div>
    </section>

    <!-- PASO 1: Ingresar laboratorio ANTES de subir -->
    <section class="card">
      <h2 class="card-titulo">PASO 1 - LABORATORIO</h2>
      <p style="font-size:var(--text-sm);color:var(--color-text-muted);margin-bottom:1rem">
        Ingrese el nombre del laboratorio que emitió el certificado antes de extraer los datos.
        El sistema no detecta el laboratorio automáticamente.
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
        <div class="field">
          <label class="field-label">TIPO DE ANÁLISIS:</label>
          <select class="field-select field-sm field-input" v-model="form.tipo_analisis">
            <option value="externo">Externo</option>
            <option value="minero">Minero (presentado por proveedor)</option>
            <option value="dirimencia">Dirimencia</option>
          </select>
        </div>
      </div>
    </section>

    <!-- PASO 2: Subir certificado -->
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
          Click para subir el certificado (PDF, JPG, PNG)<br/>
          <small>O arrastra y suelta el archivo</small>
        </span>
      </div>
      <input ref="fileInput" type="file" accept="application/pdf,image/jpeg,image/png" style="display:none" @change="onFileChange" />

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

    <!-- PASO 3: Verificar y corregir datos extraídos -->
    <template v-if="fase === 'form'">
      <section class="card">
        <h2 class="card-titulo">PASO 3 - VERIFICAR DATOS EXTRAÍDOS</h2>
        <p style="font-size:var(--text-sm);color:var(--color-text-muted);margin-bottom:1rem">
          Revise y corrija los campos. El OCR puede cometer errores especialmente en imágenes escaneadas.
        </p>

        <div v-if="errCip" class="alerta-warning" style="margin-bottom:1rem"><AlertTriangle :size="16" /> {{ errCip }}</div>

        <div class="form-grid" style="margin-bottom:1.25rem">
          <div class="field">
            <label class="field-label">CIP DEL CERTIFICADO (verificar):</label>
            <input class="field-input" v-model="cipExtraido"
              :class="{ 'field-error': errCip }"
              @input="validarCip" />
          </div>
          <div class="field">
            <label class="field-label">N° INFORME / CERTIFICADO:</label>
            <input class="field-input" v-model="nInforme" placeholder="Ej: MSSC 001-34764-RLV" />
          </div>
          <div class="field">
            <label class="field-label">FECHA ANÁLISIS:</label>
            <input type="date" class="field-input" v-model="form.fecha_analisis" />
          </div>
          <div class="field">
            <label class="field-label">TIPO DE ANÁLISIS:</label>

            <div v-if="form.tipo_analisis === 'dirimencia'" class="info-box warning" style="margin-bottom:0.75rem">
              <AlertTriangle :size="14" /> Modo DIRIMENCIA: este análisis prevalecerá sobre todos los demás.
            </div>

            <select class="field-select field-input" v-model="form.tipo_analisis">
              <option value="externo">Externo</option>
              <option value="minero">Minero</option>
              <option value="dirimencia">Dirimencia</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">MATERIAL:</label>
            <select class="field-select field-input" v-model="form.material">
              <option value="Au">Au</option>
              <option value="Ag">Ag</option>
            </select>
          </div>
        </div>

        <!-- Leyes: ley_fino = malla -140/-150, ley_grueso = malla +140/+150 -->
        <h3 class="subtitulo-seccion">LEYES DE LA MUESTRA (oz/TC)</h3>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">MALLA -140/-150 (ley fino):</label>
            <input type="number" class="field-input" v-model.number="form.ley_fino"
              step="0.0001" placeholder="0.0000" @input="recalcFinal" />
          </div>
          <div class="field">
            <label class="field-label">MALLA +140/+150 (ley grueso):</label>
            <input type="number" class="field-input" v-model.number="form.ley_grueso"
              step="0.0001" placeholder="0.0000" @input="recalcFinal" />
          </div>
          <!-- ley_final se calcula y muestra read-only; backend la recalcula igual -->
          <div class="field">
            <label class="field-label">LEY FINAL oz/TC (fino + grueso):</label>
            <input class="field-input" :value="leyFinalCalc != null ? leyFinalCalc.toFixed(4) : '-'"
              disabled style="color:var(--color-gold);font-family:var(--font-mono)" />
          </div>
          <div class="field">
            <label class="field-label">GR/TM (referencia):</label>
            <input class="field-input" :value="leyGrTm != null ? leyGrTm.toFixed(3) : '-'"
              disabled style="color:var(--color-text-muted)" />
          </div>
        </div>

        <!-- Advertencia si ley_final extraída difiere del cálculo -->
        <div v-if="alertaDivergencia" class="alerta-warning" style="margin-top:0.75rem">
          <AlertTriangle :size="16" /> La ley final extraída del certificado ({{ leyFinalExtraida?.toFixed(4) }}) difiere
          del cálculo fino+grueso ({{ leyFinalCalc?.toFixed(4) }}).
          Verifique los valores.
        </div>

        <p v-if="errForm" class="error-msg" style="margin-top:0.75rem">{{ errForm }}</p>
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
import type { TipoAnalisis } from '@/types/laboratorio'
import { AlertTriangle } from 'lucide-vue-next'
import type { OrigenDatos } from '@/types/laboratorio'
const router    = useRouter()
const route     = useRoute()
const store     = useLaboratorioStore()
const cipActual = route.params.cip as string

const fase         = ref<'upload' | 'form'>('upload')
const guardando    = ref(false)
const extrayendo   = ref(false)
const dragOver     = ref(false)
const archivo      = ref<File | null>(null)
const fileInput    = ref<HTMLInputElement | null>(null)
const loteIp = ref<string>((route.query.ip as string) ?? '')

// Ingresado por operador antes de extraer
const laboratorio  = ref('')

const cipExtraido    = ref('')
const nInforme       = ref('')
const errCip         = ref('')
const errExtraccion  = ref('')
const errForm        = ref('')
const leyFinalExtraida = ref<number | null>(null)

const FACTOR = 34.2857

const tipoDesdeQuery = (route.query.tipo as TipoAnalisis | undefined) ?? 'externo'

const form = ref({
  cip:           cipActual,
  laboratorio:   '',
  tipo_analisis: tipoDesdeQuery,
  material:      'Au',
  ley_fino:      null as number | null,
  ley_grueso:    null as number | null,
  origen_datos:  '' as OrigenDatos,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

// ley_final = ley_fino + ley_grueso (calculado aquí para mostrar, backend lo recalcula)
const leyFinalCalc = computed(() => {
  if (form.value.ley_fino == null || form.value.ley_grueso == null) return null
  return parseFloat((form.value.ley_fino + form.value.ley_grueso).toFixed(4))
})

const leyGrTm = computed(() =>
  leyFinalCalc.value != null ? parseFloat((leyFinalCalc.value * FACTOR).toFixed(3)) : null
)

// Alerta si la ley_final del cert difiere >1% del calc
const alertaDivergencia = computed(() => {
  if (!leyFinalExtraida.value || !leyFinalCalc.value) return false
  const diff = Math.abs(leyFinalExtraida.value - leyFinalCalc.value)
  return diff > leyFinalCalc.value * 0.01
})

function recalcFinal() {
  // Solo actualiza el computed - no hace falta nada
}

function validarCip() {
  errCip.value = cipExtraido.value && cipExtraido.value !== cipActual
    ? `El CIP del certificado (${cipExtraido.value}) no coincide con el esperado (${cipActual}). Verifique.`
    : ''
}

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) { archivo.value = f; fase.value = 'upload'; errExtraccion.value = '' }
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) { archivo.value = f; fase.value = 'upload'; errExtraccion.value = '' }
}

async function extraer() {
  if (!archivo.value || !laboratorio.value) return
  extrayendo.value = true
  errExtraccion.value = ''
  try {
    const datos = await laboratorioApi.extraerCertificadoLey(archivo.value, laboratorio.value)

    // Mapeo correcto: fino = malla -140, grueso = malla +140
    form.value.laboratorio = laboratorio.value  // operador siempre prevalece
    if (datos.fecha_analisis) form.value.fecha_analisis = datos.fecha_analisis
    if (datos.n_informe) nInforme.value = datos.n_informe

    // Leyes - asignar con separación clara
    form.value.ley_fino   = datos.ley_fino   ?? null   // malla -140/-150
    form.value.ley_grueso = datos.ley_grueso ?? null   // malla +140/+150

    // Guardar ley_final extraída para comparar vs cálculo
    leyFinalExtraida.value = datos.ley_final ?? null

    // Si solo viene ley_final (sin fino/grueso), no podemos separar:
    // se deja al operador que ajuste manualmente
    if (!datos.ley_fino && !datos.ley_grueso && datos.ley_final) {
      errExtraccion.value = 'El certificado solo reporta ley final (no mallas separadas). '
        + 'Ingrese manualmente MALLA -140 y MALLA +140.'
    }

    form.value.origen_datos = 'certificado'

    cipExtraido.value = datos.cip ?? ''
    validarCip()
    fase.value = 'form'
  } catch {
    errExtraccion.value = 'No se pudo extraer datos del certificado. Complete los campos manualmente.'
    fase.value = 'form'
  } finally {
    form.value.laboratorio = laboratorio.value // asegurar que se mantenga el laboratorio ingresado por operador aunque falle extracción
    extrayendo.value = false
  }
}

function saltarOcr() {
  form.value.origen_datos  = 'manual'
  form.value.laboratorio   = laboratorio.value   // propagar el lab del paso 1
  archivo.value            = null
  cipExtraido.value        = cipActual
  fase.value               = 'form'
}

async function guardar() {
  errForm.value = ''
  if (!form.value.ley_fino && !form.value.ley_grueso) {
    errForm.value = 'Ingrese al menos una ley (fino o grueso)'
    return
  }
  // ley_fino y ley_grueso pueden ser 0 (volado): permitido
  const payload = {
    ...form.value,
    ley_fino:   form.value.ley_fino   ?? 0,
    ley_grueso: form.value.ley_grueso ?? 0,
  }
  guardando.value = true
  const ok = await store.registrarLey(payload, archivo.value ?? undefined)
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
  background: rgba(255,160,0,0.1);
  border: 1px solid rgba(255,160,0,0.4);
  border-radius: 4px;
  padding: 0.6rem 0.9rem;
  color: #ffa000;
  font-size: var(--text-sm);
}
.subtitulo-seccion {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  margin-bottom: 0.75rem;
  text-transform: uppercase;
}
</style>
