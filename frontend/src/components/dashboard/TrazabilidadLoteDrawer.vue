<template>
  <Teleport to="body">
    <!-- Overlay -->
    <Transition name="drawer-fade">
      <div v-if="open" class="trz-overlay" @click.self="$emit('close')" />
    </Transition>

    <!-- Panel -->
    <Transition name="drawer-slide">
      <aside
        v-if="open"
        class="trz-panel"
        role="dialog"
        aria-modal="true"
        aria-label="Trazabilidad del lote"
      >
        <!-- ════ HEADER ════ -->
        <header class="trz-header">
          <div class="trz-header-left">
            <div class="trz-title-row">
              <span class="trz-ip">{{ data?.ip ?? ip ?? '…' }}</span>
              <span
                v-if="data"
                class="trz-pill"
                :class="`pill-${(data.estado ?? '').toLowerCase()}`"
              >{{ data.estado }}</span>
              <span v-if="data?.volado"    class="trz-pill pill-volado">VOLADO</span>
              <span v-if="data?.dirimencia" class="trz-pill pill-dirim">DIRIM</span>
            </div>
            <p class="trz-subtitle">
              <strong>{{ data?.proveedor ?? '…' }}</strong>
              <span v-if="data?.ruc_proveedor" class="muted"> · {{ data.ruc_proveedor }}</span>
              <span v-if="data?.acopiador"     class="muted"> · Acop: {{ data.acopiador }}</span>
            </p>
          </div>
          <button class="trz-close-btn" @click="$emit('close')" title="Cerrar"><X :size="14" /></button>
        </header>

        <!-- ════ TIMELINE ════ -->
        <div class="trz-timeline-bar">
          <div
            v-for="(node, i) in timeline"
            :key="node.key"
            class="tl-node"
            :class="node.status"
          >
            <div class="tl-connector" v-if="i > 0" :class="timeline[i - 1]?.status === 'done' && node.status === 'done' ? 'done' : ''" />
            <div class="tl-dot" :title="node.label">
              <component :is="node.icon" :size="11" />
            </div>
            <span class="tl-label">{{ node.label }}</span>
          </div>
        </div>

        <!-- ════ SCROLL BODY ════ -->
        <div class="trz-scroll">

          <!-- Spinner -->
          <div v-if="loading" class="trz-center">
            <span class="ring" /><span class="muted">Cargando trazabilidad…</span>
          </div>

          <!-- Error -->
          <div v-else-if="error" class="trz-center err">{{ error }}</div>

          <!-- Contenido -->
          <template v-else-if="data">

            <!-- 1 · RECEPCIÓN -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('recepcion')">
                <span class="head-icon"><Truck :size="13"/></span>
                <span class="head-title">Recepción</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.recepcion }" :size="14"/>
              </div>
              <div v-show="open_sections.recepcion" class="trz-card-body">
                <div class="g2">
                  <Field label="Placa"           :val="data.sesion.placa" mono />
                  <Field label="Conductor"       :val="data.sesion.conductor" />
                  <Field label="Transportista"   :val="data.sesion.transportista" />
                  <Field label="Material"        :val="data.tipo_material" />
                  <Field label="Guía remisión"   :val="data.sesion.guia_remision" mono />
                  <Field label="Guía transporte" :val="data.sesion.guia_transporte" mono />
                  </div>
                <ResponsableRow :accion="data.sesion.registro" />
              </div>
            </section>

            <!-- 2 · PESAJE -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('pesaje')">
                <span class="head-icon"><Scale :size="13"/></span>
                <span class="head-title">Pesaje</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.pesaje }" :size="14"/>
              </div>
              <div v-show="open_sections.pesaje" class="trz-card-body">
                <template v-if="lastPesaje">
                  <!-- Pesaje válido (el más reciente) -->
                  <div class="g3">
                    <Field label="Ticket"       :val="lastPesaje.numero_ticket" mono />
                    <Field label="Sacos"        :val="lastPesaje.sacos?.toString()" mono />
                    <Field label="Granel"       :val="lastPesaje.granel ? 'Sí' : 'No'" />
                    <Field label="Peso inicial" :val="fmt3(lastPesaje.peso_inicial) + ' TM'" mono />
                    <Field label="Peso final"   :val="fmt3(lastPesaje.peso_final)   + ' TM'" mono />
                    <Field label="Peso neto"    :val="fmt3(lastPesaje.peso_neto)    + ' TM'" mono gold />
                    <Field label="Inicio"       :val="fmtDt(lastPesaje.fecha_inicio)" mono />
                    <Field label="Fin"          :val="fmtDt(lastPesaje.fecha_fin)" />
                  </div>
                  <div v-if="pesajeEditado" class="warn-row">
                    <AlertTriangle :size="12" />
                    <span>Peso editado<span v-if="lastPesaje.es_manual"> manualmente — {{ lastPesaje.justificacion_manual ?? 'Sin justificación' }}</span></span>
                  </div>
                  <ResponsableRow :accion="lastPesaje.registro" />

                  <!-- Historial de pesajes anteriores (solo si hay más de 1) -->
                  <template v-if="data.pesajes.length > 1">
                    <div class="hist-header">
                      <span>Historial de correcciones ({{ data.pesajes.length - 1 }})</span>
                    </div>
                    <div
                      v-for="(p, idx) in data.pesajes.slice(0, -1)"
                      :key="idx"
                      class="sub-card sub-card--dim"
                    >
                      <div class="sub-header">
                        <span class="pill pill-dim">anterior</span>
                        <span class="muted mono" style="font-size:0.65rem">{{ fmtDt(p.registro.fecha) }}</span>
                      </div>
                      <div class="g3">
                        <Field label="Ticket"       :val="p.numero_ticket" mono />
                        <Field label="Peso inicial" :val="fmt3(p.peso_inicial) + ' TM'" mono />
                        <Field label="Peso final"   :val="fmt3(p.peso_final)   + ' TM'" mono />
                        <Field label="Peso neto"    :val="fmt3(p.peso_neto)    + ' TM'" mono />
                      </div>
                      <div v-if="p.es_manual" class="warn-row">
                        <AlertTriangle :size="12" />
                        <span>Manual — {{ p.justificacion_manual ?? 'Sin justificación' }}</span>
                      </div>
                      <ResponsableRow :accion="p.registro" label="Registrado por" />
                    </div>
                  </template>
                </template>
                <div v-else class="empty-state-row">
                  <Clock :size="12" />
                  <span>Pendiente de pesaje</span>
                </div>
              </div>
            </section>

            <!-- 3 · MUESTREO -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('muestreo')">
                <span class="head-icon"><Droplets :size="13"/></span>
                <span class="head-title">Muestreo</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.muestreo }" :size="14"/>
              </div>
              <div v-show="open_sections.muestreo" class="trz-card-body">
                <template v-if="data.muestreos.length">
                  <!-- Resumen del intento definitivo -->
                  <div v-if="lastMuestreo" class="summary-row">
                    <span class="sr-lbl">TMS definitivo</span>
                    <span class="sr-val mono gold">{{ lastMuestreo.tms_calculado?.toFixed(3) ?? '—' }} TM</span>
                    <span class="sr-sep">·</span>
                    <span class="sr-lbl">H₂O</span>
                    <span class="sr-val mono">{{ lastMuestreo.porcentaje_humedad?.toFixed(2) ?? '—' }}%</span>
                  </div>
                  <div
                    v-for="m in data.muestreos" :key="m.intento"
                    class="sub-card"
                    :class="{ 'sub-card--gold': m.intento === data.muestreos.length }"
                  >
                    <div class="sub-header">
                      <b>Intento {{ m.intento }}</b>
                      <span v-if="m.intento === data.muestreos.length" class="pill pill-ok"><Check :size="9"/> definitivo</span>
                      <span v-else class="pill pill-dim">fallido</span>
                    </div>
                    <div class="g3">
                      <Field label="Peso húmedo" :val="fmt3(m.peso_humedo) + ' kg'" mono />
                      <Field label="Peso seco"   :val="fmt3(m.peso_seco)   + ' kg'" mono />
                      <Field label="% Humedad"   :val="(m.porcentaje_humedad?.toFixed(2) ?? '—') + '%'" mono gold />
                      <Field label="TMS calc."   :val="(m.tms_calculado?.toFixed(3) ?? '—') + ' TM'" mono />
                      <Field label="Fecha"       :val="fmtDt(m.registro.fecha)" mono />
                      <Field label="Observaciones" :val="m.observaciones" class="g-span3" />
                    </div>
                    <ResponsableRow :accion="m.registro" />
                  </div>
                </template>
                <div v-else class="empty-state-row">
                  <Clock :size="12" />
                  <span>Pendiente de muestreo</span>
                </div>
              </div>
            </section>

            <!-- 4 · PRUEBAS METALÚRGICAS -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('prueba')">
                <span class="head-icon"><FlaskConical :size="13"/></span>
                <span class="head-title">Pruebas metalúrgicas</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.prueba }" :size="14"/>
              </div>
              <div v-show="open_sections.prueba" class="trz-card-body">
                <template v-if="data.prueba_metalurgica">
                  <div class="g3">
                    <Field label="CIP"           :val="data.prueba_metalurgica.cip" mono gold class="g-span2" />
                    <Field label="Malla"          :val="(data.prueba_metalurgica.malla_porcentaje?.toFixed(2) ?? '—') + '%'" mono />
                    <Field label="% NaCN"         :val="(data.prueba_metalurgica.porcentaje_nacn?.toFixed(2) ?? '—') + '%'" mono />
                    <Field label="pH inicial"     :val="data.prueba_metalurgica.ph_inicial?.toFixed(2)" mono />
                    <Field label="pH final"       :val="data.prueba_metalurgica.ph_final?.toFixed(2)" mono />
                    <Field label="Adic. NaCN"     :val="(data.prueba_metalurgica.adicion_nacn?.toFixed(4) ?? '—') + ' g'" mono />
                    <Field label="Adic. NaOH"     :val="(data.prueba_metalurgica.adicion_naoh?.toFixed(4) ?? '—') + ' g'" mono />
                    <Field label="Gasto AgNO₃"    :val="(data.prueba_metalurgica.gasto_agno3?.toFixed(4) ?? '—') + ' ml'" mono />
                    <Field label="Ingreso a lab"  :val="fmtDt(data.prueba_metalurgica.fecha_ingreso)" mono />
                    <Field label="Salida estimada" :val="fmtDt(data.prueba_metalurgica.fecha_salida)" mono />
                  </div>
                  <ResponsableRow :accion="data.prueba_metalurgica.registro" />
                </template>
                <div v-else class="empty-state-row">
                  <Clock :size="12" />
                  <span>Pendiente de pruebas metalúrgicas</span>
                </div>
              </div>
            </section>

            <!-- 5 · ANÁLISIS DE LEY -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('ley')">
                <span class="head-icon"><BarChart2 :size="13"/></span>
                <span class="head-title">Análisis de ley</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.ley }" :size="14"/>
              </div>
              <div v-show="open_sections.ley" class="trz-card-body">
                <template v-if="data.analisis_ley.length">
                  <div
                    v-for="a in data.analisis_ley" :key="a.id"
                    class="sub-card"
                    :class="{ 'sub-card--dim': !a.vigente }"
                  >
                    <div class="sub-header">
                      <span class="pill pill-tipo">{{ a.tipo_analisis.toUpperCase() }}</span>
                      <b>{{ a.laboratorio }}</b>
                      <span v-if="a.vigente"  class="pill pill-ok"><Check :size="9"/> vigente</span>
                      <span v-else            class="pill pill-dim">descartado</span>
                      <span class="ml-auto muted" style="font-size:0.65rem">
                        {{ a.registro.por?.nombre_completo ?? '—' }}
                      </span>
                    </div>
                    <div class="g3">
                      <Field v-if="a.cip" label="CIP"         :val="a.cip"                            mono gold class="g-span2" />
                      <Field label="Ley final"  :val="(a.ley_final?.toFixed(4) ?? '—') + ' Oz/TC'" mono />
                      <Field label="Ley gr/TM"  :val="(a.ley_gr_tm?.toFixed(3) ?? '—') + ' g/T'"  mono />
                      <Field label="Material"   :val="a.material" />
                      <Field label="Origen"     :val="a.origen_datos" />
                      <Field label="Fecha"      :val="a.fecha_analisis ?? '—'" mono />
                      <Field v-if="a.certificado_url" label="Certificado" :val="'Disponible'" />
                    </div>
                    <ResponsableRow :accion="a.registro" label="Registrado por" />
                    <div v-if="!a.vigente && a.descarte" class="descarte-row">
                      <Trash2 :size="12" />
                      <span class="lbl">Descartado por</span>
                      <span class="descarte-name">{{ a.descarte.por?.nombre_completo ?? '—' }}</span>
                      <span class="descarte-date">{{ fmtDt(a.descarte.fecha) }}</span>
                      <span v-if="a.justificacion_descarte" class="italic descarte-just">{{ a.justificacion_descarte }}</span>
                    </div>
                  </div>
                </template>
                <div v-else class="empty-state-row">
                  <Clock :size="12" />
                  <span>Pendiente de análisis de ley</span>
                </div>
              </div>
            </section>

            <!-- 6 · RECUPERACIÓN -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('rec')">
                <span class="head-icon"><TrendingUp :size="13"/></span>
                <span class="head-title">Recuperación</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.rec }" :size="14"/>
              </div>
              <div v-show="open_sections.rec" class="trz-card-body">
                <template v-if="data.analisis_recuperacion.length">
                  <div
                    v-for="a in data.analisis_recuperacion" :key="a.id"
                    class="sub-card"
                    :class="{ 'sub-card--dim': !a.vigente }"
                  >
                    <div class="sub-header">
                      <b>{{ a.laboratorio }}</b>
                      <span class="pill" :class="estadoRecTag(a.estado)">{{ a.estado }}</span>
                      <span v-if="a.vigente"  class="pill pill-ok"><Check :size="9"/> vigente</span>
                      <span v-else            class="pill pill-dim">descartado</span>
                      <span class="ml-auto muted" style="font-size:0.65rem">
                        {{ a.registro.por?.nombre_completo ?? '—' }}
                      </span>
                    </div>
                    <div class="g3">
                      <Field v-if="a.cip" label="CIP"          :val="a.cip"                          mono gold class="g-span2" />
                      <Field label="Ley cabeza"   :val="a.ley_cabeza?.toFixed(4)"  mono />
                      <Field label="Ley cola"     :val="a.ley_cola?.toFixed(4)"    mono />
                      <Field label="Ley líquido"  :val="a.ley_liquido?.toFixed(4)" mono />
                      <Field label="% Recup."     :val="(a.recuperacion?.toFixed(2) ?? '—') + '%'" mono gold />
                      <Field label="Origen"       :val="a.origen_datos" />
                      <Field label="Fecha"        :val="a.fecha_analisis ?? '—'"   mono />
                    </div>
                    <ResponsableRow :accion="a.registro" label="Registrado por" />
                    <div v-if="!a.vigente && a.descarte" class="descarte-row">
                      <Trash2 :size="12" />
                      <span class="lbl">Descartado por</span>
                      <span class="descarte-name">{{ a.descarte.por?.nombre_completo ?? '—' }}</span>
                      <span class="descarte-date">{{ fmtDt(a.descarte.fecha) }}</span>
                      <span v-if="a.justificacion_descarte" class="italic descarte-just">{{ a.justificacion_descarte }}</span>
                    </div>
                  </div>
                </template>
                <div v-else class="empty-state-row">
                  <Clock :size="12" />
                  <span>Pendiente de recuperación</span>
                </div>
              </div>
            </section>

            <!-- 7 · RUMA / CAMPAÑA -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('ruma')">
                <span class="head-icon"><Layers :size="13"/></span>
                <span class="head-title">Ruma / Campaña</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.ruma }" :size="14"/>
              </div>
              <div v-show="open_sections.ruma" class="trz-card-body">
                <template v-if="data.ruma">
                  <div class="g2">
                    <Field label="Código ruma"    :val="data.ruma.codigo"                     mono />
                    <Field label="Estado ruma"    :val="data.ruma.estado" />
                    <Field label="Campaña"        :val="data.ruma.campana"                    mono />
                    <Field label="Fecha creación" :val="data.ruma.fecha_creacion ?? '—'"      mono />
                  </div>
                </template>
                <div v-else class="empty-state-row">
                  <Clock :size="12" />
                  <span>Pendiente de asignación a ruma</span>
                </div>
              </div>
            </section>

            <!-- 8 · LIQUIDACIÓN -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('liq')">
                <span class="head-icon"><FileText :size="13"/></span>
                <span class="head-title">Liquidación</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.liq }" :size="14"/>
              </div>
              <div v-show="open_sections.liq" class="trz-card-body">
                <template v-if="data.liquidacion">
                  <div class="g3">
                    <Field label="N° Liquidación" :val="data.liquidacion.numero_liquidacion" mono class="g-span2" />
                    <Field label="Estado"         :val="data.liquidacion.estado" />
                    <Field label="Spot USD"       :val="'$' + fmtNum(data.liquidacion.precio_oro_usd)" mono />
                    <Field label="Total USD"      :val="'$' + fmtNum(data.liquidacion.valor_total_usd)" mono gold />
                    <Field label="Fino rec."      :val="data.liquidacion.fino_recuperable?.toFixed(4)" mono />
                    <Field label="Ley comercial"  :val="data.liquidacion.ley_comercial?.toFixed(4)" mono />
                    <Field label="Dirimencia"     :val="data.liquidacion.usa_dirimencia ? 'Sí' : 'No'" />
                  </div>
                  <ResponsableRow :accion="data.liquidacion.generacion" label="Generado por" />
                  <ResponsableRow v-if="data.liquidacion.cierre" :accion="data.liquidacion.cierre" label="Cerrado por" />
                </template>
                <div v-else class="empty-state-row">
                  <Clock :size="12" />
                  <span>Pendiente de liquidación</span>
                </div>
              </div>
            </section>

            <!-- 9 · AUDITORÍA -->
            <section class="trz-card">
              <div class="trz-card-head" @click="toggleSection('auditoria')">
                <span class="head-icon"><ShieldCheck :size="13"/></span>
                <span class="head-title">Auditoría</span>
                <ChevronDown class="head-caret" :class="{ rotated: open_sections.auditoria }" :size="14"/>
              </div>
              <div v-show="open_sections.auditoria" class="trz-card-body">
                <template v-if="data.auditoria">
                  <ResponsableRow
                    :accion="data.auditoria.registro_lote"
                    label="Lote registrado por"
                    placeholder="—"
                  />
                  <ResponsableRow
                    :accion="data.auditoria.habilitacion_ruma"
                    label="Habilitado para ruma por"
                    placeholder="Pendiente de habilitar"
                  />
                  <ResponsableRow
                    :accion="data.auditoria.cambio_estado"
                    label="Último cambio de estado por"
                    placeholder="Sin cambios de estado"
                  />
                  <!-- Resumen rápido de datos clave -->
                  <div class="audit-summary">
                    <div class="audit-item">
                      <span class="audit-lbl">Peso neto</span>
                      <span class="audit-val gold">
                        <template v-if="lastPesaje">
                          <span class="val-num">{{ fmt3(lastPesaje.peso_neto) }}</span>
                          <span class="val-unit"> TM</span>
                        </template>
                        <template v-else>—</template>
                      </span>
                    </div>
                    <div class="audit-item">
                      <span class="audit-lbl">TMS</span>
                      <span class="audit-val gold">
                        <template v-if="lastMuestreo">
                          <span class="val-num">{{ lastMuestreo.tms_calculado?.toFixed(3) ?? '—' }}</span>
                          <span class="val-unit"> TM</span>
                        </template>
                        <template v-else>—</template>
                      </span>
                    </div>
                    <div class="audit-item">
                      <span class="audit-lbl">Muestreos</span>
                      <span class="audit-val">
                        <span class="val-num">{{ data.muestreos.length }}</span>
                      </span>
                    </div>
                    <div class="audit-item">
                      <span class="audit-lbl">Análisis ley</span>
                      <span class="audit-val">
                        <span class="val-num">{{ data.analisis_ley.length }}</span>
                      </span>
                    </div>
                    <div class="audit-item">
                      <span class="audit-lbl">Análisis rec.</span>
                      <span class="audit-val">
                        <span class="val-num">{{ data.analisis_recuperacion.length }}</span>
                      </span>
                    </div>
                    <div class="audit-item">
                      <span class="audit-lbl">Peso editado</span>
                      <span class="audit-val" :class="pesajeEditado ? 'gold' : 'muted'">
                        <span class="val-num">{{ pesajeEditado ? 'Sí' : 'No' }}</span>
                      </span>
                    </div>
                    <div class="audit-item">
                      <span class="audit-lbl">Hab. ruma</span>
                      <span class="audit-val" :class="data.habilitado_ruma ? 'gold' : 'muted'">
                        <span class="val-num">{{ data.habilitado_ruma ? 'Sí' : 'No' }}</span>
                      </span>
                    </div>
                    <div class="audit-item">
                      <span class="audit-lbl">Dirimencia</span>
                      <span class="audit-val" :class="data.dirimencia ? 'gold' : 'muted'">
                        <span class="val-num">{{ data.dirimencia ? 'Sí' : 'No' }}</span>
                      </span>
                    </div>
                  </div>
                </template>
                <div v-else class="empty-state-row">
                  <AlertCircle :size="12" />
                  <span>Sin datos de auditoría</span>
                </div>
              </div>
            </section>

          </template>
        </div><!-- /scroll -->
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, h } from 'vue'
import {
  Truck, Scale, Droplets, FlaskConical, BarChart2,
  TrendingUp, Layers, FileText, ShieldCheck, ChevronDown,
  Pencil, AlertTriangle, Check, History, X, User, Clock, Trash2, AlertCircle
} from 'lucide-vue-next'
import { dashboardApi, type TrazabilidadLoteResponse } from '@/api/dashboard'
import type { AccionRegistro } from '@/api/dashboard'



/** Fila de responsable: label · nombre (rol) · fecha */
const ResponsableRow = {
  props: {
    accion: { type: Object as () => AccionRegistro | null | undefined, default: null },
    label:  { type: String, default: 'Registrado por' },
    placeholder: { type: String, default: '—' },
  },
  setup(props: any) {
    return () => {
      const por = props.accion?.por
      const fecha = props.accion?.fecha
      const children: any[] = [
        h(User, { size: 11, class: 'resp-icon' }),
        h('span', { class: 'resp-lbl' }, props.label)
      ]
      if (por) {
        children.push(h('span', { class: 'resp-name' }, por.nombre_completo))
        children.push(h('span', { class: 'resp-rol' }, `(${por.rol})`))
        if (fecha) {
          children.push(h('span', { class: 'resp-date' },
            new Date(fecha).toLocaleString('es-PE', { dateStyle: 'short', timeStyle: 'short' })
          ))
        }
      } else {
        children.push(h('span', { class: 'muted' }, props.placeholder))
      }
      return h('div', { class: 'resp-row' }, children)
    }
  },
}

/** Campo label + valor */
const Field = {
  props: {
    label: String,
    val:   { type: String as () => string | null | undefined, default: null },
    mono:  Boolean,
    gold:  Boolean,
  },
  setup(props: any) {
    return () => {
      const s = props.val ? String(props.val).trim() : '—'
      let num = s
      let unit = ''

      const labelLower = props.label ? String(props.label).toLowerCase() : ''
      const isDate = labelLower.includes('fecha') ||
                     labelLower.includes('inicio') ||
                     labelLower.includes('fin') ||
                     labelLower.includes('ingreso') ||
                     labelLower.includes('salida') ||
                     /^\d+[\/\-]\d+/.test(s)

      if (!isDate) {
        const regex = /^([+-]?[$\d,.]+)\s*(.*)$/
        const m = s.match(regex)
        if (m) {
          num = m[1]
          unit = m[2]
        }
      }

      const valChildren = [h('span', { class: 'val-num' }, num)]
      if (unit) {
        valChildren.push(h('span', { class: 'val-unit' }, ' ' + unit))
      }

      return h('div', { class: 'f-field' }, [
        h('span', { class: 'f-label' }, props.label),
        h('span', { class: ['f-val', props.mono && 'mono', props.gold && 'gold'].filter(Boolean) }, valChildren)
      ])
    }
  },
}

// ── Props / Emits ──────────────────────────────────────────────────────
const props = defineProps<{ ip: string | null; open: boolean }>()
defineEmits<{ close: [] }>()

// ── State ──────────────────────────────────────────────────────────────
const data    = ref<TrazabilidadLoteResponse | null>(null)
const loading = ref(false)
const error   = ref<string | null>(null)

// Secciones abiertas por defecto según qué tiene datos
const open_sections = reactive({
  recepcion: true,
  pesaje:    true,
  muestreo:  false,
  prueba:    false,
  ley:       true,
  rec:       false,
  ruma:      false,
  liq:       false,
  auditoria: true,
})
function toggleSection(key: keyof typeof open_sections) {
  open_sections[key] = !open_sections[key]
}

// ── Fetch lazy ─────────────────────────────────────────────────────────
async function fetchData(ip: string) {
  loading.value = true
  error.value   = null
  data.value    = null
  try {
    data.value = await dashboardApi.getTrazabilidad(ip)
    // Abrir automáticamente las secciones que tienen datos
    open_sections.muestreo = (data.value.muestreos.length > 0)
    open_sections.prueba   = !!data.value.prueba_metalurgica
    open_sections.rec      = (data.value.analisis_recuperacion.length > 0)
    open_sections.ruma     = !!data.value.ruma
    open_sections.liq      = !!data.value.liquidacion
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? 'Error al cargar la trazabilidad'
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.ip, props.open] as const,
  ([ip, isOpen]) => { if (isOpen && ip) fetchData(ip) },
  { immediate: true },
)

// ── Timeline ───────────────────────────────────────────────────────────
const timeline = computed(() => {
  const d = data.value
  return [
    { key: 'recep',   label: 'Recep.',    icon: Truck,        status: d                              ? 'done' : 'pend' },
    { key: 'pesaje',  label: 'Pesaje',    icon: Scale,        status: d?.pesajes.length              ? 'done' : 'pend' },
    { key: 'mue',     label: 'Muestreo',  icon: Droplets,     status: d?.muestreos.length            ? 'done' : 'pend' },
    { key: 'prueba',  label: 'Pruebas',   icon: FlaskConical, status: d?.prueba_metalurgica           ? 'done' : 'pend' },
    { key: 'lab',     label: 'Lab',       icon: BarChart2,    status: d?.analisis_ley.some(a=>a.vigente) ? 'done' : 'pend' },
    { key: 'ruma',    label: 'Ruma',      icon: Layers,       status: d?.ruma                        ? 'done' : 'pend' },
    { key: 'liq',     label: 'Liquid.',   icon: FileText,     status: d?.liquidacion                 ? 'done' : 'pend' },
  ]
})

const lastMuestreo = computed(() =>
  data.value?.muestreos.at(-1) ?? null
)

/** Pesaje válido: el último registrado (mayor id = más reciente) */
const lastPesaje = computed(() =>
  data.value?.pesajes.at(-1) ?? null
)

/** True si el pesaje fue editado (múltiples registros) o el válido es manual */
const pesajeEditado = computed(() => {
  const pesajes = data.value?.pesajes
  if (!pesajes) return false
  return pesajes.length > 1 || (pesajes.at(-1)?.es_manual ?? false)
})

// ── Helpers ────────────────────────────────────────────────────────────
function fmtDt(s: string | null | undefined): string {
  if (!s) return '—'
  return new Date(s).toLocaleString('es-PE', { dateStyle: 'short', timeStyle: 'short' })
}
function fmtNum(v: number | null | undefined): string {
  if (v == null) return '—'
  return Number(v).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function fmt3(v: number | null | undefined): string {
  if (v == null) return '—'
  return Number(v).toFixed(3)
}
function estadoRecTag(e: string): string {
  return { COMPLETADO: 'pill-ok', CERT_COMERCIAL: 'pill-ok', CERT_RECONOCIMIENTO: 'pill-ok', PENDIENTE: 'pill-dim' }[e] ?? 'pill-dim'
}
</script>

<style scoped>
/* ══ OVERLAY ══════════════════════════════════════════════════════════ */
.trz-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(3px);
  z-index: 1000;
}

/* ══ PANEL ════════════════════════════════════════════════════════════ */
.trz-panel {
  position: fixed;
  top: 0; right: 0;
  width: min(540px, 100vw);
  height: 100dvh;           /* dynamic viewport — no se corta en móvil */
  background: var(--color-bg-card, #16181e);
  border-left: 1px solid var(--color-border, #2a2d37);
  z-index: 1001;
  display: flex;
  flex-direction: column;
  overflow: hidden;         /* el scroll lo hace .trz-scroll */
  box-shadow: -12px 0 50px rgba(0,0,0,0.55);
}

/* ══ TRANSITIONS ═══════════════════════════════════════════════════════ */
.drawer-fade-enter-active, .drawer-fade-leave-active { transition: opacity .2s; }
.drawer-fade-enter-from,   .drawer-fade-leave-to     { opacity: 0; }
.drawer-slide-enter-active, .drawer-slide-leave-active {
  transition: transform .26s cubic-bezier(.4,0,.2,1);
}
.drawer-slide-enter-from, .drawer-slide-leave-to { transform: translateX(100%); }

/* expand transition removed — using v-show without animation to avoid clipping */

/* ══ HEADER ════════════════════════════════════════════════════════════ */
.trz-header {
  flex-shrink: 0;
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
  padding: 1.1rem 1.25rem 0.85rem;
  border-bottom: 1px solid var(--color-border, #2a2d37);
  background: var(--color-bg-card);
}
.trz-header-left { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.3rem; }
.trz-title-row   { display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; }
.trz-ip {
  font-family: var(--font-mono, monospace);
  font-size: 1.15rem; font-weight: 800;
  color: var(--color-gold, #c9a227);
  letter-spacing: 0.06em;
}
.trz-subtitle {
  font-size: 0.76rem; color: var(--color-text-muted, #8892a4);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.trz-subtitle strong { color: var(--color-text, #e2e8f0); }

.trz-close-btn {
  flex-shrink: 0;
  background: transparent;
  border: 1px solid var(--color-border, #3a3a28);
  color: var(--color-text-muted); border-radius: 6px;
  width: 28px; height: 28px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.trz-close-btn:hover {
  background: rgba(165, 71, 61, 0.1);
  border-color: var(--color-error);
  color: var(--color-error);
}

/* ══ TIMELINE BAR ══════════════════════════════════════════════════════ */
.trz-timeline-bar {
  flex-shrink: 0;
  display: flex; align-items: flex-start;
  padding: 0.65rem 1rem;
  gap: 0;
  border-bottom: 1px solid var(--color-border, #2a2d37);
  background: rgba(255,255,255,0.018);
  overflow-x: auto;
}
.tl-node {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.25rem; flex: 1; min-width: 50px; position: relative;
}
.tl-connector {
  position: absolute; top: 10px; left: 0; right: 0;
  height: 2px; background: var(--color-border, #2a2d37);
  transform: translateX(-50%);
  width: 100%;
  z-index: 0;
}
.tl-connector.done { background: var(--color-gold, #c9a227); }
.tl-dot {
  width: 20px; height: 20px; border-radius: 50%;
  border: 2px solid var(--color-border, #2a2d37);
  background: var(--color-bg-card, #16181e);
  color: var(--color-text-muted, #8892a4);
  display: flex; align-items: center; justify-content: center;
  position: relative; z-index: 1;
  transition: border-color .2s, background .2s, color .2s;
}
.tl-node.done .tl-dot {
  border-color: var(--color-gold, #c9a227);
  background: rgba(201,162,39,.15);
  color: var(--color-gold, #c9a227);
}
.tl-label {
  font-size: 0.56rem; text-transform: uppercase; letter-spacing: .06em;
  color: var(--color-text-muted, #8892a4); text-align: center;
  white-space: nowrap;
}
.tl-node.done .tl-label { color: var(--color-gold, #c9a227); }

/* ══ SCROLL BODY ═══════════════════════════════════════════════════════ */
.trz-scroll {
  flex: 1 1 0;          /* ocupa todo el espacio restante */
  overflow-y: auto;
  min-height: 0;        /* crítico: evita que flex hijo desborde al padre */
  padding: 0.75rem 1rem 3rem;
  display: flex; flex-direction: column; gap: 0.45rem;
}

/* ══ CENTRO (carga / error) ════════════════════════════════════════════ */
.trz-center {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.75rem; padding: 3rem 1rem;
  color: var(--color-text-muted, #8892a4); font-size: 0.85rem;
}
.trz-center.err { color: #f87171; }

/* ══ CARD DE SECCIÓN ═══════════════════════════════════════════════════ */
.trz-card {
  border: 1px solid var(--color-border, #3a3a28);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.01);
  margin-bottom: 0.45rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: border-color 0.2s, box-shadow 0.2s;
  flex-shrink: 0;
}
.trz-card:hover {
  border-color: rgba(179, 144, 40, 0.15);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
}

.trz-card-head {
  display: flex; align-items: center; gap: 0.65rem;
  padding: 0.65rem 0.9rem;
  cursor: pointer; user-select: none;
  background: rgba(184, 150, 46, 0.02);
  transition: background .15s;
  min-height: 2.5rem;
  border-top-left-radius: 7px;
  border-top-right-radius: 7px;
}
.trz-card-head:hover { background: rgba(184, 150, 46, 0.06); }

.head-icon { color: var(--color-gold, #b39028); display: flex; align-items: center; }
.head-title {
  font-family: var(--font-main);
  font-size: 0.78rem; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--color-text, #d4c47a);
}
.head-count {
  background: rgba(201,162,39,.13); color: var(--color-gold, #c9a227);
  font-size: 0.62rem; font-weight: 700;
  padding: 0.08rem 0.45rem; border-radius: 999px;
}
.head-resp {
  font-size: 0.7rem; color: var(--color-text, #e2e8f0); font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 160px;
}
.head-rol { font-weight: 400; color: var(--color-text-muted, #8892a4); margin-left: 0.3rem; font-style: normal; }
.head-date { font-size: 0.66rem; font-family: var(--font-mono, monospace); }
.head-caret {
  margin-left: auto; color: var(--color-text-muted, #8892a4);
  transition: transform .2s; flex-shrink: 0;
}
.head-caret.rotated { transform: rotate(180deg); }

.trz-card-body {
  padding: 0.75rem 0.9rem;
  display: flex; flex-direction: column; gap: 0.6rem;
  border-top: 1px solid var(--color-border, #2a2d37);
}

/* ══ SUB-CARDS ═════════════════════════════════════════════════════════ */
.sub-card {
  background: rgba(255,255,255,0.022);
  border: 1px solid var(--color-border, #2a2d37);
  border-radius: 6px; padding: 0.6rem 0.7rem;
  display: flex; flex-direction: column; gap: 0.5rem;
}
.sub-card--gold  { border-color: rgba(201,162,39,0.3); }
.sub-card--dim   { opacity: 0.55; border-style: dashed; }

.sub-header {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.72rem; flex-wrap: wrap;
}

/* ══ GRILLAS ═══════════════════════════════════════════════════════════ */
/* ══ GRILLAS ═══════════════════════════════════════════════════════════ */
.audit-summary,
.trz-card-body > .g2,
.trz-card-body > .g3 {
  display: grid;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid var(--color-border, #3a3a28);
  border-radius: 6px;
  padding: 0.65rem 0.85rem;
  gap: 0.6rem 0.85rem;
}
.audit-summary { grid-template-columns: repeat(3, 1fr); margin-top: 0.25rem; }
.trz-card-body > .g2 { grid-template-columns: 1fr 1fr; }
.trz-card-body > .g3 { grid-template-columns: repeat(3, 1fr); }

/* Grillas limpias cuando están anidadas (ej. dentro de .sub-card) */
.sub-card .g2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 0.8rem; }
.sub-card .g3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem 0.6rem; }

.g-span2 { grid-column: span 2; }
.g-span3 { grid-column: span 3; }

/* ══ FIELD / AUDIT ITEM ═════════════════════════════════════════════════ */
.f-field {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.audit-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  align-items: center;
  text-align: center;
}
.f-field :deep(.f-label),
.audit-lbl {
  font-family: var(--font-main);
  font-size: 0.72rem;
  font-weight: 500; /* Normal weight - NOT bold */
  text-transform: uppercase;
  letter-spacing: .06em;
  color: #8892a4; /* Steel gray for clear label/value distinction */
}
.f-field :deep(.f-val),
.audit-val {
  font-family: var(--font-main);
  font-size: 0.95rem;
  font-weight: 700; /* Bold/Negrita for value */
  color: #ffffff; /* White for clean contrast against the background */
  line-height: 1.1;
  word-break: break-all;
  display: inline-flex;
  align-items: baseline;
}
.f-field :deep(.f-val.mono),
.audit-val.mono {
  font-family: var(--font-mono);
  font-size: 0.88rem;
  letter-spacing: 0.02em;
  font-weight: 700; /* Bold/Negrita for monospace value */
  color: var(--color-gold, #b39028); /* Gold for numeric codes/weights */
}
.f-field :deep(.f-val.gold),
.audit-val.gold {
  color: var(--color-gold, #b39028);
  font-weight: 800; /* Extra bold/Negrita for gold values */
}

/* Diferenciación de estilo dentro de los valores (número vs unidad) */
.f-field :deep(.val-num),
.audit-val :deep(.val-num),
.val-num {
  font-weight: inherit;
  color: inherit;
}
.f-field :deep(.val-unit),
.audit-val :deep(.val-unit),
.val-unit {
  font-family: var(--font-main);
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-dim, #6b6b50);
  margin-left: 0.15rem;
}

/* ══ RESPONSABLE ROW ═══════════════════════════════════════════════════ */
.resp-row {
  display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap;
  font-size: 0.72rem;
  padding: 0.45rem 0.6rem;
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  color: var(--color-text-muted, #8a8762);
  margin-top: 0.35rem;
}
.resp-row :deep(.resp-icon) {
  color: var(--color-text-dim, #6b6b50);
  opacity: 0.75;
}
.resp-row :deep(.resp-lbl) {
  font-family: var(--font-main);
  font-size: 0.68rem;
  font-weight: 500; /* Normal weight - NOT bold */
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--color-text-dim, #6b6b50);
}
.resp-row :deep(.resp-name) {
  font-family: var(--font-main);
  color: #ffffff; /* White for name */
  font-weight: 700; /* Bold/Negrita */
}
.resp-row :deep(.resp-rol) {
  font-family: var(--font-main);
  color: var(--color-text-muted, #8a8762);
  font-size: 0.7rem;
}
.resp-row :deep(.resp-date) {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: var(--color-text-dim, #6b6b50);
}

/* ══ DESCARTE ══════════════════════════════════════════════════════════ */
.descarte-row {
  display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap;
  font-size: 0.72rem;
  color: var(--color-error, #a5473d);
  background: var(--color-error-bg, rgba(165, 71, 61, 0.10));
  border: 1px solid rgba(165, 71, 61, 0.25);
  padding: 0.45rem 0.6rem;
  border-radius: 4px;
}
.descarte-row .lbl {
  font-family: var(--font-main);
  font-size: 0.68rem;
  font-weight: 500; /* Normal weight - NOT bold */
  text-transform: uppercase;
  letter-spacing: .08em;
  color: rgba(165, 71, 61, 0.7);
}
.descarte-name {
  font-family: var(--font-main);
  font-weight: 700; /* Bold/Negrita */
  color: #ffffff;
}
.descarte-date {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  color: rgba(165, 71, 61, 0.7);
  margin-left: auto;
}
.descarte-just {
  width: 100%;
  padding-left: 1.15rem;
  margin-top: 0.1rem;
  font-style: italic;
  color: rgba(212, 196, 122, 0.8); /* var(--color-text) slightly faded */
}

/* ══ SUMMARY ROW (muestreo resumen) ═══════════════════════════════════ */
.summary-row {
  display: flex; align-items: center; gap: 0.45rem;
  background: rgba(201,162,39,0.07);
  border: 1px solid rgba(201,162,39,0.2);
  border-radius: 5px; padding: 0.35rem 0.6rem;
  font-size: 0.72rem;
}
.sr-lbl { color: var(--color-text-muted, #8892a4); font-size: 0.6rem; text-transform: uppercase; letter-spacing: .06em; }
.sr-val { color: var(--color-text, #e2e8f0); font-weight: 600; }
.sr-val.gold { color: var(--color-gold, #c9a227); }
.sr-sep { color: var(--color-border, #2a2d37); }

/* ══ HEAD BADGE ════════════════════════════════════════════════════════ */
.head-badge {
  font-size: 0.6rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
  background: rgba(255,255,255,0.06); color: var(--color-text-muted, #8892a4);
  padding: 0.06rem 0.4rem; border-radius: 4px; white-space: nowrap;
}

/* ══ HEAD KV (chip etiqueta + valor en header) ══════════════════════════ */
.head-kv {
  display: inline-flex; align-items: baseline; gap: 0.28rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--color-border, #2a2d37);
  border-radius: 4px; padding: 0.06rem 0.45rem;
  white-space: nowrap;
}
.hkv-lbl {
  font-size: 0.55rem; text-transform: uppercase; letter-spacing: .07em;
  color: var(--color-text-muted, #8892a4);
}
.hkv-val {
  font-size: 0.72rem; font-weight: 600; color: var(--color-text, #e2e8f0);
}
.hkv-val.gold { color: var(--color-gold, #c9a227); }

/* Audit styles are unified above under Grillas and Fields */

/* ══ WARN / EMPTY ══════════════════════════════════════════════════════ */
.warn-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.72rem;
  color: var(--color-warning, #cf973d);
  background: var(--color-warning-bg, rgba(207, 151, 61, 0.12));
  border: 1px solid rgba(207, 151, 61, 0.25);
  padding: 0.45rem 0.6rem;
  border-radius: 4px;
}
.empty-state-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--color-text-dim, #6b6b50);
  font-size: 0.78rem;
  padding: 0.5rem 0.7rem;
  background: rgba(255, 255, 255, 0.012);
  border: 1px dashed rgba(255, 255, 255, 0.06);
  border-radius: 6px;
}

/* ══ HIST HEADER (separador historial de correcciones) ════════════════════ */
.hist-header {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.6rem; text-transform: uppercase; letter-spacing: .07em;
  color: var(--color-text-muted, #8892a4);
  margin-top: 0.25rem;
}
.hist-header::before, .hist-header::after {
  content: ''; flex: 1;
  height: 1px; background: var(--color-border, #2a2d37);
}

/* ══ PILLS / TAGS ══════════════════════════════════════════════════════ */
.trz-pill, .pill {
  font-size: 0.58rem; font-weight: 700; letter-spacing: .07em;
  padding: 0.1rem 0.45rem; border-radius: 999px; text-transform: uppercase;
  white-space: nowrap;
}
.pill-ok,           .trz-pill.pill-ok        { background: rgba(34,197,94,.15); color: #22c55e; }
.pill-dim,          .trz-pill.pill-dim        { background: rgba(148,163,184,.12); color: #94a3b8; }
.pill-tipo,         .trz-pill.pill-tipo       { background: rgba(96,165,250,.12); color: #60a5fa; }
.pill-volado,       .trz-pill.pill-volado     { background: rgba(251,191,36,.15); color: #fbbf24; }
.pill-dirim,        .trz-pill.pill-dirim      { background: rgba(168,85,247,.15); color: #a855f7; }
.pill-recepcionado, .trz-pill.pill-recepcionado { background: rgba(96,165,250,.15); color: #60a5fa; }
.pill-asignado_ruma,.trz-pill.pill-asignado_ruma{ background: rgba(168,85,247,.15); color: #a855f7; }
.pill-liquidado,    .trz-pill.pill-liquidado  { background: rgba(34,197,94,.15);  color: #22c55e; }
.pill-facturado,    .trz-pill.pill-facturado  { background: rgba(251,191,36,.15); color: #fbbf24; }
.pill-pagado,       .trz-pill.pill-pagado     { background: rgba(201,162,39,.2);  color: var(--color-gold, #c9a227); }
.pill-warn,         .trz-pill.pill-warn       { background: rgba(245,158,11,.15); color: #f59e0b; }

/* ══ MISC ══════════════════════════════════════════════════════════════ */
.muted    { color: var(--color-text-muted, #8892a4); }
.ml-auto  { margin-left: auto; }
.mono     { font-family: var(--font-mono, monospace); }

/* ══ SPINNER ═══════════════════════════════════════════════════════════ */
.ring {
  display: inline-block; width: 22px; height: 22px;
  border: 2px solid var(--color-border, #2a2d37);
  border-top-color: var(--color-gold, #c9a227);
  border-radius: 50%;
  animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
