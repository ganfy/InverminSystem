<template>
    <div class="page-container">

      <header class="page-header">
        <div class="header-title-row">
          <Target class="header-icon" :size="26" />
          <div>
            <h1 class="page-title">Gestión de Campañas</h1>
            <p class="page-subtitle">Seguimiento de metas de oro fino por campaña</p>
          </div>
        </div>
      </header>

      <!-- Cargando -->
      <div v-if="store.cargando && !store.campanaActiva" class="estado-cargando">
        <span class="spinner-sm" /> Cargando campaña…
      </div>

      <!-- Sin campaña activa -->
      <div v-else-if="!store.campanaActiva" class="sin-campana">
        <p class="sin-campana-msg">No hay ninguna campaña activa.</p>
        <button v-if="puedeGestionar" class="btn-primary" @click="abrirModalNuevaCampana">
          <Plus :size="16" style="margin-right:0.4rem" /> Crear primera campaña
        </button>
      </div>

      <!-- Campaña activa -->
      <template v-else>
        <div class="campana-activa">

          <!-- Código y meta -->
          <div class="campana-header">
            <div>
              <span class="campana-codigo">{{ store.campanaActiva.codigo }}</span>
              <span class="campana-meta-badge">
                Meta: {{ fmtNum(store.campanaActiva.meta_oro_fino, 0) }} g
              </span>
            </div>
            <div class="campana-info-row">
              <span class="info-chip">
                <Calendar :size="12" /> Inicio: {{ fmtDate(store.campanaActiva.fecha_inicio) }}
              </span>
              <span class="info-chip">
                <Clock :size="12" /> {{ store.campanaActiva.dias_transcurridos ?? 0 }} días transcurridos
              </span>
              <span class="info-chip">
                <Layers :size="12" /> {{ store.campanaActiva.total_lotes }} lotes
              </span>
            </div>
          </div>

          <!-- Barra de progreso -->
          <div class="progreso-section">
            <div class="progreso-label-row">
              <span class="progreso-label">PROGRESO DE LA META</span>
              <span class="progreso-valores">
                ACUMULADO DE ORO FINO
                <strong class="progreso-num">{{ fmtNum(store.campanaActiva.oro_fino_acumulado, 2) }}</strong>
                / {{ fmtNum(store.campanaActiva.meta_oro_fino, 0) }} g
              </span>
            </div>
            <div class="barra-wrap">
              <div
                class="barra-fill"
                :style="{ width: Math.min(store.campanaActiva.progreso_pct, 100) + '%' }"
                :class="{
                  'barra-warn': store.campanaActiva.progreso_pct >= 95,
                  'barra-completa': store.campanaActiva.progreso_pct >= 100,
                }"
              />
              <span class="barra-pct">{{ store.campanaActiva.progreso_pct.toFixed(1) }}%</span>
            </div>
            <div v-if="store.campanaActiva.progreso_pct >= 95 && store.campanaActiva.progreso_pct < 100" class="alerta-meta">
              <AlertTriangle :size="13" style="vertical-align:middle;margin-right:4px" />
              Cerca del 95% — considera cerrar la campaña próximamente
            </div>
          </div>

          <!-- KPIs -->
          <div class="kpi-grid-campana">
            <div class="kpi-c">
              <div class="kpi-c-label">ORO FINO TOTAL</div>
              <div class="kpi-c-val">{{ fmtNum(store.campanaActiva.oro_fino_acumulado / 1000, 3) }} Kg</div>
            </div>
            <div class="kpi-c">
              <div class="kpi-c-label">LOTES PROCESADOS</div>
              <div class="kpi-c-val">{{ store.campanaActiva.total_lotes }}</div>
            </div>
            <div class="kpi-c">
              <div class="kpi-c-label">TONELADAS (TMS)</div>
              <div class="kpi-c-val">{{ fmtNum(store.campanaActiva.total_toneladas, 0) }}</div>
            </div>
            <div class="kpi-c">
              <div class="kpi-c-label">RUMAS CREADAS</div>
              <div class="kpi-c-val">{{ store.campanaActiva.total_rumas }}</div>
            </div>
          </div>

          <!-- Acciones -->
          <div v-if="puedeGestionar" class="campana-acciones">
            <button class="btn-secondary btn-sm" @click="abrirModalEditarMeta">
              <Pencil :size="14" style="margin-right:0.35rem" /> Editar meta
            </button>
            <button class="btn-danger btn-sm" @click="abrirModalCerrar">
              <FlagOff :size="14" style="margin-right:0.35rem" /> Finalizar y crear nueva campaña
            </button>
          </div>
        </div>

        <!-- Historial -->
        <div class="historial-section">
          <div class="hist-titulo">Historial de campañas</div>
          <div v-if="campanasCerradas.length === 0" class="estado-tabla">
            Sin campañas previas
          </div>
          <div
            v-for="c in campanasCerradas"
            :key="c.id"
            class="hist-card"
          >
            <div class="hist-card-top">
              <span class="hist-codigo">{{ c.codigo }}</span>
              <span class="hist-total">TOTAL AU ACUMULADO <strong>{{ fmtNum(c.oro_fino_acumulado, 2) }}g</strong></span>
            </div>
            <div class="hist-card-sub">
              Meta: {{ fmtNum(c.meta_oro_fino, 0) }}g
              · {{ fmtDate(c.fecha_inicio) }} – {{ fmtDate(c.fecha_cierre) }}
              · {{ c.dias_transcurridos ?? '—' }} días
              · {{ c.total_lotes }} lotes
            </div>
          </div>
        </div>
      </template>

      <div class="asignacion-rumas-section" style="margin-top: 2rem; border-top: 1px solid var(--color-border); padding-top: 1.5rem;">
        <div class="hist-titulo">Asignación de Rumas</div>
        <p class="text-sm text-muted mb-4">Selecciona rumas independientes para procesarlas en esta campaña.</p>
        
        <div class="rumas-grid">
          <div v-for="ruma in rumasDisponibles" :key="ruma.id" class="hist-card" style="display: flex; justify-content: space-between;">
            <div>
              <strong>{{ ruma.codigo }}</strong>
              <span class="text-xs text-muted" style="margin-left: 1rem;">
                {{ ruma.total_lotes }} lotes | {{ fmtNum(ruma.total_tms, 2) }} TM
              </span>
            </div>
            <button class="btn-primary btn-sm" @click="vincularRuma(ruma.id)">
              <Plus :size="14" style="margin-right:0.3rem"/> Añadir a Campaña
            </button>
          </div>
          
          <div v-if="rumasDisponibles.length === 0" class="text-muted text-sm">
            No hay rumas huérfanas disponibles para asignar.
          </div>
        </div>
      </div>

      <!-- Modal: Editar meta -->
      <Transition name="modal">
        <div v-if="modalMeta" class="modal-overlay" @click.self="modalMeta = false">
          <div class="modal modal-sm">
            <div class="modal-header">
              <div class="modal-title-group">
                <Pencil :size="16" />
                <h2>Editar meta de oro fino</h2>
              </div>
              <button class="modal-close" @click="modalMeta = false"><X :size="16" /></button>
            </div>
            <div class="modal-body">
              <div class="field">
                <label class="field-label">Meta (gramos)</label>
                <input
                  v-model.number="metaInput"
                  type="number" min="1" step="100"
                  class="field-input"
                  placeholder="ej: 5000"
                />
                <span class="field-hint">Valor actual: {{ fmtNum(store.campanaActiva?.meta_oro_fino, 0) }} g</span>
              </div>
              <p v-if="store.error" class="error-msg" style="margin-top:0.75rem">{{ store.error }}</p>
            </div>
            <div class="modal-footer">
              <div class="spacer" />
              <button class="btn-secondary" @click="modalMeta = false">Cancelar</button>
              <button class="btn-primary ready" :disabled="store.cargando || !metaInput || metaInput <= 0" @click="guardarMeta">
                <span v-if="store.cargando" class="spinner" />
                <span v-else>Guardar</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Modal: Cerrar campaña -->
      <Transition name="modal">
        <div v-if="modalCerrar" class="modal-overlay" @click.self="modalCerrar = false">
          <div class="modal modal-md">
            <div class="modal-header">
              <div class="modal-title-group">
                <FlagOff :size="16" />
                <h2>Finalizar campaña {{ store.campanaActiva?.codigo }}</h2>
              </div>
              <button class="modal-close" @click="modalCerrar = false"><X :size="16" /></button>
            </div>
            <div class="modal-body">
              <div class="cierre-resumen">
                <div class="cierre-item"><span>Oro fino acumulado</span><strong>{{ fmtNum(store.campanaActiva?.oro_fino_acumulado, 2) }} g</strong></div>
                <div class="cierre-item"><span>Lotes procesados</span><strong>{{ store.campanaActiva?.total_lotes }}</strong></div>
                <div class="cierre-item"><span>Rumas creadas</span><strong>{{ store.campanaActiva?.total_rumas }}</strong></div>
              </div>
              <div class="field" style="margin-top:1.25rem">
                <label class="field-label">Meta para la nueva campaña (gramos)</label>
                <input
                  v-model.number="metaNuevaCampana"
                  type="number" min="1" step="100"
                  class="field-input"
                  placeholder="ej: 5000"
                />
                <span class="field-hint">La nueva campaña se creará automáticamente al confirmar</span>
              </div>
              <p v-if="store.error" class="error-msg" style="margin-top:0.75rem">{{ store.error }}</p>
            </div>
            <div class="modal-footer">
              <div class="spacer" />
              <button class="btn-secondary" @click="modalCerrar = false">Cancelar</button>
              <button
                class="btn-danger"
                :disabled="store.cargando || !metaNuevaCampana || metaNuevaCampana <= 0"
                @click="confirmarCierre"
              >
                <span v-if="store.cargando" class="spinner" />
                <span v-else>Finalizar y crear nueva</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Modal: Nueva campaña (sin activa) -->
      <Transition name="modal">
        <div v-if="modalNueva" class="modal-overlay" @click.self="modalNueva = false">
          <div class="modal modal-sm">
            <div class="modal-header">
              <div class="modal-title-group">
                <Plus :size="16" />
                <h2>Nueva campaña</h2>
              </div>
              <button class="modal-close" @click="modalNueva = false"><X :size="16" /></button>
            </div>
            <div class="modal-body">
              <div class="field">
                <label class="field-label">Meta de oro fino (gramos)</label>
                <input
                  v-model.number="metaNuevaCampana"
                  type="number" min="1" step="100"
                  class="field-input"
                  placeholder="ej: 5000"
                />
              </div>
              <p v-if="store.error" class="error-msg" style="margin-top:0.75rem">{{ store.error }}</p>
            </div>
            <div class="modal-footer">
              <div class="spacer" />
              <button class="btn-secondary" @click="modalNueva = false">Cancelar</button>
              <button
                class="btn-primary ready"
                :disabled="store.cargando || !metaNuevaCampana || metaNuevaCampana <= 0"
                @click="crearNueva"
              >
                <span v-if="store.cargando" class="spinner" />
                <span v-else>Crear campaña</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { Calendar, Clock, Layers, Plus, Pencil, FlagOff, X, Target, AlertTriangle } from 'lucide-vue-next'
  import { useRumasStore } from '@/stores/rumas'
  import { useAuthStore } from '@/stores/auth'
  import { useUiStore } from '@/stores/ui'
  import * as api from '@/api/rumas'

  const store    = useRumasStore()
  const auth     = useAuthStore()
  const ui       = useUiStore()

  const modalMeta   = ref(false)
  const modalCerrar = ref(false)
  const modalNueva  = ref(false)
  const metaInput        = ref<number>(5000)
  const metaNuevaCampana = ref<number>(5000)

  const puedeGestionar = computed(() =>
    ['Admin', 'Gerencia'].includes(auth.user?.rol ?? '')
  )

  const campanasCerradas = computed(() =>
    store.historialCampanas.filter(c => c.estado === 'CERRADA')
      .sort((a, b) => b.id - a.id)
  )

  function fmtNum(v: number | null | undefined, dec = 2) {
    if (v == null) return '—'
    return new Intl.NumberFormat('es-PE', { minimumFractionDigits: dec, maximumFractionDigits: dec }).format(v)
  }
  function fmtDate(s: string | null | undefined) {
    if (!s) return '—'
    return new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  function abrirModalEditarMeta() {
    metaInput.value = store.campanaActiva?.meta_oro_fino ?? 5000
    modalMeta.value = true
  }
  function abrirModalCerrar() {
    metaNuevaCampana.value = store.campanaActiva?.meta_oro_fino ?? 5000
    modalCerrar.value = true
  }
  function abrirModalNuevaCampana() {
    metaNuevaCampana.value = 5000
    modalNueva.value = true
  }

 const rumasDisponibles = computed(() => {
  return store.rumas.filter(r => !r.asignada) 
})

async function vincularRuma(rumaId: number) {
  if (!store.campanaActiva) return
  const ok = await store.asignarRuma(store.campanaActiva.id, rumaId)
  if (ok) {
    ui.toast('Ruma añadida a la campaña exitosamente', 'success')
    await store.cargarCampanaActiva() // Refresca KPIs
  }
}

  async function guardarMeta() {
    if (!store.campanaActiva) return
    const ok = await store.editarMeta(store.campanaActiva.id, metaInput.value)
    if (ok) { modalMeta.value = false; ui.toast('Meta actualizada', 'success') }
  }

  async function confirmarCierre() {
    if (!store.campanaActiva) return
    const ok = await store.cerrarCampana(store.campanaActiva.id, metaNuevaCampana.value)
    if (ok) {
      modalCerrar.value = false
      ui.toast('Campaña cerrada. Nueva campaña creada.', 'success')
    }
  }

  async function crearNueva() {
    try {
      await api.crearCampana(metaNuevaCampana.value)
      await store.cargarCampanaActiva()
      await store.cargarHistorial()
      modalNueva.value = false
      ui.toast('Campaña creada', 'success')
    } catch (e: any) {
      ui.toast(e?.response?.data?.detail ?? 'Error al crear campaña', 'error')
    }
  }

  onMounted(async () => {
    await store.cargarCampanaActiva()
    await store.cargarHistorial()
    await store.cargarRumas()
  })
  </script>

  <style scoped>
  @import '@/assets/base.css';

  /* Campaña activa */
  .campana-activa {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
  }
  .campana-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
  .campana-codigo {
    font-family: var(--font-mono);
    font-size: var(--text-xl);
    color: var(--color-gold);
    letter-spacing: 0.08em;
    margin-right: 0.75rem;
  }
  .campana-meta-badge {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    background: var(--color-gold-bg);
    border: 1px solid rgba(179,144,40,0.2);
    border-radius: var(--radius-sm);
    padding: 0.15rem 0.6rem;
    vertical-align: middle;
  }
  .campana-info-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
  }
  .info-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  /* Progreso */
  .progreso-section { margin-bottom: 1.75rem; }
  .progreso-label-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 0.6rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .progreso-label {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.2em;
    color: var(--color-text-muted);
  }
  .progreso-valores {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }
  .progreso-num {
    font-size: var(--text-lg);
    color: var(--color-text);
    font-weight: 700;
    margin: 0 0.3rem;
  }
  .barra-wrap {
    position: relative;
    background: rgba(58,58,40,0.5);
    border-radius: 3px;
    height: 28px;
    overflow: hidden;
  }
  .barra-fill {
    height: 100%;
    background: var(--color-gold);
    border-radius: 3px;
    transition: width 0.6s ease;
  }
  .barra-fill.barra-warn    { background: var(--color-warning); }
  .barra-fill.barra-completa { background: var(--color-success); }
  .barra-pct {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    font-weight: 700;
    color: var(--color-bg);
    letter-spacing: 0.05em;
  }
  .alerta-meta {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-warning);
    margin-top: 0.5rem;
  }

  /* KPIs campaña */
  .kpi-grid-campana {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  @media (max-width: 700px) { .kpi-grid-campana { grid-template-columns: repeat(2,1fr); } }
  .kpi-c {
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 0.85rem 1rem;
    text-align: center;
  }
  .kpi-c-label {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.15em;
    color: var(--color-text-muted);
    margin-bottom: 0.4rem;
  }
  .kpi-c-val {
    font-family: var(--font-mono);
    font-size: var(--text-xl);
    color: var(--color-text);
    font-weight: 700;
  }

  /* Acciones */
  .campana-acciones {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    border-top: 1px solid var(--color-border);
    padding-top: 1rem;
  }
  .btn-sm {
    padding: 0.45rem 0.9rem !important;
    font-size: var(--text-sm) !important;
    min-height: 34px !important;
    display: inline-flex;
    align-items: center;
  }

  /* Sin campaña */
  .sin-campana {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
  }
  .sin-campana-msg { font-size: var(--text-lg); margin-bottom: 1.25rem; }

  /* Historial */
  .historial-section { margin-top: 0.5rem; }
  .hist-titulo {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    letter-spacing: 0.18em;
    color: var(--color-gold);
    margin-bottom: 0.75rem;
    text-transform: uppercase;
  }
  .hist-card {
    background: rgba(179,144,40,0.04);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 0.9rem 1.25rem;
    margin-bottom: 0.6rem;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
  }
  .hist-card-top { display: flex; align-items: center; gap: 1rem; }
  .hist-codigo {
    font-family: var(--font-mono);
    font-size: var(--text-base);
    color: var(--color-text-muted);
    letter-spacing: 0.06em;
  }
  .hist-total {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    letter-spacing: 0.08em;
  }
  .hist-total strong { color: var(--color-text); font-size: var(--text-base); }
  .hist-card-sub {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-dim);
    flex: 0 0 100%;
    margin-top: 0.2rem;
  }

  /* Cierre resumen */
  .cierre-resumen {
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 0.85rem 1rem;
  }
  .cierre-item {
    display: flex;
    justify-content: space-between;
    font-family: var(--font-mono);
    font-size: var(--text-md);
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(58,58,40,0.4);
    color: var(--color-text-muted);
  }
  .cierre-item:last-child { border-bottom: none; }
  .cierre-item strong { color: var(--color-text); }

  .estado-cargando {
    display: flex; gap: 0.5rem; align-items: center;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-md);
    padding: 2rem 0;
  }
  </style>
