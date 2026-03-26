<template>
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Eliminar {{ modalData.ip }}</h2>
          <button class="btn-cerrar" @click="$emit('close')">✕</button>
        </div>
        <div class="modal-body">
          <p class="elim-aviso">Acción irreversible — queda registrado en auditoría.</p>
          <p v-if="modalData.error" class="error-msg">{{ modalData.error }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="$emit('close')">Cancelar</button>
          <button class="btn-danger" :disabled="guardando" @click="$emit('confirm')">
            <span v-if="guardando" class="spinner" />
            <span v-else>Eliminar</span>
          </button>
        </div>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  defineProps<{ modalData: any; guardando: boolean }>()
  defineEmits(['close', 'confirm'])
  </script>

  <style scoped>
    .elim-aviso { font-size: var(--text-md); color: var(--color-error); margin: 0; }
    .bottom-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding-top: 1rem; border-top: 1px solid var(--color-border);
    }
    .bottom-bar-acciones { display: flex; gap: .75rem; }
    .estado-tabla { padding: 2rem; text-align: center; color: var(--color-text-muted); }
    .form-faltantes {
    display: flex; align-items: center; gap: 0.4rem;
    font-family: var(--font-mono); font-size: var(--text-sm);
    color: var(--color-warning); background: rgba(207, 151, 61, 0.08);
    border: 1px solid rgba(207, 151, 61, 0.3); border-radius: var(--radius-sm);
    padding: 0.4rem 0.75rem; margin-bottom: 0.5rem;
    }
    .faltante-icono { font-size: var(--text-base); }
    .btn-incompleto {
    border-color: var(--color-warning) !important;
    box-shadow: 0 0 0 1px var(--color-warning);
    }
</style>
