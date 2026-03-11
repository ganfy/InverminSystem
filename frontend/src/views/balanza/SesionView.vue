<template>
  <div class="sesion-page" v-if="sesion">

    <!-- ── HEADER SESIÓN ────────────────────────────────────── -->
    <div class="sesion-header">
      <div class="header-meta">
        <div class="hm-row">
          <span class="hm-label">PROVEEDOR:</span>
          <span class="hm-val">{{ sesion.proveedor_razon_social }}</span>
        </div>
        <div class="hm-row">
          <span class="hm-label">PRODUCTO:</span>
          <select
            class="field-input select-producto"
            v-model="tipoMaterial"
            :disabled="sesion.estado !== 'EN_PROCESO'"
          >
            <option value="" disabled>— Tipo —</option>
            <option value="Mineral">Mineral</option>
            <option value="Llampo">Llampo</option>
            <option value="M.Llampo">M.Llampo</option>
          </select>
        </div>
        <div class="hm-row hm-row-sacos">
          <span class="hm-label">N° SACOS:</span>
          <input
            class="field-input input-sacos"
            type="number"
            min="0"
            v-model.number="sacos"
            placeholder="Ej: 99"
            :disabled="granel || sesion.estado !== 'EN_PROCESO'"
            @input="granel = false"
          />
          <label class="granel-toggle" :class="{ active: granel }">
            <input
              type="checkbox"
              v-model="granel"
              :disabled="sesion.estado !== 'EN_PROCESO'"
              @change="granel ? sacos = null : null"
            />
            Granel
          </label>
        </div>
      </div>

      <div class="header-badge" :class="estadoClass(sesion.estado)">
        <div class="badge-lote">LOTE {{ lotesActivos.length + (sesion.estado === 'EN_PROCESO' ? 1 : 0) }}</div>
        <div class="badge-estado-txt">{{ estadoLabel(sesion.estado) }}</div>
      </div>
    </div>

    <!-- ── CUERPO 2 COLUMNAS ──────────────────────────────── -->
    <div class="cuerpo">

      <!-- Columna izquierda: transporte + pesaje -->
      <div class="col-izq">

        <div class="card card-transporte">
          <h3 class="card-titulo">DATOS DEL TRANSPORTE</h3>
          <div class="transporte-datos">
            <div class="td-row">
              <span class="td-label">PLACA:</span>
              <span class="td-val mono">{{ sesion.placa }}</span>
              <template v-if="sesion.carreta">
                <span class="td-label" style="margin-left:1.25rem">CARRETA:</span>
                <span class="td-val mono">{{ sesion.carreta }}</span>
              </template>
            </div>
            <div v-if="sesion.conductor" class="td-row">
              <span class="td-label">CONDUCTOR:</span>
              <span class="td-val">{{ sesion.conductor }}</span>
            </div>
            <div v-if="sesion.transportista" class="td-row">
              <span class="td-label">TRANSPORTISTA:</span>
              <span class="td-val">{{ sesion.transportista }}</span>
            </div>
            <div v-if="sesion.razon_social" class="td-row">
              <span class="td-label">RAZÓN SOCIAL:</span>
              <span class="td-val">{{ sesion.razon_social }}</span>
            </div>
            <div v-if="sesion.guia_remision || sesion.guia_transporte" class="td-row">
              <template v-if="sesion.guia_remision">
                <span class="td-label">G. REM:</span>
                <span class="td-val mono">{{ sesion.guia_remision }}</span>
              </template>
              <template v-if="sesion.guia_transporte">
                <span class="td-label" style="margin-left:1.25rem">G. TRANSP:</span>
                <span class="td-val mono">{{ sesion.guia_transporte }}</span>
              </template>
            </div>
          </div>
        </div>

        <!-- Formulario pesaje — solo si EN_PROCESO -->
        <div v-if="sesion.estado === 'EN_PROCESO'" class="card card-pesaje">
          <div class="resumen-y-display">
            <div class="resumen">
              <span class="resumen-titulo">RESUMEN</span>
              <div class="resumen-row">
                <span>Peso inicial:</span>
                <span class="resumen-val">{{ loteForm.peso_inicial ? fmtTm(loteForm.peso_inicial / 1000) + ' TM' : '—' }}</span>
              </div>
              <div class="resumen-row">
                <span>Peso final:</span>
                <span class="resumen-val">{{ loteForm.peso_final ? fmtTm(loteForm.peso_final / 1000) + ' TM' : '—' }}</span>
              </div>
              <div class="resumen-row">
                <span>Peso neto:</span>
                <span class="resumen-val" :class="{ 'resumen-neto': pesoNeto > 0 }">
                  {{ pesoNeto > 0 ? fmtTm(pesoNeto / 1000) + ' TM' : '—' }}
                </span>
              </div>
            </div>

            <div class="balanza-display">
              <div class="balanza-label">PESO ACTUAL EN BALANZA</div>
              <input
                class="balanza-input"
                type="number" step="0.001" min="0"
                v-model.number="pesoActual"
                placeholder="0.000"
              />
              <span class="balanza-um">TM</span>
            </div>
          </div>

          <div class="pesos-grid">
            <div class="campo-fila-peso">
              <label class="campo-label-peso">BRUTO — camión cargado (kg)</label>
              <div class="peso-input-wrap">
                <input
                  class="field-input"
                  type="number" step="1" min="0"
                  v-model.number="loteForm.peso_inicial"
                  placeholder="Ej: 18750.000"
                />
                <button class="btn-capturar" type="button" @click="capturarBruto">↓ Capturar</button>
              </div>
            </div>
            <div class="campo-fila-peso">
              <label class="campo-label-peso">TARA — camión vacío (kg)</label>
              <div class="peso-input-wrap">
                <input
                  class="field-input"
                  type="number" step="1" min="0"
                  v-model.number="loteForm.peso_final"
                  placeholder="Ej: 12.500"
                />
                <button class="btn-capturar" type="button" @click="capturarTara">↓ Capturar</button>
              </div>
            </div>
          </div>

          <p v-if="pesoError" class="error-msg" style="margin-top:0.5rem;text-align:left">{{ pesoError }}</p>
          <p v-if="!tipoMaterial" class="error-msg" style="margin-top:0.5rem;text-align:left">
            Seleccione el tipo de producto en el encabezado
          </p>

          <button
            class="btn-registrar-lote"
            :disabled="store.guardando || !loteFormValido"
            @click="registrarLote"
          >
            <span v-if="store.guardando" class="spinner" />
            <span v-else>Capturar peso</span>
          </button>
        </div>
      </div>

      <!-- Columna derecha: lote cards -->
      <div class="col-der">
        <div
          v-for="lote in sesion.lotes"
          :key="lote.id"
          class="lote-card"
          :class="{
            'lote-card--completado': !lote.eliminado && lote.pesaje?.peso_final,
            'lote-card--proceso':    !lote.eliminado && !lote.pesaje?.peso_final,
            'lote-card--eliminado':   lote.eliminado,
          }"
        >
          <div class="lc-header">
            <span class="lc-ip">{{ lote.ip }} | Lote {{ lote.numero_lote }}</span>
            <div class="lc-header-right">
              <span class="lc-estado" :class="lote.eliminado ? 'lc-eliminado' : loteEstadoClass(lote)">
                {{ lote.eliminado ? 'Eliminado' : loteEstadoLabel(lote) }}
              </span>
              <button
                v-if="!lote.eliminado && sesion.estado === 'EN_PROCESO'"
                class="btn-icon btn-lc-menu"
                title="Eliminar lote"
                @click="abrirEliminar(lote)"
              >⋮</button>
            </div>
          </div>
          <div class="lc-pesos">
            <div class="lc-peso-row">
              <span class="lc-peso-label">PESO INICIAL:</span>
              <span class="lc-peso-val">
                {{ lote.pesaje ? fmtTm(lote.pesaje.peso_inicial / 1000) + ' TM' : '—' }}
              </span>
              <span class="lc-peso-label" style="margin-left:auto">PESO NETO:</span>
              <span class="lc-peso-neto">
                {{ lote.peso_neto != null ? fmtTm(lote.peso_neto) + ' TM' : '···' }}
              </span>
            </div>
            <div class="lc-peso-row">
              <span class="lc-peso-label">PESO FINAL:</span>
              <span class="lc-peso-val">
                {{ lote.pesaje?.peso_final ? fmtTm(lote.pesaje.peso_final / 1000) + ' TM' : '···' }}
              </span>
            </div>
          </div>
          <button
            v-if="!lote.eliminado && lote.pesaje?.peso_final"
            class="btn-ticket"
            @click="descargarTicket(lote)"
          >🖨 Descargar ticket</button>
        </div>

        <div v-if="sesion.lotes.length === 0" class="sin-lotes">
          Aún no hay lotes registrados
        </div>
      </div>
    </div>

    <!-- ── BARRA INFERIOR ─────────────────────────────────── -->
    <div class="bottom-bar">
      <button class="btn-secondary btn-volver" @click="router.push({ name: 'Balanza' })">
        ← Volver
      </button>
      <div class="bottom-bar-right">
        <button
          v-if="sesion.estado === 'EN_PROCESO'" class="btn-secondary"
          :disabled="store.guardando" @click="pausar"
        >⏸ Pausar</button>
        <button
          v-if="sesion.estado === 'PAUSADO'" class="btn-secondary"
          :disabled="store.guardando" @click="reanudar"
        >▶ Reanudar</button>
        <button
          v-if="sesion.estado !== 'COMPLETO'"
          class="btn-primary ready"
          :disabled="store.guardando || lotesActivos.length === 0"
          @click="finalizar"
        >
          <span v-if="store.guardando" class="spinner" />
          <span v-else>Finalizar y generar tickets →</span>
        </button>
      </div>
    </div>
  </div>

  <div v-else class="loading-state">
    {{ store.loadingSesion ? 'Cargando sesión...' : '' }}
  </div>

  <!-- Modal eliminar lote -->
  <div v-if="eliminarModal.visible" class="modal-overlay" @click.self="cerrarEliminar">
    <div class="modal modal-sm">
      <div class="modal-header">
        <h2>Eliminar {{ eliminarModal.ip }}</h2>
        <button class="btn-cerrar" @click="cerrarEliminar">✕</button>
      </div>
      <div class="modal-body">
        <p class="elim-aviso">Acción irreversible — queda registrado en auditoría.</p>
        <div class="field" style="margin-top:0.75rem">
          <label class="field-label">Motivo *</label>
          <textarea class="field-input" rows="3" v-model="eliminarModal.motivo" placeholder="Describa el motivo..." />
        </div>
        <p v-if="eliminarModal.error" class="error-msg">{{ eliminarModal.error }}</p>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" @click="cerrarEliminar">Cancelar</button>
        <button class="btn-danger" :disabled="store.guardando" @click="confirmarEliminar">
          <span v-if="store.guardando" class="spinner" />
          <span v-else>Eliminar</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBalanzaStore } from '@/stores/balanza'
import { useUiStore } from '@/stores/ui'
import type { LoteDetalle } from '@/api/balanza'

const route  = useRoute()
const router = useRouter()
const store  = useBalanzaStore()
const ui     = useUiStore()

const sesionId = Number(route.params.id)
const sesion   = computed(() => store.sesionActual)
const lotesActivos = computed(() => sesion.value?.lotes.filter(l => !l.eliminado) ?? [])

// ── Tipo material — global para todos los lotes ────────────
const tipoMaterial = ref('')

// ── Sacos / Granel — mutuamente excluyentes ────────────────
const sacos  = ref<number | null>(null)
const granel = ref(false)

// ── Balanza manual ─────────────────────────────────────────
const pesoActual = ref<number | null>(null)

function capturarTara()  { if (pesoActual.value !== null) loteForm.peso_final = pesoActual.value * 1000 }
function capturarBruto() { if (pesoActual.value !== null) loteForm.peso_inicial   = pesoActual.value * 1000 }

// ── Formulario lote ────────────────────────────────────────
const loteForm = reactive({
  peso_inicial: null as number | null,
  peso_final:   null as number | null,
})

const pesoError = computed(() => {
  const { peso_inicial: i, peso_final: f } = loteForm
  if (i !== null && f !== null && i > 0 && f > 0 && f >= i) return 'El bruto debe superar la tara'
  return ''
})

const pesoNeto = computed(() => {
  const { peso_inicial: i, peso_final: f } = loteForm
  return (i !== null && f !== null && f > i) ? f - i : 0
})

const loteFormValido = computed(() =>
  !!tipoMaterial.value &&
  (loteForm.peso_inicial ?? 0) > 0 &&
  (loteForm.peso_final   ?? 0) > 0 &&
  loteForm.peso_final! > loteForm.peso_inicial! &&
  !pesoError.value
)

async function registrarLote() {
  if (!loteFormValido.value) return
  const ok = await store.agregarLote(sesionId, {
    tipo_material: tipoMaterial.value,
    pesaje: {
      peso_inicial: loteForm.peso_inicial!,
      peso_final:   loteForm.peso_final!,
      sacos:        granel.value ? null : (sacos.value || null),
      granel:       granel.value,
    },
  })
  if (ok) { loteForm.peso_inicial = null; loteForm.peso_final = null }
}

// ── Sesión ─────────────────────────────────────────────────
async function pausar() {
  const ok = await ui.showConfirm({ title: 'Pausar sesión', message: '¿Pausar? Podrá reanudarla.', confirmLabel: 'Pausar' })
  if (ok) await store.pausarSesion(sesionId)
}
async function reanudar() { await store.reanudarSesion(sesionId) }
async function finalizar() {
  const ok = await ui.showConfirm({
    title: 'Finalizar sesión',
    message: `¿Finalizar con ${lotesActivos.value.length} lotes? Se generarán los tickets.`,
    confirmLabel: 'Finalizar y generar tickets',
  })
  if (ok) await store.finalizarSesion(sesionId)
}

async function descargarTicket(lote: LoteDetalle) {
  await store.descargarTicket(sesionId, lote.id, lote.ip)
}

// ── Modal eliminar ─────────────────────────────────────────
const eliminarModal = reactive({ visible: false, loteId: 0, ip: '', motivo: '', error: '' })

function abrirEliminar(lote: LoteDetalle) {
  Object.assign(eliminarModal, { visible: true, loteId: lote.id, ip: lote.ip, motivo: '', error: '' })
}
function cerrarEliminar() { eliminarModal.visible = false }

async function confirmarEliminar() {
  if (!eliminarModal.motivo.trim()) { eliminarModal.error = 'Motivo obligatorio'; return }
  const ok = await store.eliminarLote(sesionId, eliminarModal.loteId, eliminarModal.motivo.trim())
  if (ok) cerrarEliminar()
}

// ── Helpers ────────────────────────────────────────────────
function fmtTm(n: number) { return Number(n).toFixed(3) }
function estadoClass(e: string) {
  return { EN_PROCESO: 'badge-en-proceso', PAUSADO: 'badge-pausado', COMPLETO: 'badge-completo' }[e] ?? ''
}
function estadoLabel(e: string) {
  return { EN_PROCESO: 'EN PROCESO', PAUSADO: 'PAUSADO', COMPLETO: 'COMPLETO' }[e] ?? e
}
function loteEstadoClass(lote: LoteDetalle) { return lote.pesaje?.peso_final ? 'lc-completado' : 'lc-en-proceso' }
function loteEstadoLabel(lote: LoteDetalle) { return lote.pesaje?.peso_final ? 'Completado' : 'En proceso' }

onMounted(() => store.cargarSesion(sesionId))
</script>

<style scoped>
.sesion-page  { display: flex; flex-direction: column; gap: 1.25rem; }
.loading-state { padding: 3rem; text-align: center; color: var(--color-text-muted); font-family: var(--font-mono); }

/* ── Header ───────────────────────────────────────────────── */
.sesion-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  padding: 1rem 1.5rem; gap: 1.5rem;
}
.header-meta { display: flex; flex-wrap: wrap; gap: 0.75rem 2rem; align-items: center; flex: 1; }
.hm-row      { display: flex; align-items: center; gap: 0.6rem; }
.hm-label    { font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.1em; color: var(--color-text-muted); white-space: nowrap; }
.hm-val      { font-weight: 600; color: var(--color-text); }
.hm-row-sacos { gap: 0.75rem; }

.select-producto { width: auto; min-width: 130px; padding: 0.35rem 0.6rem; font-size: 0.9rem; }
.input-sacos     { width: 90px; padding: 0.35rem 0.6rem; font-size: 0.9rem; }

.granel-toggle {
  display: flex; align-items: center; gap: 0.4rem; cursor: pointer;
  font-family: var(--font-mono); font-size: 0.8rem; color: var(--color-text-muted);
  transition: color 0.15s; user-select: none;
}
.granel-toggle.active { color: var(--color-gold); }
.granel-toggle input  { accent-color: var(--color-gold); }

.header-badge {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 0.65rem 1.25rem; border-radius: var(--radius-sm);
  min-width: 160px; border: 1px solid currentColor; flex-shrink: 0;
}
.badge-en-proceso { color: #38bdf8; background: rgba(14,165,233,0.08); border-color: rgba(14,165,233,0.3); }
.badge-pausado    { color: #c084fc; background: rgba(168,85,247,0.08);  border-color: rgba(168,85,247,0.3); }
.badge-completo   { color: #4ade80; background: rgba(34,197,94,0.08);   border-color: rgba(34,197,94,0.3); }
.badge-lote       { font-family: var(--font-mono); font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; }
.badge-estado-txt { font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.12em; margin-top: 0.2rem; opacity: 0.8; }

/* ── Cuerpo ───────────────────────────────────────────────── */
.cuerpo { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; align-items: start; }
@media (max-width: 920px) { .cuerpo { grid-template-columns: 1fr; } }

/* ── Cards ────────────────────────────────────────────────── */
.card { background: var(--color-bg-card); border: 1px solid var(--color-border); border-radius: var(--radius-md); padding: 1.25rem 1.5rem; }
.col-izq { display: flex; flex-direction: column; gap: 1rem; }
.card-titulo { font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.15em; color: var(--color-gold); margin-bottom: 1rem; }

/* Datos transporte */
.transporte-datos { display: flex; flex-direction: column; gap: 0.5rem; }
.td-row   { display: flex; align-items: baseline; gap: 0.5rem; flex-wrap: wrap; }
.td-label { font-family: var(--font-mono); font-size: 0.7rem; letter-spacing: 0.08em; color: var(--color-text-muted); }
.td-val   { font-family: var(--font-mono); font-size: 0.85rem; color: var(--color-text); }
.mono     { font-family: var(--font-mono); }

/* Pesaje */
.resumen-y-display { display: flex; gap: 1.25rem; align-items: flex-start; margin-bottom: 1rem; }
.resumen           { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; }
.resumen-titulo    { font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.14em; color: var(--color-text-muted); margin-bottom: 0.2rem; }
.resumen-row       { display: flex; justify-content: space-between; font-family: var(--font-mono); font-size: 0.78rem; color: var(--color-text-muted); }
.resumen-val       { color: var(--color-text); }
.resumen-neto      { color: #4ade80; font-weight: 700; }

.balanza-display {
  background: var(--color-bg); border: 1px solid var(--color-border-focus);
  border-radius: var(--radius-sm); padding: 0.75rem 1rem;
  display: flex; flex-direction: column; align-items: center; min-width: 130px;
}
.balanza-label { font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.1em; color: var(--color-text-muted); margin-bottom: 0.4rem; text-align: center; }
.balanza-input {
  background: transparent; border: none; outline: none;
  font-family: var(--font-mono); font-size: 1.5rem; font-weight: 700; color: var(--color-gold);
  width: 100%; text-align: center; -moz-appearance: textfield;
}
.balanza-input::-webkit-outer-spin-button, .balanza-input::-webkit-inner-spin-button { -webkit-appearance: none; }
.balanza-um { font-family: var(--font-mono); font-size: 0.75rem; color: var(--color-text-muted); }

.pesos-grid       { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 0.75rem; }
.campo-fila-peso  { display: flex; flex-direction: column; gap: 0.35rem; }
.campo-label-peso { font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.08em; color: var(--color-text-muted); }
.peso-input-wrap  { display: flex; gap: 0.4rem; align-items: center; }
.peso-input-wrap .field-input { flex: 1; }

.btn-capturar {
  background: var(--color-gold-bg); border: 1px solid var(--color-border-focus);
  border-radius: var(--radius-sm); color: var(--color-gold);
  font-family: var(--font-mono); font-size: 0.7rem; letter-spacing: 0.06em;
  cursor: pointer; padding: 0.4rem 0.5rem; white-space: nowrap; transition: background 0.15s;
}
.btn-capturar:hover { background: rgba(184,150,46,0.2); }

.btn-registrar-lote {
  width: 100%; padding: 0.9rem; background: var(--color-gold);
  border: none; border-radius: var(--radius-sm); color: var(--color-bg);
  font-family: var(--font-main); font-size: 1rem; font-weight: 700; letter-spacing: 0.15em;
  cursor: pointer; transition: background 0.2s;
  display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-top: 0.5rem;
}
.btn-registrar-lote:hover:not(:disabled) { background: var(--color-gold-light); }
.btn-registrar-lote:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Lote cards ───────────────────────────────────────────── */
.col-der { display: flex; flex-direction: column; gap: 0.75rem; }

.lote-card {
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); padding: 1rem 1.25rem; transition: border-color 0.2s;
}
.lote-card--completado { border-left: 3px solid #4ade80; }
.lote-card--proceso    { border-left: 3px solid #38bdf8; }
.lote-card--eliminado  { opacity: 0.4; }

.lc-header       { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; }
.lc-ip           { font-family: var(--font-mono); font-size: 0.85rem; color: var(--color-gold); font-weight: 600; }
.lc-header-right { display: flex; align-items: center; gap: 0.5rem; }

.lc-estado     { font-family: var(--font-mono); font-size: 0.7rem; letter-spacing: 0.08em; padding: 2px 8px; border-radius: 3px; }
.lc-completado { background: rgba(34,197,94,0.15);  color: #4ade80; }
.lc-en-proceso { background: rgba(14,165,233,0.15); color: #38bdf8; }
.lc-eliminado  { background: rgba(107,114,128,0.2); color: #9ca3af; }

.btn-lc-menu { width: 24px !important; height: 24px !important; font-size: 1rem !important; }

.lc-pesos    { display: flex; flex-direction: column; gap: 0.3rem; }
.lc-peso-row { display: flex; align-items: baseline; gap: 0.5rem; font-family: var(--font-mono); font-size: 0.78rem; }
.lc-peso-label { color: var(--color-text-muted); }
.lc-peso-val   { color: var(--color-text); }
.lc-peso-neto  { color: #4ade80; font-weight: 700; font-size: 0.95rem; margin-left: auto; }

.btn-ticket {
  margin-top: 0.6rem; background: none;
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  color: var(--color-text-muted); font-family: var(--font-mono); font-size: 0.72rem;
  letter-spacing: 0.06em; cursor: pointer; padding: 0.3rem 0.6rem;
  transition: border-color 0.15s, color 0.15s;
}
.btn-ticket:hover { border-color: var(--color-gold); color: var(--color-gold); }

.sin-lotes {
  text-align: center; padding: 2.5rem 1rem; color: var(--color-text-muted);
  font-family: var(--font-mono); font-size: 0.85rem;
  border: 1px dashed var(--color-border); border-radius: var(--radius-md);
}

/* ── Barra inferior ───────────────────────────────────────── */
.bottom-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 1.25rem; border-top: 1px solid var(--color-border);
  gap: 1rem; margin-top: 0.5rem;
}
.bottom-bar-right { display: flex; gap: 0.75rem; align-items: center; }
.btn-volver { min-width: 130px; }

/* ── Modal eliminar ───────────────────────────────────────── */
.elim-aviso {
  color: var(--color-warning); font-size: 0.83rem; line-height: 1.5;
  padding: 0.5rem 0.75rem; border-left: 2px solid var(--color-warning);
  background: rgba(207,151,61,0.06);
}
.btn-danger {
  padding: 0.65rem 1.25rem; background: transparent;
  border: 1px solid var(--color-error); border-radius: var(--radius-sm);
  color: var(--color-error); font-family: var(--font-main); font-size: 0.85rem;
  font-weight: 700; letter-spacing: 0.1em; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  min-height: 38px; text-transform: uppercase; transition: background 0.2s;
}
.btn-danger:hover:not(:disabled) { background: rgba(165,71,61,0.15); }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
