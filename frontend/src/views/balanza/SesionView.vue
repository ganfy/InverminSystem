<template>
  <div class="sesion-page">

    <!-- ── ENCABEZADO ──────────────────────────────────────── -->
    <div class="sesion-header">
      <div class="header-info">
        <div class="header-campo">
          <span class="header-label">PROVEEDOR:</span>
          <span class="header-valor">{{ sesion?.proveedor_razon_social ?? '—' }}</span>
        </div>
        <div class="header-campo">
          <span class="header-label">ACOPIADOR:</span>
          <span class="header-valor">
            {{ sesion?.es_propio ? '(auto-acopio)' : (sesion?.acopiador_razon_social ?? '—') }}
          </span>
        </div>
        <div class="header-campo">
          <span class="header-label">PRODUCTO:</span>
          <select
            v-if="sesion?.estado === 'EN_PROCESO'"
            class="field-input header-select"
            v-model="tipoMaterial"
          >
            <option value="">— seleccionar —</option>
            <option value="Mineral">Mineral</option>
            <option value="Llampo">Llampo</option>
            <option value="M.Llampo">M.Llampo</option>
          </select>
          <span v-else class="header-valor">{{ tipoMaterial || '—' }}</span>
        </div>
        <div v-if="sesion?.estado === 'EN_PROCESO'" class="header-campo">
          <span class="header-label">N° SACOS:</span>
          <input
            class="field-input header-sacos"
            type="number" min="0"
            v-model.number="sacos"
            placeholder="Ej: 99"
            :disabled="granel"
            @input="granel = false"
          />
          <label class="granel-label">
            <input type="checkbox" v-model="granel" @change="sacos = null" />
            Granel
          </label>
        </div>
      </div>

      <div class="header-right">
        <div class="lote-badge" :class="estadoClass(sesion?.estado ?? '')">
          <template v-if="lotesActivos.length > 0">
            LOTE {{ lotesActivos.length }} DE {{ sesion?.lotes.filter(l=>!l.eliminado).length }}
          </template>
          <template v-else>SIN LOTES</template>
          <br />{{ estadoLabel(sesion?.estado ?? '') }}
        </div>
        <button
          v-if="sesion?.estado !== 'COMPLETO'"
          class="btn-secondary btn-editar-sesion"
          @click="abrirEditarSesion"
        >✎ Editar sesión</button>
      </div>
    </div>

    <!-- ── CUERPO 2 COLUMNAS ──────────────────────────────── -->
    <div class="sesion-body">

      <!-- Columna izquierda -->
      <div class="col-left">

        <!-- Datos de transporte -->
        <div class="card">
          <div class="card-titulo">DATOS DEL TRANSPORTE</div>
          <div class="transp-grid">
            <div class="transp-fila">
              <span class="transp-label">PLACA:</span>
              <span class="transp-val">{{ sesion?.placa ?? '—' }}</span>
            </div>
            <div class="transp-fila">
              <span class="transp-label">CARRETA:</span>
              <span class="transp-val">{{ sesion?.carreta || '—' }}</span>
            </div>
            <div class="transp-fila transp-full">
              <span class="transp-label">CONDUCTOR:</span>
              <span class="transp-val">{{ sesion?.conductor || '—' }}</span>
            </div>
            <div class="transp-fila transp-full">
              <span class="transp-label">TRANSPORTISTA:</span>
              <span class="transp-val">{{ sesion?.transportista || '—' }}</span>
            </div>
            <div class="transp-fila transp-full">
              <span class="transp-label">RAZÓN SOCIAL:</span>
              <span class="transp-val">{{ sesion?.razon_social || '—' }}</span>
            </div>
            <div class="transp-fila">
              <span class="transp-label">G. REM:</span>
              <span class="transp-val td-mono">{{ sesion?.guia_remision || '—' }}</span>
            </div>
            <div class="transp-fila">
              <span class="transp-label">G. TRANSP:</span>
              <span class="transp-val td-mono">{{ sesion?.guia_transporte || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- Pesaje activo (solo EN_PROCESO) -->
        <div v-if="sesion?.estado === 'EN_PROCESO'" class="card card-pesaje">
          <div class="card-titulo">PESAJE — NUEVO LOTE</div>

          <div class="pesaje-display">
            <div class="peso-display-label">PESO ACTUAL EN BALANZA</div>
            <input
              class="peso-display-input"
              min="0"
              v-model.number="pesoActual"
              placeholder="0.000"
            />
            <span class="peso-display-unit">TM</span>
          </div>

          <div class="pesaje-campos">
            <!-- BRUTO = peso_inicial (primer pesaje, camión cargado) -->
            <div class="campo-peso">
              <label class="campo-peso-label">BRUTO (camión cargado)</label>
              <div class="campo-peso-row">
                <input
                  class="field-input"
                  type="number" step="0.001" min="0"
                  v-model.number="loteForm.peso_inicial"
                  placeholder="TM"
                />
                <button class="btn-capturar" title="Capturar peso actual como BRUTO" @click="capturarBruto">
                  ↓ Capturar
                </button>
              </div>
            </div>
            <!-- TARA = peso_final (segundo pesaje, camión vacío) -->
            <div class="campo-peso">
              <label class="campo-peso-label">TARA (camión vacío)</label>
              <div class="campo-peso-row">
                <input
                  class="field-input"
                  type="number" step="0.001" min="0"
                  v-model.number="loteForm.peso_final"
                  placeholder="TM"
                />
                <button class="btn-capturar" title="Capturar peso actual como TARA" @click="capturarTara">
                  ↓ Capturar
                </button>
              </div>
            </div>
          </div>

          <p v-if="pesoError" class="error-msg" style="margin:.25rem 0">{{ pesoError }}</p>

          <div class="pesaje-resumen">
            <span>BRUTO: <strong>{{ loteForm.peso_inicial ? fmtTm(loteForm.peso_inicial) + ' TM' : '—' }}</strong></span>
            <span>TARA: <strong>{{ loteForm.peso_final ? fmtTm(loteForm.peso_final) + ' TM' : '—' }}</strong></span>
            <span class="neto-resumen">NETO: <strong>{{ pesoNeto > 0 ? fmtTm(pesoNeto) + ' TM' : '—' }}</strong></span>
          </div>

          <!-- Mensaje de validación (aparece solo al intentar con errores) -->
          <div v-if="mostrarFaltantes && loteFormFaltantes.length > 0" class="form-faltantes">
            <span class="faltante-icono">⚠</span>
            Falta: {{ loteFormFaltantes.join(' · ') }}
          </div>

          <button
            class="btn-primary ready btn-registrar"
            :class="{ 'btn-incompleto': !loteFormValido && mostrarFaltantes }"
            :disabled="store.guardando"
            @click="intentarRegistrar"
          >
            <span v-if="store.guardando" class="spinner" />
            <span v-else>Capturar peso</span>
          </button>
        </div>

      </div><!-- /col-left -->

      <!-- Columna derecha: lista de lotes -->
      <div class="col-right">
        <div v-if="store.loadingSesion" class="estado-tabla">Cargando...</div>

        <div
          v-for="lote in sesion?.lotes.filter(l => !l.eliminado)"
          :key="lote.id"
          class="lote-card"
          :class="{ 'lote-en-proceso': !lote.pesaje?.peso_final }"
        >
          <div class="lote-card-header">
            <span class="lote-ip">{{ lote.ip }} | Lote {{ lote.numero_lote }}</span>
            <div class="lote-acciones">
              <button
                v-if="authStore.user?.rol === 'Admin'"
                class="btn-icon" title="Editar lote"
                @click="abrirEditarLote(lote)"
              >✎</button>
              <button
                class="btn-icon btn-icon-danger" title="Eliminar lote"
                @click="abrirEliminar(lote)"
              >✕</button>
              <span class="badge-lote-estado" :class="loteEstadoClass(lote)">
                {{ loteEstadoLabel(lote) }}
              </span>
            </div>
          </div>

          <div class="lote-card-body">
            <div class="lote-fila">
              <span class="lote-dato-label">BRUTO:</span>
              <span class="lote-dato-val">
                {{ lote.pesaje?.peso_inicial != null ? fmtTm(lote.pesaje.peso_inicial) + ' TM' : '…' }}
              </span>
            </div>
            <div class="lote-fila">
              <span class="lote-dato-label">TARA:</span>
              <span class="lote-dato-val">
                {{ lote.pesaje?.peso_final != null ? fmtTm(lote.pesaje.peso_final) + ' TM' : '…' }}
              </span>
            </div>
            <div class="lote-fila lote-neto">
              <span class="lote-dato-label">NETO:</span>
              <span class="lote-dato-val neto-val">
                {{ lote.peso_neto != null ? fmtTm(lote.peso_neto) + ' TM' : '…' }}
              </span>
            </div>
            <div v-if="lote.pesaje?.sacos" class="lote-fila">
              <span class="lote-dato-label">SACOS:</span>
              <span class="lote-dato-val">{{ lote.pesaje.sacos }}</span>
            </div>
            <div v-if="lote.pesaje?.granel" class="lote-fila">
              <span class="badge-propio">Granel</span>
            </div>
          </div>

          <div class="lote-card-footer">
          <button class="btn-secondary btn-sm" @click="verTicket(lote)" title="Ver antes de imprimir">
            👁 Ver ticket
          </button>
          <button class="btn-secondary btn-sm" @click="descargarTicket(lote)" title="Descargar PDF">
            ⬇ PDF
          </button>
        </div>
        </div>

        <!-- Lotes eliminados -->
        <details v-if="sesion?.lotes.some(l => l.eliminado)" class="lotes-eliminados">
          <summary>{{ sesion?.lotes.filter(l=>l.eliminado).length }} lote(s) eliminado(s)</summary>
          <div
            v-for="lote in sesion?.lotes.filter(l => l.eliminado)"
            :key="lote.id"
            class="lote-card lote-eliminado"
          >
            <div class="lote-card-header">
              <span class="lote-ip">{{ lote.ip }} | Lote {{ lote.numero_lote }}</span>
              <span class="badge-lote-estado badge-eliminado">ELIMINADO</span>
            </div>
          </div>
        </details>

      </div><!-- /col-right -->
    </div><!-- /sesion-body -->

    <!-- ── BARRA INFERIOR ─────────────────────────────────── -->
    <div class="bottom-bar">
      <button class="btn-secondary" @click="router.push({ name: 'Balanza' })">← Volver</button>
      <div class="bottom-bar-acciones">
        <!-- Botón: descargar todos los tickets (visible si hay al menos 1 lote) -->
        <button
        v-if="lotesActivos.length > 0"
        class="btn-secondary"
        :disabled="descargandoTodos"
        @click="descargarTodos"
        title="Genera un PDF con los tickets de todos los lotes para entregar al transportista"
        >
        <span v-if="descargandoTodos" class="spinner" />
        <span v-else>🖨 Tickets sesión</span>
        </button>
        <button v-if="sesion?.estado === 'EN_PROCESO'" class="btn-secondary" @click="pausar">
          ⏸ Pausar
        </button>
        <button v-if="sesion?.estado === 'PAUSADO'" class="btn-secondary" @click="reanudar">
          ▶ Reanudar
        </button>
        <button
          v-if="sesion?.estado !== 'COMPLETO'"
          class="btn-primary ready"
          :disabled="store.guardando || lotesActivos.length === 0"
          @click="finalizar"
        >
          <span v-if="store.guardando" class="spinner" />
          <span v-else>Finalizar y generar tickets →</span>
        </button>
      </div>
    </div>

    <!-- ── MODAL: Editar Sesión ───────────────────────────── -->
    <div v-if="editSesionModal.visible" class="modal-overlay" @click.self="cerrarEditarSesion">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h2>EDITAR SESIÓN</h2>
          <button class="btn-cerrar" @click="cerrarEditarSesion">✕</button>
        </div>
        <div class="modal-body">
          <div class="seccion-edit">
            <div class="seccion-edit-titulo">PROVEEDOR Y ACOPIADOR</div>
            <div class="form-grid">
              <div class="field field-full">
                <label class="field-label">Proveedor (buscar)</label>
                <div class="autocomplete-wrap">
                  <input
                    class="field-input"
                    v-model="editSesionModal.busqProv"
                    placeholder="Buscar proveedor..."
                    @input="editSesionModal.editProv = null; editSesionModal.editAcop = null; editSesionModal.dropProv = true"
                    @focus="editSesionModal.dropProv = true"
                    @blur="globalSetTimeout(() => editSesionModal.dropProv = false, 150)"
                    autocomplete="off"
                  />
                  <div v-if="editSesionModal.dropProv && editProvsFiltered.length" class="ac-dropdown">
                    <div
                      v-for="p in editProvsFiltered" :key="p.proveedor_id"
                      class="ac-item"
                      @mousedown.prevent="editSelProv(p)"
                    >{{ p.proveedor_razon_social }}</div>
                  </div>
                </div>
              </div>
              <div class="field field-full">
                <label class="field-label">Acopiador</label>
                <div class="autocomplete-wrap">
                  <input
                    class="field-input"
                    :class="{ 'field-disabled': !editSesionModal.editProv }"
                    v-model="editSesionModal.busqAcop"
                    :disabled="!editSesionModal.editProv"
                    placeholder="Seleccione proveedor primero"
                    @focus="editSesionModal.dropAcop = true"
                    @blur="globalSetTimeout(() => editSesionModal.dropAcop = false, 150)"
                    autocomplete="off"
                  />
                  <div v-if="editSesionModal.dropAcop && editAcopsFiltered.length" class="ac-dropdown">
                    <div
                      v-for="a in editAcopsFiltered" :key="a.provacop_id"
                      class="ac-item"
                      @mousedown.prevent="editSelAcop(a)"
                    >{{ a.acopiador_razon_social }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="seccion-edit">
            <div class="seccion-edit-titulo">DATOS DE TRANSPORTE</div>
            <div class="form-grid">
              <div class="field">
                <label class="field-label">Placa</label>
                <input class="field-input" v-model="editSesionModal.form.placa" style="text-transform:uppercase" />
              </div>
              <div class="field">
                <label class="field-label">Carreta</label>
                <input class="field-input" v-model="editSesionModal.form.carreta" />
              </div>
              <div class="field field-full">
                <label class="field-label">Conductor</label>
                <input class="field-input" v-model="editSesionModal.form.conductor" />
              </div>
              <div class="field field-full">
                <label class="field-label">Transportista</label>
                <input class="field-input" v-model="editSesionModal.form.transportista" />
              </div>
              <div class="field field-full">
                <label class="field-label">Razón social</label>
                <input class="field-input" v-model="editSesionModal.form.razon_social" />
              </div>
              <div class="field">
                <label class="field-label">Guía de Remisión</label>
                <input class="field-input" v-model="editSesionModal.form.guia_remision" />
              </div>
              <div class="field">
                <label class="field-label">Guía de Transporte</label>
                <input class="field-input" v-model="editSesionModal.form.guia_transporte" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="cerrarEditarSesion">Cancelar</button>
          <button class="btn-primary ready" :disabled="store.guardando" @click="guardarEditarSesion">
            <span v-if="store.guardando" class="spinner" />
            <span v-else>Guardar cambios</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL: Editar Lote (Admin) ────────────────────── -->
    <div v-if="editLoteModal.visible" class="modal-overlay" @click.self="cerrarEditarLote">
      <div class="modal">
        <div class="modal-header">
          <h2>EDITAR LOTE {{ editLoteModal.ip }}</h2>
          <button class="btn-cerrar" @click="cerrarEditarLote">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field field-full">
              <label class="field-label">Tipo de material</label>
              <select class="field-input field-select" v-model="editLoteModal.form.tipo_material">
                <option value="Mineral">Mineral</option>
                <option value="Llampo">Llampo</option>
                <option value="M.Llampo">M.Llampo</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">BRUTO / peso_inicial (TM)</label>
              <input class="field-input" type="number" step="0.001" v-model.number="editLoteModal.form.peso_inicial" />
            </div>
            <div class="field">
              <label class="field-label">TARA / peso_final (TM)</label>
              <input class="field-input" type="number" step="0.001" v-model.number="editLoteModal.form.peso_final" />
            </div>
            <div class="field">
              <label class="field-label">N° Sacos</label>
              <input class="field-input" type="number" min="0" v-model.number="editLoteModal.form.sacos" :disabled="editLoteModal.form.granel" />
            </div>
            <div class="field" style="display:flex;align-items:center;gap:.5rem;padding-top:1.5rem">
              <input type="checkbox" id="edit-granel" v-model="editLoteModal.form.granel" @change="editLoteModal.form.sacos = null" />
              <label for="edit-granel" class="field-label" style="margin:0">Granel</label>
            </div>
          </div>
          <p v-if="editLoteModal.error" class="error-msg" style="margin-top:.75rem">{{ editLoteModal.error }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="cerrarEditarLote">Cancelar</button>
          <button class="btn-primary ready" :disabled="store.guardando" @click="guardarEditarLote">
            <span v-if="store.guardando" class="spinner" />
            <span v-else>Guardar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ── MODAL: Eliminar Lote ──────────────────────────── -->
    <div v-if="eliminarModal.visible" class="modal-overlay" @click.self="cerrarEliminar">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Eliminar {{ eliminarModal.ip }}</h2>
          <button class="btn-cerrar" @click="cerrarEliminar">✕</button>
        </div>
        <div class="modal-body">
          <p class="elim-aviso">Acción irreversible — queda registrado en auditoría.</p>
          <div class="field" style="margin-top:.75rem">
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

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBalanzaStore } from '@/stores/balanza'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import type { LoteDetalle, ProvAcopDropdown} from '@/api/balanza'
import { balanzaApi } from '@/api/balanza'

const globalSetTimeout = setTimeout

const route     = useRoute()
const router    = useRouter()
const store     = useBalanzaStore()
const authStore = useAuthStore()
const ui        = useUiStore()

const sesionId     = Number(route.params.id)
const sesion       = computed(() => store.sesionActual)
const lotesActivos = computed(() => sesion.value?.lotes.filter(l => !l.eliminado) ?? [])

// ── Tipo material — global para todos los lotes ────────────
const tipoMaterial = ref('')

// ── Sacos / Granel ─────────────────────────────────────────
const sacos  = ref<number | null>(null)
const granel = ref(false)

// ── Peso actual en balanza ─────────────────────────────────
const pesoActual = ref<number | null>(null)

function capturarBruto() { if (pesoActual.value !== null) loteForm.peso_inicial = pesoActual.value }
function capturarTara()  { if (pesoActual.value !== null) loteForm.peso_final   = pesoActual.value }

// ── Formulario lote ────────────────────────────────────────
const loteForm = reactive({
  peso_inicial: null as number | null,  // BRUTO (camión cargado)
  peso_final:   null as number | null,  // TARA  (camión vacío)
})

/**
 * Pre-rellena BRUTO del nuevo lote con TARA del lote anterior.
 * Lógica: un camión que descargas en varias pasadas →
 *   TARA_N = peso del camión tras descarga = BRUTO_{N+1} antes de nueva descarga.
 */
function preFillBruto() {
  const activos = sesion.value?.lotes.filter(l => !l.eliminado) ?? []
  if (activos.length > 0) {
    const ultimo = activos[activos.length - 1]
    if (ultimo?.pesaje?.peso_final != null) {
      loteForm.peso_inicial = Number(ultimo.pesaje.peso_final)
    }
  }
}

// Validación: BRUTO (peso_inicial) > TARA (peso_final)
const pesoError = computed(() => {
  const { peso_inicial: bruto, peso_final: tara } = loteForm
  if (bruto !== null && tara !== null && bruto > 0 && tara > 0 && bruto <= tara) {
    return 'El BRUTO debe ser mayor que la TARA'
  }
  return ''
})

// NETO = BRUTO - TARA
const pesoNeto = computed(() => {
  const { peso_inicial: bruto, peso_final: tara } = loteForm
  return (bruto !== null && tara !== null && bruto > tara) ? bruto - tara : 0
})

/** Lista de requisitos pendientes para habilitar "Capturar peso" */
const loteFormFaltantes = computed(() => {
  const f: string[] = []
  if (!tipoMaterial.value)                                  f.push('seleccionar PRODUCTO')
  if ((loteForm.peso_inicial ?? 0) <= 0)                    f.push('ingresar BRUTO')
  if ((loteForm.peso_final   ?? 0) <= 0)                    f.push('ingresar TARA')
  if (
    loteForm.peso_inicial !== null && loteForm.peso_final !== null &&
    loteForm.peso_inicial > 0 && loteForm.peso_final > 0 &&
    loteForm.peso_inicial <= loteForm.peso_final
  )                                                         f.push('BRUTO debe ser > TARA')
  return f
})

const loteFormValido = computed(() => loteFormFaltantes.value.length === 0)

const mostrarFaltantes = ref(false)

function intentarRegistrar() {
  if (!loteFormValido.value) {
    mostrarFaltantes.value = true
    return
  }
  mostrarFaltantes.value = false
  registrarLote()
}

// Ocultar mensaje al corregir campos
watch(
  [tipoMaterial, () => loteForm.peso_inicial, () => loteForm.peso_final],
  () => { if (loteFormValido.value) mostrarFaltantes.value = false }
)

async function registrarLote() {
  if (!loteFormValido.value) return
  const ok = await store.agregarLote(sesionId, {
    tipo_material: tipoMaterial.value,
    pesaje: {
      peso_inicial: loteForm.peso_inicial!,   // BRUTO
      peso_final:   loteForm.peso_final!,     // TARA
      sacos:        granel.value ? null : (sacos.value || null),
      granel:       granel.value,
    },
  })
  if (ok) {
    loteForm.peso_inicial = null
    loteForm.peso_final   = null
    // Pre-rellenar BRUTO del siguiente lote con la TARA que acaba de quedar registrada
    preFillBruto()
  }
}

// ── Sesión ─────────────────────────────────────────────────
async function pausar() {
  const ok = await ui.showConfirm({
    title: 'Pausar sesión',
    message: '¿Pausar? Podrá reanudarla.',
    confirmLabel: 'Pausar',
  })
  if (ok) await store.pausarSesion(sesionId)
}
async function reanudar() { await store.reanudarSesion(sesionId) }
async function finalizar() {
  const ok = await ui.showConfirm({
    title: 'Finalizar sesión',
    message: `¿Finalizar con ${lotesActivos.value.length} lote(s)? Se generarán los tickets.`,
    confirmLabel: 'Finalizar y generar tickets',
  })
  if (ok) await store.finalizarSesion(sesionId)
}

async function verTicket(lote: LoteDetalle) {
  try {
    const url = await balanzaApi.ticketPreviewBlob(sesionId, lote.id)
    window.open(url, '_blank')
    // Liberar memoria después de un momento (la pestaña ya cargó el HTML)
    setTimeout(() => URL.revokeObjectURL(url), 10_000)
  } catch {
    ui.toast('Error al cargar preview del ticket', 'error')
  }
}

async function descargarTicket(lote: LoteDetalle) {
  await store.descargarTicket(sesionId, lote.id, lote.ip)
}

const descargandoTodos = ref(false)

async function descargarTodos() {
  if (!sesion.value) return
  descargandoTodos.value = true
  try {
    await store.descargarTicketsSesion(sesion.value.id)
    ui.toast('PDF generado', 'success')
  } catch {
    ui.toast('Error al generar PDF', 'error')
  } finally {
    descargandoTodos.value = false
  }
}

// ── Modal: Editar Sesión ───────────────────────────────────
const editSesionModal = reactive({
  visible: false,
  busqProv: '', dropProv: false,
  busqAcop: '', dropAcop: false,
  editProv: null as ProvAcopDropdown | null,
  editAcop: null as ProvAcopDropdown | null,
  form: {
    placa: '', carreta: '', conductor: '',
    transportista: '', razon_social: '',
    guia_remision: '', guia_transporte: '',
  },
})

function abrirEditarSesion() {
  const s = sesion.value
  if (!s) return
  store.cargarProvacops()
  Object.assign(editSesionModal.form, {
    placa: s.placa, carreta: s.carreta ?? '',
    conductor: s.conductor ?? '', transportista: s.transportista ?? '',
    razon_social: s.razon_social ?? '',
    guia_remision: s.guia_remision ?? '', guia_transporte: s.guia_transporte ?? '',
  })
  editSesionModal.busqProv = s.proveedor_razon_social
  editSesionModal.busqAcop = s.acopiador_razon_social
  editSesionModal.editProv = null
  editSesionModal.editAcop = null
  editSesionModal.visible  = true
}
function cerrarEditarSesion() { editSesionModal.visible = false }

const editProvsFiltered = computed(() => {
  const seen = new Set<number>()
  const q = editSesionModal.busqProv.toLowerCase()
  return store.provacops.filter(p => {
    if (seen.has(p.proveedor_id)) return false
    seen.add(p.proveedor_id)
    return p.proveedor_razon_social.toLowerCase().includes(q)
  })
})

const editAcopsFiltered = computed(() => {
  if (!editSesionModal.editProv) return []
  const q = editSesionModal.busqAcop.toLowerCase()
  return store.provacops.filter(p =>
    p.proveedor_id === editSesionModal.editProv!.proveedor_id &&
    p.acopiador_razon_social.toLowerCase().includes(q)
  )
})

function editSelProv(p: ProvAcopDropdown) {
  editSesionModal.editProv = p
  editSesionModal.busqProv = p.proveedor_razon_social
  editSesionModal.dropProv = false
  editSesionModal.editAcop = null
  editSesionModal.busqAcop = ''
  const opts = store.provacops.filter(x => x.proveedor_id === p.proveedor_id)
  if (opts.length === 1) editSelAcop(opts[0]!)
}
function editSelAcop(a: ProvAcopDropdown) {
  editSesionModal.editAcop = a
  editSesionModal.busqAcop = a.acopiador_razon_social
  editSesionModal.dropAcop = false
}

async function guardarEditarSesion() {
  const payload: Record<string, any> = { ...editSesionModal.form }
  if (editSesionModal.editAcop) {
    payload.provacop_id = editSesionModal.editAcop.provacop_id
  }
  const ok = await store.editarSesion(sesionId, payload)
  if (ok) cerrarEditarSesion()
}

// ── Modal: Editar Lote (Admin) ─────────────────────────────
const editLoteModal = reactive({
  visible: false,
  loteId: 0,
  ip: '',
  error: '',
  form: {
    tipo_material: 'Mineral',
    peso_inicial: null as number | null,
    peso_final:   null as number | null,
    sacos:        null as number | null,
    granel:       false,
  },
})

function abrirEditarLote(lote: LoteDetalle) {
  Object.assign(editLoteModal, {
    visible: true, loteId: lote.id, ip: lote.ip, error: '',
    form: {
      tipo_material: lote.tipo_material ?? 'Mineral',
      peso_inicial:  lote.pesaje ? Number(lote.pesaje.peso_inicial) : null,
      peso_final:    lote.pesaje ? Number(lote.pesaje.peso_final)   : null,
      sacos:         lote.pesaje?.sacos ?? null,
      granel:        lote.pesaje?.granel ?? false,
    },
  })
}
function cerrarEditarLote() { editLoteModal.visible = false }

async function guardarEditarLote() {
  editLoteModal.error = ''
  const f = editLoteModal.form
  if (f.peso_inicial !== null && f.peso_final !== null && f.peso_inicial <= f.peso_final) {
    editLoteModal.error = 'El BRUTO debe ser mayor que la TARA'
    return
  }
  const ok = await store.editarLote(sesionId, editLoteModal.loteId, {
    tipo_material: f.tipo_material,
    peso_inicial:  f.peso_inicial ?? undefined,
    peso_final:    f.peso_final   ?? undefined,
    sacos:         f.sacos,
    granel:        f.granel,
  })
  if (ok) cerrarEditarLote()
}

// ── Modal: Eliminar Lote ───────────────────────────────────
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
function fmtTm(n: number | string) { return Number(n).toFixed(3) }
function estadoClass(e: string) {
  return { EN_PROCESO: 'badge-en-proceso', PAUSADO: 'badge-pausado', COMPLETO: 'badge-completo' }[e] ?? ''
}
function estadoLabel(e: string) {
  return { EN_PROCESO: 'EN PROCESO', PAUSADO: 'PAUSADO', COMPLETO: 'COMPLETO' }[e] ?? e
}
function loteEstadoClass(lote: LoteDetalle) {
  return lote.pesaje?.peso_final != null ? 'lc-completado' : 'lc-en-proceso'
}
function loteEstadoLabel(lote: LoteDetalle) {
  return lote.pesaje?.peso_final != null ? 'Completado' : 'En proceso'
}

onMounted(async () => {
  await store.cargarSesion(sesionId)
  preFillBruto()
})
</script>

<style scoped>
.sesion-page { max-width: 1200px; }

/* ── Header ──────────────────────────────────────────────── */
.sesion-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 1.5rem; background: var(--color-bg-card);
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  padding: 1rem 1.5rem; margin-bottom: 1.25rem;
}
.header-info    { display: flex; flex-wrap: wrap; gap: .75rem 2rem; align-items: center; flex: 1; }
.header-campo   { display: flex; align-items: center; gap: .5rem; }
.header-label   { font-family: var(--font-mono); font-size: .72rem; color: var(--color-text-muted); letter-spacing: .12em; white-space: nowrap; }
.header-valor   { font-family: var(--font-mono); font-size: .9rem; color: var(--color-text); }
.header-select  { height: 30px; padding: 0 .5rem; font-size: .82rem; }
.header-sacos   { width: 80px; height: 30px; padding: 0 .4rem; font-size: .82rem; text-align: center; }
.granel-label   { display: flex; align-items: center; gap: .35rem; font-size: .78rem; color: var(--color-text-muted); cursor: pointer; }
.header-right   { display: flex; flex-direction: column; align-items: flex-end; gap: .5rem; flex-shrink: 0; }
.btn-editar-sesion { font-size: .78rem; padding: .3rem .7rem; }

.lote-badge {
  font-family: var(--font-mono); font-size: .78rem; letter-spacing: .08em;
  text-align: center; padding: .5rem .9rem; border-radius: var(--radius-sm);
  background: var(--color-bg); border: 1px solid var(--color-border); line-height: 1.5;
}
.badge-en-proceso { border-color: var(--color-warning) !important; color: var(--color-warning) !important; }
.badge-pausado    { border-color: var(--color-gold) !important; color: var(--color-gold) !important; }
.badge-completo   { border-color: var(--color-success) !important; color: var(--color-success) !important; }

/* ── Body 2 columnas ─────────────────────────────────────── */
.sesion-body {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 1.25rem; margin-bottom: 1.25rem;
}
@media (max-width: 900px) { .sesion-body { grid-template-columns: 1fr; } }

/* ── Cards ───────────────────────────────────────────────── */
.card {
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); padding: 1.25rem 1.5rem; margin-bottom: 1rem;
}
.card-titulo {
  font-family: var(--font-mono); font-size: .72rem; letter-spacing: .18em;
  color: var(--color-gold); margin-bottom: 1rem;
  padding-bottom: .4rem; border-bottom: 1px solid var(--color-border);
}

/* ── Transporte ──────────────────────────────────────────── */
.transp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem .75rem; }
.transp-full { grid-column: 1 / -1; }
.transp-fila { display: flex; gap: .5rem; align-items: baseline; }
.transp-label { font-family: var(--font-mono); font-size: .68rem; color: var(--color-text-muted); white-space: nowrap; min-width: 85px; }
.transp-val   { font-size: .85rem; color: var(--color-text); }

/* ── Pesaje activo ───────────────────────────────────────── */
.card-pesaje { border-color: var(--color-gold); }
.pesaje-display {
  display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem;
  background: var(--color-bg); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); padding: .75rem 1.25rem;
}
.peso-display-label { font-family: var(--font-mono); font-size: .68rem; color: var(--color-text-muted); letter-spacing: .12em; white-space: nowrap; }
.peso-display-input {
  font-family: var(--font-mono); font-size: 2rem; font-weight: 700;
  color: var(--color-gold-light); background: transparent;
  border: none; outline: none; width: 140px; text-align: right;
}
.peso-display-unit { font-family: var(--font-mono); font-size: 1rem; color: var(--color-text-muted); }

.pesaje-campos { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin-bottom: .75rem; }
.campo-peso    { display: flex; flex-direction: column; gap: .3rem; }
.campo-peso-label { font-family: var(--font-mono); font-size: .7rem; color: var(--color-text-muted); letter-spacing: .1em; }
.campo-peso-row { display: flex; gap: .4rem; }

.btn-capturar {
  background: rgba(184,150,46,.15); border: 1px solid var(--color-border);
  color: var(--color-gold); font-family: var(--font-mono); font-size: .72rem;
  border-radius: var(--radius-sm); padding: 0 .6rem; cursor: pointer; white-space: nowrap;
  transition: background .15s;
}
.btn-capturar:hover { background: rgba(184,150,46,.3); }

.pesaje-resumen {
  display: flex; gap: 1.5rem; margin-bottom: 1rem;
  font-family: var(--font-mono); font-size: .8rem; color: var(--color-text-muted);
}
.neto-resumen strong { color: var(--color-gold-light); }
.btn-registrar { width: 100%; }

/* ── Lotes ───────────────────────────────────────────────── */
.lote-card {
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); margin-bottom: .75rem; overflow: hidden;
}
.lote-en-proceso { border-color: rgba(220,160,20,.5); }
.lote-eliminado  { opacity: .45; }

.lote-card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: .6rem 1rem; background: rgba(184,150,46,.06);
  border-bottom: 1px solid var(--color-border);
}
.lote-ip { font-family: var(--font-mono); font-size: .82rem; color: var(--color-gold); }
.lote-acciones { display: flex; align-items: center; gap: .4rem; }
.btn-icon-danger:hover { color: var(--color-error); border-color: var(--color-error); }

.badge-lote-estado {
  font-family: var(--font-mono); font-size: .68rem; letter-spacing: .1em;
  padding: .2rem .5rem; border-radius: var(--radius-sm);
}
.lc-completado { background: rgba(60,180,80,.15); color: #4ecf7a; border: 1px solid #4ecf7a; }
.lc-en-proceso { background: rgba(220,160,20,.12); color: var(--color-warning); border: 1px solid var(--color-warning); }
.badge-eliminado { background: rgba(220,60,60,.1); color: var(--color-error); border: 1px solid var(--color-error); }

.lote-card-body {
  padding: .75rem 1rem; display: grid;
  grid-template-columns: 1fr 1fr; gap: .3rem .75rem;
}
.lote-fila { display: flex; gap: .4rem; align-items: baseline; }
.lote-neto { grid-column: 1 / -1; margin-top: .2rem; }
.lote-dato-label { font-family: var(--font-mono); font-size: .68rem; color: var(--color-text-muted); min-width: 45px; }
.lote-dato-val   { font-family: var(--font-mono); font-size: .85rem; color: var(--color-text); }
.neto-val        { font-size: 1.1rem; color: var(--color-gold-light); font-weight: 600; }
.badge-propio    { font-size: .68rem; padding: .15rem .4rem; background: rgba(184,150,46,.1); border-radius: 3px; color: var(--color-gold); }

.lote-card-footer {
  padding: .5rem 1rem; border-top: 1px solid var(--color-border);
  display: flex; justify-content: flex-end;
}
.btn-sm { padding: .3rem .7rem; font-size: .78rem; }
.lotes-eliminados { margin-top: .5rem; font-size: .82rem; color: var(--color-text-muted); }
.lotes-eliminados summary { cursor: pointer; padding: .3rem 0; }

/* ── Modal edición ───────────────────────────────────────── */
.seccion-edit { margin-bottom: 1.25rem; }
.seccion-edit-titulo {
  font-family: var(--font-mono); font-size: .72rem; letter-spacing: .18em;
  color: var(--color-gold); margin-bottom: .75rem;
  padding-bottom: .3rem; border-bottom: 1px solid var(--color-border);
}
.field-disabled { opacity: .4; cursor: not-allowed; }

/* ── Autocomplete ────────────────────────────────────────── */
.autocomplete-wrap { position: relative; }
.ac-dropdown {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 200;
  background: var(--color-bg-card); border: 1px solid var(--color-gold);
  border-radius: var(--radius-sm); max-height: 180px; overflow-y: auto;
}
.ac-item { padding: .5rem .75rem; font-size: .85rem; cursor: pointer; }
.ac-item:hover { background: var(--color-gold-bg); }

/* ── Otros ───────────────────────────────────────────────── */
.elim-aviso { font-size: .82rem; color: var(--color-error); margin: 0; }
.bottom-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 1rem; border-top: 1px solid var(--color-border);
}
.bottom-bar-acciones { display: flex; gap: .75rem; }
.estado-tabla { padding: 2rem; text-align: center; color: var(--color-text-muted); }
.form-faltantes {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--color-warning);
  background: rgba(220, 160, 20, 0.08);
  border: 1px solid rgba(220, 160, 20, 0.3);
  border-radius: var(--radius-sm);
  padding: 0.4rem 0.75rem;
  margin-bottom: 0.5rem;
}
.faltante-icono { font-size: 0.9rem; }

.btn-incompleto {
  border-color: var(--color-warning) !important;
  box-shadow: 0 0 0 1px var(--color-warning);
}
</style>
