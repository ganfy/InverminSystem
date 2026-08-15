<template>
    <div class="modal-overlay" @click.self="emit('close')">
      <div class="modal modal-md">
        <header class="modal-header">
          <div class="modal-title-group">
            <h2>Detalles de Muestreo: <span class="gold">{{ ipLote }}</span></h2>
          </div>
          <button class="modal-close" @click="emit('close')"><X :size="18" /></button>
        </header>

        <div class="modal-body">
          <div v-if="cargando" class="estado-tabla">Cargando historial...</div>

          <div v-else-if="errorRed" class="aviso-offline">
            <span class="aviso-icono"><AlertTriangle :size="20" class="aviso-icono" /></span>
            <p class="aviso-texto">
              <strong>Sin conexión.</strong> No se puede consultar o editar el historial detallado de intentos mientras el dispositivo esté fuera de línea.
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
                  <th>OBSERVACIONES</th>
                  <th>ACCIONES</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in historial" :key="item.id">
                  <td class="td-mono">#{{ item.intento }}</td>
                  <td class="td-fecha">{{ formatearFecha(item.creado_en) }}</td>
                  
                  <template v-if="editandoId === item.id">
                    <td>
                      <input type="number" v-model.number="formEdit.peso_humedo" class="pinput" step="1" style="width: 70px; padding: 0.2rem;" />
                    </td>
                    <td>
                      <input type="number" v-model.number="formEdit.peso_seco" class="pinput" step="1" style="width: 70px; padding: 0.2rem;" />
                    </td>
                    <td class="td-mono highlight-gold">
                      --
                    </td>
                    <td>
                      <input type="text" v-model="formEdit.observaciones" class="pinput" style="width: 120px; padding: 0.2rem;" />
                    </td>
                    <td>
                      <div class="acciones-edit">
                        <button class="btn-icon" @click="guardarEdicion" title="Guardar" :disabled="guardando">
                          <Check :size="16" />
                        </button>
                        <button class="btn-icon btn-icon-danger" @click="cancelarEdicion" title="Cancelar" :disabled="guardando">
                          <X :size="16" />
                        </button>
                      </div>
                    </td>
                  </template>

                  <template v-else>
                    <td class="td-mono">{{ Math.round(item.peso_humedo) }}g</td>
                    <td class="td-mono">{{ Math.round(item.peso_seco) }}g</td>
                    <td class="td-mono highlight-gold">
                      {{ item.porcentaje_humedad }}%
                    </td>
                    <td class="td-obs" :title="item.observaciones || ''">
                      {{ item.observaciones || '---' }}
                    </td>
                    <td>
                      <button 
                        v-if="esEditable(item.creado_en)"
                        class="btn-icon"
                        @click="iniciarEdicion(item)"
                        title="Editar">
                        <Edit2 :size="16" />
                      </button>
                      <span v-else class="td-obs" title="Expiró el tiempo de edición o el lote fue liquidado">---</span>
                    </td>
                  </template>
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
import { muestreoApi, type MuestreoOut } from '@/api/muestreo'
import { useSync } from '@/composables/useSync'
import {
  AlertTriangle,
  X,
  Edit2,
  Check
} from 'lucide-vue-next'

const props = defineProps<{ ipLote: string }>()
const emit = defineEmits(['close'])
const sync = useSync()

const cargando = ref(true)
const historial = ref<MuestreoOut[]>([])
const errorRed = ref(false)

const editandoId = ref<number | null>(null)
const guardando = ref(false)
const formEdit = ref({
  peso_humedo: 0,
  peso_seco: 0,
  observaciones: '' as string | null
})

onMounted(async () => {
  if (!sync.online.value) {
    errorRed.value = true
    cargando.value = false
    return
  }

  await cargarHistorial()
})

async function cargarHistorial() {
  cargando.value = true
  try {
    const data = await muestreoApi.listarMuestreosPorLote(props.ipLote)
    historial.value = data
  } catch (error) {
    console.error('Error al cargar historial', error)
  } finally {
    cargando.value = false
  }
}

function esEditable(creado_en: string) {
  const diff = new Date().getTime() - new Date(creado_en).getTime()
  return diff < 60 * 60 * 1000 // 1 hour
}

function iniciarEdicion(item: MuestreoOut) {
  editandoId.value = item.id
  formEdit.value = {
    peso_humedo: item.peso_humedo,
    peso_seco: item.peso_seco,
    observaciones: item.observaciones || ''
  }
}

function cancelarEdicion() {
  editandoId.value = null
}

async function guardarEdicion() {
  if (!editandoId.value) return
  
  if (formEdit.value.peso_seco >= formEdit.value.peso_humedo) {
    alert("El peso seco debe ser menor al peso húmedo")
    return
  }

  guardando.value = true
  try {
    await muestreoApi.actualizarMuestreo(editandoId.value, {
      peso_humedo: formEdit.value.peso_humedo,
      peso_seco: formEdit.value.peso_seco,
      observaciones: formEdit.value.observaciones
    })
    editandoId.value = null
    await cargarHistorial()
  } catch (error: any) {
    console.error('Error al editar muestreo', error)
    alert(error.response?.data?.detail || "Error al actualizar el muestreo.")
  } finally {
    guardando.value = false
  }
}

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
