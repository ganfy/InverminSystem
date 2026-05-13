<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">Análisis de Recuperación</h1>
        <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">{{ cipActual }}</p>
      </div>
      <div style="display:flex;gap:0.75rem">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <button class="btn-primary" @click="guardar" :disabled="guardando || !analisisPendiente">
          <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
          Guardar y Generar Certificado
        </button>
      </div>
    </header>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
    </div>

    <div v-else-if="!analisisPendiente" class="estado-tabla" style="color:var(--color-error)">
      No se encontró un análisis de recuperación PENDIENTE para este CIP.<br>
      Verifique que Comercial haya enviado el lote a recuperación.
    </div>

    <template v-else>

      <!-- DATOS DEL ANÁLISIS -->
      <section class="card">
        <h2 class="card-titulo">DATOS DEL ANÁLISIS</h2>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">CIP:</label>
            <input class="field-input" :value="cipActual" disabled style="color:var(--color-gold);font-family:var(--font-mono)" />
          </div>
          <div class="field">
            <label class="field-label">FECHA ANÁLISIS:</label>
            <input type="date" class="field-input" v-model="fechaAnalisis" />
          </div>
        </div>
      </section>

      <!-- LEYES -->
      <section class="card">
        <h2 class="card-titulo">LEYES DE LA MUESTRA</h2>

        <div class="ensayo-col">
          <div class="field">
            <label class="field-label">LEY CABEZA (ley planta - snapshot):</label>
            <div class="ley-cabeza-display">
              <span class="lc-valor">{{ analisisPendiente.ley_cabeza }}</span>
              <span class="lc-label">oz/TC</span>
            </div>
          </div>

          <div class="field">
            <label class="field-label">LEY COLA:</label>
            <input type="number" class="field-input" v-model.number="form.ley_cola" step="0.0001" placeholder="0.0000" @input="calcRec" />
          </div>

          <div class="field">
            <label class="field-label">LEY LÍQUIDO:</label>
            <input type="number" class="field-input" v-model.number="form.ley_liquido" step="0.0001" placeholder="0.0000" />
          </div>

          <div class="recup-row" v-if="recuperacionCalc != null">
            <span class="field-label">% RECUPERACIÓN:</span>
            <span class="recup-valor">{{ recuperacionCalc.toFixed(2) }}%</span>
          </div>

          <p v-if="errCola" class="error-msg" style="font-size:0.8rem">{{ errCola }}</p>
        </div>

        <p v-if="errForm" class="error-msg" style="margin-top:.75rem">{{ errForm }}</p>
      </section>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import type { AnalisisRecuperacionOut, EstadoRecuperacion, TipoMuestra } from '@/types/laboratorio'
import { useSync } from '@/composables/useSync'

const router = useRouter()
const route  = useRoute()
const store  = useLaboratorioStore()
const ui     = useUiStore()
const { online } = useSync()

const cipActual  = route.params.cip as string
// analisis_id puede venir como query param desde el dashboard
const analisisIdParam = route.query.id ? Number(route.query.id) : null

const cargando  = ref(true)
const guardando = ref(false)
const errForm   = ref('')
const errCola   = ref('')
const archivo   = ref<File | null>(null)

const analisisPendiente = ref<AnalisisRecuperacionOut | null>(null)
const fechaAnalisis = ref(new Date().toISOString().split('T')[0])

const form = ref({
  ley_cola:    null as number | null,
  ley_liquido: null as number | null,
})

const recuperacionCalc = computed(() => {
  if (!analisisPendiente.value?.ley_cabeza || !form.value.ley_cola) return null
  const cabeza = Number(analisisPendiente.value.ley_cabeza)
  const cola   = form.value.ley_cola
  if (cola >= cabeza) return null
  return ((cabeza - cola) / cabeza) * 100
})

function calcRec() {
  errCola.value = ''
  if (!analisisPendiente.value?.ley_cabeza || !form.value.ley_cola) return
  if (form.value.ley_cola >= Number(analisisPendiente.value.ley_cabeza)) {
    errCola.value = 'La ley cola debe ser menor a la ley cabeza'
  }
}

function onArchivo(e: Event) {
  archivo.value = (e.target as HTMLInputElement).files?.[0] ?? null
}

onMounted(async () => {
  cargando.value = true
  try {
    // Asegurar que los CIPs están cargados
    if (!store.cips.length) await store.cargarCips()

    // Buscar el pending por CIP (y opcionalmente por id)
    const cipObj = store.cips.find(c => c.cip === cipActual)
    if (cipObj) {
      const pending = analisisIdParam
        ? cipObj.analisis_recuperacion.find(a => a.id === analisisIdParam && a.estado === 'PENDIENTE' && a.vigente)
        : cipObj.analisis_recuperacion.find(a => a.estado === 'PENDIENTE' && a.vigente)
      analisisPendiente.value = pending ?? null
    }

    const yaCompletado = cipObj?.analisis_recuperacion.find(
        a => a.estado === 'COMPLETADO' && a.vigente
    )
    if (yaCompletado) {
        ui.toast('Este CIP ya tiene un análisis de recuperación completado', 'info')
    }
  } catch {
    ui.toast('Error al cargar datos', 'error')
  } finally {
    cargando.value = false
  }
})


async function guardar() {
  errForm.value = ''
  if (!analisisPendiente.value) { errForm.value = 'Sin análisis pendiente'; return }
  if (!form.value.ley_cola)     { errForm.value = 'Ingrese la ley cola'; return }

  const cabeza = Number(analisisPendiente.value.ley_cabeza)
  if (form.value.ley_cola >= cabeza) {
    errForm.value = 'Ley cola debe ser menor a ley cabeza'
    return
  }

  const okConf = await ui.showConfirm({
      title: 'Generar Certificado',
      message: 'Al guardar y generar el certificado, el informe será adjuntado automáticamente y los datos no podrán modificarse. ¿Desea continuar?',
      confirmLabel: 'Generar y Guardar'
  })
  if (!okConf) return

  guardando.value = true
  const result = await store.completarRecuperacion(
    analisisPendiente.value.id,
    {
      ley_cola:       form.value.ley_cola,
      ley_liquido:    form.value.ley_liquido,
      fecha_analisis: fechaAnalisis.value,
    }
  )
  if (result) {
      await store.generarCertificadoRecInterno(result.id)
      router.push('/laboratorio')
  } else if (!online.value) {
      router.push('/laboratorio')
  }
  guardando.value = false
}
</script>

<style scoped>
.ensayo-col {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 480px;
}

.ley-cabeza-display {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(184,151,75,.08);
  border: 1px solid rgba(184,151,75,.25);
  border-radius: 4px;
}

.lc-valor {
  font-family: var(--font-mono);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-gold);
}

.lc-label {
  font-size: .7rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
}

.recup-row {
  display: flex;
  align-items: center;
  gap: .75rem;
  margin-top: .25rem;
}

.recup-valor {
  font-family: var(--font-mono);
  color: var(--color-gold);
  font-size: var(--text-lg);
  font-weight: 600;
}

.info-ley-cabeza {
  background: rgba(59,130,246,.08);
  border: 1px solid rgba(59,130,246,.2);
  border-radius: 4px;
  padding: .6rem .9rem;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: 1rem;
}
</style>
