<template>
  <div class="modal-overlay" @click.self="cerrarSiSeguro">
    <div class="modal-box">

      <header class="modal-header">
        <h2 class="modal-title">Hermanos — {{ ip }}</h2>
        <button class="btn-icon" @click="cerrarSiSeguro">✕</button>
      </header>

      <!-- Hermanos actuales -->
      <section class="modal-seccion">
        <p class="seccion-label">Hermanos vinculados</p>
        <div v-if="hermanos.length" class="chips-row">
          <div v-for="h in hermanos" :key="h" class="chip-hermano-item">
            <span class="chip-ip">{{ h }}</span>
            <button
              class="btn-desvincular"
              :disabled="cargando"
              :title="`Quitar vínculo con ${h}`"
              @click="confirmarDesvincular"
            >✕</button>
          </div>
        </div>
        <p v-else class="texto-muted">Sin hermanos vinculados.</p>
      </section>

      <!-- Vincular nuevo -->
      <section class="modal-seccion">
        <p class="seccion-label">Vincular IP hermano</p>
        <div class="input-row">
          <input
            v-model="ipNuevo"
            class="field-input"
            placeholder="IP-XXXX"
            :disabled="cargando"
            @keyup.enter="vincular"
          />
          <button
            class="btn-primary btn-sm"
            :disabled="cargando || !ipNuevo.trim()"
            @click="vincular"
          >Vincular</button>
        </div>
      </section>

      <!-- Completar por referencia -->
      <section v-if="hermanos.length" class="modal-seccion seccion-ref">
        <hr class="divider" />
        <p class="seccion-label">Completar por referencia</p>
        <p class="texto-hint">
          Copia la humedad del IP fuente, genera los CIPs paralelos y clona
          los análisis de ley y recuperación.
          El TMS se recalcula con el peso neto propio de este lote.
          <strong>Solo disponible si este lote no tiene muestreo propio. No se puede deshacer.</strong>
        </p>

        <!-- Paso 1: elegir fuente -->
        <div v-if="!confirmarRef" class="input-row">
          <select v-model="ipFuente" class="field-input field-select" :disabled="cargando">
            <option value="">Seleccionar IP fuente…</option>
            <option v-for="h in hermanos" :key="h" :value="h">{{ h }}</option>
          </select>
          <button
            class="btn-secondary btn-sm"
            :disabled="cargando || !ipFuente"
            @click="confirmarRef = true"
          >Completar…</button>
        </div>

        <!-- Paso 2: confirmación inline -->
        <div v-else class="confirm-inline">
          <p class="confirm-inline-msg">
            ¿Completar <strong>{{ ip }}</strong> usando datos de <strong>{{ ipFuente }}</strong>?
            Esta acción no se puede deshacer.
          </p>
          <div class="confirm-inline-btns">
            <button class="btn-secondary btn-sm" :disabled="cargando" @click="confirmarRef = false">Cancelar</button>
            <button class="btn-danger btn-sm" :disabled="cargando" @click="completarPorReferencia">
              {{ cargando ? 'Procesando…' : 'Sí, completar' }}
            </button>
          </div>
        </div>
      </section>

      <p v-if="error" class="error-inline" style="margin-top:0.75rem">{{ error }}</p>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { laboratorioApi } from '@/api/laboratorio'
import { useUiStore } from '@/stores/ui'

const props = defineProps<{
  ip: string
  hermanos: string[]
}>()      

const emit = defineEmits<{
  close: []
  actualizar: []
}>()

const ui = useUiStore()
const ipNuevo    = ref('')
const ipFuente   = ref('')
const error      = ref('')
const cargando   = ref(false)
const confirmarRef   = ref(false)  // paso de confirmación inline para Completar
const confirmarDesv  = ref(false)  // paso de confirmación inline para Desvincular

function cerrarSiSeguro() {
  if (!cargando.value) emit('close')
}

async function vincular() {
  if (!ipNuevo.value.trim()) return
  error.value = ''
  cargando.value = true
  try {
    await laboratorioApi.vincularHermanos(props.ip, ipNuevo.value.trim())
    ipNuevo.value = ''
    emit('actualizar')
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Error al vincular'
  } finally {
    cargando.value = false
  }
}

function confirmarDesvincular() {
  confirmarDesv.value = true
}

async function desvincular() {
  error.value = ''
  cargando.value = true
  try {
    await laboratorioApi.desvincularHermano(props.ip)
    emit('actualizar')
    emit('close')
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Error al desvincular'
    confirmarDesv.value = false
  } finally {
    cargando.value = false
  }
}

async function completarPorReferencia() {
  if (!ipFuente.value) return
  error.value = ''
  cargando.value = true
  try {
    const res = await laboratorioApi.completarPorReferencia(props.ip, ipFuente.value)
    const cipsStr = res.cips_generados.join(', ')
    ui.toast(
      `Completado. CIPs: ${cipsStr} · ` +
      `${res.analisis_ley_copiados} análisis de ley · ${res.analisis_rec_copiados} de recuperación` +
      (res.tms_calculado != null ? ` · TMS: ${res.tms_calculado}` : ''),
      'success'
    )
    emit('actualizar')
    emit('close')
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Error al completar'
    confirmarRef.value = false
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 900;
}
.modal-box {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
  width: min(480px, 95vw);
  max-height: 85vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}
.modal-title {
  font-size: 1rem;
  font-family: var(--font-mono);
  color: var(--color-gold);
}
.modal-seccion { margin-bottom: 1.25rem; }
.seccion-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
  margin-bottom: 0.5rem;
}
.chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.chip-hermano-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--color-surface-2, rgba(255,255,255,0.05));
  border: 1px solid var(--color-border-subtle, rgba(255,255,255,0.1));
  border-radius: 4px;
  padding: 2px 6px;
}
.chip-ip {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--color-gold);
}
.btn-desvincular {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 0.7rem;
  padding: 0 2px;
  line-height: 1;
}
.btn-desvincular:hover { color: var(--color-danger, #e05); }
.btn-icon {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 2px 4px;
}
.btn-icon:hover { color: var(--color-text); }
.input-row {
  display: flex;
  gap: 0.5rem;
}
.input-row .field-input { flex: 1; }
.seccion-ref { margin-top: 0.5rem; }
.texto-hint {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  margin-bottom: 0.75rem;
  line-height: 1.5;
}
.texto-muted {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.divider {
  border: none;
  border-top: 1px solid var(--color-border-subtle, rgba(255,255,255,0.08));
  margin-bottom: 1rem;
}
.error-inline {
  font-size: 0.8rem;
  color: var(--color-danger, #e05);
}
.confirm-inline {
  background: rgba(220, 38, 38, 0.06);
  border: 1px solid rgba(220, 38, 38, 0.25);
  border-radius: 6px;
  padding: 0.75rem 1rem;
}
.confirm-inline-msg {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  margin: 0 0 0.75rem;
  line-height: 1.5;
}
.confirm-inline-btns {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
.btn-danger {
  padding: 0.35rem 0.85rem;
  border-radius: 3px;
  border: none;
  font-family: var(--font-mono);
  font-size: var(--text-sm, 0.8rem);
  font-weight: 600;
  cursor: pointer;
  background: rgba(220, 38, 38, 0.8);
  color: #fff;
  transition: background 0.15s;
}
.btn-danger:hover:not(:disabled) { background: rgba(220, 38, 38, 1); }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
