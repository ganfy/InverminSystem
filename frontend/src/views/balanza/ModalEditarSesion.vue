<template>
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>EDITAR SESIÓN</h2>
          <button class="btn-cerrar" @click="$emit('close')">✕</button>
        </div>
        <div class="modal-body">
          <div class="seccion-edit">
            <div class="seccion-edit-titulo">PROVEEDOR Y ACOPIADOR</div>
            <div class="form-grid">
              <div class="field field-full">
                <label class="field-label">Proveedor (buscar)</label>
                <div class="autocomplete-wrap">
                  <input
                    class="field-input"
                    v-model="modalData.busqProv"
                    placeholder="Buscar proveedor..."
                    @input="modalData.editProv = null; modalData.editAcop = null; modalData.dropProv = true"
                    @focus="modalData.dropProv = true"
                    @blur="onBlurProv"
                    autocomplete="off"
                  />
                  <div v-if="modalData.dropProv && provsFiltrados.length" class="ac-dropdown">
                    <div
                      v-for="p in provsFiltrados" :key="p.proveedor_id"
                      class="ac-item"
                      @mousedown.prevent="$emit('selProv', p)"
                    >{{ p.proveedor_razon_social }}</div>
                  </div>
                </div>
              </div>
              <div class="field field-full">
                <label class="field-label">Acopiador</label>
                <div class="autocomplete-wrap">
                  <input
                    class="field-input"
                    :class="{ 'field-disabled': !modalData.editProv }"
                    v-model="modalData.busqAcop"
                    :disabled="!modalData.editProv"
                    placeholder="Seleccione proveedor primero"
                    @focus="modalData.dropAcop = true"
                    @blur="onBlurAcop"
                    autocomplete="off"
                  />
                  <div v-if="modalData.dropAcop && acopsFiltrados.length" class="ac-dropdown">
                    <div
                      v-for="a in acopsFiltrados" :key="a.provacop_id"
                      class="ac-item"
                      @mousedown.prevent="$emit('selAcop', a)"
                    >{{ a.acopiador_razon_social }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="seccion-edit">
            <div class="seccion-edit-titulo">DATOS DE TRANSPORTE</div>
            <div class="form-grid">
              <div class="field">
                <label class="field-label">Placa</label>
                <input class="field-input" v-model="modalData.form.placa" style="text-transform:uppercase" />
              </div>
              <div class="field">
                <label class="field-label">Carreta</label>
                <input class="field-input" v-model="modalData.form.carreta" />
              </div>
              <div class="field field-full">
                <label class="field-label">Conductor</label>
                <input class="field-input" v-model="modalData.form.conductor" />
              </div>
              <div class="field field-full">
                <label class="field-label">Transportista</label>
                <input class="field-input" v-model="modalData.form.transportista" />
              </div>
              <div class="field field-full">
                <label class="field-label">Razón social</label>
                <input class="field-input" v-model="modalData.form.razon_social" />
              </div>
              <div class="field">
                <label class="field-label">Guía de Remisión</label>
                <input class="field-input" v-model="modalData.form.guia_remision" />
              </div>
              <div class="field">
                <label class="field-label">Guía de Transporte</label>
                <input class="field-input" v-model="modalData.form.guia_transporte" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="$emit('close')">Cancelar</button>
          <button class="btn-primary ready" :disabled="guardando" @click="$emit('save')">
            <span v-if="guardando" class="spinner" />
            <span v-else>Guardar cambios</span>
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
  const props = defineProps<{
    modalData: any;
    guardando: boolean;
    provsFiltrados: any[];
    acopsFiltrados: any[];
  }>()

  defineEmits(['close', 'save', 'selProv', 'selAcop'])

  function onBlurProv() { setTimeout(() => { props.modalData.dropProv = false }, 150) }
  function onBlurAcop() { setTimeout(() => { props.modalData.dropAcop = false }, 150) }
</script>

<style scoped>
/* ── Modal edición ───────────────────────────────────────── */
.seccion-edit { margin-bottom: 1.25rem; }
.seccion-edit-titulo {
  font-family: var(--font-mono); font-size: var(--text-sm); letter-spacing: .18em;
  color: var(--color-gold); margin-bottom: .75rem;
  padding-bottom: .3rem; border-bottom: 1px solid var(--color-border);
}
.field-disabled { opacity: .4; cursor: not-allowed; }

</style>
