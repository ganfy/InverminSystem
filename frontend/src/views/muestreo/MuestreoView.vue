<template>
    <div class="muestreo-page">
      <div class="page-header">
        <h1 class="page-title">Muestreo</h1>
      </div>

      <div v-if="featureControlTiemposPrueba && lotesPendientesEtiquetado.length > 0" class="sla-container">
  <h3 class="td-label-gold">CONTROL SLA: PENDIENTES DE ETIQUETADO</h3>
  <table class="sla-table">
    <thead>
      <tr>
        <th>LOTE</th>
        <th>INICIO PRUEBA</th>
        <th>TIEMPO</th>
        <th>ESTADO</th>
        <th>ACCIONES</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="lote in lotesPendientesEtiquetado" :key="lote.ip">
        <td class="td-value-mono">{{ lote.ip }}</td>
        <td>{{ formatearFecha(lote.fecha_ingreso_prueba) }}</td>
        <td class="td-value-mono">{{ Math.floor(calcularEstadoSLA(lote)?.horas ?? 0) }}h</td>
        <td>
          <span :class="['sla-badge', calcularEstadoSLA(lote)?.clase]">
            {{ calcularEstadoSLA(lote)?.texto }}
          </span>
        </td>
        <td>
          <button
            class="btn-primary"
            :disabled="!calcularEstadoSLA(lote)?.habilitado"
            @click="abrirModalEtiquetas(lote.ip)"
          >
            Etiquetar
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</div>

      <div class="tabs-container">
        <button class="tab-btn" :class="{ active: tabActual === 'PENDIENTES' }" @click="tabActual = 'PENDIENTES'">
          Pendientes <span class="tab-badge">{{ store.lotesPendientes.length }}</span>
        </button>
        <button class="tab-btn" :class="{ active: tabActual === 'COMPLETADOS' }" @click="tabActual = 'COMPLETADOS'">
          Completados <span class="tab-badge completados">{{ store.lotesCompletados.length }}</span>
        </button>
      </div>

      <div class="cards-grid">
        <div v-if="store.cargando" class="sin-datos">Cargando lotes...</div>
        <div v-else-if="lotesMostrar.length === 0" class="sin-datos">No hay lotes en esta sección.</div>

        <div v-for="lote in lotesMostrar" :key="lote.ip" class="card-lote">
          <div class="card-header">
            <div class="lote-info">
              <span class="lote-label">LOTE</span>
              <h2 class="lote-ip">{{ lote.ip }}</h2>
            </div>
            <span class="badge-estado" :class="lote.estado_muestreo === 'PENDIENTE' ? 'pendiente' : 'completo'">
              {{ lote.estado_muestreo }}
            </span>
          </div>

          <div class="card-body">
            <p class="data-row">
              <span class="td-label-gold">RECIBIDO EN:</span>
              <span class="td-value-mono">{{ formatearFecha(lote.fecha_recepcion) }}</span>
            </p>

            <p v-if="lote.fecha_muestreo || lote.estado_muestreo === 'COMPLETADO'" class="data-row">
              <span class="td-label-gold">MUESTREADO EN:</span>
              <span class="td-value-mono">{{ formatearFecha(lote.fecha_muestreo) }}</span>
            </p>

            <p class="data-row">
              <span class="td-label-gold">PESO ({{ getUnidadPorModulo('MUESTREO') }}):</span>
              <span class="td-value-mono highlight">{{ formatPesoPorModulo(lote.peso_neto, 'MUESTREO') }}</span>
            </p>
            <p class="data-row">
              <span class="td-label-gold">SACOS:</span>
              <span class="td-value-mono">{{ lote.sacos || 'A GRANEL' }}</span>
            </p>
          </div>

          <div class="card-actions">
            <template v-if="lote.estado_muestreo === 'PENDIENTE'">
              <button class="btn-primary flex-1 btn-tablet-large" @click="irARegistrarHumedad(lote.ip)">
                Registrar Humedad
              </button>
            </template>

            <template v-else>
              <div class="actions-grid">
                <button class="btn-primary flex-1 btn-con-icono" @click="abrirModalEtiquetas(lote.ip)">
                  <Plus v-if="lote.etiquetado" :size="18" />
                  <span>{{ lote.etiquetado ? 'Etiquetas Extra' : 'Etiquetar' }}</span>
                </button>

                <button v-if="!lote.etiquetado && lote.cantidad_intentos_previos < 3" class="btn-secondary flex-1" @click="irARegistrarHumedad(lote.ip)">
                  Remuestrear
                </button>

                <button class="btn-secondary flex-1" @click="abrirDetalles(lote.ip)">
                  Ver Detalles
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>

      <ModalDetallesMuestreo
        v-if="modalDetallesIp"
        :ip-lote="modalDetallesIp"
        @close="modalDetallesIp = null"
      />

      <ModalEtiquetas
      v-if="modalEtiquetasIp"
      :ip-lote="modalEtiquetasIp"
      @close="modalEtiquetasIp = null"
      @etiquetado="onEtiquetasGeneradas"
    />
    </div>
  </template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMuestreoStore } from '@/stores/muestreo'
import ModalDetallesMuestreo from './ModalDetallesMuestreo.vue'
import ModalEtiquetas from './ModalEtiquetas.vue'
import { formatPesoPorModulo, getUnidadPorModulo } from '@/utils/units'
import {
  WifiOff,
    AlertTriangle,
    Plus,
} from 'lucide-vue-next'


const router = useRouter()
const store = useMuestreoStore()

const featureControlTiemposPrueba = ref(true) // Esto debería venir de una configuración o store centralizada de features
const lotesPendientesEtiquetado = computed(() => {
    return store.lotesCompletados.filter(l => l.pendiente_sla);
});
function calcularEstadoSLA(lote: any) {
  if (!lote.fecha_ingreso_prueba) return null;

  const utcStr = (lote.fecha_ingreso_prueba.includes('+') || lote.fecha_ingreso_prueba.endsWith('Z'))
    ? lote.fecha_ingreso_prueba
    : lote.fecha_ingreso_prueba + 'Z';

  const ingreso = new Date(utcStr);
  const ahora = new Date();

  const horasTranscurridas = (ahora.getTime() - ingreso.getTime()) / (1000 * 60 * 60);

  const { h_min, h_max } = lote.sla_config || { h_min: 48, h_max: 72 };

  if (horasTranscurridas < h_min) {
    return { clase: 'sla-espera', texto: 'EN METALURGIA', habilitado: false, horas: horasTranscurridas };
  } else if (horasTranscurridas <= h_max) {
    return { clase: 'sla-plazo', texto: 'LISTO (EN PLAZO)', habilitado: true, horas: horasTranscurridas };
  } else {
    return { clase: 'sla-retraso', texto: 'RETRASADO', habilitado: true, horas: horasTranscurridas };
  }
}

const tabActual = ref<'PENDIENTES' | 'COMPLETADOS'>('PENDIENTES')

// Variable para controlar qué modal de detalles está abierto
const modalDetallesIp = ref<string | null>(null)

const lotesMostrar = computed(() => {
  return tabActual.value === 'PENDIENTES'
    ? store.lotesPendientes
    : store.lotesCompletados
})

onMounted(async () => {
  await store.cargarLotes()
})

function formatearFecha(isoString?: string | null): string {
  if (!isoString) return '---'
  const utc = (isoString.includes('+') || isoString.endsWith('Z')) ? isoString : isoString + 'Z'
  const fecha = new Date(utc)
  const fechaPart = fecha.toLocaleDateString('es-PE', { timeZone: 'America/Lima', day: '2-digit', month: '2-digit', year: 'numeric' })
  const horaPart = fecha.toLocaleTimeString('es-PE', { timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit', hour12: false })
  return `${fechaPart}, ${horaPart}`
}

function irARegistrarHumedad(ip: string) {
  router.push({ name: 'RegistrarHumedad', params: { ip } })
}

function abrirDetalles(ip: string) {
  modalDetallesIp.value = ip
}

const modalEtiquetasIp = ref<string | null>(null)

function abrirModalEtiquetas(ip: string) {
  modalEtiquetasIp.value = ip
}

async function onEtiquetasGeneradas() {
  await store.cargarLotes()
}
</script>

<style scoped>
/* Estilos base mantenidos */
.muestreo-page {
  padding: var(--page-padding);
  max-width: 1200px;
  margin: 0 auto;
}

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
  margin-bottom: -2px;
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

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); /* Un poco más ancho para las fechas */
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

.card-lote {
  min-width: 360px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  box-shadow: 0 4px 6px rgba(0,0,0,0.2);
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

.badge-estado {
  padding: 0.25rem 0.6rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: bold;
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.badge-estado.pendiente {
  background-color: var(--color-error-bg);
  color: var(--color-error);
  border: 1px solid rgba(165, 71, 61, 0.3);
}

.badge-estado.completo {
  background-color: var(--color-success-bg);
  color: var(--color-success);
  border: 1px solid rgba(81, 161, 85, 0.3);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) 0;
}

.data-row {
  margin: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-md);
}

.td-label-gold {
  color: var(--color-gold);
  font-weight: bold;
  font-family: var(--font-main);
  letter-spacing: 0.03em;
}

.td-value-mono {
  font-family: var(--font-mono);
  color: var(--color-text);
  font-weight: 600;
  text-align: right;
}

.highlight {
  color: var(--color-gold);
}

.card-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: auto;
  padding-top: var(--spacing-md);
}

.flex-1 {
  flex: 1;
}

.actions-grid {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
    width: 100%;
  }

  .actions-grid > button {
  /* Esto permite que los botones crezcan para ocupar el espacio disponible */
  flex: 1 1 calc(50% - var(--spacing-sm));
  min-width: 130px; /* Evita que queden demasiado pequeños en tablets */
  justify-content: center;
}

  .btn-tablet-large {
  padding: var(--spacing-md);
  font-size: var(--text-base);
  justify-content: center;
  font-weight: bold;
}

/* =========================================
   ESTILOS DE LA TABLA SLA
   ========================================= */
.sla-container {
  margin-bottom: var(--spacing-xl);
  background: var(--color-bg-card);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-gold-bg);
}

.sla-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: var(--spacing-md);
}

.sla-table th {
  text-align: left;
  color: var(--color-gold);
  font-size: var(--text-xs);
  padding: var(--spacing-sm);
  border-bottom: 2px solid var(--color-border);
}

.sla-table td {
  padding: var(--spacing-md) var(--spacing-sm);
  border-bottom: 1px solid var(--color-border);
}

.sla-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
}

/* Colores del Semáforo */
.sla-espera { background: var(--color-bg-input); color: var(--color-text-dim); }
.sla-plazo { background: var(--color-success-bg); color: var(--color-success); }
.sla-retraso {
  background: var(--color-error-bg);
  color: var(--color-error);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}
</style>
