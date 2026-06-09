<template>
    <div class="page-container">

      <!-- ── Header ────────────────────────────────────────────── -->
      <header class="page-header">
        <div style="display:flex;align-items:center;gap:0.75rem">
          <button class="btn-back" @click="router.back()">
            <ChevronLeft :size="20" />
          </button>
          <div>
            <h1 class="page-title">
              <FilePlus :size="24" style="margin-right:0.5rem" />
              Nueva Liquidación
            </h1>
            <p class="page-subtitle">Paso {{ paso }} de 3 — {{ tituloPaso }}</p>
          </div>
        </div>
      </header>

      <!-- ── Stepper ───────────────────────────────────────────── -->
      <div class="stepper">
        <div v-for="n in 3" :key="n" class="step" :class="{ active: paso === n, done: paso > n }">
          <span class="step-num">{{ paso > n ? '✓' : n }}</span>
          <span class="step-label">{{ ['Selección', 'Preview', 'Confirmar'][n-1] }}</span>
        </div>
        <div class="step-line" />
      </div>

      <!-- ════════════════════════════════════════════════════════
           PASO 1: Selección de provacop y lotes
      ════════════════════════════════════════════════════════════ -->
      <template v-if="paso === 1">

        <!-- Selección de provacop -->
        <div class="seccion-card">
          <p class="seccion-titulo">PARÁMETROS DE LIQUIDACIÓN</p>
          <div class="form-grid">
            <div class="field">
              <label class="field-label">PROVEEDOR / ACOPIADOR</label>
              <select class="field-input field-select" v-model="provacopId" @change="onProvacopChange">
                <option value="">Seleccionar…</option>
                <option v-for="p in provacops" :key="p.id" :value="p.id">
                  {{ p.proveedor }} – {{ p.acopiador }}
                </option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">PRECIO SPOT ORO (USD/Oz Troy)</label>
              <input
                type="number"
                class="field-input"
                v-model.number="spotUsd"
                min="0"
                step="0.01"
                placeholder="ej: 3050.00"
              />
            </div>
            <div class="field">
              <label class="field-label">SPOT PLATA Ag (USD/Oz) <span style="color:var(--color-text-faint);font-size:var(--text-xs);font-weight:400;text-transform:none">(opcional)</span></label>
              <input
                type="number"
                class="field-input"
                v-model.number="spotAgUsd"
                min="0"
                step="0.01"
                placeholder="ej: 32.00"
              />
            </div>
            <div class="field">
              <label class="field-label">FECHA LIQUIDACIÓN</label>
              <input type="date" class="field-input" v-model="fechaLiq" />
            </div>
          </div>
        </div>

        <!-- Tabla de lotes disponibles -->
        <div v-if="provacopId" class="seccion-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem">
            <p class="seccion-titulo" style="margin:0">LOTES DISPONIBLES</p>
            <span class="badge-lotes-sel">{{ lotesSeleccionados.length }} seleccionados</span>
          </div>

          <div v-if="store.cargando" class="cargando-inline">
            <span class="spinner" /> Cargando lotes…
          </div>
          <div v-else-if="lotesListos.length === 0" class="sin-lotes">
            Sin lotes disponibles para este proveedor-acopiador
          </div>
          <div v-else class="tabla-wrapper">
            <table class="tabla">
              <thead>
                <tr>
                  <th><input type="checkbox" :checked="todosSeleccionados" @change="toggleTodos" class="check" /></th>
                  <th>IP</th>
                  <th>MATERIAL</th>
                  <th>RECEPCIÓN</th>
                  <th class="col-r">TMS</th>
                  <th class="col-r">LEY PLANTA</th>
                  <th class="col-r">LEY MINERO</th>
                  <th class="col-r">LEY COMERC.</th>
                  <th class="col-r">% REC</th>
                  <th>ESTADO</th>
                  <th class="col-r">DÍAS</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="lote in lotesListos"
                  :key="lote.ip"
                  class="tabla-row"
                  :class="{ 'fila-volado': lote.volado, 'fila-vencimiento': lote.alerta_vencimiento && !lote.volado }"
                  @click="toggleLote(lote.ip)"
                  style="cursor:pointer"
                >
                  <td @click.stop>
                    <input type="checkbox" :checked="lotesSeleccionados.includes(lote.ip)" @change="toggleLote(lote.ip)" class="check" />
                  </td>
                  <td class="td-mono" style="color:var(--color-gold)">{{ lote.ip }}</td>
                  <td class="td-muted">{{ lote.tipo_material || '—' }}</td>
                  <td class="td-fecha">{{ fmtDate(lote.fecha_recepcion) }}</td>
                  <td class="col-r td-mono">{{ fmtNum(lote.tms, 3) }}</td>
                  <td class="col-r td-mono td-muted">{{ fmtNum(lote.oz_tc_planta, 4) }}</td>
                  <td class="col-r td-mono td-muted">{{ fmtNum(lote.oz_tc_minero, 4) }}</td>
                  <td class="col-r td-mono" style="color:var(--color-gold)">{{ fmtNum(lote.ley_comercial, 4) }}</td>
                  <td class="col-r td-mono">{{ fmtNum(lote.porcentaje_rec, 1) }}%</td>
                  <td>
                    <span v-if="lote.usa_dirimencia" class="alerta-tag alerta-dirim">DIRIM</span>
                    <span v-else-if="lote.volado" class="alerta-tag alerta-volado">VOLADO</span>
                    <span v-else-if="lote.alerta_vencimiento" class="alerta-tag alerta-venc">{{ lote.dias_almacen }}D</span>
                  </td>
                  <td class="col-r">
                    <span class="dias-badge" :class="{'dias-warn':lote.alerta_vencimiento,'dias-danger':lote.dias_almacen>=30}">
                      {{ lote.dias_almacen }}d
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="acciones-pie">
          <span v-if="errorPaso1" class="error-inline">
            <AlertTriangle :size="14" style="margin-right:0.3rem" /> {{ errorPaso1 }}
          </span>
          <button
            class="btn-primary ready"
            :disabled="!puedeCalcular"
            @click="calcularPreview"
          >
            <template v-if="store.cargando">
              <span class="spinner" style="margin-right:0.5rem" /> Calculando…
            </template>
            <template v-else>
              Calcular Preview →
            </template>
          </button>
        </div>
      </template>

      <!-- ════════════════════════════════════════════════════════
           PASO 2: Preview de resultados
      ════════════════════════════════════════════════════════════ -->
      <template v-if="paso === 2 && store.preview">

        <!-- Alertas críticas -->
        <div v-if="alertasCriticas.length" class="alertas-bloque criticas">
          <AlertTriangle :size="16" style="margin-right:0.5rem;flex-shrink:0" />
          <div>
            <p class="alerta-titulo">No se puede generar la liquidación:</p>
            <ul>
              <li v-for="a in alertasCriticas" :key="a.mensaje">{{ a.mensaje }}</li>
            </ul>
          </div>
        </div>

        <!-- Alertas informativas -->
        <div v-if="alertasInfo.length" class="alertas-bloque info">
          <Info :size="16" style="margin-right:0.5rem;flex-shrink:0" />
          <div>
            <p class="alerta-titulo">Observaciones:</p>
            <ul>
              <li v-for="a in alertasInfo" :key="a.mensaje">{{ a.mensaje }}</li>
            </ul>
          </div>
        </div>

        <!-- Encabezado proveedor -->
        <div class="seccion-card resumen-header">
          <div class="resumen-col">
            <span class="resumen-lbl">PROVEEDOR</span>
            <span class="resumen-val">{{ store.preview.proveedor_razon_social }}</span>
            <span class="resumen-sub">RUC: {{ store.preview.proveedor_ruc ?? '-' }}</span>
          </div>
          <div class="resumen-col">
            <span class="resumen-lbl">ACOPIADOR</span>
            <span class="resumen-val">{{ store.preview.acopiador_nombre }}</span>
          </div>
          <div class="resumen-col">
            <span class="resumen-lbl">SPOT ORO</span>
            <span class="resumen-val">${{ fmtNum(store.preview.spot_usd, 2) }} /Oz</span>
          </div>
          <div class="resumen-col">
            <span class="resumen-lbl">TOTAL TMS</span>
            <span class="resumen-val">{{ fmtNum(store.preview.total_tms, 3) }} TMS</span>
          </div>
          <div class="resumen-col resumen-total">
            <span class="resumen-lbl">TOTAL USD (Au)</span>
            <span class="resumen-val-big">${{ fmtNum(store.preview.total_usd, 2) }}</span>
          </div>
          <div v-if="hayAg" class="resumen-col resumen-total-ag">
            <span class="resumen-lbl">TOTAL AG (Plata)</span>
            <span class="resumen-val-ag">${{ fmtNum(store.preview.total_ag_usd, 2) }}</span>
          </div>
        </div>

        <!-- Tabla de detalle por lote -->
        <div class="tabla-wrapper tabla-scroll-x">
          <table class="tabla tabla-preview">
            <thead>
              <tr>
                <th>LOTE</th>
                <th>RECEPCIÓN</th>
                <th>TMH</th>
                <th>%H₂O</th>
                <th>TMS</th>
                <th>LEY PLANTA</th>
                <th>LEY COMERC.</th>
                <th>LEY MINERO</th>
                <th>PROMEDIO</th>
                <th>%REC LIQ</th>
                <th>MAQUILA</th>
                <th>INSUMOS</th>
                <th>PRECIO/TMS</th>
                <!-- Columnas Ag (opcionales) -->
                <th v-if="hayAg" class="col-ag">Ag Gr/TM</th>
                <th v-if="hayAg" class="col-ag">Ag Oz/TC</th>
                <th v-if="hayAg" class="col-ag">VALOR Ag</th>
                <th>TOTAL USD</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="lote in store.preview.lotes"
                :key="lote.ip"
                class="tabla-row"
              >
                <td class="td-mono" style="color:var(--color-gold)">
                  {{ lote.ip }}
                  <span v-if="lote.usa_dirimencia" class="badge-dirimencia" title="Usó dirimencia">D</span>
                </td>
                <td class="td-fecha">{{ fmtDate(lote.fecha_recepcion) }}</td>
                <td class="td-mono td-right">{{ fmtNum(lote.tmh, 3) }}</td>
                <td class="td-mono td-right">{{ fmtNum(lote.pct_humedad, 2) }}%</td>
                <td class="td-mono td-right">{{ fmtNum(lote.tms, 3) }}</td>
                <td class="td-mono td-right">{{ fmtNum(lote.oz_tc_planta, 4) }}</td>
                <td class="td-mono td-right">{{ fmtNum(lote.oz_tc_comercial, 4) }}</td>
                <td class="td-mono td-right">{{ fmtNum(lote.oz_tc_minero, 4) }}</td>
                <td class="td-mono td-right" style="color:var(--color-gold)">{{ fmtNum(lote.oz_tc_promedio, 4) }}</td>
                <td class="td-mono td-right">{{ fmtNum(lote.pct_rec_liq, 1) }}%</td>
                <td class="td-mono td-right">{{ fmtNum(lote.maquila, 2) }}</td>
                <td class="td-mono td-right">${{ fmtNum(lote.insumos_total, 2) }}</td>
                <td class="td-mono td-right">${{ fmtNum(lote.precio_x_tms, 4) }}</td>
                <!-- Ag (opcionales) -->
                <td v-if="hayAg" class="td-mono td-right col-ag">{{ fmtNum(lote.ley_ag_gr_tm, 2) }}</td>
                <td v-if="hayAg" class="td-mono td-right col-ag">{{ fmtNum(lote.ley_ag_oz_tc, 4) }}</td>
                <td v-if="hayAg" class="td-mono td-right col-ag total-ag-cel">${{ fmtNum(lote.valor_ag_usd, 2) }}</td>
                <td class="td-mono td-right total-cel">${{ fmtNum(lote.total_usd, 2) }}</td>
              </tr>
              <!-- Fila total -->
              <tr class="fila-total">
                <td colspan="4" style="text-align:right">TOTALES</td>
                <td class="td-mono td-right">{{ fmtNum(store.preview.total_tms, 3) }}</td>
                <td colspan="8" />
                <!-- celdas vacías para columnas Ag -->
                <td v-if="hayAg" colspan="2" />
                <td v-if="hayAg" class="td-mono td-right total-ag-cel">${{ fmtNum(store.preview.total_ag_usd, 2) }}</td>
                <td class="td-mono td-right total-cel">${{ fmtNum(store.preview.total_usd, 2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Panel editable — solo Admin/Gerencia -->
        <div v-if="puedeEditarParams" class="params-panel">
          <p class="seccion-titulo">PARÁMETROS DE CÁLCULO</p>

          <!-- Globales (aplican a todos los lotes) -->
          <div class="params-globales">
            <div class="pfield">
              <span class="plbl">GASTO ACOPIO</span>
              <input type="number" class="pinput" v-model.number="editOv.gasto_acopio"
                step="0.01" @input="pendienteRecalculo = true" />
            </div>
            <div class="pfield">
              <span class="plbl">GASTO CONSUMO (INSUMOS LIQ)</span>
              <input type="number" class="pinput" v-model.number="editOv.gasto_consumo"
                step="0.01" @input="pendienteRecalculo = true" />
            </div>
            <div class="pfield">
              <span class="plbl">BONO</span>
              <input type="number" class="pinput" v-model.number="editOv.bono"
                step="0.01" @input="pendienteRecalculo = true" />
            </div>
          </div>

          <!-- Por lote: % Rec Liq -->
          <div class="params-por-lote">
            <div v-for="lote in store.preview.lotes" :key="lote.ip" class="pfield">
              <span class="plbl">{{ lote.ip }} — % REC LIQ</span>
              <input type="number" class="pinput" v-model.number="editOv.rec_liq[lote.ip]"
                step="0.1" min="0" max="100" @input="pendienteRecalculo = true" />
            </div>
          </div>

          <button v-if="pendienteRecalculo" class="btn-primary"
            style="margin-top:0.75rem;font-size:0.8rem"
            :disabled="store.cargando" @click="recalcularConOverrides">
            <span v-if="store.cargando" class="spinner" style="margin-right:0.4rem"/>
            Recalcular →
          </button>
        </div>

        <div class="acciones-pie">
          <button class="btn-secondary" @click="paso = 1">← Volver</button>
          <span v-if="pendienteRecalculo" class="warn-recalc">
            <AlertTriangle :size="16" class="warn-icon" />
            Hay cambios sin recalcular
          </span>
          <button
            class="btn-secondary"
            :disabled="store.cargando || pendienteRecalculo"
            @click="guardarBorrador"
          >
            <template v-if="store.cargando && guardandoBorrador">
              <span class="spinner" style="margin-right:0.4rem" /> Guardando…
            </template>
            <template v-else>
              Guardar borrador
            </template>
          </button>
          <button
            class="btn-primary ready"
            :disabled="!store.preview.puede_generar || store.cargando || pendienteRecalculo"
            @click="paso = 3"
          >
            Confirmar y Generar →
          </button>
        </div>
      </template>

      <!-- ════════════════════════════════════════════════════════
           PASO 3: Confirmación
      ════════════════════════════════════════════════════════════ -->
      <template v-if="paso === 3 && store.preview">
        <div class="confirm-panel">
          <CheckCircle :size="48" class="confirm-icon" />
          <h2 class="confirm-titulo">Confirmar liquidación</h2>
          <p class="confirm-detalle">
            Proveedor: <strong>{{ store.preview.proveedor_razon_social }}</strong><br/>
            Lotes: <strong>{{ store.preview.count_lotes }}</strong> &nbsp;|&nbsp;
            TMS: <strong>{{ fmtNum(store.preview.total_tms, 3) }}</strong> &nbsp;|&nbsp;
            Total: <strong class="total-gold">${{ fmtNum(store.preview.total_usd, 2) }}</strong>
          </p>
          <p class="confirm-aviso">
            Una vez generada, los lotes cambiarán a estado <strong>LIQUIDADO</strong> y
            se generará el PDF. Esta acción no se puede deshacer.
          </p>
          <div style="display:flex;gap:1rem;justify-content:center;margin-top:1.5rem">
            <button class="btn-secondary" @click="paso = 2" :disabled="store.cargando">Volver</button>
            <button class="btn-primary ready" :disabled="store.cargando" @click="confirmarCreacion">
              <template v-if="store.cargando">
                <span class="spinner" style="margin-right:0.5rem" /> Generando…
              </template>
              <template v-else>
                <FilePlus :size="18" style="margin-right:0.5rem" />
                GENERAR LIQUIDACIÓN
              </template>
            </button>
          </div>
        </div>
      </template>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import {
    ChevronLeft, FilePlus, AlertTriangle, Info, CheckCircle,
  } from 'lucide-vue-next'
  import { useLiquidacionesStore } from '@/stores/liquidaciones'
  import { useUiStore } from '@/stores/ui'
  import { useAuthStore } from '@/stores/auth'
  import api from '@/api/axios'
  import { obtenerPrecioOro, obtenerPrecioPlata, type EditOverrides } from '@/api/liquidaciones'

  const router = useRouter()
  const store  = useLiquidacionesStore()
  const ui     = useUiStore()
  const auth   = useAuthStore()
  const puedeEditarParams = computed(() => ['Admin', 'Gerencia'].includes(auth.user?.rol ?? ''))


  // ── State ──────────────────────────────────────────────────────────
  const paso             = ref(1)
  const provacopId       = ref<number | ''>('')
  const spotUsd          = ref<number | null>(null)
  const spotAgUsd        = ref<number | null>(null)
  const fechaLiq         = ref(new Date().toISOString().slice(0, 10))
  const lotesSeleccionados = ref<string[]>([])
  const errorPaso1       = ref('')
  const provacops        = ref<{ id: number; proveedor: string; acopiador: string }[]>([])
  const guardandoBorrador = ref(false)

  // ── Computed ───────────────────────────────────────────────────────
  const tituloPaso = computed(() => ['Selección de lotes', 'Revisión de valores', 'Confirmar'][paso.value - 1])

  const todosSeleccionados = computed(() =>
    store.lotesDisponibles.length > 0 &&
    store.lotesDisponibles.every(l => lotesSeleccionados.value.includes(l.ip))
  )

  const lotesListos = computed(() =>
    store.lotesDisponibles.filter(l => l.listo_para_liquidar)
  )

  const puedeCalcular = computed(() =>
    provacopId.value !== '' &&
    (spotUsd.value ?? 0) > 0 &&
    lotesSeleccionados.value.length > 0
  )

  const alertasCriticas = computed(() =>
    [...(store.preview?.alertas_globales ?? []), ...(store.preview?.lotes.flatMap(l => l.alertas) ?? [])]
      .filter(a => a.critico)
  )
  const alertasInfo = computed(() =>
    [...(store.preview?.alertas_globales ?? [])]
      .filter(a => !a.critico)
  )

  const hayAg = computed(() => store.preview?.hay_ag ?? false)

  const cargarPrecio = async () => {
    try {
      spotUsd.value = await obtenerPrecioOro()
    } catch {
      spotUsd.value = null
    }
    try {
      spotAgUsd.value = await obtenerPrecioPlata()
    } catch {
      spotAgUsd.value = null
    }
  }

  // ── Methods ─────────────────────────────────────────────────────────
  async function cargarProvacops() {
    try {
      const r = await api.get('/terceros/provacop', { params: { con_lotes: true } })
      provacops.value = r.data
    } catch {
      provacops.value = []
    }
  }

  async function onProvacopChange() {
    lotesSeleccionados.value = []
    if (!provacopId.value) return
    await store.cargarLotesDisponibles(provacopId.value as number)
  }

  function toggleLote(ip: string) {
    const idx = lotesSeleccionados.value.indexOf(ip)
    if (idx >= 0) lotesSeleccionados.value.splice(idx, 1)
    else lotesSeleccionados.value.push(ip)
  }

  function toggleTodos() {
    if (todosSeleccionados.value) {
      lotesSeleccionados.value = []
    } else {
      lotesSeleccionados.value = store.lotesDisponibles.map(l => l.ip)
    }
  }

  //Editar
  const editOv = ref<EditOverrides>({ gasto_acopio: null, gasto_consumo: null, bono: 0, rec_liq: {} })
const pendienteRecalculo = ref(false)

function initEditOverrides() {
  const lotes = store.preview?.lotes ?? []
  if (!lotes.length) return
  const l0 = lotes[0]
  if (!l0) return
  editOv.value.gasto_acopio  = Number(l0.insumos_acopio)  || null
  editOv.value.gasto_consumo = Number(l0.insumos_consumo) || null
  editOv.value.bono          = Number(l0.bono)            || 0
  for (const l of lotes) {
    editOv.value.rec_liq[l.ip] = Number(l.pct_rec_liq) || null
  }
  pendienteRecalculo.value = false
}

async function recalcularConOverrides() {
  if (!provacopId.value || !spotUsd.value) return
  await store.calcularPreview({
    provacop_id: provacopId.value as number,
    spot_usd: spotUsd.value,
    fecha_liquidacion: fechaLiq.value,
    lotes: lotesSeleccionados.value.map(ip => ({
      ip,
      bono: editOv.value.bono ?? 0,
      rec_liq_override: editOv.value.rec_liq[ip] ?? null,
      gasto_acopio_override: editOv.value.gasto_acopio,
      gasto_consumo_override: editOv.value.gasto_consumo,
    })),
  })
  pendienteRecalculo.value = false
}

  async function calcularPreview() {
    errorPaso1.value = ''
    if (!provacopId.value) { errorPaso1.value = 'Seleccione un proveedor-acopiador'; return }
    if (!spotUsd.value || spotUsd.value <= 0) { errorPaso1.value = 'Ingrese el precio spot del oro'; return }
    if (lotesSeleccionados.value.length === 0) { errorPaso1.value = 'Seleccione al menos un lote'; return }

    const result = await store.calcularPreview({
      provacop_id: provacopId.value as number,
      lotes: lotesSeleccionados.value.map(ip => ({ ip })),
      spot_usd: spotUsd.value,
      spot_ag_usd: spotAgUsd.value ?? null,
      fecha_liquidacion: fechaLiq.value || null,
    })
    initEditOverrides()

    if (result) paso.value = 2
    else ui.toast(store.error ?? 'Error al calcular preview', 'error')
  }

  async function confirmarCreacion() {
    const confirmed = await ui.showConfirm({
      title: 'Generar Liquidación',
      message: `¿Confirmar la liquidación por $${fmtNum(store.preview?.total_usd ?? 0, 2)} USD? Los lotes cambiarán a estado LIQUIDADO.`,
      confirmLabel: 'Generar',
      danger: false,
    })
    if (!confirmed) return

    const result = await store.crear({
      provacop_id: provacopId.value as number,
      lotes: lotesSeleccionados.value.map(ip => ({ ip })),
      spot_usd: spotUsd.value!,
      spot_ag_usd: spotAgUsd.value ?? null,
      fecha_liquidacion: fechaLiq.value || null,
    })

    if (result) {
      ui.toast(`Liquidación ${result.numero_liquidacion} generada correctamente`, 'success')
      router.push(`/liquidaciones/${result.id}`)
    } else {
      ui.toast(store.error ?? 'Error al crear liquidación', 'error')
    }
  }

  async function guardarBorrador() {
    if (!provacopId.value || !spotUsd.value) return
    guardandoBorrador.value = true
    const result = await store.crear({
      provacop_id: provacopId.value as number,
      lotes: lotesSeleccionados.value.map(ip => ({
        ip,
        bono: editOv.value.bono ?? 0,
        rec_liq_override: editOv.value.rec_liq[ip] ?? null,
        gasto_acopio_override: editOv.value.gasto_acopio,
        gasto_consumo_override: editOv.value.gasto_consumo,
      })),
      spot_usd: spotUsd.value,
      spot_ag_usd: spotAgUsd.value ?? null,
      fecha_liquidacion: fechaLiq.value || null,
      como_borrador: true,
    })
    guardandoBorrador.value = false

    if (result) {
      ui.toast(`Borrador ${result.numero_liquidacion} guardado`, 'success')
      router.push('/liquidaciones')
    } else {
      ui.toast(store.error ?? 'Error al guardar borrador', 'error')
    }
  }

  function fmtNum(v: number | null | undefined, d = 2) {
    if (v == null) return '-'
    return Number(v).toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
  }
  function fmtDate(s: string | null) {
    if (!s) return '-'
    return new Date(s).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  onMounted(() => {
    store.limpiarPreview()
    cargarProvacops()
    cargarPrecio()
  })
  </script>

  <style scoped>
  @import '@/assets/base.css';

  .page-subtitle { font-size:var(--text-sm); color:var(--color-text-muted); margin-top:0.25rem; font-family:var(--font-mono); }

  .btn-back {
    background:transparent; border:1px solid var(--color-border);
    border-radius:var(--radius-sm); color:var(--color-text-muted);
    width:36px; height:36px; display:flex; align-items:center; justify-content:center;
    cursor:pointer; transition:all 0.15s;
  }
  .btn-back:hover { border-color:var(--color-gold); color:var(--color-gold); }

  /* Stepper */
  .stepper {
    display:flex; gap:0; margin-bottom:2rem; position:relative;
    border-bottom:1px solid var(--color-border); padding-bottom:1rem;
  }
  .step {
    display:flex; align-items:center; gap:0.5rem;
    padding:0.4rem 1.25rem 0.4rem 0;
    font-family:var(--font-mono); font-size:var(--text-sm);
    color:var(--color-text-faint); letter-spacing:0.1em;
  }
  .step.active { color:var(--color-gold); }
  .step.done   { color:var(--color-success); }
  .step-num {
    width:22px; height:22px; border-radius:50%; border:1px solid currentColor;
    display:flex; align-items:center; justify-content:center; font-size:0.7rem; flex-shrink:0;
  }
  .step-line { display:none; }

  /* Secciones */
  .seccion-card {
    background:var(--color-bg-card); border:1px solid var(--color-border);
    border-radius:var(--radius-sm); padding:1.25rem; margin-bottom:1.25rem;
  }
  .seccion-titulo {
    font-family:var(--font-mono); font-size:var(--text-xs); letter-spacing:0.2em;
    color:var(--color-text-muted); text-transform:uppercase; margin-bottom:1rem;
    border-left:2px solid var(--color-gold); padding-left:0.6rem;
  }
  .form-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:1rem; }

  /* Tabla */
  .tabla-wrapper { overflow-x:auto; border:1px solid var(--color-border); border-radius:var(--radius-sm); }
  .tabla { width:100%; border-collapse:collapse; font-size:var(--text-md); }
  .tabla thead tr { background:rgba(179,144,40,0.06); border-bottom:1px solid var(--color-border); }
  .tabla th {
    padding:0.65rem 0.75rem; text-align:left;
    font-family:var(--font-mono); font-size:var(--text-xs);
    letter-spacing:0.12em; color:var(--color-text-muted); text-transform:uppercase; white-space:nowrap;
  }
  .tabla td { padding:0.65rem 0.75rem; color:var(--color-text); vertical-align:middle; }
  .tabla-row { border-bottom:1px solid rgba(58,58,40,0.5); transition:background 0.1s; }
  .tabla-row:hover { background:rgba(179,144,40,0.04); }

  .fila-volado   { background:rgba(207,151,61,0.05) !important; }
  .fila-vencimiento { background:rgba(245,158,11,0.04) !important; }

  .tabla-scroll-x { margin-bottom:1.25rem; }
  .tabla-preview th, .tabla-preview td { padding:0.55rem 0.65rem; }

  .fila-total { background:rgba(179,144,40,0.08) !important; font-weight:700; border-top:2px solid var(--color-border); }
  .total-cel  { color:var(--color-gold) !important; font-weight:700; }

  .td-mono  { font-family:var(--font-mono); }
  .td-muted { color:var(--color-text-muted); }
  .td-fecha { font-family:var(--font-mono); color:var(--color-text-dim); font-size:var(--text-sm); }
  .td-right { text-align:right; }
  .td-center { text-align:center; }

  .check { width:15px; height:15px; cursor:pointer; accent-color:var(--color-gold); }

  .dias-badge {
    font-family:var(--font-mono); font-size:var(--text-xs); padding:0.1rem 0.4rem;
    border-radius:2px; background:rgba(255,255,255,0.05); border:1px solid var(--color-border);
  }
  .dias-badge.dias-warn   { background:var(--color-warning-bg); border-color:rgba(207,151,61,0.4); color:var(--color-warning); }
  .dias-badge.dias-danger { background:var(--color-error-bg);   border-color:rgba(165,71,61,0.4);  color:var(--color-error); }

  .alerta-tag {
    font-family:var(--font-mono); font-size:var(--text-xs); letter-spacing:0.1em;
    padding:0.1rem 0.5rem; border-radius:2px; font-weight:700;
  }
  .alerta-volado { background:var(--color-warning-bg); color:var(--color-warning); border:1px solid rgba(207,151,61,0.4); }
  .alerta-venc   { background:var(--color-error-bg);   color:var(--color-error);   border:1px solid rgba(165,71,61,0.4); }

  .badge-lotes-sel {
    font-family:var(--font-mono); font-size:var(--text-xs); letter-spacing:0.1em;
    background:rgba(179,144,40,0.12); border:1px solid rgba(179,144,40,0.3);
    color:var(--color-gold); padding:0.2rem 0.65rem; border-radius:2px;
  }
  .badge-dirimencia {
    display:inline-flex; align-items:center; justify-content:center;
    width:16px; height:16px; background:var(--color-gold); color:var(--color-bg);
    border-radius:50%; font-size:0.6rem; font-weight:700; margin-left:0.3rem; vertical-align:middle;
  }

  /* Alertas */
  .alertas-bloque {
    display:flex; align-items:flex-start; gap:0; padding:0.85rem 1rem;
    border-radius:var(--radius-sm); margin-bottom:1rem; font-size:var(--text-md);
  }
  .alertas-bloque.criticas { background:var(--color-error-bg); border:1px solid rgba(165,71,61,0.4); color:var(--color-error); }
  .alertas-bloque.info     { background:var(--color-warning-bg); border:1px solid rgba(207,151,61,0.35); color:var(--color-warning); }
  .alerta-titulo { font-weight:700; margin:0 0 0.3rem; font-family:var(--font-mono); font-size:var(--text-sm); letter-spacing:0.1em; }
  .alertas-bloque ul { margin:0; padding-left:1.2rem; }
  .alertas-bloque li { margin:0.15rem 0; font-size:var(--text-sm); }

  /* Resumen header */
  .resumen-header { display:flex; flex-wrap:wrap; gap:2rem; }
  .resumen-col { display:flex; flex-direction:column; gap:0.15rem; }
  .resumen-lbl { font-family:var(--font-mono); font-size:var(--text-xs); letter-spacing:0.15em; color:var(--color-text-muted); text-transform:uppercase; }
  .resumen-val { font-size:var(--text-base); font-weight:600; color:var(--color-text); }
  .resumen-sub { font-family:var(--font-mono); font-size:var(--text-xs); color:var(--color-text-dim); }
  .resumen-total { margin-left:auto; text-align:right; }
  .resumen-val-big { font-family:var(--font-mono); font-size:var(--text-xl); font-weight:700; color:var(--color-gold); }

  /* Confirmacion */
  .confirm-panel {
    display:flex; flex-direction:column; align-items:center;
    background:var(--color-bg-card); border:1px solid var(--color-border);
    border-radius:var(--radius-sm); padding:3rem 2rem; text-align:center; max-width:560px; margin:0 auto;
  }
  .confirm-icon { color:var(--color-gold); margin-bottom:1rem; }
  .confirm-titulo { font-size:var(--text-xl); color:var(--color-text); margin:0 0 0.75rem; }
  .confirm-detalle { font-size:var(--text-md); color:var(--color-text-muted); margin:0 0 1rem; line-height:1.7; }
  .confirm-aviso {
    font-size:var(--text-sm); font-family:var(--font-mono);
    background:var(--color-warning-bg); border:1px solid rgba(207,151,61,0.3);
    color:var(--color-warning); padding:0.65rem 1rem; border-radius:var(--radius-sm); line-height:1.6;
  }
  .total-gold { color:var(--color-gold); }

  /* Cargando / sin lotes */
  .cargando-inline { display:flex; align-items:center; gap:0.5rem; padding:1.5rem; font-family:var(--font-mono); font-size:var(--text-sm); color:var(--color-text-muted); }
  .sin-lotes { padding:2rem 1rem; text-align:center; font-family:var(--font-mono); font-size:var(--text-sm); color:var(--color-text-faint); }

  .error-inline {
    display:flex; align-items:center; font-size:var(--text-sm);
    color:var(--color-error); font-family:var(--font-mono);
  }

  .acciones-pie {
    display:flex; justify-content:flex-end; align-items:center;
    gap:1rem; margin-top:1.25rem;
  }

  .spinner { animation:spin 0.8s linear infinite; display:inline-block; }
  @keyframes spin { to { transform:rotate(360deg); } }

  .col-r { text-align: right; }
  .alerta-dirim { background: rgba(179,144,40,0.12); color: var(--color-gold); border: 1px solid rgba(179,144,40,0.3); }

  /* Columnas Ag (Plata) */
  .col-ag { color: var(--color-text-muted); }
  .total-ag-cel { color: #94a3b8 !important; font-weight: 700; }
  .resumen-total-ag { margin-left: 1.5rem; }
  .resumen-val-ag {
    font-family: var(--font-mono); font-size: var(--text-lg); font-weight: 700;
    color: #94a3b8;
  }
  </style>
