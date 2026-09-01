<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">
          Análisis Newmont
        </h1>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="router.back()">← Volver</button>
        <button class="btn-primary" @click="guardar" :disabled="guardando || agBloqueado">
          <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
          Guardar cambios
        </button>
        <!-- Generar/Regenerar certificado -->
        <button
          v-if="!agBloqueado"
          class="btn-primary"
          @click="generarCertificado"
          :disabled="generandoCert || !yaGuardado"
          title="Generar y guardar certificado PDF"
        >
          <span v-if="generandoCert" class="spinner" style="margin-right:0.4rem"></span>
          {{ certificadoGenerado ? '↺ Regen. con Ag' : 'Guardar certificado' }}
        </button>
        <span v-if="agBloqueado" class="badge-cert-ok">✓ Certificado Ley generado</span>
      </div>
    </header>

    <!-- Banner offline -->
    <div v-if="!online" class="offline-banner">
      <WifiOff :size="16" style="margin-right:0.5rem;vertical-align:middle" />
      Sin conexión — el análisis se guardará localmente y se sincronizará al reconectar.
    </div>

    <!-- Banner Ag existente (editable) -->
    <div v-if="tieneAg && !agBloqueado" class="cert-generado-banner" style="background:rgba(96,165,250,0.06);border-color:rgba(96,165,250,0.3);color:#93c5fd">
      Ley de Plata registrada previamente. Puede actualizar el valor Au + Ag y guardar para regenerar el certificado.
    </div>

    <!-- Banner Ag bloqueada -->
    <div v-if="agBloqueado" class="cert-generado-banner">
      ✓ Certificado generado con Ley de Plata incluida. Para modificar los datos, use el modo edición (requiere permiso).
    </div>

    <!-- DATOS DEL LOTE -->
    <section class="card">
      <h2 class="card-titulo">DATOS DEL LOTE</h2>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">CÓDIGO:</label>
          <input class="field-input" v-model="form.cip" :disabled="!modoNuevo" style="color:var(--color-gold);font-family:var(--font-mono)" placeholder="Ingrese código..." />
        </div>
      </div>
    </section>

    <!-- DATOS DEL ENSAYO -->
    <section class="card">
      <h2 class="card-titulo">DATOS DEL ENSAYO</h2>
      <div class="form-grid">
        <div class="field">
          <label class="field-label">FECHA INGRESO:</label>
          <input type="date" class="field-input" v-model="form.fecha_analisis" :disabled="agBloqueado" />
        </div>
        <div class="field">
          <label class="field-label">RECEPCIÓN DE MUESTRAS:</label>
          <input class="field-input" v-model="descripcion" placeholder="0.5kg aprox. de Mineral" :disabled="agBloqueado" />
        </div>
        <div class="field">
          <label class="field-label">DESCRIPCIÓN:</label>
          <select v-model="descripcionPDF" class="field-select field-input field-sm" :disabled="agBloqueado">
            <option value="PROCESO">PROCESO</option>
            <option value="LAB. METALÚRGICO">LAB. METALÚRGICO</option>
            <option value="RECONOCIMIENTO">RECONOCIMIENTO</option>
            <option value="LOTE">LOTE</option>
          </select>
        </div>
        <div class="field">
          <label class="field-label">PARA:</label>
          <select v-model="paraDest" class="field-select field-input field-sm" :disabled="agBloqueado">
            <option value="COMERCIAL">COMERCIAL</option>
            <option value="PLANTA">PLANTA</option>
          </select>
        </div>
        <div class="field">
          <label class="field-label">SOLICITUD:</label>
          <input class="field-input" v-model="solicitudTexto" :disabled="agBloqueado" />
        </div>
        <div class="field">
          <label class="field-label">TIPO DE ANÁLISIS:</label>
          <input class="field-input"
            :value="'Fire Assay - Gravimétrico'"
            disabled />
        </div>
      </div>
    </section>

    <!-- LEYES DE LA MUESTRA (Triple Sampling Au) -->
    <section class="card">
      <h2 class="card-titulo">LEYES DE LA MUESTRA (Triple Sampling)</h2>
      <div class="muestras-cards">

        <!-- Card Fino 1 -->
        <div class="muestra-card">
          <h3 class="muestra-card-titulo">MUESTRA FINO 1</h3>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Peso (g)</label>
              <input type="number" class="field-input" v-model.number="pFino1"
                :disabled="certificadoGenerado"
                step="0.001" placeholder="0.000" @input="recalc" />
            </div>
            <div class="field">
              <label class="field-label">Au (mg)</label>
              <input type="number" class="field-input" v-model.number="auFino1"
                :disabled="certificadoGenerado"
                step="0.0001" placeholder="0.0000" @input="recalc" />
            </div>
          </div>
        </div>

        <!-- Card Fino 2 -->
        <div class="muestra-card">
          <h3 class="muestra-card-titulo">MUESTRA FINO 2</h3>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Peso (g)</label>
              <input type="number" class="field-input" v-model.number="pFino2"
                :disabled="certificadoGenerado"
                step="0.001" placeholder="0.000" @input="recalc" />
            </div>
            <div class="field">
              <label class="field-label">Au (mg)</label>
              <input type="number" class="field-input" v-model.number="auFino2"
                :disabled="certificadoGenerado"
                step="0.0001" placeholder="0.0000" @input="recalc" />
            </div>
          </div>
        </div>

        <!-- Card Grueso -->
        <div class="muestra-card">
          <h3 class="muestra-card-titulo">MUESTRA GRUESO</h3>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Peso (g)</label>
              <input type="number" class="field-input" v-model.number="pGrueso"
                :disabled="certificadoGenerado"
                step="0.001" placeholder="0.000" @input="recalc" />
            </div>
            <div class="field">
              <label class="field-label">Au (mg)</label>
              <input type="number" class="field-input" v-model.number="auGrueso"
                :disabled="certificadoGenerado"
                step="0.0001" placeholder="0.0000" @input="recalc" />
            </div>
          </div>
        </div>

        <!-- Card Resultados Au -->
        <div class="muestra-card muestra-card--resultados">
          <h3 class="muestra-card-titulo">RESULTADOS CALCULADOS</h3>
          <div class="resultados-grid">
            <div class="resultado-item">
              <span class="resultado-label">OZ/TC −140 (fino prom.)</span>
              <span class="resultado-valor" style="font-size:var(--resultado-fs, var(--text-md))">{{ fmtNum(ozMenos) }}</span>
            </div>
            <div class="resultado-item resultado-item--sub">
              <span class="resultado-label resultado-label--unit">≡ GR/TM −140</span>
              <span class="resultado-valor resultado-valor--sub" style="font-size:var(--resultado-sub-fs, 0.72rem)">{{ ozMenos != null ? (ozMenos * FACTOR).toFixed(3) : '-' }}</span>
            </div>
            <div class="resultado-item">
              <span class="resultado-label">OZ/TC +140 (grueso)</span>
              <span class="resultado-valor" style="font-size:var(--resultado-fs, var(--text-md))">{{ fmtNum(ozMas) }}</span>
            </div>
            <div class="resultado-item resultado-item--sub">
              <span class="resultado-label resultado-label--unit">≡ GR/TM +140</span>
              <span class="resultado-valor resultado-valor--sub" style="font-size:var(--resultado-sub-fs, 0.72rem)">{{ ozMas != null ? (ozMas * FACTOR).toFixed(3) : '-' }}</span>
            </div>
            <div class="resultado-item resultado-item--gold">
              <span class="resultado-label">LEY AU (OZ/TC)</span>
              <span class="resultado-valor highlight" style="font-size:var(--resultado-hl-fs, var(--text-xl))">{{ fmtNum(leyFinal) }}</span>
            </div>
            <div class="resultado-item">
              <span class="resultado-label">LEY AU (GR/TM)</span>
              <span class="resultado-valor" style="color:var(--color-gold);font-size:var(--resultado-fs, var(--text-md))">
                {{ leyGrTm != null ? leyGrTm.toFixed(3) : '-' }}
              </span>
            </div>
          </div>
        </div>

      </div>
      <p v-if="errCalc" class="error-msg" style="margin-top:0.75rem">{{ errCalc }}</p>
    </section>

    <!-- LEY DE PLATA (fórmula Newmont) -->
    <section class="card">
      <h2 class="card-titulo">LEY DE PLATA (Au + Ag)</h2>
      <div class="muestras-cards">

        <!-- Card entrada Au + Ag -->
        <div class="muestra-card">
          <h3 class="muestra-card-titulo">SEÑAL COMBINADA</h3>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Au + Ag (mg)</label>
              <input type="number" class="field-input" v-model.number="auAgMg"
                :disabled="agBloqueado"
                step="0.0001" min="0" placeholder="0.0000"
                style="font-family:var(--font-mono);font-size:1.05em" />
            </div>
          </div>
        </div>

        <!-- Card resultados Ag -->
        <div class="muestra-card muestra-card--resultados-ag">
          <h3 class="muestra-card-titulo">RESULTADO CALCULADO</h3>
          <div class="resultados-grid">
            <div class="resultado-item resultado-item--silver">
              <span class="resultado-label">LEY Ag (g/TM)</span>
              <span class="resultado-valor highlight-ag" style="font-size:var(--resultado-hl-fs, var(--text-xl))">
                {{ leyAgGrTmNewmont != null ? leyAgGrTmNewmont.toFixed(4) : '-' }}
              </span>
            </div>
            <div class="resultado-item resultado-item--sub">
              <span class="resultado-label resultado-label--unit">≡ Ag (oz/TC)</span>
              <span class="resultado-valor resultado-valor--sub" style="font-size:var(--resultado-sub-fs, 0.72rem);color:#60a5fa">
                {{ leyAgOzTcNewmont != null ? leyAgOzTcNewmont.toFixed(4) : '-' }}
              </span>
            </div>
          </div>
        </div>

      </div>
      <p v-if="errCalcAg" class="error-msg" style="margin-top:0.75rem">{{ errCalcAg }}</p>

    </section>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { WifiOff } from 'lucide-vue-next'
import { useLaboratorioStore } from '@/stores/laboratorio'
import type { TipoAnalisis } from '@/types/laboratorio'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'

const router = useRouter()
const route  = useRoute()
const ui     = useUiStore()
const store  = useLaboratorioStore()
const { online } = useSync()

const cipActual    = route.params.cip as string
const guardando    = ref(false)
const generandoCert= ref(false)
const errCalc      = ref('')
const errCalcAg    = ref('')
const materialInfo = ref('Mineral')

const yaGuardado = ref(false)
const certificadoGenerado = ref(false)
const analisisCompletadoId = ref<number | null>(null)

// ── Tracking ley de plata ─────────────────────────────────────────────────────
const tieneAg      = ref(false)
const analisisAgId = ref<number | null>(null)

// ── Campos del formulario ─────────────────────────────────────────────────────
const descripcion    = ref('0.5kg aprox. de Mineral')
const descripcionPDF = ref('LOTE')
const paraDest       = ref('COMERCIAL')
const modoNuevo = cipActual === '_nuevo'

const form = ref({
  cip:            modoNuevo ? '' : cipActual,
  laboratorio:    'Paititi',
  tipo_analisis:  ((route.query.tipo as TipoAnalisis | undefined) ?? 'planta'),
  origen_datos:   'manual' as const,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

const solicitudTexto = ref('Análisis de sólidos por Au')

// ── Constantes ────────────────────────────────────────────────────────────────
const FACTOR         = 34.2857
const FACTOR_NEWMONT = 34.285   // constante del laboratorio

// ── Campos de triple sampling (Au) ───────────────────────────────────────────
const pFino1   = ref<number | null>(15)
const auFino1  = ref<number | null>(null)
const pFino2   = ref<number | null>(15)
const auFino2  = ref<number | null>(null)
const pGrueso  = ref<number | null>(null)
const auGrueso = ref<number | null>(null)

// ── Campo Ag: señal combinada Au + Ag ─────────────────────────────────────────
const auAgMg = ref<number | null>(null)

// ── Fórmulas Newmont (Au) ─────────────────────────────────────────────────────
// ozMenos: usa auFino1 como peso de referencia (estándar Excel planta)
const ozMenos = computed(() => {
  if (auFino1.value == null || auFino2.value == null ||
      pFino1.value == null || pGrueso.value == null) return null
  const avgAu = (auFino1.value + auFino2.value) / 2
  return parseFloat(
    (avgAu * (200 - pGrueso.value) / (pFino1.value * 200) * 1000 / FACTOR_NEWMONT).toFixed(5)
  )
})

const ozMas = computed(() => {
  if (auGrueso.value == null) return null
  return parseFloat((auGrueso.value / (200 * FACTOR_NEWMONT / 1000)).toFixed(5))
})

const leyFinal = computed(() => {
  if (ozMenos.value == null || ozMas.value == null) return null
  return parseFloat((ozMenos.value + ozMas.value).toFixed(5))
})

const leyGrTm = computed(() => {
  if (leyFinal.value == null) return null
  return parseFloat((leyFinal.value * FACTOR).toFixed(3))
})

// Leyes individuales por muestra para analisis_detalle
const leyFino1Individual = computed(() => {
  if (auFino1.value == null || pFino1.value == null || pGrueso.value == null) return null
  return parseFloat(
    (auFino1.value * (200 - pGrueso.value) / (pFino1.value * 200) * 1000 / FACTOR_NEWMONT).toFixed(5)
  )
})

const leyFino2Individual = computed(() => {
  // Usa pFino1 como referencia por consistencia con fórmula original del Excel
  if (auFino2.value == null || pFino1.value == null || pGrueso.value == null) return null
  return parseFloat(
    (auFino2.value * (200 - pGrueso.value) / (pFino1.value * 200) * 1000 / FACTOR_NEWMONT).toFixed(5)
  )
})

// ── Fórmula Newmont (Ag) ──────────────────────────────────────────────────────
// Excel: =SI(Q="","-",((Q − PROMEDIO(F)) * 1000) / PROMEDIO(E))
// Donde Q = au_ag_mg, PROMEDIO(F) = avg(au1, au2), PROMEDIO(E) = avg(peso1, peso2)
const leyAgGrTmNewmont = computed(() => {
  if (auAgMg.value == null ||
      auFino1.value == null || auFino2.value == null ||
      pFino1.value == null  || pFino2.value == null) return null
  const avgAu   = (auFino1.value + auFino2.value) / 2
  const avgPeso = (pFino1.value  + pFino2.value)  / 2
  if (avgPeso <= 0) return null
  const result = ((auAgMg.value - avgAu) * 1000) / avgPeso
  return result > 0 ? parseFloat(result.toFixed(4)) : null
})

const leyAgOzTcNewmont = computed(() => {
  if (leyAgGrTmNewmont.value == null) return null
  return parseFloat((leyAgGrTmNewmont.value / FACTOR).toFixed(5))
})

// Ag bloqueada: el certificado ya fue generado incluyendo la ley de plata
const agBloqueado = computed(() => certificadoGenerado.value && tieneAg.value)

function recalc() {
  errCalc.value = ''
}

function fmtNum(n: number | null | undefined) {
  if (n == null) return '-'
  return n.toFixed(4)
}

// ── Cargar análisis existente ─────────────────────────────────────────────────
onMounted(async () => {
  if (!store.cips.length) await store.cargarCips()
  const cipObj = store.cips.find(c => c.cip === cipActual)
  if (cipObj?.tipo_muestra) materialInfo.value = cipObj.tipo_muestra

  if (cipObj) {
    // Encontrar el análisis Au a cargar
    let analysisToLoad: any = null
    if (route.query.id) {
      analysisToLoad = cipObj.analisis_ley.find((a: any) => a.id === Number(route.query.id))
    } else {
      // Usar el más reciente Au vigente
      analysisToLoad = cipObj.analisis_ley
        .filter((a: any) => a.material === 'Au' && a.vigente)
        .sort((a: any, b: any) => b.id - a.id)[0]
    }

    if (analysisToLoad) {
      form.value.fecha_analisis = analysisToLoad.fecha_analisis
        ? analysisToLoad.fecha_analisis.split('T')[0]
        : new Date().toISOString().split('T')[0]
      yaGuardado.value          = true
      analisisCompletadoId.value = analysisToLoad.id
      // En modo edición, el cert no bloquea
      certificadoGenerado.value = route.query.edit === '1' ? false : !!analysisToLoad.certificado_url

      // Cargar detalles Au en los campos del triple sampling
      if (analysisToLoad.detalles && analysisToLoad.detalles.length > 0) {
        const dFino1  = analysisToLoad.detalles.find((d: any) => d.origen === 'FINO1')
        const dFino2  = analysisToLoad.detalles.find((d: any) => d.origen === 'FINO2')
        const dGrueso = analysisToLoad.detalles.find((d: any) => d.origen === 'GRUESO')
        if (dFino1)  { pFino1.value  = Number(dFino1.peso)  || 15;  auFino1.value  = Number(dFino1.mineral_mg)  }
        if (dFino2)  { pFino2.value  = Number(dFino2.peso)  || 15;  auFino2.value  = Number(dFino2.mineral_mg)  }
        if (dGrueso) { pGrueso.value = Number(dGrueso.peso) || null; auGrueso.value = Number(dGrueso.mineral_mg) }
        recalc()
      }
    }

    // Cargar análisis Ag existente
    const agAnalisis: any = cipObj.analisis_ley.find(
      (a: any) => a.material === 'Ag' && a.vigente && !a.eliminado
    )
    if (agAnalisis) {
      tieneAg.value      = true
      analisisAgId.value = agAnalisis.id
      // Reconstruir auAgMg a partir de ley_gr_tm almacenada:
      // leyAgGrTm = ((auAgMg - avgAu) * 1000) / avgPeso  →  auAgMg = leyAgGrTm * avgPeso / 1000 + avgAu
      if (pFino1.value != null && pFino2.value != null &&
          auFino1.value != null && auFino2.value != null) {
        const avgAu   = (auFino1.value + auFino2.value) / 2
        const avgPeso = (pFino1.value  + pFino2.value)  / 2
        if (avgPeso > 0 && agAnalisis.ley_gr_tm != null) {
          auAgMg.value = parseFloat(
            ((Number(agAnalisis.ley_gr_tm) * avgPeso / 1000) + avgAu).toFixed(4)
          )
        }
      }
    }

    // Auto-generar certificado si se pidió desde el router
    if (route.query.gen === '1') {
      setTimeout(() => generarCertificado(), 800)
    }
  }
})

// ── Guardar ───────────────────────────────────────────────────────────────────
async function guardar() {
  errCalc.value   = ''
  errCalcAg.value = ''

  if (!form.value.cip) {
    errCalc.value = 'Ingrese el código de la muestra'
    return
  }

  // Au debe estar disponible (ya guardado o calculado ahora)
  const auDisponible = yaGuardado.value || (leyFinal.value != null && leyFinal.value > 0)
  if (!auDisponible) {
    errCalc.value = 'Ingrese los pesos y valores Au para calcular las leyes'
    return
  }

  const okConf = await ui.showConfirm({
    title:        'Guardar cambios',
    message:      '¿Desea guardar los datos del análisis?',
    confirmLabel: 'Guardar',
  })
  if (!okConf) return

  guardando.value = true
  let auSaved = false
  let agSaved = false

  // ── Guardar Au ────────────────────────────────────────────────────────────
  // Solo si el cert no fue generado aún, o si estamos en modo edición
  const debeGuardarAu = !certificadoGenerado.value || route.query.edit === '1'
  if (debeGuardarAu && leyFinal.value != null && leyFinal.value > 0) {
    const muestrasDetalle = leyFino1Individual.value != null
      ? [
          { peso_g: pFino1.value!,  au_mg: auFino1.value!, ley_oz_tc: leyFino1Individual.value! },
          { peso_g: pGrueso.value!, au_mg: auGrueso.value!, ley_oz_tc: ozMas.value! },
          { peso_g: pFino2.value!,  au_mg: auFino2.value!, ley_oz_tc: leyFino2Individual.value! },
        ]
      : undefined

    const payload = {
      cip:             form.value.cip,
      laboratorio:     form.value.laboratorio,
      tipo_analisis:   form.value.tipo_analisis,
      material:        'Au' as const,
      ley_fino:        ozMenos.value ?? 0,
      ley_grueso:      ozMas.value   ?? 0,
      origen_datos:    form.value.origen_datos,
      fecha_analisis:  form.value.fecha_analisis,
      descripcion_pdf: descripcionPDF.value,
      ...(muestrasDetalle ? { muestras_detalle: muestrasDetalle } : {}),
      es_edicion: route.query.edit === '1',
    }

    let result;
    if (route.query.edit === '1' && analisisCompletadoId.value) {
      result = await store.editarLey(analisisCompletadoId.value, payload)
    } else {
      result = await store.registrarLey(payload)
    }
    if (result) {
      yaGuardado.value           = true
      analisisCompletadoId.value = result.id
      auSaved = true
    }
  }

  // ── Guardar Ag (fórmula Newmont) ─────────────────────────────────────────
  if (auAgMg.value != null && auAgMg.value > 0 && !agBloqueado.value) {
    if (leyAgOzTcNewmont.value == null || leyAgGrTmNewmont.value == null) {
      errCalcAg.value = 'Verifique los datos Au (finos y pesos) para que la fórmula Ag sea válida.'
      guardando.value = false
      return
    }
    const agPayload = {
      cip:            form.value.cip,
      laboratorio:    form.value.laboratorio,
      tipo_analisis:  form.value.tipo_analisis as TipoAnalisis,
      material:       'Ag' as const,
      ley_fino:       leyAgOzTcNewmont.value,
      ley_grueso:     0,
      punto:          'CABEZA',
      origen_datos:   'manual' as const,
      fecha_analisis: form.value.fecha_analisis,
      es_edicion:     tieneAg.value,  // edición si ya existe un Ag previo
    }
    const agResult = await store.registrarLey(agPayload)
    if (agResult) {
      tieneAg.value      = true
      analisisAgId.value = agResult.id
      agSaved = true
    }
  }

  // ── Mensajes de resultado ─────────────────────────────────────────────────
  if (auSaved && agSaved) {
    ui.toast('Análisis Au + Ag guardado. Puede generar el certificado.', 'success')
  } else if (auSaved) {
    ui.toast('Datos Au guardados. Puede generar el certificado.', 'success')
  } else if (agSaved) {
    ui.toast('Ley de Plata actualizada. Regenere el certificado para incluirla.', 'success')
  } else {
    ui.toast('Sin cambios que guardar.', 'info')
  }

  guardando.value = false
}

async function generarCertificado() {
  if (!analisisCompletadoId.value) return

  const okConf = await ui.showConfirm({
    title:        online.value ? 'Generar Certificado' : 'Guardar sin conexión',
    message:      online.value
      ? 'Al generar el certificado, el informe será adjuntado automáticamente y los datos no podrán modificarse. ¿Desea continuar?'
      : 'Sin conexión: el certificado se generará después del sync. ¿Continuar?',
    confirmLabel: 'Generar',
  })
  if (!okConf) return

  generandoCert.value = true
  const result = await store.generarCertificadoLeyInterno(
    analisisCompletadoId.value,
    descripcionPDF.value,
    paraDest.value,
  )
  if (result) {
    certificadoGenerado.value = true
    ui.toast('Certificado generado exitosamente', 'success')
    setTimeout(() => router.push('/laboratorio'), 1500)
  }
  generandoCert.value = false
}


</script>

<style scoped>
.offline-banner {
  background: rgba(245,158,11,.1);
  border: 1px solid rgba(245,158,11,.35);
  border-radius: var(--radius-md);
  color: #f59e0b;
  font-size: var(--text-sm);
  padding: 0.6rem 1rem;
  margin-bottom: 1.25rem;
  font-family: var(--font-mono);
}

.muestras-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.muestra-card {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.9rem 1rem;
  background: rgba(255,255,255,0.02);
}

.muestra-card--resultados {
  border-color: rgba(184,151,75,0.3);
  background: rgba(184,151,75,0.04);
  --resultado-fs: 1.25rem;
  --resultado-sub-fs: 0.95rem;
  --resultado-hl-fs: 1.8rem;
}

.muestra-card-titulo {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  color: var(--color-text-faint);
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}

.resultados-grid {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.resultado-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resultado-item--sub {
  margin-top: -0.15rem;
  margin-bottom: 0.2rem;
  opacity: 0.75;
}

.resultado-label {
  font-size: 0.68rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
}

.resultado-label--unit {
  font-size: 0.62rem;
  padding-left: 0.6rem;
}

.resultado-valor {
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  font-size: var(--resultado-fs, var(--text-md));
}

.resultado-valor--sub {
  font-size: var(--resultado-sub-fs, 0.72rem);
  color: var(--color-text-faint);
}

.resultado-valor.highlight {
  color: var(--color-gold);
  font-size: var(--resultado-hl-fs, var(--text-xl));
  font-weight: 700;
}

.badge-cert-ok {
  font-size: 0.78rem; font-weight: 700; color: #4ade80;
  background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3);
  border-radius: var(--radius-sm); padding: 0.3rem 0.7rem;
}

.cert-generado-banner {
  background: rgba(34,197,94,0.06);
  border: 1px solid rgba(34,197,94,0.25);
  border-radius: var(--radius-md);
  color: #4ade80;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 0.6rem 1rem;
  margin-bottom: 1rem;
}

.error-msg {
  color: var(--color-error);
  font-size: 0.82rem;
}

.muestra-card--resultados-ag {
  border-color: rgba(96,165,250,0.3);
  background: rgba(96,165,250,0.04);
  --resultado-fs: 1.25rem;
  --resultado-sub-fs: 0.95rem;
  --resultado-hl-fs: 1.8rem;
}

.resultado-valor.highlight-ag {
  color: #60a5fa;
  font-size: var(--resultado-hl-fs, var(--text-xl));
  font-weight: 700;
  font-family: var(--font-mono);
}
</style>
