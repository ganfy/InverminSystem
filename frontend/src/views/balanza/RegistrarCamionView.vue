<template>
  <div class="registrar-page">
    <h1 class="page-title">Registrar Camión</h1>

    <!-- ── SECCIÓN 1: Proveedor y Acopiador ───────────────── -->
    <div class="seccion">
      <h2 class="seccion-titulo">PROVEEDOR Y ACOPIADOR</h2>
      <div class="seccion-grid">
        <!-- Proveedor autocomplete -->
        <div class="campo-fila">
          <label class="campo-label">PROVEEDOR:</label>
          <div class="autocomplete-wrap">
            <input
              class="field-input"
              v-model="busqProv"
              placeholder="Buscar proveedor..."
              @input="onInputProv"
              @focus="dropProv = true"
              @blur="cerrarDropProv"
              autocomplete="off"
            />
            <div v-if="dropProv && provsFiltrados.length > 0" class="ac-dropdown">
              <div
                v-for="p in provsFiltrados"
                :key="p.proveedor_id"
                class="ac-item"
                @mousedown.prevent="seleccionarProv(p)"
              >
                {{ p.proveedor_razon_social }}
              </div>
            </div>
          </div>
        </div>
        <!-- RUC -->
        <div class="campo-fila">
          <label class="campo-label">RUC:</label>
          <input
            class="field-input field-readonly"
            :value="provSeleccionado?.proveedor_ruc ?? ''"
            readonly
            placeholder="Auto-completado"
          />
        </div>
        <!-- Procedencia -->
        <div class="campo-fila">
          <label class="campo-label">PROCEDENCIA:</label>
          <input
            class="field-input"
            v-model="form.procedencia"
            placeholder="Ej: Concesión Los Lirios"
          />
        </div>
        <!-- Acopiador autocomplete -->
        <div class="campo-fila">
          <label class="campo-label">ACOPIADOR:</label>
          <div class="autocomplete-wrap">
            <input
              class="field-input"
              :class="{ 'field-disabled': !provSeleccionado }"
              v-model="busqAcop"
              :disabled="!provSeleccionado"
              placeholder="Seleccione proveedor primero"
              @input="onInputAcop"
              @focus="dropAcop = true"
              @blur="cerrarDropAcop"
              autocomplete="off"
            />
            <div v-if="dropAcop && acopsFiltrados.length > 0" class="ac-dropdown">
              <div
                v-for="a in acopsFiltrados"
                :key="a.provacop_id"
                class="ac-item"
                @mousedown.prevent="seleccionarAcop(a)"
              >
                <span>{{ a.acopiador_razon_social }}</span>
                <span v-if="a.es_propio" class="badge-propio">Auto-acopio</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SECCIÓN 2: Documentos (va ANTES del form de transporte) ────────── -->
    <!-- sesionId es null hasta que se cree la sesión al enviar -->
    <DocumentosPanel
      :sesion-id="null"
      @aplicar="aplicarDatosExtraidos"
      @archivos-listos="guardarArchivosPendientes"
    />

    <!-- ── SECCIÓN 3: Datos del transporte ────────────────── -->
    <div class="seccion">
      <h2 class="seccion-titulo">DATOS DEL TRANSPORTE</h2>
      <div class="transporte-grid">
        <div class="campo-fila">
          <label class="campo-label">PLACA:</label>
          <input
            class="field-input"
            :class="{ 'field-error': placaInvalida }"
            v-model="form.placa"
            placeholder="BVE-452"
            style="text-transform:uppercase"
            @input="normalizarPlaca"
          />
        </div>
        <div class="campo-fila">
          <label class="campo-label">CARRETA:</label>
          <input class="field-input" v-model="form.carreta" placeholder="N° carreta" />
        </div>
        <div class="campo-fila campo-fila-wide">
          <label class="campo-label">CONDUCTOR:</label>
          <input class="field-input" v-model="form.conductor" placeholder="Nombre del conductor" />
        </div>
        <div class="campo-fila campo-fila-wide">
          <label class="campo-label">TRANSPORTISTA:</label>
          <input class="field-input" v-model="form.transportista" placeholder="Empresa / nombre" />
        </div>
        <div class="campo-fila campo-fila-wide">
          <label class="campo-label">RAZÓN SOCIAL:</label>
          <input class="field-input" v-model="form.razon_social" placeholder="Razón social transportista" />
        </div>
        <div class="campo-fila">
          <label class="campo-label">G. REMISIÓN:</label>
          <input class="field-input" v-model="form.guia_remision" placeholder="GRE-XXXX" />
        </div>
        <div class="campo-fila">
          <label class="campo-label">G. TRANSPORTISTA:</label>
          <input class="field-input" v-model="form.guia_transporte" placeholder="TXX-XXXX" />
        </div>
      </div>
    </div>

    <p v-if="formError" class="error-msg">{{ formError }}</p>

    <!-- ── Barra inferior ─────────────────────────────────── -->
    <div class="bottom-bar">
      <button class="btn-secondary btn-volver" @click="router.push({ name: 'Balanza' })">
        <ArrowLeft :size="16" style="margin-right: 4px;" /> Volver
      </button>
      <button
        class="btn-primary ready"
        :disabled="store.guardando || !formValido"
        @click="continuar"
      >
        <span v-if="store.guardando" class="spinner" />
        <span v-else>Continuar →</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBalanzaStore } from '@/stores/balanza'
import { useUiStore } from '@/stores/ui'
import { balanzaApi } from '@/api/balanza'
import type { ProvAcopDropdown } from '@/api/balanza'
import type { TipoDocumento } from '@/types/balanza'
import DocumentosPanel from '@/components/balanza/DocumentosPanel.vue'

const router = useRouter()
const store  = useBalanzaStore()
const ui       = useUiStore()

// ── Archivos pendientes de subir tras crear sesión ─────────
/** Guardados por el panel de documentos antes de que exista sesión */
const archivosPendientes = ref<Array<{ file: File; tipo: TipoDocumento }>>([])

function guardarArchivosPendientes(archivos: Array<{ file: File; tipo: TipoDocumento }>) {
  archivosPendientes.value = archivos
}

// ── Autocomplete Proveedor ─────────────────────────────────
const busqProv         = ref('')
const dropProv         = ref(false)
const provSeleccionado = ref<ProvAcopDropdown | null>(null)

const provsUnicos = computed(() => {
  const seen = new Set<number>()
  return store.provacops.filter(p => {
    if (seen.has(p.proveedor_id)) return false
    seen.add(p.proveedor_id)
    return true
  })
})
const provsFiltrados = computed(() => {
  if (!busqProv.value.trim()) return provsUnicos.value
  const q = busqProv.value.toLowerCase()
  return provsUnicos.value.filter(p => p.proveedor_razon_social.toLowerCase().includes(q))
})

function onInputProv() {
  provSeleccionado.value = null
  acopSeleccionado.value = null
  busqAcop.value = ''
  dropProv.value = true
}
function seleccionarProv(p: ProvAcopDropdown) {
  provSeleccionado.value = p
  busqProv.value = p.proveedor_razon_social
  dropProv.value = false
  const opciones = store.provacops.filter(x => x.proveedor_id === p.proveedor_id)
  if (opciones.length === 1 && opciones[0]) seleccionarAcop(opciones[0])
}
function cerrarDropProv() {
  setTimeout(() => { dropProv.value = false }, 150)
}

// ── Autocomplete Acopiador ─────────────────────────────────
const busqAcop         = ref('')
const dropAcop         = ref(false)
const acopSeleccionado = ref<ProvAcopDropdown | null>(null)

const acopsDelProv = computed(() => {
  if (!provSeleccionado.value) return []
  return store.provacops.filter(p => p.proveedor_id === provSeleccionado.value!.proveedor_id)
})
const acopsFiltrados = computed(() => {
  if (!busqAcop.value.trim()) return acopsDelProv.value
  const q = busqAcop.value.toLowerCase()
  return acopsDelProv.value.filter(a => a.acopiador_razon_social.toLowerCase().includes(q))
})

function onInputAcop() {
  acopSeleccionado.value = null
  dropAcop.value = true
}
function seleccionarAcop(a: ProvAcopDropdown) {
  acopSeleccionado.value = a
  busqAcop.value = a.es_propio
    ? `${a.acopiador_razon_social} (auto-acopio)`
    : a.acopiador_razon_social
  dropAcop.value = false
}
function cerrarDropAcop() {
  setTimeout(() => { dropAcop.value = false }, 150)
}

// ── Formulario transporte ──────────────────────────────────
const form = reactive({
  placa:           '',
  carreta:         '',
  conductor:       '',
  transportista:   '',
  razon_social:    '',
  guia_remision:   '',
  guia_transporte: '',
  procedencia:     '',
})

/** Aplica datos extraídos del DocumentosPanel al formulario */
function aplicarDatosExtraidos(datos: Partial<Record<string, string | null>>) {
  if (datos.placa)          form.placa          = datos.placa
  if (datos.carreta)        form.carreta        = datos.carreta
  if (datos.conductor)      form.conductor      = datos.conductor
  if (datos.transportista)  form.transportista  = datos.transportista
  if (datos.razon_social)   form.razon_social   = datos.razon_social
  if (datos.guia_remision)  form.guia_remision  = datos.guia_remision
  if (datos.guia_transporte) form.guia_transporte = datos.guia_transporte

// ── Auto-seleccionar proveedor por RUC o razón social ──────────────────────
  // Solo intentar si aún no hay proveedor seleccionado manualmente
  if (provSeleccionado.value) return

  const rucExtraido = datos.ruc_proveedor?.trim()
  const rsExtraida  = datos.razon_social?.trim().toLowerCase()

  // Buscar primero por RUC (coincidencia exacta — más fiable)
  let coincidencia = rucExtraido
    ? provsUnicos.value.find(p => p.proveedor_ruc === rucExtraido)
    : undefined

  // Si no hay RUC o no coincide, buscar por razón social (coincidencia parcial)
  if (!coincidencia && rsExtraida) {
    coincidencia = provsUnicos.value.find(p =>
      p.proveedor_razon_social.toLowerCase().includes(rsExtraida) ||
      rsExtraida.includes(p.proveedor_razon_social.toLowerCase())
    )
  }

  if (coincidencia) {
    seleccionarProv(coincidencia)
    ui.toast(`Proveedor auto-seleccionado: ${coincidencia.proveedor_razon_social}`)
  }
}

// ── Validaciones ──────────────────────────────────────────
const regexPlaca = /^[A-Z0-9]{3}-\d{3}$|^[A-Z0-9]{2}-\d{4}$/

function normalizarPlaca() {
  form.placa = form.placa.toUpperCase().replace(/[^A-Z0-9-]/g, '')
}
const placaInvalida = computed(() => !!form.placa && !regexPlaca.test(form.placa))

const formError = ref('')
const formValido = computed(() =>
  !!provSeleccionado.value &&
  !!acopSeleccionado.value &&
  !!form.placa.trim() &&
  !placaInvalida.value
)

// ── Acción principal ───────────────────────────────────────
async function continuar() {
  formError.value = ''
  if (!provSeleccionado.value || !acopSeleccionado.value) {
    formError.value = 'Seleccione un proveedor y acopiador'
    return
  }
  if (!form.placa.trim()) {
    formError.value = 'La placa es obligatoria'
    return
  }
  if (placaInvalida.value) {
    formError.value = 'Formato de placa inválido (ej: ABC-123)'
    return
  }

  // 1. Crear sesión
  const sesion = await store.crearSesion({
    provacop_id:     acopSeleccionado.value.provacop_id,
    placa:           form.placa.trim().toUpperCase(),
    carreta:         form.carreta || null,
    conductor:       form.conductor || null,
    transportista:   form.transportista || null,
    razon_social:    form.razon_social || null,
    guia_remision:   form.guia_remision || null,
    guia_transporte: form.guia_transporte || null,
  })

  if (!sesion) return  // store.crearSesion ya maneja el error con toast

  // 2. Subir archivos pendientes (en background, sin bloquear navegación)
  if (archivosPendientes.value.length  && sesion.id > 0) {
    // Fire-and-forget: los archivos se suben en background
    // Si fallan, el usuario puede subirlos desde SesionView
    Promise.allSettled(
      archivosPendientes.value.map(item =>
        balanzaApi.subirDocumento(sesion.id, item.file, item.tipo)
      )
    )
  }

  const destId = sesion.offline_id ?? sesion.id
  router.push({ name: 'SesionBalanza', params: { id: String(destId) } })
}

onMounted(() => store.cargarProvacops())
</script>

<style scoped>
.registrar-page { max-width: 1100px; }
/* ── Grids ────────────────────────────────────────────────── */
.seccion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem 2.5rem;
  align-items: start;
}
.transporte-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem 2.5rem;
  align-items: start;
}
.campo-fila-wide { grid-column: 1 / -1; }
/* ── Campo fila ───────────────────────────────────────────── */
.campo-fila {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.campo-label {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  letter-spacing: 0.1em;
  color: var(--color-text-muted);
  white-space: nowrap;
  min-width: 100px;
  flex-shrink: 0;
  text-align: right;
}
.campo-fila .field-input { flex: 1; margin: 0; }
.field-readonly { opacity: 0.65; cursor: default; }
.field-disabled { opacity: 0.4; cursor: not-allowed; }
/* ── Barra inferior ───────────────────────────────────────── */
.bottom-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}
.btn-volver { min-width: 140px; }
</style>
