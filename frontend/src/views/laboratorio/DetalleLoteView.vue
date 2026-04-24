<template>
  <div class="page-container">

    <header class="page-header">
      <div>
        <h1 class="page-title">
          {{ tabActual === 'ley' ? 'Análisis de Ley' : 'Análisis de Recuperación' }}
        </h1>
        <p class="page-subtitle" style="color:var(--color-gold);font-family:var(--font-mono)">
          {{ ipActual }}
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;align-items:center">
        <button class="btn-secondary" @click="toggleTab">
          {{ tabActual === 'ley' ? 'Ver Recuperación ↓' : 'Ver Análisis Ley ↑' }}
        </button>
        <button class="btn-secondary" @click="router.back()">← Volver</button>
      </div>
    </header>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem"></span> Cargando...
    </div>

    <template v-else-if="lote">

      <section class="card">
        <h2 class="card-titulo">DATOS DEL LOTE</h2>
        <div class="detalle-row-grid">
          <div class="detalle-item">
            <span class="di-label">IP:</span>
            <span class="di-value" style="color:var(--color-gold)">{{ lote.ip }}</span>
          </div>
          <div class="detalle-item">
            <span class="di-label">FECHA RECEPCIÓN:</span>
            <span class="di-value">{{ fmt(lote.fecha_recepcion) }}</span>
          </div>
          <div class="detalle-item">
            <span class="di-label">PROVEEDOR:</span>
            <span class="di-value">{{ lote.proveedor }}</span>
          </div>
          <div class="detalle-item">
            <span class="di-label">MATERIAL:</span>
            <span class="di-value">{{ lote.material ?? '-' }}</span>
          </div>
          <div class="detalle-item" v-if="lote.ley_planta != null">
            <span class="di-label">LEY PLANTA (promedio):</span>
            <span class="di-value" style="color:var(--color-gold);font-family:var(--font-mono)">
              {{ Number(lote.ley_planta).toFixed(4) }} oz/TC
            </span>
          </div>
          <div class="detalle-item" v-if="lote.ley_minero != null">
            <span class="di-label">LEY MINERO:</span>
            <span class="di-value" style="font-family:var(--font-mono)">
              {{ Number(lote.ley_minero).toFixed(4) }} oz/TC
            </span>
          </div>
        </div>

        <div v-if="lote.tiene_dirimencia" class="dirimencia-alert" style="margin-top:0.75rem">
          <AlertTriangle :size="16" /> Este lote tiene análisis de dirimencia - prevalece sobre todos los demás
        </div>
      </section>

      <template v-if="tabActual === 'ley'">

        <div class="labs-grid">
          <div
            v-for="(a, i) in lote.analisis_ley"
            :key="a.id"
            class="lab-card"
            :class="{ descartado: !a.vigente }"
          >
            <div class="lab-card-header">
              <span class="lab-titulo">{{ tipoBadge(a.tipo_analisis) }}</span>
              <span v-if="!a.vigente" class="badge-estado pendiente" style="font-size:0.65rem">DESCARTADO</span>
            </div>

            <div class="lab-field"><span class="lf-label">CIP:</span>          <span class="lf-value td-mono" style="color:var(--color-gold)">{{ a.cip ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LABORATORIO:</span>  <span class="lf-value">{{ a.laboratorio }}</span></div>
            <div class="lab-field"><span class="lf-label">FECHA:</span>        <span class="lf-value">{{ fmt(a.fecha_analisis) }}</span></div>
            <div class="lab-field"><span class="lf-label">MALLA +140:</span>   <span class="lf-value">{{ a.ley_grueso }}</span></div>
            <div class="lab-field"><span class="lf-label">MALLA -140:</span>   <span class="lf-value">{{ a.ley_fino }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY OZ/TC:</span>    <span class="lf-value highlight">{{ a.ley_final }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY GR/TM:</span>    <span class="lf-value">{{ a.ley_gr_tm }}</span></div>

            <div v-if="a.certificado_url" class="lab-field">
              <span class="lf-label">CERTIFICADO:</span>
              <a href="#" @click.prevent="verCertificado(a.certificado_url)" class="link-cert">Ver PDF</a>
            </div>

            <div class="lab-card-footer" v-if="!a.eliminado">
              <template v-if="a.vigente">
                <button class="btn-danger-sm" @click="toggleDescartarLey(a.id)" title="Excluir del calculo de ley comercial">
                  Descartar
                </button>
                <label class="btn-secondary-sm" title="Adjuntar certificado">
                  Adjuntar cert.
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="adjuntarCertLey($event, a.id)" />
                </label>
              </template>
              <!-- Eliminar: solo Admin y Gerencia, oculta de TODAS las vistas -->
              <button
                v-if="auth.user?.rol === 'Admin' || auth.user?.rol === 'Gerencia'"
                class="btn-danger-sm"
                style="margin-left:auto;opacity:0.7"
                @click="eliminarLey(a.id)"
                title="Eliminar registro permanentemente de la vista"
              >
                Eliminar
              </button>
            </div>
          </div>

          <div v-if="lote.analisis_ley.length === 0" class="estado-tabla sin-datos">
            Sin análisis de ley registrados
          </div>
        </div>

        <section class="card" v-if="lote.ley_planta != null">
          <h2 class="card-titulo" style="display:flex;justify-content:space-between;align-items:center">
            <span>LEY COMERCIAL (con reglas aplicadas)</span>
            <button
              class="btn-primary"
              style="font-size:0.75rem;padding:0.35rem 0.9rem"
              @click="generarCertificado"
              :disabled="generando"
            >
              <span v-if="generando" class="spinner" style="margin-right:0.4rem"></span>
              Generar certificado PDF
            </button>
          </h2>

          <div v-if="cargandoLeyComercial" class="estado-tabla">
            <span class="spinner" style="margin-right:0.5rem"></span> Calculando...
          </div>

          <template v-else-if="leyComercialCalc">
            <div class="lc-grid">
              <div class="lc-item">
                <span class="lc-label">LEY PLANTA (promedio vigentes):</span>
                <span class="lc-valor mono">{{ Number(lote.ley_planta)?.toFixed(4) }} oz/TC</span>
              </div>
              <div class="lc-item" v-if="lote.ley_minero">
                <span class="lc-label">LEY MINERO:</span>
                <span class="lc-valor mono">{{ Number(lote.ley_minero)?.toFixed(4) }} oz/TC</span>
              </div>
              <div class="lc-item">
                <span class="lc-label">LEY COMERCIAL (a entregar):</span>
                <span class="lc-valor mono gold">{{ leyComercialCalc.ley_comercial.toFixed(4) }} oz/TC</span>
              </div>
              <div class="lc-item" v-if="leyComercialCalc.descuento_aplicado">
                <span class="lc-label">DESCUENTO APLICADO:</span>
                <span class="lc-valor mono">- {{ leyComercialCalc.descuento_aplicado.toFixed(4) }}</span>
              </div>
              <div class="lc-item" v-if="leyComercialCalc.factor_aplicado !== 1">
                <span class="lc-label">FACTOR:</span>
                <span class="lc-valor mono">× {{ leyComercialCalc.factor_aplicado.toFixed(3) }}</span>
              </div>
            </div>

            <div v-if="leyComercialCalc.sin_parametros" class="info-box warning" style="margin-top:0.75rem">
              <AlertTriangle :size="16" /> Sin parámetros comerciales configurados para este proveedor-acopiador.
            </div>
            <div v-if="leyComercialCalc.detalle && !leyComercialCalc.sin_parametros"
              style="font-size:0.75rem;color:var(--color-text-faint);margin-top:0.5rem;font-family:var(--font-mono)">
              Detalle: {{ leyComercialCalc.detalle }}
            </div>
          </template>
          <div v-else class="info-box warning" style="margin-top:0.75rem">
            <AlertTriangle /> No se pudo calcular la ley comercial.
            <button class="btn-secondary" style="margin-left:0.5rem;font-size:0.75rem" @click="recargarLeyComercial">Reintentar</button>
          </div>
        </section>

        <!-- Alerta dirimencia -->
        <div v-if="alertaDirimencia" class="dirimencia-request-alert">
          <AlertTriangle :size="16" /> Diferencia Planta/Minero:
          <strong style="font-family:var(--font-mono)">{{ alertaDirimencia.toFixed(4) }} oz/TC</strong>
          supera el límite (0.10). Se recomienda solicitar dirimencia.
          <button class="btn-warning-sm" style="margin-left:0.75rem" @click="abrirModalDirimencia">
            Solicitar Dirimencia →
          </button>
        </div>

        <div class="acciones-lote" style="display:flex;gap:0.75rem;flex-wrap:wrap">
          <button class="btn-primary" @click="abrirModalAgregarLeyNormal">
            + Registrar nueva ley
          </button>
          <!-- Ley minero: solo si aun no hay una registrada -->
          <button
            v-if="!lote.ley_minero"
            class="btn-secondary"
            @click="modalLeyMinero = true"
          >
            Registrar Ley Minero
          </button>
          <!-- Si ya hay ley minero pero sin dirimencia, mostrar el valor y permitir dirimencia -->
          <span
            v-else-if="lote.ley_minero && !lote.tiene_dirimencia"
            style="font-size:0.85rem;color:var(--color-text-muted);align-self:center"
          >
            Ley minero registrada: <strong style="font-family:var(--font-mono)">
              {{ Number(lote.ley_minero).toFixed(4) }} oz/TC
            </strong>
          </span>
        </div>

        <!-- Modal Ley Minero -->
        <div v-if="modalLeyMinero" class="modal-overlay" @click.self="modalLeyMinero = false">
          <div class="modal modal-sm">
            <div class="modal-header">
              <h2>Registrar Ley Minero</h2>
              <button class="btn-cerrar" @click="modalLeyMinero = false">×</button>
            </div>
            <div class="modal-body">
              <p style="font-size:0.85rem;color:var(--color-text-muted);margin-bottom:1rem">
                Ley declarada por el proveedor. Si difiere más de 0.10 oz/TC
                de la ley de planta, se habilitará la solicitud de dirimencia.
              </p>

              <!-- Zona de carga de certificado (OCR) -->
              <div class="field" style="margin-bottom:0.75rem">
                <label class="field-label">CERTIFICADO (opcional — pre-llena los campos)</label>
                <label
                  class="upload-zone-sm"
                  :class="{ 'uploading': extrayendoMinero }"
                  style="display:flex;align-items:center;gap:0.5rem;padding:0.6rem 0.75rem;border:1px dashed var(--color-border);border-radius:6px;cursor:pointer"
                >
                  <span v-if="extrayendoMinero" class="spinner"></span>
                  <span v-else-if="archivoMinero" style="color:var(--color-success);font-size:0.82rem">
                    ✓ {{ archivoMinero.name }}
                  </span>
                  <span v-else style="font-size:0.82rem;color:var(--color-text-muted)">
                    Subir PDF o imagen del certificado…
                  </span>
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    style="display:none"
                    @change="extraerCertMinero"
                  />
                </label>
                <p v-if="errOcrMinero" style="font-size:0.78rem;color:var(--color-danger);margin-top:0.35rem">
                  {{ errOcrMinero }}
                </p>
              </div>

              <div class="field">
                <label class="field-label">LABORATORIO / ORIGEN</label>
                <input
                  class="field-input"
                  v-model="formLeyMinero.laboratorio"
                  placeholder="Ej: Laboratorio del Minero"
                />
              </div>
              <div class="form-grid" style="grid-template-columns:1fr 1fr">
                <div class="field">
                  <label class="field-label">LEY FINO (Oz/TC)</label>
                  <input type="number" class="field-input" v-model.number="formLeyMinero.ley_fino"
                    step="0.0001" placeholder="0.0000" />
                </div>
                <div class="field">
                  <label class="field-label">LEY GRUESO (Oz/TC)</label>
                  <input type="number" class="field-input" v-model.number="formLeyMinero.ley_grueso"
                    step="0.0001" placeholder="0.0000" />
                </div>
              </div>
              <div class="field">
                <label class="field-label">FECHA ANÁLISIS</label>
                <input type="date" class="field-input" v-model="formLeyMinero.fecha_analisis" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="modalLeyMinero = false">Cancelar</button>
              <button
                class="btn-primary"
                @click="guardarLeyMinero"
                :disabled="guardandoLeyMinero || extrayendoMinero"
              >
                <span v-if="guardandoLeyMinero" class="spinner" style="margin-right:0.4rem"></span>
                Guardar Ley Minero
              </button>
            </div>
          </div>
        </div>

      </template>

      <template v-if="tabActual === 'rec'">

        <div v-if="lote.ley_planta == null" class="info-box warning">
          <AlertTriangle :size="16" /> Sin ley planta disponible. Registre al menos un análisis de ley vigente antes de enviar a recuperación.
        </div>
        <div v-else-if="!cipRecupInterno" class="info-box warning">
          <AlertTriangle :size="16" /> Sin CIP de recuperación. El técnico debe completar pruebas metalúrgicas y etiquetar la muestra.
        </div>

        <div class="labs-grid" v-if="lote.analisis_recuperacion.length > 0">
          <div
            v-for="(a, i) in lote.analisis_recuperacion"
            :key="a.id"
            class="lab-card"
            :class="{ descartado: !a.vigente }"
          >
            <div class="lab-card-header">
              <span class="lab-titulo">RECUPERACIÓN {{ i + 1 }}</span>
              <span class="badge-estado" :class="a.estado === 'PENDIENTE' ? 'pendiente' : 'completo'" style="font-size:0.65rem">
                {{ a.estado }}
              </span>
            </div>

            <div class="lab-field"><span class="lf-label">CIP:</span>           <span class="lf-value td-mono" style="color:var(--color-gold)">{{ a.cip ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LABORATORIO:</span>   <span class="lf-value">{{ a.laboratorio }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY CABEZA:</span>    <span class="lf-value">{{ a.ley_cabeza ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY COLA:</span>      <span class="lf-value">{{ a.ley_cola ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY LÍQUIDO:</span>   <span class="lf-value">{{ a.ley_liquido ?? '-' }}</span></div>
            <div class="lab-field">
              <span class="lf-label">% RECUPERACIÓN:</span>
              <span class="lf-value highlight">{{ a.recuperacion != null ? a.recuperacion + '%' : '-' }}</span>
            </div>

            <div v-if="a.certificado_url" class="lab-field">
              <span class="lf-label">CERTIFICADO:</span>
              <a href="#" @click.prevent="verCertificado(a.certificado_url)" class="link-cert">Ver PDF</a>
            </div>

            <div class="lab-card-footer" v-if="!a.eliminado">
              <template v-if="a.vigente">
                <button class="btn-danger-sm" @click="toggleDescartarLey(a.id)" title="Excluir del calculo de ley comercial">
                  Descartar
                </button>
                <label class="btn-secondary-sm" title="Adjuntar certificado">
                  Adjuntar cert.
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="adjuntarCertLey($event, a.id)" />
                </label>
              </template>
              <!-- Eliminar: solo Admin y Gerencia, oculta de TODAS las vistas -->
              <button
                v-if="auth.user?.rol === 'Admin' || auth.user?.rol === 'Gerencia'"
                class="btn-danger-sm"
                style="margin-left:auto;opacity:0.7"
                @click="eliminarLey(a.id)"
                title="Eliminar registro permanentemente de la vista"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>

        <!-- CIPs enviados a lab externo esperando certificado -->
        <div
          v-if="cipsExternosPendienteCert.length > 0"
          v-for="c in cipsExternosPendienteCert"
          :key="c.codigo_cip"
          class="lab-card"
          style="margin-bottom:0.75rem"
        >
          <div class="lab-card-header">
            <span class="lab-titulo">RECUPERACIÓN EXTERNA - ESPERANDO CERT.</span>
            <span class="badge-estado pendiente" style="font-size:0.65rem">PENDIENTE</span>
          </div>
          <div class="lab-field">
            <span class="lf-label">CIP:</span>
            <span class="lf-value td-mono" style="color:var(--color-gold)">{{ c.codigo_cip }}</span>
          </div>
          <div class="lab-field">
            <span class="lf-label">LABORATORIO:</span>
            <span class="lf-value">{{ c.laboratorio }}</span>
          </div>
          <div class="lab-card-footer">
            <button
              class="btn-primary"
              style="font-size:0.72rem;padding:0.25rem 0.65rem"
              @click="router.push(`/laboratorio/importar-rec/${c.codigo_cip}?ip=${ipActual}&lab=${encodeURIComponent(c.laboratorio || '')}`)"
            >
              Subir certificado →
            </button>
          </div>
        </div>

        <div class="acciones-lote">
          <button
            v-if="lote.ley_planta != null && cipsRecuperacionDisponibles.length > 0"
            class="btn-primary"
            @click="abrirModalRecup"
            :disabled="enviando"
          >
            <span v-if="enviando" class="spinner" style="margin-right:0.4rem"></span>
            Enviar a recuperación
          </button>
          <span v-if="tienePendiente" class="info-inline" style="margin-left:0.5rem">
            <Hourglass :size ="16"/> Análisis pendiente en laboratorio
          </span>
        </div>

        <div v-if="lote.tiene_prueba_pendiente" class="alerta-warning" style="margin-top:0.75rem">
        <TriangleAlert :size="16"/> Este lote tiene una prueba metalúrgica en curso (PENDIENTE o EN PROCESO).
          Revise el módulo de <strong>Pruebas Metalúrgicas</strong> antes de solicitar nuevas muestras.
        </div>
        <button
          class="btn-secondary"
          @click="solicitarRemuestreo"
          :disabled="lote.tiene_prueba_pendiente"
          style="margin-top:0.5rem"
        >
          Solicitar nueva prueba
        </button>

      </template>

    </template>

    <div v-if="modalDescartar" class="modal-overlay" @click.self="modalDescartar = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Descartar análisis</h2>
          <button class="btn-cerrar" @click="modalDescartar = null">×</button>
        </div>
        <div class="modal-body">

          <!-- Preview de impacto en ley planta -->
          <div v-if="modalDescartar.tipo === 'ley' && previewLeyPlantaPostDescarte !== null"
            class="descarte-preview"
            :class="{ 'descarte-preview--sin-cambio': previewLeyPlantaPostDescarte === lote?.ley_planta }"
          >
            <div class="dp-titulo">IMPACTO EN LEY PLANTA</div>
            <div class="dp-row">
              <span class="dp-label">Actual:</span>
              <span class="dp-val">{{ lote?.ley_planta != null ? Number(lote.ley_planta).toFixed(4) : '-' }} oz/TC</span>
            </div>
            <div class="dp-row">
              <span class="dp-label">Tras descarte:</span>
              <span class="dp-val" :class="{ 'dp-val--changed': previewLeyPlantaPostDescarte !== lote?.ley_planta }">
                {{ previewLeyPlantaPostDescarte != null ? previewLeyPlantaPostDescarte.toFixed(4) : 'Sin análisis vigentes' }} oz/TC
              </span>
            </div>
            <div v-if="previewLeyPlantaPostDescarte == null" class="dp-aviso">
              Sin análisis vigentes restantes — la ley planta quedará vacía.
            </div>
          </div>

          <div class="field" style="margin-top:0.75rem">
            <label class="field-label">Justificación (obligatoria):</label>
            <textarea class="field-input" v-model="justificacion" rows="3" placeholder="Ej: Resultado discordante"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalDescartar = null">Cancelar</button>
          <button class="btn-danger" @click="confirmarDescartar" :disabled="!justificacion.trim()">Confirmar descarte</button>
        </div>
      </div>
    </div>


    <div v-if="modalAgregarLey" class="modal-overlay" @click.self="modalAgregarLey = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Registrar Nueva Ley</h2>
          <button class="btn-cerrar" @click="modalAgregarLey = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="cipsDisponiblesLey.length === 0" class="info-box warning">
            <AlertTriangle :size="16" /> No hay CIPs de laboratorio disponibles sin análisis. Es necesario generar nuevas etiquetas o solicitar un remuestreo.
          </div>
          <div v-else class="field">
            <label class="field-label">Seleccione el CIP a analizar:</label>
            <select class="field-select field-input" v-model="cipSeleccionado">
              <option disabled value="">-- Seleccionar CIP --</option>
              <option v-for="c in cipsDisponiblesLey" :key="c.codigo_cip" :value="c.codigo_cip">
                {{ c.codigo_cip }} ({{ c.laboratorio || 'Por definir' }})
              </option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalAgregarLey = false">Cancelar</button>
          <button class="btn-primary" @click="confirmarAgregarLey" :disabled="!cipSeleccionado">Continuar</button>
        </div>
      </div>
    </div>

  </div>

    <!-- Modal selección lab recuperacion -->
    <div v-if="modalRecup" class="modal-overlay" @click.self="modalRecup = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Enviar a Recuperación</h2>
          <button class="btn-cerrar" @click="modalRecup = false">×</button>
        </div>
        <div class="modal-body">
          <div class="field" style="margin-bottom:1rem">
            <label class="field-label">CIP A USAR:</label>
            <select class="field-select field-input" v-model="cipRecupElegido" @change="onCipRecupChange">
              <option v-for="c in cipsRecuperacionDisponibles" :key="c.codigo_cip" :value="c.codigo_cip">
                {{ c.codigo_cip }} - {{ c.tipo_muestra }}
              </option>
            </select>
          </div>
          <div class="field">
            <label class="field-label">LABORATORIO DESTINO:</label>
            <select class="field-select field-input" v-model="labRecupElegida">
              <option v-for="lab in labsRecupDisponibles" :key="lab" :value="lab">{{ lab }}</option>
            </select>
            <p style="font-size:0.7rem;color:var(--color-text-faint);margin-top:0.4rem">
              <span v-if="labRecupElegida === 'Paititi' || labRecupElegida === 'Laboratorio Interno'">
                Laboratorio interno: se creará análisis PENDIENTE para el laboratorista.
              </span>
              <span v-else>
                Lab externo: se marcará el CIP como enviado. Suba el certificado cuando lo reciba.
              </span>
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalRecup = false">Cancelar</button>
          <button class="btn-primary" @click="confirmarEnvioRecuperacion" :disabled="!cipRecupElegido">Confirmar</button>
        </div>
      </div>
    </div>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import type { LoteLabOut } from '@/types/laboratorio'
import { laboratorioApi, type LeyComercialCalc } from '@/api/laboratorio'
import { muestreoApi } from '@/api/muestreo'
import { pruebasApi } from '@/api/pruebas'
import { AlertTriangle, Hourglass, TriangleAlert } from 'lucide-vue-next'

const router = useRouter()
const route  = useRoute()
const store  = useLaboratorioStore()
const ui     = useUiStore()
const auth   = useAuthStore()

const ipActual  = route.params.ip as string
const cargando  = ref(false)
const enviando  = ref(false)
const lote      = ref<LoteLabOut | null>(null)
const tabActual = ref<'ley' | 'rec'>('ley')

// Descarte
const modalDescartar = ref<{ id: number; tipo: 'ley' | 'rec' } | null>(null)
const justificacion  = ref('')

// Agregar Ley
const modalAgregarLey = ref(false)
const cipSeleccionado = ref('')

const cargandoLeyComercial = ref(false)
const leyComercialCalc = ref<LeyComercialCalc | null>(null)
const generando = ref(false)

// Modal seleccion lab para recuperacion
const modalRecup = ref(false)
const cipRecupElegido = ref<string | null>(null)
const labRecupElegida = ref('')
const labsRecupDisponibles = ref<string[]>([])

// Dirimencia / Ley Minero
const modalLeyMinero = ref(false)
const guardandoLeyMinero = ref(false)
const extrayendoMinero = ref(false)
const archivoMinero = ref<File | null>(null)
const errOcrMinero = ref('')
const formLeyMinero = ref({
  laboratorio: '',
  ley_fino: null as number | null,
  ley_grueso: null as number | null,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

const modoModalLey = ref<'normal' | 'dirimencia'>('normal')

// ── Computed: CIPs Disponibles para Ley ──
// Solo traemos los CIPs de tipo Laboratorio que NO existan en el array de analisis_ley
const cipsDisponiblesLey = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(c =>
    c.tipo_muestra === 'Laboratorio' &&
    !lote.value!.analisis_ley.some(a => a.cip === c.codigo_cip)
  )
})

// CIPs de recuperacion disponibles (sin analisis vigente)
const cipsRecuperacionDisponibles = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(c =>
    (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno') &&
    !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente)
  )
})

const cipRecupInterno = computed(() =>
  lote.value?.cips_detalle.find(c => (c.tipo_muestra === 'RecuperacionInterno') && !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente))
)

const tienePendiente = computed(() =>
  lote.value?.analisis_recuperacion.some(a => a.estado === 'PENDIENTE' && a.vigente) ?? false
)

// alerta |ley_planta - ley_minero| > 0.10
const alertaDirimencia = computed(() => {
  if (!lote.value?.ley_planta || !lote.value?.ley_minero) return null
  if (lote.value.tiene_dirimencia) return null  // ya tiene dirimencia, no alertar
  const diff = Math.abs(Number(lote.value.ley_planta) - Number(lote.value.ley_minero))
  return diff > 0.10 ? diff : null
})

// CIPs de recuperación enviados a lab externo que aún no tienen certificado
const internos = new Set(['Paititi', 'Laboratorio Interno'])
const cipsExternosPendienteCert = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(c => {
    const esRec = c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno'
    const tieneLabExterno = c.laboratorio && !internos.has(c.laboratorio)
    const sinVigente = !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente)
    return esRec && tieneLabExterno && sinVigente
  })
})

// Cargar ley comercial
watch([tabActual, lote], async ([tab, l]: ['ley' | 'rec', LoteLabOut | null]) => {
  if (tab === 'ley' && l?.ley_planta != null && !leyComercialCalc.value) {
    cargandoLeyComercial.value = true
    try {
      leyComercialCalc.value = await laboratorioApi.getLeyComercial(ipActual)
    } catch { } finally {
      cargandoLeyComercial.value = false
    }
  }
}, { immediate: true })

async function recargarLeyComercial() {
  if (!lote.value?.ley_planta) return
  cargandoLeyComercial.value = true
  try {
    leyComercialCalc.value = await laboratorioApi.getLeyComercial(ipActual)
  } catch { } finally {
    cargandoLeyComercial.value = false
  }
}

const previewLeyPlantaPostDescarte = computed<number | null>(() => {
  if (!modalDescartar.value || modalDescartar.value.tipo !== 'ley') return null
  if (!lote.value) return null
  const idADescartar = modalDescartar.value.id
  // Análisis vigentes excluyendo el que se va a descartar
  // Solo contamos planta y externo (no minero, no dirimencia) - igual que calcular_ley_planta en backend
  const restantes = lote.value.analisis_ley.filter(
    a => a.vigente && !a.eliminado && a.id !== idADescartar
      && (a.tipo_analisis === 'planta' || a.tipo_analisis === 'externo')
  )
  if (restantes.length === 0) return null
  const promedio = restantes.reduce((acc, a) => acc + Number(a.ley_final), 0) / restantes.length
  return parseFloat(promedio.toFixed(4))
})

async function generarCertificado() {
  generando.value = true
  try {
    await laboratorioApi.descargarCertificadoPdf(ipActual)
  } catch {
    ui.toast('Error al generar certificado PDF', 'error')
  } finally {
    generando.value = false
  }
}

onMounted(async () => {
  cargando.value = true
  ;[lote.value, labsRecupDisponibles.value] = await Promise.all([
    store.cargarDetalleLote(ipActual),
    muestreoApi.listarLaboratorios().catch(() => ['Paititi', 'Minares South S.R.L.', 'El Dorado', 'Otro']),
  ])
  cargando.value = false
})

function toggleTab() {
  tabActual.value = tabActual.value === 'ley' ? 'rec' : 'ley'
}

function fmt(d?: string | null) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function tipoBadge(tipo: string) {
  const m: Record<string, string> = {
    planta: 'LAB INTERNO',
    externo: 'LAB EXTERNO',
    minero: 'LEY MINERO',
    dirimencia: 'DIRIMENCIA',
  }
  return m[tipo] ?? tipo.toUpperCase()
}

// ── Visor Seguro de PDF ──
async function verCertificado(ruta: string | null | undefined) {
  if (!ruta) return
  try {
    const url = await laboratorioApi.obtenerUrlArchivoVirtual(ruta)
    window.open(url, '_blank')
  } catch (error) {
    ui.toast('Error al descargar o visualizar el documento', 'error')
  }
}

// ── Modal Agregar Ley ──
function abrirModalAgregarLey() {
  cipSeleccionado.value = '' // Reiniciamos el estado del select
  modalAgregarLey.value = true
}

function confirmarAgregarLey() {
  if (!cipSeleccionado.value) return
  const tipoPorUrl = modoModalLey.value === 'dirimencia' ? 'dirimencia' : 'externo'
  if (store.puedeImportarCert) {
    router.push(
      `/laboratorio/importar-ley/${cipSeleccionado.value}?ip=${ipActual}&tipo=${tipoPorUrl}`
    )
  } else {
    router.push(`/laboratorio/ley/${cipSeleccionado.value}?tipo=${tipoPorUrl}`)
  }
}

function abrirModalAgregarLeyNormal() {
  modoModalLey.value = 'normal'
  cipSeleccionado.value = ''
  modalAgregarLey.value = true
}

function abrirModalDirimencia() {
  modoModalLey.value = 'dirimencia'
  cipSeleccionado.value = ''
  modalAgregarLey.value = true
}

// ── Descartar ──
function toggleDescartarLey(id: number) {
  justificacion.value = ''
  modalDescartar.value = { id, tipo: 'ley' }
}
function toggleDescartarRec(id: number) {
  justificacion.value = ''
  modalDescartar.value = { id, tipo: 'rec' }
}

async function confirmarDescartar() {
  if (!modalDescartar.value) return
  const { id, tipo } = modalDescartar.value
  const j = justificacion.value.trim()
  if (!j) return

  const ok = tipo === 'ley'
    ? await store.descartarLey(id, j)
    : await store.descartarRecuperacion(id, j)

  if (ok) {
    modalDescartar.value = null
    lote.value = await store.cargarDetalleLote(ipActual)
  }
}

async function eliminarLey(id: number) {
  const ok = await store.eliminarLey(id)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

async function eliminarRecuperacion(id: number) {
  const ok = await store.eliminarRecuperacion(id)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

// ── Adjuntar certificados ──
async function adjuntarCertLey(e: Event, analisisId: number) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const ok = await store.subirCertificadoLey(analisisId, file)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

async function adjuntarCertRec(e: Event, analisisId: number) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const ok = await store.subirCertificadoRecuperacion(analisisId, file)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

// ── Modal recuperacion ──
function abrirModalRecup() {
  cipRecupElegido.value = cipsRecuperacionDisponibles.value[0]?.codigo_cip ?? null
  labRecupElegida.value = cipsRecuperacionDisponibles.value[0]?.laboratorio ?? labsRecupDisponibles.value[0] ?? 'Paititi'
  modalRecup.value = true
}

function onCipRecupChange() {
  const cip = cipsRecuperacionDisponibles.value.find(c => c.codigo_cip === cipRecupElegido.value)
  labRecupElegida.value = cip?.laboratorio ?? labsRecupDisponibles.value[0] ?? 'Paititi'
}

async function confirmarEnvioRecuperacion() {
  if (!cipRecupElegido.value) return
  enviando.value = true
  modalRecup.value = false
  const esInterno = labRecupElegida.value === 'Paititi' || labRecupElegida.value === 'Laboratorio Interno'
  if (esInterno) {
    await store.enviarRecuperacion(ipActual, { cip: cipRecupElegido.value, laboratorio: labRecupElegida.value })
  } else {
    // Externo: solo actualizar lab destino en el CIP
    const cipObj = lote.value?.cips_detalle.find(c => c.codigo_cip === cipRecupElegido.value)
    if (cipObj) {
      try {
        // Necesitamos el id numerico del CIP - viene de cips_detalle que no tiene id
        // Recargamos cips para obtenerlo y hacer el patch
        const cips = await muestreoApi.obtenerEtiquetas(ipActual)
        const cipConId = cips.find(c => c.codigo_cip === cipRecupElegido.value)
        if (cipConId) await muestreoApi.actualizarLaboratorioCip(cipConId.id, labRecupElegida.value)
        ui.toast(`CIP marcado para ${labRecupElegida.value}. Suba el certificado cuando lo reciba.`, 'info')
      } catch {
        ui.toast('Error al asignar laboratorio', 'error')
      }
    }
  }
  enviando.value = false
  lote.value = await store.cargarDetalleLote(ipActual)
}

async function subirCertExterno(e: Event) {
  ui.toast('Para registrar recuperación externa, use el formulario de laboratorio con el CIP externo', 'info')
}

async function solicitarRemuestreo() {
  const ok = await ui.showConfirm({
    title: 'Solicitar Remuestreo',
    message: `Se creará un nuevo registro de prueba metalúrgica para ${ipActual}. ` +
             'El registro anterior se conserva para auditoría. El técnico deberá completar los parámetros y etiquetar un nuevo CIP. ¿Confirmar?',
    confirmLabel: 'Solicitar',
  })
  if (!ok) return
  try {
    await pruebasApi.solicitarRemuestreo(ipActual)
    ui.toast('Remuestreo solicitado. El lote aparece en Pruebas Metalúrgicas.', 'success')
    lote.value = await store.cargarDetalleLote(ipActual)
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al solicitar remuestreo', 'error')
  }
}

// ── Modal Ley Minero (Dirimencia) ──
async function extraerCertMinero(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  archivoMinero.value = file
  errOcrMinero.value = ''
  extrayendoMinero.value = true
  try {
    const res = await laboratorioApi.extraerCertificadoLey(file, formLeyMinero.value.laboratorio)
    if (res.ley_fino != null) formLeyMinero.value.ley_fino = res.ley_fino
    if (res.ley_grueso != null) formLeyMinero.value.ley_grueso = res.ley_grueso
    if (res.fecha_analisis) formLeyMinero.value.fecha_analisis = res.fecha_analisis
    if (res.laboratorio && !formLeyMinero.value.laboratorio) formLeyMinero.value.laboratorio = res.laboratorio
    if (!res.ley_fino && !res.ley_grueso) errOcrMinero.value = 'No se pudieron extraer las leyes. Ingrese los valores manualmente.'
  } catch {
    errOcrMinero.value = 'Error al procesar el certificado. Ingrese los valores manualmente.'
  } finally {
    extrayendoMinero.value = false
  }
}

async function guardarLeyMinero() {
  if (!formLeyMinero.value.laboratorio.trim()) {
    ui.toast('Ingrese el nombre del laboratorio o minero', 'error')
    return
  }
  if (formLeyMinero.value.ley_fino == null || formLeyMinero.value.ley_grueso == null) {
    ui.toast('Ingrese ambas leyes (fino y grueso)', 'error')
    return
  }
  guardandoLeyMinero.value = true
  try {
    const nuevo = await laboratorioApi.registrarLeyPorIP(ipActual, {
      tipo_analisis: 'minero',
      laboratorio: formLeyMinero.value.laboratorio,
      ley_fino: formLeyMinero.value.ley_fino,
      ley_grueso: formLeyMinero.value.ley_grueso,
      fecha_analisis: formLeyMinero.value.fecha_analisis,
    })
    if (archivoMinero.value) {
      await laboratorioApi.subirCertificadoLey(nuevo.id, archivoMinero.value)
    }
    ui.toast('Ley minero registrada', 'success')
    modalLeyMinero.value = false
    archivoMinero.value = null
    errOcrMinero.value = ''
    lote.value = await store.cargarDetalleLote(ipActual)
    leyComercialCalc.value = null
    await recargarLeyComercial()
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al registrar ley minero', 'error')
  } finally {
    guardandoLeyMinero.value = false
  }
}

</script>

<style scoped>
.detalle-row-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.detalle-item { display: flex; flex-direction: column; gap: 0.15rem; }

.di-label {
  font-size: 0.68rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.di-value { font-size: var(--text-md); color: var(--color-text); }

.labs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1rem;
}

.lab-card {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 1rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: rgba(255,255,255,0.02);
}

.lab-card.descartado { opacity: 0.45; border-style: dashed; }

.lab-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.lab-titulo {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  color: var(--color-text-muted);
  text-transform: uppercase;
}

.lab-field { display: flex; justify-content: space-between; align-items: center; }

.lf-label { font-size: 0.68rem; color: var(--color-text-faint); font-family: var(--font-mono); letter-spacing: 0.05em; }
.lf-value { font-family: var(--font-mono); color: var(--color-text-muted); font-size: var(--text-md); }
.lf-value.highlight { color: var(--color-gold); font-size: var(--text-lg); }

.lab-card-footer {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.btn-danger-sm {
  font-size: 0.72rem;
  padding: 0.25rem 0.65rem;
  background: rgba(239,68,68,0.12);
  color: #f87171;
  border: 1px solid rgba(239,68,68,0.3);
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary-sm {
  font-size: 0.72rem;
  padding: 0.25rem 0.65rem;
  background: transparent;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
}

.link-cert { font-size: 0.75rem; color: var(--color-gold); text-decoration: underline; cursor: pointer; }

.acciones-lote {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
  margin: 0.5rem 0 1.5rem;
}

.info-inline {
  font-size: var(--text-sm);
  color: var(--color-text-faint);
  font-family: var(--font-mono);
}

.dirimencia-alert {
  background: rgba(168,85,247,0.12);
  border: 1px solid rgba(168,85,247,0.4);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  color: #c084fc;
  font-size: var(--text-sm);
}

.info-box {
  border-radius: 6px;
  padding: 0.75rem 1rem;
  font-size: var(--text-sm);
  margin-bottom: 1rem;
}

.info-box.warning {
  background: rgba(234,179,8,0.08);
  border: 1px solid rgba(234,179,8,0.3);
  color: #fbbf24;
}

.lc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.lc-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.lc-label {
  font-size: 0.68rem;
  color: var(--color-text-faint);
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.lc-valor {
  font-size: var(--text-md);
  color: var(--color-text);
}

.lc-valor.mono { font-family: var(--font-mono); }
.lc-valor.gold { color: var(--color-gold); font-size: var(--text-lg); font-weight: 600; }

.dirimencia-request-alert {
  background: rgba(234,179,8,0.10);
  border: 1px solid rgba(234,179,8,0.45);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  color: #fbbf24;
  font-size: var(--text-sm);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.btn-warning-sm {
  font-size: 0.72rem;
  padding: 0.25rem 0.65rem;
  background: rgba(234,179,8,0.15);
  color: #fbbf24;
  border: 1px solid rgba(234,179,8,0.4);
  border-radius: 4px;
  cursor: pointer;
}
</style>
