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

        <!-- RUC (auto-fill solo lectura) -->
        <div class="campo-fila">
          <label class="campo-label">RUC:</label>
          <input
            class="field-input field-readonly"
            :value="provSeleccionado?.proveedor_ruc ?? ''"
            readonly
            placeholder="Auto-completado"
          />
        </div>

        <!-- Procedencia (solo lectura si viene del proveedor) -->
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

    <!-- ── SECCIÓN 2: Datos del transporte ────────────────── -->
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
          <input
            class="field-input"
            v-model="form.carreta"
            placeholder="N° carreta"
          />
        </div>

        <div class="campo-fila campo-fila-wide">
          <label class="campo-label">CONDUCTOR:</label>
          <input
            class="field-input"
            v-model="form.conductor"
            placeholder="Nombre del conductor"
          />
        </div>

        <div class="campo-fila campo-fila-wide">
          <label class="campo-label">TRANSPORTISTA:</label>
          <input
            class="field-input"
            v-model="form.transportista"
            placeholder="Empresa / nombre"
          />
        </div>

        <div class="campo-fila campo-fila-wide">
          <label class="campo-label">RAZÓN SOCIAL:</label>
          <input
            class="field-input"
            v-model="form.razon_social"
            placeholder="Razón social transportista"
          />
        </div>

        <div class="campo-fila">
          <label class="campo-label">G. REMISIÓN:</label>
          <input
            class="field-input"
            v-model="form.guia_remision"
            placeholder="GRE-XXXX"
          />
        </div>

        <div class="campo-fila">
          <label class="campo-label">G. TRANSPORTISTA:</label>
          <input
            class="field-input"
            v-model="form.guia_transporte"
            placeholder="TXX-XXXX"
          />
        </div>
      </div>
    </div>

    <p v-if="formError" class="error-msg">{{ formError }}</p>

    <!-- ── Barra inferior ─────────────────────────────────── -->
    <div class="bottom-bar">
      <button class="btn-secondary btn-volver" @click="router.push({ name: 'Balanza' })">
        ← Volver
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
import type { ProvAcopDropdown } from '@/api/balanza'

const router = useRouter()
const store  = useBalanzaStore()

// ── Autocomplete Proveedor ─────────────────────────────────
const busqProv        = ref('')
const dropProv        = ref(false)
const provSeleccionado = ref<ProvAcopDropdown | null>(null)

// Proveedores únicos (deduplicados por proveedor_id)
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
  return provsUnicos.value.filter(p =>
    p.proveedor_razon_social.toLowerCase().includes(q)
  )
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
  // Auto-fill acopiador si solo hay uno o es propio
  const opciones = store.provacops.filter(x => x.proveedor_id === p.proveedor_id)
  if (opciones.length === 1 && opciones[0]) {
    seleccionarAcop(opciones[0])
  }
}

function cerrarDropProv() {
  setTimeout(() => { dropProv.value = false }, 150)
}

// ── Autocomplete Acopiador ─────────────────────────────────
const busqAcop         = ref('')
const dropAcop         = ref(false)
const acopSeleccionado = ref<ProvAcopDropdown | null>(null)

// Opciones de acopiador solo del proveedor seleccionado
const acopsDelProv = computed(() => {
  if (!provSeleccionado.value) return []
  return store.provacops.filter(p => p.proveedor_id === provSeleccionado.value!.proveedor_id)
})

const acopsFiltrados = computed(() => {
  if (!busqAcop.value.trim()) return acopsDelProv.value
  const q = busqAcop.value.toLowerCase()
  return acopsDelProv.value.filter(a =>
    a.acopiador_razon_social.toLowerCase().includes(q)
  )
})

function onInputAcop() {
  acopSeleccionado.value = null
  dropAcop.value = true
}

function seleccionarAcop(a: ProvAcopDropdown) {
  acopSeleccionado.value = a
  busqAcop.value = a.es_propio ? `${a.acopiador_razon_social} (auto-acopio)` : a.acopiador_razon_social
  dropAcop.value = false
}

function cerrarDropAcop() {
  setTimeout(() => { dropAcop.value = false }, 150)
}

// ── Formulario transporte ──────────────────────────────────
const form = reactive({
  placa:          '',
  carreta:        '',
  conductor:      '',
  transportista:  '',
  razon_social:   '',
  guia_remision:  '',
  guia_transporte: '',
  procedencia:    '',
})

// ── Validaciones ──────────────────────────────────────────

// Formatos válidos Perú:
// ABC-123
// AB-1234
const regexPlaca = /^[A-Z]{3}-\d{3}$|^[A-Z]{2}-\d{4}$/

function normalizarPlaca() {
  form.placa = form.placa
    .toUpperCase()
    .replace(/[^A-Z0-9-]/g, '')
}

const placaInvalida = computed(() => {
  if (!form.placa) return false
  return !regexPlaca.test(form.placa)
})

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

  if (sesion) {
    router.push({ name: 'SesionBalanza', params: { id: sesion.id } })
  }
}

onMounted(() => store.cargarProvacops())
</script>

<style scoped>
.registrar-page { max-width: 1100px; }

/* ── Sección ──────────────────────────────────────────────── */
.seccion {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.5rem 2rem;
  margin-bottom: 1.5rem;
}

.seccion-titulo {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  color: var(--color-gold);
  margin-bottom: 1.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

/* ── Grid proveedor/acopiador ─────────────────────────────── */
.seccion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem 2.5rem;
  align-items: start;
}

/* ── Grid transporte ──────────────────────────────────────── */
.transporte-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem 2.5rem;
  align-items: start;
}
.campo-fila-wide { grid-column: 1 / -1; }

/* ── Campo fila (label + input en línea) ──────────────────── */
.campo-fila {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.campo-label {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: var(--color-text-muted);
  white-space: nowrap;
  min-width: 100px;
  flex-shrink: 0;
  text-align: right;
}

.campo-fila .field-input {
  flex: 1;
  margin: 0;
}

.field-readonly {
  opacity: 0.65;
  cursor: default;
}

.field-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ── Autocomplete ─────────────────────────────────────────── */
.autocomplete-wrap {
  position: relative;
  flex: 1;
}

.autocomplete-wrap .field-input {
  width: 100%;
}

.ac-dropdown {
  position: absolute;
  top: 100%;
  left: 0; right: 0;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-focus);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  max-height: 200px;
  overflow-y: auto;
  z-index: 200;
}

.ac-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.9rem;
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
  transition: background 0.15s;
}
.ac-item:last-child { border-bottom: none; }
.ac-item:hover { background: var(--color-gold-bg); }

.badge-propio {
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  background: rgba(14, 165, 233, 0.15);
  color: #38bdf8;
  padding: 1px 6px;
  border-radius: 3px;
  flex-shrink: 0;
}

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

.btn-volver {
  min-width: 140px;
}
</style>
