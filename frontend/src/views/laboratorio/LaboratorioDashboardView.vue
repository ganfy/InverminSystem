<template>
    <div class="page-container">
      <header class="page-header">
        <div>
          <h1 class="page-title">
            <FlaskConical class="lucide" :size="24" style="margin-right: 0.5rem;" />
            Laboratorio
          </h1>
          <p class="page-subtitle">Dashboard de Muestras CIP</p>
        </div>

        <button @click="store.cargarMuestras()" class="btn-secondary" :disabled="store.cargando">
          <RefreshCw class="lucide" :class="{ 'spinner': store.cargando }" :size="18" style="margin-right: 0.5rem;" />
          ACTUALIZAR
        </button>
      </header>

      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>CÓDIGO CIP</th>
              <th>FECHA ENVÍO</th>
              <th>TIPO</th>
              <th>LEY (FIRE ASSAY)</th>
              <th>RECUPERACIÓN</th>
              <th>ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.cargando">
              <td colspan="6" class="estado-tabla">
                <span class="spinner" style="margin-right: 0.5rem;"></span> Cargando muestras...
              </td>
            </tr>

            <template v-else>
              <tr v-for="muestra in store.muestras" :key="muestra.cip">
                <td class="td-mono" style="color: var(--color-gold);">{{ muestra.cip }}</td>
                <td class="td-fecha">{{ muestra.fecha_envio }}</td>
                <td>{{ muestra.tipo_muestra }}</td>

                <td>
                  <span :class="[
                    'badge-estado',
                    muestra.estado_ley === 'COMPLETADO' ? 'badge-completo' : 'badge-pausado'
                  ]">
                    {{ muestra.estado_ley }}
                  </span>
                </td>

                <td>
                  <span :class="[
                    'badge-estado',
                    muestra.estado_recuperacion === 'COMPLETADO' ? 'badge-completo' : 'badge-pausado'
                  ]">
                    {{ muestra.estado_recuperacion }}
                  </span>
                </td>

                <td class="td-acciones">
                  <button
                    v-if="muestra.estado_ley === 'PENDIENTE'"
                    @click="irARegistro(muestra.cip, 'ley')"
                    class="btn-icon"
                    title="Ingresar Ley"
                  >
                    <ClipboardList class="lucide" :size="16" />
                  </button>

                  <button
                    v-if="muestra.estado_recuperacion === 'PENDIENTE'"
                    @click="irARegistro(muestra.cip, 'recuperacion')"
                    class="btn-icon"
                    title="Ingresar Recuperación"
                  >
                    <TestTubes class="lucide" :size="16" />
                  </button>
                </td>
              </tr>
              <tr v-if="store.muestras.length === 0">
                <td colspan="6" class="sin-datos">
                  No hay muestras generadas para laboratorio.
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { FlaskConical, RefreshCw, ClipboardList, TestTubes } from 'lucide-vue-next'

const store = useLaboratorioStore()
const router = useRouter()

onMounted(() => {
    store.cargarMuestras()
})

const irARegistro = (cip: string, tipo: string) => {
    router.push({
        name: 'LaboratorioRegistrar',
        query: { cip: cip, tipo: tipo }
    })
}
</script>
