<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMuestreoStore } from '@/stores/muestreo'

const router = useRouter()
const store = useMuestreoStore()

// Manejo de Tabs
const tabActual = ref<'PENDIENTES' | 'COMPLETADOS'>('PENDIENTES')

// Computed para filtrar las listas según el tab
const lotesMostrar = computed(() => {
  return tabActual.value === 'PENDIENTES'
    ? store.lotesPendientes
    : store.lotesCompletados
})

onMounted(async () => {
  // Inicialización (luego conectaremos esto con la carga real de datos)
})

function irARegistrarHumedad(ip: string) {
  router.push({ name: 'RegistrarHumedad', params: { ip } })
}

function abrirModalEtiquetas(ip: string) {
  // Lógica para el modal de códigos CIP
  console.log('Abriendo modal para:', ip)
}
</script>

<template>
  <div class="muestreo-page">
    <div class="page-header">
      <h1 class="page-title">Muestreo</h1>
    </div>

    <div class="tabs-container">
      <button
        class="tab-btn"
        :class="{ active: tabActual === 'PENDIENTES' }"
        @click="tabActual = 'PENDIENTES'"
      >
        Pendientes
        <span class="tab-badge">{{ store.lotesPendientes.length }}</span>
      </button>
      <button
        class="tab-btn"
        :class="{ active: tabActual === 'COMPLETADOS' }"
        @click="tabActual = 'COMPLETADOS'"
      >
        Completados
        <span class="tab-badge completados">{{ store.lotesCompletados.length }}</span>
      </button>
    </div>

    <div class="cards-grid">
      <div v-if="lotesMostrar.length === 0" class="sin-datos">
        No hay lotes en esta sección.
      </div>

      <div
        v-for="lote in lotesMostrar"
        :key="lote.ip"
        class="card-lote"
      >
        <div class="card-header">
          <div class="lote-info">
            <span class="lote-label">LOTE</span>
            <h2 class="lote-ip">{{ lote.ip }}</h2>
          </div>
          <span
            class="badge-estado"
            :class="tabActual === 'PENDIENTES' ? 'en-proceso' : 'completo'"
          >
            {{ tabActual === 'PENDIENTES' ? 'PENDIENTE' : 'COMPLETADO' }}
          </span>
        </div>

        <div class="card-body">
          <p class="data-row">
            <span class="td-muted">Recibido:</span>
            <span class="td-mono">{{ lote.fecha_recepcion || '---' }}</span>
          </p>
          <p class="data-row">
            <span class="td-muted">Peso TMH:</span>
            <span class="td-mono highlight">{{ lote.peso_neto || '0.00' }} TM</span>
          </p>
          <p class="data-row">
            <span class="td-muted">Sacos:</span>
            <span class="td-mono">{{ lote.sacos || 'A GRANEL' }}</span>
          </p>
        </div>

        <div class="card-actions">
          <template v-if="tabActual === 'PENDIENTES'">
            <button class="btn-primary flex-1" @click="irARegistrarHumedad(lote.ip)">
              Registrar Humedad
            </button>
            <button
              v-if="lote.tiene_humedad && !lote.etiquetado"
              class="btn-secondary flex-1"
              @click="abrirModalEtiquetas(lote.ip)"
            >
              Etiquetar Lote
            </button>
          </template>

          <template v-else>
            <button class="btn-secondary flex-1">
              Ver Detalles
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.muestreo-page {
  padding: var(--page-padding);
  max-width: 1200px;
  margin: 0 auto;
}

/* ── Tabs Táctiles ── */
.tabs-container {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: calc(var(--spacing-lg) * 1.5);
  border-bottom: 2px solid var(--color-border);
}

.tab-btn {
  background: none;
  border: none;
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--text-base);
  font-family: var(--font-main);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  border-bottom: 3px solid transparent;
  margin-bottom: -2px; /* Superpone el borde */
  transition: all 0.2s ease;
}

.tab-btn.active {
  color: var(--color-gold);
  border-bottom-color: var(--color-gold);
}

.tab-badge {
  background: var(--color-gold-bg);
  color: var(--color-gold);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  padding: 0.1rem 0.5rem;
  border-radius: var(--radius-md);
  font-weight: bold;
}

.tab-badge.completados {
  background: var(--color-bg-input);
  color: var(--color-text-dim);
}

/* ── Grid de Tarjetas (Tablet/Desktop) ── */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.sin-datos {
  grid-column: 1 / -1;
  text-align: center;
  padding: calc(var(--spacing-lg) * 2);
  color: var(--color-text-muted);
  background: var(--color-bg-input);
  border-radius: var(--radius-md);
  border: 1px dashed var(--color-border);
  font-size: var(--text-base);
}

/* ── Estilo de Tarjeta Individual ── */
.card-lote {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  box-shadow: 0 4px 6px rgba(0,0,0,0.2); /* Sombra adaptada al modo oscuro */
  transition: transform 0.2s, border-color 0.2s;
}

.card-lote:hover {
  transform: translateY(-2px);
  border-color: var(--color-border-focus);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: var(--spacing-sm);
}

.lote-label {
  font-size: var(--text-xs);
  font-weight: bold;
  color: var(--color-text-dim);
  letter-spacing: 0.05em;
}

.lote-ip {
  margin: 0;
  font-size: var(--text-xl);
  font-family: var(--font-mono);
  color: var(--color-text);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.data-row {
  margin: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-md);
}

.data-row .td-muted {
  color: var(--color-text-muted);
}

.data-row .td-mono {
  font-family: var(--font-mono);
  color: var(--color-text);
}

.data-row .highlight {
  font-weight: bold;
  color: var(--color-gold);
  font-size: var(--text-lg);
}

/* ── Acciones (Botones Grandes Táctiles) ── */
.card-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: auto;
  padding-top: var(--spacing-md);
}

.flex-1 {
  flex: 1;
}

.card-actions .btn-primary,
.card-actions .btn-secondary {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--text-base);
  justify-content: center;
}
</style>
