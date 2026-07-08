<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Reconocimiento — Sólidos</h1>
        <div style="display:flex;align-items:center;gap:0.6rem;margin-top:0.2rem">
          <span class="badge-subtipo solidos">SÓLIDOS</span>
          <span class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">{{ cipActual }}</span>
        </div>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <button
          class="btn-primary"
          @click="guardar"
          :disabled="guardando || (!modoNuevo && !esCreacionDirecta && !analisisPendiente && !analisisCompletadoId)"
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
          {{ isFromAg ? 'Generar Certificado Newmont (Ag)' : 'Guardar certificado' }}
        </button>
        <span v-if="certificadoGenerado && !isFromAg" class="badge-cert-ok">✓ Certificado Sólidos generado</span>
      </div>
    </header>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
    </div>

    <div v-else-if="!analisisPendiente && !modoNuevo && !esCreacionDirecta" class="estado-tabla" style="color:var(--color-error)">
      No se encontró un análisis de sólidos PENDIENTE para este CIP.<br>
      Verifique que Comercial haya enviado el lote indicando el tipo SÓLIDOS.
    </div>

    <div v-if="certificadoGenerado && !cargando" class="cert-generado-banner">
      ✓ Certificado Sólidos generado. Puede agregar Ley de Plata (Au + Ag) a las muestras; esto actualizará el análisis Newmont sin afectar el certificado original.
    </div>

    <template v-if="(analisisPendiente || modoNuevo || esCreacionDirecta) && !cargando">

      <!-- DATOS DEL ANÁLISIS -->
      <section class="card">
        <h2 class="card-titulo">DATOS DEL ANÁLISIS</h2>
        <div class="form-grid">
          <div class="field">
            <label class="field-label">CIP:</label>
            <input class="field-input" v-model="formCip" :disabled="!modoNuevo" style="color:var(--color-gold);font-family:var(--font-mono)" placeholder="Ingrese código..." />
          </div>
          <div class="field" v-if="modoNuevo || esCreacionDirecta">
            <label class="field-label">DESCRIPCIÓN:</label>
            <select v-model="descripcionPDF" class="field-select field-input field-sm" :disabled="certificadoGenerado">
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
          <div class="field" v-if="store.puedeVerIP">
            <label class="field-label">LEY CABEZA:</label>
            <div class="ley-cabeza-display">
              <span class="lc-valor">{{ analisisPendiente.ley_cabeza }}</span>
              <span class="lc-label">oz/TC</span>
            </div>
          </div>
        </div>
      </section>

      <!-- MUESTRAS SÓLIDAS -->
      <section class="card">
        <div class="card-header-row">
          <h2 class="card-titulo">MUESTRAS SÓLIDAS (Fire Assay)</h2>
          <!-- TO DO: Revisar cómo se comporta el análisis al agregar muestra -->
          <!-- <button class="btn-add-muestra" @click="agregarMuestra" :disabled="certificadoGenerado">
            + Agregar Muestra
          </button> -->
        </div>

        <div v-if="errMuestras" class="err-msg">{{ errMuestras }}</div>

        <div class="muestras-cards">
          <div v-for="(m, idx) in muestras" :key="idx" class="muestra-card">
            <h3 class="muestra-card-titulo">
              ENSAYO {{ m.numero_ensayo }}
              <button v-if="muestras.length > 1 && !yaGuardado" class="btn-remove" @click="muestras.splice(idx, 1)">×</button>
            </h3>
            <div class="form-grid">
              <div class="field">
                <label class="field-label">Peso (g)</label>
                <input type="number" class="field-input" v-model.number="m.peso_g" step="0.001" placeholder="0.000" @input="recalcMuestra(idx)" />
              </div>
              <div class="field">
                <label class="field-label">Au 1 (mg)</label>
                <input type="number" class="field-input" v-model.number="m.au1_mg" step="0.0001" placeholder="0.0000" @input="recalcMuestra(idx)" />
              </div>
              <div class="field">
                <label class="field-label">Au 2 (mg)</label>
                <input type="number" class="field-input" v-model.number="m.au2_mg" step="0.0001" placeholder="0.0000" @input="recalcMuestra(idx)" />
              </div>
              <div class="field">
                <label class="field-label">Au + Ag (mg)</label>
                <input type="number" class="field-input" v-model.number="m.au_ag_mg" step="0.0001" placeholder="0.0000" @input="recalcMuestra(idx)" />
              </div>
            </div>

            <!-- Resultados calculados por muestra -->
            <div class="resultados-muestra" v-if="m._calc && (m._calc.avg_gr_tm != null || m._calc.ag_gr_tm != null)">
              <div class="res-item">
                <span class="res-label">Ley Au</span>
                <span class="res-val gold">{{ m._calc.avg_gr_tm?.toFixed(4) ?? '—' }} <small>g/tm</small></span>
                <span class="res-val-alt">{{ (m._calc.avg_gr_tm != null ? (m._calc.avg_gr_tm / 34.2857).toFixed(4) : '—') }} <small>oz/TC</small></span>
              </div>
              <div class="res-item">
                <span class="res-label">Ley Ag</span>
                <span class="res-val blue">{{ m._calc.ag_gr_tm?.toFixed(4) ?? '—' }} <small>g/tm</small></span>
                <span class="res-val-alt">{{ (m._calc.ag_gr_tm != null ? (m._calc.ag_gr_tm / 34.2857).toFixed(4) : '—') }} <small>oz/TC</small></span>
              </div>
            </div>
          </div>
        </div>

        <!-- RESUMEN SÓLIDOS -->
        <div v-if="resumen.leyColaAuOzTc != null" class="resumen-grid" style="margin-top: 1rem">
          <div class="res-item">
            <span class="res-label">Ley Au</span>
            <span class="res-val gold">{{ resumen.leyColaAuGrTm?.toFixed(4) ?? '—' }} <small>g/tm</small></span>
            <span class="res-val-alt">{{ resumen.leyColaAuOzTc?.toFixed(4) ?? '—' }} <small>oz/TC</small></span>
          </div>
          <div class="res-item" v-if="resumen.leyColaAgGrTm">
            <span class="res-label">Ley Ag</span>
            <span class="res-val blue">{{ resumen.leyColaAgGrTm?.toFixed(4) ?? '—' }} <small>g/tm</small></span>
            <span class="res-val-alt">{{ resumen.leyColaAgOzTc?.toFixed(4) ?? '—' }} <small>oz/TC</small></span>
          </div>
        </div>

        <div v-if="errForm" class="err-msg">{{ errForm }}</div>
      </section>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import type { AnalisisRecuperacionOut } from '@/types/laboratorio'
import { laboratorioApi } from '@/api/laboratorio'

const router = useRouter()
const route = useRoute()
const store = useLaboratorioStore()
const ui = useUiStore()
const api = laboratorioApi

const cipActual = route.params.cip as string
const analisisIdParam = route.query.id ? Number(route.query.id) : null

const modoNuevo = cipActual === '_nuevo'
const esCreacionDirecta = route.query.peso != null || route.query.direct === '1'
const isFromAg = route.query.fromAg === '1'
const formCip = ref(modoNuevo ? '' : cipActual)
const descripcionPDF = ref('LOTE')

// ── Estado ────────────────────────────────────────────────────────────────────
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

// ── Constantes ────────────────────────────────────────────────────────────────
const FACTOR = 34.2857  // oz/TC → g/TM

// ── Muestras ──────────────────────────────────────────────────────────────────
interface Muestra {
  peso_g: number | null; au1_mg: number | null; au2_mg: number | null; au_ag_mg: number | null
  numero_ensayo: number
  _calc: { au1_gr_tm: number | null; au2_gr_tm: number | null; avg_gr_tm: number | null; ag_gr_tm: number | null } | null
}

function nuevaMuestra(): Muestra {
  return { peso_g: null, au1_mg: null, au2_mg: null, au_ag_mg: null, numero_ensayo: 1, _calc: null }
}

const muestras = ref<Muestra[]>([nuevaMuestra()])

function recalcMuestra(idx: number) {
  const m = muestras.value[idx]
  if (!m.peso_g) { m._calc = null; recalcResumen(); return }
  const peso = m.peso_g
  const au1GrTm = m.au1_mg != null ? (m.au1_mg / peso) * 1000 : null
  const au2GrTm = m.au2_mg != null ? (m.au2_mg / peso) * 1000 : null
  const avgGrTm = (au1GrTm != null && au2GrTm != null) ? (au1GrTm + au2GrTm) / 2 : null
  const agMg = m.au_ag_mg != null && m.au2_mg != null
    ? Math.max(0, m.au_ag_mg - m.au2_mg - 0.001) : null
  const agGrTm = agMg != null && agMg > 0 ? (agMg / peso) * 1000 : 0
  m._calc = { au1_gr_tm: au1GrTm, au2_gr_tm: au2GrTm, avg_gr_tm: avgGrTm, ag_gr_tm: agGrTm }
  recalcResumen()
}

const resumen = computed(() => {
  const avgs = muestras.value.filter(m => m._calc?.avg_gr_tm != null).map(m => m._calc!.avg_gr_tm!)
  const ags  = muestras.value.filter(m => m._calc?.ag_gr_tm != null).map(m => m._calc!.ag_gr_tm!)
  
  if (!avgs.length) {
    if (analisisPendiente.value && yaGuardado.value) {
      const leyCola = Number(analisisPendiente.value.ley_cola)
      const cabeza = Number(analisisPendiente.value.ley_cabeza)
      const recuperacion = (cabeza && cabeza > 0 && leyCola != null) ? ((cabeza - leyCola) / cabeza * 100) : null
      const leyColaAg = analisisPendiente.value.ley_cola_ag ?? null
      
      return { 
        leyColaAuGrTm: leyCola * FACTOR, 
        leyColaAuOzTc: leyCola, 
        leyColaAgGrTm: leyColaAg != null ? Number(leyColaAg) * FACTOR : null, 
        leyColaAgOzTc: leyColaAg != null ? Number(leyColaAg) : null,
        recuperacion 
      }
    }
    return { leyColaAuGrTm: null, leyColaAuOzTc: null, leyColaAgGrTm: null, leyColaAgOzTc: null, recuperacion: null }
  }
  
  const avgGrTm = avgs.reduce((a, b) => a + b, 0) / avgs.length
  const ozTc = avgGrTm / FACTOR
  const agGrTm = ags.length ? ags.reduce((a, b) => a + b, 0) / ags.length : null
  
  const cabeza = analisisPendiente.value ? Number(analisisPendiente.value.ley_cabeza) : null
  const recuperacion = (cabeza && cabeza > 0) ? ((cabeza - ozTc) / cabeza * 100) : null
  
  return { leyColaAuGrTm: avgGrTm, leyColaAuOzTc: ozTc, leyColaAgGrTm: agGrTm, leyColaAgOzTc: agGrTm != null ? agGrTm / FACTOR : null, recuperacion }
})

function recalcResumen() { /* trigger reactivity */ }
function agregarMuestra() { muestras.value.push(nuevaMuestra()) }

// ── Ciclo de vida ─────────────────────────────────────────────────────────────
onMounted(async () => {
  if (modoNuevo || esCreacionDirecta) {
    if (route.query.peso || route.query.au1 || route.query.au2) {
      muestras.value[0].peso_g = route.query.peso ? Number(route.query.peso) : null
      muestras.value[0].au1_mg = route.query.au1 ? Number(route.query.au1) : null
      muestras.value[0].au2_mg = route.query.au2 ? Number(route.query.au2) : null
      recalcMuestra(0)
    }
    cargando.value = false
    if (modoNuevo) return
  }

  if (esCreacionDirecta && cipActual !== '_nuevo') {
    // Aún en creación directa (desde Newmont), intentamos cargar CIP para validar si existe
    try {
      if (!store.cips.length) await store.cargarCips()
    } catch (e) {
      // Ignorar si falla la carga del CIP
    }
    return
  }

  cargando.value = true
  try {
    if (!store.cips.length) await store.cargarCips()
    const cipObj = store.cips.find(c => c.cip === cipActual)
    if (cipObj) {
      // Buscar el pendiente de tipo SOLIDOS
      const pending = cipObj.analisis_recuperacion.find(
        a => a.estado === 'PENDIENTE' && a.vigente && a.sub_tipo === 'SOLIDOS'
      ) ?? cipObj.analisis_recuperacion.find(
        a => a.estado === 'PENDIENTE' && a.vigente && !a.sub_tipo  // legacy
      )
      analisisPendiente.value = pending ?? null

      // Detectar si ya existe COMPLETADO de tipo SOLIDOS
      const completado = cipObj.analisis_recuperacion.find(
        a => a.estado === 'COMPLETADO' && a.vigente &&
             (a.sub_tipo === 'SOLIDOS' || !a.sub_tipo)
      )
      if (completado) {
        yaGuardado.value = true
        analisisCompletadoId.value = completado.id
        certificadoGenerado.value = !!completado.certificado_url
        if (!analisisPendiente.value) analisisPendiente.value = completado

        // Cargar muestras del backend para que el usuario pueda verlas/editarlas
        try {
          const res = await api.get(`/laboratorio/recuperacion/${completado.id}`)
          if (res.data && res.data.detalles && res.data.detalles.length) {
            muestras.value = res.data.detalles.map((d: any) => ({
              peso_g: d.peso_g,
              au1_mg: d.au1_mg,
              au2_mg: d.au2_mg,
              au_ag_mg: d.au_ag_mg,
              numero_ensayo: d.numero_ensayo || 1,
              _calc: null
            }))
            muestras.value.forEach((_, i) => recalcMuestra(i))
          }
        } catch (e) {
          console.warn('No se pudieron cargar los detalles del análisis', e)
        }
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
  errForm.value = ''; errMuestras.value = ''
  if (!modoNuevo && !esCreacionDirecta && !analisisPendiente.value && !analisisCompletadoId.value) { 
    errForm.value = 'Sin análisis pendiente ni completado'
    return 
  }
  if ((modoNuevo || esCreacionDirecta) && !formCip.value) { errForm.value = 'Ingrese el código de la muestra'; return }

  const invalidas = muestras.value.filter(m => !m.peso_g || m.au1_mg == null || m.au2_mg == null || m.au_ag_mg == null)
  if (invalidas.length) { errMuestras.value = 'Complete todos los campos de cada muestra'; return }
  if (resumen.value.leyColaAuOzTc == null) { errForm.value = 'No se pudo calcular la ley cola'; return }

  guardando.value = true

  const esActualizacionDirecta = esCreacionDirecta && yaGuardado.value

  if ((modoNuevo || esCreacionDirecta) && !esActualizacionDirecta) {
    // Registro directo
    const payload = {
      cip: formCip.value,
      laboratorio: 'Paititi',
      ley_cabeza: null,
      ley_cola: resumen.value.leyColaAuOzTc,
      ley_liquido: null,
      solucion_ag_g_m3: null,
      fecha_analisis: fechaAnalisis.value,
      sub_tipo: 'SOLIDOS',
      ley_cola_ag: resumen.value.leyColaAgGrTm,
      muestras: muestras.value.map(m => ({
        peso_g: m.peso_g, au1_mg: m.au1_mg, au2_mg: m.au2_mg,
        au_ag_mg: m.au_ag_mg, numero_ensayo: m.numero_ensayo,
      }))
    }
    const result = await store.registrarRecuperacion(payload)
    if (result && typeof result === 'object' && 'id' in result) {
      yaGuardado.value = true
      analisisCompletadoId.value = result.id
      certificadoGenerado.value = !!result.certificado_url
      ui.toast('Datos guardados. Puede guardar el certificado.', 'success')
    } else if (result) {
      ui.toast('Datos guardados.', 'success')
    }
  } else {
    // Completar PENDIENTE o Actualizar COMPLETADO
    const payload = {
      muestras: muestras.value.map(m => ({
        peso_g: m.peso_g, au1_mg: m.au1_mg, au2_mg: m.au2_mg,
        au_ag_mg: m.au_ag_mg, numero_ensayo: m.numero_ensayo,
      })),
      ley_cola: resumen.value.leyColaAuOzTc,
      ley_liquido: null,
      solucion_ag_g_m3: null,
      fecha_analisis: fechaAnalisis.value,
      ley_cola_ag: resumen.value.leyColaAgGrTm,
    }

    const idACompletar = analisisPendiente.value?.id || analisisCompletadoId.value
    if (!idACompletar) { ui.toast('No se encontró el ID para actualizar', 'error'); guardando.value = false; return }

    const result = await store.completarRecuperacion(idACompletar, payload)
    if (result) {
      yaGuardado.value = true
      analisisCompletadoId.value = result.id
      certificadoGenerado.value = !!result.certificado_url
      ui.toast('Datos de sólidos guardados exitosamente.', 'success')
    }
  }

  guardando.value = false
}

// ── Generar Certificado ───────────────────────────────────────────────────────
async function generarCertificado() {
  if (!yaGuardado.value) { ui.toast('Guarde primero los datos.', 'warning'); return }

  if (isFromAg) {
    const ok = await ui.showConfirm({
      title: 'Regenerar Certificado Newmont',
      message: '¿Generar el certificado Newmont incluyendo la nueva Ley de Plata?',
      confirmLabel: 'Generar',
    })
    if (!ok) return

    generandoCert.value = true
    try {
      if (!store.cips.length) await store.cargarCips()
      const cipObj = store.cips.find(c => c.cip === formCip.value)
      const analisisLey = cipObj?.analisis_ley.find(a => a.material === 'Au' && a.estado === 'COMPLETADO' && a.vigente)
      
      if (analisisLey) {
        const result = await store.generarCertificadoLeyInterno(analisisLey.id)
        if (result) {
          ui.toast('Certificado Newmont actualizado exitosamente.', 'success')
          setTimeout(() => {
            window.close() // Close the current tab and return to dashboard
            router.push('/laboratorio')
          }, 1000)
        }
      } else {
        ui.toast('No se encontró el análisis de Newmont original para regenerarlo.', 'error')
      }
    } finally {
      generandoCert.value = false
    }
    return
  }

  if (!analisisCompletadoId.value) return

  const ok = await ui.showConfirm({
    title: 'Generar Certificado de Sólidos',
    message: 'Al generar el certificado los datos quedarán bloqueados. ¿Continuar?',
    confirmLabel: 'Generar',
  })
  if (!ok) return

  generandoCert.value = true
  const result = await store.generarCertificadoRecInterno(analisisCompletadoId.value, descripcionPDF.value)
  if (result) {
    certificadoGenerado.value = true
    ui.toast('Certificado de sólidos generado.', 'success')
    setTimeout(() => {
      router.push('/laboratorio')
    }, 1500)
  }
  generandoCert.value = false
}
</script>

<style scoped>
.badge-subtipo {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: var(--font-mono);
}
.badge-subtipo.solidos {
  background: rgba(212, 175, 55, 0.15);
  color: var(--color-gold);
  border: 1px solid rgba(212, 175, 55, 0.35);
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
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
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

.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.btn-add-muestra { font-size: var(--text-sm); padding: 0.35rem 0.85rem; border-radius: var(--radius-md); border: 1px solid var(--color-border-accent); color: var(--color-accent); background: transparent; cursor: pointer; }
.muestra-bloque { border: 1px solid rgba(212,175,55,0.15); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1rem; }
.muestra-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
.muestra-num { font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-gold); font-weight: 700; }
.btn-remove-muestra { background: transparent; border: 1px solid rgba(239,68,68,0.3); color: #f87171; border-radius: 4px; padding: 2px 8px; cursor: pointer; }
.resultados-muestra { display: flex; gap: 1.5rem; margin-top: 0.6rem; padding: 0.5rem 0.75rem; background: rgba(184,151,75,0.04); border: 1px solid rgba(184,151,75,0.15); border-radius: 4px; }
.resumen-grid { display: flex; flex-wrap: wrap; gap: 2rem; margin-top: 1.25rem; border-top: 1px solid var(--color-border); padding-top: 1rem; }
.res-item { display: flex; flex-direction: column; gap: 0.2rem; }
.res-label { font-size: 0.65rem; font-family: var(--font-mono); color: var(--color-text-faint); text-transform: uppercase; letter-spacing: 0.06em; }
.res-val { font-family: var(--font-mono); font-size: var(--resultado-fs, var(--text-md)); color: var(--color-text-muted); }
.res-val.gold { color: var(--color-gold); font-weight: 600; }
.res-val.blue { color: #60a5fa; font-weight: 600; }
.res-val-alt { font-family: var(--font-mono); font-size: var(--resultado-sub-fs, 0.85rem); color: var(--color-text-muted); }
.err-msg { color: var(--color-error); font-size: 0.82rem; margin-top: 0.5rem; }
.ley-cabeza-display { display: flex; align-items: baseline; gap: 0.4rem; }
.lc-valor { font-family: var(--font-mono); font-size: 1.3rem; font-weight: 700; color: var(--color-gold); }
.lc-label { font-size: .7rem; color: var(--color-text-faint); font-family: var(--font-mono); }
</style>
