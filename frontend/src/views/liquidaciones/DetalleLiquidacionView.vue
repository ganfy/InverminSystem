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
          <button
            class="btn-primary ready btn-con-icono"
            :disabled="descargandoPdf"
            @click="descargarPdf"
          >
            <Download :size="18" :class="{ spinner: descargandoPdf }" />
            <span>Descargar PDF</span>
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
              <span class="dato-lbl">TOTAL USD</span>
              <span class="dato-val-big">${{ fmtNum(store.detalle.total_usd, 2) }}</span>
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
                  <th>TOTAL USD</th>
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
                  <td class="td-mono td-right total-cel">${{ fmtNum(lote.total_usd, 2) }}</td>
                </tr>
                <!-- Fila total -->
                <tr class="fila-total">
                  <td colspan="4" style="text-align:right;padding-right:1rem">TOTALES</td>
                  <td class="td-mono td-right">{{ fmtNum(totalTms, 3) }}</td>
                  <td colspan="12" />
                  <td class="td-mono td-right total-cel">${{ fmtNum(store.detalle.total_usd, 2) }}</td>
                </tr>
              </tbody>
            </table>
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

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ChevronLeft, FileText, Download, AlertTriangle } from 'lucide-vue-next'
  import { useLiquidacionesStore } from '@/stores/liquidaciones'
  import { useAuthStore } from '@/stores/auth'
  import { useUiStore } from '@/stores/ui'
  import { descargarPDF } from '@/api/liquidaciones'

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

  const totalTms = computed(() =>
    (store.detalle?.lotes ?? []).reduce((acc, l) => acc + Number(l.tms), 0)
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
  </style>
