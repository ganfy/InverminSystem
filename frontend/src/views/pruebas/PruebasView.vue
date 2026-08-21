<template>
  <div class="page-container">
    <header class="page-header">
      <div class="header-title-row">
        <Beaker class="header-icon" :size="26" />
        <div>
          <h1 class="page-title">Pruebas Metalúrgicas</h1>
          <p class="page-subtitle">Gestión y registro de análisis de preparación</p>
        </div>
      </div>
      <div style="display:flex;gap:0.5rem;align-items:center">
        <!-- Botón de registro en lote: aparece cuando hay IPs seleccionados -->
        <button
          v-if="ipsSeleccionados.length > 0"
          class="btn-primary"
          style="font-size:0.78rem;padding:0.4rem 0.9rem"
          @click="irARegistrarLote"
        >
          <Layers :size="15" style="margin-right:0.3rem;vertical-align:middle" />
          Registrar Lote ({{ ipsSeleccionados.length }})
        </button>
        <button
          class="btn-secondary"
          style="font-size:0.78rem;padding:0.4rem 0.9rem"
          @click="router.push('/pruebas/recuperaciones')"
        >
          Ver Recuperaciones →
        </button>
        <button
          class="btn-refresh"
          @click="cargarDatos"
          :disabled="cargando"
          title="Actualizar datos"
        >
          <RefreshCw :size="20" :class="{ 'spinning': cargando }" />
        </button>
      </div>
    </header>

    <AlertasBanner modulo="PRUEBAS" con-observaciones />

    <!-- Offline queue -->
    <div v-if="pruebasOffline.length > 0" class="offline-section">
      <div class="offline-section-header">
        <span class="offline-section-titulo">
          <WifiOff :size="20" style="vertical-align:middle;margin-right:5px" /> SIN SINCRONIZAR
        </span>
        <span class="offline-section-count">{{ pruebasOffline.length }} prueba(s) local(es)</span>
      </div>
      <div class="tabla-wrapper">
        <table class="tabla">
          <thead>
            <tr>
              <th>IP</th>
              <th>Fecha Registro Local</th>
              <th>Malla (%)</th>
              <th>Gasto AgNO3</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in pruebasOffline" :key="p.offline_id" class="fila-offline">
              <td class="td-mono" style="color:var(--color-gold)">{{ p.ip }}</td>
              <td class="td-fecha">{{ fmtLocal(p.datos.fecha_ingreso) }}</td>
              <td class="td-mono">{{ p.datos.malla_porcentaje?.toFixed(3) ?? '---' }}</td>
              <td class="td-mono">{{ p.datos.gasto_agno3?.toFixed(3) ?? '---' }}</td>
              <td>
                <span class="badge-estado pendiente">PENDIENTE</span>
                <span class="badge-local" v-if="p.sync_error" :title="p.sync_error" style="color:#dc3c3c">ERROR</span>
                <span class="badge-local" v-else>LOCAL</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filtros-bar">
      <div class="field" style="min-width:180px">
        <label class="field-label">Estado</label>
        <select class="field-select field-sm field-sm field-input" v-model="filtroEstado">
          <option value="Todos">Todos los estados</option>
          <option value="PENDIENTE">PENDIENTE</option>
          <option value="EN PROCESO">EN PROCESO</option>
          <option value="COMPLETADO">COMPLETADO</option>
        </select>
      </div>
      <div class="field" style="flex:1">
        <label class="field-label">Búsqueda</label>
        <input type="text" class="field-input" v-model="filtroBusqueda" placeholder="Buscar por IP, CIP..." />
      </div>
      <div class="field" style="align-items:center; flex-direction:row; gap:0.5rem; justify-content:flex-end">
        <input type="checkbox" id="toggleDescartadas" v-model="mostrarDescartadas" />
        <label for="toggleDescartadas" class="field-label" style="margin-bottom:0; cursor:pointer">
          Mostrar descartadas
        </label>
      </div>
    </div>

    <!-- Tabla principal -->
    <div v-if="cargando && pruebas.length === 0" class="estado-tabla">
      <span class="spinner"></span> Cargando pruebas metalúrgicas...
    </div>
    <div v-else class="tabla-wrapper">
      <table class="tabla">
        <thead>
          <tr>
            <th style="width:36px;text-align:center">
              <input type="checkbox" :checked="todosPendientesSeleccionados" @change="toggleTodosPendientes" title="Seleccionar todos los pendientes" />
            </th>
            <th>IP</th>
            <th>FECHA RECEPCIÓN</th>
            <th>INGRESO A RODILLOS</th>
            <th>FIN PROYECTADO</th>
            <th>MALLA (%)</th>
            <th>ADIC. NaCN</th>
            <th>ADIC. NaOH</th>
            <th>CIP RECUPERACIÓN</th>
            <th>ESTADO</th>
            <th>ACCIONES</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="prueba in pruebasFiltradas"
            :key="prueba.ip + (prueba.fecha_ingreso ?? '')"
            :class="{ 'fila-descartada': prueba.descartado, 'fila-seleccionada': ipsSeleccionados.includes(prueba.ip) }"
          >
            <!-- Checkbox de selección (solo para pruebas no descartadas) -->
            <td style="text-align:center">
              <input
                v-if="!prueba.descartado && esPendienteSeleccionable(prueba)"
                type="checkbox"
                :value="prueba.ip"
                v-model="ipsSeleccionados"
              />
            </td>
            <td class="td-mono" style="color:var(--color-gold)">{{ prueba.ip }}</td>
            <td class="td-fecha">{{ fmt(prueba.fecha_recepcion) }}</td>
            <td class="td-fecha">{{ fmt(prueba.fecha_ingreso) }}</td>
            <td class="td-mono" style="color:var(--color-gold-light)">
              {{ fmt(prueba.fecha_salida) }}
            </td>
            <td class="td-mono">{{ prueba.malla_porcentaje?.toFixed(1) ?? '---' }}</td>
            <!-- Columnas de adición acumulada -->
            <td class="td-mono">
              <span v-if="prueba.adicion_nacn != null" class="adicion-badge">{{ prueba.adicion_nacn.toFixed(2) }}g</span>
              <span v-else class="td-mono" style="color:var(--color-text-faint)">—</span>
            </td>
            <td class="td-mono">
              <span v-if="prueba.adicion_naoh != null" class="adicion-badge">{{ prueba.adicion_naoh.toFixed(2) }}g</span>
              <span v-else class="td-mono" style="color:var(--color-text-faint)">—</span>
            </td>
            <!-- CIP de recuperación -->
            <td>
              <div v-if="prueba.cips_asignados?.length">
                <div v-for="cip in prueba.cips_asignados" :key="cip" class="td-mono" style="color:var(--color-gold);font-size:0.8rem">
                  {{ cip }}
                </div>
              </div>
              <span v-else class="badge-estado pendiente" style="font-size:0.65rem">Sin CIP</span>
            </td>
            <td>
              <template v-if="prueba.descartado">
                <span class="badge-estado descartado" :title="prueba.motivo_descarte ?? ''">
                  DESCARTADO
                </span>
              </template>
              <template v-else>
                <span class="badge-estado" :class="estadoClase(prueba.estado)">
                  {{ prueba.estado }}
                </span>
              </template>
            </td>
            <!-- Columna ACCIONES: registrar, adición, etiquetar -->
            <td class="td-acciones">
              <template v-if="!prueba.descartado">
                <!-- Registrar / Ver prueba -->
                <button
                  class="btn-primary"
                  style="font-size:0.75rem;padding:0.3rem 0.75rem"
                  :disabled="estadoBotonRegistrar(prueba).disabled"
                  @click="irARegistrar(prueba.ip)"
                >
                  {{ estadoBotonRegistrar(prueba).texto }}
                </button>

                <!-- Adición: solo cuando EN PROCESO (rodando) -->
                <button
                  v-if="prueba.estado === 'EN PROCESO'"
                  class="btn-adicion"
                  style="font-size:0.75rem;padding:0.3rem 0.75rem"
                  @click="abrirModalAdicion(prueba)"
                >
                  + Adición
                </button>

                <!-- Etiquetar: solo cuando COMPLETADO, o EN PROCESO faltando 5h, y sin CIP aún -->
                <button
                  v-if="puedeEtiquetar(prueba)"
                  class="btn-secondary"
                  style="font-size:0.75rem;padding:0.3rem 0.75rem"
                  :disabled="etiquetando === prueba.ip"
                  @click="etiquetar(prueba.ip)"
                  title="Generar CIP de recuperación para laboratorio"
                >
                  <span v-if="etiquetando === prueba.ip" class="spinner" style="margin-right:0.3rem"></span>
                  Etiquetar
                </button>

                <!-- Ver CIP (ya etiquetado) -->
                <button
                  v-if="prueba.etiquetado"
                  class="btn-secondary"
                  style="font-size:0.75rem;padding:0.3rem 0.75rem"
                  @click="verEtiqueta(prueba)"
                  title="Ver etiqueta CIP"
                >
                  <Tag :size="14" /> Reimprimir
                </button>

                <!-- Enviar a Lab: badge si TODO enviado, botón si quedan sub-tipos -->
                <template v-if="prueba.estado === 'COMPLETADO' && prueba.etiquetado">
                  <!-- Todo ya fue enviado -->
                  <span
                    v-if="prueba.sub_tipos_enviados.includes('SOLIDOS') && prueba.sub_tipos_enviados.includes('SOLUCION')"
                    class="badge-lab-enviado"
                    :title="'Enviado: ' + prueba.sub_tipos_enviados.join(' + ')"
                  >
                    <FlaskConical :size="12" style="margin-right:0.25rem;vertical-align:middle" />
                    Enviado
                  </span>

                  <!-- Quedan sub-tipos por enviar -->
                  <button
                    v-else
                    class="btn-enviar-lab"
                    style="font-size:0.75rem;padding:0.3rem 0.75rem"
                    :disabled="enviandoLab === prueba.ip"
                    @click="abrirModalEnviarLab(prueba)"
                    :title="prueba.sub_tipos_enviados.length ? 'Ya enviado: ' + prueba.sub_tipos_enviados.join(', ') + '. Click para enviar el resto.' : 'Enviar muestras al laboratorio interno Paititi'"
                  >
                    <span v-if="enviandoLab === prueba.ip" class="spinner" style="margin-right:0.3rem"></span>
                    <FlaskConical v-else :size="14" style="margin-right:0.25rem;vertical-align:middle" />
                    Enviar a Lab
                    <span v-if="prueba.sub_tipos_enviados.length" style="font-size:0.65rem;opacity:0.7;margin-left:0.2rem">(parcial)</span>
                  </button>
                </template>
              </template>
            </td>
            <!-- Columna DESCARTAR: separada para mejor orden -->
            <td class="td-descartar">
              <template v-if="!prueba.descartado">
                <button
                  class="btn-descartar"
                  style="font-size:0.72rem;padding:0.25rem 0.6rem"
                  @click="abrirModalDescartar(prueba.ip)"
                  title="Descartar prueba (envase roto, etc.)"
                >
                  Descartar
                </button>
              </template>
              <template v-else>
                <span class="td-mono" style="font-size:0.7rem;color:var(--color-text-faint);font-style:italic" :title="prueba.motivo_descarte ?? ''">
                  {{ prueba.motivo_descarte ? prueba.motivo_descarte.slice(0, 30) + (prueba.motivo_descarte.length > 30 ? '…' : '') : '' }}
                </span>
              </template>
            </td>
          </tr>
          <tr v-if="pruebasFiltradas.length === 0">
            <td colspan="12" class="estado-tabla sin-datos">Sin pruebas registradas</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal etiqueta CIP (impresión) -->
    <div v-if="etiquetaModal" class="modal-overlay" @click.self="etiquetaModal = null">
      <div class="modal modal-md">
        <div class="modal-header">
          <h2>Etiquetas CIP Recuperación</h2>
          <button class="btn-cerrar" @click="etiquetaModal = null">×</button>
        </div>
        <div class="modal-body" style="text-align:center; max-height: 60vh; overflow-y: auto;">
          <p class="field-label" style="margin-bottom:0.5rem">LOTE: {{ etiquetaModal.ip }}</p>
          
          <div class="control-impresion no-print">
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

          <div id="area-impresion-pruebas" class="grid-etiquetas" :class="{ 'grid-etiquetas--1col': formatoRollo === '1col' }">
            <div v-for="(cip, i) in etiquetaModal.cips" :key="cip" class="etiqueta-print">
              <span class="etiqueta-title">INVERMIN PAITITI S.A.C. - RECUPERACIÓN</span>
              <svg :id="'barcode-prueba-' + i" class="barcode-visual"></svg>
              <span class="etiqueta-codigo">{{ cip }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer no-print">
          <button class="btn-secondary" @click="etiquetaModal = null">Cerrar</button>
          <button class="btn-primary" @click="imprimirEtiqueta(etiquetaModal)">Imprimir Todas</button>
        </div>
      </div>
    </div>

    <!-- Modal Descartar Prueba -->
    <div v-if="modalDescartar" class="modal-overlay" @click.self="modalDescartar = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Descartar Prueba</h2>
          <button class="btn-cerrar" @click="modalDescartar = null">×</button>
        </div>
        <div class="modal-body">
          <p style="font-size:0.85rem;color:var(--color-text-muted);margin-bottom:1rem">
            Esta prueba será descartada (ej: envase roto, derrame, etc.).<br>
            El registro se conserva para <strong>seguimiento de insumos gastados</strong>,
            pero <strong>no se tomará para etiquetado ni análisis</strong>.
          </p>
          <div class="field">
            <label class="field-label">MOTIVO DEL DESCARTE (obligatorio):</label>
            <textarea
              class="field-input"
              v-model="motivoDescarte"
              rows="3"
              placeholder="Ej: Se rompió el envase durante el transporte"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalDescartar = null">Cancelar</button>
          <button
            class="btn-danger"
            :disabled="!motivoDescarte.trim() || descartando"
            @click="confirmarDescartar"
          >
            <span v-if="descartando" class="spinner" style="margin-right:0.3rem"></span>
            Confirmar Descarte
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Adición (NaCN / NaOH) -->
    <div v-if="modalAdicion" class="modal-overlay" @click.self="modalAdicion = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Registrar Adición</h2>
          <button class="btn-cerrar" @click="modalAdicion = null">×</button>
        </div>
        <div class="modal-body">
          <p style="font-size:0.85rem;color:var(--color-text-muted);margin-bottom:0.75rem">
            Lote <strong style="font-family:var(--font-mono);color:var(--color-gold)">{{ modalAdicion.ip }}</strong>
            — Los valores se <strong>suman</strong> al acumulado existente.
          </p>

          <div v-if="modalAdicion.adicion_nacn != null || modalAdicion.adicion_naoh != null"
            class="adicion-acumulado-info"
          >
            <span>Acumulado actual:</span>
            <span v-if="modalAdicion.adicion_nacn != null">NaCN: <strong>{{ modalAdicion.adicion_nacn.toFixed(2) }}g</strong></span>
            <span v-if="modalAdicion.adicion_naoh != null">NaOH: <strong>{{ modalAdicion.adicion_naoh.toFixed(2) }}g</strong></span>
          </div>

          <div class="form-grid" style="grid-template-columns:1fr 1fr;gap:0.75rem">
            <div class="field">
              <label class="field-label">ADICIÓN NaCN (g)</label>
              <input
                type="number"
                class="field-input"
                v-model.number="formAdicion.adicion_nacn"
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
            <div class="field">
              <label class="field-label">ADICIÓN NaOH (g)</label>
              <input
                type="number"
                class="field-input"
                v-model.number="formAdicion.adicion_naoh"
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalAdicion = null">Cancelar</button>
          <button
            class="btn-primary"
            :disabled="(!formAdicion.adicion_nacn && !formAdicion.adicion_naoh) || registrandoAdicion"
            @click="confirmarAdicion"
          >
            <span v-if="registrandoAdicion" class="spinner" style="margin-right:0.3rem"></span>
            Registrar Adición
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Enviar a Laboratorio Interno -->
    <div v-if="modalEnviarLab" class="modal-overlay" @click.self="modalEnviarLab = null">
      <div class="modal modal-md">
        <div class="modal-header">
          <h2 style="display:flex;align-items:center;gap:0.5rem">
            <FlaskConical :size="18" style="color:var(--color-gold)" />
            Enviar a Laboratorio Interno
          </h2>
          <button class="btn-cerrar" @click="modalEnviarLab = null">×</button>
        </div>
        <div class="modal-body">
          <div style="background:rgba(184,151,75,0.06);border:1px solid rgba(184,151,75,0.2);border-radius:6px;padding:0.55rem 0.85rem;margin-bottom:1rem;display:flex;flex-wrap:wrap;gap:0.5rem 1.25rem;font-size:0.82rem; align-items:center;">
            <span style="color:var(--color-text-muted)">Lote IP: <strong style="font-family:var(--font-mono);color:var(--color-gold)">{{ modalEnviarLab.ip }}</strong></span>
            
            <span style="color:var(--color-text-muted); display:flex; align-items:center; gap:0.5rem;">
              CIP Recuperación: 
              <select v-if="modalEnviarLab.cips_asignados?.length > 1" v-model="envioCip" class="input-moderno" style="font-family:var(--font-mono);color:var(--color-gold); padding:0.1rem 0.5rem; height:auto; min-width:140px; font-size:0.8rem;">
                <option v-for="cip in modalEnviarLab.cips_asignados" :key="cip" :value="cip">{{ cip }}</option>
              </select>
              <strong v-else style="font-family:var(--font-mono);color:var(--color-gold)">{{ modalEnviarLab.cips_asignados?.[0] || '---' }}</strong>
            </span>
          </div>
          <p style="font-size:0.84rem;color:var(--color-text-muted);margin-bottom:1rem">
            Seleccione qué análisis debe realizar el laboratorio Paititi sobre el CIP asignado.
          </p>

          <div style="display:flex;flex-direction:column;gap:0.75rem">

            <!-- Info de lo ya enviado -->
            <div
              v-if="yaEnviadosCipActual.length"
              style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.25);border-radius:6px;padding:0.55rem 0.8rem;font-size:0.78rem;color:#a5b4fc"
            >
              Ya en laboratorio:
              <strong>{{ yaEnviadosCipActual.join(' + ') }}</strong>
            </div>

            <!-- Opción: Ambos (solo disponible si ninguno fue enviado) -->
            <label
              class="lab-opcion"
              :class="{ activo: envioModo === 'ambos', deshabilitado: yaEnviadosCipActual.length > 0 }"
            >
              <input
                type="radio" name="subtipo" value="ambos" v-model="envioModo"
                style="margin-right:0.5rem"
                :disabled="yaEnviadosCipActual.length > 0"
              />
              <div>
                <div style="font-weight:700;font-size:0.85rem">Sólidos + Solución (completo)</div>
                <div style="font-size:0.75rem;color:var(--color-text-muted)">Reconocimiento de pulpa (FA) y Absorción Atómica (AAS)</div>
              </div>
            </label>

            <!-- Opción: Solo Sólidos -->
            <label
              class="lab-opcion"
              :class="{ activo: envioModo === 'solidos', deshabilitado: yaEnviadosCipActual.includes('SOLIDOS') }"
            >
              <input
                type="radio" name="subtipo" value="solidos" v-model="envioModo"
                style="margin-right:0.5rem"
                :disabled="yaEnviadosCipActual.includes('SOLIDOS')"
              />
              <div style="display:flex;align-items:center;gap:0.5rem">
                <div>
                  <div style="font-weight:700;font-size:0.85rem">Solo Sólidos (FA)</div>
                  <div style="font-size:0.75rem;color:var(--color-text-muted)">Reconocimiento de sólidos por Fire Assay</div>
                </div>
                <span
                  v-if="modalEnviarLab.sub_tipos_enviados.includes('SOLIDOS')"
                  style="font-size:0.7rem;background:rgba(99,102,241,0.15);color:#a5b4fc;border-radius:4px;padding:0.1rem 0.4rem;white-space:nowrap"
                >✓ Enviado</span>
              </div>
            </label>

            <!-- Opción: Solo Solución -->
            <label
              class="lab-opcion"
              :class="{ activo: envioModo === 'solucion', deshabilitado: yaEnviadosCipActual.includes('SOLUCION') }"
            >
              <input
                type="radio" name="subtipo" value="solucion" v-model="envioModo"
                style="margin-right:0.5rem"
                :disabled="yaEnviadosCipActual.includes('SOLUCION')"
              />
              <div style="display:flex;align-items:center;gap:0.5rem">
                <div>
                  <div style="font-weight:700;font-size:0.85rem">Solo Solución (AAS)</div>
                  <div style="font-size:0.75rem;color:var(--color-text-muted)">Leyes en solución por Absorción Atómica</div>
                </div>
                <span
                  v-if="modalEnviarLab.sub_tipos_enviados.includes('SOLUCION')"
                  style="font-size:0.7rem;background:rgba(99,102,241,0.15);color:#a5b4fc;border-radius:4px;padding:0.1rem 0.4rem;white-space:nowrap"
                >✓ Enviado</span>
              </div>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalEnviarLab = null">Cancelar</button>
          <button
            class="btn-primary"
            :disabled="enviandoLab === modalEnviarLab.ip || envioSubTiposEfectivos.length === 0"
            @click="confirmarEnviarLab"
          >
            <span v-if="enviandoLab === modalEnviarLab.ip" class="spinner" style="margin-right:0.3rem"></span>
            Enviar al Laboratorio
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import AlertasBanner from '@/components/AlertasBanner.vue'
import { pruebasApi, type LotePruebaList } from '@/api/pruebas'
import { useSync } from '@/composables/useSync'
import {
    obtenerPruebasPendientes,
    type PruebaQueueData,
    guardarPruebasListaCache,
    obtenerPruebasListaCache,
    encolarCipPruebaOffline,
    contarCipsPruebasPorLote,
} from '@/composables/useOfflineQueue'
import { generarParCipsRecuperacion, generarParIpRecuperacion } from '@/utils/cipGenerator'
import { CONFIG_PRUEBAS } from '@/utils/units'
import { generateUUID } from '@/utils/uuid'
import { WifiOff, Tag, RefreshCw, Beaker, Layers, FlaskConical } from 'lucide-vue-next'
import JsBarcode from 'jsbarcode'

const router  = useRouter()
const ui      = useUiStore()
const sync    = useSync()
const { pendientes, online, ultimoSync } = sync

const pruebas       = ref<LotePruebaList[]>([])
const pruebasOffline = ref<PruebaQueueData[]>([])
const cargando      = ref(false)
const etiquetando   = ref<string | null>(null)   // IP en proceso de etiquetado
const etiquetaModal = ref<{ ip: string; cips: string[] } | null>(null)

type FormatoRollo = '1col' | '2col'
const formatoRollo = ref<FormatoRollo>(
  (localStorage.getItem('invermin_formato_etiquetas') as FormatoRollo) || '2col'
)
const cambiarFormato = (formato: FormatoRollo) => {
  formatoRollo.value = formato
  localStorage.setItem('invermin_formato_etiquetas', formato)
}

const ipsSeleccionados = ref<string[]>([])
const filtroEstado   = ref('Todos')
const filtroBusqueda = ref('')
const mostrarDescartadas = ref(false)

function puedeEtiquetar(prueba: LotePruebaList) {
  if (prueba.etiquetado) return false
  if (prueba.estado === 'COMPLETADO') return true
  if (prueba.estado === 'EN PROCESO' && prueba.fecha_ingreso) {
    const restante = obtenerTiempoRestante(prueba.fecha_ingreso)
    if (restante.terminado) return true
    
    // Si faltan <= 5 horas (por ej. 4h 59m, o exactamente 5h 0m)
    if (restante.horas < 5 || (restante.horas === 5 && restante.minutos === 0)) {
      return true
    }
  }
  return false
}

// ── Descartar prueba ──────────────────────────────────────────────────────────
const modalDescartar  = ref<string | null>(null)  // IP de la prueba a descartar
const motivoDescarte  = ref('')
const descartando     = ref(false)

// ── Enviar a Laboratorio ──────────────────────────────────────────────────────
const modalEnviarLab = ref<LotePruebaList | null>(null)
const enviandoLab    = ref<string | null>(null)
const envioModo      = ref<'ambos' | 'solidos' | 'solucion'>('ambos')
const envioCip       = ref<string>('')

const yaEnviadosCipActual = computed(() => {
  if (!modalEnviarLab.value || !envioCip.value) return []
  return modalEnviarLab.value.sub_tipos_enviados_por_cip?.[envioCip.value] || []
})

// Sub-tipos seleccionados por el usuario en el modo actual
const envioSubTipos = computed(() => {
  if (envioModo.value === 'ambos')   return ['SOLIDOS', 'SOLUCION']
  if (envioModo.value === 'solidos') return ['SOLIDOS']
  return ['SOLUCION']
})

// Sub-tipos efectivos a enviar = seleccionados menos los ya enviados
const envioSubTiposEfectivos = computed(() => {
  const yaEnviados = yaEnviadosCipActual.value
  return envioSubTipos.value.filter(t => !yaEnviados.includes(t))
})

watch([modalEnviarLab, envioCip], () => {
  if (!modalEnviarLab.value || !envioCip.value) return
  const yaEnviados = yaEnviadosCipActual.value
  if (!yaEnviados.includes('SOLIDOS') && !yaEnviados.includes('SOLUCION')) {
    envioModo.value = 'ambos'
  } else if (!yaEnviados.includes('SOLIDOS')) {
    envioModo.value = 'solidos'
  } else if (!yaEnviados.includes('SOLUCION')) {
    envioModo.value = 'solucion'
  } else {
    envioModo.value = 'ambos'
  }
})

// ── Adición modal ─────────────────────────────────────────────────────────────
const modalAdicion = ref<LotePruebaList | null>(null)
const formAdicion  = ref({ adicion_nacn: null as number | null, adicion_naoh: null as number | null })
const registrandoAdicion = ref(false)

const estadosPrueba = [
  { id: 'PENDIENTE', nombre: 'Pendiente' },
  { id: 'EN PROCESO', nombre: 'En Proceso' }, // Cambiado de EN_PROCESO a EN PROCESO
  { id: 'COMPLETADO', nombre: 'Completado' }
];

// ── Watchers ──────────────────────────────────────────────────────────────────
watch(pendientes, async (nuevo, viejo) => {
  await cargarOffline()
  if (nuevo === 0 && (viejo ?? 0) > 0) await cargarDatos()
})
watch(ultimoSync, async () => {
  await cargarDatos()
  await cargarOffline()
})
watch(online, async (isOnline) => {
  if (isOnline) {
    await new Promise(r => setTimeout(r, 300))
    const hay = (await obtenerPruebasPendientes()).length
    if (hay === 0) { await cargarDatos(); await cargarOffline() }
  } else {
    await cargarOffline()
  }
})
watch(etiquetaModal, async (val) => {
  if (!val) return
  await nextTick()
  try {
    val.cips.forEach((cip, i) => {
      JsBarcode(`#barcode-prueba-${i}`, cip, {
        format: 'CODE128',
        displayValue: false,
        width: 2,
        height: 45,
        margin: 0,
        background: 'transparent',
        lineColor: '#000000',
      })
    })
  } catch (e) {
    console.error('Error dibujando barcode prueba:', e)
  }
})

watch(() => sync.sincronizando.value, async (isSyncing, wasSyncing) => {
  if (wasSyncing && !isSyncing && sync.online.value) {
    // Sincronización terminada, refrescar los datos del backend
    await cargarDatos()
  }
})

// ── Carga ─────────────────────────────────────────────────────────────────────
async function cargarOffline() {
  try {
    const pend = await obtenerPruebasPendientes()
    pruebasOffline.value = pend.filter(p => !p.synced)
  } catch { /* silencioso */ }
}

async function cargarDatos() {
  if (cargando.value) return
  cargando.value = true
  try {
    if (online.value) {
      // ONLINE: descargar del servidor y guardar en cache local
      const data = await pruebasApi.obtenerListaPruebas()
      const lista = Array.isArray(data) ? data : []
      await guardarPruebasListaCache(lista)
    }
  } catch (err: any) {
    console.warn('[PruebasView] No se pudo actualizar lista del servidor. Usando caché local.', err)
    if (online.value && err?.response?.status !== 403) ui.toast('Error al conectar con el servidor', 'error')
  } finally {
    // SIEMPRE leer de IndexedDB para pintar la UI (garantiza consistencia offline)
    const local = await obtenerPruebasListaCache<LotePruebaList>()
    pruebas.value = local
    cargando.value = false
  }
}

onMounted(async () => {
  await cargarDatos()
  await cargarOffline()
})

// ── Filtros ───────────────────────────────────────────────────────────────────
const pruebasFiltradas = computed(() => {
  // 1. Filtrar IPs que están en cola offline para no duplicar
  const estaOffline = new Set(pruebasOffline.value.map(p => p.ip));

  const filtrado = pruebas.value.filter(p => {
    // Regla 1: Ocultar si está en cola de subida
    if (estaOffline.has(p.ip)) return false;

    // Regla 2: Filtro de Estado (EL PUNTO CRÍTICO)
    // Forzamos comparación limpia de strings
    if (filtroEstado.value && filtroEstado.value !== 'Todos') {
      if (p.estado.trim() !== filtroEstado.value.trim()) {
        return false;
      }
    }

    // Regla 3: Búsqueda por IP o CIP_ASIGNADO
    const q = filtroBusqueda.value.trim().toLowerCase();
    if (q) {
      const coincideIP = (p.ip || '').toLowerCase().includes(q);
      const coincideCIP = (p.cip_asignado || '').toLowerCase().includes(q);

      if (!coincideIP && !coincideCIP) return false;
    }

    // Regla 4: Ocultar descartadas a menos que se solicite
    if (!mostrarDescartadas.value && p.descartado) return false;

    return true;
  });

  // Ordenar para que los descartados vayan al final de la lista
  return filtrado.sort((a, b) => {
    if (a.descartado === b.descartado) return 0;
    return a.descartado ? 1 : -1;
  });
})

// ── Selección múltiple de IPs ─────────────────────────────────────────────────
// Solo IPs PENDIENTE (sin fecha_ingreso) son seleccionables para registro en lote
function esPendienteSeleccionable(p: LotePruebaList) {
  return !p.fecha_ingreso && !p.descartado
}

const pendientesSeleccionables = computed(() =>
  pruebasFiltradas.value.filter(p => esPendienteSeleccionable(p))
)

const todosPendientesSeleccionados = computed(() =>
  pendientesSeleccionables.value.length > 0 &&
  pendientesSeleccionables.value.every(p => ipsSeleccionados.value.includes(p.ip))
)

function toggleTodosPendientes(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  if (checked) {
    ipsSeleccionados.value = pendientesSeleccionables.value.map(p => p.ip)
  } else {
    ipsSeleccionados.value = []
  }
}

function irARegistrarLote() {
  if (ipsSeleccionados.value.length === 0) return
  if (ipsSeleccionados.value.length === 1) {
    router.push({ name: 'RegistrarPrueba', params: { ip: ipsSeleccionados.value[0] } })
    return
  }
  router.push({
    name: 'RegistrarPrueba',
    params: { ip: ipsSeleccionados.value[0] },
    query: { ips: ipsSeleccionados.value.join(',') }
  })
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(d: string | null | undefined) {
  if (!d) return '---'
  const hasTz = d.endsWith('Z') || /([+-]\d{2}:\d{2})$/.test(d)
  // Si es "ingenuo" (sin zona), forzamos que lo interprete como hora de Lima (-05:00)
  const iso = hasTz ? d : d + '-05:00'
  return new Date(iso).toLocaleString('es-PE', {
    timeZone: 'America/Lima', day: '2-digit', month: '2-digit',
    year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function fmtLocal(d: string) {
  try { return new Date(d).toLocaleString('es-PE', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' }) }
  catch { return '---' }
}

function estadoClase(estado: string) {
  return { PENDIENTE: 'pendiente', 'EN PROCESO': 'en-proceso', COMPLETADO: 'completo' }[estado] ?? ''
}

function estadoBotonRegistrar(p: LotePruebaList) {
  if (!p.fecha_ingreso) return { texto: 'Iniciar Prueba', disabled: false }
  if (p.estado === 'EN PROCESO') {
    const restante = obtenerTiempoRestante(p.fecha_ingreso)

    if (restante.terminado) {
      return { texto: 'Ver / Editar', disabled: false }
    } else {
      // Formateador dinámico: Muestra "2h 15m rest." o solo "45min rest."
      const textoTiempo = restante.horas > 0
        ? `${restante.horas}h ${restante.minutos}m rest.`
        : `${restante.minutos}min rest.`

      return { texto: `Rodando... (${textoTiempo})`, disabled: true }
    }
  }
  return { texto: 'Ver / Editar', disabled: false }
}

function obtenerTiempoRestante(fechaIngreso: string) {
  const hasTz = fechaIngreso.endsWith('Z') || /([+-]\d{2}:\d{2})$/.test(fechaIngreso)
  const isoString = hasTz ? fechaIngreso : fechaIngreso + '-05:00'

  const msIngreso = new Date(isoString).getTime()
  const msSalida = msIngreso + (48 * 60 * 60 * 1000) // Sumamos 48 horas en milisegundos
  const msAhora = new Date().getTime()

  const msRestantes = msSalida - msAhora

  // Si ya pasó la hora
  if (msRestantes <= 0) {
    return { horas: 0, minutos: 0, terminado: true }
  }

  // Calcular horas y minutos restantes
  const horas = Math.floor(msRestantes / (1000 * 60 * 60))
  const minutos = Math.floor((msRestantes % (1000 * 60 * 60)) / (1000 * 60))

  return { horas, minutos, terminado: false }
}


// ── Acciones ──────────────────────────────────────────────────────────────────
function irARegistrar(ip: string) {
  router.push({ name: 'RegistrarPrueba', params: { ip } })
}

async function etiquetar(ip: string) {
  const prueba = pruebas.value.find(p => p.ip === ip)

  if (!online.value) {
    // Offline: generar CIPs localmente
    if (!prueba?.lote_id) {
      ui.toast(
        'Sin conexión y sin datos del lote en cache. Carga la lista una vez con red para poder etiquetar offline.',
        'error'
      )
      return
    }
    if (prueba.etiquetado) {
      ui.toast('Este lote ya tiene CIPs de recuperación asignados.', 'warning')
      return
    }
    etiquetando.value = ip
    try {
      // Contador independiente: cuántos CIPs de recuperación hay en la cola local
      const totalRec = await contarCipsPruebasPorLote(ip)

      // Respetar configuración de modo: CIP ofuscado vs IP con sufijo
      const par = CONFIG_PRUEBAS.usa_cip
        ? generarParCipsRecuperacion(prueba.lote_id, totalRec, 'RecuperacionInterno')
        : generarParIpRecuperacion(ip, totalRec, 'RecuperacionInterno')
      const { cip1, cip2, correlativo1, correlativo2 } = par

      await encolarCipPruebaOffline({
        offline_id: `cip-prb-${generateUUID()}`,
        ip,
        lote_id: prueba.lote_id,
        codigo_cip1: cip1,
        codigo_cip2: cip2,
        correlativo1,
        correlativo2,
        sufijo: 'R',
        tipo: 'RecuperacionInterno',
        synced: false,
        sync_error: null,
      })

      ui.toast(`Sin red: identificadores generados localmente (${cip1}). Se registrarán al reconectar.`, 'warning')

      // Actualizar la fila en memoria para que el botón cambie a "Ver Etiqueta"
      const idx = pruebas.value.findIndex(p => p.ip === ip)
      if (idx !== -1) {
        pruebas.value[idx] = {
          ...pruebas.value[idx],
          cip_asignado: cip1,
          cips_asignados: [cip1, cip2],
          etiquetado: true,
        }
        // También actualizar el cache local sin proxies reactivos (evita DataCloneError)
        const pruebasLimpias = JSON.parse(JSON.stringify(pruebas.value))
        await guardarPruebasListaCache(pruebasLimpias)
      }

      // Mostrar modal con los CIPs generados para poder imprimir de inmediato
      etiquetaModal.value = { ip, cips: [cip1, cip2] }
    } catch (e: any) {
      ui.toast(e?.message ?? 'Error al generar CIPs offline', 'error')
    } finally {
      etiquetando.value = null
    }
    return
  }

  // ONLINE: comportamiento original
  etiquetando.value = ip
  try {
    const resultado = await pruebasApi.etiquetar(ip)
    ui.toast(`CIP ${resultado.cip} generado para ${ip}`, 'success')
    // Refrescar los datos para obtener todos los cips_asignados
    await cargarDatos()
    // Mostrar modal de etiqueta con los CIPs de la prueba
    const p = pruebas.value.find(x => x.ip === ip)
    if (p && p.cips_asignados?.length) {
      etiquetaModal.value = { ip, cips: p.cips_asignados }
    } else {
      etiquetaModal.value = { ip, cips: [resultado.cip] }
    }
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al etiquetar', 'error')
  } finally {
    etiquetando.value = null
  }
}

function verEtiqueta(prueba: LotePruebaList) {
  if (prueba.cips_asignados?.length) {
    etiquetaModal.value = { ip: prueba.ip, cips: prueba.cips_asignados }
  } else if (prueba.cip_asignado) {
    etiquetaModal.value = { ip: prueba.ip, cips: [prueba.cip_asignado] }
  }
}

// ── Enviar a Laboratorio ──────────────────────────────────────────────────────
function abrirModalEnviarLab(prueba: LotePruebaList) {
  modalEnviarLab.value = prueba
  envioCip.value = prueba.cips_asignados?.[0] ?? ''
}

async function confirmarEnviarLab() {
  if (!modalEnviarLab.value || !envioCip.value) return
  const ip = modalEnviarLab.value.ip
  const subTiposAEnviar = envioSubTiposEfectivos.value
  if (!subTiposAEnviar.length) {
    ui.toast('Todos los análisis ya fueron enviados al laboratorio para este CIP', 'info')
    modalEnviarLab.value = null
    return
  }
  enviandoLab.value = ip
  try {
    await pruebasApi.enviarALaboratorio(ip, subTiposAEnviar, envioCip.value)
    const labels = subTiposAEnviar.join(' + ')
    ui.toast(`✓ Enviado a laboratorio: ${labels} para ${ip}`, 'success')
    modalEnviarLab.value = null
    await cargarDatos()
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al enviar al laboratorio', 'error')
  } finally {
    enviandoLab.value = null
  }
}

// ── Descartar ─────────────────────────────────────────────────────────────────
function abrirModalDescartar(ip: string) {
  modalDescartar.value = ip
  motivoDescarte.value = ''
}

async function confirmarDescartar() {
  if (!modalDescartar.value || !motivoDescarte.value.trim()) return
  descartando.value = true
  try {
    await pruebasApi.descartar(modalDescartar.value, motivoDescarte.value.trim())
    ui.toast('Prueba descartada. El registro se conserva para trazabilidad.', 'success')
    modalDescartar.value = null
    await cargarDatos()
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al descartar la prueba', 'error')
  } finally {
    descartando.value = false
  }
}

// ── Adición ───────────────────────────────────────────────────────────────────
function abrirModalAdicion(prueba: LotePruebaList) {
  modalAdicion.value = prueba
  formAdicion.value = { adicion_nacn: null, adicion_naoh: null }
}

async function confirmarAdicion() {
  if (!modalAdicion.value) return
  registrandoAdicion.value = true
  try {
    await pruebasApi.registrarAdicion(modalAdicion.value.ip, {
      adicion_nacn: formAdicion.value.adicion_nacn,
      adicion_naoh: formAdicion.value.adicion_naoh,
    })
    ui.toast('Adición registrada correctamente', 'success')
    modalAdicion.value = null
    await cargarDatos()
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al registrar adición', 'error')
  } finally {
    registrandoAdicion.value = false
  }
}

function imprimirEtiqueta(e: { ip: string; cips: string[] }) {
  const esDobleColumna = formatoRollo.value === '2col';

  const css = `
    @page { size: ${esDobleColumna ? '4in 1in' : 'auto'}; margin: 0mm; }
    body { font-family: sans-serif; margin: 0; padding: 0; background: white; color: black; }
    #area-impresion-pruebas {
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
    .etiqueta-title { font-size: ${esDobleColumna ? '0.45rem' : '0.65rem'}; font-weight: 900; letter-spacing: 0.05em; margin: 0 0 2px 0; line-height: 1.15; text-align: center; }
    .barcode-visual { width: 95%; max-width: 100%; height: ${esDobleColumna ? '26px' : '45px'}; margin: 1px 0; }
    .etiqueta-codigo { font-family: monospace; font-size: ${esDobleColumna ? '0.85rem' : '1.2rem'}; font-weight: 900; letter-spacing: 0.03em; margin: 2px 0 0 0; line-height: 1.15; }
    .no-print { display: none !important; }
    @media print {
      .etiqueta-print { border: none !important; border-radius: 0; box-shadow: none !important; }
    }
  `

  const htmlEtiquetas = e.cips.map((cip, i) => {
    const svgEl = document.querySelector<SVGElement>(`#barcode-prueba-${i}`)
    const svgHtml = svgEl ? svgEl.outerHTML : ''
    return `
    <div class="etiqueta-print">
      <span class="etiqueta-title">INVERMIN PAITITI S.A.C. - RECUPERACIÓN</span>
      ${svgHtml}
      <span class="etiqueta-codigo">${cip}</span>
    </div>`
  }).join('');

  const html = `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Impresión de Etiquetas Pruebas</title><style>${css}</style></head><body>
    <div id="area-impresion-pruebas">
      ${htmlEtiquetas}
    </div>
    <script>window.addEventListener('load',()=>setTimeout(()=>window.print(),250))<\/script>
  </body></html>`
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 120000)
}
</script>

<style scoped>
.filtros-bar {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

/* ── Estilos de Etiquetas (Impresión Doble) ────────────────────────── */
.control-impresion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 1rem;
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
.grid-etiquetas { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.grid-etiquetas--1col { grid-template-columns: 1fr; max-width: 340px; margin: 0 auto; width: 100%; }

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
  page-break-inside: avoid;
}
.etiqueta-title { font-size: 0.65rem; font-weight: 900; letter-spacing: 0.1em; text-align: center; }
.barcode-visual { transform: scaleY(1.1); margin: 0.5rem 0; width: 95%; height: 45px; }
.etiqueta-codigo { font-family: var(--font-mono); font-size: 1.1rem; font-weight: 900; letter-spacing: 0.05em; }

@media print { .no-print { display: none !important; } }
@media (max-width: 560px) {
  .grid-etiquetas { grid-template-columns: 1fr; }
}

/* ── Offline section ─────────────────────────────────── */
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
.offline-section-titulo { font-family: var(--font-mono); font-size: var(--text-sm); letter-spacing: .18em; color: #f59e0b; }
.offline-section-count  { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted); }
.fila-offline { background: rgba(245,158,11,.04); }
.badge-local {
  font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: .1em;
  background: rgba(245,158,11,.15); color: #f59e0b;
  border: 1px solid rgba(245,158,11,.3); border-radius: 3px;
  padding: 1px 5px; margin-left: .4rem; vertical-align: middle;
}

/* ── Badges ──────────────────────────────────────────── */
.badge-estado { padding: .25rem .6rem; border-radius: var(--radius-sm); font-size: var(--text-xs); font-weight: bold; font-family: var(--font-mono); letter-spacing: .05em; text-transform: uppercase; white-space: nowrap; }
.pendiente   { background: rgba(220,60,60,.1);  color: var(--color-error);   border: 1px solid rgba(220,60,60,.3); }
.en-proceso  { background: rgba(220,160,20,.1); color: var(--color-warning); border: 1px solid rgba(220,160,20,.3); }
.completo    { background: rgba(60,180,80,.1);  color: var(--color-success); border: 1px solid rgba(60,180,80,.3); }
.descartado  { background: rgba(120,120,120,.15); color: var(--color-text-muted); border: 1px solid rgba(120,120,120,.3); }

/* ── Fila descartada ─────────────────────────────────── */
.fila-descartada {
  opacity: 0.55;
  text-decoration: line-through;
  text-decoration-color: rgba(255,255,255,0.2);
}
.fila-descartada .td-mono,
.fila-descartada .td-fecha { text-decoration: line-through; }
.fila-descartada .badge-estado { text-decoration: none; }
.fila-descartada .td-acciones { text-decoration: none; }

/* ── Adición badge ───────────────────────────────────── */
.adicion-badge {
  display: inline-block;
  background: rgba(34,197,94,0.12);
  color: #4ade80;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
}

.adicion-acumulado-info {
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.75rem;
  display: flex;
  gap: 0.75rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}
.adicion-acumulado-info strong {
  color: #4ade80;
}

/* ── Botón descartar ─────────────────────────────────── */
.btn-descartar {
  background: transparent;
  border: 1px solid rgba(220,60,60,.3);
  color: var(--color-error);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-main);
  font-weight: 600;
  transition: all 0.2s;
}
.btn-descartar:hover {
  background: rgba(220,60,60,.1);
  border-color: rgba(220,60,60,.5);
}

/* ── Botón adición ───────────────────────────────────── */
.btn-adicion {
  background: rgba(34,197,94,0.1);
  border: 1px solid rgba(34,197,94,.3);
  color: #4ade80;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-main);
  font-weight: 600;
  transition: all 0.2s;
}
.btn-adicion:hover {
  background: rgba(34,197,94,0.18);
  border-color: rgba(34,197,94,.5);
}

/* ── Botón danger (modal) ────────────────────────────── */
.btn-danger {
  background: rgba(220,60,60,.15);
  border: 1px solid rgba(220,60,60,.4);
  color: #f87171;
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-md);
  font-family: var(--font-main);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-danger:hover:not(:disabled) {
  background: rgba(220,60,60,.25);
}
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Etiqueta CIP (modal) ────────────────────────────── */
.etiqueta-cip {
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  background: #fff;
  color: #000;
  min-width: 200px;
}
.etiqueta-title { font-size: 0.6rem; font-weight: 900; letter-spacing: .1em; }
.etiqueta-codigo { font-family: var(--font-mono); font-size: 1.1rem; font-weight: 900; }
.barcode-container { height: 40px; }

.btn-refresh {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-gold);
  padding: 0.5rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(212, 175, 55, 0.1);
  border-color: var(--color-gold);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animación de rotación para el icono */
.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Ajuste opcional para el layout del header */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* ── Fila seleccionada (batch) ───────────────────────────── */
.fila-seleccionada {
  background: rgba(212, 175, 55, 0.07) !important;
  outline: 1px solid rgba(212, 175, 55, 0.25);
}

/* ── Columna Descartar ───────────────────────────────────── */
.td-descartar {
  white-space: nowrap;
  text-align: center;
  vertical-align: middle;
  max-width: 140px;
}

/* ── Botón Enviar a Lab ──────────────────────────────────── */
.btn-enviar-lab {
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #a5b4fc;
  border-radius: var(--radius-md);
  padding: 0.3rem 0.75rem;
  font-family: var(--font-main);
  font-weight: 700;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}
.btn-enviar-lab:hover:not(:disabled) {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.6);
}
.btn-enviar-lab:disabled { opacity: 0.45; cursor: not-allowed; }

/* ── Opciones de análisis en modal Enviar a Lab ─────────── */
.lab-opcion {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: rgba(255,255,255,0.02);
  cursor: pointer;
  transition: all 0.15s;
}
.lab-opcion:hover {
  border-color: rgba(99, 102, 241, 0.4);
  background: rgba(99, 102, 241, 0.06);
}
.lab-opcion.activo {
  border-color: rgba(99, 102, 241, 0.6);
  background: rgba(99, 102, 241, 0.1);
}
.lab-opcion.deshabilitado {
  opacity: 0.45;
  cursor: not-allowed;
  pointer-events: none;
}

/* ── Badge "Enviado" (todos sub-tipos enviados al lab) ──── */
.badge-lab-enviado {
  display: inline-flex;
  align-items: center;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #a5b4fc;
  border-radius: var(--radius-md);
  padding: 0.25rem 0.65rem;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.03em;
}
</style>
