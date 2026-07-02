<template>
    <div class="page-container">
      <header class="page-header">
        <div>
          <h1 class="page-title">Registrar Prueba{{ modoLote ? ' en Lote' : '' }}</h1>
          <p class="page-subtitle">Análisis de preparación para proceso metalúrgico</p>
        </div>
      </header>

      <!-- Banner de modo lote -->
      <div v-if="modoLote" class="lote-banner">
        <div class="lote-banner-header">
          <Layers :size="18" style="flex-shrink:0" />
          <strong>REGISTRO EN LOTE — {{ ipsLote.length }} botellas</strong>
        </div>
        <div class="lote-ips">
          <span v-for="ip in ipsLote" :key="ip" class="lote-ip-badge">{{ ip }}</span>
        </div>
        <p style="font-size:0.78rem;color:var(--color-text-muted);margin-top:0.4rem">
          Los mismos valores se registrarán para todas las botellas seleccionadas.
          La fecha de ingreso será la misma para todas.
        </p>
      </div>

      <!-- Resultados del lote -->
      <div v-if="resultadosLote.length > 0" class="lote-resultados">
        <div
          v-for="r in resultadosLote"
          :key="r.ip"
          class="lote-resultado-item"
          :class="r.ok ? 'ok' : 'err'"
        >
          <span class="td-mono" style="font-weight:700">{{ r.ip }}</span>
          <span v-if="r.ok">✓ Guardado</span>
          <span v-else>✗ {{ r.error }}</span>
        </div>
      </div>

      <div class="card">
        <h2 class="card-titulo">DATOS DEL LOTE</h2>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">IP{{ modoLote ? ' (primer lote)' : '' }}:</label>
            <input type="text" class="field-input" :value="ipActual" disabled />
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
              <AlertTriangle :size="16" /> El porcentaje de malla está fuera del rango aceptable (88% - 94%).
            </p>
          </div>

          <div class="field">
            <label class="field-label">GASTO AgNO3 (ml):</label>
            <input type="number" class="field-input" v-model.number="form.gasto_agno3" step="0.01" />
          </div>

          <div class="field">
            <label class="field-label">NaCN (%):</label>
            <input type="number" class="field-input" v-model.number="form.porcentaje_nacn" step="0.01" />
          </div>

          <div class="field">
            <label class="field-label">pH INICIAL:</label>
            <input type="number" class="field-input" v-model.number="form.ph_inicial" step="0.01" />
          </div>
        </div>
      </div>

      <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;">
        <button class="btn-secondary" @click="volver">Volver</button>
        <button class="btn-primary" @click="guardarPrueba" :disabled="guardando">
          <span v-if="guardando" class="spinner-sm" style="margin-right: 0.5rem;"></span>
          {{ modoLote ? `Guardar Lote (${ipsLote.length})` : 'Guardar' }}
        </button>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useUiStore } from '@/stores/ui'
  import { useSync } from '@/composables/useSync'
  import { pruebasApi } from '@/api/pruebas'
  import { encolarPruebaOffline } from '@/composables/useOfflineQueue'
  import { AlertTriangle, Layers } from 'lucide-vue-next'

  const router = useRouter()
  const route = useRoute()
  const ui = useUiStore()
  const { online } = useSync()

  // IP principal (del param de ruta)
  const ipActual = route.params.ip as string

  // Modo lote: si viene ?ips=IP-001,IP-002,...
  const ipsLote = computed<string[]>(() => {
    const qIps = route.query.ips as string | undefined
    if (qIps) return qIps.split(',').map(s => s.trim()).filter(Boolean)
    return [ipActual]
  })
  const modoLote = computed(() => ipsLote.value.length > 1)

  interface ResultadoLote { ip: string; ok: boolean; error?: string }
  const resultadosLote = ref<ResultadoLote[]>([])

  const form = ref({
    malla_porcentaje: null as number | null,
    porcentaje_nacn: null as number | null,
    ph_inicial: 6 as number | null,
    ph_final: null as number | null,
    adicion_nacn: null as number | null,
    adicion_naoh: null as number | null,
    gasto_agno3: null as number | null,
  })

  const cargandoDatos = ref(false)
  const guardando = ref(false)

  onMounted(async () => {
    if (modoLote.value) return  // en modo lote no precargamos datos
    cargandoDatos.value = true
    try {
      const datosGuardados = await pruebasApi.obtenerDetallePrueba(ipActual)
      if (datosGuardados) {
        form.value = {
          malla_porcentaje: datosGuardados.malla_porcentaje,
          porcentaje_nacn: datosGuardados.porcentaje_nacn,
          ph_inicial: datosGuardados.ph_inicial,
          ph_final: datosGuardados.ph_final,
          adicion_nacn: datosGuardados.adicion_nacn,
          adicion_naoh: datosGuardados.adicion_naoh,
          gasto_agno3: datosGuardados.gasto_agno3
        }
      }
    } catch (error) {
      console.error('Error cargando la prueba:', error)
    } finally {
      cargandoDatos.value = false
    }
  })

  const mostrarWarningMalla = computed(() => {
    if (form.value.malla_porcentaje === null || form.value.malla_porcentaje === undefined) return false
    return form.value.malla_porcentaje < 88 || form.value.malla_porcentaje > 94
  })

  const volver = () => { router.push('/pruebas') }

  const sanitizeNumber = (val: any) =>
    (val === '' || val === null || val === undefined) ? null : Number(val)

  async function guardarPrueba() {
    guardando.value = true
    resultadosLote.value = []
    const fechaActual = new Date().toISOString()

    const payload = {
      malla_porcentaje: sanitizeNumber(form.value.malla_porcentaje),
      porcentaje_nacn:  sanitizeNumber(form.value.porcentaje_nacn),
      ph_inicial:       sanitizeNumber(form.value.ph_inicial),
      ph_final:         sanitizeNumber(form.value.ph_final),
      adicion_nacn:     sanitizeNumber(form.value.adicion_nacn),
      adicion_naoh:     sanitizeNumber(form.value.adicion_naoh),
      gasto_agno3:      sanitizeNumber(form.value.gasto_agno3),
      fecha_ingreso:    fechaActual,
    }

    const targets = modoLote.value ? ipsLote.value : [ipActual]
    let errores = 0

    for (const ip of targets) {
      if (!ip) { errores++; resultadosLote.value.push({ ip, ok: false, error: 'IP vacío' }); continue }

      try {
        if (online.value) {
          await pruebasApi.registrarPrueba(ip, payload)
          resultadosLote.value.push({ ip, ok: true })
        } else {
          const offlineId = `pm-${Date.now()}-${ip}`
          await encolarPruebaOffline({
            offline_id: offlineId,
            ip,
            datos: payload,
            synced: false,
            sync_error: null
          })
          resultadosLote.value.push({ ip, ok: true })
        }
      } catch (error: any) {
        errores++
        const msg = error.response?.data?.detail || 'Error al guardar'
        resultadosLote.value.push({ ip, ok: false, error: msg })
      }
    }

    guardando.value = false

    if (!modoLote.value) {
      // Modo individual: comportamiento original
      if (errores === 0) {
        ui.toast(online.value ? 'Prueba registrada correctamente' : 'Sin conexión. Prueba guardada localmente.', online.value ? 'success' : 'warning')
        setTimeout(() => volver(), 1000)
      } else {
        const msg = resultadosLote.value[0]?.error || 'Error al guardar'
        ui.toast(msg, 'error')
      }
    } else {
      // Modo lote: mostrar resumen
      const ok = targets.length - errores
      if (errores === 0) {
        ui.toast(`✓ ${ok} prueba(s) registradas en lote`, 'success')
        setTimeout(() => volver(), 1500)
      } else {
        ui.toast(`${ok} guardadas, ${errores} con error. Revise los detalles arriba.`, 'warning')
      }
    }
  }
  </script>

  <style scoped>
  /* Banner de modo lote */
  .lote-banner {
    background: rgba(212, 175, 55, 0.06);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem;
    margin-bottom: 1.25rem;
  }
  .lote-banner-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--color-gold);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    letter-spacing: 0.06em;
    margin-bottom: 0.5rem;
  }
  .lote-ips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  .lote-ip-badge {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    background: rgba(212, 175, 55, 0.12);
    color: var(--color-gold);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 4px;
    padding: 2px 8px;
  }

  /* Resultados del lote */
  .lote-resultados {
    margin-bottom: 1rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
  }
  .lote-resultado-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.4rem 0.85rem;
    font-size: 0.82rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .lote-resultado-item:last-child { border-bottom: none; }
  .lote-resultado-item.ok  { color: var(--color-success); }
  .lote-resultado-item.err { color: var(--color-error); }

  .spinner-sm {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  </style>
