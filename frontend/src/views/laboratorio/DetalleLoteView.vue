<template>
    <div class="page-container">

      <header class="page-header">
        <div>
          <h1 class="page-title">
            {{ tabActual === 'ley' ? 'Detalle Análisis Newmont' : 'Detalle Análisis Recuperación' }}
          </h1>
        </div>
        <div style="display:flex;gap:0.75rem;align-items:center">
          <!-- Tab toggle top-right (como en mockup) -->
          <button class="btn-secondary" @click="toggleTab">
            {{ tabActual === 'ley' ? 'Análisis de Recuperación ↓' : 'Análisis Newmont ↑' }}
          </button>
          <button class="btn-secondary" @click="router.back()">← Volver</button>
          <button class="btn-primary" @click="guardar" :disabled="guardando">
            <span v-if="guardando" class="spinner" style="margin-right:0.4rem"></span>
            Guardar →
          </button>
        </div>
      </header>

      <!-- Spinner de carga -->
      <div v-if="cargando" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem"></span> Cargando datos del lote...
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
          </div>
        </section>

        <!-- ── TAB: ANÁLISIS DE LEY ──────────────────────────────────────── -->
        <template v-if="tabActual === 'ley'">
          <div v-if="lote.analisis_ley.length === 0" class="estado-tabla sin-datos">
            Sin análisis de ley registrados para este lote
          </div>

          <!-- Cards de laboratorios -->
          <div class="labs-grid">
            <div
              v-for="(a, i) in lote.analisis_ley"
              :key="a.id"
              class="lab-card"
              :class="{ descartado: !a.vigente }"
            >
              <div class="lab-card-header">
                <span class="lab-titulo">LABORATORIO {{ i + 1 }}</span>
                <button
                  v-if="a.vigente"
                  class="btn-edit-inline"
                  @click="irARegistrar(a.cip)"
                  title="Editar"
                >✎</button>
                <span v-else class="badge-estado pendiente" style="font-size:0.65rem">DESCARTADO</span>
              </div>

              <div class="lab-field"><span class="lf-label">LABORATORIO:</span>  <span class="lf-value">{{ a.laboratorio }}</span></div>
              <div class="lab-field"><span class="lf-label">FECHA ANÁLISIS:</span><span class="lf-value">{{ fmt(a.fecha_analisis) }}</span></div>
              <div class="lab-field"><span class="lf-label">MALLA +140:</span>    <span class="lf-value">{{ a.ley_grueso }}</span></div>
              <div class="lab-field"><span class="lf-label">MALLA -140:</span>    <span class="lf-value">{{ a.ley_fino }}</span></div>
              <div class="lab-field"><span class="lf-label">LEY AU OZ/TC:</span> <span class="lf-value highlight">{{ a.ley_final }}</span></div>
              <div class="lab-field"><span class="lf-label">TIPO:</span>         <span class="lf-value">{{ a.tipo_analisis }}</span></div>

              <!-- Checkbox de selección (vigente = seleccionado) -->
              <div class="lab-card-footer">
                <div
                  class="check-box"
                  :class="{ checked: a.vigente }"
                  @click="a.vigente && toggleDescartarLey(a.id)"
                  :title="a.vigente ? 'Clic para descartar' : 'Descartado'"
                >
                  <span v-if="a.vigente">✓</span>
                </div>
              </div>
            </div>

            <!-- Card vacía si tiene < 3 análisis: botón para agregar -->
            <div
              v-for="n in Math.max(0, 3 - lote.analisis_ley.length)"
              :key="'empty-' + n"
              class="lab-card lab-card-empty"
              @click="irARegistrarPorIP"
            >
              <div class="lab-card-header">
                <span class="lab-titulo">LABORATORIO {{ lote.analisis_ley.length + n }}</span>
              </div>
              <div class="lab-empty-msg">Sin datos</div>
              <button class="btn-secondary" style="margin-top:auto;font-size:0.75rem">+ Agregar</button>
            </div>
          </div>

          <!-- Acciones -->
          <div class="acciones-lote">
            <button class="btn-secondary" @click="solicitarRemuestreo">
              Solicitar remuestreo
            </button>
            <label class="btn-secondary" style="cursor:pointer">
              Adjuntar certificado
              <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="adjuntarCertLey" />
            </label>
          </div>

          <!-- Dirimencia badge -->
          <div v-if="lote.tiene_dirimencia" class="dirimencia-alert">
            ⚠️ Este lote tiene análisis de dirimencia — prevalece sobre todos los demás
          </div>
        </template>

        <!-- ── TAB: ANÁLISIS DE RECUPERACIÓN ────────────────────────────── -->
        <template v-if="tabActual === 'rec'">
          <div v-if="lote.analisis_recuperacion.length === 0" class="estado-tabla sin-datos">
            Sin análisis de recuperación registrados para este lote
          </div>

          <div class="labs-grid">
            <div
              v-for="(a, i) in lote.analisis_recuperacion"
              :key="a.id"
              class="lab-card"
              :class="{ descartado: !a.vigente }"
            >
              <div class="lab-card-header">
                <span class="lab-titulo">LABORATORIO {{ i + 1 }}</span>
                <button
                  v-if="a.vigente"
                  class="btn-edit-inline"
                  @click="irARegistrarRecuperacionCip(a.cip)"
                  title="Editar"
                >✎</button>
                <span v-else class="badge-estado pendiente" style="font-size:0.65rem">DESCARTADO</span>
              </div>

              <div class="lab-field"><span class="lf-label">LABORATORIO:</span>  <span class="lf-value">{{ a.laboratorio }}</span></div>
              <div class="lab-field"><span class="lf-label">FECHA ANÁLISIS:</span><span class="lf-value">{{ fmt(a.fecha_analisis) }}</span></div>
              <div class="lab-field"><span class="lf-label">LEY CABEZA:</span>   <span class="lf-value">{{ a.ley_cabeza }}</span></div>
              <div class="lab-field"><span class="lf-label">LEY COLA:</span>     <span class="lf-value">{{ a.ley_cola }}</span></div>
              <div class="lab-field"><span class="lf-label">RECUPERACIÓN:</span> <span class="lf-value highlight">{{ a.recuperacion != null ? a.recuperacion + '%' : '-' }}</span></div>

              <div class="lab-card-footer">
                <div
                  class="check-box"
                  :class="{ checked: a.vigente }"
                  @click="a.vigente && toggleDescartarRec(a.id)"
                  :title="a.vigente ? 'Clic para descartar' : 'Descartado'"
                >
                  <span v-if="a.vigente">✓</span>
                </div>
              </div>
            </div>

            <div
              v-for="n in Math.max(0, 2 - lote.analisis_recuperacion.length)"
              :key="'emp-rec-' + n"
              class="lab-card lab-card-empty"
              @click="irARegistrarRecuperacionPorIP"
            >
              <div class="lab-card-header">
                <span class="lab-titulo">LABORATORIO {{ lote.analisis_recuperacion.length + n }}</span>
              </div>
              <div class="lab-empty-msg">Sin datos</div>
              <button class="btn-secondary" style="margin-top:auto;font-size:0.75rem">+ Agregar</button>
            </div>
          </div>

          <!-- Acciones recuperación -->
          <div class="acciones-lote">
            <button class="btn-secondary" @click="calcularRecuperacion">
              Calcular Recuperación
            </button>
            <label class="btn-secondary" style="cursor:pointer">
              Adjuntar certificado
              <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="adjuntarCertRec" />
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
              <textarea class="field-input" v-model="justificacion" rows="3" placeholder="Ej: Resultado discordante con demás laboratorios"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="modalDescartar = null">Cancelar</button>
            <button class="btn-danger" @click="confirmarDescartar" :disabled="!justificacion.trim()">Confirmar descarte</button>
          </div>
        </div>
      </div>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, onMounted } from 'vue'
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
  const guardando = ref(false)
  const lote      = ref<LoteLabOut | null>(null)
  const tabActual = ref<'ley' | 'rec'>('ley')

  // Modal descartar
  const modalDescartar  = ref<{ id: number; tipo: 'ley' | 'rec' } | null>(null)
  const justificacion   = ref('')

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

  // ── Navegación ────────────────────────────────────────────────────────────────
  function irARegistrar(cip: string | null) {
    if (cip) router.push(`/laboratorio/ley/${cip}`)
  }
  function irARegistrarPorIP() {
    // Usa el primer CIP del lote para crear nuevo análisis
    const cip = lote.value?.cips[0]
    if (cip) router.push(`/laboratorio/ley/${cip}`)
  }
  function irARegistrarRecuperacionCip(cip: string | null) {
    if (cip) router.push(`/laboratorio/recuperacion/${cip}`)
  }
  function irARegistrarRecuperacionPorIP() {
    const cip = lote.value?.cips[0]
    if (cip) router.push(`/laboratorio/recuperacion/${cip}`)
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

    let ok: boolean
    if (tipo === 'ley') {
      ok = await store.descartarLey(id, j)
    } else {
      ok = await store.descartarRecuperacion(id, j)
    }

    if (ok) {
      modalDescartar.value = null
      lote.value = await store.cargarDetalleLote(ipActual)
    }
  }

  // ── Adjuntar certificado ──────────────────────────────────────────────────────
  async function adjuntarCertLey(e: Event) {
    const input = e.target as HTMLInputElement
    const file  = input.files?.[0]
    if (!file || !lote.value) return
    // Subir al primer análisis vigente de ley
    const a = lote.value.analisis_ley.find(x => x.vigente)
    if (!a) { ui.toast('No hay análisis vigente al que adjuntar', 'warning'); return }
    const ok = await store.subirCertificadoLey(a.id, file)
    if (ok) lote.value = await store.cargarDetalleLote(ipActual)
  }

  async function adjuntarCertRec(e: Event) {
    const input = e.target as HTMLInputElement
    const file  = input.files?.[0]
    if (!file || !lote.value) return
    const a = lote.value.analisis_recuperacion.find(x => x.vigente)
    if (!a) { ui.toast('No hay análisis vigente al que adjuntar', 'warning'); return }
    const ok = await store.subirCertificadoRecuperacion(a.id, file)
    if (ok) lote.value = await store.cargarDetalleLote(ipActual)
  }

  async function solicitarRemuestreo() {
    const ok = await ui.showConfirm({
      title:   'Solicitar Remuestreo',
      message: `¿Confirmar solicitud de remuestreo para el lote ${ipActual}?`,
    })
    if (ok) ui.toast('Remuestreo solicitado — avise al área de muestreo', 'info')
  }

  function calcularRecuperacion() {
    // Solo informativo en esta versión — los cálculos se hacen al registrar
    ui.toast('Los valores de recuperación se calculan automáticamente al guardar', 'info')
  }

  async function guardar() {
    ui.toast('Cambios guardados', 'success')
    router.push('/laboratorio')
  }
  </script>

  <style scoped>
  .detalle-row-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
  }

  @media (max-width: 800px) {
    .detalle-row-grid { grid-template-columns: 1fr 1fr; }
  }

  .detalle-item {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .di-label {
    font-size: 0.68rem;
    color: var(--color-text-faint);
    font-family: var(--font-mono);
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .di-value {
    font-size: var(--text-md);
    color: var(--color-text);
  }

  /* ── Lab cards ───────────────────────────────────────────── */
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
    gap: 0.55rem;
    background: rgba(255,255,255,0.02);
    transition: border-color 0.15s;
  }

  .lab-card:hover { border-color: var(--color-gold-dim, #8b7a3a); }

  .lab-card.descartado {
    opacity: 0.45;
    border-style: dashed;
  }

  .lab-card-empty {
    border-style: dashed;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    min-height: 200px;
    gap: 0.75rem;
  }

  .lab-card-empty:hover { border-color: var(--color-gold); }

  .lab-empty-msg {
    color: var(--color-text-faint);
    font-size: var(--text-sm);
  }

  .lab-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
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

  .btn-edit-inline {
    background: transparent;
    border: none;
    color: var(--color-text-faint);
    cursor: pointer;
    font-size: 1rem;
    line-height: 1;
    padding: 0;
  }

  .btn-edit-inline:hover { color: var(--color-gold); }

  .lab-field {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .lf-label {
    font-size: 0.68rem;
    color: var(--color-text-faint);
    font-family: var(--font-mono);
    letter-spacing: 0.05em;
  }

  .lf-value {
    font-family: var(--font-mono);
    color: var(--color-text-muted);
    font-size: var(--text-md);
  }

  .lf-value.highlight {
    color: var(--color-gold);
    font-size: var(--text-lg);
  }

  .lab-card-footer {
    display: flex;
    justify-content: center;
    margin-top: auto;
    padding-top: 0.5rem;
  }

  .check-box {
    width: 36px;
    height: 36px;
    border: 2px solid var(--color-border);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
    font-size: 1.1rem;
  }

  .check-box.checked {
    background: rgba(34, 197, 94, 0.15);
    border-color: #4ade80;
    color: #4ade80;
    cursor: pointer;
  }

  /* ── Acciones lote ───────────────────────────────────────── */
  .acciones-lote {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
    margin: 0.5rem 0 1.5rem;
  }

  .dirimencia-alert {
    background: rgba(168, 85, 247, 0.12);
    border: 1px solid rgba(168, 85, 247, 0.4);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    color: #c084fc;
    font-size: var(--text-sm);
    margin-top: 0.5rem;
  }
  </style>
