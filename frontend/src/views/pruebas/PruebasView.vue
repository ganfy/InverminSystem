<template>
  <div class="page-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">Pruebas Metalúrgicas</h1>
        <p class="page-subtitle">Gestión y registro de análisis de preparación</p>
      </div>
    </header>

    <div v-if="pruebasOffline.length > 0" class="offline-section">
      <div class="offline-section-header">
        <span class="offline-section-titulo">
          <WifiOff :size="20" class="aviso-icono" style="vertical-align: middle; margin-right: 5px;"/> SIN SINCRONIZAR
        </span>
        <span class="offline-section-count">{{ pruebasOffline.length }} prueba(s) local(es)</span>
      </div>
      <div class="tabla-wrapper">
        <table class="tabla" style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="text-align: left; border-bottom: 2px solid var(--color-border);">
              <th style="padding: 1rem;">IP</th>
              <th>Fecha Registro Local</th>
              <th>Malla (%)</th>
              <th>Gasto AgNO3</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pruebasOffline" :key="p.offline_id" class="fila-offline" style="border-bottom: 1px solid var(--color-border);">
              <td class="td-mono font-bold" style="padding: 1rem; color: var(--color-gold);">{{ p.ip }}</td>
              <td class="td-fecha">{{ formatearFechaLocal(p.datos.fecha_ingreso) }}</td>
              <td class="td-mono">
                {{ (p.datos.malla_porcentaje != null)
                    ? Number(p.datos.malla_porcentaje).toFixed(3)
                    : '---' }}
              </td>
              <td class="td-mono">
                {{ (p.datos.gasto_agno3 != null)
                    ? Number(p.datos.gasto_agno3).toFixed(3)
                    : '---' }}
              </td>
              <td>
                <span class="badge-estado" style="background-color: rgba(220,160,20,0.1); color: var(--color-warning);">PENDIENTE</span>
                <span class="badge-local" v-if="p.sync_error" style="background: rgba(220,60,60,.15); color: #dc3c3c; border-color: #dc3c3c;" :title="p.sync_error">ERROR</span>
                <span class="badge-local" v-else>LOCAL</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="filtros-bar card" style="margin-bottom: 1rem; padding: 1rem; display: flex; gap: 1rem; align-items: flex-end;">
      <div class="field" style="margin-bottom: 0;">
        <label class="field-label">Estado</label>
        <select class="field-input field-select" v-model="filtroEstado">
          <option value="Todos">Todos los estados</option>
          <option value="PENDIENTE">PENDIENTE</option>
          <option value="EN PROCESO">EN PROCESO</option>
          <option value="COMPLETO">COMPLETO</option>
        </select>
      </div>
      <div class="field" style="flex: 1; margin-bottom: 0;">
        <label class="field-label">Búsqueda</label>
        <input type="text" class="field-input" v-model="filtroBusqueda" placeholder="Buscar por IP..." />
      </div>
    </div>

    <div v-if="cargando && pruebas.length === 0" class="estado-tabla" style="text-align: center; padding: 2rem;">
      <span class="spinner-sm"></span> Cargando pruebas metalúrgicas...
    </div>

    <div v-else class="tabla-wrapper card">
      <table class="tabla" style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="text-align: left; border-bottom: 2px solid var(--color-border);">
            <th style="padding: 1rem;">IP</th>
            <th>Fecha Recepción</th>
            <th>Ingreso a Rodillos</th>
            <th>Fin Proyectado</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr class="row-hover" v-for="prueba in pruebasFiltradas" :key="prueba.ip" style="border-bottom: 1px solid var(--color-border);">
            <td style="padding: 1rem;" class="td-value-mono">{{ prueba.ip }}</td>

              <td>{{ prueba.fecha_recepcion ? formatearFecha(prueba.fecha_recepcion) : '---' }}</td>

              <td>{{ prueba.fecha_ingreso ? formatearFecha(prueba.fecha_ingreso) : '---' }}</td>

              <td class="td-value-mono highlight">
                {{ prueba.fecha_salida ? formatearFecha(prueba.fecha_salida) : '---' }}
              </td>

            <td>
              <span :class="['badge-estado', getEstadoRodillos(prueba).clase_badge]">
                {{ getEstadoRodillos(prueba).estado }}
              </span>
            </td>

            <td>
              <button
                class="btn-primary btn-sm"
                :disabled="getEstadoRodillos(prueba).boton_deshabilitado"
                @click="manejarAccionPrueba(prueba)"
              >
                {{ getEstadoRodillos(prueba).texto_boton }}
              </button>
            </td>
          </tr>
          <tr v-if="pruebasFiltradas.length === 0">
            <td colspan="6" style="text-align: center; padding: 2rem; color: var(--color-text-muted);">
              No se encontraron registros de pruebas en el servidor.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

  <script setup lang="ts">
  import { ref, computed, onMounted, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useUiStore } from '@/stores/ui'
  import { pruebasApi, type LotePruebaList } from '@/api/pruebas'
  import { useSync } from '@/composables/useSync'
  import { obtenerPruebasPendientes, type PruebaQueueData } from '@/composables/useOfflineQueue'
  import { WifiOff } from 'lucide-vue-next'

  const router = useRouter()
  const ui = useUiStore()
  const { pendientes, online, ultimoSync } = useSync()

  // Estado Local
  const pruebas = ref<LotePruebaList[]>([])
  const pruebasOffline = ref<PruebaQueueData[]>([])
  const cargando = ref(false)

  const filtroEstado = ref('Todos')
  const filtroBusqueda = ref('')

watch(pendientes, async (nuevosPendientes, viejosPendientes) => {
  // Siempre actualizamos la tablita naranja
  await cargarPruebasOffline()

  // Si la cola bajó a 0 (es decir, el internet volvió y se envió todo con éxito), forzamos la recarga de la tabla principal para que aparezca ahí.
  if (nuevosPendientes === 0 && (viejosPendientes || 0) > 0) {
    await cargarDatos()
  }
})

watch(ultimoSync, async () => {
  await cargarDatos()
  await cargarPruebasOffline()
})

  watch(online, async (isOnline) => {
    if (isOnline) {
      await new Promise(r => setTimeout(r, 300)) // delay para sync
      const hay = (await obtenerPruebasPendientes()).length
      if (hay === 0) {
        await cargarDatos()
        await cargarPruebasOffline()
      }
    } else {
      await cargarPruebasOffline()
    }
  })

  // ── Carga de Datos ──
  const cargarPruebasOffline = async () => {
    try {
      const pend = await obtenerPruebasPendientes()
      pruebasOffline.value = pend.filter(p => !p.synced)
    } catch (e) {
      console.error('Error cargando pruebas offline:', e)
    }
  }

  const cargarDatos = async () => {
    if (cargando.value) return
    cargando.value = true
    try {
      const data = await pruebasApi.obtenerListaPruebas()
      pruebas.value = Array.isArray(data) ? data : []
    } catch (error: any) {
      console.error("Error al cargar la lista de pruebas:", error)
      if (online.value) ui.toast('Error al conectar con el servidor', 'error')
      pruebas.value = []
    } finally {
      cargando.value = false
    }
  }

  onMounted(async () => {
    await cargarDatos()
    await cargarPruebasOffline()
  })

  // ── Filtros y Utilidades ──
  const pruebasFiltradas = computed(() => {
    if (!pruebas.value) return []
    return pruebas.value.filter(p => {
      const matchEstado = filtroEstado.value === 'Todos' || p.estado === filtroEstado.value
      const query = filtroBusqueda.value.toLowerCase()
      const matchBusqueda = !query || p.ip.toLowerCase().includes(query)
      // Filtramos las que ya están en la cola local para no duplicar info visualmente
      const estaOffline = pruebasOffline.value.some(off => off.ip === p.ip)
      return matchEstado && matchBusqueda && !estaOffline
    })
  })

  const formatearFecha = (fechaStr: string | null | undefined) => {
    if (!fechaStr) return '---'
    try {
      const utc = (fechaStr.includes('+') || fechaStr.endsWith('Z')) ? fechaStr : fechaStr + 'Z'
      return new Date(utc).toLocaleString('es-PE', {
        timeZone: 'America/Lima',
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      })
    } catch (e) { return '---' }
  }

  const formatearFechaLocal = (fechaStr: string | null | undefined) => {
    if (!fechaStr) return '---'
    try {
      return new Date(fechaStr).toLocaleString('es-PE', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      })
    } catch (e) { return '---' }
  }

  const irARegistrar = (ip: any) => {
    if (!ip) return
    router.push({ name: 'RegistrarPrueba', params: { ip: String(ip) } })
  }

  const manejarAccionPrueba = (prueba: any) => {
    const estado = getEstadoRodillos(prueba)
    if (estado.estado === 'PENDIENTE') {
      irARegistrar(prueba.ip)
    } else if (estado.estado === 'COMPLETADO') {
      router.push({ name: 'RegistrarPrueba', params: { ip: String(prueba.ip) } })
    }
  }

  function getEstadoRodillos(lote: any) {
  // Ahora usamos la variable exacta que manda el backend
  const ingreso = lote.fecha_ingreso;

  if (!ingreso) {
    return {
      estado: 'PENDIENTE',
      clase_badge: 'pendiente',
      texto_boton: 'Iniciar Prueba',
      boton_deshabilitado: false
    };
  }

  const normalizarZonaHoraria = (fechaStr: string) => {
    return (fechaStr.includes('+') || fechaStr.endsWith('Z')) ? fechaStr : fechaStr + 'Z';
  };

  const ingresoN = new Date(normalizarZonaHoraria(ingreso));
  let salida;
  const salidaBackend = lote.fecha_salida || lote.fecha_salida_prueba;

  if (salidaBackend) {
    salida = new Date(normalizarZonaHoraria(salidaBackend));
  } else {
    salida = new Date(ingresoN);
    salida.setHours(salida.getHours() + 48); // Respaldo matemático de +48h
  }

  const ahora = new Date();

  if (ahora < salida) {
    const horasRestantes = Math.ceil((salida.getTime() - ahora.getTime()) / (1000 * 60 * 60));
    return {
      estado: 'EN PROCESO',
      clase_badge: 'en-proceso',
      texto_boton: `Rodando... (${horasRestantes}h rest.)`,
      boton_deshabilitado: true
    };
  }

  return {
    estado: 'COMPLETADO',
    clase_badge: 'completado',
    texto_boton: 'Registrar Fin / Ver',
    boton_deshabilitado: false
  };
}

  </script>

  <style scoped>
  /* ── [OFFLINE] Sección sin sincronizar (copiada de Balanza) ───────────────────── */
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
  .fila-offline { background: rgba(245,158,11,.04); }
  .fila-offline:hover { background: rgba(245,158,11,.09) !important; }
  .badge-local {
    font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: .1em;
    background: rgba(245,158,11,.15); color: #f59e0b;
    border: 1px solid rgba(245,158,11,.3); border-radius: 3px;
    padding: 1px 5px; margin-left: .4rem; vertical-align: middle;
  }

  /* ── Badges Normales ───────────────────── */
  .badge-estado {
    padding: 0.25rem 0.6rem;
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: bold;
    font-family: var(--font-mono);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .en-proceso { background-color: rgba(220,160,20,0.1); color: var(--color-warning); border: 1px solid rgba(220,160,20,0.3); }
  .completado { background-color: rgba(60,180,80,0.1); color: var(--color-success); border: 1px solid rgba(60,180,80,0.3); }
  .pendiente { background-color: rgba(220,60,60,0.1); color: var(--color-error); border: 1px solid rgba(220,60,60,0.3); }
  </style>
