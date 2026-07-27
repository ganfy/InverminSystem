<template>
    <div class="page-container">

      <!-- Header -->
      <header class="page-header">
        <div class="header-title-row">
          <Boxes class="header-icon" :size="26" />
          <div>
            <h1 class="page-title">Rumas</h1>
            <p class="page-subtitle">
              {{ store.campanaActiva ? store.campanaActiva.codigo : '—' }}
              · {{ store.rumas.length }} ruma{{ store.rumas.length !== 1 ? 's' : '' }}
            </p>
          </div>
        </div>
        <div style="display:flex;gap:0.75rem;align-items:center">
          <button
            v-if="puedeEditar && store.campanaActiva"
            class="btn-primary btn-con-icono ready"
            :disabled="store.cargando"
            @click="crearRuma"
          >
            <Plus :size="16" /> Nueva Ruma
          </button>
        </div>
      </header>

      <!-- Sin campaña -->
      <div v-if="!store.campanaActiva && !store.cargando" class="estado-tabla">
        No hay campaña activa.
        <router-link to="/administracion/campanas" class="link-accion">Gestionar campañas →</router-link>
      </div>

      <!-- Cargando -->
      <div v-else-if="store.cargando" class="estado-cargando">
        <span class="spinner-sm" /> Cargando rumas…
      </div>

      <!-- Sin rumas -->
      <div v-else-if="!store.rumas.length" class="vacio-panel">
        <Boxes :size="36" style="opacity:0.3;margin-bottom:0.75rem" />
        <p>No hay rumas en esta campaña.</p>
        <button v-if="puedeEditar" class="btn-primary ready" style="margin-top:1rem" @click="crearRuma">
          <Plus :size="15" style="margin-right:0.35rem" /> Crear primera ruma
        </button>
      </div>

      <!-- Tabla de rumas -->
      <div v-else class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>CÓDIGO</th>
              <th class="col-r">LOTES</th>
              <th class="col-r">TMS TOTAL</th>
              <th class="col-r">LEY POND.</th>
              <th class="col-r">% REC.</th>
              <th>ESTADO</th>
              <th>FECHA</th>
              <th />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="ruma in store.rumas"
              :key="ruma.id"
              class="tabla-row"
              style="cursor:pointer"
              @click="irADetalle(ruma.id)"
            >
              <td class="td-mono td-gold">{{ ruma.codigo }}</td>
              <td class="col-r td-mono">{{ ruma.total_lotes }}</td>
              <td class="col-r td-mono">{{ fmtNum(ruma.total_tms, 3) }} T</td>
              <td class="col-r td-mono">
                <span v-if="ruma.ley_ponderada != null">{{ fmtNum(ruma.ley_ponderada, 4) }}</span>
                <span v-else class="td-dim">—</span>
              </td>
              <td class="col-r td-mono">
                <span v-if="ruma.rec_promedio != null">{{ fmtNum(ruma.rec_promedio, 1) }}%</span>
                <span v-else class="td-dim">—</span>
              </td>
              <td>
                <span class="badge-estado" :class="badgeRuma(ruma.estado)">
                  {{ ruma.estado }}
                </span>
              </td>
              <td class="td-fecha td-muted">{{ fmtDate(ruma.fecha_creacion) }}</td>
              <td class="col-acciones" @click.stop>
                <div class="td-acciones">
                  <button class="btn-icon" title="Ver detalle" @click="irADetalle(ruma.id)">
                    <ChevronRight :size="14" />
                  </button>
                  <button
                    v-if="puedeEditar && ruma.estado === 'ABIERTA'"
                    class="btn-icon warn"
                    title="Cerrar ruma"
                    @click="pedirCerrarRuma(ruma)"
                  >
                    <Lock :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Panel resumen campaña abajo -->
      <div v-if="store.campanaActiva" class="resumen-campana">
        <div class="resumen-item">
          <span class="resumen-lbl">ORO ACUMULADO</span>
          <span class="resumen-val gold">{{ fmtNum(store.campanaActiva.oro_fino_acumulado, 2) }} g</span>
        </div>
        <div class="resumen-barra-wrap">
          <div class="resumen-barra-fill" :style="{ width: Math.min(store.campanaActiva.progreso_pct, 100) + '%' }" />
          <span class="resumen-barra-pct">{{ store.campanaActiva.progreso_pct.toFixed(1) }}%</span>
        </div>
        <div class="resumen-item">
          <span class="resumen-lbl">META</span>
          <span class="resumen-val">{{ fmtNum(store.campanaActiva.meta_oro_fino, 0) }} g</span>
        </div>
        <router-link to="/administracion/campanas" class="resumen-link">Gestionar campaña →</router-link>
      </div>

    </div>
  </template>

  <script setup lang="ts">
  import { computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { Boxes, Plus, ChevronRight, Lock } from 'lucide-vue-next'
  import { useRumasStore } from '@/stores/rumas'
  import { useAuthStore } from '@/stores/auth'
  import { useUiStore } from '@/stores/ui'
  import type { RumaLista } from '@/api/rumas'

  const store  = useRumasStore()
  const auth   = useAuthStore()
  const ui     = useUiStore()
  const router = useRouter()

  const puedeEditar = computed(() =>
    ['Admin', 'Gerencia', 'Comercial', 'JefeComercial'].includes(auth.user?.rol ?? '')
  )

  function fmtNum(v: number | null | undefined, dec = 2) {
    if (v == null) return '—'
    return new Intl.NumberFormat('es-PE', { minimumFractionDigits: dec, maximumFractionDigits: dec }).format(v)
  }
  function fmtDate(s: string | null | undefined) {
    if (!s) return '—'
    return new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }
  function badgeRuma(estado: string) {
    return estado === 'ABIERTA' ? 'badge-activo' : 'badge-inactivo'
  }

  async function crearRuma() {
    const nueva = await store.crearRuma()
    if (nueva) {
      ui.toast(`Ruma ${nueva.codigo} creada`, 'success')
      router.push(`/rumas/${nueva.id}`)
    } else {
      ui.toast(store.error ?? 'Error al crear ruma', 'error')
    }
  }

  function irADetalle(id: number) {
    router.push(`/rumas/${id}`)
  }

  async function pedirCerrarRuma(ruma: RumaLista) {
    const ok = await ui.showConfirm({
      title: `Cerrar ${ruma.codigo}`,
      message: `¿Cerrar la ruma ${ruma.codigo}? Una vez cerrada no se pueden asignar más lotes.`,
      confirmLabel: 'Cerrar ruma',
      danger: true,
    })
    if (!ok) return
    const exito = await store.cerrarRuma(ruma.id)
    if (exito) ui.toast(`Ruma ${ruma.codigo} cerrada`, 'success')
    else ui.toast(store.error ?? 'Error al cerrar ruma', 'error')
  }

  onMounted(async () => {
    await store.cargarCampanaActiva()
    await store.cargarRumas()
  })
  </script>

  <style scoped>
  @import '@/assets/base.css';

  .col-r { text-align: right; }
  .td-gold { color: var(--color-gold) !important; }
  .td-dim  { color: var(--color-text-dim); }
  .btn-con-icono { display: inline-flex; align-items: center; gap: 0.4rem; }

  /* Vacío */
  .vacio-panel {
    text-align: center;
    padding: 3.5rem 1rem;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-md);
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  /* Resumen campaña */
  .resumen-campana {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 1.5rem;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1.25rem;
    flex-wrap: wrap;
  }
  .resumen-item { display: flex; flex-direction: column; gap: 0.15rem; }
  .resumen-lbl {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.15em;
    color: var(--color-text-muted);
  }
  .resumen-val {
    font-family: var(--font-mono);
    font-size: var(--text-base);
    font-weight: 700;
    color: var(--color-text);
  }
  .resumen-val.gold { color: var(--color-gold); }
  .resumen-barra-wrap {
    flex: 1;
    position: relative;
    background: rgba(58,58,40,0.5);
    border-radius: 2px;
    height: 18px;
    min-width: 80px;
    overflow: hidden;
  }
  .resumen-barra-fill {
    height: 100%;
    background: var(--color-gold);
    border-radius: 2px;
    transition: width 0.5s ease;
  }
  .resumen-barra-pct {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    font-weight: 700;
    color: var(--color-bg);
  }
  .resumen-link {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-gold);
    text-decoration: none;
    margin-left: auto;
  }
  .resumen-link:hover { text-decoration: underline; }
  .link-accion {
    color: var(--color-gold);
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    text-decoration: none;
    margin-left: 0.5rem;
  }
  .estado-cargando {
    display: flex; gap: 0.5rem; align-items: center;
    color: var(--color-text-muted);
    font-family: var(--font-mono);
    font-size: var(--text-md);
    padding: 2rem 0;
  }
  </style>
