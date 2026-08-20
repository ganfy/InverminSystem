<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">
          <FlaskConical class="lucide" :size="24" style="margin-right:0.5rem" />
          Laboratorio
        </h1>
        <p class="page-subtitle">
          {{ store.puedeVerIP ? 'Gestión de Lotes y Leyes' : (tabActual === 'ley' ? 'Análisis de Ley' : 'Análisis de Recuperación') }}
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="recargar" :disabled="store.cargando || cargandoLotes">
          <RefreshCw :size="16" :class="{ spinner: store.cargando || cargandoLotes }" style="margin-right:0.4rem" />
          ACTUALIZAR
        </button>
      </div>
    </header>

    <AlertasBanner modulo="LABORATORIO" con-observaciones />

    <!-- ── [OFFLINE] Análisis pendientes de sincronizar (solo Laboratorista) ── -->
    <div
      v-if="!store.puedeVerIP && analisisOfflinePendientes.length > 0"
      class="offline-section"
    >
      <div class="offline-section-header">
        <span class="offline-section-titulo">
          <WifiOff :size="16" style="margin-right:0.4rem;vertical-align:middle" />
          SIN SINCRONIZAR
        </span>
        <span class="offline-section-count">
          {{ analisisOfflinePendientes.length }} análisis local(es)
        </span>
      </div>
      <div style="padding:0.75rem 1rem">
        <div
          v-for="item in analisisOfflinePendientes"
          :key="item.offline_id"
          class="pendiente-item"
        >
          <span class="pendiente-cip">{{ item.datos.cip }}</span>
          <span class="pendiente-tipo">Análisis de ley · {{ item.datos.tipo_analisis }}</span>
          <span v-if="item.error" class="pendiente-error" :title="item.error">
            <AlertTriangle :size="12" style="vertical-align:middle;margin-right:2px" />
            Error sync
          </span>
          <span v-else class="badge-local">LOCAL</span>
        </div>
      </div>
    </div>

    <template v-if="store.puedeVerIP">
      <div class="filtros-bar">
        <div class="field" style="min-width:180px">
          <label class="field-label">MATERIAL</label>
          <select class="field-select field-sm field-input" v-model="filtroMaterialLotes">
            <option value="">Todos los materiales</option>
            <option value="Mineral">Mineral</option>
            <option value="Llampo">Llampo</option>
            <option value="M.Llampo">M. Llampo</option>
            <option value="Au">Au</option>
            <option value="Ag">Ag</option>
          </select>
        </div>
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <input type="text" class="field-input" v-model="filtroBusquedaLotes" placeholder="IP, CIP, Proveedor o Material" />
        </div>
      </div>

      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>IP</th>
              <th>PROVEEDOR</th>
              <th>MATERIAL</th>
              <th>FECHA RECEPCIÓN</th>
              <th>LEY PLANTA</th>
              <th>LEY MINERO</th>
              <th>% RECUP</th>
              <th>ESTADO LEYES</th>
              <th>ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="cargandoLotes">
              <td colspan="8" class="estado-tabla">
                <span class="spinner" style="margin-right:0.5rem"></span> Cargando lotes...
              </td>
            </tr>
            <template v-else>
              <tr v-if="lotesFiltrados.length === 0">
                <td colspan="9" class="estado-tabla sin-datos">Sin registros</td>
              </tr>
              <tr v-for="lote in lotesFiltrados" :key="lote.ip">
                <td class="td-mono" style="color:var(--color-gold)">{{ lote.ip }}</td>
                <td>{{ lote.proveedor }}</td>
                <td>{{ lote.material || '-' }}</td>
                <td class="td-fecha">{{ fmt(lote.fecha_recepcion) }}</td>
                <td class="td-mono">{{ lote.ley_planta ?? '-' }}</td>
                <td class="td-mono">{{ lote.ley_minero ?? '-' }}</td>
                <td class="td-mono" style="color:var(--color-gold-light)">{{ getRecuperacion(lote) }}</td>
                <td>
                  <span class="badge-estado">{{ lote.analisis_ley.length }} análisis</span>
                </td>
                <td class="td-acciones">
                  <button class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irADetalleLote(lote.ip)">
                    Gestionar Leyes
                  </button>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </template>

    <template v-else>
      <div class="tabs-lab">
        <button class="tab-lab-btn" :class="{ active: tabActual === 'ley' }" @click="tabActual = 'ley'">
          Newmont
          <span v-if="pendientesLey > 0" class="badge-count">{{ pendientesLey }}</span>
          <ChevronUp v-if="tabActual === 'ley'" :size="14" class="tab-chevron" />
          <ChevronDown v-else :size="14" class="tab-chevron" />
        </button>
        <button class="tab-lab-btn" :class="{ active: tabActual === 'solidos' }" @click="tabActual = 'solidos'">
          Sólidos
          <span v-if="pendientesSolidos > 0" class="badge-count">{{ pendientesSolidos }}</span>
          <ChevronUp v-if="tabActual === 'solidos'" :size="14" class="tab-chevron" />
          <ChevronDown v-else :size="14" class="tab-chevron" />
        </button>
        <button class="tab-lab-btn" :class="{ active: tabActual === 'solucion' }" @click="tabActual = 'solucion'">
          Absorción Atómica
          <span v-if="pendientesSolucion > 0" class="badge-count">{{ pendientesSolucion }}</span>
          <ChevronUp v-if="tabActual === 'solucion'" :size="14" class="tab-chevron" />
          <ChevronDown v-else :size="14" class="tab-chevron" />
        </button>
      </div>

      <div class="filtros-bar">
        <div class="field" style="min-width:180px">
          <label class="field-label">ESTADO</label>
          <select class="field-select field-sm field-input" v-model="filtroEstado">
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="COMPLETADO">Completado</option>
          </select>
        </div>
        <div class="field" style="display:flex;align-items:center;">
          <label style="color:var(--color-text); font-size:var(--text-sm); display:flex; align-items:center; gap:0.5rem; cursor:pointer; margin-top:1rem;">
            <input type="checkbox" v-model="mostrarSoloCIPs" />
            Mostrar solo CIPs
          </label>
        </div>
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <input type="text" class="field-input" v-model="filtroBusqueda" placeholder="CIP" />
        </div>
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
        <div>
          <template v-if="tabActual === 'ley'">
            <button class="btn-secondary" style="font-size:0.8rem;padding:0.4rem 0.8rem" @click="irARegistrarLey('_nuevo')">
              + Nuevo Análisis de Ley (Blanco)
            </button>
          </template>
          <template v-else-if="tabActual === 'solidos'">
            <button class="btn-secondary" style="font-size:0.8rem;padding:0.4rem 0.8rem" @click="irANuevoReconocimiento('solidos')">
              + Nuevo Reconocimiento (Sólidos)
            </button>
          </template>
          <template v-else-if="tabActual === 'solucion'">
            <button class="btn-secondary" style="font-size:0.8rem;padding:0.4rem 0.8rem" @click="irANuevoReconocimiento('solucion')">
              + Nuevo Reconocimiento (Solución)
            </button>
          </template>
        </div>

        <button
          class="btn-primary"
          :disabled="cipsSeleccionados.length === 0 || generandoConjunto"
          @click="generarCertificadoConjunto"
        >
          <span v-if="generandoConjunto" class="spinner" style="margin-right:0.4rem"></span>
          Generar Certificado en Conjunto ({{ cipsSeleccionados.length }})
        </button>
      </div>

      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <template v-if="tabActual === 'ley'">
                <th style="width:40px;text-align:center">
                  <input type="checkbox" :checked="todosSeleccionados" @change="toggleTodosSeleccionados" />
                </th>
                <th>CIP</th>
                <th>FECHA ENVÍO</th>
                <th>MALLA +140</th>
                <th>MALLA -140</th>
                <th>AU OZ/TC</th>
                <th>AU GR/TM</th>
                <th>ESTADO</th>
                <th></th>
              </template>
              <template v-else-if="tabActual === 'solidos'">
                <th style="width:36px;text-align:center">
                  <input type="checkbox" :checked="todosSeleccionados" @change="toggleTodosSeleccionados" />
                </th>
                <th>CIP</th>
                <th>FECHA ENVÍO</th>
                <th>TIPO</th>
                <th>LEY AU</th>
                <th>LEY AG</th>
                <th>ESTADO</th>
                <th>ACCIONES</th>
              </template>
              <template v-else-if="tabActual === 'solucion'">
                <th style="width:36px;text-align:center">
                  <input type="checkbox" :checked="todosSeleccionados" @change="toggleTodosSeleccionados" />
                </th>
                <th>CIP</th>
                <th>FECHA ENVÍO</th>
                <th>TIPO</th>
                <th>LEY LÍQ. (Au)</th>
                <th>LEY LÍQ. (Ag)</th>
                <th>ESTADO</th>
                <th>ACCIONES</th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.cargando">
              <td :colspan="tabActual === 'ley' ? 9 : 8" class="estado-tabla">
                <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
              </td>
            </tr>
            <template v-else>
              <tr v-if="filasMostrar.length === 0">
                <td :colspan="tabActual === 'ley' ? 9 : 7" class="estado-tabla sin-datos">Sin registros</td>
              </tr>

              <template v-if="tabActual === 'ley'">
                <tr v-for="fila in filasMostrar" :key="fila.cip">
                  <td style="text-align:center">
                    <input type="checkbox" :value="fila.cip" v-model="cipsSeleccionados" />
                  </td>
                  <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                  <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                  <td>{{ fila.leyMas ?? '-' }}</td>
                  <td>{{ fila.leyMenos ?? '-' }}</td>
                  <td class="td-mono" style="color:var(--color-gold-light)">{{ fila.ozTc ?? '-' }}</td>
                  <td class="td-mono">{{ fila.grTm ?? '-' }}</td>
                  <td>
                    <span class="badge-estado" :class="badgeClass(fila.estado)">{{ fila.estado }}</span>
                  </td>
                  <td class="td-acciones">
                    <button v-if="fila.estado === 'PENDIENTE'" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irARegistrarLey(fila.cip)">Registrar</button>
                    <button v-if="fila.estado === 'COMPLETADO' && !fila.certificadoUrl" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="generarCertLey(fila)">Generar cert.</button>
                    <button v-if="fila.certificadoUrl" class="btn-secondary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="verCertificado(fila.certificadoUrl)">Ver cert.</button>
                    <button v-if="fila.certificadoUrl" class="btn-secondary" style="font-size:0.75rem;padding:0.3rem 0.75rem;opacity:0.7" @click="generarCertLey(fila)" title="Regenerar certificado (e.g. tras agregar ley Ag)">↺ Regen.</button>
                    <button
                      v-if="fila.estado === 'COMPLETADO'"
                      class="btn-secondary"
                      style="font-size:0.75rem;padding:0.3rem 0.75rem;color:#60a5fa;border-color:rgba(96,165,250,0.4)"
                      @click="irARegistrarPlata(fila)"
                      :disabled="fila.tieneAg"
                      :title="fila.tieneAg ? 'La Ley de Plata ya ha sido agregada' : 'Agregar ley de plata a este análisis'"
                    >
                      + Ag
                    </button>
                    <!-- Botón de re-ensayo (REE) -->
                    <button
                      v-if="fila.estado === 'COMPLETADO'"
                      class="btn-secondary"
                      style="font-size:0.75rem;padding:0.3rem 0.75rem;color:#a3e635;border-color:rgba(163,230,53,0.4)"
                      @click="agregarEnsayoREE(fila.cip)"
                      :disabled="cargandoREE === fila.cip"
                      title="Añadir un nuevo ensayo de re-ensayo (REE) para este CIP"
                    >
                      <span v-if="cargandoREE === fila.cip" class="spinner" style="margin-right:0.3rem"></span>
                      <span v-else>+ Ensayo</span>
                    </button>

                  </td>
                </tr>
              </template>

              <template v-else-if="tabActual === 'solidos'">
                <tr v-for="fila in filasMostrar" :key="fila.id || fila.cip">
                  <td style="text-align:center">
                    <input type="checkbox" :value="fila.cip" v-model="cipsSeleccionados" />
                  </td>
                  <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                  <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                  <td>
                    <span v-if="fila.sub_tipo === 'SOLIDOS'" class="badge-subtipo solidos">SÓLIDOS</span>
                    <span v-else class="td-mono" style="font-size:0.75rem;color:var(--color-text-faint)">LEGACY</span>
                  </td>
                  <td>{{ fila.leyCola ?? '-' }}</td>
                  <td>{{ fila.leyColaAg ?? '-' }}</td>
                  <td>
                    <span class="badge-estado" :class="badgeClass(fila.estado)">{{ fila.estado }}</span>
                  </td>
                  <td class="td-acciones">
                    <button v-if="fila.estado === 'PENDIENTE'" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irARegistrarRecuperacion(fila)">Registrar</button>
                    <button v-if="fila.estado === 'COMPLETADO' && !fila.certificadoUrl" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irARegistrarRecuperacion(fila)">Generar cert.</button>
                    <button v-if="fila.certificadoUrl" class="btn-secondary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="verCertificado(fila.certificadoUrl)">Ver cert.</button>
                  </td>
                </tr>
              </template>
              
              <template v-else-if="tabActual === 'solucion'">
                <tr v-for="fila in filasMostrar" :key="fila.id || fila.cip">
                  <td style="text-align:center">
                    <input type="checkbox" :value="fila.cip" v-model="cipsSeleccionados" />
                  </td>
                  <td class="td-mono" style="color:var(--color-gold)">{{ fila.cip }}</td>
                  <td class="td-fecha">{{ fmt(fila.fecha_envio) }}</td>
                  <td>
                    <span v-if="fila.sub_tipo === 'SOLUCION'" class="badge-subtipo solucion">SOLUCIÓN</span>
                    <span v-else class="td-mono" style="font-size:0.75rem;color:var(--color-text-faint)">LEGACY</span>
                  </td>
                  <td>{{ fila.leyLiquido ?? '-' }}</td>
                  <td>{{ fila.solucionAg ?? '-' }}</td>
                  <td>
                    <span class="badge-estado" :class="badgeClass(fila.estado)">{{ fila.estado }}</span>
                  </td>
                  <td class="td-acciones">
                    <button v-if="fila.estado === 'PENDIENTE'" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irARegistrarRecuperacion(fila)">Registrar</button>
                    <button v-if="fila.estado === 'COMPLETADO' && !fila.certificadoUrl" class="btn-primary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="irARegistrarRecuperacion(fila)">Generar cert.</button>
                    <button v-if="fila.certificadoUrl" class="btn-secondary" style="font-size:0.75rem;padding:0.3rem 0.75rem" @click="verCertificado(fila.certificadoUrl)">Ver cert.</button>
                  </td>
                </tr>
              </template>
            </template>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FlaskConical, RefreshCw, WifiOff, ChevronUp, ChevronDown, AlertTriangle } from 'lucide-vue-next'
import AlertasBanner from '@/components/AlertasBanner.vue'
import { useUiStore } from '@/stores/ui'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { laboratorioApi } from '@/api/laboratorio'
import { crearEnsayoREE } from '@/api/laboratorio'
import type { CIPAnalisisOut, LoteLabOut, AnalisisRecuperacionOut } from '@/types/laboratorio'
import { useSync } from '@/composables/useSync'
import { obtenerAnalisisLeyPendientes, type AnalisisLeyOfflineItem, encolarCipREE, obtenerCipsREEPorLote } from '@/composables/useOfflineQueue'
import { generateUUID } from '@/utils/uuid'

const router = useRouter()
const store  = useLaboratorioStore()
const ui     = useUiStore()
const {
  online,
  pendientes: pendientesSync,
  ultimoSync,
  sincronizar,
} = useSync()

const tabActual      = ref<'ley' | 'solidos' | 'solucion'>('ley')
const filtroEstado   = ref('')
const filtroBusqueda = ref('')
const filtroBusquedaLotes = ref('')
const filtroMaterialLotes = ref('')
const mostrarSoloCIPs = ref(false)

const cipsSeleccionados = ref<string[]>([])
const generandoConjunto = ref(false)

// ── Estado de carga para ensayo REE por CIP ────────────────────────────────────────────────────────────
const cargandoREE = ref<string | null>(null)

// Resetear selección al cambiar de pestaña
watch(tabActual, () => {
  cipsSeleccionados.value = []
})

const lotes = ref<LoteLabOut[]>([])
const cargandoLotes = ref(false)

// Análisis encolados offline para mostrar al laboratorista
const analisisOfflinePendientes = ref<AnalisisLeyOfflineItem[]>([])

async function cargarAnalisisOffline() {
  try {
    analisisOfflinePendientes.value = await obtenerAnalisisLeyPendientes()
  } catch {
    analisisOfflinePendientes.value = []
  }
}

async function cargarDatos() {
  if (store.puedeVerIP) {
    cargandoLotes.value = true
    try {
      lotes.value = await laboratorioApi.listarLotes()
    } catch (e) {
      console.error(e)
    } finally {
      cargandoLotes.value = false
    }
  } else {
    await store.cargarCips()
    await cargarAnalisisOffline()
  }
}

onMounted(() => cargarDatos())
function recargar() { cargarDatos() }

// ── Recargar datos cuando el sync completa ──────────────────────────────
watch(ultimoSync, async () => {
  await cargarDatos()
})

// ── Recargar cuando vuelve la conexión ──────────────────────────────────
watch(online, async (ahoraOnline) => {
  if (ahoraOnline) {
    // Pequeño delay para que el sync arranque primero
    await new Promise(r => setTimeout(r, 300))
    if (pendientesSync.value === 0) {
      // Sin pendientes: recargar directo (watch(ultimoSync) no disparará)
      await cargarDatos()
    }
    // Con pendientes: watch(ultimoSync) recargará cuando el sync termine
  } else {
    // Al desconectarse: actualizar sección de pendientes offline
    await cargarAnalisisOffline()
  }
})

// ── Actualizar pendientes offline cuando cambia el count global ─────────
watch(pendientesSync, () => {
  if (!store.puedeVerIP) cargarAnalisisOffline()
})

const pendientesLey = computed(() =>
  store.cips.filter(c => c.tipo_muestra === 'Laboratorio' && c.estado_ley === 'PENDIENTE').length
)

const pendientesSolidos = computed(() => {
  let count = 0
  for (const c of store.cips) {
    if (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno') {
      const hasPending = c.analisis_recuperacion.some(a => a.estado === 'PENDIENTE' && a.sub_tipo === 'SOLIDOS')
      if (hasPending) count++
    }
  }
  return count
})

const pendientesSolucion = computed(() => {
  let count = 0
  for (const c of store.cips) {
    if (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno') {
      const hasPending = c.analisis_recuperacion.some(a => a.estado === 'PENDIENTE' && a.sub_tipo === 'SOLUCION')
      if (hasPending) count++
    }
  }
  return count
})

function mapearCIP(c: CIPAnalisisOut) {
  if (tabActual.value === 'ley') {
    const vigente = c.analisis_ley.find(x => x.vigente)
    const ultimo = c.analisis_ley[c.analisis_ley.length - 1]
    const a = vigente ?? ultimo
    const tieneAg = c.analisis_ley.some(x => x.material === 'Ag' && x.vigente && x.estado === 'COMPLETADO')
    return [{
      id: a?.id,
      cip: c.cip,
      fecha_envio: c.fecha_envio,
      estado: c.estado_ley,
      leyMas:  (a?.ley_grueso ?? null) ,
      leyMenos:  (a?.ley_fino   ?? null) ,
      ozTc:     (a?.ley_final   ?? null) ,
      grTm:    (a?.ley_gr_tm   ?? null) ,
      certificadoUrl: a?.certificado_url ?? null,
      tieneAg: tieneAg,
    }]
  } else {
    // Solidos o Solucion
    const subTipoDeseado = tabActual.value === 'solidos' ? 'SOLIDOS' : 'SOLUCION'
    
    // Filtrar vigentes por el sub_tipo deseado.
    // Si queremos incluir 'LEGACY' en sólidos (opcional), podríamos hacerlo. Asumiremos que legacy va a sólidos.
    const vigentes = c.analisis_recuperacion.filter(x => x.vigente && (x.sub_tipo === subTipoDeseado || (!x.sub_tipo && tabActual.value === 'solidos')))
    
    if (vigentes.length === 0) {
      return []
    }
    
    return vigentes.map(a => ({
      id: a.id,
      cip: c.cip,
      sub_tipo: a.sub_tipo,
      fecha_envio: c.fecha_envio,
      estado: a.estado,
      leyCola: a.ley_cola ?? null,
      leyColaAg: a.ley_cola_ag ?? null,
      leyLiquido: a.ley_liquido ?? null,
      solucionAg: a.solucion_ag_g_m3 ?? null,
      certificadoUrl: a.certificado_url ?? null,
    }))
  }
}

const filasMostrar = computed(() => {
  // CIPs con análisis ya registrado offline → aparecen en la sección superior
  const cipsConAnalisisOffline = new Set(
    analisisOfflinePendientes.value.map(a => a.datos.cip)
  )

  const cipsFiltrados = store.cips.filter(c => {
    const tm = (c.tipo_muestra || '').toUpperCase()

    if (tabActual.value === 'ley') {
      if (tm !== 'LABORATORIO' && tm !== 'PROCESO') return false
      if (cipsConAnalisisOffline.has(c.cip)) return false  // excluir si ya está en sección offline
      
      if (tm === 'PROCESO' && mostrarSoloCIPs.value) return false
      
      // Ocultar completados si el tipo de análisis es externo (ej. llenado desde Comercial)
      if (c.estado_ley === 'COMPLETADO') {
        const vigente = c.analisis_ley.find(x => x.vigente)
        const ultimo = c.analisis_ley[c.analisis_ley.length - 1]
        const a = vigente ?? ultimo
        if (a && a.tipo_analisis === 'externo') {
          return false // Es externo, se oculta del dashboard de laboratorio
        }
      }

      return true
    }
    // For solidos/solucion tab: show Recuperacion types, or PROCESO if it has recuperacion analysis
    if (tm === 'RECUPERACIONINTERNO' || tm === 'RECUPERACIONEXTERNO') return true
    if (tm === 'PROCESO' && c.analisis_recuperacion.length > 0) {
      if (mostrarSoloCIPs.value) return false
      return true
    }
    return false
  })

  // map devuelve array de arrays, usamos flatMap
  return cipsFiltrados.flatMap(mapearCIP).filter(f => {
    if (filtroEstado.value && f.estado !== filtroEstado.value) return false
    if (filtroBusqueda.value && !f.cip.toLowerCase().includes(filtroBusqueda.value.toLowerCase())) return false
    return true
  })
})

const lotesFiltrados = computed(() => {
  return lotes.value.filter(l => {
    if (filtroMaterialLotes.value && (l.material || '').toLowerCase() !== filtroMaterialLotes.value.toLowerCase()) {
      return false
    }
    if (filtroBusquedaLotes.value) {
      const q = filtroBusquedaLotes.value.toLowerCase()
      const matchIp  = l.ip.toLowerCase().includes(q)
      const matchProv = (l.proveedor || '').toLowerCase().includes(q)
      const matchMat  = (l.material || '').toLowerCase().includes(q)
      // Buscar también en cualquier CIP vinculado al lote
      const matchCip  = (l.cips || []).some((cip: string) => cip.toLowerCase().includes(q))
      if (!matchIp && !matchProv && !matchMat && !matchCip) return false
    }
    return true
  })
})

function getRecuperacion(lote: LoteLabOut): string {
  const rec = lote.analisis_recuperacion.find(
    (a: AnalisisRecuperacionOut) => a.vigente && a.recuperacion != null
  )
  return rec?.recuperacion != null ? Number(rec.recuperacion).toFixed(1) + '%' : '-'
}

function fmt(d?: string | null | Date) {
  if (!d) return '-'
  // ISO date-only strings ("2026-07-06") are parsed as UTC midnight by JS,
  // which in Peru (UTC-5) would show as the previous day. Fix: treat as local.
  const dt = (typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d))
    ? new Date(d + 'T00:00:00')
    : new Date(d)
  return dt.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function badgeClass(estado: string) {
  return estado === 'COMPLETADO' ? 'completo' : estado === 'PENDIENTE' ? 'pendiente' : 'parcial'
}

async function verCertificado(ruta: string) {
  try {
    const url = await laboratorioApi.obtenerUrlArchivoVirtual(ruta)
    window.open(url, '_blank')
  } catch { ui.toast('Error al abrir certificado', 'error') }
}

function irARegistrarLey(cip: string) { router.push(`/laboratorio/ley/${cip}`) }
function irARegistrarRecuperacion(fila: any) {
  if (fila.sub_tipo === 'SOLIDOS') {
    router.push(`/laboratorio/solidos/${fila.cip}?id=${fila.id}`)
  } else if (fila.sub_tipo === 'SOLUCION') {
    router.push(`/laboratorio/solucion/${fila.cip}?id=${fila.id}`)
  } else {
    router.push(`/laboratorio/recuperacion/${fila.cip}?id=${fila.id}`)
  }
}
function irADetalleLote(ip: string) {
  router.push(`/laboratorio/lote/${ip}`)
}

async function agregarEnsayoREE(cipOrigen: string) {
  if (cargandoREE.value) return
  cargandoREE.value = cipOrigen
  try {
    if (online.value) {
      // ── Modo online: llamada directa al servidor ────────────────────────────
      const { nuevo_cip } = await crearEnsayoREE(cipOrigen)
      ui.toast(`Re-ensayo creado: ${nuevo_cip}`, 'success')
      router.push(`/laboratorio/ley/${nuevo_cip}`)
    } else {
      // ── Modo offline: cálculo local del código REE ─────────────────────────
      // 1. Obtener el CIP origen del caché local
      const cipData = store.cips.find(c => c.cip === cipOrigen)
      if (!cipData) {
        ui.toast('CIP no encontrado en caché local. Reconecta para crear el reensayo.', 'error')
        return
      }

      // 2. Extraer la base ofuscada del código CIP (ej: "058598D" de "CIP-058598D-A1")
      const match = cipOrigen.match(/^CIP-([A-Z0-9]+)-/)
      if (!match) {
        ui.toast('Formato de CIP no reconocido.', 'error')
        return
      }
      const baseOfuscada = match[1]!

      // 3. Contar REEs existentes: en caché de CIPs del store + pendientes offline para este lote
      const loteId = cipData.lote_id
      const cipsReeLoteCache = store.cips.filter(
        c => c.lote_id === loteId && c.cip.includes('-REE')
      ).length
      const cipsReeLoteOffline = (await obtenerCipsREEPorLote(loteId)).length
      const nRee = cipsReeLoteCache + cipsReeLoteOffline + 1

      // 4. Construir código
      const codigoRee = `CIP-${baseOfuscada}-REE${nRee}`

      // 5. Encolar en IndexedDB
      await encolarCipREE({
        offline_id: generateUUID(),
        cip_origen: cipOrigen,
        codigo_ree: codigoRee,
        lote_id: loteId,
        synced: false,
        sync_error: null,
      })

      ui.toast(`Re-ensayo creado offline: ${codigoRee}. Se sincronizará al reconectar.`, 'info')
      router.push(`/laboratorio/ley/${codigoRee}`)
    }
  } catch (err: any) {
    const msg = err?.response?.data?.detail ?? 'Error al crear el re-ensayo'
    ui.toast(msg, 'error')
  } finally {
    cargandoREE.value = null
  }
}

function irANuevoReconocimiento(subtipo: 'solidos' | 'solucion') {
  if (subtipo === 'solidos') router.push(`/laboratorio/solidos/_nuevo`)
  else router.push(`/laboratorio/solucion/_nuevo`)
}

function irARegistrarPlata(fila: any) {
  const cip = fila.cip
  const query = new URLSearchParams()

  const cipObj = store.cips.find(c => c.cip === cip)
  const auAnalisis = cipObj?.analisis_ley.find(
    (a: any) => a.material === 'Au' && a.vigente && !a.eliminado && a.detalles && a.detalles.length > 0
  ) || cipObj?.analisis_ley.find(
    (a: any) => a.material === 'Au' && a.vigente && !a.eliminado
  )

  if (auAnalisis && auAnalisis.detalles) {
    const dFino1 = auAnalisis.detalles.find((d: any) => d.origen === 'FINO1')
    const dFino2 = auAnalisis.detalles.find((d: any) => d.origen === 'FINO2')
    // Au 1 prellenado con valor de fino 2
    if (dFino2?.mineral_mg != null) query.set('au1', dFino2.mineral_mg.toString())
    // Au 2 prellenado con valor de fino 1
    if (dFino1?.mineral_mg != null) query.set('au2', dFino1.mineral_mg.toString())
    const pesoVal = dFino2?.peso ?? dFino1?.peso
    if (pesoVal != null) query.set('peso', pesoVal.toString())
  }

  // Buscar si ya existe un análisis SOLIDOS para este CIP
  const solidosExistente = cipObj?.analisis_recuperacion.find(
    (a: any) => (a.sub_tipo === 'SOLIDOS') && a.vigente && !a.eliminado
  )

  if (solidosExistente) {
    // Navegar al análisis SOLIDOS existente
    query.set('id', solidosExistente.id.toString())
    query.set('fromAg', '1')
    const url = router.resolve(`/laboratorio/solidos/${cip}?${query.toString()}`)
    window.open(url.href, '_blank')
    return
  }

  // Crear nuevo análisis SOLIDOS
  query.set('direct', '1')
  query.set('fromAg', '1')
  const url = router.resolve(`/laboratorio/solidos/${cip}?${query.toString()}`)
  window.open(url.href, '_blank')
}

// ── Generar Certificados Individuales ─────────────────────────────────────────
const descargando = ref<string | null>(null)

async function descargarInforme(cip: string) {
  descargando.value = cip
  try {
    await laboratorioApi.descargarCertificadoEnsayo(cip)
  } catch {
    ui.toast('Error al generar informe de ensayo', 'error')
  } finally {
    descargando.value = null
  }
}

async function generarCertLey(fila: any) {
    if (!fila.id) return
    await store.generarCertificadoLeyInterno(fila.id)
    recargar()
}

async function generarCertRec(fila: any) {
    if (!fila.id) return
    await store.generarCertificadoRecInterno(fila.id)
    recargar()
}

const todosSeleccionados = computed(() => {
  return filasMostrar.value.length > 0 && cipsSeleccionados.value.length === filasMostrar.value.length
})

function toggleTodosSeleccionados(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  if (checked) {
    cipsSeleccionados.value = filasMostrar.value.map(f => f.cip)
  } else {
    cipsSeleccionados.value = []
  }
}

async function generarCertificadoConjunto() {
  if (cipsSeleccionados.value.length === 0) return
  generandoConjunto.value = true
  try {
    if (tabActual.value === 'ley') {
      await laboratorioApi.descargarCertificadoEnsayoConjunto(cipsSeleccionados.value)
    } else {
      await laboratorioApi.descargarCertificadoRecuperacionConjunto(cipsSeleccionados.value)
    }
  } catch (e) {
    ui.toast('Error al generar certificado consolidado', 'error')
  } finally {
    generandoConjunto.value = false
  }
}
</script>

<style scoped>
.tabs-lab { display: flex; gap: 0; margin-bottom: 1.25rem; border-bottom: 1px solid var(--color-border); }
.tab-lab-btn { background: transparent; border: none; color: var(--color-text-muted); padding: 0.6rem 1.25rem; font-size: var(--text-md); font-family: var(--font-mono); cursor: pointer; border-bottom: 2px solid transparent; transition: color 0.15s, border-color 0.15s; display: flex; align-items: center; gap: 0.5rem; }
.tab-lab-btn.active { color: var(--color-gold); border-bottom-color: var(--color-gold); }
.tab-chevron { flex-shrink: 0; opacity: 0.6; }
.filtros-bar { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }

/* ── Sección offline pendientes ──────────────────────────── */
.offline-section {
  border: 1px solid rgba(245,158,11,.4);
  border-radius: var(--radius-md);
  margin-bottom: 1.25rem;
  overflow: hidden;
}
.offline-section-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: .55rem 1rem;
  background: rgba(245,158,11,.1);
  border-bottom: 1px solid rgba(245,158,11,.3);
}
.offline-section-titulo {
  font-family: var(--font-mono); font-size: var(--text-sm);
  letter-spacing: .18em; color: #f59e0b;
}
.offline-section-count {
  font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted);
}
.pendiente-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: var(--text-sm);
}
.pendiente-item:last-child { border-bottom: none; }
.pendiente-cip {
  font-family: var(--font-mono); color: var(--color-gold);
  min-width: 120px;
}
.pendiente-tipo { color: var(--color-text-muted); flex: 1; }
.pendiente-error { color: var(--color-error); font-size: 0.7rem; }
.badge-local {
  font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: .1em;
  background: rgba(245,158,11,.15); color: #f59e0b;
  border: 1px solid rgba(245,158,11,.3); border-radius: 3px;
  padding: 1px 5px;
}
.badge-subtipo {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
}
.badge-subtipo.solidos {
  background: rgba(212, 175, 55, 0.15);
  color: var(--color-gold);
  border: 1px solid rgba(212, 175, 55, 0.35);
}
.badge-subtipo.solucion {
  background: rgba(96, 165, 250, 0.15);
  color: #93c5fd;
  border: 1px solid rgba(96, 165, 250, 0.3);
}
</style>
