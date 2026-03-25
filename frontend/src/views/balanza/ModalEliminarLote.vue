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
