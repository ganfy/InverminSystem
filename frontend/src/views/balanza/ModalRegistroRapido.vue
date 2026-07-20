<template>
  <div v-if="isOpen" class="modal-overlay" @mousedown.self="closeModal">
    <div class="modal-content" style="max-width: 500px;">
      <div class="modal-header">
        <h2 class="modal-title">
          <Zap :size="20" style="margin-right:0.5rem" />
          Registro Rápido
        </h2>
        <button class="modal-close" @click="closeModal"><X :size="20" /></button>
      </div>

      <div class="modal-body">
        <p style="margin-bottom: 1rem; color: var(--color-text-dim);">
          Registre rápidamente un proveedor y/o acopiador para continuar. Los parámetros comerciales deberán configurarse luego en la pantalla de Terceros.
        </p>

        <form @submit.prevent="submit" class="form-grid">
          <div v-if="proveedorPreseleccionado" class="field" style="grid-column: 1 / -1; margin-bottom: 1rem; padding: 0.75rem; background: var(--color-bg-subtle); border-radius: 6px;">
            <label class="field-label" style="margin-bottom: 0.25rem;">PROVEEDOR SELECCIONADO</label>
            <div style="font-weight: 500;">{{ proveedorPreseleccionado.razon_social }}</div>
            <div style="font-size: var(--text-sm); color: var(--color-text-dim);">RUC: {{ proveedorPreseleccionado.ruc }}</div>
          </div>
          <template v-else>
            <div class="field" style="grid-column: 1 / -1">
              <label class="field-label required">PROVEEDOR (Razón Social)</label>
              <input
                v-model="form.proveedor_razon_social"
                class="field-input"
                required
                placeholder="Ej: Minera San Juan S.A.C."
                ref="firstInput"
              />
            </div>

            <div class="field" style="grid-column: 1 / -1">
              <label class="field-label required">RUC PROVEEDOR</label>
              <input
                v-model="form.proveedor_ruc"
                class="field-input"
                required
                placeholder="Ej: 20123456789"
                minlength="11"
                maxlength="11"
              />
            </div>
          </template>

          <div class="field" style="grid-column: 1 / -1; margin-top: 1rem;">
            <label class="field-label" :class="{ required: proveedorPreseleccionado }">ACOPIADOR {{ proveedorPreseleccionado ? '' : '(Opcional)' }}</label>
            <p v-if="!proveedorPreseleccionado" style="font-size: var(--text-xs); color: var(--color-text-dim); margin-bottom: 0.5rem;">
              Si se deja en blanco, se asumirá "Auto-acopio" (el proveedor es su propio acopiador).
            </p>
            <input
              v-model="form.acopiador_razon_social"
              class="field-input"
              :required="!!proveedorPreseleccionado"
              placeholder="Ej: Juan Perez"
              ref="acopiadorInput"
            />
          </div>
        </form>

        <div v-if="errorMsg" class="alert-error" style="margin-top: 1rem;">
          <XCircle :size="16" /> {{ errorMsg }}
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn-secondary" @click="closeModal" :disabled="cargando">Cancelar</button>
        <button type="submit" class="btn-primary" @click="submit" :disabled="cargando">
          <span v-if="cargando" class="spinner" style="margin-right:0.5rem" />
          {{ cargando ? 'Guardando...' : 'Guardar y Continuar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick } from 'vue'
import { X, Zap, XCircle } from 'lucide-vue-next'
import tercerosApi from '@/api/terceros'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

const isOpen = ref(false)
const cargando = ref(false)
const errorMsg = ref('')

const firstInput = ref<HTMLInputElement | null>(null)
const acopiadorInput = ref<HTMLInputElement | null>(null)
const proveedorPreseleccionado = ref<{ id: number; razon_social: string; ruc: string } | null>(null)

const form = reactive({
  proveedor_razon_social: '',
  proveedor_ruc: '',
  acopiador_razon_social: ''
})

const emit = defineEmits<{
  (e: 'registrado', provacop_id: number): void
}>()

function openModal(proveedor?: { id: number; razon_social: string; ruc: string }) {
  isOpen.value = true
  cargando.value = false
  errorMsg.value = ''
  form.proveedor_razon_social = ''
  form.proveedor_ruc = ''
  form.acopiador_razon_social = ''
  
  if (proveedor) {
    proveedorPreseleccionado.value = proveedor
    nextTick(() => {
      acopiadorInput.value?.focus()
    })
  } else {
    proveedorPreseleccionado.value = null
    nextTick(() => {
      firstInput.value?.focus()
    })
  }
}

function closeModal() {
  if (cargando.value) return
  isOpen.value = false
}

async function submit() {
  if (!proveedorPreseleccionado.value) {
    if (!form.proveedor_razon_social.trim()) {
      errorMsg.value = 'La razón social del proveedor es obligatoria'
      return
    }
    if (!form.proveedor_ruc.trim()) {
      errorMsg.value = 'El RUC del proveedor es obligatorio'
      return
    }
    if (form.proveedor_ruc.length !== 11) {
      errorMsg.value = 'El RUC debe tener 11 dígitos'
      return
    }
  } else {
    if (!form.acopiador_razon_social.trim()) {
      errorMsg.value = 'El nombre del acopiador es obligatorio'
      return
    }
  }

  errorMsg.value = ''
  cargando.value = true

  try {
    const payload: any = {
      acopiador_razon_social: form.acopiador_razon_social.trim() || null
    }

    if (proveedorPreseleccionado.value) {
      payload.proveedor_id = proveedorPreseleccionado.value.id
    } else {
      payload.proveedor_razon_social = form.proveedor_razon_social.trim()
      payload.proveedor_ruc = form.proveedor_ruc.trim()
    }

    const res = await tercerosApi.registroRapido(payload)
    
    ui.toast('Tercero registrado exitosamente', 'success')
    emit('registrado', res.provacop_id)
    isOpen.value = false
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Error al registrar'
    errorMsg.value = Array.isArray(msg) ? msg[0].msg : msg
  } finally {
    cargando.value = false
  }
}

defineExpose({
  openModal
})
</script>
