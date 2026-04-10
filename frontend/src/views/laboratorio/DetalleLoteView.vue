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

      <!-- DATOS DEL LOTE -->
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
          <!-- Ley planta calculada on-the-fly -->
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

        <!-- Dirimencia badge -->
        <div v-if="lote.tiene_dirimencia" class="dirimencia-alert" style="margin-top:0.75rem">
          ⚠️ Este lote tiene análisis de dirimencia — prevalece sobre todos los demás
        </div>
      </section>

      <!-- ── TAB: ANÁLISIS DE LEY ──────────────────────────────────────── -->
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
              <a :href="a.certificado_url" target="_blank" class="link-cert">Ver PDF</a>
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

        <!-- Acciones ley -->
        <div class="acciones-lote">
          <button class="btn-secondary" @click="solicitarRemuestreo">
            Solicitar remuestreo
          </button>
        </div>

      </template>

      <!-- ── TAB: ANÁLISIS DE RECUPERACIÓN ──────────────────────────────── -->
      <template v-if="tabActual === 'rec'">

        <!-- Info ley planta necesaria para enviar a recuperación -->
        <div v-if="lote.ley_planta == null" class="info-box warning">
          ⚠️ Sin ley planta disponible. Registre al menos un análisis de ley vigente antes de enviar a recuperación.
        </div>
        <div v-else-if="!cipRecupInterno" class="info-box warning">
          ⚠️ Sin CIP de recuperación. El técnico debe completar pruebas metalúrgicas y etiquetar la muestra.
        </div>

        <!-- Cards de análisis de recuperación existentes -->
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
              <a :href="a.certificado_url" target="_blank" class="link-cert">Ver PDF</a>
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

        <!-- Acciones recuperación -->
        <div class="acciones-lote">
          <!-- Enviar a lab interno: solo si hay ley planta y CIP rec interno y no hay pending activo -->
          <button
            v-if="lote.ley_planta != null && cipRecupInterno && !tienePendiente"
            class="btn-primary"
            @click="enviarARecuperacion"
            :disabled="enviando"
          >
            <span v-if="enviando" class="spinner" style="margin-right:0.4rem"></span>
            Enviar a recuperación interna
          </button>
          <span v-else-if="tienePendiente" class="info-inline">
            ⏳ Pendiente en laboratorio
          </span>

          <!-- Adjuntar certificado externo directamente -->
          <label v-if="cipRecupExterno" class="btn-secondary" style="cursor:pointer">
            Subir certificado externo
            <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="subirCertExterno" />
          </label>
        </div>

      </template>

    </template>

    <!-- Modal descartar -->
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

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import type { LoteLabOut } from '@/types/laboratorio'

const router = useRouter()
const route  = useRoute()
const store  = useLaboratorioStore()
const ui     = useUiStore()

const ipActual  = route.params.ip as string
const cargando  = ref(false)
const enviando  = ref(false)
const lote      = ref<LoteLabOut | null>(null)
const tabActual = ref<'ley' | 'rec'>('ley')

const modalDescartar = ref<{ id: number; tipo: 'ley' | 'rec' } | null>(null)
const justificacion  = ref('')

// CIPs de recuperación del lote
const cipRecupInterno = computed(() =>
  lote.value?.cips_detalle.find(c => c.tipo_muestra === 'RecuperacionInterno')?.codigo_cip ?? null
)
const cipRecupExterno = computed(() =>
  lote.value?.cips_detalle.find(c => c.tipo_muestra === 'RecuperacionExterno')?.codigo_cip ?? null
)

const tienePendiente = computed(() =>
  lote.value?.analisis_recuperacion.some(a => a.estado === 'PENDIENTE' && a.vigente) ?? false
)

onMounted(async () => {
  cargando.value = true
  lote.value = await store.cargarDetalleLote(ipActual)
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

// ── Descartar ─────────────────────────────────────────────────────────────────
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

// ── Adjuntar certificados ─────────────────────────────────────────────────────
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

// ── Enviar a recuperación interna ─────────────────────────────────────────────
async function enviarARecuperacion() {
  enviando.value = true
  const nuevo = await store.enviarRecuperacion(ipActual, {
    cip: cipRecupInterno.value ?? undefined,
  })
  enviando.value = false
  if (nuevo) lote.value = await store.cargarDetalleLote(ipActual)
}

// ── Subir certificado externo (sin pending previo, registro directo) ───────────
async function subirCertExterno(e: Event) {
  ui.toast('Para registrar recuperación externa, use el formulario de laboratorio con el CIP externo', 'info')
}

async function solicitarRemuestreo() {
  const ok = await ui.showConfirm({
    title: 'Solicitar Remuestreo',
    message: `¿Confirmar solicitud de remuestreo para el lote ${ipActual}?`,
  })
  if (ok) ui.toast('Remuestreo solicitado — avise al área de muestreo', 'info')
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

.link-cert { font-size: 0.75rem; color: var(--color-gold); text-decoration: underline; }

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
</style>
