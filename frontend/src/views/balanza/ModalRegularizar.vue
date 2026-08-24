<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>REGULARIZAR LOTES OBSERVADOS</h2>
        <button class="btn-cerrar" @click="$emit('close')"><X :size="18" /></button>
      </div>

      <div class="modal-body">
        <p>
          Se detectaron <strong>{{ opsCount }}</strong> lote(s) observado(s) (OP) en esta sesión.
        </p>
        <p v-if="opsCount > 1">
          ¿Desea regularizar <strong>todos</strong> los lotes observados de esta sesión, o solo el lote seleccionado (<strong>{{ loteNumero }}</strong>)?
        </p>
        <p v-else>
          ¿Desea regularizar el lote <strong>{{ loteNumero }}</strong> y generar su IP oficial?
        </p>
      </div>

      <div class="modal-footer" style="justify-content: flex-end; gap: 0.5rem; margin-top: 1rem;">
        <button class="btn-secondary" @click="$emit('close')">Cancelar</button>
        <button 
          v-if="opsCount > 1" 
          class="btn-primary" 
          @click="$emit('regularizar-todos')"
          :disabled="guardando"
        >
          Regularizar Todos (Recomendado)
        </button>
        <button 
          class="btn-primary" 
          @click="$emit('regularizar-uno')"
          :disabled="guardando"
        >
          Regularizar Solo Este
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'

defineProps<{
  opsCount: number
  loteNumero: number | string
  guardando: boolean
}>()

defineEmits(['close', 'regularizar-uno', 'regularizar-todos'])
</script>
