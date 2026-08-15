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
          <label>PESO HÚMEDO (g) - GLOBAL</label>
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

        <div v-for="(peso, index) in pesosSecos" :key="index" class="input-group">
          <label>PESO SECO ENSAYO {{ intentoActual + index }} (g)</label>
          <div class="input-wrapper">
            <input
              v-model="pesosSecos[index]"
              type="number"
              inputmode="decimal"
              placeholder="0"
            />
            <span class="unit">g</span>
          </div>
        </div>

        <button 
          v-if="Number(intentoActual) + pesosSecos.length <= maxIntentos" 
          class="btn-secondary btn-sm add-btn" 
          @click="addEnsayo"
        >
          + Añadir Ensayo
        </button>

        <div class="input-group" style="margin-top: 1rem;">
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
          <label>% HUMEDAD PROMEDIO</label>
          <div class="result-value" :class="{ 'parametro-ajustado': esAjustadoPorParametro }">
            {{ porcentajeHumedadPromedio > 0 ? porcentajeHumedadPromedio.toFixed(2) : '0.00' }}%
          </div>
          <div v-if="esAjustadoPorParametro" class="parametro-badge" :title="`Calculado real: ${humedadCalculadaRaw.toFixed(2)}%`">
            ⚠ Humedad mínima contractual aplicada ({{ humedadMinimaParametro?.toFixed(2) }}%)
          </div>
          <div class="intentos-badge">Ingresando {{ pesosSecos.length }} ensayos (Máx {{ maxIntentos }})</div>
        </div>
      </div>

      <div class="actions-footer">
        <button class="btn-primary ready btn-tablet-xl" :disabled="!puedeGuardar || store.guardando" @click="confirmarGuardado">
          Guardar Ensayos
        </button>
      </div>

      <!-- Modal de Confirmación -->
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal">
          <div class="modal-header">
            <h2>Confirmar Ensayos</h2>
            <button class="btn-cerrar" @click="showModal = false">×</button>
          </div>
          <div class="modal-body">
            <p style="color:var(--color-text-muted); margin-bottom: 1rem;">
              Se guardarán los siguientes ensayos para el lote <strong>{{ ipLote }}</strong>:
            </p>
            
            <table class="modal-table">
              <thead>
                <tr>
                  <th>Ensayo</th>
                  <th>P. Húmedo</th>
                  <th>P. Seco</th>
                  <th>Humedad</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(seco, idx) in ensayosValidos" :key="idx">
                  <td>{{ intentoActual + idx }}</td>
                  <td>{{ pesoHumedo }}g</td>
                  <td>{{ seco }}g</td>
                  <td>{{ store.calcularHumedad(pesoHumedo!, seco).toFixed(2) }}%</td>
                </tr>
              </tbody>
            </table>

            <div class="modal-promedio">
              <strong>Promedio Total:</strong> <span class="gold">{{ porcentajeHumedadPromedio.toFixed(2) }}%</span>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showModal = false">Cancelar</button>
            <button class="btn-primary" @click="guardarBatch" :disabled="store.guardando">
              {{ store.guardando ? 'Guardando...' : 'Confirmar Guardado' }}
            </button>
          </div>
        </div>
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
const pesosSecos = ref<(number | null)[]>([null])
const observaciones = ref<string>('')
const intentoActual = ref(1)
const maxIntentos = 3
const showModal = ref(false)

const ensayosValidos = computed(() => {
  return pesosSecos.value.filter(s => s !== null && s > 0 && pesoHumedo.value !== null && s < pesoHumedo.value) as number[]
})

const loteActual = computed(() => {
  return store.lotesPendientes.find(l => l.ip === ipLote) || store.lotesCompletados.find(l => l.ip === ipLote)
})
const humedadMinimaParametro = computed(() => loteActual.value?.humedad_minima ?? null)

const humedadCalculadaRaw = computed(() => {
  if (ensayosValidos.value.length === 0 || !pesoHumedo.value) return 0
  let totalHumedad = 0
  ensayosValidos.value.forEach(seco => {
    totalHumedad += store.calcularHumedad(pesoHumedo.value!, seco)
  })
  return totalHumedad / ensayosValidos.value.length
})

const esAjustadoPorParametro = computed(() => {
  if (humedadMinimaParametro.value == null || humedadCalculadaRaw.value <= 0) return false
  return humedadCalculadaRaw.value < humedadMinimaParametro.value
})

const porcentajeHumedadPromedio = computed(() => {
  if (esAjustadoPorParametro.value && humedadMinimaParametro.value != null) {
    return humedadMinimaParametro.value
  }
  return humedadCalculadaRaw.value
})

const puedeGuardar = computed(() => {
  return ensayosValidos.value.length > 0 && ensayosValidos.value.length === pesosSecos.value.length
})

onMounted(async () => {
  await store.cargarLotes()
  intentoActual.value = await store.calcularProximoIntento(ipLote)

  if (intentoActual.value > maxIntentos) {
    ui.toast('Este lote ya completó sus 3 intentos de muestreo.', 'warning')
    router.push({ name: 'Muestreo' })
  }
})

const addEnsayo = (e?: Event) => {
  if (e) e.preventDefault();
  if (Number(intentoActual.value) + pesosSecos.value.length <= maxIntentos) {
    pesosSecos.value.push(null)
  }
}

const confirmarGuardado = () => {
  if (!puedeGuardar.value) return
  showModal.value = true
}

const guardarBatch = async () => {
  if (!puedeGuardar.value || !pesoHumedo.value) return

  const datosList = ensayosValidos.value.map((seco, index) => ({
    intento: intentoActual.value + index,
    peso_humedo: pesoHumedo.value!,
    peso_seco: seco,
    observaciones: observaciones.value.trim() || null,
  }))

  const exito = await store.registrarHumedadBatch(ipLote, datosList)

  if (exito) {
    showModal.value = false
    ui.toast('Ensayos guardados con éxito.', 'success')
    router.push({ name: 'Muestreo' })
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
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  color: var(--color-text);
  font-family: inherit;
  font-size: var(--text-sm);
  resize: vertical;
}

.parametro-ajustado {
  border: 2px dashed #eab308 !important;
  border-radius: 6px;
  padding: 0.2rem 0.6rem;
  background: rgba(234, 179, 8, 0.12) !important;
  color: #eab308 !important;
  display: inline-block;
}

.parametro-badge {
  font-size: 0.78rem;
  color: #eab308;
  margin-top: 0.35rem;
  font-weight: 600;
}

.textarea-observaciones:focus {
  outline: none;
  border-color: var(--color-gold);
  box-shadow: 0 0 0 2px var(--color-gold-bg);
}

.add-btn {
  align-self: flex-start;
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px dashed var(--color-border);
  background: transparent;
  color: var(--color-text);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.add-btn:hover {
  border-color: var(--color-gold);
  color: var(--color-gold);
  background: var(--color-bg-card);
}

.modal-table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--spacing-md) 0;
  font-family: var(--font-mono);
}

.modal-table th, .modal-table td {
  border: 1px solid var(--color-border);
  padding: var(--spacing-md);
  text-align: center;
}

.modal-table th {
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  text-transform: uppercase;
}

.modal-table td {
  font-size: var(--text-md);
}

.modal-promedio {
  font-size: var(--text-xl);
  text-align: right;
  margin-top: var(--spacing-md);
  padding-right: var(--spacing-sm);
}
</style>
