<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Reconocimiento — Solución AA</h1>
        <div style="display:flex;align-items:center;gap:0.6rem;margin-top:0.2rem">
          <span class="badge-subtipo solucion">SOLUCIÓN</span>
          <span class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">{{ cipActual }}</span>
        </div>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <button
          class="btn-primary"
          @click="guardar"
          :disabled="guardando || !analisisPendiente || certificadoGenerado"
        >
          <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
          Guardar cambios
        </button>
        <button
          v-if="!certificadoGenerado"
          class="btn-primary"
          @click="generarCertificado"
          :disabled="generandoCert || !yaGuardado"
        >
          <span v-if="generandoCert" class="spinner" style="margin-right:0.4rem"></span>
          Guardar certificado
        </button>
        <span v-if="certificadoGenerado" class="badge-cert-ok">✓ Certificado Solución generado</span>
      </div>
    </header>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
    </div>

    <div v-else-if="!analisisPendiente && !modoNuevo" class="estado-tabla" style="color:var(--color-error)">
      No se encontró un análisis de Solución PENDIENTE para este CIP.<br>
      Verifique que Comercial haya enviado el lote indicando el tipo SOLUCIÓN.
    </div>

    <div v-if="certificadoGenerado && !cargando" class="cert-generado-banner">
      El certificado de solución ya fue generado. Los datos son de solo lectura.
    </div>

    <template v-if="(analisisPendiente || modoNuevo) && !cargando">

      <!-- DATOS DEL ANÁLISIS -->
      <section class="card">
        <h2 class="card-titulo">DATOS DEL ANÁLISIS</h2>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">CIP:</label>
            <input class="field-input" v-model="formCip" :disabled="!modoNuevo" style="color:var(--color-gold);font-family:var(--font-mono)" placeholder="Ingrese código..." />
          </div>
          <div class="field" v-if="modoNuevo">
            <label class="field-label">DESCRIPCIÓN:</label>
            <select v-model="descripcionPDF" class="field-select field-input field-sm">
              <option value="PROCESO">PROCESO</option>
              <option value="LAB. METALÚRGICO">LAB. METALÚRGICO</option>
              <option value="RECONOCIMIENTO">RECONOCIMIENTO</option>
              <option value="LOTE">LOTE</option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">FECHA ANÁLISIS:</label>
            <input type="date" class="field-input" v-model="fechaAnalisis" :disabled="certificadoGenerado" />
          </div>
        </div>
      </section>

      <!-- LEYES EN SOLUCIÓN (Absorción Atómica) -->
      <section class="card">
        <h2 class="card-titulo">LEYES EN SOLUCIÓN — ABSORCIÓN ATÓMICA</h2>
        <div v-if="errForm" class="err-msg">{{ errForm }}</div>

        <div class="liquido-grid">

          <!-- Au en Solución -->
          <div class="liquido-field">
            <div class="liquido-label">Au en Solución (g/m³)</div>
            <div class="field">
              <input
                type="number" class="field-input"
                v-model.number="solucionAu"
                step="0.0001" placeholder="0.0000"
                :disabled="certificadoGenerado"
              />
            </div>
          </div>

          <!-- Ag en Solución -->
          <div class="liquido-field">
            <div class="liquido-label">Ag en Solución (g/m³)</div>
            <div class="field">
              <input
                type="number" class="field-input"
                v-model.number="solucionAg"
                step="0.0001" placeholder="0.0000"
                :disabled="certificadoGenerado"
              />
            </div>
          </div>

        </div>
      </section>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import type { AnalisisRecuperacionOut } from '@/types/laboratorio'

const router = useRouter()
const route = useRoute()
const store = useLaboratorioStore()
const ui = useUiStore()

const cipActual = route.params.cip as string

// ── Constantes ────────────────────────────────────────────────────────────────
const OZ_TC_TO_GR_TM = 34.2857

const modoNuevo = cipActual === '_nuevo'
const formCip = ref(modoNuevo ? '' : cipActual)
const descripcionPDF = ref('PROCESO')

// ── Estado ────────────────────────────────────────────────────────────────────
const cargando = ref(true)
const guardando = ref(false)
const generandoCert = ref(false)
const errForm = ref('')

const yaGuardado = ref(false)
const certificadoGenerado = ref(false)
const analisisCompletadoId = ref<number | null>(null)

const analisisPendiente = ref<AnalisisRecuperacionOut | null>(null)
const fechaAnalisis = ref(new Date().toISOString().split('T')[0])
const laboratorio = ref('Paititi')
const solucionAu = ref<number | null>(null)
const solucionAg = ref<number | null>(null)

// ── Ciclo de vida ─────────────────────────────────────────────────────────────
onMounted(async () => {
  if (modoNuevo) {
    cargando.value = false
    return
  }

  cargando.value = true
  try {
    if (!store.cips.length) await store.cargarCips()
    const cipObj = store.cips.find(c => c.cip === cipActual)
    if (cipObj) {
      // Buscar pendiente de tipo SOLUCION
      const pending = cipObj.analisis_recuperacion.find(
        a => a.estado === 'PENDIENTE' && a.vigente && a.sub_tipo === 'SOLUCION'
      )
      analisisPendiente.value = pending ?? null

      // Buscar COMPLETADO de tipo SOLUCION (datos previos)
      const completado = cipObj.analisis_recuperacion.find(
        a => a.estado === 'COMPLETADO' && a.vigente && a.sub_tipo === 'SOLUCION'
      )
      if (completado) {
        yaGuardado.value = true
        analisisCompletadoId.value = completado.id
        certificadoGenerado.value = route.query.edit === '1' ? false : !!completado.certificado_url
        if (completado.ley_liquido != null)
          solucionAu.value = parseFloat(Number(completado.ley_liquido).toFixed(4))
        if (completado.solucion_ag_g_m3 != null)
          solucionAg.value = parseFloat(String(completado.solucion_ag_g_m3))
        if (completado.fecha_analisis) fechaAnalisis.value = completado.fecha_analisis
        if (!analisisPendiente.value) analisisPendiente.value = completado
      }
    }
  } catch {
    ui.toast('Error al cargar datos', 'error')
  } finally {
    cargando.value = false
  }
})

// ── Guardar ───────────────────────────────────────────────────────────────────
async function guardar() {
  errForm.value = ''
  if (!modoNuevo && !analisisPendiente.value) { errForm.value = 'Sin análisis pendiente'; return }
  if (modoNuevo && !formCip.value) { errForm.value = 'Ingrese el código de la muestra'; return }
  if (solucionAu.value == null && solucionAg.value == null) {
    errForm.value = 'Ingrese al menos la ley de Au o Ag en solución'; return
  }

  guardando.value = true

  if (modoNuevo) {
    const payload = {
      cip: formCip.value,
      laboratorio: laboratorio.value,
      ley_cabeza: null,
      ley_cola: null, // Solución no tiene ley_cola, solo ley_liquido
      ley_liquido: solucionAu.value,  // g/m³ — se guarda directamente
      solucion_ag_g_m3: solucionAg.value,
      fecha_analisis: fechaAnalisis.value,
      sub_tipo: 'SOLUCION',
    }
    const result = await store.registrarRecuperacion(payload)
    if (result) {
      yaGuardado.value = true
      analisisCompletadoId.value = result.id
      certificadoGenerado.value = !!result.certificado_url
      ui.toast('Datos de solución guardados. Puede guardar el certificado.', 'success')
    }
  } else if (route.query.edit === '1' && analisisCompletadoId.value) {
    const payload = {
      ley_liquido: solucionAu.value,
      solucion_ag_g_m3: solucionAg.value,
      fecha_analisis: fechaAnalisis.value,
    }
    const result = await store.editarRecuperacion(analisisCompletadoId.value, payload)
    if (result) {
      yaGuardado.value = true
      certificadoGenerado.value = !!result.certificado_url
      ui.toast('Datos de solución guardados. Puede generar el certificado.', 'success')
    }
  } else {
    const payload = {
      muestras: null,
      ley_cola: null,
      ley_liquido: solucionAu.value,  // g/m³ — se guarda directamente
      solucion_ag_g_m3: solucionAg.value,
      fecha_analisis: fechaAnalisis.value,
    }

    const result = await store.completarRecuperacion(analisisPendiente.value!.id, payload as any)
    if (result) {
      yaGuardado.value = true
      analisisCompletadoId.value = result.id
      certificadoGenerado.value = !!result.certificado_url
      ui.toast('Datos de solución guardados. Puede generar el certificado.', 'success')
    }
  }

  guardando.value = false
}

// ── Generar Certificado ───────────────────────────────────────────────────────
async function generarCertificado() {
  if (!analisisCompletadoId.value) { ui.toast('Guarde primero los datos.', 'warning'); return }

  const ok = await ui.showConfirm({
    title: 'Generar Certificado de Solución',
    message: 'Al generar el certificado los datos quedarán bloqueados. ¿Continuar?',
    confirmLabel: 'Generar',
  })
  if (!ok) return

  generandoCert.value = true
  const result = await store.generarCertificadoRecInterno(analisisCompletadoId.value, descripcionPDF.value)
  if (result) {
    certificadoGenerado.value = true
    ui.toast('Certificado de solución generado', 'success')
    setTimeout(() => router.push('/laboratorio'), 1500)
  }
  generandoCert.value = false
}
</script>

<style scoped>
.badge-subtipo {
  font-size: 0.68rem; font-weight: 800; letter-spacing: 0.08em;
  padding: 2px 8px; border-radius: 4px; font-family: var(--font-mono);
}
.badge-subtipo.solucion {
  background: rgba(96, 165, 250, 0.15);
  color: #93c5fd;
  border: 1px solid rgba(96, 165, 250, 0.3);
}
.btn-cert {
  background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(34, 197, 94, 0.4); color: #4ade80;
  border-radius: var(--radius-md); padding: 0.4rem 0.9rem;
  font-family: var(--font-main); font-weight: 700; font-size: 0.83rem;
  cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center;
}
.btn-cert:hover:not(:disabled) { background: rgba(34,197,94,0.22); }
.btn-cert:disabled { opacity: 0.5; cursor: not-allowed; }
.badge-cert-ok {
  font-size: 0.78rem; font-weight: 700; color: #4ade80;
  background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3);
  border-radius: var(--radius-sm); padding: 0.3rem 0.7rem;
}
.cert-generado-banner {
  background: rgba(34,197,94,0.06); border: 1px solid rgba(34,197,94,0.25);
  border-radius: var(--radius-md); color: #4ade80;
  font-size: 0.82rem; font-weight: 600; padding: 0.6rem 1rem; margin-bottom: 1rem;
}
.liquido-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1rem; }
.liquido-field { display: flex; flex-direction: column; gap: 0.5rem; }
.liquido-label { font-size: 0.78rem; font-weight: 700; color: var(--color-text-muted); letter-spacing: 0.05em; }
.liquido-input-row { display: flex; align-items: flex-end; gap: 0.75rem; }
.liquido-conv { display: flex; flex-direction: column; align-items: center; padding-bottom: 0.25rem; }
.liquido-conv-label { font-size: 0.68rem; color: var(--color-text-faint); }
.liquido-conv-val { font-family: var(--font-mono); font-size: var(--resultado-fs, 0.9rem); color: #93c5fd; font-weight: 700; }
.err-msg { color: var(--color-error); font-size: 0.82rem; margin-top: 0.5rem; }
</style>
