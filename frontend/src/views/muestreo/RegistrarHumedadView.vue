<template>
    <div class="humedad-page">
      <header class="page-header" @click="volver">
        <button class="btn-back">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          Registrar humedad
        </button>
      </header>

      <div class="lote-header-card">
        <div class="prominent-field">
          <label class="prominent-label">CÓDIGO DE LOTE</label>
          <div class="prominent-value-box">
            <span class="prominent-value mono gold">{{ ipLote }}</span>
          </div>
        </div>
      </div>

      <div class="form-card">
        <div class="input-group">
          <label>PESO HÚMEDO (g)</label>
          <div class="input-wrapper">
            <input
              v-model="pesoHumedo"
              type="number"
              inputmode="decimal"
              placeholder="0"
            />
            <span class="unit">g</span>
          </div>
        </div>

        <div class="input-group">
          <label>PESO SECO (g)</label>
          <div class="input-wrapper">
            <input
              v-model="pesoSeco"
              type="number"
              inputmode="decimal"
              placeholder="0"
            />
            <span class="unit">g</span>
          </div>
        </div>

        <div class="input-group">
          <label>OBSERVACIONES (Opcional)</label>
          <div class="input-wrapper">
            <textarea
              v-model="observaciones"
              placeholder="Escriba alguna nota sobre la muestra..."
              rows="2"
              class="textarea-observaciones"
            ></textarea>
          </div>
        </div>

        <div class="result-box">
          <label>% HUMEDAD</label>
          <div class="result-value">
            {{ porcentajeHumedad > 0 ? porcentajeHumedad.toFixed(2) : '0.00' }}%
          </div>
          <div class="intentos-badge">{{ intentoActual }}/{{ maxIntentos }} intentos</div>
        </div>
      </div>

      <div class="actions-footer">
        <button class="btn-primary ready btn-tablet-xl" :disabled="!puedeGuardar || store.guardando" @click="() => guardar(false)">
          {{ store.guardando ? 'Guardando...' : 'Guardar y Salir' }}
        </button>

        <button v-if="intentoActual < maxIntentos" class="btn-secondary btn-tablet-xl" :disabled="!puedeGuardar || store.guardando" @click="() => guardar(true)">
          Guardar y Remuestrear
        </button>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMuestreoStore } from '@/stores/muestreo'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const router = useRouter()
const store = useMuestreoStore()
const ui = useUiStore()

const ipLote = route.params.ip as string

const pesoHumedo = ref<number | null>(200)
const pesoSeco = ref<number | null>(null)
const observaciones = ref<string>('')
const intentoActual = ref(1)
const maxIntentos = 3

const porcentajeHumedad = computed(() => {
  if (!pesoHumedo.value || !pesoSeco.value) return 0
  return store.calcularHumedad(pesoHumedo.value, pesoSeco.value)
})

const puedeGuardar = computed(() => {
  return (
    pesoHumedo.value !== null &&
    pesoSeco.value !== null &&
    pesoSeco.value < pesoHumedo.value
  )
})

onMounted(async () => {
  await store.cargarLotes()
  intentoActual.value = await store.calcularProximoIntento(ipLote)

  if (intentoActual.value > maxIntentos) {
    ui.toast('Este lote ya completó sus 3 intentos de muestreo.', 'warning')
    router.push({ name: 'Muestreo' })
  }
})

const guardar = async (esRemuestreo = false) => {
  if (!puedeGuardar.value) return

  const exito = await store.registrarHumedad(ipLote, {
    intento: intentoActual.value,
    peso_humedo: pesoHumedo.value!,
    peso_seco: pesoSeco.value!,
    observaciones: observaciones.value.trim() || null,
  })

  if (exito) {
    if (esRemuestreo && intentoActual.value < maxIntentos) {
      // Flujo: REMUESTREAR
      pesoHumedo.value = 200
      pesoSeco.value = null
      observaciones.value = ''
      intentoActual.value = await store.calcularProximoIntento(ipLote)
      ui.toast(`Intento guardado. Proceda con el intento ${intentoActual.value}/${maxIntentos}`, 'success')
    } else {
      // Flujo: GUARDAR (o si ya llegó al límite de 3/3)
      ui.toast('Muestreo guardado con éxito.', 'success')
      router.push({ name: 'Muestreo' })
    }
  }
}

const volver = () => {
  router.push({ name: 'Muestreo' })
}
</script>

<style scoped>
/* Los mismos estilos que tenías en el paso anterior se mantienen idénticos */
.humedad-page {
  padding: var(--page-padding);
  max-width: 650px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  min-height: calc(100vh - 60px);
}

.btn-back {
  background: none;
  border: none;
  color: var(--color-text);
  font-size: var(--text-lg);
  font-family: var(--font-main);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  padding: var(--spacing-sm) 0;
}

.lote-header-card {
  margin-bottom: var(--spacing-sm);
}

.prominent-field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.prominent-label {
  color: var(--color-text-dim);
  font-size: var(--text-sm);
  font-weight: bold;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.prominent-value-box {
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
}

.prominent-value {
  font-size: var(--text-xl);
  font-weight: 700;
}

.mono {
  font-family: var(--font-mono);
}

.gold {
  color: var(--color-gold);
}

.form-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.input-group label {
  display: block;
  color: var(--color-text-muted);
  font-size: var(--text-md);
  margin-bottom: var(--spacing-sm);
  font-weight: bold;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input {
  width: 100%;
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-family: var(--font-mono);
  font-size: var(--text-xxl);
  padding: var(--spacing-md) var(--spacing-lg);
  text-align: right;
  padding-right: 3rem;
}

.input-wrapper input:focus {
  outline: none;
  border-color: var(--color-gold);
  box-shadow: 0 0 0 2px var(--color-gold-bg);
}

.input-wrapper .unit {
  position: absolute;
  right: var(--spacing-lg);
  color: var(--color-text-muted);
  font-size: var(--text-xl);
  font-family: var(--font-mono);
}

.result-box {
  background: var(--color-bg-card);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  text-align: center;
  margin-top: var(--spacing-md);
  position: relative;
}

.result-value {
  color: var(--color-gold);
  font-size: var(--text-title);
  font-family: var(--font-mono);
  line-height: 1;
  margin: var(--spacing-md) 0;
  text-shadow: 0 0 20px var(--color-gold-bg);
}

.intentos-badge {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  background: var(--color-bg-input);
  color: var(--color-text-dim);
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-family: var(--font-mono);
}

.actions-footer {
  display: flex;
  gap: var(--spacing-md);
  margin-top: auto;
  padding-bottom: var(--spacing-lg);
}

.btn-tablet-xl {
  flex: 1;
  padding: var(--spacing-lg);
  font-size: var(--text-xl);
  border-radius: var(--radius-md);
  font-weight: bold;
  text-transform: uppercase;
}

.textarea-observaciones {
  width: 100%;
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-family: var(--font-main);
  font-size: var(--text-base);
  padding: var(--spacing-md);
  resize: vertical;
  min-height: 80px;
}

.textarea-observaciones:focus {
  outline: none;
  border-color: var(--color-gold);
  box-shadow: 0 0 0 2px var(--color-gold-bg);
}
</style>
