<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal modal-md">
      <header class="modal-header">
        <div class="modal-title-group" style="position: relative; display: flex; align-items: center; gap: 0.5rem;">
          <h2>Etiquetado CIP: <span class="gold">{{ ipLote }}</span></h2>
          <button class="btn-icon" @click="mostrarAyuda = !mostrarAyuda" title="Ayuda sobre sufijos">
            <HelpCircle :size="18" />
          </button>
          
          <div v-if="mostrarAyuda" class="ayuda-popover">
            <h4>Sufijos de Etiquetas</h4>
            <ul>
              <li><strong>1 y 2:</strong> Laboratorio</li>
              <li><strong>3:</strong> Contramuestra</li>
              <li><strong>4:</strong> Minero</li>
              <li><strong>5:</strong> Dirimencia</li>
              <li><strong>6, 7:</strong> Remuestreo</li>
            </ul>
          </div>
        </div>
        <button class="modal-close" @click="emit('close')"><X :size="20" /></button>
      </header>

      <div class="modal-body">
        <div v-if="cargando" class="estado-tabla">
          <span class="spinner"></span>
          <p style="margin-top: 1rem;">{{ mensajeCarga }}</p>
        </div>

        <div v-else-if="error === 'offline'" class="aviso-offline">
          <span class="aviso-icono"><WifiOff :size="24" class="aviso-icono" /></span>
          <p class="aviso-texto">
            <strong>Sin conexión y sin datos en cache.</strong>
            Abre el modal una vez con red para poder etiquetar offline.
          </p>
        </div>

        <div v-else-if="error" class="error-msg" style="padding: 2rem;">
          {{ error }}
        </div>

        <div v-else class="etiquetas-wrapper">
          <!-- Banner informativo cuando los CIPs son offline -->
          <div v-if="!sync.online.value" class="aviso-offline aviso-offline--sm" style="margin-bottom:1rem">
            <WifiOff :size="14" style="vertical-align:middle;margin-right:4px" />
            <span style="font-size:0.78rem">Sin red &mdash; CIPs generados localmente. Se sincronizar&aacute;n al reconectar.</span>
          </div>
          <div class="control-impresion no-print">
            <p class="instruccion">
              Muestras generadas: <strong>{{ cantidadEtiquetasAx }}</strong> de un máximo de {{ MAX_CIPS }}.
            </p>
            <div class="formato-selector">
              <span class="formato-label">Formato de Rollo:</span>
              <div class="formato-toggle">
                <button
                  type="button"
                  class="btn-toggle"
                  :class="{ active: formatoRollo === '2col' }"
                  @click="cambiarFormato('2col')"
                >
                  2 Columnas (2"×1" Doble)
                </button>
                <button
                  type="button"
                  class="btn-toggle"
                  :class="{ active: formatoRollo === '1col' }"
                  @click="cambiarFormato('1col')"
                >
                  1 Columna (4"×2" / Simple)
                </button>
              </div>
            </div>
          </div>

          <div id="area-impresion" class="grid-etiquetas" :class="{ 'grid-etiquetas--1col': formatoRollo === '1col' }">
            <div v-for="cip in codigosExistentes" :key="cip.id" class="etiqueta-print">
              <span class="etiqueta-title">INVERMIN PAITITI S.A.C.</span>
              <span class="etiqueta-subtitle">MUESTRA ANÁLISIS</span>

              <svg :id="`barcode-${cip.id}`" class="barcode-visual"></svg>

              <span class="etiqueta-codigo">{{ cip.codigo_cip }}</span>

              <span class="etiqueta-lab" style="font-size:0.5rem;color:#555;margin-top:0.2rem">
                {{ labsPorCip[cip.id] || cip.laboratorio || '' }}
              </span>

              <div v-if="puedeAsignarLab" class="lab-selector no-print">
                <label style="font-size:0.68rem;color:var(--color-text-faint)">LABORATORIO DESTINO:</label>
                <span
                  v-if="cip.tiene_analisis_ley || cip.tiene_analisis_recuperacion"
                  style="font-size:var(--font-size-sm);color:var(--color-text-faint);font-style:italic"
                >
                {{ labsPorCip[cip.id] || cip.laboratorio }} <em>(ya tiene análisis)</em>
                </span>
                <select
                  v-else
                  class="field-select field-input"
                  style="font-size:0.75rem;padding:0.25rem 0.5rem"
                  :value="labsPorCip[cip.id] || cip.laboratorio"
                  @change="cambiarLab(cip, ($event.target as HTMLSelectElement).value)"
                >
                  <option v-for="lab in labsDisponibles" :key="lab" :value="lab">{{ lab }}</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer class="modal-footer no-print">
        <button class="btn-secondary" @click="emit('close')">Cerrar</button>
        <div class="spacer"></div>

        <button
          v-if="codigosExistentes.length > 0 && cantidadEtiquetasAx < MAX_CIPS"
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
import { ref, onMounted, nextTick, computed } from 'vue'
import JsBarcode from 'jsbarcode'
import { useMuestreoStore } from '@/stores/muestreo'
import { useUiStore } from '@/stores/ui'
import { useSync } from '@/composables/useSync'
import type { MapeoCIPOut } from '@/api/muestreo'
import { X, WifiOff, HelpCircle } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { muestreoApi } from '@/api/muestreo'
import { adminApi } from '@/api/admin'

const props = defineProps<{ ipLote: string }>()
const emit = defineEmits(['close', 'etiquetado'])

const store = useMuestreoStore()
const ui = useUiStore()
const sync = useSync()

const mostrarAyuda = ref(false)

const MAX_CIPS = ref(5)
const cargando = ref(true)
const mensajeCarga = ref('Consultando historial de etiquetas...')
const codigosExistentes = ref<MapeoCIPOut[]>([])
const error = ref<string | null>(null)

const cantidadEtiquetasAx = computed(() => {
  return codigosExistentes.value.filter(c => /-A\d+$/.test(c.codigo_cip)).length
})

type FormatoRollo = '1col' | '2col'
const formatoRollo = ref<FormatoRollo>(
  (localStorage.getItem('invermin_formato_etiquetas') as FormatoRollo) || '2col'
)
const cambiarFormato = (formato: FormatoRollo) => {
  formatoRollo.value = formato
  localStorage.setItem('invermin_formato_etiquetas', formato)
}

const auth = useAuthStore()
const puedeAsignarLab = computed(() => auth.puede('MUESTREO', 'UPDATE'))
const labsDisponibles = ref<string[]>([])
const labsPorCip = ref<Record<number, string>>({})

onMounted(async () => {
  await inicializarEtiquetas()
})

const inicializarEtiquetas = async () => {
  // ── MODO OFFLINE ──────────────────────────────────────────────────────────
  if (!sync.online.value) {
    cargando.value = true
    error.value = null
    mensajeCarga.value = 'Buscando etiquetas locales...'
    try {
      // 1. Leer CIPs ya encolados para este lote
      const { obtenerCipsPorLote } = await import('@/composables/useOfflineQueue')
      const cipsCola = await obtenerCipsPorLote(props.ipLote)

      if (cipsCola.length > 0) {
        // Ya hay CIPs locales generados → mostrarlos directamente
        codigosExistentes.value = cipsCola.map(c => ({
          id: -(c.correlativo),          // ID negativo = offline
          lote_id: c.lote_id,
          codigo_cip: c.codigo_cip,
          laboratorio: c.laboratorio,
          tipo_muestra: c.tipo_muestra,
          tiene_analisis_ley: false,
          tiene_analisis_recuperacion: false,
        } as any))
        cargando.value = false
        await dibujarCodigosBarras()
        return
      }

      // 2. No hay en cola → generar nuevos localmente
      mensajeCarga.value = 'Generando etiquetas offline...'
      const { MUESTREO_CIPS_IMPRIMIR } = { MUESTREO_CIPS_IMPRIMIR: '3' }  // default sin servidor
      const cantidadAImprimir = parseInt(MUESTREO_CIPS_IMPRIMIR, 10) || 3

      const nuevos = await store.generarCodigosCip(props.ipLote, cantidadAImprimir)
      if (nuevos && nuevos.length > 0) {
        codigosExistentes.value = nuevos
        emit('etiquetado')
        cargando.value = false
        await dibujarCodigosBarras()
      } else {
        // Lote no está en cache — bloqueo justo
        error.value = 'offline'
        cargando.value = false
      }
    } catch (e: any) {
      error.value = 'offline'
      cargando.value = false
    }
    return
  }

  // ── MODO ONLINE ───────────────────────────────────────────────────────────
  try {
  cargando.value = true
  error.value = null

  const [labs, historialInicial] = await Promise.all([
    puedeAsignarLab.value ? muestreoApi.listarLaboratorios() : Promise.resolve([]),
    store.obtenerCodigosCip(props.ipLote),
  ])

  if (puedeAsignarLab.value) labsDisponibles.value = labs

  let historial = historialInicial

  let cantidadAImprimir = 3; // Default
  try {
    const config = await adminApi.getPublicConfig()
    if (config['MUESTREO_CIPS_IMPRIMIR']) {
      cantidadAImprimir = parseInt(config['MUESTREO_CIPS_IMPRIMIR'], 10) || 3
    }
    if (config['MAX_CIPS_GENERADOS']) {
      MAX_CIPS.value = parseInt(config['MAX_CIPS_GENERADOS'], 10) || 5
    }
  } catch (e) {
    console.error('No se pudo cargar config de impresión', e)
  }

  if (!historial || historial.length === 0) {
    mensajeCarga.value = 'Generando muestras iniciales...'
    const nuevos = await store.generarCodigosCip(props.ipLote, cantidadAImprimir)
    if (nuevos) {
      historial = nuevos
      emit('etiquetado')
    }
  }

  if (historial && historial.length > 0) {
    codigosExistentes.value = historial
    // Precargar lab por CIP DESPUÉS de tener los datos
    if (puedeAsignarLab.value) {
      historial.forEach(c => {
        labsPorCip.value[c.id] = c.laboratorio ?? ''
      })
    }
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
  if (cantidadEtiquetasAx.value >= MAX_CIPS.value) return

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
        height: 55,
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
  // 1. Capturamos el HTML generado de las etiquetas (con los SVGs ya dibujados)
  const areaImpresion = document.getElementById('area-impresion');
  if (!areaImpresion) return;
  const contenidoHtml = areaImpresion.innerHTML;

  const esDobleColumna = formatoRollo.value === '2col';

  // 2. Definimos el CSS exclusivo para esta nueva pestaña de impresión
  const printCss = `
    @page { size: ${esDobleColumna ? '4in 1in' : 'auto'}; margin: 0mm; }
    body { font-family: sans-serif; margin: 0; padding: 0; background: white; color: black; }
    #area-impresion {
      display: flex;
      flex-wrap: ${esDobleColumna ? 'wrap' : 'nowrap'};
      flex-direction: ${esDobleColumna ? 'row' : 'column'};
      width: 100%;
    }
    .etiqueta-print {
      width: ${esDobleColumna ? '50%' : '100%'};
      max-width: ${esDobleColumna ? '50%' : '100%'};
      height: ${esDobleColumna ? '24.5mm' : 'auto'};
      max-height: ${esDobleColumna ? '24.5mm' : 'none'};
      overflow: hidden;
      box-sizing: border-box;
      padding: ${esDobleColumna ? '1mm 1mm' : '3mm 2mm'};
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      page-break-inside: avoid;
      break-inside: avoid;
    }
    ${esDobleColumna ? `
    .etiqueta-print:nth-child(2n):not(:last-child) {
      page-break-after: always;
      break-after: page;
    }
    ` : `
    .etiqueta-print:not(:last-child) {
      page-break-after: always;
      break-after: page;
    }
    `}
    .etiqueta-title { font-size: ${esDobleColumna ? '0.5rem' : '0.7rem'}; font-weight: 900; letter-spacing: 0.05em; margin: 0; line-height: 1.15; }
    .etiqueta-subtitle { font-size: ${esDobleColumna ? '0.42rem' : '0.6rem'}; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 1px; width: 100%; text-align: center; margin: 1px 0; line-height: 1.15; }
    .barcode-visual { width: 95%; max-width: 100%; height: ${esDobleColumna ? '26px' : '50px'}; margin: 1px 0; }
    .no-print { display: none !important; }
    .etiqueta-codigo { font-family: monospace; font-size: ${esDobleColumna ? '0.85rem' : '1.2rem'}; font-weight: 900; letter-spacing: 0.03em; margin: 1px 0 0 0; line-height: 1.15; }
    .etiqueta-lab { font-size: ${esDobleColumna ? '0.4rem' : '0.5rem'}; color: #555; margin: 0; line-height: 1.15; }
    @media print {
      .etiqueta-print { border: none !important; border-radius: 0; box-shadow: none !important; }
    }
  `;

  // 3. Construimos el documento HTML limpio (Igual que en balanza.ts)
  const htmlDocument = `
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>Impresión de Etiquetas CIP</title>
      <style>${printCss}</style>
    </head>
    <body>
      <div id="area-impresion">
        ${contenidoHtml}
      </div>
      <script>
        window.addEventListener('load', function() {
          setTimeout(function() { window.print(); }, 250);
        });
      <\/script>
    <\/body>
    <\/html>
  `;

  // 4. Abrimos en una nueva pestaña usando un Blob (Estrategia Balanza)
  const blob = new Blob([htmlDocument], { type: 'text/html; charset=utf-8' });
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank');
  setTimeout(() => URL.revokeObjectURL(url), 120000);
}

const formatearFecha = (isoDate: string | undefined | null) => {
  if (!isoDate) return new Date().toLocaleDateString('es-PE')
  return new Date(isoDate).toLocaleDateString('es-PE')
}

async function cambiarLab(cip: MapeoCIPOut, lab: string) {
  try {
    await muestreoApi.actualizarLaboratorioCip(cip.id, lab)
    labsPorCip.value[cip.id] = lab
    ui.toast(`Lab asignado: ${lab}`, 'success')
  } catch {
    ui.toast('Error al asignar laboratorio', 'error')
  }
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

.etiqueta-container {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.lab-selector {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.control-impresion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.5rem;
}
.formato-selector {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.4rem 0.8rem;
  background: var(--color-background-soft, rgba(255, 255, 255, 0.04));
  border: 1px solid var(--color-border, rgba(255, 255, 255, 0.08));
  border-radius: 8px;
}
.formato-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  font-weight: 600;
}
.formato-toggle {
  display: inline-flex;
  background: var(--color-background-mute, rgba(0, 0, 0, 0.35));
  border: 1px solid var(--color-border, rgba(255, 255, 255, 0.1));
  border-radius: 6px;
  padding: 2px;
}
.btn-toggle {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-toggle:hover {
  color: var(--color-text);
}
.btn-toggle.active {
  background: var(--color-gold, #d4af37);
  color: #000;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}
.grid-etiquetas--1col {
  grid-template-columns: 1fr;
  max-width: 340px;
  margin: 0 auto;
  width: 100%;
}

.btn-icon {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  transition: color 0.2s;
}
.btn-icon:hover {
  color: var(--color-gold);
}
.ayuda-popover {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: var(--color-background-soft, #1e1e1e);
  border: 1px solid var(--color-border, rgba(255, 255, 255, 0.1));
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  z-index: 100;
  width: max-content;
  text-align: left;
}
.ayuda-popover h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-gold);
  font-size: 0.9rem;
}
.ayuda-popover ul {
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.8rem;
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.ayuda-popover li strong {
  color: var(--color-text-bright, #fff);
}

@media print { .no-print { display: none !important; } }
</style>
