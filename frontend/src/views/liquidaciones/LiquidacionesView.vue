<template>
    <div class="page-container">

      <!-- ── Header ─────────────────────────────────────────────── -->
      <header class="page-header">
        <div>
          <h1 class="page-title">
            <FileText class="lucide" :size="24" style="margin-right:0.5rem" />
            Liquidaciones
          </h1>
          <p class="page-subtitle">Historial y gestión de liquidaciones de mineral</p>
        </div>
        <div style="display:flex;gap:0.75rem;align-items:center">
          <button class="btn-secondary" @click="cargar" :disabled="store.cargando">
            <RefreshCw :size="16" :class="{ spinner: store.cargando }" style="margin-right:0.4rem" />
            ACTUALIZAR
          </button>
          <button v-if="puedeCrear" class="btn-primary ready btn-con-icono" @click="irACrear">
            <PlusCircle :size="18" />
            <span>NUEVA LIQUIDACIÓN</span>
          </button>
        </div>
      </header>

      <!-- ── Filtros ─────────────────────────────────────────────── -->
      <div class="filtros-bar">
        <div class="field" style="width:180px">
          <label class="field-label">ESTADO</label>
          <select class="field-input field-select" v-model="filtroEstado" @change="cargar">
            <option value="">Todos</option>
            <option value="GENERADA">Generada</option>
            <option value="FACTURADA">Facturada</option>
            <option value="PAGADA">Pagada</option>
          </select>
        </div>
        <div class="field" style="flex:1;min-width:220px">
          <label class="field-label">BÚSQUEDA</label>
          <input
            type="text"
            class="field-input"
            v-model="busqueda"
            placeholder="N° liquidación, proveedor, RUC…"
          />
        </div>
      </div>

      <!-- ── Error ──────────────────────────────────────────────── -->
      <div v-if="store.error" class="estado-error">
        <AlertTriangle :size="16" style="margin-right:0.4rem" />
        {{ store.error }}
      </div>

      <!-- ── Tabla ──────────────────────────────────────────────── -->
      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>N° LIQUIDACIÓN</th>
              <th>PROVEEDOR</th>
              <th>ACOPIADOR</th>
              <th>LOTES</th>
              <th>SPOT USD</th>
              <th>TOTAL USD</th>
              <th>ESTADO</th>
              <th>FECHA</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.cargando">
              <td colspan="9" class="estado-tabla">
                <span class="spinner" style="margin-right:0.5rem" /> Cargando…
              </td>
            </tr>
            <template v-else>
              <tr v-if="listaFiltrada.length === 0">
                <td colspan="9" class="estado-tabla sin-datos">
                  <FolderSearch :size="28" style="margin-bottom:0.5rem;opacity:0.4;display:block;margin-inline:auto" />
                  Sin liquidaciones registradas
                </td>
              </tr>
              <tr
                v-for="liq in listaFiltrada"
                :key="liq.id"
                class="tabla-row clickable"
                @click="irADetalle(liq.id)"
              >
                <td class="td-mono" style="color:var(--color-gold)">{{ liq.numero_liquidacion }}</td>
                <td>
                  <span class="nombre-text">{{ liq.proveedor_razon_social }}</span>
                  <span v-if="liq.proveedor_ruc" class="ruc-sub">{{ liq.proveedor_ruc }}</span>
                </td>
                <td class="td-muted">{{ liq.acopiador_nombre }}</td>
                <td class="td-center">
                  <span class="badge-count">{{ liq.count_lotes }}</span>
                </td>
                <td class="td-mono td-right">${{ fmtNum(liq.spot_usd, 2) }}</td>
                <td class="td-mono td-right" style="color:var(--color-gold);font-weight:700">
                  ${{ fmtNum(liq.total_usd, 2) }}
                </td>
                <td>
                  <span class="badge-estado" :class="badgeClass(liq.estado)">{{ liq.estado }}</span>
                </td>
                <td class="td-fecha">{{ fmtDate(liq.fecha_creacion) }}</td>
                <td class="td-acciones" @click.stop>
                  <div class="acciones-grupo">
                    <button class="btn-accion" title="Ver detalle" @click="irADetalle(liq.id)">
                      <Eye :size="15" />
                    </button>
                    <button
                      class="btn-accion"
                      title="Descargar PDF"
                      :disabled="descargando === liq.id"
                      @click="descargarPdf(liq.id, liq.numero_liquidacion)"
                    >
                      <Download :size="15" :class="{ spinner: descargando === liq.id }" />
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <div v-if="!store.cargando" class="tabla-footer">
        <span class="tabla-count">{{ listaFiltrada.length }} de {{ store.lista.length }} registros</span>
      </div>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { FileText, RefreshCw, PlusCircle, Eye, Download, AlertTriangle, FolderSearch } from 'lucide-vue-next'
  import { useLiquidacionesStore } from '@/stores/liquidaciones'
  import { useAuthStore } from '@/stores/auth'
  import { useUiStore } from '@/stores/ui'
  import { getPdfLiquidacion } from '@/api/liquidaciones'

  const router = useRouter()
  const store  = useLiquidacionesStore()
  const auth   = useAuthStore()
  const ui     = useUiStore()

  const filtroEstado = ref('')
  const busqueda     = ref('')
  const descargando  = ref<number | null>(null)

  const puedeCrear = computed(() =>
    ['Admin', 'Gerencia', 'Comercial'].includes(auth.user?.rol ?? '')
  )

  const listaFiltrada = computed(() => {
    const q = busqueda.value.trim().toLowerCase()
    return store.lista.filter(l => {
      if (filtroEstado.value && l.estado !== filtroEstado.value) return false
      if (!q) return true
      return (
        l.numero_liquidacion.toLowerCase().includes(q) ||
        l.proveedor_razon_social.toLowerCase().includes(q) ||
        (l.proveedor_ruc?.includes(q) ?? false) ||
        l.acopiador_nombre.toLowerCase().includes(q)
      )
    })
  })

  async function cargar() {
    await store.cargarLista(filtroEstado.value ? { estado: filtroEstado.value } : undefined)
  }

  function irACrear()          { router.push('/liquidaciones/nueva') }
  function irADetalle(id: number) { router.push(`/liquidaciones/${id}`) }

  async function descargarPdf(id: number, numero: string) {
    descargando.value = id
    try {
      const link = document.createElement('a')
      link.href = getPdfLiquidacion(id)
      link.download = `Liquidacion_${numero}.pdf`
      link.click()
    } catch {
      ui.toast('Error al descargar PDF', 'error')
    } finally {
      descargando.value = null
    }
  }

  function fmtNum(v: number, d = 2) {
    return Number(v).toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
  }
  function fmtDate(s: string) {
    if (!s) return '-'
    return new Date(s).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }
  function badgeClass(estado: string) {
    return { GENERADA: 'parcial', FACTURADA: 'pendiente', PAGADA: 'completo' }[estado] ?? 'pendiente'
  }

  onMounted(cargar)
  </script>

  <style scoped>
  @import '@/assets/base.css';

  .page-subtitle {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    margin-top: 0.25rem;
    font-family: var(--font-mono);
    letter-spacing: 0.06em;
  }

  .filtros-bar { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.25rem; align-items: flex-end; }

  .btn-con-icono { display: flex; align-items: center; gap: 0.5rem; }

  .estado-error {
    display: flex; align-items: center;
    padding: 0.75rem 1rem; margin-bottom: 1rem;
    background: var(--color-error-bg); border: 1px solid var(--color-error);
    border-radius: var(--radius-sm); color: var(--color-error); font-size: var(--text-md);
  }

  .tabla-wrapper { overflow-x: auto; border: 1px solid var(--color-border); border-radius: var(--radius-sm); }
  .tabla { width: 100%; border-collapse: collapse; font-size: var(--text-md); }
  .tabla thead tr { background: rgba(179,144,40,0.06); border-bottom: 1px solid var(--color-border); }
  .tabla th {
    padding: 0.7rem 1rem; text-align: left;
    font-family: var(--font-mono); font-size: var(--text-xs);
    letter-spacing: 0.15em; color: var(--color-text-muted); text-transform: uppercase; white-space: nowrap;
  }
  .tabla td { padding: 0.75rem 1rem; color: var(--color-text); vertical-align: middle; }
  .tabla-row { border-bottom: 1px solid rgba(58,58,40,0.5); transition: background 0.1s; }
  .tabla-row.clickable { cursor: pointer; }
  .tabla-row:hover { background: rgba(179,144,40,0.04); }

  .estado-tabla {
    text-align: center; padding: 3rem 1rem;
    color: var(--color-text-faint); font-family: var(--font-mono); font-size: var(--text-md);
  }
  .sin-datos { display: table-cell; }

  .td-mono   { font-family: var(--font-mono); }
  .td-muted  { color: var(--color-text-muted); }
  .td-fecha  { font-family: var(--font-mono); color: var(--color-text-dim); font-size: var(--text-sm); }
  .td-right  { text-align: right; }
  .td-center { text-align: center; }

  .nombre-text { display: block; font-weight: 600; }
  .ruc-sub     { display: block; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-dim); }

  .badge-count {
    display: inline-block; padding: 0.15rem 0.6rem;
    background: rgba(179,144,40,0.1); border: 1px solid rgba(179,144,40,0.25);
    border-radius: 2px; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-gold);
  }

  .badge-estado {
    display: inline-block; padding: 0.18rem 0.55rem; border-radius: 2px;
    font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: 0.12em; font-weight: 700;
  }
  .badge-estado.completo  { background: var(--color-success-bg); color: #4ade80; border: 1px solid rgba(81,161,85,0.3); }
  .badge-estado.parcial   { background: var(--color-gold-bg); color: var(--color-gold); border: 1px solid rgba(179,144,40,0.3); }
  .badge-estado.pendiente { background: var(--color-warning-bg); color: var(--color-warning); border: 1px solid rgba(207,151,61,0.3); }

  .acciones-grupo { display: flex; gap: 0.4rem; }
  .btn-accion {
    background: transparent; border: 1px solid var(--color-border);
    color: var(--color-text-muted); width: 30px; height: 30px;
    border-radius: var(--radius-sm); cursor: pointer;
    display: flex; align-items: center; justify-content: center; transition: all 0.15s;
  }
  .btn-accion:hover:not(:disabled) { border-color: var(--color-gold); color: var(--color-gold); }
  .btn-accion:disabled { opacity: 0.4; cursor: not-allowed; }

  .tabla-footer { display: flex; justify-content: flex-end; padding: 0.6rem 1rem; border-top: 1px solid var(--color-border); }
  .tabla-count  { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-faint); letter-spacing: 0.08em; }

  .spinner { animation: spin 0.8s linear infinite; display: inline-block; }
  @keyframes spin { to { transform: rotate(360deg); } }
  </style>
