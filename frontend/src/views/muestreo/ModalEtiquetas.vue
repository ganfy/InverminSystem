<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal modal-md">
      <header class="modal-header">
        <div class="modal-title-group">
          <h2>Etiquetado CIP: <span class="gold">{{ ipLote }}</span></h2>
        </div>
        <button class="modal-close" @click="emit('close')">✕</button>
      </header>

      <div class="modal-body">

        <div v-if="cargando" class="estado-tabla">
          <span class="spinner"></span>
          <p style="margin-top: 1rem;">Generando códigos de muestra ciego seguros...</p>
        </div>

        <div v-else-if="error === 'offline'" class="aviso-offline">
          <span class="aviso-icono">📡</span>
          <p class="aviso-texto">
            <strong>Sin conexión al servidor.</strong> No se pueden generar códigos de barras seguros (CIP) en modo offline. Conéctese a la red de la planta para etiquetar este lote.
          </p>
        </div>

        <div v-else-if="error" class="error-msg" style="padding: 2rem;">
          {{ error }}
        </div>

        <div v-else class="etiquetas-container">
          <p class="instruccion">Se han generado las siguientes muestras para laboratorio:</p>

          <div class="grid-etiquetas">
            <div v-for="cip in codigosGenerados" :key="cip.id" class="etiqueta-print">
              <span class="etiqueta-title">INVERMIN S.A.C.</span>
              <span class="etiqueta-subtitle">MUESTRA CONFIDENCIAL</span>

              <div class="barcode-visual">
                ||| ||||| || |||| |||
              </div>

              <span class="etiqueta-codigo">{{ cip.codigo_cip }}</span>
              <span class="etiqueta-fecha">{{ new Date().toLocaleDateString('es-PE') }}</span>
            </div>
          </div>
        </div>

      </div>

      <footer class="modal-footer">
        <button class="btn-secondary" @click="emit('close')">Cancelar</button>
        <div class="spacer"></div>
        <button
          class="btn-primary ready"
          :disabled="cargando || codigosGenerados.length === 0"
          @click="imprimir"
        >
          🖨️ Imprimir y Finalizar
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMuestreoStore } from '@/stores/muestreo'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'
import type { MapeoCIPOut } from '@/api/muestreo'

const props = defineProps<{ ipLote: string }>()
const emit = defineEmits(['close', 'etiquetado'])

const store = useMuestreoStore()
const ui = useUiStore()
const sync = useSync()

const cargando = ref(true)
const codigosGenerados = ref<MapeoCIPOut[]>([])
const error = ref<string | null>(null)

onMounted(async () => {
  // 1. Validar conexión (Los CIPs nacen en el servidor por seguridad)
  if (!sync.online.value) {
    error.value = 'offline'
    cargando.value = false
    return
  }

  // 2. Generar códigos (Por defecto 2 bolsas de laboratorio)
  try {
    const resultados = await store.generarCodigosCip(props.ipLote, 2)
    if (resultados && resultados.length > 0) {
      codigosGenerados.value = resultados
    } else {
      error.value = 'No se pudieron generar los códigos. Intente nuevamente.'
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error interno al generar etiquetas.'
  } finally {
    cargando.value = false
  }
})

const imprimir = async () => {
  ui.toast('Imprimiendo etiquetas...', 'success')

  await store.cargarLotes()

  // Emitimos el evento y cerramos
  emit('etiquetado')
  emit('close')
}
</script>

<style scoped>
.gold {
  color: var(--color-gold);
  font-family: var(--font-mono);
}

.etiquetas-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.instruccion {
  color: var(--color-text-muted);
  font-size: var(--text-md);
  margin-bottom: var(--spacing-sm);
  text-align: center;
}

.grid-etiquetas {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

/* ── DISEÑO DE LA ETIQUETA FÍSICA ── */
/* Forzamos fondo blanco y texto negro puro para legibilidad láser */
.etiqueta-print {
  background-color: #ffffff;
  color: #000000;
  border-radius: 4px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  border: 1px dashed #ccc;
}

.etiqueta-title {
  font-size: 0.65rem;
  font-weight: 900;
  letter-spacing: 0.1em;
}

.etiqueta-subtitle {
  font-size: 0.55rem;
  font-weight: bold;
  border-bottom: 1px solid #000;
  padding-bottom: 0.2rem;
  width: 100%;
  text-align: center;
  margin-bottom: 0.2rem;
}

.barcode-visual {
  font-family: 'Courier New', Courier, monospace;
  font-size: 2.2rem;
  font-weight: normal;
  letter-spacing: 2px;
  transform: scaleY(1.5); /* Estira las barras hacia arriba */
  margin: 0.5rem 0;
  opacity: 0.8;
}

.etiqueta-codigo {
  font-family: var(--font-mono);
  font-size: 1.1rem;
  font-weight: 900;
  letter-spacing: 0.05em;
}

.etiqueta-fecha {
  font-size: 0.55rem;
  color: #444;
  margin-top: 0.2rem;
}

@media (max-width: 560px) {
  .grid-etiquetas {
    grid-template-columns: 1fr; /* Apilar en móviles pequeños */
  }
}
</style>
