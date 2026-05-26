<template>
    <div class="page-container">
      <header class="page-header">
        <div>
          <h1 class="page-title">Configuración de Cálculo</h1>
          <p class="page-subtitle">Constantes metalúrgicas usadas en los cálculos de ley y recuperación</p>
        </div>
      </header>

      <div v-if="cargando" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando…
      </div>

      <div v-else class="config-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>PARÁMETRO</th>
              <th>DESCRIPCIÓN</th>
              <th class="align-right">VALOR DEFAULT</th>
              <th class="align-right" style="width:180px">VALOR ACTUAL</th>
              <th style="width:120px"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in constantes" :key="c.clave">
              <td>
                <code class="code-badge">{{ c.clave }}</code>
                <span v-if="!c.en_bd" class="badge-default">default</span>
              </td>
              <td class="text-muted">{{ c.descripcion }}</td>
              <td class="align-right text-muted">{{ c.default }}</td>
              <td class="align-right">
                <input
                  v-model="edits[c.clave]"
                  type="text"
                  class="field-input input-valor"
                  :class="{ modified: edits[c.clave] !== c.valor }"
                />
              </td>
              <td class="align-center">
                <button
                  class="btn-save"
                  :disabled="guardando[c.clave] || edits[c.clave] === c.valor"
                  @click="guardar(c.clave)"
                >
                  <span v-if="guardando[c.clave]" class="spinner" />
                  <span v-else>Guardar</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p class="nota-info">
          ⚠ Estos valores afectan los cálculos de ley y liquidación para todos los lotes nuevos.
          Los lotes ya liquidados no se recalculan.
          Solo Admin puede modificar estos valores.
        </p>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminApi, type ConstanteCalculo } from '@/api/admin'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

const cargando   = ref(true)
const constantes = ref<ConstanteCalculo[]>([])
const edits      = reactive<Record<string, string>>({})
const guardando  = reactive<Record<string, boolean>>({})

async function cargar() {
cargando.value = true
try {
    constantes.value = await adminApi.getConstantesCalculo()
    for (const c of constantes.value) {
    edits[c.clave] = c.valor
    }
} catch {
    ui.toast('Error al cargar constantes', 'error')
} finally {
    cargando.value = false
}
}

async function guardar(clave: string) {
const valor = edits[clave]?.trim()
if (!valor) return

const ok = await ui.showConfirm({
    title: 'Actualizar constante',
    message: `¿Cambiar "${clave}" a ${valor}? Esto afecta futuros cálculos de ley.`,
    confirmLabel: 'Actualizar',
})
if (!ok) return

guardando[clave] = true
try {
    await adminApi.updateConstante(clave, valor)
    ui.toast(`"${clave}" actualizado correctamente`, 'success')
    await cargar()
} catch {
    ui.toast('Error al guardar el valor', 'error')
} finally {
    guardando[clave] = false
}
}

onMounted(cargar)
</script>

<style scoped>
.page-subtitle {
color: var(--color-text-muted);
font-family: var(--font-mono);
font-size: var(--text-sm);
margin-top: 0.25rem;
}

.config-table-wrapper {
background: var(--color-surface);
border: 1px solid var(--color-border);
border-radius: 4px;
overflow: hidden;
}

.input-valor {
width: 130px;
text-align: right;
font-family: var(--font-mono);
}

.input-valor.modified {
border-color: var(--color-gold);
box-shadow: 0 0 0 2px rgba(201, 162, 39, 0.2);
}

.code-badge {
font-family: var(--font-mono);
font-size: var(--text-sm);
background: rgba(201, 162, 39, 0.1);
color: var(--color-gold);
padding: 0.1rem 0.4rem;
border-radius: 3px;
margin-right: 0.4rem;
}

.badge-default {
font-family: var(--font-mono);
font-size: 0.65rem;
background: rgba(148, 163, 184, 0.15);
color: var(--color-text-muted);
padding: 0.1rem 0.35rem;
border-radius: 3px;
vertical-align: middle;
}

.btn-save {
padding: 0.3rem 0.8rem;
font-family: var(--font-mono);
font-size: var(--text-sm);
font-weight: 600;
border: none;
border-radius: 3px;
background: var(--color-gold);
color: #1a1a14;
cursor: pointer;
transition: background 0.15s;
min-width: 80px;
}
.btn-save:hover:not(:disabled) { background: var(--color-gold-light); }
.btn-save:disabled {
opacity: 0.4;
cursor: not-allowed;
}

.text-muted {
color: var(--color-text-muted);
}

.nota-info {
font-family: var(--font-mono);
font-size: var(--text-sm);
color: var(--color-text-muted);
padding: 1rem 1.25rem;
border-top: 1px solid var(--color-border);
margin: 0;
line-height: 1.6;
}
</style>
