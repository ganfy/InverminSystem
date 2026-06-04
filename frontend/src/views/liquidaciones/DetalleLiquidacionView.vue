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
              <FileText :size="24" style="margin-right:0.5rem" />
              {{ store.detalle?.numero_liquidacion ?? 'Liquidación' }}
            </h1>
            <p class="page-subtitle">
              Generada {{ fmtDate(store.detalle?.fecha_creacion) }}
            </p>
          </div>
        </div>
        <div style="display:flex;gap:0.75rem;align-items:center" v-if="store.detalle">
          <!-- Estado badge -->
          <span class="badge-estado-lg" :class="badgeClass(store.detalle.estado)">
            {{ store.detalle.estado }}
          </span>
          <!-- Cambiar estado -->
          <button
            v-if="puedeCambiarEstado && store.detalle.estado !== 'PAGADA'"
            class="btn-secondary"
            @click="abrirCambioEstado"
            :disabled="store.cargando"
          >
            Cambiar estado
          </button>
          <!-- PDF -->
          <span
            v-if="store.detalle?.pdf_url"
            class="badge-pdf-emitido"
            title="PDF generado y guardado en el sistema"
          >
            <FileCheck :size="14" style="margin-right:0.25rem" /> PDF emitido
          </span>
          <button
            class="btn-primary ready btn-con-icono"
            :disabled="descargandoPdf"
            @click="descargarPdf"
          >
            <Download :size="18" :class="{ spinner: descargandoPdf }" />
            <span>{{ store.detalle?.pdf_url ? 'Ver PDF' : 'Generar PDF' }}</span>
          </button>
        </div>
      </header>

      <!-- ── Loading / Error ───────────────────────────────────── -->
      <div v-if="store.cargando && !store.detalle" class="cargando-full">
        <span class="spinner-lg" /> Cargando liquidación…
      </div>
      <div v-else-if="store.error && !store.detalle" class="estado-error">
        <AlertTriangle :size="16" style="margin-right:0.4rem" />
        {{ store.error }}
      </div>

      <!-- ── Contenido ─────────────────────────────────────────── -->
      <template v-if="store.detalle">

        <!-- Bloque de datos del cliente -->
        <div class="seccion-card">
          <p class="seccion-titulo">DATOS DEL CLIENTE</p>
          <div class="datos-grid">
            <div class="dato-col">
              <span class="dato-lbl">PROVEEDOR</span>
              <span class="dato-val">{{ store.detalle.proveedor_razon_social }}</span>
              <span class="dato-sub">RUC: {{ store.detalle.proveedor_ruc ?? '-' }}</span>
            </div>
            <div class="dato-col">
              <span class="dato-lbl">ACOPIADOR</span>
              <span class="dato-val">{{ store.detalle.acopiador_nombre }}</span>
            </div>
            <div class="dato-col">
              <span class="dato-lbl">PRECIO ORO SPOT</span>
              <span class="dato-val mono">${{ fmtNum(store.detalle.spot_usd, 2) }} /Oz</span>
            </div>
            <div class="dato-col">
              <span class="dato-lbl">LOTES</span>
              <span class="dato-val">{{ store.detalle.count_lotes }}</span>
            </div>
            <div class="dato-col">
              <span class="dato-lbl">TMS TOTAL</span>
              <span class="dato-val mono">{{ fmtNum(totalTms, 3) }} TMS</span>
            </div>
            <div class="dato-col dato-total">
              <span class="dato-lbl">TOTAL USD (Au)</span>
              <span class="dato-val-big">${{ fmtNum(store.detalle.total_usd, 2) }}</span>
            </div>
            <div v-if="hayAg" class="dato-col dato-total-ag">
              <span class="dato-lbl">TOTAL AG (Plata)</span>
              <span class="dato-val-ag">${{ fmtNum(totalAgUsd, 2) }}</span>
            </div>
          </div>
        </div>

        <!-- Tabla de lotes -->
        <div class="seccion-card" style="padding:0;overflow:hidden">
          <div style="padding:1rem 1.25rem;border-bottom:1px solid var(--color-border)">
            <p class="seccion-titulo" style="margin:0">DETALLE DE LOTES</p>
          </div>
          <div class="tabla-wrapper" style="border:none;border-radius:0">
            <table class="tabla">
              <thead>
                <tr>
                  <th>LOTE</th>
                  <th>RECEPCIÓN</th>
                  <th>TMH</th>
                  <th>%H₂O</th>
                  <th>TMS</th>
                  <th>SACOS</th>
                  <th>LEY PLANTA</th>
                  <th>LEY COMERC.</th>
                  <th>LEY MINERO</th>
                  <th>PROMEDIO</th>
                  <th>%REC LIQ</th>
                  <th>TC US$ x tc</th>
                  <th>RIESGO</th>
                  <th>INSUMOS</th>
                  <th>BONO</th>
                  <th>FACTOR</th>
                  <th>PRECIO/TMS</th>
                  <th>FINO OZ</th>
                  <!-- Columnas Ag (opcionales) -->
                  <th v-if="hayAg" class="col-ag">Ag Gr/TM</th>
                  <th v-if="hayAg" class="col-ag">Ag Oz/TC</th>
                  <th v-if="hayAg" class="col-ag">VALOR Ag</th>
                  <th>TOTAL USD</th>
                  <th v-if="puedeEditarParams">ACCIONES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lote in store.detalle.lotes" :key="lote.ip" class="tabla-row">
                  <td>
                    <span class="td-mono" style="color:var(--color-gold)">{{ lote.ip }}</span>
                    <span v-if="lote.usa_dirimencia" class="badge-dirimencia" title="Usó dirimencia">D</span>
                  </td>
                  <td class="td-fecha">{{ fmtDate(lote.fecha_recepcion) }}</td>
                  <td class="td-mono td-right">{{ fmtNum(lote.tmh, 3) }}</td>
                  <td class="td-mono td-right">{{ fmtNum(lote.pct_humedad, 2) }}%</td>
                  <td class="td-mono td-right">{{ fmtNum(lote.tms, 3) }}</td>
                  <td class="td-center td-muted">{{ lote.sacos ?? '-' }}</td>
                  <td class="td-mono td-right td-muted">{{ fmtNum(lote.oz_tc_planta, 4) }}</td>
                  <td class="td-mono td-right td-muted">{{ fmtNum(lote.oz_tc_comercial, 4) }}</td>
                  <td class="td-mono td-right td-muted">{{ fmtNum(lote.oz_tc_minero, 4) }}</td>
                  <td class="td-mono td-right" style="color:var(--color-gold)">{{ fmtNum(lote.oz_tc_promedio, 4) }}</td>
                  <td class="td-mono td-right">{{ fmtNum(lote.pct_rec_liq, 1) }}%</td>
                  <td class="td-mono td-right">${{ fmtNum(lote.maquila, 2) }}</td>
                  <td class="td-mono td-right td-muted">${{ fmtNum(lote.riesgo, 2) }}</td>
                  <td class="td-mono td-right td-muted">${{ fmtNum(lote.insumos_total, 2) }}</td>
                  <td class="td-mono td-right td-muted">{{ lote.bono ? '$' + fmtNum(lote.bono, 2) : '-' }}</td>
                  <td class="td-mono td-right td-muted">{{ fmtNum(lote.factor, 4) }}</td>
                  <td class="td-mono td-right">${{ fmtNum(lote.precio_x_tms, 4) }}</td>
                  <td class="td-mono td-right td-muted">{{ fmtNum(lote.fino_recuperable, 4) }}</td>
                  <!-- Ag (opcionales) -->
                  <td v-if="hayAg" class="td-mono td-right col-ag">{{ fmtNum(lote.ley_ag_gr_tm, 2) }}</td>
                  <td v-if="hayAg" class="td-mono td-right col-ag">{{ fmtNum(lote.ley_ag_oz_tc, 4) }}</td>
                  <td v-if="hayAg" class="td-mono td-right col-ag total-ag-cel">${{ fmtNum(lote.valor_ag_usd, 2) }}</td>
                  <td class="td-mono td-right total-cel">${{ fmtNum(lote.total_usd, 2) }}</td>
                  <td v-if="puedeEditarParams">
                    <button
                      class="btn-icon"
                      title="Editar parámetros"
                      @click="abrirEditParams(lote)"
                      :disabled="store.detalle?.estado === 'PAGADA'"
                    >
                      <Pencil :size="14" />
                    </button>
                  </td>
                                  </tr>
                <!-- Fila total -->
                <tr class="fila-total">
                  <td colspan="4" style="text-align:right;padding-right:1rem">TOTALES</td>
                  <td class="td-mono td-right">{{ fmtNum(totalTms, 3) }}</td>
                  <td :colspan="hayAg ? 12 : 12" />
                  <!-- celdas vacías para columnas Ag -->
                  <td v-if="hayAg" colspan="2" />
                  <td v-if="hayAg" class="td-mono td-right total-ag-cel">${{ fmtNum(totalAgUsd, 2) }}</td>
                  <td class="td-mono td-right total-cel">${{ fmtNum(store.detalle.total_usd, 2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Panel editable de parámetros — Admin/Gerencia -->
        <div v-if="puedeEditarParams" class="params-panel seccion-card">
          <p class="seccion-titulo">PARÁMETROS DE CÁLCULO</p>

          <div class="params-globales">
            <template v-for="lote in store.detalle.lotes" :key="lote.ip">
              <div class="pfield" v-if="detailOv[lote.ip]">
                <span class="plbl">{{ lote.ip }} — BONO</span>
                <input type="number" class="pinput"
                  v-model.number="detailOv[lote.ip]!.bono"
                  step="0.01" @input="pendienteGuardar = true" />
              </div>
              <div class="pfield" v-if="detailOv[lote.ip]">
                <span class="plbl">{{ lote.ip }} — % REC LIQ</span>
                <input type="number" class="pinput"
                  v-model.number="detailOv[lote.ip]!.rec_liq"
                  step="0.1" min="0" max="100" @input="pendienteGuardar = true" />
              </div>
              <div class="pfield" v-if="detailOv[lote.ip]">
                <span class="plbl">{{ lote.ip }} — GASTO ACOPIO</span>
                <input type="number" class="pinput"
                  v-model.number="detailOv[lote.ip]!.gasto_acopio_override"
                  step="0.01" @input="pendienteGuardar = true" />
              </div>
              <div class="pfield" v-if="detailOv[lote.ip]">
                <span class="plbl">{{ lote.ip }} — INSUMOS LIQ</span>
                <input type="number" class="pinput"
                  v-model.number="detailOv[lote.ip]!.gasto_consumo_override"
                  step="0.01" @input="pendienteGuardar = true" />
              </div>
            </template>
          </div>

          <div style="display:flex;align-items:center;gap:1rem;margin-top:0.75rem">
            <button class="btn-primary" style="font-size:0.8rem"
              :disabled="guardandoParams || !pendienteGuardar"
              @click="guardarParamsDetalle">
              <span v-if="guardandoParams" class="spinner" style="margin-right:0.4rem"/>
              {{ guardandoParams ? 'Guardando…' : 'Guardar y Recalcular' }}
            </button>
            <span v-if="pendienteGuardar" class="warn-recalc">
              <AlertTriangle :size="13" style="vertical-align:middle;margin-right:4px" />
              Cambios sin guardar
            </span>
          </div>
        </div>

        <!-- Notas reglamentarias -->
        <div class="seccion-card notas-card">
          <p class="seccion-titulo">CONDICIONES COMERCIALES</p>
          <ul class="notas-lista">
            <li>Se promedia diferencia de leyes según parámetros del acopiador.</li>
            <li>Si existe una falsificación o adulteración de los datos serán denunciados penalmente.</li>
            <li>Si el proveedor minero desea retirar el mineral de nuestra planta deberá realizar un pago por almacenaje, chancado y gastos operativos.</li>
            <li>Se acepta reclamos y/u observaciones antes de que se efectúe la factura y por ende el pago correspondiente, después queda sin efecto todo reclamo.</li>
            <li>Si el mineral ingresado es considerado <strong>Sin Valor Comercial</strong> (Ley Oz/tc menor a 0.100) y llega a cumplir los 30 días en nuestro almacén, se dispondrá del mismo sin lugar a reclamo.</li>
            <li>Si el mineral ingresado es considerado <strong>Con Valor Comercial</strong> (Ley Oz/tc mayor a 0.100) y llega a cumplir los 30 días y no hay respuesta de confirmación del proveedor minero, se liquidará con las condiciones comerciales de la empresa.</li>
          </ul>
        </div>

      </template>

      <!-- ── Modal cambio de estado ────────────────────────────── -->
      <Teleport to="body">
        <div v-if="modalEstado" class="modal-overlay" @click.self="modalEstado = false">
          <div class="modal-panel">
            <h3 class="modal-titulo">Cambiar estado de liquidación</h3>
            <p class="modal-sub">N° {{ store.detalle?.numero_liquidacion }}</p>

            <div class="field" style="margin:1.25rem 0">
              <label class="field-label">NUEVO ESTADO</label>
              <select class="field-input field-select" v-model="nuevoEstado">
                <option v-for="e in estadosSiguientes" :key="e.value" :value="e.value">
                  {{ e.label }}
                </option>
              </select>
            </div>

            <div style="display:flex;gap:0.75rem;justify-content:flex-end">
              <button class="btn-secondary" @click="modalEstado = false" :disabled="store.cargando">
                Cancelar
              </button>
              <button
                class="btn-primary ready"
                :disabled="!nuevoEstado || store.cargando"
                @click="guardarEstado"
              >
                <span v-if="store.cargando" class="spinner" style="margin-right:0.4rem" />
                Guardar
              </button>
            </div>
          </div>
        </div>
      </Teleport>

      <div v-if="editModal" class="modal-overlay" @click.self="editModal = null">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2 style="font-size:1rem">Editar Parámetros — {{ editModal.ip }}</h2>
            <button class="btn-cerrar" @click="editModal = null">×</button>
          </div>
          <div class="modal-body">
            <div class="form-grid" style="grid-template-columns:1fr 1fr">
              <div class="field">
                <label class="field-label">BONO (USD)</label>
                <input type="number" class="field-input" v-model.number="editForm.bono" step="0.01" />
              </div>
              <div class="field">
                <label class="field-label">% REC LIQ</label>
                <input type="number" class="field-input" v-model.number="editForm.rec_liq_override" step="0.1" min="0" max="100" />
              </div>
              <div class="field">
                <label class="field-label">RIESGO (USD)</label>
                <input type="number" class="field-input" v-model.number="editForm.riesgo_override" step="0.01" />
              </div>
              <div class="field">
                <label class="field-label">MAQUILA (USD/TC)</label>
                <input type="number" class="field-input" v-model.number="editForm.maquila_override" step="0.01" />
              </div>
              <div class="field">
                <label class="field-label">GASTO ACOPIO (USD)</label>
                <input type="number" class="field-input" v-model.number="editForm.gasto_acopio_override" step="0.01" />
              </div>
              <div class="field">
                <label class="field-label">GASTO CONSUMO (USD)</label>
                <input type="number" class="field-input" v-model.number="editForm.gasto_consumo_override" step="0.01" />
              </div>
            </div>
            <p class="field-hint" style="margin-top:0.5rem">
              Solo los campos modificados se actualizarán. El PDF se regenera automáticamente.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="editModal = null">Cancelar</button>
            <button class="btn-primary" @click="guardarEditParams" :disabled="guardandoParams">
              <span v-if="guardandoParams" class="spinner" style="margin-right:0.3rem"></span>
              Guardar y Recalcular
            </button>
          </div>
        </div>
      </div>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ChevronLeft, FileText, Download, AlertTriangle, FileCheck, Pencil } from 'lucide-vue-next'
  import { useLiquidacionesStore } from '@/stores/liquidaciones'
  import { useAuthStore } from '@/stores/auth'
  import { useUiStore } from '@/stores/ui'
  import { descargarPDF, editarParamsLote, type LiquidacionLoteParamsUpdate, type LiquidacionLoteOut } from '@/api/liquidaciones'

  const route  = useRoute()
  const router = useRouter()
  const store  = useLiquidacionesStore()
  const auth   = useAuthStore()
  const ui     = useUiStore()

  const descargandoPdf = ref(false)
  const modalEstado    = ref(false)
  const nuevoEstado    = ref('')

  const id = Number(route.params.id)

  const rol               = computed(() => auth.user?.rol ?? '')
  const puedeCambiarEstado = computed(() => ['Admin', 'Gerencia', 'Comercial'].includes(rol.value))

  const puedeEditarParams = computed(() =>
    ['Admin', 'Gerencia'].includes(auth.user?.rol ?? '')
  )

  const totalTms = computed(() =>
    (store.detalle?.lotes ?? []).reduce((acc, l) => acc + Number(l.tms), 0)
  )

  const hayAg = computed(() =>
    store.detalle?.hay_ag ??
    (store.detalle?.lotes?.some(l => l.aplica_ag) ?? false)
  )

  const totalAgUsd = computed(() =>
    (store.detalle?.total_ag_usd) ??
    (store.detalle?.lotes ?? []).reduce((acc, l) => acc + (l.aplica_ag ? Number(l.valor_ag_usd ?? 0) : 0), 0)
  )

  const estadosSiguientes = computed(() => {
    const estado = store.detalle?.estado
    if (estado === 'GENERADA')  return [{ value: 'FACTURADA', label: 'FACTURADA' }]
    if (estado === 'FACTURADA') return [{ value: 'PAGADA', label: 'PAGADA' }]
    return []
  })

  function abrirCambioEstado() {
    nuevoEstado.value = estadosSiguientes.value[0]?.value ?? ''
    modalEstado.value = true
  }

  async function guardarEstado() {
    if (!nuevoEstado.value) return
    const ok = await store.cambiarEstado(id, nuevoEstado.value)
    if (ok) {
      ui.toast(`Estado actualizado a ${nuevoEstado.value}`, 'success')
      modalEstado.value = false
    } else {
      ui.toast(store.error ?? 'Error al cambiar estado', 'error')
    }
  }

  //Edición de parámetros del lote
  interface EditModal { ip: string; lote: LiquidacionLoteOut }
  const editModal = ref<EditModal | null>(null)
  const guardandoParams = ref(false)
  const pendienteGuardar = ref(false)
  const detailOv = ref<Record<string, LiquidacionLoteParamsUpdate & { rec_liq: number | null }>>({})
  const editForm = ref<LiquidacionLoteParamsUpdate>({})

  function abrirEditParams(lote: any) {
    editModal.value = { ip: lote.ip, lote }
    editForm.value = {
      bono: lote.bono ?? 0,
      rec_liq_override: lote.pct_rec_liq ?? null,
      riesgo_override: lote.riesgo ?? null,
      maquila_override: lote.maquila ?? null,
      gasto_acopio_override: lote.insumos_acopio ?? null,
      gasto_consumo_override: lote.insumos_consumo ?? null,
    }
  }

  watch(() => store.detalle, (d) => {
  if (!d) return
  for (const l of d.lotes) {
    detailOv.value[l.ip] = {
      bono:                 Number(l.bono)         || 0,
      rec_liq_override:     Number(l.pct_rec_liq)  || null,
      gasto_acopio_override: Number(l.insumos_acopio)  || null,
      gasto_consumo_override: Number(l.insumos_consumo) || null,
      rec_liq: Number(l.pct_rec_liq) || null,
    }
  }
}, { immediate: true })

async function guardarParamsDetalle() {
  if (!store.detalle) return
  guardandoParams.value = true
  try {
    for (const l of store.detalle.lotes) {
      const ov = detailOv.value[l.ip]
      if (!ov) continue
      await editarParamsLote(store.detalle.id, l.ip, {
        bono: ov.bono,
        rec_liq_override: ov.rec_liq,
        gasto_acopio_override: ov.gasto_acopio_override,
        gasto_consumo_override: ov.gasto_consumo_override,
      })
    }
    await store.cargarDetalle(id)
    pendienteGuardar.value = false
    ui.toast('Parámetros actualizados. PDF regenerado.', 'success')
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al guardar', 'error')
  } finally {
    guardandoParams.value = false
  }
}

async function guardarEditParams() {
  if (!editModal.value || !store.detalle) return
  guardandoParams.value = true
  try {
    const r = await editarParamsLote(store.detalle.id, editModal.value.ip, editForm.value)
    store.detalle = r.data
    editModal.value = null
    ui.toast('Parámetros actualizados y PDF regenerado', 'success')
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al guardar', 'error')
  } finally {
    guardandoParams.value = false
  }
}

  // PDF
  async function descargarPdf() {
    descargandoPdf.value = true
    try {
      await descargarPDF(id.toString())
    } catch {
      ui.toast('Error al descargar PDF', 'error')
    } finally {
      descargandoPdf.value = false
    }
  }

  function badgeClass(estado: string) {
    return { GENERADA: 'parcial', FACTURADA: 'pendiente', PAGADA: 'completo' }[estado] ?? 'pendiente'
  }
  function fmtNum(v: number | null | undefined, d = 2) {
    if (v == null) return '-'
    return Number(v).toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
  }
  function fmtDate(s: string | null | undefined) {
    if (!s) return '-'
    return new Date(s).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  onMounted(() => store.cargarDetalle(id))
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

.btn-con-icono { display:flex; align-items:center; gap:0.5rem; }

.badge-estado-lg {
  display:inline-block; padding:0.3rem 0.85rem; border-radius:3px;
  font-family:var(--font-mono); font-size:var(--text-sm); letter-spacing:0.15em; font-weight:700;
}
.badge-estado-lg.completo  { background:var(--color-success-bg); color:#4ade80; border:1px solid rgba(81,161,85,0.3); }
.badge-estado-lg.parcial   { background:var(--color-gold-bg); color:var(--color-gold); border:1px solid rgba(179,144,40,0.3); }
.badge-estado-lg.pendiente { background:var(--color-warning-bg); color:var(--color-warning); border:1px solid rgba(207,151,61,0.3); }

/* Cards */
.seccion-card {
  background:var(--color-bg-card); border:1px solid var(--color-border);
  border-radius:var(--radius-sm); padding:1.25rem; margin-bottom:1.25rem;
}
.seccion-titulo {
  font-family:var(--font-mono); font-size:var(--text-xs); letter-spacing:0.2em;
  color:var(--color-text-muted); text-transform:uppercase; margin-bottom:1rem;
  border-left:2px solid var(--color-gold); padding-left:0.6rem;
}

/* Datos grid */
.datos-grid { display:flex; flex-wrap:wrap; gap:2rem; }
.dato-col { display:flex; flex-direction:column; gap:0.2rem; }
.dato-lbl { font-family:var(--font-mono); font-size:var(--text-xs); letter-spacing:0.15em; color:var(--color-text-muted); text-transform:uppercase; }
.dato-val { font-size:var(--text-base); font-weight:600; color:var(--color-text); }
.dato-val.mono { font-family:var(--font-mono); }
.dato-sub { font-family:var(--font-mono); font-size:var(--text-xs); color:var(--color-text-dim); }
.dato-total { margin-left:auto; }
.dato-val-big { font-family:var(--font-mono); font-size:var(--text-xl); font-weight:700; color:var(--color-gold); }

/* Tabla */
.tabla-wrapper { overflow-x:auto; border:1px solid var(--color-border); border-radius:var(--radius-sm); }
.tabla { width:100%; border-collapse:collapse; font-size:var(--text-sm); }
.tabla thead tr { background:rgba(179,144,40,0.06); border-bottom:1px solid var(--color-border); }
.tabla th {
  padding:0.6rem 0.7rem; text-align:left;
  font-family:var(--font-mono); font-size:var(--text-xs);
  letter-spacing:0.1em; color:var(--color-text-muted); text-transform:uppercase; white-space:nowrap;
}
.tabla td { padding:0.65rem 0.7rem; color:var(--color-text); vertical-align:middle; white-space:nowrap; }
.tabla-row { border-bottom:1px solid rgba(58,58,40,0.5); transition:background 0.1s; }

.td-mono  { font-family:var(--font-mono); }
.td-muted { color:var(--color-text-dim); }
.td-fecha { font-family:var(--font-mono); color:var(--color-text-dim); }
.td-right { text-align:right; }
.td-center { text-align:center; }
.total-cel { color:var(--color-gold) !important; font-weight:700; }

.fila-total { background:rgba(179,144,40,0.08) !important; font-weight:700; border-top:2px solid var(--color-border); }

.badge-dirimencia {
  display:inline-flex; align-items:center; justify-content:center;
  width:15px; height:15px; background:var(--color-gold); color:var(--color-bg);
  border-radius:50%; font-size:0.6rem; font-weight:700; margin-left:0.3rem; vertical-align:middle;
}

/* Notas */
.notas-card { background:rgba(179,144,40,0.03); }
.notas-lista { margin:0; padding-left:1.4rem; list-style:disc; }
.notas-lista li { padding:0.2rem 0; font-size:var(--text-sm); color:var(--color-text-muted); line-height:1.6; }
.notas-lista strong { color:var(--color-text); }

/* Cargando / error */
.cargando-full {
  display:flex; align-items:center; gap:0.75rem;
  padding:3rem; font-family:var(--font-mono); font-size:var(--text-md); color:var(--color-text-muted);
}
.spinner-lg {
  display:inline-block; width:20px; height:20px;
  border:2px solid var(--color-border); border-top-color:var(--color-gold);
  border-radius:50%; animation:spin 0.7s linear infinite; flex-shrink:0;
}
.estado-error {
  display:flex; align-items:center;
  padding:0.75rem 1rem; margin-bottom:1rem;
  background:var(--color-error-bg); border:1px solid var(--color-error);
  border-radius:var(--radius-sm); color:var(--color-error); font-size:var(--text-md);
}

.badge-pdf-emitido {
display: inline-flex;
align-items: center;
font-size: 0.7rem;
font-family: var(--font-mono);
letter-spacing: 0.08em;
padding: 0.25rem 0.6rem;
border-radius: var(--radius-sm);
background: rgba(60, 180, 80, 0.1);
color: var(--color-success);
border: 1px solid rgba(60, 180, 80, 0.3);
}

/* Modal */
.modal-overlay {
  position:fixed; inset:0; background:rgba(0,0,0,0.65); z-index:200;
  display:flex; align-items:center; justify-content:center;
}
.modal-panel {
  background:var(--color-bg-card); border:1px solid var(--color-border);
  border-radius:var(--radius-md); padding:1.75rem 2rem; min-width:380px; max-width:95vw;
}
.modal-titulo { font-size:var(--text-lg); color:var(--color-text); margin:0 0 0.25rem; }
.modal-sub { font-family:var(--font-mono); font-size:var(--text-sm); color:var(--color-text-muted); margin:0; }

.spinner { animation:spin 0.8s linear infinite; display:inline-block; }
@keyframes spin { to { transform:rotate(360deg); } }

/* Columnas Ag (Plata) */
.col-ag { color: var(--color-text-dim); }
.total-ag-cel { color: #94a3b8 !important; font-weight: 700; }
.dato-total-ag { margin-left: 1rem; }
.dato-val-ag {
  font-family: var(--font-mono);
  font-size: var(--text-xl);
  font-weight: 700;
  color: #94a3b8;
}
</style>
