<template>
  <div class="dashboard-page">
    <header class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <span class="last-sync" v-if="lastUpdate">Última actualización: {{ lastUpdate }}</span>
    </header>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner"></span> Cargando métricas en tiempo real...
    </div>

    <template v-else>
      <section class="kpi-grid">
        <div class="kpi-card gold-accent">
          <div class="kpi-info">
            <span class="kpi-label">Au Real 100%</span>
            <span class="kpi-value">{{ data?.kpis.au_real_100.toLocaleString() }}g</span>
          </div>
          <Zap class="kpi-icon" :size="36" />
        </div>

        <div class="kpi-card gold-accent">
          <div class="kpi-info">
            <span class="kpi-label">Au Real Rec.</span>
            <span class="kpi-value">{{ data?.kpis.au_real_rec.toLocaleString() }}g</span>
          </div>
          <TrendingUp class="kpi-icon" :size="36" />
        </div>

        <div class="kpi-card">
          <div class="kpi-info">
            <span class="kpi-label">TMH en Stock</span>
            <span class="kpi-value highlight">{{ data?.kpis.tmh_stock.toFixed(2) }} TM</span>
          </div>
          <Scale class="kpi-icon" :size="36" />
        </div>

        <div class="kpi-card">
          <div class="kpi-info">
            <span class="kpi-label">TMS en Stock</span>
            <span class="kpi-value">{{ data?.kpis.tms_stock.toFixed(2) }} TM</span>
          </div>
          <Database class="kpi-icon" :size="36" />
        </div>

        <div class="kpi-card">
          <div class="kpi-info">
            <span class="kpi-label">Oz en Stock</span>
            <span class="kpi-value">{{ data?.kpis.oz_stock.toFixed(2) }} oz</span>
          </div>
          <Coins class="kpi-icon" :size="36" />
        </div>
      </section>

      <section class="card table-section">
    <div class="table-header">
      <h2 class="section-title">Lotes Recientes</h2>
      <div class="table-actions">
          <div class="search-wrapper">
            <Search class="search-icon" :size="16" />
            <input
              v-model="searchFilter"
              type="text"
              placeholder="Buscar IP, Proveedor..."
              class="field-input"
            />
          </div>
      </div>
    </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Lote</th>
                <th class="align-right">TMH</th>
                <th class="align-right">TMS</th>
                <th class="align-right">%H2O</th>
                <th>Proveedor</th>
                <th>RUC</th>
                <th class="align-right">Ley Prom.</th>
                <th class="align-right">% Rec.</th>
                <th>Acopiador</th>
                <th class="align-center">Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lote in lotesFiltrados" :key="lote.ip">
                <td class="td-mono gold">{{ lote.ip }}</td>
                <td class="align-right td-mono">{{ lote.tmh.toFixed(3) }}</td>
                <td class="align-right td-mono">{{ lote.tms?.toFixed(3) ?? '---' }}</td>
                <td class="align-right td-mono">{{ lote.h2o_porc ? lote.h2o_porc + '%' : '---' }}</td>
                <td class="td-truncate" :title="lote.proveedor">{{ lote.proveedor }}</td>
                <td class="td-mono">{{ lote.ruc }}</td>
                <td class="align-right td-mono">{{ lote.ley_avg?.toFixed(2) ?? '---' }}</td>
                <td class="align-right td-mono">{{ lote.rec_porc ? lote.rec_porc + '%' : '---' }}</td>
                <td class="td-truncate" :title="lote.acopiador || ''">{{ lote.acopiador || '---' }}</td>
                <td class="align-center">
                  <span class="badge-estado" :class="lote.estado.toLowerCase().replace(' ', '-')">
                    {{ lote.estado }}
                  </span>
                </td>
              </tr>
              <tr v-if="data?.lotes.length === 0">
                <td colspan="10" class="empty-state">No hay lotes registrados todavía.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue' // Agregamos computed
import { Zap, TrendingUp, Scale, Database, Coins, Search } from 'lucide-vue-next' // Agregamos Search
import { dashboardApi, type DashboardResponse } from '@/api/dashboard'

const data = ref<DashboardResponse | null>(null)
const lastUpdate = ref<string | null>(null)
const cargando = ref(true)
const searchFilter = ref('') // Variable para el filtro

// Lógica de filtrado reactivo
const lotesFiltrados = computed(() => {
  if (!data.value) return []
  if (!searchFilter.value.trim()) return data.value.lotes

  const query = searchFilter.value.toLowerCase()
  return data.value.lotes.filter(lote =>
    lote.ip.toLowerCase().includes(query) ||
    lote.proveedor.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  try {
    data.value = await dashboardApi.getResumen()
    lastUpdate.value = new Date().toLocaleTimeString('es-PE')
  } catch (error) {
    console.error("Error cargando dashboard:", error)
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.dashboard-page {
  padding: var(--page-padding);
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.last-sync {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ── KPIs ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-lg);
}

.kpi-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.gold-accent {
  border-left: 4px solid var(--color-gold);
}

.kpi-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.kpi-label {
  font-family: var(--font-main);
  font-size: var(--text-xs);
  font-weight: 700;
  color: var(--color-text-muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.kpi-value {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
}

.kpi-value.highlight {
  color: var(--color-gold-light);
}

.kpi-icon {
  color: var(--color-text-muted);
  opacity: 0.4;
}

/* ── TABLA ── */
.table-section {
  margin-top: 4%;
  padding: var(--spacing-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.data-table th {
  text-align: left;
  padding: var(--spacing-md);
  border-bottom: 2px solid var(--color-border);
  color: var(--color-text-muted);
  font-family: var(--font-main);
  font-weight: 600;
  white-space: nowrap;
}

.data-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.td-mono { font-family: var(--font-mono); }
.gold { color: var(--color-gold); font-weight: bold; }
.align-right { text-align: right !important; }
.align-center { text-align: center !important; }

/* Truncar textos largos (como nombres de empresas) */
.td-truncate {
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Badges de estado */
.badge-estado {
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: bold;
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap;
}

.en-proceso { background-color: var(--color-warning-bg, rgba(220,160,20,0.1)); color: var(--color-warning); border: 1px solid rgba(220,160,20,0.3); }
.completado { background-color: var(--color-success-bg, rgba(60,180,80,0.1)); color: var(--color-success); border: 1px solid rgba(60,180,80,0.3); }
.pendiente { background-color: var(--color-error-bg, rgba(220,60,60,0.1)); color: var(--color-error); border: 1px solid rgba(220,60,60,0.3); }

.empty-state {
  text-align: center;
  padding: calc(var(--spacing-xl) * 2) !important;
  color: var(--color-text-dim);
  font-style: italic;
}

/* Añade esto a tu sección <style scoped> */
.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.field-input {
  padding-left: 36px; /* Espacio para el ícono */
  width: 300px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.field-input:focus {
  border-color: var(--color-gold);
  box-shadow: 0 0 0 2px rgba(184, 150, 46, 0.2);
  outline: none;
}
</style>
