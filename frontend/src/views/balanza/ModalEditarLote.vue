<template>
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-header">
          <h2>EDITAR LOTE {{ modalData.ip }}</h2>
          <button class="btn-cerrar" @click="$emit('close')"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field field-full">
              <label class="field-label">Tipo de material</label>
              <select class="field-input field-select" v-model="modalData.form.tipo_material">
                <option value="Mineral">Mineral</option>
                <option value="Llampo">Llampo</option>
                <option value="M.Llampo">M.Llampo</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">BRUTO / peso_inicial ({{ getUnidadPorModulo('BALANZA') }})</label>
              <input class="field-input" type="number" step="0.001" v-model.number="modalData.form.peso_inicial" />
            </div>
            <div class="field">
              <label class="field-label">TARA / peso_final ({{ getUnidadPorModulo('BALANZA') }})</label>
              <input class="field-input" type="number" step="0.001" v-model.number="modalData.form.peso_final" />
            </div>
            <div class="field">
              <label class="field-label">N° Sacos</label>
              <input class="field-input" type="number" min="0" v-model.number="modalData.form.sacos" :disabled="modalData.form.granel" />
            </div>
            <div class="field" style="display:flex;align-items:center;gap:.5rem;padding-top:1.5rem">
              <input type="checkbox" id="edit-granel" v-model="modalData.form.granel" @change="modalData.form.sacos = null" />
              <label for="edit-granel" class="field-label" style="margin:0">Granel</label>
            </div>

            <template v-if="isAdmin">
              <div class="field field-full" style="padding-top:0.75rem;border-top:1px solid var(--color-border)">
                <div class="seccion-edit-titulo" style="font-family:var(--font-mono);font-size:0.7rem;letter-spacing:.15em;color:var(--color-gold);margin-bottom:0.5rem">
                  FECHAS DEL PESAJE <span class="badge-admin">ADMIN</span>
                </div>
              </div>
              <div class="field">
                <label class="field-label">Fecha/hora BRUTO (camión cargado)</label>
                <input type="datetime-local" class="field-input" v-model="modalData.form.fecha_inicio" />
              </div>
              <div class="field">
                <label class="field-label">Fecha/hora TARA (camión vacío)</label>
                <input type="datetime-local" class="field-input" v-model="modalData.form.fecha_fin" />
              </div>
            </template>

            <div class="field field-full" style="padding-top: 1rem;">
              <label class="field-label" style="color: var(--color-warning);">Justificación de Edición Manual *</label>
              <textarea class="field-input" rows="2" v-model="modalData.form.justificacion_manual" placeholder="Obligatorio..."></textarea>
            </div>
          </div>
          <p v-if="modalData.error" class="error-msg" style="margin-top:.75rem">{{ modalData.error }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="$emit('close')">Cancelar</button>
          <button class="btn-primary ready" :disabled="guardando" @click="$emit('save')">
            <span v-if="guardando" class="spinner" />
            <span v-else>Guardar</span>
          </button>
        </div>
      </div>
    </div>
  </template>

<script setup lang="ts">

import { getUnidadPorModulo } from '@/utils/units'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'
import { X } from 'lucide-vue-next'

const auth = useAuthStore()
const isAdmin = computed(() => auth.user?.rol === 'Admin')

defineProps<{ modalData: any; guardando: boolean }>()
defineEmits(['close', 'save'])
</script>
