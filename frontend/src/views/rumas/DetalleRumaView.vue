<template>
    <div class="page-container">

      <!-- Header -->
      <header class="page-header">
        <div style="display:flex;align-items:center;gap:0.75rem">
          <button class="btn-icon" @click="router.push('/rumas')">
            <ChevronLeft :size="18" />
          </button>
          <div>
            <h1 class="page-title" style="padding-bottom:0">
              {{ store.rumaDetalle?.codigo ?? 'Cargando…' }}
            </h1>
            <p class="page-subtitle">
              {{ store.rumaDetalle?.estado === 'CERRADA' ? '🔒 Ruma cerrada' : 'Asignación de lotes' }}
            </p>
          </div>
        </div>
        <div style="display:flex;gap:0.75rem;align-items:center" v-if="store.rumaDetalle">
          <button
            v-if="puedeEditar && store.rumaDetalle.estado === 'ABIERTA'"
            class="btn-danger btn-sm"
            @click="pedirCerrarRuma"
          >
            <Lock :size="14" style="margin-right:0.35rem" /> Cerrar ruma
          </button>
        </div>
      </header>

      <!-- Loading inicial -->
      <div v-if="store.cargandoDetalle && !store.rumaDetalle" class="estado-cargando">
        <span class="spinner-sm" /> Cargando ruma…
      </div>

      <template v-else-if="store.rumaDetalle">

        <!-- Panel de totales (preview en tiempo real) -->
        <div class="totales-panel" :class="{ 'totales-modificado': hayPendientes }">
          <div class="totales-grid">
            <div class="total-item">
              <span class="total-lbl">LOTES</span>
              <span class="total-val">{{ ipsSeleccionadas.size }}</span>
              <span v-if="hayPendientes" class="total-delta">
                {{ ipsSeleccionadas.size - store.rumaDetalle.total_lotes > 0 ? '+' : '' }}{{ ipsSeleccionadas.size - store.rumaDetalle.total_lotes }}
              </span>
            </div>
            <div class="total-item">
              <span class="total-lbl">TMS TOTAL</span>
              <span class="total-val">{{ fmtNum(preview.total_tms, 3) }} T</span>
            </div>
            <div class="total-item">
              <span class="total-lbl">LEY POND.</span>
              <span class="total-val">{{ preview.ley_ponderada != null ? fmtNum(preview.ley_ponderada, 4) : '—' }}</span>
              <span class="total-sub">oz/tc</span>
            </div>
            <div class="total-item">
              <span class="total-lbl">% REC. PROM.</span>
              <span class="total-val">{{ preview.rec_promedio != null ? fmtNum(preview.rec_promedio, 1) + '%' : '—' }}</span>
            </div>
            <div class="total-item">
              <span class="total-lbl">% LLAMPO</span>
              <span class="total-val">{{ preview.pct_llampo != null ? fmtNum(preview.pct_llampo, 1) + '%' : '—' }}</span>
            </div>
          </div>

          <!-- Acciones de guardado -->
          <div v-if="hayPendientes && puedeEditar && store.rumaDetalle.estado === 'ABIERTA'" class="totales-acciones">
            <span class="pendientes-aviso">
              <AlertCircle :size="14" /> {{ cambiosPendientes }} cambio{{ cambiosPendientes !== 1 ? 's' : '' }} sin guardar
            </span>
            <button class="btn-secondary btn-sm" @click="descartarCambios">Descartar</button>
            <button
              class="btn-primary btn-sm ready"
              :disabled="store.cargandoDetalle"
              @click="guardarAsignacion"
            >
              <span v-if="store.cargandoDetalle" class="spinner" />
              <span v-else>Guardar asignación</span>
            </button>
          </div>
          <p v-if="store.error" class="error-msg" style="margin-top:0.5rem;text-align:right">{{ store.error }}</p>
        </div>

        <!-- Layout split -->
        <div class="split-layout">

          <!-- Izquierda: lotes en la ruma -->
          <div class="split-col">
            <div class="split-header">
              <span class="split-titulo">EN LA RUMA</span>
              <span class="split-count">{{ ipsEnRuma.size }} lote{{ ipsEnRuma.size !== 1 ? 's' : '' }}</span>
            </div>

            <div v-if="!lotesMostradosEnRuma.length" class="col-vacio">
              Sin lotes asignados aún
            </div>

            <div
              v-for="lote in lotesMostradosEnRuma"
              :key="lote.ip"
              class="lote-card lote-en-ruma"
              :class="{ 'lote-quitado': !ipsSeleccionadas.has(lote.ip) }"
            >
              <div class="lote-ip">{{ lote.ip }}</div>
              <div class="lote-meta">
                <span class="lote-prov">{{ lote.proveedor }}</span>
                <span class="lote-stats">
                  {{ fmtNum(lote.tms, 3) }} TMS
                  <span v-if="lote.ley_avg != null"> · Ley {{ fmtNum(lote.ley_avg, 4) }}</span>
                  <span v-if="lote.rec_porc != null"> · {{ fmtNum(lote.rec_porc, 1) }}% rec</span>
                </span>
                <span v-if="lote.volado" class="badge-volado">VOLADO</span>
                <span v-if="lote.tipo_material" class="badge-material">{{ lote.tipo_material }}</span>
              </div>
              <button
                v-if="puedeEditar && store.rumaDetalle?.estado === 'ABIERTA'"
                class="btn-icon danger lote-quitar"
                title="Quitar de ruma"
                @click="quitarLote(lote.ip)"
              >
                <Minus :size="13" />
              </button>
            </div>
          </div>

          <!-- Derecha: pool de disponibles -->
          <div class="split-col">
            <div class="split-header">
              <span class="split-titulo">DISPONIBLES PARA AGREGAR</span>
              <span class="split-count">{{ lotesFiltrados.length }}</span>
            </div>

            <!-- Filtros -->
            <div class="pool-filtros">
              <input
                v-model="filtroTexto"
                class="field-input filtro-input-sm"
                placeholder="IP, proveedor…"
              />
              <select v-model="filtroMaterial" class="field-input field-select filtro-input-sm">
                <option value="">Todo</option>
                <option value="mineral">Mineral</option>
                <option value="llampo">Llampo</option>
              </select>
            </div>

            <div
              v-if="store.cargandoDetalle && !store.lotesDisponibles.length"
              class="col-vacio"
            >
              <span class="spinner-sm" /> Cargando…
            </div>
            <div v-else-if="!lotesFiltrados.length" class="col-vacio">
              Sin lotes disponibles
            </div>

            <div
              v-for="lote in lotesFiltrados"
              :key="lote.ip"
              class="lote-card lote-disponible"
              :class="{
                'lote-agregado': ipsSeleccionadas.has(lote.ip),
                'lote-disabled': store.rumaDetalle?.estado === 'CERRADA',
              }"
            >
              <div class="lote-ip">{{ lote.ip }}</div>
              <div class="lote-meta">
                <span class="lote-prov">{{ lote.proveedor }}</span>
                <span v-if="lote.acopiador" class="lote-acop">{{ lote.acopiador }}</span>
                <span class="lote-stats">
                  {{ fmtNum(lote.tms, 3) }} TMS
                  <span v-if="lote.ley_avg != null"> · Ley {{ fmtNum(lote.ley_avg, 4) }}</span>
                  <span v-if="lote.rec_porc != null"> · {{ fmtNum(lote.rec_porc, 1) }}% rec</span>
                  · {{ lote.dias_almacen }}d almacén
                </span>
                <div style="display:flex;gap:0.35rem;flex-wrap:wrap;margin-top:0.2rem">
                  <span v-if="lote.volado" class="badge-volado">VOLADO</span>
                  <span v-if="lote.tipo_material" class="badge-material">{{ lote.tipo_material }}</span>
                </div>
              </div>
              <button
                v-if="puedeEditar && store.rumaDetalle?.estado === 'ABIERTA'"
                class="btn-icon success lote-agregar"
                :class="{ 'lote-check': ipsSeleccionadas.has(lote.ip) }"
                :title="ipsSeleccionadas.has(lote.ip) ? 'Ya agregado' : 'Agregar a ruma'"
                @click="toggleLote(lote.ip)"
              >
                <Check v-if="ipsSeleccionadas.has(lote.ip)" :size="13" />
                <Plus v-else :size="13" />
              </button>
            </div>
          </div>

        </div>
      </template>

    </div>
  </template>

  <script setup lang="ts">
  import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { ChevronLeft, Lock, Plus, Minus, Check, AlertCircle } from 'lucide-vue-next'
  import { useRumasStore } from '@/stores/rumas'
  import { useAuthStore } from '@/stores/auth'
  import { useUiStore } from '@/stores/ui'

  const route  = useRoute()
  const router = useRouter()
  const store  = useRumasStore()
  const auth   = useAuthStore()
  const ui     = useUiStore()

  const rumaId = Number(route.params.id)

  // Filtros del pool
  const filtroTexto    = ref('')
  const filtroMaterial = ref('')

  const puedeEditar = computed(() =>
    ['Admin', 'Gerencia', 'Comercial'].includes(auth.user?.rol ?? '')
  )

  // IPs actualmente en la ruma (de la respuesta del servidor)
  const ipsEnRuma = computed(() => new Set(store.rumaDetalle?.lotes.map(l => l.ip) ?? []))

  // Selección local (preview antes de guardar)
  // Se inicializa con los lotes ya en ruma
  const ipsSeleccionadas = ref<Set<string>>(new Set())

  watch(() => store.rumaDetalle, (val) => {
    if (val) ipsSeleccionadas.value = new Set(val.lotes.map(l => l.ip))
  }, { immediate: true })

  // ¿Hay cambios pendientes?
  const hayPendientes = computed(() => {
    const actual = ipsEnRuma.value
    const sel    = ipsSeleccionadas.value
    if (actual.size !== sel.size) return true
    for (const ip of sel) if (!actual.has(ip)) return true
    return false
  })

  const cambiosPendientes = computed(() => {
    let c = 0
    for (const ip of ipsSeleccionadas.value) if (!ipsEnRuma.value.has(ip)) c++
    for (const ip of ipsEnRuma.value)         if (!ipsSeleccionadas.value.has(ip)) c++
    return c
  })

  // Preview calculada en tiempo real (store.calcularPreviewRuma incluye lotes en ruma + nuevos)
  const preview = computed(() =>
    store.calcularPreviewRuma(Array.from(ipsSeleccionadas.value))
  )

  // Lotes mostrados en el panel izquierdo (los que ya estaban + los recién agregados del pool)
  const lotesMostradosEnRuma = computed(() => {
    const base = store.rumaDetalle?.lotes ?? []
    // Agregar los del pool que están seleccionados pero no están aún en rumaDetalle
    const extra = store.lotesDisponibles.filter(l => ipsSeleccionadas.value.has(l.ip))
    const todos = [
      ...base,
      ...extra.map(l => ({
        ip: l.ip,
        proveedor: l.proveedor,
        tmh: l.tmh,
        tms: l.tms,
        ley_avg: l.ley_avg,
        rec_porc: l.rec_porc,
        tipo_material: l.tipo_material,
        habilitado_ruma: true,
        volado: l.volado,
      })),
    ]
    // Dedup
    const visto = new Set<string>()
    return todos.filter(l => { if (visto.has(l.ip)) return false; visto.add(l.ip); return true })
  })

  // Pool filtrado (disponibles que no estén ya en la ruma actual del servidor)
  const lotesFiltrados = computed(() => {
    return store.lotesDisponibles.filter(l => {
      // Ya en ruma → no mostrar en pool (salvo que estén "quitados" por la selección local)
      if (ipsEnRuma.value.has(l.ip)) return false
      const txt = filtroTexto.value.toLowerCase()
      if (txt && !l.ip.toLowerCase().includes(txt) && !l.proveedor.toLowerCase().includes(txt)) return false
      if (filtroMaterial.value && !l.tipo_material?.toLowerCase().includes(filtroMaterial.value)) return false
      return true
    })
  })

  function toggleLote(ip: string) {
    const s = new Set(ipsSeleccionadas.value)
    if (s.has(ip)) s.delete(ip)
    else s.add(ip)
    ipsSeleccionadas.value = s
  }

  function quitarLote(ip: string) {
    const s = new Set(ipsSeleccionadas.value)
    s.delete(ip)
    ipsSeleccionadas.value = s
  }

  function descartarCambios() {
    ipsSeleccionadas.value = new Set(store.rumaDetalle?.lotes.map(l => l.ip) ?? [])
  }

  async function guardarAsignacion() {
    const ok = await store.guardarAsignacion(rumaId, Array.from(ipsSeleccionadas.value))
    if (ok) ui.toast('Asignación guardada', 'success')
    else ui.toast(store.error ?? 'Error al guardar', 'error')
  }

  async function pedirCerrarRuma() {
    const ok = await ui.showConfirm({
      title: `Cerrar ${store.rumaDetalle?.codigo}`,
      message: 'Una ruma cerrada no acepta más cambios. ¿Continuar?',
      confirmLabel: 'Cerrar ruma',
      danger: true,
    })
    if (!ok) return
    const exito = await store.cerrarRuma(rumaId)
    if (exito) ui.toast('Ruma cerrada', 'success')
    else ui.toast(store.error ?? 'Error al cerrar ruma', 'error')
  }

  function fmtNum(v: number | null | undefined, dec = 2) {
    if (v == null) return '—'
    return new Intl.NumberFormat('es-PE', { minimumFractionDigits: dec, maximumFractionDigits: dec }).format(v)
  }

  onMounted(() => {
    store.cargarDetalleRuma(rumaId)
  })
  onUnmounted(() => {
    store.limpiarDetalle()
  })
  </script>

  <style scoped>
  @import '@/assets/base.css';

  /* Totales panel */
  .totales-panel {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 1rem 1.5rem;
    margin-bottom: 1.25rem;
    transition: border-color 0.2s;
  }
  .totales-panel.totales-modificado {
    border-color: var(--color-warning);
    background: rgba(207, 151, 61, 0.04);
  }
  .totales-grid {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    align-items: flex-end;
    margin-bottom: 0.25rem;
  }
  .total-item {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    min-width: 80px;
  }
  .total-lbl {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.15em;
    color: var(--color-text-muted);
  }
  .total-val {
    font-family: var(--font-mono);
    font-size: var(--text-lg);
    font-weight: 700;
    color: var(--color-text);
  }
  .total-sub {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-dim);
  }
  .total-delta {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-warning);
  }
  .totales-acciones {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(58,58,40,0.4);
    margin-top: 0.5rem;
    flex-wrap: wrap;
  }
  .pendientes-aviso {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-warning);
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    flex: 1;
  }
  .btn-sm {
    padding: 0.4rem 0.85rem !important;
    font-size: var(--text-sm) !important;
    min-height: 32px !important;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }

  /* Split layout */
  .split-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    align-items: start;
  }
  @media (max-width: 800px) { .split-layout { grid-template-columns: 1fr; } }

  .split-col {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
    max-height: 72vh;
    display: flex;
    flex-direction: column;
  }
  .split-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--color-border);
    background: rgba(184,150,46,0.06);
    flex-shrink: 0;
  }
  .split-titulo {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.18em;
    color: var(--color-gold);
    font-weight: 700;
  }
  .split-count {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  /* Filtros pool */
  .pool-filtros {
    display: flex;
    gap: 0.5rem;
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid var(--color-border);
    flex-shrink: 0;
  }
  .filtro-input-sm {
    padding: 0.35rem 0.6rem !important;
    font-size: var(--text-sm) !important;
  }

  /* Cards de lotes */
  .lote-card {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.7rem 1rem;
    border-bottom: 1px solid rgba(58,58,40,0.4);
    transition: background 0.15s;
    flex-shrink: 0;
    overflow-y: auto;
  }
  .split-col > .lote-card:last-child { border-bottom: none; }
  .split-col > .col-vacio ~ .lote-card { overflow-y: auto; }

  /* Scroll dentro del col */
  .split-col > :not(.split-header):not(.pool-filtros) {
    overflow-y: auto;
  }

  .lote-en-ruma  { background: rgba(81,161,85,0.04); }
  .lote-quitado  { background: rgba(165,71,61,0.07); opacity: 0.6; }
  .lote-disponible:hover { background: rgba(184,150,46,0.04); cursor: pointer; }
  .lote-agregado { background: rgba(81,161,85,0.07); }
  .lote-disabled { pointer-events: none; opacity: 0.5; }

  .lote-ip {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    font-weight: 700;
    color: var(--color-gold);
    min-width: 72px;
    flex-shrink: 0;
  }
  .lote-meta {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }
  .lote-prov {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text);
  }
  .lote-acop {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
  .lote-stats {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-dim);
  }
  .badge-volado {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.08em;
    background: var(--color-volado-bg);
    color: var(--color-volado);
    border-radius: 2px;
    padding: 1px 5px;
    border: 1px solid rgba(68,122,239,0.3);
  }
  .badge-material {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.06em;
    background: var(--color-gold-bg);
    color: var(--color-gold);
    border-radius: 2px;
    padding: 1px 5px;
    border: 1px solid rgba(179,144,40,0.2);
  }
  .lote-quitar { flex-shrink: 0; align-self: center; }
  .lote-agregar { flex-shrink: 0; align-self: center; }
  .lote-check {
    border-color: var(--color-success) !important;
    color: var(--color-success) !important;
    background: rgba(81,161,85,0.1) !important;
  }

  .col-vacio {
    padding: 2rem;
    text-align: center;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-md);
  }
  .estado-cargando {
    display: flex; gap: 0.5rem; align-items: center;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-md);
    padding: 2rem 0;
  }
  </style>
