<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">
          {{ tabActual === 'ley' ? 'Análisis de Ley' : 'Análisis de Recuperación' }}
        </h1>
        <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">
          {{ ipActual }}
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="toggleTab">
          {{ tabActual === 'ley' ? 'Ver Recuperación ↓' : 'Ver Análisis Ley ↑' }}
        </button>
        <button class="btn-secondary" @click="router.back()">← Volver</button>
      </div>
    </header>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
    </div>

    <template v-else-if="lote">

      <section class="card">
        <h2 class="card-titulo">DATOS DEL LOTE</h2>
        <div class="detalle-row-grid">
          <div class="detalle-item">
            <span class="di-label">IP:</span>
            <span class="di-value" style="color:var(--color-gold)">{{ lote.ip }}</span>
          </div>
          <div class="detalle-item">
            <span class="di-label">FECHA RECEPCIÓN:</span>
            <span class="di-value">{{ fmt(lote.fecha_recepcion) }}</span>
          </div>
          <div class="detalle-item">
            <span class="di-label">PROVEEDOR:</span>
            <span class="di-value">{{ lote.proveedor }}</span>
          </div>
          <div class="detalle-item">
            <span class="di-label">MATERIAL:</span>
            <span class="di-value">{{ lote.material ?? '-' }}</span>
          </div>
          <div class="detalle-item" v-if="lote.ley_planta != null">
            <span class="di-label">LEY PLANTA (promedio):</span>
            <span class="di-value" style="color:var(--color-gold);font-family:var(--font-mono)">
              {{ Number(lote.ley_planta).toFixed(4) }} oz/TC
            </span>
          </div>
          <div class="detalle-item" v-if="lote.ley_minero != null">
            <span class="di-label">LEY MINERO:</span>
            <span class="di-value" style="font-family:var(--font-mono)">
              {{ Number(lote.ley_minero).toFixed(4) }} oz/TC
            </span>
          </div>
        </div>

        <div v-if="lote.tiene_dirimencia" class="dirimencia-alert" style="margin-top:0.75rem">
          ⚠️ Este lote tiene análisis de dirimencia — prevalece sobre todos los demás
        </div>
      </section>

      <template v-if="tabActual === 'ley'">

        <div class="labs-grid">
          <div
            v-for="(a, i) in lote.analisis_ley"
            :key="a.id"
            class="lab-card"
            :class="{ descartado: !a.vigente }"
          >
            <div class="lab-card-header">
              <span class="lab-titulo">{{ tipoBadge(a.tipo_analisis) }}</span>
              <span v-if="!a.vigente" class="badge-estado pendiente" style="font-size:0.65rem">DESCARTADO</span>
            </div>

            <div class="lab-field"><span class="lf-label">CIP:</span>          <span class="lf-value td-mono" style="color:var(--color-gold)">{{ a.cip ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LABORATORIO:</span>  <span class="lf-value">{{ a.laboratorio }}</span></div>
            <div class="lab-field"><span class="lf-label">FECHA:</span>        <span class="lf-value">{{ fmt(a.fecha_analisis) }}</span></div>
            <div class="lab-field"><span class="lf-label">MALLA +140:</span>   <span class="lf-value">{{ a.ley_grueso }}</span></div>
            <div class="lab-field"><span class="lf-label">MALLA -140:</span>   <span class="lf-value">{{ a.ley_fino }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY OZ/TC:</span>    <span class="lf-value highlight">{{ a.ley_final }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY GR/TM:</span>    <span class="lf-value">{{ a.ley_gr_tm }}</span></div>

            <div v-if="a.certificado_url" class="lab-field">
              <span class="lf-label">CERTIFICADO:</span>
              <a href="#" @click.prevent="verCertificado(a.certificado_url)" class="link-cert">Ver PDF</a>
            </div>

            <div class="lab-card-footer" v-if="a.vigente">
              <button class="btn-danger-sm" @click="toggleDescartarLey(a.id)" title="Descartar">
                Descartar
              </button>
              <label class="btn-secondary-sm" title="Adjuntar certificado">
                Adjuntar cert.
                <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="adjuntarCertLey($event, a.id)" />
              </label>
            </div>
          </div>

          <div v-if="lote.analisis_ley.length === 0" class="estado-tabla sin-datos">
            Sin análisis de ley registrados
          </div>
        </div>

        <section class="card" v-if="lote.ley_planta != null">
          <h2 class="card-titulo" style="display:flex;justify-content:space-between;align-items:center">
            <span>LEY COMERCIAL (con reglas aplicadas)</span>
            <button
              class="btn-primary"
              style="font-size:0.75rem;padding:0.35rem 0.9rem"
              @click="generarCertificado"
              :disabled="generando"
            >
              <span v-if="generando" class="spinner" style="margin-right:0.4rem"></span>
              Generar certificado PDF
            </button>
          </h2>

          <div v-if="cargandoLeyComercial" class="estado-tabla">
            <span class="spinner" style="margin-right:0.5rem"></span> Calculando...
          </div>

          <template v-else-if="leyComercialCalc">
            <div class="lc-grid">
              <div class="lc-item">
                <span class="lc-label">LEY PLANTA (promedio vigentes):</span>
                <span class="lc-valor mono">{{ Number(lote.ley_planta)?.toFixed(4) }} oz/TC</span>
              </div>
              <div class="lc-item" v-if="lote.ley_minero">
                <span class="lc-label">LEY MINERO:</span>
                <span class="lc-valor mono">{{ Number(lote.ley_minero)?.toFixed(4) }} oz/TC</span>
              </div>
              <div class="lc-item">
                <span class="lc-label">LEY COMERCIAL (a entregar):</span>
                <span class="lc-valor mono gold">{{ leyComercialCalc.ley_comercial.toFixed(4) }} oz/TC</span>
              </div>
              <div class="lc-item" v-if="leyComercialCalc.descuento_aplicado">
                <span class="lc-label">DESCUENTO APLICADO:</span>
                <span class="lc-valor mono">- {{ leyComercialCalc.descuento_aplicado.toFixed(4) }}</span>
              </div>
              <div class="lc-item" v-if="leyComercialCalc.factor_aplicado !== 1">
                <span class="lc-label">FACTOR:</span>
                <span class="lc-valor mono">× {{ leyComercialCalc.factor_aplicado.toFixed(3) }}</span>
              </div>
            </div>

            <div v-if="leyComercialCalc.sin_parametros" class="info-box warning" style="margin-top:0.75rem">
              ⚠️ Sin parámetros comerciales configurados para este proveedor-acopiador.
            </div>
            <div v-if="leyComercialCalc.detalle && !leyComercialCalc.sin_parametros"
              style="font-size:0.75rem;color:var(--color-text-faint);margin-top:0.5rem;font-family:var(--font-mono)">
              Detalle: {{ leyComercialCalc.detalle }}
            </div>
          </template>
          <div v-else class="info-box warning" style="margin-top:0.75rem">
            <AlertTriangle /> No se pudo calcular la ley comercial.
            <button class="btn-secondary" style="margin-left:0.5rem;font-size:0.75rem" @click="recargarLeyComercial">Reintentar</button>
          </div>
        </section>

        <div class="acciones-lote">
          <button class="btn-primary" @click="abrirModalAgregarLey">
            + Registrar nueva ley
          </button>
        </div>

      </template>

      <template v-if="tabActual === 'rec'">

        <div v-if="lote.ley_planta == null" class="info-box warning">
          ⚠️ Sin ley planta disponible. Registre al menos un análisis de ley vigente antes de enviar a recuperación.
        </div>
        <div v-else-if="!cipRecupInterno" class="info-box warning">
          ⚠️ Sin CIP de recuperación. El técnico debe completar pruebas metalúrgicas y etiquetar la muestra.
        </div>

        <div class="labs-grid" v-if="lote.analisis_recuperacion.length > 0">
          <div
            v-for="(a, i) in lote.analisis_recuperacion"
            :key="a.id"
            class="lab-card"
            :class="{ descartado: !a.vigente }"
          >
            <div class="lab-card-header">
              <span class="lab-titulo">RECUPERACIÓN {{ i + 1 }}</span>
              <span class="badge-estado" :class="a.estado === 'PENDIENTE' ? 'pendiente' : 'completo'" style="font-size:0.65rem">
                {{ a.estado }}
              </span>
            </div>

            <div class="lab-field"><span class="lf-label">CIP:</span>           <span class="lf-value td-mono" style="color:var(--color-gold)">{{ a.cip ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LABORATORIO:</span>   <span class="lf-value">{{ a.laboratorio }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY CABEZA:</span>    <span class="lf-value">{{ a.ley_cabeza ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY COLA:</span>      <span class="lf-value">{{ a.ley_cola ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY LÍQUIDO:</span>   <span class="lf-value">{{ a.ley_liquido ?? '-' }}</span></div>
            <div class="lab-field">
              <span class="lf-label">% RECUPERACIÓN:</span>
              <span class="lf-value highlight">{{ a.recuperacion != null ? a.recuperacion + '%' : '-' }}</span>
            </div>

            <div v-if="a.certificado_url" class="lab-field">
              <span class="lf-label">CERTIFICADO:</span>
              <a href="#" @click.prevent="verCertificado(a.certificado_url)" class="link-cert">Ver PDF</a>
            </div>

            <div class="lab-card-footer" v-if="a.vigente">
              <button class="btn-danger-sm" @click="toggleDescartarRec(a.id)">Descartar</button>
              <label class="btn-secondary-sm">
                Adjuntar cert.
                <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="adjuntarCertRec($event, a.id)" />
              </label>
            </div>
          </div>
        </div>

        <div class="acciones-lote">
          <button
            v-if="lote.ley_planta != null && cipsRecuperacionDisponibles.length > 0"
            class="btn-primary"
            @click="abrirModalRecup"
            :disabled="enviando"
          >
            <span v-if="enviando" class="spinner" style="margin-right:0.4rem"></span>
            Enviar a recuperación
          </button>
          <span v-if="tienePendiente" class="info-inline" style="margin-left:0.5rem">
            ⏳ Análisis pendiente en laboratorio
          </span>
        </div>

        <button class="btn-secondary" @click="solicitarRemuestreo">
            Solicitar nueva prueba
        </button>

      </template>

    </template>

    <div v-if="modalDescartar" class="modal-overlay" @click.self="modalDescartar = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Descartar análisis</h2>
          <button class="btn-cerrar" @click="modalDescartar = null">×</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label class="field-label">Justificación (obligatoria):</label>
            <textarea class="field-input" v-model="justificacion" rows="3" placeholder="Ej: Resultado discordante"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalDescartar = null">Cancelar</button>
          <button class="btn-danger" @click="confirmarDescartar" :disabled="!justificacion.trim()">Confirmar</button>
        </div>
      </div>
    </div>

    <div v-if="modalAgregarLey" class="modal-overlay" @click.self="modalAgregarLey = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Registrar Nueva Ley</h2>
          <button class="btn-cerrar" @click="modalAgregarLey = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="cipsDisponiblesLey.length === 0" class="info-box warning">
            ⚠️ No hay CIPs de laboratorio disponibles sin análisis. Es necesario generar nuevas etiquetas o solicitar un remuestreo.
          </div>
          <div v-else class="field">
            <label class="field-label">Seleccione el CIP a analizar:</label>
            <select class="field-select field-input" v-model="cipSeleccionado">
              <option disabled value="">-- Seleccionar CIP --</option>
              <option v-for="c in cipsDisponiblesLey" :key="c.codigo_cip" :value="c.codigo_cip">
                {{ c.codigo_cip }} ({{ c.laboratorio || 'Por definir' }})
              </option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalAgregarLey = false">Cancelar</button>
          <button class="btn-primary" @click="confirmarAgregarLey" :disabled="!cipSeleccionado">Continuar</button>
        </div>
      </div>
    </div>

  </div>

    <!-- Modal selección lab recuperacion -->
    <div v-if="modalRecup" class="modal-overlay" @click.self="modalRecup = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Enviar a Recuperación</h2>
          <button class="btn-cerrar" @click="modalRecup = false">×</button>
        </div>
        <div class="modal-body">
          <div class="field" style="margin-bottom:1rem">
            <label class="field-label">CIP A USAR:</label>
            <select class="field-select field-input" v-model="cipRecupElegido" @change="onCipRecupChange">
              <option v-for="c in cipsRecuperacionDisponibles" :key="c.codigo_cip" :value="c.codigo_cip">
                {{ c.codigo_cip }} — {{ c.tipo_muestra }}
              </option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">LABORATORIO DESTINO:</label>
            <select class="field-select field-input" v-model="labRecupElegida">
              <option v-for="lab in labsRecupDisponibles" :key="lab" :value="lab">{{ lab }}</option>
            </select>
            <p style="font-size:0.7rem;color:var(--color-text-faint);margin-top:0.4rem">
              <span v-if="labRecupElegida === 'Paititi' || labRecupElegida === 'Laboratorio Interno'">
                Laboratorio interno: se creará análisis PENDIENTE para el laboratorista.
              </span>
              <span v-else>
                Lab externo: se marcará el CIP como enviado. Suba el certificado cuando lo reciba.
              </span>
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalRecup = false">Cancelar</button>
          <button class="btn-primary" @click="confirmarEnvioRecuperacion" :disabled="!cipRecupElegido">Confirmar</button>
        </div>
      </div>
    </div>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import type { LoteLabOut } from '@/types/laboratorio'
import { laboratorioApi, type LeyComercialCalc } from '@/api/laboratorio'
import { muestreoApi } from '@/api/muestreo'
import { pruebasApi } from '@/api/pruebas'

const router = useRouter()
const route  = useRoute()
const store  = useLaboratorioStore()
const ui     = useUiStore()

const ipActual  = route.params.ip as string
const cargando  = ref(false)
const enviando  = ref(false)
const lote      = ref<LoteLabOut | null>(null)
const tabActual = ref<'ley' | 'rec'>('ley')

// Descarte
const modalDescartar = ref<{ id: number; tipo: 'ley' | 'rec' } | null>(null)
const justificacion  = ref('')

// Agregar Ley
const modalAgregarLey = ref(false)
const cipSeleccionado = ref('')

const cargandoLeyComercial = ref(false)
const leyComercialCalc = ref<LeyComercialCalc | null>(null)
const generando = ref(false)

// Modal seleccion lab para recuperacion
const modalRecup = ref(false)
const cipRecupElegido = ref<string | null>(null)
const labRecupElegida = ref('')
const labsRecupDisponibles = ref<string[]>([])

// ── Computed: CIPs Disponibles para Ley ──
// Solo traemos los CIPs de tipo Laboratorio que NO existan en el array de analisis_ley
const cipsDisponiblesLey = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(c =>
    c.tipo_muestra === 'Laboratorio' &&
    !lote.value!.analisis_ley.some(a => a.cip === c.codigo_cip)
  )
})

// CIPs de recuperacion disponibles (sin analisis vigente)
const cipsRecuperacionDisponibles = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(c =>
    (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno') &&
    !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente)
  )
})

const cipRecupInterno = computed(() =>
  lote.value?.cips_detalle.find(c => (c.tipo_muestra === 'RecuperacionInterno') && !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente))
)

const tienePendiente = computed(() =>
  lote.value?.analisis_recuperacion.some(a => a.estado === 'PENDIENTE' && a.vigente) ?? false
)

// Cargar ley comercial
watch([tabActual, lote], async ([tab, l]: ['ley' | 'rec', LoteLabOut | null]) => {
  if (tab === 'ley' && l?.ley_planta != null && !leyComercialCalc.value) {
    cargandoLeyComercial.value = true
    try {
      leyComercialCalc.value = await laboratorioApi.getLeyComercial(ipActual)
    } catch { } finally {
      cargandoLeyComercial.value = false
    }
  }
}, { immediate: true })

async function recargarLeyComercial() {
  if (!lote.value?.ley_planta) return
  cargandoLeyComercial.value = true
  try {
    leyComercialCalc.value = await laboratorioApi.getLeyComercial(ipActual)
  } catch { } finally {
    cargandoLeyComercial.value = false
  }
}

async function generarCertificado() {
  generando.value = true
  try {
    await laboratorioApi.descargarCertificadoPdf(ipActual)
  } catch {
    ui.toast('Error al generar certificado PDF', 'error')
  } finally {
    generando.value = false
  }
}

onMounted(async () => {
  cargando.value = true
  ;[lote.value, labsRecupDisponibles.value] = await Promise.all([
    store.cargarDetalleLote(ipActual),
    muestreoApi.listarLaboratorios().catch(() => ['Paititi', 'Minares South S.R.L.', 'El Dorado', 'Otro']),
  ])
  cargando.value = false
})

function toggleTab() {
  tabActual.value = tabActual.value === 'ley' ? 'rec' : 'ley'
}

function fmt(d?: string | null) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function tipoBadge(tipo: string) {
  const m: Record<string, string> = {
    planta: 'LAB INTERNO',
    externo: 'LAB EXTERNO',
    minero: 'LEY MINERO',
    dirimencia: 'DIRIMENCIA',
  }
  return m[tipo] ?? tipo.toUpperCase()
}

// ── Visor Seguro de PDF ──
async function verCertificado(ruta: string | null | undefined) {
  if (!ruta) return
  try {
    const url = await laboratorioApi.obtenerUrlArchivoVirtual(ruta)
    window.open(url, '_blank')
  } catch (error) {
    ui.toast('Error al descargar o visualizar el documento', 'error')
  }
}

// ── Modal Agregar Ley ──
function abrirModalAgregarLey() {
  cipSeleccionado.value = '' // Reiniciamos el estado del select
  modalAgregarLey.value = true
}

function confirmarAgregarLey() {
  if (cipSeleccionado.value) {
    if (store.puedeImportarCert) {
      router.push(`/laboratorio/importar-ley/${cipSeleccionado.value}`)
    } else {
      router.push(`/laboratorio/ley/${cipSeleccionado.value}`)
    }
  }
}

// ── Descartar ──
function toggleDescartarLey(id: number) {
  justificacion.value = ''
  modalDescartar.value = { id, tipo: 'ley' }
}
function toggleDescartarRec(id: number) {
  justificacion.value = ''
  modalDescartar.value = { id, tipo: 'rec' }
}

async function confirmarDescartar() {
  if (!modalDescartar.value) return
  const { id, tipo } = modalDescartar.value
  const j = justificacion.value.trim()
  if (!j) return

  const ok = tipo === 'ley'
    ? await store.descartarLey(id, j)
    : await store.descartarRecuperacion(id, j)

  if (ok) {
    modalDescartar.value = null
    lote.value = await store.cargarDetalleLote(ipActual)
  }
}

// ── Adjuntar certificados ──
async function adjuntarCertLey(e: Event, analisisId: number) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const ok = await store.subirCertificadoLey(analisisId, file)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

async function adjuntarCertRec(e: Event, analisisId: number) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const ok = await store.subirCertificadoRecuperacion(analisisId, file)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

// ── Modal recuperacion ──
function abrirModalRecup() {
  cipRecupElegido.value = cipsRecuperacionDisponibles.value[0]?.codigo_cip ?? null
  labRecupElegida.value = cipsRecuperacionDisponibles.value[0]?.laboratorio ?? labsRecupDisponibles.value[0] ?? 'Paititi'
  modalRecup.value = true
}

function onCipRecupChange() {
  const cip = cipsRecuperacionDisponibles.value.find(c => c.codigo_cip === cipRecupElegido.value)
  labRecupElegida.value = cip?.laboratorio ?? labsRecupDisponibles.value[0] ?? 'Paititi'
}

async function confirmarEnvioRecuperacion() {
  if (!cipRecupElegido.value) return
  enviando.value = true
  modalRecup.value = false
  const esInterno = labRecupElegida.value === 'Paititi' || labRecupElegida.value === 'Laboratorio Interno'
  if (esInterno) {
    await store.enviarRecuperacion(ipActual, { cip: cipRecupElegido.value, laboratorio: labRecupElegida.value })
  } else {
    // Externo: solo actualizar lab destino en el CIP
    const cipObj = lote.value?.cips_detalle.find(c => c.codigo_cip === cipRecupElegido.value)
    if (cipObj) {
      try {
        // Necesitamos el id numerico del CIP - viene de cips_detalle que no tiene id
        // Recargamos cips para obtenerlo y hacer el patch
        const cips = await muestreoApi.obtenerEtiquetas(ipActual)
        const cipConId = cips.find(c => c.codigo_cip === cipRecupElegido.value)
        if (cipConId) await muestreoApi.actualizarLaboratorioCip(cipConId.id, labRecupElegida.value)
        ui.toast(`CIP marcado para ${labRecupElegida.value}. Suba el certificado cuando lo reciba.`, 'info')
      } catch {
        ui.toast('Error al asignar laboratorio', 'error')
      }
    }
  }
  enviando.value = false
  lote.value = await store.cargarDetalleLote(ipActual)
}

async function subirCertExterno(e: Event) {
  ui.toast('Para registrar recuperación externa, use el formulario de laboratorio con el CIP externo', 'info')
}

async function solicitarRemuestreo() {
  const ok = await ui.showConfirm({
    title: 'Solicitar Remuestreo',
    message: `Se creará un nuevo registro de prueba metalúrgica para ${ipActual}. ` +
             'El registro anterior se conserva para auditoría. El técnico deberá completar los parámetros y etiquetar un nuevo CIP. ¿Confirmar?',
    confirmLabel: 'Solicitar',
  })
  if (!ok) return
  try {
    await pruebasApi.solicitarRemuestreo(ipActual)
    ui.toast('Remuestreo solicitado. El lote aparece en Pruebas Metalúrgicas.', 'success')
    lote.value = await store.cargarDetalleLote(ipActual)
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al solicitar remuestreo', 'error')
  }
}
</script>

<style scoped>
.detalle-row-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.detalle-item { display: flex; flex-direction: column; gap: 0.15rem; }

.di-label {
  font-size: 0.68rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.di-value { font-size: var(--text-md); color: var(--color-text); }

.labs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1rem;
}

.lab-card {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 1rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: rgba(255,255,255,0.02);
}

.lab-card.descartado { opacity: 0.45; border-style: dashed; }

.lab-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.lab-titulo {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  text-transform: uppercase;
}

.lab-field { display: flex; justify-content: space-between; align-items: center; }

.lf-label { font-size: 0.68rem; color: var(--color-text-faint); font-family: var(--font-mono); letter-spacing: 0.05em; }
.lf-value { font-family: var(--font-mono); color: var(--color-text-muted); font-size: var(--text-md); }
.lf-value.highlight { color: var(--color-gold); font-size: var(--text-lg); }

.lab-card-footer {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.btn-danger-sm {
  font-size: 0.72rem;
  padding: 0.25rem 0.65rem;
  background: rgba(239,68,68,0.12);
  color: #f87171;
  border: 1px solid rgba(239,68,68,0.3);
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary-sm {
  font-size: 0.72rem;
  padding: 0.25rem 0.65rem;
  background: transparent;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
}

.link-cert { font-size: 0.75rem; color: var(--color-gold); text-decoration: underline; cursor: pointer; }

.acciones-lote {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
  margin: 0.5rem 0 1.5rem;
}

.info-inline {
  font-size: var(--text-sm);
  color: var(--color-text-faint);
  font-family: var(--font-mono);
}

.dirimencia-alert {
  background: rgba(168,85,247,0.12);
  border: 1px solid rgba(168,85,247,0.4);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  color: #c084fc;
  font-size: var(--text-sm);
}

.info-box {
  border-radius: 6px;
  padding: 0.75rem 1rem;
  font-size: var(--text-sm);
  margin-bottom: 1rem;
}

.info-box.warning {
  background: rgba(234,179,8,0.08);
  border: 1px solid rgba(234,179,8,0.3);
  color: #fbbf24;
}

.lc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.lc-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.lc-label {
  font-size: 0.68rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.lc-valor {
  font-size: var(--text-md);
  color: var(--color-text);
}

.lc-valor.mono { font-family: var(--font-mono); }
.lc-valor.gold { color: var(--color-gold); font-size: var(--text-lg); font-weight: 600; }
</style>
