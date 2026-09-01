<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">Reconocimientos</h1>
        <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">{{ cipActual }}</p>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <!-- Botón Guardar: disponible mientras no haya certificado generado -->
        <button
          class="btn-primary"
          @click="guardar"
          :disabled="guardando || !analisisPendiente || certificadoGenerado"
        >
          <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
          {{ yaGuardado ? 'Re-Guardar' : 'Guardar' }}
        </button>
        <!-- Botón Generar Certificado: solo cuando ya hay datos guardados y sin certificado -->
        <button
          v-if="yaGuardado && !certificadoGenerado"
          class="btn-cert"
          @click="generarCertificado"
          :disabled="generandoCert"
        >
          <span v-if="generandoCert" class="spinner" style="margin-right:0.4rem"></span>
          Generar Certificado
        </button>
        <!-- Indicador: certificado ya generado -->
        <span v-if="certificadoGenerado" class="badge-cert-ok">
          ✓ Certificado generado
        </span>
      </div>
    </header>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
    </div>

    <div v-else-if="!analisisPendiente" class="estado-tabla" style="color:var(--color-error)">
      No se encontró un análisis de recuperación PENDIENTE para este CIP.<br>
      Verifique que Comercial haya enviado el lote a recuperación.
    </div>

    <!-- Aviso cuando el certificado ya fue generado -->
    <div v-if="certificadoGenerado && !cargando" class="cert-generado-banner">
      El certificado ya fue generado. Los datos son de solo lectura.
    </div>

    <template v-else>

      <!-- DATOS DEL ANÁLISIS -->
      <section class="card">
        <h2 class="card-titulo">DATOS DEL ANÁLISIS</h2>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">CIP:</label>
            <input class="field-input" :value="cipActual" disabled style="color:var(--color-gold);font-family:var(--font-mono)" />
          </div>
          <div class="field">
            <label class="field-label">FECHA ANÁLISIS:</label>
            <input type="date" class="field-input" v-model="fechaAnalisis" :disabled="certificadoGenerado" />
          </div>
          <div class="field" v-if="store.puedeVerIP">
            <label class="field-label">LEY CABEZA:</label>
            <div class="ley-cabeza-display">
              <span class="lc-valor">{{ analisisPendiente.ley_cabeza }}</span>
              <span class="lc-label">oz/TC</span>
            </div>
          </div>
        </div>
      </section>

      <!-- MUESTRAS SÓLIDAS (reconocimiento) -->
      <section class="card">
        <div class="card-header-row">
          <h2 class="card-titulo">MUESTRAS SÓLIDAS</h2>
          <button class="btn-add-muestra" @click="agregarMuestra" type="button">
            + Agregar muestra
          </button>
        </div>

        <div
          v-for="(m, idx) in muestras"
          :key="idx"
          class="muestra-block"
        >
          <div class="muestra-block-header">
            <span class="muestra-label">Muestra {{ idx + 1 }}</span>
            <button
              v-if="muestras.length > 1"
              class="btn-remove-muestra"
              @click="quitarMuestra(idx)"
              type="button"
            >✕</button>
          </div>

          <!-- Inputs crudos -->
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Peso muestra (g)</label>
              <input
                type="number" class="field-input"
                v-model.number="m.peso_g"
                step="0.001" placeholder="0.000"
                @input="recalcMuestra(idx)"
              />
            </div>
            <div class="field">
              <label class="field-label">Au 1 (mg)</label>
              <input
                type="number" class="field-input"
                v-model.number="m.au1_mg"
                step="0.0001" placeholder="0.0000"
                @input="recalcMuestra(idx)"
              />
            </div>
            <div class="field">
              <label class="field-label">Au 2 (mg)</label>
              <input
                type="number" class="field-input"
                v-model.number="m.au2_mg"
                step="0.0001" placeholder="0.0000"
                @input="recalcMuestra(idx)"
              />
            </div>
            <div class="field">
              <label class="field-label">Au + Ag (mg)</label>
              <input
                type="number" class="field-input"
                v-model.number="m.au_ag_mg"
                step="0.0001" placeholder="0.0000"
                @input="recalcMuestra(idx)"
              />
            </div>
          </div>

          <!-- Resultados calculados por muestra -->
          <div class="resultados-muestra" v-if="m._leyAu != null || m._leyAg != null">
            <div class="res-item">
              <span class="res-label">Ley Au</span>
              <span class="res-val gold">{{ fmtD(m._leyAu) }} <small>g/tm</small></span>
              <span class="res-val-alt">{{ fmtD(toOzTc(m._leyAu)) }} <small>oz/TC</small></span>
            </div>
            <div class="res-item">
              <span class="res-label">Ley Ag</span>
              <span class="res-val blue">{{ fmtD(m._leyAg) }} <small>g/tm</small></span>
              <span class="res-val-alt">{{ fmtD(toOzTc(m._leyAg)) }} <small>oz/TC</small></span>
            </div>
          </div>
        </div>

        <p v-if="errMuestras" class="error-msg" style="margin-top:0.5rem">{{ errMuestras }}</p>
      </section>

      <!-- SOLUCIÓN (LÍQUIDO) -->
      <section class="card">
        <h2 class="card-titulo">SOLUCIÓN (LÍQUIDO)</h2>
        <div class="liquido-grid">

          <!-- Au líquido -->
          <div class="liquido-field">
            <div class="liquido-label">Au en Solución</div>
            <div class="liquido-input-row">
              <div class="field" style="flex:1">
                <label class="field-label">g/m³</label>
                <input
                  type="number" class="field-input"
                  v-model.number="solucionAu"
                  step="0.0001" placeholder="0.0000"
                />
              </div>
              <div class="liquido-conv">
                <span class="liquido-conv-label">≡ oz/TC</span>
                <span class="liquido-conv-val blue">
                  {{ solucionAu != null ? (solucionAu / OZ_TC_TO_GR_TM).toFixed(4) : '—' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Ag en solución -->
          <div class="liquido-field">
            <div class="liquido-label">Ag EN SOLUCIÓN</div>
            <div class="liquido-input-row">
              <div class="field" style="flex:1">
                <label class="field-label">g/m³</label>
                <input
                  type="number" class="field-input"
                  v-model.number="solucionAg"
                  step="0.0001" placeholder="0.0000"
                />
              </div>
              <div class="liquido-conv">
                <span class="liquido-conv-label">≡ oz/TC</span>
                <span class="liquido-conv-val blue">
                  {{ solucionAg != null ? (solucionAg / OZ_TC_TO_GR_TM).toFixed(4) : '—' }}
                </span>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- RESUMEN: solo Comercial/Gerencia/Admin -->
      <section class="card card--resultados" v-if="store.puedeVerIP && resumen.leyColaAuOzTc != null">
        <h2 class="card-titulo">RESULTADOS</h2>
        <div class="resumen-grid">
          <div class="res-item">
            <span class="res-label">Ley cola Au promedio</span>
            <span class="res-val gold">{{ fmtD(resumen.leyColaAuGrTm) }} <small>g/tm</small></span>
            <span class="res-val-alt">{{ fmtD(resumen.leyColaAuOzTc) }} <small>oz/TC</small></span>
          </div>
          <div class="res-item">
            <span class="res-label">Ley cola Ag promedio</span>
            <span class="res-val blue">{{ fmtD(resumen.leyColaAgGrTm) }} <small>g/tm</small></span>
            <span class="res-val-alt">{{ fmtD(resumen.leyColaAgOzTc) }} <small>oz/TC</small></span>
          </div>
          <div class="res-item">
            <span class="res-label">% Recuperación Au</span>
            <span class="res-val highlight" style="margin-top: 0.2rem;">
              {{ resumen.recuperacion != null ? resumen.recuperacion.toFixed(2) + '%' : '—' }}
            </span>
          </div>
        </div>
      </section>

      <p v-if="errForm" class="error-msg" style="margin-top:.75rem">{{ errForm }}</p>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import type { AnalisisRecuperacionOut } from '@/types/laboratorio'

const router  = useRouter()
const route   = useRoute()
const store   = useLaboratorioStore()
const ui      = useUiStore()
import axiosApi from '@/api/axios'

const cipActual      = route.params.cip as string
const analisisIdParam = route.query.id ? Number(route.query.id) : null

const cargando = ref(true)
const guardando = ref(false)
const generandoCert = ref(false)
const errForm = ref('')
const errMuestras = ref('')

const yaGuardado = ref(false)
const certificadoGenerado = ref(false)
const analisisCompletadoId = ref<number | null>(null)

const analisisPendiente = ref<AnalisisRecuperacionOut | null>(null)
const fechaAnalisis = ref(new Date().toISOString().split('T')[0])
const solucionAu  = ref<number | null>(null)
const solucionAg    = ref<number | null>(null)

// ── Constante del lab ─────────────────────────────────────────────────────────
const OZ_TC_TO_GR_TM = 34.2857

// ── Muestras ──────────────────────────────────────────────────────────────────
interface MuestraForm {
  peso_g:    number | null
  au1_mg:    number | null
  au2_mg:    number | null
  au_ag_mg:  number | null
  numero_ensayo: number
  _leyAu:  number | null
  _leyAg:  number | null
}

function toOzTc(grTm: number | null): number | null {
  if (grTm == null) return null
  return parseFloat((grTm / OZ_TC_TO_GR_TM).toFixed(4))
}

function muestraVacia(): MuestraForm {
  return { peso_g: null, au1_mg: null, au2_mg: null, au_ag_mg: 0, numero_ensayo: 1, _leyAu: null, _leyAg: null }
}

const muestras = ref<MuestraForm[]>([muestraVacia()])

function agregarMuestra() {
  muestras.value.push(muestraVacia())
}

function quitarMuestra(idx: number) {
  muestras.value.splice(idx, 1)
}

function calcLeyGrTm(mg: number | null, pesoG: number | null): number | null {
  if (mg == null || pesoG == null || pesoG <= 0) return null
  return parseFloat((mg / pesoG * 1000).toFixed(4))
}

function recalcMuestra(idx: number) {
  errMuestras.value = ''
  const m = muestras.value[idx]
  if (!m) return

  const au1 = calcLeyGrTm(m.au1_mg, m.peso_g)
  const au2 = calcLeyGrTm(m.au2_mg, m.peso_g)
  m._leyAu = (au1 != null && au2 != null) ? parseFloat(((au1 + au2) / 2).toFixed(4)) : null

  if (m.au_ag_mg != null && m.au2_mg != null && m.peso_g != null && m.peso_g > 0) {
    const agMg = Math.max(0, m.au_ag_mg - m.au2_mg - 0.001)
    m._leyAg = parseFloat((agMg / m.peso_g * 1000).toFixed(4))
  } else {
    m._leyAg = null
  }
}

// ── Resumen calculado ─────────────────────────────────────────────────────────
const resumen = computed(() => {
  const leyesAu = muestras.value.map(m => m._leyAu).filter(v => v != null) as number[]
  const leyesAg = muestras.value.map(m => m._leyAg).filter(v => v != null) as number[]

  if (!leyesAu.length) {
    return {
      leyColaAuOzTc: null, leyColaAuGrTm: null,
      leyColaAgGrTm: null, leyColaAgOzTc: null,
      recuperacion: null
    }
  }

  const avgAuGrTm = leyesAu.reduce((a, b) => a + b, 0) / leyesAu.length
  const leyColaAuGrTm = parseFloat(avgAuGrTm.toFixed(4))
  const leyColaAuOzTc = parseFloat((avgAuGrTm / OZ_TC_TO_GR_TM).toFixed(4))

  const avgAgGrTm = leyesAg.length ? leyesAg.reduce((a, b) => a + b, 0) / leyesAg.length : 0
  const leyColaAgGrTm = leyesAg.length ? parseFloat(avgAgGrTm.toFixed(4)) : null
  const leyColaAgOzTc = leyesAg.length ? parseFloat((avgAgGrTm / OZ_TC_TO_GR_TM).toFixed(4)) : null

  const cabeza = analisisPendiente.value ? Number(analisisPendiente.value.ley_cabeza) : null
  const recuperacion = (cabeza && cabeza > 0)
    ? parseFloat(((cabeza - leyColaAuOzTc) / cabeza * 100).toFixed(2))
    : null

  return { leyColaAuOzTc, leyColaAuGrTm, leyColaAgGrTm, leyColaAgOzTc, recuperacion }
})

function fmtD(v: number | null) {
  if (v == null) return '—'
  return v.toFixed(4)
}

// ── Ciclo de vida ─────────────────────────────────────────────────────────────
onMounted(async () => {
  cargando.value = true
  try {
    if (!store.cips.length) await store.cargarCips()
    const cipObj = store.cips.find(c => c.cip === cipActual)
    if (cipObj) {
      const pending = analisisIdParam
        ? cipObj.analisis_recuperacion.find(a => a.id === analisisIdParam && a.estado === 'PENDIENTE' && a.vigente)
        : cipObj.analisis_recuperacion.find(a => a.estado === 'PENDIENTE' && a.vigente)
      
      const completado = cipObj.analisis_recuperacion.find(a => a.estado === 'COMPLETADO' && a.vigente)

      if (completado) {
        yaGuardado.value = true
        analisisCompletadoId.value = completado.id
        certificadoGenerado.value = route.query.edit === '1' ? false : !!completado.certificado_url
        if (!pending) analisisPendiente.value = completado
        if (completado.fecha_analisis) fechaAnalisis.value = completado.fecha_analisis
        if (completado.ley_liquido != null) solucionAu.value = parseFloat((completado.ley_liquido * OZ_TC_TO_GR_TM).toFixed(4))
        if (completado.solucion_ag_g_m3 != null) solucionAg.value = parseFloat(String(completado.solucion_ag_g_m3))

        // Cargar muestras del backend para que el usuario pueda verlas/editarlas
        try {
          const res = await axiosApi.get(`/laboratorio/recuperacion/${completado.id}`)
          if (res.data && res.data.detalles && res.data.detalles.length) {
            const agrupado = new Map<number, any>()
            for (const d of res.data.detalles) {
              const num = d.numero_ensayo || 1
              if (!agrupado.has(num)) {
                agrupado.set(num, {
                  peso_g: parseFloat(d.peso || d.peso_g || 0),
                  au1_mg: null,
                  au2_mg: null,
                  au_ag_mg: 0,
                  numero_ensayo: num,
                  _leyAu: null,
                  _leyAg: null
                })
              }
              const obj = agrupado.get(num)
              const val = d.mineral_mg != null ? parseFloat(d.mineral_mg) : null
              if (d.origen === 'AU1') obj.au1_mg = val
              else if (d.origen === 'AU2') obj.au2_mg = val
              else if (d.origen === 'AU_AG') obj.au_ag_mg = val
            }
            muestras.value = Array.from(agrupado.values())
            muestras.value.forEach((_, i) => recalcMuestra(i))
          }
        } catch (e) {
          console.warn('No se pudieron cargar los detalles del análisis', e)
        }
      }
      
      if (pending) analisisPendiente.value = pending
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
  if (!analisisPendiente.value) { errForm.value = 'Sin análisis pendiente'; return }

  const muestrasInvalidas = muestras.value.filter(
    m => !m.peso_g || m.au1_mg == null || m.au2_mg == null || m.au_ag_mg == null
  )
  if (muestrasInvalidas.length) {
    errMuestras.value = 'Complete todos los campos de cada muestra (peso, Au1, Au2, Au+Ag)'
    return
  }

  if (resumen.value.leyColaAuOzTc == null) {
    errForm.value = 'No se pudo calcular la ley cola. Revise las muestras.'
    return
  }

  guardando.value = true
  let result;
  
  if (route.query.edit === '1' && analisisCompletadoId.value) {
    const payload = {
      ley_cola: resumen.value.leyColaAuOzTc,
      ley_liquido: solucionAu.value != null ? parseFloat((solucionAu.value / OZ_TC_TO_GR_TM).toFixed(4)) : null,
      solucion_ag_g_m3: solucionAg.value,
      fecha_analisis: fechaAnalisis.value,
      muestras: muestras.value.map(m => ({
        peso_g:        m.peso_g,
        au1_mg:        m.au1_mg,
        au2_mg:        m.au2_mg,
        au_ag_mg:      m.au_ag_mg,
        numero_ensayo: m.numero_ensayo,
      })),
      ley_cola_ag: resumen.value.leyColaAgGrTm,
    }
    result = await store.editarRecuperacion(analisisCompletadoId.value, payload)
  } else {
    const payload = {
      muestras: muestras.value.map(m => ({
        peso_g:        m.peso_g,
        au1_mg:        m.au1_mg,
        au2_mg:        m.au2_mg,
        au_ag_mg:      m.au_ag_mg,
        numero_ensayo: m.numero_ensayo,
      })),
      ley_cola: resumen.value.leyColaAuOzTc,
      ley_liquido:     solucionAu.value != null ? parseFloat((solucionAu.value / OZ_TC_TO_GR_TM).toFixed(4)) : null,
      solucion_ag_g_m3: solucionAg.value,
      fecha_analisis:  fechaAnalisis.value,
    }
    result = await store.completarRecuperacion(analisisPendiente.value.id, payload)
  }

  if (result) {
    yaGuardado.value = true
    analisisCompletadoId.value = result.id
    certificadoGenerado.value = !!result.certificado_url
    ui.toast('Datos guardados exitosamente.', 'success')
  }
  guardando.value = false
}

// ── Generar Certificado ───────────────────────────────────────────────────────
async function generarCertificado() {
  if (!analisisCompletadoId.value) return
  const ok = await ui.showConfirm({
    title: 'Generar Certificado',
    message: 'Al generar el certificado los datos quedarán bloqueados y no podrán ser editados. ¿Desea continuar?',
    confirmLabel: 'Generar',
  })
  if (!ok) return

  generandoCert.value = true
  const result = await store.generarCertificadoRecInterno(analisisCompletadoId.value)
  if (result) {
    certificadoGenerado.value = true
    ui.toast('Certificado generado exitosamente', 'success')
    setTimeout(() => { router.push('/laboratorio') }, 1500)
  }
  generandoCert.value = false
}
</script>

<style scoped>
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-add-muestra {
  font-size: var(--text-sm);
  padding: 0.35rem 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-accent);
  color: var(--color-accent);
  background: transparent;
  cursor: pointer;
}
.btn-add-muestra:hover:not(:disabled) { background: rgba(var(--color-accent-rgb), 0.08); }
.btn-add-muestra:disabled { opacity: 0.5; cursor: not-allowed; }

.muestra-block {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.9rem 1rem;
  margin-bottom: 0.75rem;
  background: rgba(255,255,255,0.02);
}

.muestra-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.muestra-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-faint);
}

.btn-remove-muestra {
  font-size: 0.65rem;
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  border: 1px solid var(--color-error-border, rgba(239,68,68,0.3));
  color: var(--color-error, #ef4444);
  background: transparent;
  cursor: pointer;
  opacity: 0.7;
}
.btn-remove-muestra:hover { opacity: 1; }

.resultados-muestra {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.6rem;
  padding: 0.5rem 0.75rem;
  background: rgba(184,151,75,0.04);
  border: 1px solid rgba(184,151,75,0.15);
  border-radius: 4px;
}

.resumen-grid {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.res-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.res-label {
  font-size: 0.65rem;
  font-family: var(--font-mono);
  color: var(--color-text-faint);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.res-val {
  font-family: var(--font-mono);
  font-size: var(--text-md);
  color: var(--color-text-muted);
}
.res-val.gold { color: var(--color-gold); font-weight: 600; }
.res-val.blue { color: #60a5fa; font-weight: 600; }
.res-val.highlight { color: var(--color-gold); font-size: var(--text-xl); font-weight: 700; }

.card--resultados {
  border-color: rgba(184,151,75,0.25);
  background: rgba(184,151,75,0.03);
}

.liquido-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
@media (max-width: 600px) {
  .liquido-grid { grid-template-columns: 1fr; }
}
.liquido-field {
  display: flex; flex-direction: column; gap: 0.5rem;
}
.liquido-label {
  font-size: 0.65rem; font-family: var(--font-mono);
  color: var(--color-text-faint); text-transform: uppercase; letter-spacing: 0.08em;
}
.liquido-input-row {
  display: flex; align-items: flex-end; gap: 0.75rem;
}
.liquido-conv {
  display: flex; flex-direction: column; align-items: center; gap: 0.15rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255,255,255,0.03); border: 1px solid var(--color-border);
  border-radius: 6px; min-width: 90px;
}
.liquido-conv-label {
  font-size: 0.6rem; font-family: var(--font-mono);
  color: var(--color-text-faint); letter-spacing: 0.06em;
}
.liquido-conv-val {
  font-family: var(--font-mono); font-size: var(--text-md); font-weight: 600;
}
.liquido-conv-val.gold { color: var(--color-gold); }
.liquido-conv-val.blue { color: #60a5fa; }

.ley-cabeza-display {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(184,151,75,.08);
  border: 1px solid rgba(184,151,75,.25);
  border-radius: 4px;
}
.lc-valor {
  font-family: var(--font-mono);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-gold);
}
.lc-label {
  font-size: .7rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
}

.btn-cert {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #4ade80;
  border-radius: var(--radius-md);
  padding: 0.4rem 0.9rem;
  font-family: var(--font-main);
  font-weight: 700;
  font-size: 0.83rem;
  cursor: pointer;
}
.btn-cert:disabled { opacity: 0.5; cursor: not-allowed; }

.cert-generado-banner {
  background: rgba(34, 197, 94, 0.06);
  border: 1px solid rgba(34, 197, 94, 0.25);
  border-radius: var(--radius-md);
  color: #4ade80;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.6rem 1rem;
  margin-top: 1rem;
}
</style>
