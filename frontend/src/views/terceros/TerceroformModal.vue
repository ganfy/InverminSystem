<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="cerrar">
        <div class="modal modal-lg">

          <!-- Header -->
          <div class="modal-header">
            <div class="modal-title-group">
              <span class="modal-icon">{{ editando ? '✎' : '+' }}</span>
              <h2>{{ editando ? 'Editar Tercero' : 'Registrar Tercero' }}</h2>
            </div>
            <!-- Indicador de sección -->
            <div class="modal-steps">
              <button
                v-for="(s, i) in secciones"
                :key="i"
                class="step-dot"
                :class="{ active: seccionActual === i, done: seccionActual > i }"
                @click="irA(i)"
                :title="s"
              >
                <span class="step-num">{{ seccionActual > i ? '✓' : i + 1 }}</span>
              </button>
            </div>
            <button class="modal-close" @click="cerrar">✕</button>
          </div>

          <!-- Nombre de sección -->
          <div class="seccion-titulo">
            <span class="seccion-num">{{ seccionActual + 1 }}/{{ secciones.length }}</span>
            <span>{{ secciones[seccionActual] }}</span>
          </div>

          <!-- Body -->
          <div class="modal-body">

            <!-- ─── SECCIÓN 0: Datos del Proveedor ─────────────────────── -->
            <div v-show="seccionActual === 0" class="form-grid">
              <div class="field field-full">
                <label class="field-label">Razón Social *</label>
                <input
                  v-model="form.razon_social"
                  class="field-input"
                  :class="{ error: errores.razon_social }"
                  placeholder="Nombre completo o razón social"
                  maxlength="200"
                />
                <span v-if="errores.razon_social" class="field-error">{{ errores.razon_social }}</span>
              </div>

              <div class="field">
                <label class="field-label">RUC {{ editando ? '' : '*' }}</label>
                <div class="ruc-input-wrapper">
                    <input
                    v-model="form.ruc"
                    class="field-input"
                    :class="{ error: errores.ruc, encontrado: proveedorEncontrado }"
                    placeholder="11 dígitos"
                    maxlength="11"
                    :disabled="editando"
                    />
                    <span v-if="buscandoRuc" class="ruc-status">
                    <span class="spinner-sm" />
                    </span>
                    <span v-else-if="proveedorEncontrado" class="ruc-status encontrado">
                    <Check :size="13" />
                    </span>
                </div>
                <span v-if="errores.ruc" class="field-error">{{ errores.ruc }}</span>
                <span v-if="proveedorEncontrado" class="field-hint" style="color:var(--color-success)">
                    Proveedor existente — datos pre-cargados. Se creará una nueva relación comercial.
                </span>
                <span v-if="editando" class="field-hint">No modificable</span>
                </div>

              <div class="field">
                <label class="field-label">Referencia / Procedencia</label>
                <input
                  v-model="form.referencia"
                  class="field-input"
                  placeholder="Comunidad, zona, referencia"
                  maxlength="200"
                />
              </div>

              <div class="field">
                <label class="field-label">Teléfono</label>
                <input
                  v-model="form.telefono"
                  class="field-input"
                  placeholder="9XXXXXXXX"
                  maxlength="20"
                />
              </div>

              <div class="field">
                <label class="field-label">Email</label>
                <input
                  v-model="form.email"
                  class="field-input"
                  :class="{ error: errores.email }"
                  type="email"
                  placeholder="correo@ejemplo.com"
                  maxlength="200"
                />
                <span v-if="errores.email" class="field-error">{{ errores.email }}</span>
              </div>
            </div>

            <!-- ─── SECCIÓN 1: Acopiador ───────────────────────────────── -->
            <div v-show="seccionActual === 1" class="form-acopiador">

              <div v-if="editando" class="acopiador-readonly">
                <p class="acopiador-readonly-label">ACOPIADOR ASIGNADO</p>
                <p class="acopiador-readonly-nombre">
                  {{ terceroOriginal?.acopiador?.razon_social ?? '—' }}
                  <span v-if="terceroOriginal?.acopiador?.es_propio" class="badge-propio">PROPIO</span>
                </p>
                <p class="acopiador-readonly-hint">El acopiador no puede modificarse una vez asignado.</p>
              </div>

              <template v-else>
                <!-- Las 2 opciones principales -->
                <div class="tipo-grid-2">
                    <button
                    v-for="opt in tiposAcopiador"
                    :key="opt.value"
                    class="tipo-btn"
                    :class="{ selected: esTipoActivo(opt.value) }"
                    type="button"
                    @click="seleccionarTipo(opt.value)"
                    >
                    <component :is="opt.icon" :size="22" class="tipo-icon" />
                    <span class="tipo-nombre">{{ opt.label }}</span>
                    <span class="tipo-desc">{{ opt.desc }}</span>
                    </button>
                </div>

                <!-- Dropdown — solo si eligió Con Acopiador -->
                <template v-if="form.tipo_acopiador !== 'sin_acopiador'">
                    <div class="field" style="margin-top:1.25rem">
                    <label class="field-label">Acopiador *</label>
                    <select
                        v-model="form.acopiador_id"
                        class="field-input field-select"
                        :class="{ error: errores.acopiador_id }"
                        @change="onAcopiadorChange"
                    >
                        <option :value="null" disabled>— Seleccione un acopiador —</option>
                        <option v-for="a in store.acopiadores" :key="a.id" :value="a.id">
                        {{ a.razon_social }} {{ a.ruc ? `(${a.ruc})` : '' }}
                        </option>
                    </select>
                    <span v-if="errores.acopiador_id" class="field-error">{{ errores.acopiador_id }}</span>
                    </div>

                    <!-- Registrar nuevo -->
                    <template>
                        <Transition name="slide-down">
                            <div v-if="mostrarNuevoAcopiador" class="nuevo-acop-form">
                            <div class="nuevo-acop-header">
                                <span class="field-label" style="margin:0">Registrar nuevo acopiador</span>
                                <button class="btn-icon" @click="mostrarNuevoAcopiador = false">
                                <X :size="13" />
                                </button>
                            </div>
                            <div class="form-grid" style="margin-top:0.75rem">
                                <div class="field field-full">
                                <label class="field-label">Razón Social *</label>
                                <input
                                    v-model="nuevoAcopiador.razon_social"
                                    class="field-input"
                                    placeholder="Nombre del acopiador"
                                />
                                </div>
                                <div class="field">
                                <label class="field-label">RUC (opcional)</label>
                                <input
                                    v-model="nuevoAcopiador.ruc"
                                    class="field-input"
                                    placeholder="11 dígitos"
                                    maxlength="11"
                                />
                                </div>
                            </div>
                            </div>
                        </Transition>

                        <button
                            v-if="!mostrarNuevoAcopiador"
                            class="btn-nuevo-acop"
                            @click="mostrarNuevoAcopiador = true"
                        >
                            <Plus :size="13" />
                            Registrar nuevo acopiador
                        </button>
                        </template>
                </template>
                </template>
            </div>

            <!-- ─── SECCIÓN 2: Parámetros Comerciales ─────────────────── -->
            <div v-show="seccionActual === 2" class="form-params">

              <div v-if="soloLecturaParams" class="params-readonly-notice">
                <span class="params-icon">👁</span>
                <span>Solo lectura — Tu rol no permite editar parámetros comerciales.</span>
              </div>

              <div class="params-grupo">
                <p class="params-grupo-titulo">Umbrales de Recuperación</p>
                <div class="form-grid">
                  <div class="field">
                    <label class="field-label">Umbral Recup. Bajo (%)</label>
                    <input v-model.number="form.params.umbral_recup_bajo" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.umbral_recup_bajo" class="field-error">
                        {{ errores.umbral_recup_bajo }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">Umbral Recup. Medio (%)</label>
                    <input v-model.number="form.params.umbral_recup_medio" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.umbral_recup_medio" class="field-error">
                        {{ errores.umbral_recup_medio }}
                    </span>
                </div>
                  <div class="field">
                    <label class="field-label">Ley Inferior</label>
                    <input v-model.number="form.params.lim_ley_inferior" type="number" step="0.001" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.lim_ley_inferior" class="field-error">
                        {{ errores.lim_ley_inferior }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">Ley Superior</label>
                    <input v-model.number="form.params.lim_ley_superior" type="number" step="0.001" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.lim_ley_superior" class="field-error">
                        {{ errores.lim_ley_superior }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="params-grupo">
                <p class="params-grupo-titulo">Gastos y Comisiones</p>
                <div class="form-grid">
                  <div class="field">
                    <label class="field-label">Gasto Acopio (US$/TM)</label>
                    <input v-model.number="form.params.gasto_acopio" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.gasto_acopio" class="field-error">
                        {{ errores.gasto_acopio }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">Gasto Consumo</label>
                    <input v-model.number="form.params.gasto_consumo" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.gasto_consumo" class="field-error">
                        {{ errores.gasto_consumo }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">Maquila (%)</label>
                    <input v-model.number="form.params.maquila" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.maquila" class="field-error">
                        {{ errores.maquila }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">Comisión (%)</label>
                    <input v-model.number="form.params.comision" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.comision" class="field-error">
                        {{ errores.comision }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">Riesgo Comercial</label>
                    <input v-model.number="form.params.riesgo_comercial" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.riesgo_comercial" class="field-error">
                        {{ errores.riesgo_comercial }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="params-grupo">
                <p class="params-grupo-titulo">Ley Comercial</p>
                <div class="form-grid">
                  <div class="field">
                    <label class="field-label">Límite Ley Comercial</label>
                    <input v-model.number="form.params.lim_ley_comercial" type="number" step="0.001" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.lim_ley_comercial" class="field-error">
                        {{ errores.lim_ley_comercial }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">Descuento Ley Comercial</label>
                    <input v-model.number="form.params.dscto_ley_comercial" type="number" step="0.001" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.dscto_ley_comercial" class="field-error">
                        {{ errores.dscto_ley_comercial }}
                    </span>
                  </div>
                  <div class="field">
                    <label class="field-label">% Ley Comercial</label>
                    <input v-model.number="form.params.porcentaje_ley_comercial" type="number" step="0.01" class="field-input" placeholder="—" :disabled="soloLecturaParams" />
                    <span v-if="errores.porcentaje_ley_comercial" class="field-error">
                        {{ errores.porcentaje_ley_comercial }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

          </div><!-- /modal-body -->

          <!-- Footer -->
          <div class="modal-footer">
            <button
              v-if="seccionActual > 0"
              class="btn-secondary"
              @click="seccionActual--"
              :disabled="guardando"
            >← Anterior</button>
            <span class="footer-spacer" />
            <button class="btn-secondary" @click="cerrar" :disabled="guardando">
              Cancelar
            </button>
            <button
              v-if="seccionActual < secciones.length - 1"
              class="btn-primary ready"
              @click="avanzar"
            >
              Siguiente →
            </button>
            <button
              v-else
              class="btn-primary ready"
              @click="guardar"
              :disabled="guardando"
            >
              <span v-if="guardando" class="spinner" />
              {{ guardando ? 'Guardando…' : (editando ? 'Guardar cambios' : 'Registrar') }}
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTercerosStore } from '@/stores/terceros'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import tercerosApi from '@/api/terceros'
import type { TerceroRespuesta, ParametrosComerciales, TipoAcopiador } from '@/api/terceros'
import {
  Pencil, Plus, X, Check, ArrowLeft, ArrowRight,
  Link2Off, AlertTriangle, Eye, ChevronUp,
  CircleUser, Users, UserCheck,
} from 'lucide-vue-next'

// ── Props / Emits ────────────────────────────────────────────────────────────
const props = defineProps<{
  visible:   boolean
  terceroId: number | null  // null = crear, number = editar
}>()

const emit = defineEmits<{
  (e: 'cerrar'): void
  (e: 'guardado', tercero: TerceroRespuesta): void
}>()

// ── Stores ───────────────────────────────────────────────────────────────────
const store    = useTercerosStore()
const auth     = useAuthStore()
const ui       = useUiStore()

// ── State ─────────────────────────────────────────────────────────────────────
const editando          = computed(() => props.terceroId !== null)
const seccionActual     = ref(0)
const guardando         = ref(false)
const mostrarNuevoAcopiador = ref(false)
const terceroOriginal   = ref<TerceroRespuesta | null>(null)

const secciones = ['Datos del Proveedor', 'Acopiador', 'Parámetros Comerciales']

const tiposAcopiador = [
  {
    value: 'sin_acopiador' as TipoAcopiador,
    icon: CircleUser,
    label: 'Sin Acopiador',
    desc: 'El proveedor se autogestiona',
  },
  {
    value: 'tercero' as TipoAcopiador,  // default para "con acopiador"
    icon: Users,
    label: 'Con Acopiador',
    desc: 'Seleccionar de la lista',
  },
]

// Estado del autocomplete
const buscandoRuc    = ref(false)
const proveedorEncontrado = ref(false)

function seleccionarTipo(tipo: TipoAcopiador) {
  form.value.tipo_acopiador = tipo
  form.value.acopiador_id   = null
  mostrarNuevoAcopiador.value = false
  nuevoAcopiador.value = { razon_social: '', ruc: '' }
}

// ── Permisos ─────────────────────────────────────────────────────────────────
const soloLecturaParams = computed(() => {
  const rol = auth.user?.rol
  return rol === 'Comercial'
})

// ── Form model ───────────────────────────────────────────────────────────────
function emptyParams(): ParametrosComerciales {
  return {
    umbral_recup_bajo: null, umbral_recup_medio: null,
    lim_ley_inferior: null,  lim_ley_superior: null,
    gasto_acopio: null,      gasto_consumo: null,
    maquila: null,           comision: null,
    lim_ley_comercial: null, dscto_ley_comercial: null,
    porcentaje_ley_comercial: null, riesgo_comercial: null,
  }
}

const form = ref({
  razon_social:    '',
  ruc:             '',
  referencia:      '',
  telefono:        '',
  email:           '',
  tipo_acopiador:  'sin_acopiador' as TipoAcopiador,
  acopiador_id:    null as number | null,
  params:          emptyParams(),
})

const nuevoAcopiador = ref({ razon_social: '', ruc: '' })
const errores        = ref<Record<string, string>>({})

// ── Watchers ─────────────────────────────────────────────────────────────────

// Debounce — busca cuando el RUC tiene 11 dígitos
watch(() => form.value.ruc, async (ruc) => {
  if (editando.value) return
  proveedorEncontrado.value = false

  if (!/^\d{11}$/.test(ruc)) return

  buscandoRuc.value = true
  try {
    const encontrado = await tercerosApi.buscarPorRuc(ruc)
    if (encontrado) {
      form.value.razon_social = encontrado.razon_social
      form.value.referencia   = encontrado.referencia ?? ''
      form.value.telefono     = encontrado.telefono   ?? ''
      form.value.email        = encontrado.email      ?? ''
      proveedorEncontrado.value = true
      ui.toast(`Proveedor encontrado: ${encontrado.razon_social}`, 'info')
    }
  } catch {
    // silencioso
  } finally {
    buscandoRuc.value = false
  }
})

watch(() => props.visible, async (v) => {
  if (!v) return
  seccionActual.value = 0
  errores.value       = {}
  mostrarNuevoAcopiador.value = false

  // Cargar acopiadores disponibles
  await store.cargarAcopiadores()

  if (props.terceroId !== null) {
    // Modo edición — cargar datos del tercero
    try {
      const t = await store.obtener(props.terceroId)
      terceroOriginal.value = t
      form.value = {
        razon_social:   t.razon_social,
        ruc:            t.ruc ?? '',
        referencia:     t.referencia ?? '',
        telefono:       t.telefono ?? '',
        email:          t.email ?? '',
        tipo_acopiador: 'sin_acopiador', // no editable
        acopiador_id:   null,
        params: t.parametros ? { ...t.parametros } : emptyParams(),
      }
    } catch {
      ui.toast('No se pudo cargar el tercero', 'error')
      cerrar()
    }
  } else {
    // Modo crear — resetear
    terceroOriginal.value = null
    form.value = {
      razon_social: '', ruc: '', referencia: '',
      telefono: '', email: '',
      tipo_acopiador: 'sin_acopiador',
      acopiador_id: null,
      params: emptyParams(),
    }
    nuevoAcopiador.value = { razon_social: '', ruc: '' }
  }
})

// ── Helpers ──────────────────────────────────────────────────────────────────
function irA(idx: number) {
  // Solo navegar hacia atrás libremente; avanzar valida
  if (idx < seccionActual.value) seccionActual.value = idx
  else avanzarHasta(idx)
}

async function onAcopiadorChange() {
  if (!form.value.acopiador_id) return
  try {
    const params = await store.parametrosAcopiador(form.value.acopiador_id)
    if (params) {
      form.value.params = { ...params }
      ui.toast('Parámetros pre-cargados del acopiador', 'info')
    }
  } catch {
    // silencioso
  }
}

function esTipoActivo(valor: TipoAcopiador): boolean {
  if (valor === 'sin_acopiador') return form.value.tipo_acopiador === 'sin_acopiador'
  // "Con Acopiador" activo si tipo es propio o tercero
  return ['propio', 'tercero'].includes(form.value.tipo_acopiador)
}

function validarSeccion(idx: number): boolean {
  const e: Record<string, string> = {}

  if (idx === 0) {
    if (!form.value.razon_social.trim())
      e.razon_social = 'Campo requerido'
    if (!editando.value) {
      if (!form.value.ruc.trim())
        e.ruc = 'Campo requerido'
      else if (!/^\d{11}$/.test(form.value.ruc))
        e.ruc = 'Debe tener exactamente 11 dígitos'
    }
    if (form.value.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email))
      e.email = 'Email inválido'
  }

  if (idx === 1 && !editando.value) {
    if (form.value.tipo_acopiador === 'tercero' && !form.value.acopiador_id && !nuevoAcopiador.value.razon_social.trim())
      e.acopiador_id = 'Seleccione un acopiador o registre uno nuevo'
  }

  if (idx === 2 && !soloLecturaParams.value) {
    const p = form.value.params

    // Porcentajes: 0-100
    const camposPct: Array<keyof typeof p> = ['umbral_recup_bajo', 'umbral_recup_medio', 'maquila', 'comision']
    for (const campo of camposPct) {
        const v = p[campo]
        if (v !== null && v !== undefined) {
        if (v < 0 || v > 100)
            e[campo] = 'Debe estar entre 0 y 100'
        }
    }

    // Leyes y factores: 0-9999
    const camposLey: Array<keyof typeof p> = [
        'lim_ley_inferior', 'lim_ley_superior',
        'lim_ley_comercial', 'dscto_ley_comercial',
        'porcentaje_ley_comercial',
    ]
    for (const campo of camposLey) {
        const v = p[campo]
        if (v !== null && v !== undefined && v < 0)
        e[campo] = 'Debe ser un valor positivo'
    }

    // Gastos: positivos
    const camposGasto: Array<keyof typeof p> = ['gasto_acopio', 'gasto_consumo', 'riesgo_comercial']
    for (const campo of camposGasto) {
        const v = p[campo]
        if (v !== null && v !== undefined && v < 0)
        e[campo] = 'Debe ser un valor positivo'
    }
    }

  errores.value = e
  return Object.keys(e).length === 0
}

function avanzar() {
  if (validarSeccion(seccionActual.value))
    seccionActual.value++
}

function avanzarHasta(target: number) {
  for (let i = seccionActual.value; i < target; i++) {
    if (!validarSeccion(i)) {
      seccionActual.value = i
      return
    }
    seccionActual.value = i + 1
  }
}

function cerrar() {
  emit('cerrar')
}

// ── Guardar ──────────────────────────────────────────────────────────────────
// Limpiar params: nullear campos vacíos para no mandar 0 por defecto
function limpiarParams(p: ParametrosComerciales): Partial<ParametrosComerciales> | null {
  const limpio: Partial<ParametrosComerciales> = {}
  let alguno = false
  for (const [k, v] of Object.entries(p)) {
    if (v !== null && v !== undefined && v !== '') {
      ;(limpio as Record<string, unknown>)[k] = v
      alguno = true
    }
  }
  return alguno ? limpio : null
}

async function guardar() {
  // Validar todas las secciones
  for (let i = 0; i < secciones.length; i++) {
    if (!validarSeccion(i)) {
      seccionActual.value = i
      return
    }
  }

  guardando.value = true
  try {
    let resultado: TerceroRespuesta

    if (editando.value) {
      resultado = await store.editar(props.terceroId!, {
        razon_social: form.value.razon_social,
        referencia:   form.value.referencia || null,
        telefono:     form.value.telefono   || null,
        email:        form.value.email      || null,
        parametros:   soloLecturaParams.value ? undefined : limpiarParams(form.value.params),
      })
      ui.toast(`${resultado.razon_social} actualizado`, 'success')
    } else {
      const payload: Parameters<typeof store.crear>[0] = {
        razon_social:   form.value.razon_social,
        ruc:            form.value.ruc || null,
        referencia:     form.value.referencia || null,
        telefono:       form.value.telefono   || null,
        email:          form.value.email      || null,
        tipo_acopiador: form.value.tipo_acopiador,
        parametros:     limpiarParams(form.value.params),
      }

      if (form.value.tipo_acopiador === 'tercero') {
        if (mostrarNuevoAcopiador.value && nuevoAcopiador.value.razon_social.trim()) {
          payload.acopiador_nuevo = {
            razon_social: nuevoAcopiador.value.razon_social,
            ruc: nuevoAcopiador.value.ruc || null,
          }
        } else {
          payload.acopiador_id = form.value.acopiador_id
        }
      }

      resultado = await store.crear(payload)
      ui.toast(`${resultado.razon_social} registrado`, 'success')
    }

    emit('guardado', resultado)
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })
      ?.response?.data?.detail ?? 'Error al guardar'
    ui.toast(msg, 'error')
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
/* ── Modal base ────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 10, 8, 0.82);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  backdrop-filter: blur(2px);
}

.modal {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
}

.modal-lg {
  width: 100%;
  max-width: 680px;
}

/* ── Header ──────────────────────────────────────────────────── */
.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.modal-icon {
  font-size: 1.1rem;
  color: var(--color-gold);
  font-family: var(--font-mono);
}

.modal-header h2 {
  font-size: 1rem;
  color: var(--color-gold-light);
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  font-weight: 600;
}

.modal-steps {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.step-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1.5px solid var(--color-border);
  background: transparent;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-dot.active {
  border-color: var(--color-gold);
  color: var(--color-gold);
  background: rgba(179, 144, 40, 0.12);
}

.step-dot.done {
  border-color: var(--color-success);
  color: var(--color-success);
  background: rgba(81, 161, 85, 0.1);
}

.step-num { line-height: 1; }

.modal-close {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.15s;
  font-family: var(--font-mono);
  flex-shrink: 0;
}
.modal-close:hover { color: var(--color-error); }

/* ── Sección título ──────────────────────────────────────────── */
.seccion-titulo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1.5rem;
  background: rgba(179, 144, 40, 0.05);
  border-bottom: 1px solid var(--color-border);
  font-size: 0.8rem;
  font-family: var(--font-mono);
  color: var(--color-text);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  flex-shrink: 0;
}

.seccion-num {
  color: var(--color-text-muted);
  font-size: 0.7rem;
}

/* ── Body ────────────────────────────────────────────────────── */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* ── Form grid ───────────────────────────────────────────────── */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.field-full { grid-column: 1 / -1; }

.field-error { font-size: 0.72rem; color: var(--color-error); margin-top: 0.2rem; }
.field-hint  { font-size: 0.72rem; color: var(--color-text-faint); margin-top: 0.2rem; }

.field-input.error { border-color: var(--color-error); }

/* ── Acopiador section ───────────────────────────────────────── */
.tipo-acopiador-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.tipo-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 1rem 0.5rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  transition: all 0.15s;
  text-align: center;
}

.tipo-btn:hover {
  border-color: var(--color-border-focus);
  background: var(--color-gold-bg);
}

.tipo-btn.selected {
  border-color: var(--color-gold);
  background: rgba(179, 144, 40, 0.1);
}

.tipo-icon  { font-size: 1.4rem; color: var(--color-gold); }
.tipo-nombre {
  font-size: 0.8rem;
  font-family: var(--font-mono);
  color: var(--color-text);
  letter-spacing: 0.05em;
}
.tipo-desc {
  font-size: 0.68rem;
  color: var(--color-text-muted);
  line-height: 1.3;
}

.field-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%238a8762' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2rem;
}

.nuevo-acopiador-form {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  background: rgba(179, 144, 40, 0.03);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-gold);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 3px;
  transition: color 0.15s;
}
.btn-link:hover { color: var(--color-text); }

/* ── Readonly acopiador (edit mode) ──────────────────────────── */
.acopiador-readonly {
  padding: 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-gold-bg);
}

.acopiador-readonly-label {
  font-size: 0.68rem;
  letter-spacing: 0.15em;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  margin-bottom: 0.5rem;
}

.acopiador-readonly-nombre {
  font-size: 1rem;
  color: var(--color-text);
  font-family: var(--font-main);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.badge-propio {
  font-size: 0.62rem;
  background: rgba(179, 144, 40, 0.2);
  color: var(--color-gold);
  border: 1px solid var(--color-gold);
  padding: 0.1rem 0.4rem;
  border-radius: 2px;
  font-family: var(--font-mono);
  letter-spacing: 0.1em;
}

.acopiador-readonly-hint {
  font-size: 0.72rem;
  color: var(--color-text-faint);
  margin-top: 0.4rem;
}

.nuevo-acop-form {
  margin-top: 0.75rem;
  padding: 1rem;
  border: 1px dashed var(--color-border-focus);
  border-radius: var(--radius-sm);
  background: rgba(179, 144, 40, 0.03);
}

.nuevo-acop-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-nuevo-acop {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.75rem;
  background: transparent;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  padding: 0.4rem 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-nuevo-acop:hover {
  border-color: var(--color-gold);
  color: var(--color-gold);
}

/* Transición slide */
.slide-down-enter-active,
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from,
.slide-down-leave-to     { opacity: 0; transform: translateY(-6px); }

/* ── Parámetros section ──────────────────────────────────────── */
.params-readonly-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1rem;
  background: rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.25);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  color: #38bdf8;
  margin-bottom: 1.25rem;
  font-family: var(--font-mono);
}

.params-grupo {
  margin-bottom: 1.5rem;
}

.params-grupo-titulo {
  font-size: 0.68rem;
  letter-spacing: 0.15em;
  color: var(--color-gold);
  font-family: var(--font-mono);
  text-transform: uppercase;
  margin-bottom: 0.75rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--color-border);
}

.tipo-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.toggle-interno {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.85rem;
  cursor: pointer;
  width: fit-content;
}

.toggle-checkbox {
  width: 15px;
  height: 15px;
  accent-color: var(--color-gold);
  cursor: pointer;
  flex-shrink: 0;
}

.toggle-label {
  font-size: 0.82rem;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
}

.toggle-hint {
  font-size: 0.72rem;
  color: var(--color-text-faint);
  margin-left: 0.3rem;
}

.ruc-input-wrapper {
  position: relative;
}

.ruc-input-wrapper .field-input {
  padding-right: 2.2rem;
}

.ruc-status {
  position: absolute;
  right: 0.65rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  color: var(--color-text-muted);
}

.ruc-status.encontrado {
  color: var(--color-success);
}

.field-input.encontrado {
  border-color: var(--color-success);
}

/* ── Footer ──────────────────────────────────────────────────── */
.modal-footer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.footer-spacer { flex: 1; }

/* ── Utilities ───────────────────────────────────────────────── */
.mt-sm { margin-top: 0.75rem; }
.mt-md { margin-top: 1rem; }
.mb-sm { margin-bottom: 0.5rem; }

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(26, 26, 20, 0.3);
  border-top-color: #1a1a14;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 6px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Transition ──────────────────────────────────────────────── */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,  .modal-leave-to      { opacity: 0; }
.modal-enter-active .modal,
.modal-leave-active .modal { transition: transform 0.2s ease; }
.modal-enter-from .modal   { transform: translateY(-16px); }
.modal-leave-to .modal     { transform: translateY(8px); }

@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
  .tipo-acopiador-grid { grid-template-columns: 1fr; }
  .field-full { grid-column: 1; }
}
</style>
