<template>
    <div class="ag-form">
      <h4 class="ag-form__title">
        <span class="ag-icon">Ag</span> Registrar Ley de Plata
      </h4>

      <div class="ag-form__grid">
        <div class="field">
          <label>Señal Au+Ag (mg)</label>
          <input v-model.number="form.au_ag_mg" type="number" step="0.0001" min="0"
                 placeholder="Ej: 2.3450" @input="calcular" />
        </div>
        <div class="field">
          <label>Señal Au pura (mg)</label>
          <input v-model.number="form.au_mg" type="number" step="0.0001" min="0"
                 placeholder="Ej: 0.1230" @input="calcular" />
        </div>
        <div class="field">
          <label>Peso muestra (g)</label>
          <input v-model.number="form.peso_muestra" type="number" step="0.01" min="0"
                 placeholder="Ej: 29.16" @input="calcular" />
        </div>
        <div class="field">
          <label>Laboratorio</label>
          <input v-model="form.laboratorio" type="text" placeholder="Nombre del laboratorio" />
        </div>
      </div>

      <!-- Preview en tiempo real -->
      <div v-if="preview" class="ag-form__preview">
        <div class="preview-item">
          <span class="preview-label">Neto (mg)</span>
          <span class="preview-val">{{ preview.neto.toFixed(4) }}</span>
        </div>
        <div class="preview-item">
          <span class="preview-label">Ley Ag (g/TM)</span>
          <span class="preview-val highlight">{{ preview.ley_gr_tm.toFixed(3) }}</span>
        </div>
        <div class="preview-item">
          <span class="preview-label">Ley Ag (Oz/TC)</span>
          <span class="preview-val">{{ preview.ley_oz_tc.toFixed(4) }}</span>
        </div>
        <p v-if="preview.ley_gr_tm < umbralAg" class="ag-form__warn">
          ⚠ Ley Ag menor al umbral de inclusión ({{ umbralAg }} g/TM) — no se incluirá en liquidación.
        </p>
      </div>

      <div class="ag-form__actions">
        <button class="btn btn--secondary" @click="$emit('cancel')">Cancelar</button>
        <button class="btn btn--primary" :disabled="!canSubmit || loading" @click="guardar">
          {{ loading ? 'Guardando…' : 'Guardar Ley Ag' }}
        </button>
      </div>
    </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { laboratorioApi, type AnalisisAgOut } from '@/api/laboratorio'
import { useUiStore } from '@/stores/ui'

const props = defineProps<{
analisisAuId: number
laboratorioDefault?: string
}>()
const emit = defineEmits<{
(e: 'saved', ag: AnalisisAgOut): void
(e: 'cancel'): void
}>()

const ui = useUiStore()
const loading = ref(false)
const BLANK = 0.1444
const umbralAg = 4.0  // g/TM — TODO: obtener de config si se expone en frontend

const form = reactive({
au_ag_mg: null as number | null,
au_mg: null as number | null,
peso_muestra: null as number | null,
laboratorio: props.laboratorioDefault ?? '',
})

interface Preview { neto: number; ley_gr_tm: number; ley_oz_tc: number }

const preview = computed<Preview | null>(() => {
if (
    form.au_ag_mg == null ||
    form.au_mg == null ||
    form.peso_muestra == null ||
    form.peso_muestra <= 0
) return null
const neto = Math.max(0, form.au_ag_mg - form.au_mg - BLANK)
const ley_gr_tm = (neto * 1000) / form.peso_muestra
const ley_oz_tc = ley_gr_tm / 34.2857
return { neto, ley_gr_tm, ley_oz_tc }
})

function calcular() { /* reactivity handles it */ }

const canSubmit = computed(
() =>
    preview.value !== null &&
    form.laboratorio.trim() !== '' &&
    !loading.value
)

async function guardar() {
if (!canSubmit.value || !form.au_ag_mg || !form.au_mg || !form.peso_muestra) return
loading.value = true
try {
    const ag = await laboratorioApi.registrarLeyAg(props.analisisAuId, {
    au_ag_mg: form.au_ag_mg,
    au_mg: form.au_mg,
    peso_muestra: form.peso_muestra,
    laboratorio: form.laboratorio,
    })
    ui.toast(`Ley Ag guardada: ${ag.ley_ag_gr_tm.toFixed(3)} g/TM`)
    emit('saved', ag)
} catch (err: any) {
    ui.toast(err?.response?.data?.detail ?? 'Error al guardar')
} finally {
    loading.value = false
}
}
</script>

<style scoped>
.ag-form { display: flex; flex-direction: column; gap: 12px; }
.ag-form__title { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 600; }
.ag-icon {
background: #6366f1; color: #fff;
border-radius: 4px; padding: 1px 6px; font-size: 0.8rem; font-weight: 700;
}
.ag-form__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.field { display: flex; flex-direction: column; gap: 4px; }
.field label { font-size: 0.8rem; font-weight: 500; color: var(--color-text-2); }
.field input {
border: 1px solid var(--color-border);
border-radius: 6px; padding: 6px 10px; font-size: 0.9rem;
background: var(--color-bg-input, #fff);
}
.ag-form__preview {
background: var(--color-bg-2, #f8f9fa);
border: 1px solid var(--color-border);
border-radius: 8px; padding: 10px 14px;
display: flex; gap: 20px; align-items: center; flex-wrap: wrap;
}
.preview-item { display: flex; flex-direction: column; align-items: center; }
.preview-label { font-size: 0.72rem; color: var(--color-text-3); text-transform: uppercase; }
.preview-val { font-size: 1rem; font-weight: 600; }
.preview-val.highlight { color: #6366f1; }
.ag-form__warn { font-size: 0.78rem; color: #d97706; width: 100%; }
.ag-form__actions { display: flex; gap: 8px; justify-content: flex-end; }
</style>
