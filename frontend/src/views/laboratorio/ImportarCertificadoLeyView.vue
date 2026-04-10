<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Importar Certificado — Análisis Newmont</h1>
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

    <!-- DATOS DEL LOTE -->
    <section class="card">
      <h2 class="card-titulo">DATOS DEL LOTE</h2>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">IP:</label>
          <input class="field-input" :value="loteInfo?.lote_ip ?? '-'" disabled />
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
        <div class="field">
          <label class="field-label">PRODUCTO:</label>
          <input class="field-input" :value="loteInfo?.tipo_muestra ?? 'Mineral'" disabled />
        </div>
      </div>
    </section>

    <!-- FASE 1: UPLOAD -->
    <section class="card">
      <h2 class="card-titulo">CARGAR ARCHIVO DEL CERTIFICADO</h2>
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
        <button class="btn-primary" @click="extraer" :disabled="!archivo || extrayendo" style="min-width:160px">
          <span v-if="extrayendo" class="spinner" style="margin-right:0.4rem"></span>
          {{ extrayendo ? 'Extrayendo...' : 'Extraer datos' }}
        </button>
      </div>
      <p v-if="errExtraccion" class="error-msg" style="margin-top:0.75rem;text-align:center">{{ errExtraccion }}</p>
    </section>

    <!-- FASE 2: VERIFICAR DATA EXTRAÍDA -->
    <template v-if="fase === 'form'">
      <section class="card">
        <h2 class="card-titulo">VERIFICAR DATA EXTRAÍDA</h2>

        <!-- Alerta si el CIP del certificado no coincide -->
        <div v-if="errCip" class="alerta-warning" style="margin-bottom:1rem">
          ⚠️ {{ errCip }}
        </div>

        <div class="form-grid" style="margin-bottom:1.25rem">
          <div class="field">
            <label class="field-label">CIP DEL CERTIFICADO:</label>
            <input class="field-input" v-model="cipExtraido"
              :class="{ 'field-error': errCip }"
              @input="validarCip" />
          </div>
          <div class="field">
            <label class="field-label">LABORATORIO:</label>
            <input class="field-input" v-model="form.laboratorio" />
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
            <label class="field-label">TIPO DE ANÁLISIS:</label>
            <select class="field-select" v-model="form.tipo_analisis">
              <option value="externo">Externo</option>
              <option value="minero">Minero</option>
              <option value="planta">Planta</option>
              <option value="dirimencia">Dirimencia</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">MATERIAL:</label>
            <select class="field-select" v-model="form.material">
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
            <label class="field-label">LEY AU OZ/TC (ley final +/-):</label>
            <input type="number" class="field-input" v-model.number="form.ley_fino"
              step="0.0001" style="color:var(--color-gold)" />
          </div>
          <div class="field">
            <label class="field-label">MESH +150 (ley grueso):</label>
            <input type="number" class="field-input" v-model.number="form.ley_grueso" step="0.0001" />
          </div>
          <div class="field">
            <label class="field-label">MESH -150:</label>
            <input type="number" class="field-input" v-model.number="leyMenos" step="0.0001" />
          </div>
          <div class="field">
            <label class="field-label">G/TM:</label>
            <input class="field-input" :value="grTm != null ? grTm.toFixed(3) : '-'" disabled
              style="color:var(--color-text-muted)" />
          </div>
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
import type { TipoAnalisis, CIPAnalisisOut } from '@/types/laboratorio'

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
const loteInfo    = ref<CIPAnalisisOut | null>(null)

const cipExtraido   = ref('')
const nInforme      = ref('')
const leyMenos      = ref<number | null>(null)
const errCip        = ref('')
const errExtraccion = ref('')
const errForm       = ref('')

const FACTOR = 34.2857

const form = ref({
  cip:           cipActual,
  laboratorio:   '',
  tipo_analisis: 'externo' as TipoAnalisis,
  material:      'Au',
  ley_fino:      0 as number,
  ley_grueso:    0 as number,
  origen_datos:  'certificado' as const,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

const grTm = computed(() =>
  form.value.ley_fino ? parseFloat((form.value.ley_fino * FACTOR).toFixed(3)) : null
)

function validarCip() {
  errCip.value = cipExtraido.value && cipExtraido.value !== cipActual
    ? `El CIP del certificado (${cipExtraido.value}) no coincide con el lote (${cipActual}). Verifique antes de continuar.`
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
  if (!archivo.value) return
  extrayendo.value = true
  errExtraccion.value = ''
  try {
    const datos = await laboratorioApi.extraerCertificadoLey(archivo.value)
    // Pre-fill form
    if (datos.laboratorio) form.value.laboratorio = datos.laboratorio
    if (datos.fecha_analisis) form.value.fecha_analisis = datos.fecha_analisis
    if (datos.n_informe) nInforme.value = datos.n_informe
    if (datos.ley_final != null) form.value.ley_fino = datos.ley_final
    if (datos.ley_grueso != null) form.value.ley_grueso = datos.ley_grueso
    if (datos.ley_fino != null) leyMenos.value = datos.ley_fino
    cipExtraido.value = datos.cip ?? ''
    validarCip()
    fase.value = 'form'
  } catch {
    errExtraccion.value = 'No se pudo extraer datos del certificado. Complete los campos manualmente.'
    fase.value = 'form'
  } finally {
    extrayendo.value = false
  }
}

onMounted(() => {
  loteInfo.value = store.cips.find(c => c.cip === cipActual) ?? null
})

async function guardar() {
  errForm.value = ''
  if (!form.value.laboratorio) { errForm.value = 'Ingrese el laboratorio'; return }
  if (!form.value.ley_fino || form.value.ley_fino <= 0) { errForm.value = 'Ingrese la ley AU OZ/TC'; return }
  guardando.value = true
  const ok = await store.registrarLey(form.value, archivo.value ?? undefined)
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
