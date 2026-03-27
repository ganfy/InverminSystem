<template>
  <div class="modal-overlay no-print" @click.self="emit('close')">
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
          <p style="margin-top: 1rem;">{{ mensajeCarga }}</p>
        </div>

        <div v-else-if="error === 'offline'" class="aviso-offline">
          <span class="aviso-icono">📡</span>
          <p class="aviso-texto">
            <strong>Sin conexión.</strong> No se pueden consultar ni generar códigos seguros en modo offline.
          </p>
        </div>

        <div v-else-if="error" class="error-msg" style="padding: 2rem;">
          {{ error }}
        </div>

        <div v-else class="etiquetas-wrapper">
          <p class="instruccion">
            Muestras generadas: <strong>{{ codigosExistentes.length }}</strong> de un máximo de {{ MAX_CIPS }}.
          </p>

          <div id="area-impresion" class="grid-etiquetas">
            <div v-for="cip in codigosExistentes" :key="cip.id" class="etiqueta-print">
              <span class="etiqueta-title">INVERMIN S.A.C.</span>
              <span class="etiqueta-subtitle">MUESTRA ANÁLISIS</span>

              <svg :id="`barcode-${cip.id}`" class="barcode-visual"></svg>

              <span class="etiqueta-codigo">{{ cip.codigo_cip }}</span>
            </div>
          </div>
        </div>
      </div>

      <footer class="modal-footer no-print">
        <button class="btn-secondary" @click="emit('close')">Cerrar</button>
        <div class="spacer"></div>

        <button
          v-if="codigosExistentes.length > 0 && codigosExistentes.length < MAX_CIPS"
          class="btn-secondary"
          :disabled="cargando"
          @click="generarExtra"
        >
          + Generar 1 Extra
        </button>

        <button
          class="btn-primary ready"
          :disabled="cargando || codigosExistentes.length === 0"
          @click="ejecutarImpresion"
        >
          Imprimir Etiquetas
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import JsBarcode from 'jsbarcode'
import { useMuestreoStore } from '@/stores/muestreo'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'
import type { MapeoCIPOut } from '@/api/muestreo'

const props = defineProps<{ ipLote: string }>()
const emit = defineEmits(['close', 'etiquetado'])

const store = useMuestreoStore()
const ui = useUiStore()
const sync = useSync()

const MAX_CIPS = 5 // Esto podría venir de un endpoint de configuración global después
const cargando = ref(true)
const mensajeCarga = ref('Consultando historial de etiquetas...')
const codigosExistentes = ref<MapeoCIPOut[]>([])
const error = ref<string | null>(null)

onMounted(async () => {
  await inicializarEtiquetas()
})

const inicializarEtiquetas = async () => {
  if (!sync.online.value) {
    error.value = 'offline'
    cargando.value = false
    return
  }

  try {
    cargando.value = true
    error.value = null

    // 1. Verificamos si ya tiene etiquetas
    let historial = await store.obtenerCodigosCip(props.ipLote)

    // 2. Lógica de negocio: Si no hay, generamos 2 automáticamente
    if (!historial || historial.length === 0) {
      mensajeCarga.value = 'Generando muestras iniciales (Laboratorio y Dirimencia)...'
      const nuevos = await store.generarCodigosCip(props.ipLote, 2)
      if (nuevos) {
        historial = nuevos
        emit('etiquetado') // Avisamos al padre que el estado cambió
      }
    }

    if (historial && historial.length > 0) {
      codigosExistentes.value = historial
      cargando.value = false
      await dibujarCodigosBarras()
    } else {
      error.value = 'No se pudieron recuperar ni generar los códigos.'
      cargando.value = false
    }

  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error interno del servidor.'
    cargando.value = false
  }
}

const generarExtra = async () => {
  if (codigosExistentes.value.length >= MAX_CIPS) return

  mensajeCarga.value = 'Generando etiqueta extra...'
  cargando.value = true

  try {
    // Generamos solo 1 extra
    const nuevos = await store.generarCodigosCip(props.ipLote, 1)
    if (nuevos && nuevos.length > 0) {
      // Como el endpoint nos devuelve SOLO el nuevo, lo agregamos a la lista
      codigosExistentes.value.push(...nuevos)
      ui.toast('Etiqueta extra generada correctamente.', 'success')
      cargando.value = false
      await dibujarCodigosBarras()
    }
  } catch (err: any) {
    ui.toast(err.response?.data?.detail || 'Error al generar etiqueta extra', 'error')
    cargando.value = false
  }
}

const dibujarCodigosBarras = async () => {
  await nextTick()
  codigosExistentes.value.forEach(cip => {
    try {
      JsBarcode(`#barcode-${cip.id}`, cip.codigo_cip, {
        format: 'CODE128',
        displayValue: false,
        width: 2,
        height: 40,
        margin: 0,
        background: "transparent",
        lineColor: "#000000"
      })
    } catch (e) {
      console.error(`Error dibujando SVG ${cip.codigo_cip}:`, e)
    }
  })
}

const ejecutarImpresion = () => {
  // Llama al sistema nativo de impresión de la tablet/navegador
  // El CSS @media print se encarga de ocultar todo menos las etiquetas
  window.print()
}

const formatearFecha = (isoDate: string | undefined | null) => {
  if (!isoDate) return new Date().toLocaleDateString('es-PE')
  return new Date(isoDate).toLocaleDateString('es-PE')
}
</script>

<style scoped>
/* ── ESTILOS DE PANTALLA (Igual que antes) ── */
.gold { color: var(--color-gold); font-family: var(--font-mono); }
.etiquetas-wrapper { display: flex; flex-direction: column; gap: var(--spacing-md); }
.instruccion { color: var(--color-text-muted); font-size: var(--text-md); text-align: center; }
.grid-etiquetas { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }

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
  page-break-inside: avoid; /* Evita que una etiqueta se corte por la mitad al imprimir */
}

.etiqueta-title { font-size: 0.65rem; font-weight: 900; letter-spacing: 0.1em; }
.etiqueta-subtitle { font-size: 0.55rem; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 0.2rem; width: 100%; text-align: center; }
.barcode-visual { transform: scaleY(1.3); margin: 0.5rem 0; }
.etiqueta-codigo { font-family: var(--font-mono); font-size: 1.1rem; font-weight: 900; letter-spacing: 0.05em; }
.etiqueta-fecha { font-size: 0.55rem; color: #444; }

@media (max-width: 560px) {
  .grid-etiquetas { grid-template-columns: 1fr; }
}
</style>

<style>
@media print {
  /* 1. Ocultamos el header, fondo, botones y resto del ERP */
  body * {
    visibility: hidden;
  }

  .no-print, .modal-header, .modal-footer, .instruccion {
    display: none !important;
  }

  /* 2. Solo hacemos visible el grid de etiquetas y sus hijos */
  #area-impresion, #area-impresion * {
    visibility: visible;
  }

  /* 3. Posicionamos las etiquetas en la esquina superior izquierda del papel */
  #area-impresion {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10mm; /* Espacio físico entre etiquetas */
  }

  /* 4. Ajustes finos para impresoras térmicas/láser */
  .etiqueta-print {
    box-shadow: none !important;
    border: 1px solid #000 !important;
    width: 80mm; /* Tamaño estándar de ticket/etiqueta ancha */
    margin: 0 auto;
    padding: 5mm;
  }
}
</style>
