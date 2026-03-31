<template>
    <div class="page-container">
      <header class="page-header">
        <div>
          <h1 class="page-title">Registrar Prueba</h1>
          <p class="page-subtitle">Análisis de preparación para proceso metalúrgico</p>
        </div>
      </header>

      <div class="card">
        <h2 class="card-titulo">DATOS DEL LOTE</h2>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">IP:</label>
            <input type="text" class="field-input" :value="loteInfo.ip" disabled />
          </div>
        </div>
      </div>

      <div class="card">
        <h2 class="card-titulo">LEYES DE LA MUESTRA</h2>
        <div class="form-grid">

          <div class="field">
            <label class="field-label">MALLA (%):</label>
            <input
              type="number"
              class="field-input"
              :class="{ 'error': mostrarWarningMalla }"
              v-model.number="form.malla_porcentaje"
              step="0.01"
            />
            <p v-if="mostrarWarningMalla" class="field-hint" style="color: var(--color-warning);">
              ⚠️ El porcentaje de malla está fuera del rango aceptable (88% - 94%).
            </p>
          </div>

          <div class="field">
            <label class="field-label">GASTO AgNO3 (ml):</label>
            <input type="number" class="field-input" v-model.number="form.gasto_agno3" step="0.01" />
          </div>

          <div class="field">
            <label class="field-label">ADICIÓN NaCN (g):</label>
            <input type="number" class="field-input" v-model.number="form.adicion_nacn" step="0.01" />
          </div>

          <div class="field">
            <label class="field-label">NaCN (%):</label>
            <input type="number" class="field-input" v-model.number="form.porcentaje_nacn" step="0.01" />
          </div>

          <div class="field">
            <label class="field-label">ADICIÓN NaOH (g):</label>
            <input type="number" class="field-input" v-model.number="form.adicion_naoh" step="0.01" />
          </div>

          <div class="field">
            <label class="field-label">pH INICIAL:</label>
            <input type="number" class="field-input" v-model.number="form.ph_inicial" step="0.01" />
          </div>

          <div class="field">
            <label class="field-label">pH FINAL:</label>
            <input type="number" class="field-input" v-model.number="form.ph_final" step="0.01" />
          </div>
        </div>
      </div>

      <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;">
        <button class="btn-secondary" @click="volver">Volver</button>
        <button class="btn-primary" @click="guardarPrueba" :disabled="guardando">
          <span v-if="guardando" class="spinner-sm" style="margin-right: 0.5rem;"></span>
          Guardar
        </button>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useUiStore } from '@/stores/ui'
  import { useSync } from '@/composables/useSync'
  import { pruebasApi } from '@/api/pruebas'
  import { encolarPruebaOffline } from '@/composables/useOfflineQueue'

  const router = useRouter()
  const route = useRoute()
  const ui = useUiStore()
  const { online } = useSync()

  // Capturamos la IP directo de la ruta
  const ipActual = route.params.ip as string

  const loteInfo = ref({
    ip: ipActual
  })

  const form = ref({
    malla_porcentaje: null as number | null,
    porcentaje_nacn: null as number | null,
    ph_inicial: null as number | null,
    ph_final: null as number | null,
    adicion_nacn: null as number | null,
    adicion_naoh: null as number | null,
    gasto_agno3: null as number | null,
  })

  const guardando = ref(false)

  const mostrarWarningMalla = computed(() => {
    if (form.value.malla_porcentaje === null || form.value.malla_porcentaje === undefined) return false
    return form.value.malla_porcentaje < 88 || form.value.malla_porcentaje > 94
  })

  const volver = () => {
    router.push('/pruebas')
  }

  const guardarPrueba = async () => {
    if (!ipActual) {
      ui.toast('No se detectó un código IP válido.', 'error')
      return
    }

    guardando.value = true
    const fechaActual = new Date().toISOString()

    const sanitizeNumber = (val: any) => (val === '' || val === null || val === undefined) ? null : Number(val)
    const payload = {
      malla_porcentaje: sanitizeNumber(form.value.malla_porcentaje),
      porcentaje_nacn: sanitizeNumber(form.value.porcentaje_nacn),
      ph_inicial: sanitizeNumber(form.value.ph_inicial),
      ph_final: sanitizeNumber(form.value.ph_final),
      adicion_nacn: sanitizeNumber(form.value.adicion_nacn),
      adicion_naoh: sanitizeNumber(form.value.adicion_naoh),
      gasto_agno3: sanitizeNumber(form.value.gasto_agno3),
      fecha_ingreso: fechaActual
    }

    try {
      if (online.value) {
        // Guardado normal (Online) usando la IP
        const response = await pruebasApi.registrarPrueba(ipActual, payload)
        ui.toast('Prueba registrada correctamente', 'success')
        if (response.warning) ui.toast(response.warning, 'warning')
      } else {
        // Guardado a la cola (Offline) usando la IP
        const offlineId = `pm-${Date.now()}`
        await encolarPruebaOffline({
          offline_id: offlineId,
          ip: ipActual,
          datos: payload,
          synced: false,
          sync_error: null
        })
        ui.toast('Sin conexión. Prueba guardada localmente.', 'warning')
      }

      setTimeout(() => { volver() }, 1000)

    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Ocurrió un error al guardar la prueba'
      ui.toast(msg, 'error')
    } finally {
      guardando.value = false
    }
  }
  </script>
