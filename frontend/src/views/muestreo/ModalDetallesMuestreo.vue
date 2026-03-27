<template>
    <div class="modal-overlay" @click.self="emit('close')">
      <div class="modal modal-md">
        <header class="modal-header">
          <div class="modal-title-group">
            <h2>Detalles de Muestreo: <span class="gold">{{ ipLote }}</span></h2>
          </div>
          <button class="modal-close" @click="emit('close')">✕</button>
        </header>

        <div class="modal-body">
          <div v-if="cargando" class="estado-tabla">Cargando historial...</div>

          <div v-else-if="errorRed" class="aviso-offline">
            <span class="aviso-icono">⚠️</span>
            <p class="aviso-texto">
              <strong>Sin conexión.</strong> No se puede consultar el historial detallado de intentos mientras el dispositivo esté fuera de línea.
            </p>
          </div>

          <div v-else-if="historial.length === 0" class="estado-tabla">
            Este lote aún no tiene intentos registrados.
          </div>

          <div v-else class="tabla-wrapper">
            <table class="tabla">
              <thead>
                <tr>
                  <th>INTENTO</th>
                  <th>REGISTRO</th>
                  <th>P. HÚMEDO</th>
                  <th>P. SECO</th>
                  <th>% HUMEDAD</th>
                  <th>OBSERVACIONES</th> </tr>
              </thead>
              <tbody>
                <tr v-for="item in historial" :key="item.id">
                  <td class="td-mono">#{{ item.intento }}</td>
                  <td class="td-fecha">{{ formatearFecha(item.creado_en) }}</td>
                  <td class="td-mono">{{ item.peso_humedo }}g</td>
                  <td class="td-mono">{{ item.peso_seco }}g</td>
                  <td class="td-mono highlight-gold">
                    {{ item.porcentaje_humedad }}%
                  </td>
                  <td class="td-obs" :title="item.observaciones || ''">
                    {{ item.observaciones || '---' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <footer class="modal-footer">
          <button class="btn-secondary" @click="emit('close')">Cerrar</button>
        </footer>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api/axios'
import type { MuestreoOut } from '@/api/muestreo'
import { useSync } from '@/composables/useSync'

const props = defineProps<{ ipLote: string }>()
const emit = defineEmits(['close'])
const sync = useSync()

const cargando = ref(true)
const historial = ref<MuestreoOut[]>([])
const errorRed = ref(false)

onMounted(async () => {
  if (!sync.online.value) {
    errorRed.value = true
    cargando.value = false
    return
  }

  try {
    const response = await api.get<MuestreoOut[]>(`/muestreo/lotes/${props.ipLote}/muestreos`)
    historial.value = response.data
  } catch (error) {
    console.error('Error al cargar historial', error)
  } finally {
    cargando.value = false
  }

})

function formatearFecha(iso: string) {
  if (!iso) return '---'
  const d = new Date(iso)
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' }) + ' ' +
         d.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit', hour12: false })
}
</script>

<style scoped>
.gold {
  color: var(--color-gold);
  font-family: var(--font-mono);
}

.highlight-gold {
  color: var(--color-gold);
  font-weight: bold;
}

.td-obs {
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: var(--text-sm);
  color: var(--color-text-dim);
}
</style>
