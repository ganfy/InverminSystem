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
        <!-- [OFFLINE] indicador -->
        <span v-if="esOffline" class="badge-offline-header"><WifiOff :size="12" style="margin-right: 4px;" /> OFFLINE</span>

        <div class="lote-badge" :class="estadoClass(sesion?.estado ?? '')">
          <template v-if="lotesActivos.length > 0">
            LOTE {{ lotesActivos.length }} DE {{ sesion?.lotes.filter(l=>!l.eliminado).length }}
          </template>
          <template v-else>SIN LOTES</template>
          <br />{{ estadoLabel(sesion?.estado ?? '') }}
        </div>
        <button
          class="btn-secondary btn-editar-sesion"
          :disabled="!online && sesionIdNum !== -1"
          :title="(!online && sesionIdNum !== -1) ? 'Solo puedes editar sesiones del servidor con internet' : 'Editar datos de transporte o proveedor'"
          @click="abrirEditarSesion"
        ><Pencil :size="14" style="margin-right: 4px;" /> Editar sesión</button>
      </div>
    </div>

    <!-- [OFFLINE] aviso documentos no subidos -->
    <div v-if="esOffline" class="aviso-offline">
      <span class="aviso-icono"><AlertTriangle :size="20" class="aviso-icono" /></span>
      <div class="aviso-texto">
        <strong>Modo sin conexión</strong> — Los documentos adjuntos en el formulario
        anterior <em>no se pudieron subir</em>. Estarán disponibles para agregar
        manualmente al sincronizar esta sesión.
        Editar sesión, pausar y ticket PDF no están disponibles hasta sincronizar.
      </div>
    </div>

    <!-- Online con pendientes: advertencia de bloqueo -->
    <div v-if="!esOffline && store.lotesHybridPendientes > 0" class="aviso-offline aviso-hybrid">
      <span class="aviso-icono"><AlertTriangle :size="20" class="aviso-icono" /></span>
      <div class="aviso-texto">
        <strong>{{ store.lotesHybridPendientes }} lote(s) sin sincronizar</strong>
        — Finalizar no estará disponible hasta reconectar y sincronizar.
      </div>
    </div>

    <!-- Offline con pendientes: solo informativo -->
    <div v-if="esOffline && store.lotesHybridPendientes > 0" class="aviso-offline aviso-hybrid">
      <span class="aviso-icono"><WifiOff :size="20" class="aviso-icono" /></span>
      <div class="aviso-texto">
        <strong>{{ store.lotesHybridPendientes }} lote(s) se sincronizarán al reconectar.</strong>
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
          <BalanzaIndicator
            :peso-display="pesoDisplay"
            :unidad="unidad"
            :estable="estable"
            :conectado="conectado"
            :ws-conectado="wsConectado"
            :error="balanzaError"
            :config="balanzaConfig"
            class="mb-4"
          />
          <div class="pesaje-display"
          :placeholder="unidadBalanza">
            <div class="peso-display-label">PESO ACTUAL EN BALANZA</div>
            <input class="peso-display-input" min="0" v-model.number="pesoActual" placeholder="0.000" />
            <span class="peso-display-unit">{{ unidadBalanza }}</span>
          </div>

          <div class="pesaje-campos">
            <div class="campo-peso">
              <label class="campo-peso-label">BRUTO (camión cargado)</label>
              <div class="campo-peso-row">
                <input
                  class="field-input"
                  type="number" step="0.001" min="0"
                  v-model.number="loteForm.peso_inicial"
                  :placeholder="unidadBalanza"
                  @input="isManualBruto = true"
                />
                <button class="btn-capturar" title="Capturar peso actual como BRUTO" @click="capturarBruto">
                  <ArrowDownToLine :size="14" style="margin-right: 4px;" /> Capturar
                </button>
              </div>
            </div>
            <div class="campo-peso">
              <label class="campo-peso-label">TARA (camión vacío)</label>
              <div class="campo-peso-row">
                <input
                  class="field-input"
                  type="number" step="0.001" min="0"
                  v-model.number="loteForm.peso_final"
                  :placeholder="unidadBalanza"
                  @input="isManualTara = true"
                />
                <button class="btn-capturar" title="Capturar peso actual como TARA" @click="capturarTara">
                  <ArrowDownToLine :size="14" style="margin-right: 4px;" /> Capturar
                </button>
              </div>
            </div>
          </div>
          <p v-if="pesoError" class="error-msg" style="margin:.25rem 0">{{ pesoError }}</p>
          <div class="pesaje-resumen">
            <span>BRUTO: <strong>{{ loteForm.peso_inicial ? loteForm.peso_inicial.toFixed(3) + ' ' + unidadBalanza : '—' }}</strong></span>
            <span>TARA: <strong>{{ loteForm.peso_final ? loteForm.peso_final.toFixed(3) + ' ' + unidadBalanza : '—' }}</strong></span>
            <span class="neto-resumen">NETO: <strong>{{ pesoNeto > 0 ? pesoNeto.toFixed(3) + ' ' + unidadBalanza : '—' }}</strong></span>
          </div>

          <div v-if="requiereJustificacion" class="field" style="margin-bottom: 1rem; text-align: left;">
            <label class="field-label" style="color: var(--color-warning);"><AlertTriangle :size="20" class="aviso-icono" /> Ingreso Manual: Justificación requerida</label>
            <textarea
              class="field-input"
              rows="2"
              v-model="loteForm.justificacion_manual"
              placeholder="Explique el motivo del ingreso manual..."
            ></textarea>
          </div>

          <div v-else-if="esRegistroManual && !balanzaDisponible" class="aviso-offline" style="margin-bottom: 1rem; padding: 0.5rem 0.75rem;">
            <Info :size="20" class="aviso-icono" />
            <div class="aviso-texto" style="font-size: var(--text-sm);">
              Balanza desconectada. Se registrará justificación automática.
            </div>
          </div>
          <div v-if="mostrarFaltantes && loteFormFaltantes.length > 0" class="form-faltantes">
            <span class="faltante-icono"><AlertTriangle :size="20" class="aviso-icono" /></span>
            Falta: {{ loteFormFaltantes.join(' · ') }}
          </div>
          <button
            class="btn-primary ready btn-registrar"
            :class="{ 'btn-incompleto': !loteFormValido && mostrarFaltantes }"
            :disabled="store.guardando"
            @click="intentarRegistrar"
          >
            <span v-if="store.guardando" class="spinner" />
            <span v-else>{{ esOffline ? 'Registrar lote (offline)' : 'Capturar peso' }}</span>
          </button>
        </div>
      </div><!-- /col-left -->

      <!-- Columna derecha: lista de lotes -->
      <div class="col-right">
        <div v-if="store.loadingSesion" class="estado-tabla">Cargando...</div>

        <LoteCard
          v-for="lote in sesion?.lotes.filter(l => !l.eliminado)"
          :key="lote.ip"
          :lote="lote"
          :is-admin="authStore.user?.rol === 'Admin'"
          :is-online="online"
          @editar="abrirEditarLote"
          @eliminar="abrirEliminar"
          @ver-ticket="store.verTicket"
          @imprimir-ticket="store.imprimirTicket"
        />

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
      </div></div><div class="bottom-bar">
      <button class="btn-secondary" @click="router.push({ name: 'Balanza' })"><ArrowLeft :size="16" style="margin-right: 4px;" /> Volver</button>
      <div class="bottom-bar-acciones">
        <button v-if="lotesActivos.length > 0" class="btn-secondary" @click="store.imprimirTicketsSesion()" title="Imprimir todos los tickets"><Printer :size="14" style="margin-right: 4px;" /> Tickets sesión</button>
        <button v-if="sesion?.estado === 'EN_PROCESO'" class="btn-secondary" :disabled="esOffline" @click="pausar"><Pause :size="14" style="margin-right: 4px;" /> Pausar</button>
        <button v-if="sesion?.estado === 'PAUSADO'" class="btn-secondary" :disabled="esOffline" @click="reanudar"><Play :size="14" style="margin-right: 4px;" /> Reanudar</button>
        <button v-if="sesion?.estado !== 'COMPLETO'" class="btn-primary ready" :disabled="store.guardando || lotesActivos.length === 0 || (!esOffline && store.lotesHybridPendientes > 0)" @click="finalizar">
          <span v-if="store.guardando" class="spinner" />
          <span v-else>{{ esOffline ? 'Finalizar (offline) →' : 'Finalizar y generar tickets →' }}</span>
        </button>
      </div>
    </div>

    <ModalEditarSesion
      v-if="editSesionModal.visible"
      :modal-data="editSesionModal"
      :guardando="store.guardando"
      :provs-filtrados="editProvsFiltered"
      :acops-filtrados="editAcopsFiltered"
      @close="cerrarEditarSesion"
      @save="guardarEditarSesion"
      @sel-prov="editSelProv"
      @sel-acop="editSelAcop"
    />

    <ModalEditarLote
      v-if="editLoteModal.visible"
      :modal-data="editLoteModal"
      :guardando="store.guardando"
      @close="cerrarEditarLote"
      @save="guardarEditarLote"
    />

    <ModalEliminarLote
      v-if="eliminarModal.visible"
      :modal-data="eliminarModal"
      :guardando="store.guardando"
      @close="cerrarEliminar"
      @confirm="confirmarEliminar"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBalanzaStore } from '@/stores/balanza'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useBalanza } from '@/composables/useBalanza'
import { useSync } from '@/composables/useSync'
import BalanzaIndicator from '@/components/balanza/BalanzaIndicator.vue'
import LoteCard from '@/components/balanza/LoteCard.vue'
import ModalEditarSesion from './ModalEditarSesion.vue'
import ModalEditarLote from './ModalEditarLote.vue'
import ModalEliminarLote from './ModalEliminarLote.vue'
import type { LoteDetalle, ProvAcopDropdown } from '@/api/balanza'
import { balanzaApi } from '@/api/balanza'
import { formatPesoPorModulo, getUnidadPorModulo, convertirParaInput, convertirParaBD } from '@/utils/units'
import {
  WifiOff,
  Pencil,
  AlertTriangle,
  ArrowDownToLine,
  ArrowLeft,
  Printer,
  Pause,
  Play,
  Info
} from 'lucide-vue-next'

const unidadBalanza = computed(() => getUnidadPorModulo('BALANZA'))

const globalSetTimeout = setTimeout

const route     = useRoute()
const router    = useRouter()
const store     = useBalanzaStore()
const authStore = useAuthStore()
const ui        = useUiStore()

// [OFFLINE] ID como string; detecta si es sesión offline por el prefijo
const sesionIdRaw = computed(() => (route.params.id || '') as string)
const esOffline = computed(() => sesionIdRaw.value.startsWith('offline-') || !online.value)
const sesionIdNum = computed(() => {
  if (!sesionIdRaw.value || sesionIdRaw.value.startsWith('offline-')) return -1
  return Number(sesionIdRaw.value)
})

const sesion       = computed(() => store.sesionActual)
const lotesActivos = computed(() => sesion.value?.lotes.filter(l => !l.eliminado) ?? [])

const {
  online, sesionRecargada,
  limpiarSesionRecargada,
  sesionOfflineSincronizada,
  limpiarSesionOfflineSincronizada,
  ultimoSync
} = useSync()

// Auto-redirect cuando una sesión 100% offline se sincroniza exitosamente en background
watch(sesionOfflineSincronizada, (val) => {
  if (val && val.offline_id === sesionIdRaw.value) {
    ui.toast('Conexión recuperada. Sesión sincronizada con el servidor.', 'success')
    if (val.server_id) {
      router.replace({ name: 'SesionBalanza', params: { id: val.server_id.toString() } })
    }
    limpiarSesionOfflineSincronizada()
  }
})

// Auto-reload cuando useSync sincroniza lotes de esta sesión
watch(ultimoSync, async () => {
  if (route.name !== 'SesionBalanza' || !sesionIdRaw.value) return
  if (!sesionIdRaw.value.startsWith('offline-') && sesionIdNum.value !== -1) {
    await store.cargarSesion(sesionIdNum.value)
    preFillTipoMaterial()
    preFillSacosGranel()
    preFillBruto()
  }
})

// ── Balanza física ─────────────────────────────────────────
const {
  peso,
  pesoDisplay,
  unidad,
  estable,
  conectado,
  wsConectado,
  error: balanzaError,
  config: balanzaConfig,
  capturar,
} = useBalanza()

// ── Peso actual en balanza ─────────────────────────────────
const pesoActual = ref<number | null>(null)
watch(peso, (nuevoPeso) => {
  if (wsConectado.value && conectado.value && nuevoPeso !== null) {
    pesoActual.value = nuevoPeso
  }
})

// ── Tipo material — global para todos los lotes ────────────
const tipoMaterial = ref('')

// ── Sacos / Granel ─────────────────────────────────────────
const sacos  = ref<number | null>(null)
const granel = ref(false)
const fechaBruto = ref<string | null>(null)

// ── Captura de pesos ───────────────────────────────────────
async function capturarBruto() {
  const valor = await resolverPeso()
  if (valor !== null) {
    loteForm.peso_inicial = valor
    isManualBruto.value = false
    fechaBruto.value = new Date().toISOString()
  }
}
async function capturarTara() {
  const valor = await resolverPeso()
  if (valor !== null) {
    loteForm.peso_final = valor
    isManualTara.value = false
  }
}
async function resolverPeso(): Promise<number | null> {
  if (wsConectado.value && conectado.value) {
    const lectura = await capturar()
    if (!lectura.estable) ui.toast('Peso capturado, pero la balanza no estaba estable. Verificar.', 'warning')
    return lectura.peso
  }
  return pesoActual.value
}

const isManualBruto = ref(false)
const isManualTara = ref(false)
const esRegistroManual = computed(() => isManualBruto.value || isManualTara.value)
const balanzaDisponible = computed(() => wsConectado.value && conectado.value)
const requiereJustificacion = computed(() => esRegistroManual.value && balanzaDisponible.value)

// ── Formulario lote ────────────────────────────────────────
const loteForm = reactive({
  peso_inicial: null as number | null,
  peso_final:   null as number | null,
  justificacion_manual: '',
})
function preFillBruto() {
  const activos = sesion.value?.lotes.filter(l => !l.eliminado) ?? []
  if (activos.length > 0) {
    const ultimo = activos[activos.length - 1]
    if (ultimo?.pesaje?.peso_final != null) {
      // LO CONVERTIMOS DE TM A LA UNIDAD VISUAL
      loteForm.peso_inicial = convertirParaInput(Number(ultimo.pesaje.peso_final), 'BALANZA')
    }
  }
}

function preFillTipoMaterial() {
  if (tipoMaterial.value) return
  const activos = sesion.value?.lotes.filter(l => !l.eliminado) ?? []
  const ultimo = activos[activos.length - 1]
  if (ultimo?.tipo_material) {
    tipoMaterial.value = ultimo.tipo_material
  }
}

function preFillSacosGranel() {
  const activos = sesion.value?.lotes.filter(l => !l.eliminado) ?? []
  const ultimo = activos[activos.length - 1]
  if (!ultimo?.pesaje) return
  if (ultimo.pesaje.granel) {
    granel.value = true
    sacos.value  = null
  } else if (ultimo.pesaje.sacos != null) {
    granel.value = false
    sacos.value  = ultimo.pesaje.sacos
  }
}

const pesoError = computed(() => {
  const { peso_inicial: bruto, peso_final: tara } = loteForm
  if (bruto !== null && tara !== null && bruto > 0 && tara > 0 && bruto <= tara) {
    return 'El BRUTO debe ser mayor que la TARA'
  }
  return ''
})

const pesoNeto = computed(() => {
  const { peso_inicial: bruto, peso_final: tara } = loteForm
  return (bruto !== null && tara !== null && bruto > tara) ? bruto - tara : 0
})

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
  if (requiereJustificacion.value && !loteForm.justificacion_manual.trim()) f.push('justificación manual')
  return f
})

const loteFormValido   = computed(() => loteFormFaltantes.value.length === 0)
const mostrarFaltantes = ref(false)

function intentarRegistrar() {
  if (!loteFormValido.value) { mostrarFaltantes.value = true; return }
  mostrarFaltantes.value = false
  registrarLote()
}

watch(
  [tipoMaterial, () => loteForm.peso_inicial, () => loteForm.peso_final],
  () => { if (loteFormValido.value) mostrarFaltantes.value = false },
)

async function registrarLote() {
  if (!loteFormValido.value) return

  let justificacionFinal = null
  if (esRegistroManual.value) {
    justificacionFinal = balanzaDisponible.value
      ? loteForm.justificacion_manual
      : 'Ingreso manual automático: Balanza física desconectada o sin servicio.'
  }
  // [OFFLINE] pasar string si es sesión offline, number si es online
  const ok = await store.agregarLote(
    sesionIdRaw.value.startsWith('offline-') ? sesionIdRaw.value : sesionIdNum.value,
    {
      tipo_material: tipoMaterial.value,
      pesaje: {
        peso_inicial: convertirParaBD(loteForm.peso_inicial, 'BALANZA')!,
        peso_final:   convertirParaBD(loteForm.peso_final, 'BALANZA')!,
        sacos:        granel.value ? null : (sacos.value || null),
        granel:       granel.value,
        fecha_inicio: fechaBruto.value ?? undefined,
        es_manual:    esRegistroManual.value,
        justificacion_manual: justificacionFinal,
      },
    },
  )
  if (ok) {
    loteForm.peso_inicial = null
    loteForm.peso_final   = null
    fechaBruto.value      = null
    loteForm.justificacion_manual = ''
    isManualBruto.value = false
    isManualTara.value = false
    preFillBruto()
  }
}

// ── Sesión ─────────────────────────────────────────────────
async function pausar() {
  if (esOffline.value) { ui.toast('Pausar no disponible sin conexión', 'warning'); return }
  const ok = await ui.showConfirm({
    title: 'Pausar sesión',
    message: '¿Pausar? Podrá reanudarla.',
    confirmLabel: 'Pausar',
  })
  if (ok) await store.pausarSesion(sesionIdNum.value)
}

async function reanudar() {
  if (esOffline.value) { ui.toast('Reanudar no disponible sin conexión', 'warning'); return }
  await store.reanudarSesion(sesionIdNum.value)
}

async function finalizar() {
  const ok = await ui.showConfirm({
    title: 'Finalizar sesión',
    message: esOffline.value
      ? `¿Finalizar con ${lotesActivos.value.length} lote(s)? Los datos se sincronizarán al reconectar.`
      : `¿Finalizar con ${lotesActivos.value.length} lote(s)? Se generarán los tickets.`,
    confirmLabel: esOffline.value ? 'Finalizar (offline)' : 'Finalizar y generar tickets',
  })
  if (!ok) return
  if (esOffline.value) {
    await store.finalizarSesionOffline(sesionIdRaw.value)
  } else {
    await store.finalizarSesion(sesionIdNum.value)
  }
}

// Auto-reload cuando useSync sincroniza lotes de esta sesión
watch(sesionRecargada, async (idRecargado) => {
  if (!idRecargado) return
  if (idRecargado === sesionIdNum.value) {
    // Esperar un tick para que limpiarLotesOnlineSynced ya haya corrido
    await nextTick()
    await store.cargarSesion(sesionIdNum.value)
    preFillTipoMaterial()
    preFillSacosGranel()
    ui.toast('Sesión actualizada con lotes sincronizados.', 'success')
    limpiarSesionRecargada()
  }
})

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
  editSesionModal.busqAcop = s.acopiador_razon_social ?? ''
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
    p.acopiador_razon_social.toLowerCase().includes(q),
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
  if (editSesionModal.editAcop) payload.provacop_id = editSesionModal.editAcop.provacop_id
  const targetId = esOffline.value ? sesionIdRaw.value : sesionIdNum.value
  const ok = await store.editarSesion(targetId, payload)
  if (ok) cerrarEditarSesion()
}

// ── Modal: Editar Lote (Admin) ─────────────────────────────
const editLoteModal = reactive({
  visible: false,
  loteId: 0 as number | string,
  ip: '',
  error: '',
  form: {
    tipo_material: '',
    peso_inicial: null as number | null,
    peso_final:   null as number | null,
    sacos:        null as number | null,
    granel:       false,
    justificacion_manual: '',
  },
})

function abrirEditarLote(lote: LoteDetalle) {
  if (!online.value && lote.id !== -1) {
    ui.toast('No se puede editar un lote del servidor sin conexión a internet.', 'warning')
    return
  }
  Object.assign(editLoteModal, {
    visible: true,
    // Si el lote no ha ido al servidor (id: -1), usamos su IP como identificador
    loteId: lote.id === -1 ? lote.ip : lote.id,
    ip: lote.ip,
    error: '',
    form: {
      tipo_material: lote.tipo_material ?? '',
      peso_inicial:  lote.pesaje ? convertirParaInput(Number(lote.pesaje.peso_inicial), 'BALANZA') : null,
      peso_final:    lote.pesaje ? convertirParaInput(Number(lote.pesaje.peso_final), 'BALANZA')   : null,
      sacos:         lote.pesaje?.sacos ?? null,
      granel:        lote.pesaje?.granel ?? false,
      justificacion_manual: '',
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
  const targetSesionId = sesionIdRaw.value.startsWith('offline-') ? sesionIdRaw.value : sesionIdNum.value;
  const ok = await store.editarLote(targetSesionId, editLoteModal.loteId, {
    tipo_material: f.tipo_material,
    peso_inicial:  convertirParaBD(f.peso_inicial, 'BALANZA') ?? undefined,
    peso_final:    convertirParaBD(f.peso_final, 'BALANZA')   ?? undefined,
    sacos:         f.sacos,
    granel:        f.granel,
    es_manual:     true,
    justificacion_manual: f.justificacion_manual.trim() || undefined,
  })
  if (ok) cerrarEditarLote()
  if (sesionIdRaw.value.startsWith('offline-')) {
      await store.cargarSesionOffline(sesionIdRaw.value)
    } else {
      await store.cargarSesion(sesionIdNum.value)
    }
}

// ── Modal: Eliminar Lote ───────────────────────────────────
const eliminarModal = reactive({ visible: false, loteId: 0, ip: '', motivo: '', error: '' })

function abrirEliminar(lote: LoteDetalle) {
  if (!online.value && lote.id !== -1) {
    ui.toast('No se puede eliminar un lote del servidor sin conexión a internet.', 'warning')
    return
  }
  Object.assign(eliminarModal, { visible: true, loteId: lote.id, ip: lote.ip, motivo: '', error: '' })
}
function cerrarEliminar() { eliminarModal.visible = false }

async function confirmarEliminar() {
  if (!eliminarModal.motivo.trim()) { eliminarModal.error = 'Motivo obligatorio'; return }
  const ok = await store.eliminarLote(sesionIdNum.value, eliminarModal.loteId, eliminarModal.motivo.trim())
  if (ok) {
    cerrarEliminar()
    await store.cargarSesion(sesionIdNum.value)
  }
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

// ── Montaje ────────────────────────────────────────────────
async function inicializarVista() {
  store.lotesHybridPendientes = 0;
  const idParam = sesionIdRaw.value;

  if (idParam.startsWith('offline-')) {
    await store.cargarSesionOffline(idParam)
  } else {
    await store.cargarSesion(sesionIdNum.value)
    preFillBruto()
  }
  preFillTipoMaterial()
  preFillSacosGranel()
}
onMounted(inicializarVista)

watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    inicializarVista()
  }
})
</script>

<style scoped>
.sesion-page { max-width: 1200px; }

/* ── Header ──────────────────────────────────────────────── */
.sesion-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 1.5rem; background: var(--color-bg-card);
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  padding: var(--spacing-lg) 2rem; margin-bottom: 1.25rem;
}
.header-info    { display: flex; flex-wrap: wrap; gap: .75rem 2rem; align-items: center; flex: 1; }
.header-campo   { display: flex; align-items: center; gap: .5rem; }
.header-label   { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted); letter-spacing: .12em; white-space: nowrap; }
.header-valor   { font-family: var(--font-mono); font-size: var(--text-base); color: var(--color-text); }
.header-select  { height: 30px; padding: 0 .5rem; font-size: var(--text-md); }
.header-sacos   { width: 80px; height: 30px; padding: 0 .4rem; font-size: var(--text-md); text-align: center; }
.granel-label   { display: flex; align-items: center; gap: .35rem; font-size: var(--text-sm); color: var(--color-text-muted); cursor: pointer; }
.header-right   { display: flex; flex-direction: column; align-items: flex-end; gap: .5rem; flex-shrink: 0; }
.btn-editar-sesion { font-size: var(--text-sm); padding: .3rem .7rem; }
.btn-secondary:disabled { opacity: .4; cursor: not-allowed; }
.lote-badge {
  font-family: var(--font-mono); font-size: var(--text-sm); letter-spacing: .08em;
  text-align: center; padding: .5rem .9rem; border-radius: var(--radius-sm);
  background: var(--color-bg); border: 1px solid var(--color-border); line-height: 1.5;
  width:  100%;
}
.badge-en-proceso { border-color: var(--color-warning) !important; color: var(--color-warning) !important; }
.badge-pausado    { border-color: var(--color-gold) !important; color: var(--color-gold) !important; }
.badge-completo   { border-color: var(--color-success) !important; color: var(--color-success) !important; }

/* ── [OFFLINE] badge ─────────────────────────────────────── */
.badge-offline-header {
  font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: .14em;
  background: var(--color-offline-bg); color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 3px;
  padding: 2px 8px;
}

/* ── Body 2 columnas ─────────────────────────────────────── */
.sesion-body {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 1.25rem; margin-bottom: 1.25rem;
}
@media (max-width: 900px) { .sesion-body { grid-template-columns: 1fr; } }

/* ── Transporte ──────────────────────────────────────────── */
.transp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem .75rem; }
.transp-full { grid-column: 1 / -1; }
.transp-fila { display: flex; gap: .5rem; align-items: baseline; }
.transp-label { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-muted); white-space: nowrap; min-width: 85px; }
.transp-val   { font-size: var(--text-md); color: var(--color-text); }

/* ── Pesaje activo ───────────────────────────────────────── */
.card-pesaje { border-color: var(--color-gold); }
.pesaje-display {
  display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem;
  background: var(--color-bg); border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); padding: .75rem 1.25rem;
}
.peso-display-label { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-muted); letter-spacing: .12em; white-space: nowrap; }
.peso-display-input {
  font-family: var(--font-mono); font-size: var(--text-xxl); font-weight: 700;
  color: var(--color-gold-light); background: transparent;
  border: none; outline: none; width: 140px; text-align: right;
}
.peso-display-unit { font-family: var(--font-mono); font-size: var(--text-base); color: var(--color-text-muted); }
.pesaje-campos { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin-bottom: .75rem; }
.campo-peso    { display: flex; flex-direction: column; gap: .3rem; }
.campo-peso-label { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted); letter-spacing: .1em; }
.campo-peso-row { display: flex; gap: .4rem; }
.btn-capturar {
  background: var(--color-gold-bg); border: 1px solid var(--color-border);
  color: var(--color-gold); font-family: var(--font-mono); font-size: var(--text-sm);
  border-radius: var(--radius-sm); padding: 0 .6rem; cursor: pointer; white-space: nowrap;
  transition: background .15s;
}
.btn-capturar:hover { background: rgba(184, 150, 46, 0.3); }
.pesaje-resumen {
  display: flex; gap: 1.5rem; margin-bottom: 1rem;
  font-family: var(--font-mono); font-size: var(--text-md); color: var(--color-text-muted);
}
.neto-resumen strong { color: var(--color-gold-light); }
.btn-registrar { width: 100%; }

/* ── BARRA INFERIOR ─────────────────────────────────── */
.bottom-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap; /* Permite que bajen si la pantalla es muy estrecha */
  gap: 1rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--color-border);
  margin-top: 1rem;
}

.bottom-bar-acciones {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}
</style>
