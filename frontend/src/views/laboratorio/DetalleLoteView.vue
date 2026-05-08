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

      <!-- ═══════════════════════════════════════ TAB LEY ═══════════════════════════════════════ -->
      <template v-if="tabActual === 'ley'">

        <div class="labs-grid">
          <div
            v-for="a in lote.analisis_ley"
            :key="a.id"
            class="lab-card"
            :class="{
              descartado: !a.vigente,
              'excluido-local': a.vigente && excluidos.has(a.id),
            }"
          >
            <div class="lab-card-header">
              <span class="lab-titulo">{{ tipoBadge(a.tipo_analisis) }}</span>
              <span v-if="!a.vigente" class="badge-estado pendiente" style="font-size:0.65rem">DESCARTADO</span>
              <span v-else-if="excluidos.has(a.id)" class="badge-excluido">EXCLUIDO</span>
            </div>

            <div class="lab-field"><span class="lf-label">CIP:</span>         <span class="lf-value td-mono" style="color:var(--color-gold)">{{ a.cip ?? '-' }}</span></div>
            <div class="lab-field"><span class="lf-label">LABORATORIO:</span> <span class="lf-value">{{ a.laboratorio }}</span></div>
            <div class="lab-field"><span class="lf-label">FECHA:</span>       <span class="lf-value">{{ fmt(a.fecha_analisis) }}</span></div>
            <div class="lab-field" v-if="a.creado_por_nombre">
              <span class="lf-label">RESPONSABLE:</span>
              <span class="lf-value" style="color:var(--color-text-muted)">{{ a.creado_por_nombre }}</span>
            </div>
            <div class="lab-field"><span class="lf-label">MALLA +140:</span>  <span class="lf-value">{{ a.ley_grueso }}</span></div>
            <div class="lab-field"><span class="lf-label">MALLA -140:</span>  <span class="lf-value">{{ a.ley_fino }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY OZ/TC:</span>   <span class="lf-value highlight">{{ a.ley_final }}</span></div>
            <div class="lab-field"><span class="lf-label">LEY GR/TM:</span>   <span class="lf-value">{{ a.ley_gr_tm }}</span></div>

            <div v-if="a.certificado_url" class="lab-field">
              <span class="lf-label">CERTIFICADO:</span>
              <a href="#" @click.prevent="verCertificado(a.certificado_url)" class="link-cert">Ver PDF</a>
            </div>

            <div class="lab-card-footer" v-if="!a.eliminado">
              <template v-if="a.vigente">
                <button
                  class="btn-excluir-sm"
                  :class="{ 'btn-excluir-sm--activo': excluidos.has(a.id) }"
                  @click="toggleExcluido(a.id)"
                  :title="excluidos.has(a.id) ? 'Incluir en ley planta' : 'Excluir de ley planta'"
                >
                  {{ excluidos.has(a.id) ? '+ Incluir' : '✕ Excluir' }}
                </button>
                <label class="btn-secondary-sm" title="Adjuntar certificado">
                  Adjuntar cert.
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none"
                    @change="adjuntarCertLey($event, a.id)" />
                </label>
              </template>
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
            <span>
              LEY PLANTA
              <span v-if="excluidos.size > 0" class="badge-simulando">SIMULANDO</span>
            </span>
            <div style="display:flex;gap:0.5rem">
              <button
                class="btn-secondary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="previsualizarCertLey"
                :disabled="previsualizandoLey || leyPlantaSimulada === null"
                title="Abrir previsualización del certificado"
              >
                <span v-if="previsualizandoLey" class="spinner" style="margin-right:0.4rem"></span>
                <span v-else>👁 Previsualizar</span>
              </button>
              <button
                class="btn-primary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="abrirConfirmarGenerar"
                :disabled="generando || leyPlantaSimulada === null"
                title="Guardar certificado PDF definitivo en el servidor"
              >
                <span v-if="generando" class="spinner" style="margin-right:0.4rem"></span>
                Guardar PDF definitivo
              </button>
            </div>
          </h2>

          <div v-if="cargandoLeyComercial" class="estado-tabla">
            <span class="spinner" style="margin-right:0.5rem"></span> Calculando...
          </div>

          <template v-else-if="leyComercialCalc">
            <div class="lc-grid">
              <div class="lc-item">
                <span class="lc-label">LEY PLANTA (vigentes seleccionados):</span>
                <span class="lc-valor mono" :class="{ gold: excluidos.size === 0 }">
                  {{ leyPlantaSimulada != null ? Number(leyPlantaSimulada).toFixed(4) : '-' }} oz/TC
                  <span v-if="excluidos.size > 0 && lote.ley_planta != null"
                    style="font-size:0.7rem;color:var(--color-text-faint);margin-left:0.35rem">
                    (antes: {{ Number(lote.ley_planta).toFixed(4) }})
                  </span>
                </span>
              </div>
              <div class="lc-item" v-if="lote.ley_minero">
                <span class="lc-label">LEY MINERO:</span>
                <span class="lc-valor mono">{{ Number(lote.ley_minero).toFixed(4) }} oz/TC</span>
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

            <div v-if="excluidos.size > 0 && leyPlantaSimulada === null" class="info-box warning" style="margin-top:0.75rem">
              <AlertTriangle :size="14" /> Sin análisis vigentes restantes — la ley planta quedaría vacía.
            </div>
            <div v-if="leyComercialCalc.sin_parametros" class="info-box warning" style="margin-top:0.75rem">
              <AlertTriangle :size="16" /> Sin parámetros comerciales configurados para este proveedor-acopiador.
            </div>
            <div v-if="leyComercialCalc.detalle && !leyComercialCalc.sin_parametros"
              style="font-size:0.75rem;color:var(--color-text-faint);margin-top:0.5rem;font-family:var(--font-mono)">
              Detalle: {{ leyComercialCalc.detalle }}
            </div>
          </template>

          <div v-if="certLeyGuardado" class="cert-guardado-info">
            ✓ Certificado guardado —
            <a href="#" @click.prevent="verCertificado(certLeyGuardado)" class="link-cert">Ver PDF guardado</a>
          </div>

          <div v-else-if="!leyComercialCalc && !cargandoLeyComercial" class="info-box warning" style="margin-top:0.75rem">
            <AlertTriangle /> No se pudo calcular la ley comercial.
            <button class="btn-secondary" style="margin-left:0.5rem;font-size:0.75rem" @click="recargarLeyComercial">Reintentar</button>
          </div>
        </section>

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
          <button v-if="!lote.ley_minero" class="btn-secondary" @click="modalLeyMinero = true">
            Registrar Ley Minero
          </button>
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
              <button class="btn-cerrar" @click="modalLeyMinero = false"><X :size="18" /></button>
            </div>
            <div class="modal-body">
              <p style="font-size:0.85rem;color:var(--color-text-muted);margin-bottom:1rem">
                Ley declarada por el proveedor. Si difiere más de 0.10 oz/TC
                de la ley de planta, se habilitará la solicitud de dirimencia.
              </p>
              <div class="field" style="margin-bottom:0.75rem">
                <label class="field-label">CERTIFICADO (opcional — pre-llena los campos)</label>
                <label
                  class="upload-zone-sm"
                  :class="{ uploading: extrayendoMinero }"
                  style="display:flex;align-items:center;gap:0.5rem;padding:0.6rem 0.75rem;border:1px dashed var(--color-border);border-radius:6px;cursor:pointer"
                >
                  <span v-if="extrayendoMinero" class="spinner"></span>
                  <span v-else-if="archivoMinero" style="color:var(--color-success);font-size:0.82rem">
                    ✓ {{ archivoMinero.name }}
                  </span>
                  <span v-else style="font-size:0.82rem;color:var(--color-text-muted)">
                    Subir PDF o imagen del certificado…
                  </span>
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="extraerCertMinero" />
                </label>
                <p v-if="errOcrMinero" style="font-size:0.78rem;color:var(--color-danger);margin-top:0.35rem">
                  {{ errOcrMinero }}
                </p>
              </div>
              <div class="field">
                <label class="field-label">LABORATORIO / ORIGEN</label>
                <input class="field-input" v-model="formLeyMinero.laboratorio" placeholder="Ej: Laboratorio del Minero" />
              </div>
              <div class="form-grid" style="grid-template-columns:1fr 1fr">
                <div class="field">
                  <label class="field-label">LEY FINO (Oz/TC)</label>
                  <input type="number" class="field-input" v-model.number="formLeyMinero.ley_fino" step="0.0001" placeholder="0.0000" />
                </div>
                <div class="field">
                  <label class="field-label">LEY GRUESO (Oz/TC)</label>
                  <input type="number" class="field-input" v-model.number="formLeyMinero.ley_grueso" step="0.0001" placeholder="0.0000" />
                </div>
              </div>
              <div class="field">
                <label class="field-label">FECHA ANÁLISIS</label>
                <input type="date" class="field-input" v-model="formLeyMinero.fecha_analisis" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="modalLeyMinero = false">Cancelar</button>
              <button class="btn-primary" @click="guardarLeyMinero" :disabled="guardandoLeyMinero || extrayendoMinero">
                <span v-if="guardandoLeyMinero" class="spinner" style="margin-right:0.4rem"></span>
                Guardar Ley Minero
              </button>
            </div>
          </div>
        </div>

      </template>

      <!-- ═══════════════════════════════════════ TAB REC ═══════════════════════════════════════ -->
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
            <div class="lab-field" v-if="a.creado_por_nombre">
              <span class="lf-label">RESPONSABLE:</span>
              <span class="lf-value" style="color:var(--color-text-muted)">{{ a.creado_por_nombre }}</span>
            </div>
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
                <button class="btn-danger-sm" @click="toggleDescartarRec(a.id)" title="Excluir del cálculo">
                  Descartar
                </button>
                <label class="btn-secondary-sm" title="Adjuntar certificado">
                  Adjuntar cert.
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" style="display:none" @change="adjuntarCertRec($event, a.id)" />
                </label>
              </template>
              <button
                v-if="auth.user?.rol === 'Admin' || auth.user?.rol === 'Gerencia'"
                class="btn-danger-sm"
                style="margin-left:auto;opacity:0.7"
                @click="eliminarRecuperacion(a.id)"
                title="Eliminar registro permanentemente de la vista"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>

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

        <!-- Sección: certificado de recuperación comercial -->
        <section class="card" v-if="tieneRecuperacionVigente">
          <h2 class="card-titulo" style="display:flex;justify-content:space-between;align-items:center">
            <span>CERTIFICADO DE RECUPERACIÓN</span>
            <div style="display:flex;gap:0.5rem">
              <button
                class="btn-secondary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="previsualizarCertRec"
                :disabled="previsualizandoRec"
                title="Abrir previsualización del certificado de recuperación"
              >
                <span v-if="previsualizandoRec" class="spinner" style="margin-right:0.4rem"></span>
                <span v-else>👁 Previsualizar</span>
              </button>
              <button
                class="btn-primary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="guardarCertRecuperacion"
                :disabled="guardandoRec"
                title="Guardar certificado PDF definitivo en el servidor"
              >
                <span v-if="guardandoRec" class="spinner" style="margin-right:0.4rem"></span>
                Guardar PDF definitivo
              </button>
            </div>
          </h2>
          <p style="font-size:0.8rem;color:var(--color-text-muted)">
            Genera el informe de recuperación (formato Paititi) para entregar al proveedor.
          </p>
          <div v-if="certRecGuardado" class="cert-guardado-info">
            ✓ Certificado guardado —
            <a href="#" @click.prevent="verCertificado(certRecGuardado)" class="link-cert">Ver PDF guardado</a>
          </div>
        </section>

        <div class="acciones-lote">
          <button
            v-if="ley_cabeza != null && cipsRecuperacionDisponibles.length > 0"
            class="btn-primary"
            @click="abrirModalRecup"
            :disabled="enviando"
          >
            <span v-if="enviando" class="spinner" style="margin-right:0.4rem"></span>
            Enviar a recuperación
          </button>
          <span v-if="tienePendiente" class="info-inline" style="margin-left:0.5rem">
            <Hourglass :size="16" /> Análisis pendiente en laboratorio
          </span>
        </div>

        <!-- Alerta: CIP listo pero sin ley de planta aún -->
        <div
          v-if="cipsRecuperacionDisponibles.length > 0 && ley_cabeza == null"
          class="alerta-warning"
          style="margin-top:0.75rem"
        >
          <TriangleAlert :size="16" />
          Prueba metalúrgica etiquetada y lista, pero falta la
          <strong>ley comercial</strong> para poder oficializar el envío a recuperación.
          Registre los análisis de ley primero.
        </div>

        <div v-if="lote.tiene_prueba_pendiente" class="alerta-warning" style="margin-top:0.75rem">
          <TriangleAlert :size="16" /> Este lote tiene una prueba metalúrgica en curso.
          Revise el módulo de <strong>Pruebas Metalúrgicas</strong> antes de solicitar nuevas muestras.
        </div>
        <button class="btn-secondary" @click="solicitarRemuestreo" :disabled="lote.tiene_prueba_pendiente" style="margin-top:0.5rem">
          Solicitar nueva prueba
        </button>

      </template>

    </template>

    <!-- ═══════════════════════ MODALES (fuera del template condicional) ════════════════════════ -->

    <!-- Modal: confirmar descarte + generar PDF (flujo ley) -->
    <div v-if="modalConfirmarGenerar" class="modal-overlay" @click.self="modalConfirmarGenerar = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Confirmar y Guardar PDF</h2>
          <button class="btn-cerrar" @click="modalConfirmarGenerar = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div v-if="excluidos.size > 0" class="descarte-preview">
            <div class="dp-titulo">ANÁLISIS A DESCARTAR ({{ excluidos.size }})</div>
            <div v-for="a in analisisADescartar" :key="a.id" class="dp-row">
              <span class="dp-label">{{ tipoBadge(a.tipo_analisis) }} — {{ a.laboratorio }}</span>
              <span class="dp-val">{{ Number(a.ley_final).toFixed(4) }}</span>
            </div>
            <div class="dp-row" style="margin-top:0.5rem;border-top:1px solid rgba(255,255,255,0.08);padding-top:0.5rem">
              <span class="dp-label">Ley planta resultante:</span>
              <span class="dp-val dp-val--changed">
                {{ leyPlantaSimulada != null ? leyPlantaSimulada.toFixed(4) : 'Sin datos' }} oz/TC
              </span>
            </div>
            <div class="field" style="margin-top:0.75rem">
              <label class="field-label">Justificación del descarte (obligatoria):</label>
              <textarea class="field-input" v-model="justificacionGenerar" rows="3"
                placeholder="Ej: Lab Minares discordante respecto a los demás"></textarea>
            </div>
          </div>
          <div v-else class="info-box" style="margin-bottom:0.75rem">
            Se guardará el certificado con todos los análisis vigentes.
            Ley planta: <strong style="font-family:var(--font-mono)">
              {{ lote?.ley_planta != null ? Number(lote.ley_planta).toFixed(4) : '-' }} oz/TC
            </strong>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalConfirmarGenerar = false">Cancelar</button>
          <button
            class="btn-primary"
            :disabled="(excluidos.size > 0 && !justificacionGenerar.trim()) || generando"
            @click="confirmarYGuardar"
          >
            <span v-if="generando" class="spinner" style="margin-right:0.4rem"></span>
            Confirmar y guardar PDF
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: descartar análisis de recuperación -->
    <div v-if="modalDescartarRec !== null" class="modal-overlay" @click.self="modalDescartarRec = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Descartar análisis de recuperación</h2>
          <button class="btn-cerrar" @click="modalDescartarRec = null"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label class="field-label">Justificación (obligatoria):</label>
            <textarea class="field-input" v-model="justificacionRec" rows="3"
              placeholder="Ej: Resultado discordante"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalDescartarRec = null">Cancelar</button>
          <button class="btn-danger" @click="confirmarDescartarRec" :disabled="!justificacionRec.trim()">
            Confirmar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: seleccionar CIP para nueva ley -->
    <div v-if="modalAgregarLey" class="modal-overlay" @click.self="modalAgregarLey = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Registrar Nueva Ley</h2>
          <button class="btn-cerrar" @click="modalAgregarLey = false"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <div v-if="cipsDisponiblesLey.length === 0" class="info-box warning">
            <AlertTriangle :size="16" /> No hay CIPs de laboratorio disponibles sin análisis.
            Es necesario generar nuevas etiquetas o solicitar un remuestreo.
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

    <!-- Modal: seleccionar lab para recuperación -->
    <div v-if="modalRecup" class="modal-overlay" @click.self="modalRecup = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Enviar a Recuperación</h2>
          <button class="btn-cerrar" @click="modalRecup = false"><X :size="18" /></button>
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

  </div>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { AlertTriangle, Hourglass, TriangleAlert, X } from 'lucide-vue-next'
import { useLaboratorioStore } from '@/stores/laboratorio'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import type { LoteLabOut } from '@/types/laboratorio'
import { laboratorioApi, type LeyComercialCalc } from '@/api/laboratorio'
import { muestreoApi } from '@/api/muestreo'
import { pruebasApi } from '@/api/pruebas'

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

// ── Flujo ley: exclusión local + guardar ──────────────────────────────────────
const excluidos             = ref<Set<number>>(new Set())
const modalConfirmarGenerar = ref(false)
const justificacionGenerar  = ref('')
const generando             = ref(false)
const previsualizandoLey    = ref(false)
const certLeyGuardado       = ref<string | null>(null)

const ley_cabeza = ref<number | null>(null)

function toggleExcluido(id: number) {
  const s = new Set(excluidos.value)
  s.has(id) ? s.delete(id) : s.add(id)
  excluidos.value = s
}

const leyPlantaSimulada = computed<number | null>(() => {
  if (!lote.value) return null
  // Sin exclusiones locales → usar el valor calculado por el servidor (incluye dirimencia)
  if (excluidos.value.size === 0) {
    return lote.value.ley_planta != null ? Number(lote.value.ley_planta) : null
  }
  // Simulación: recalcular excluyendo los marcados localmente (solo planta/externo)
  const vigentes = lote.value.analisis_ley.filter(
    a => a.vigente && !a.eliminado && !excluidos.value.has(a.id)
      && (a.tipo_analisis === 'planta' || a.tipo_analisis === 'externo'),
  )
  if (vigentes.length === 0) return null
  const prom = vigentes.reduce((acc, a) => acc + Number(a.ley_final), 0) / vigentes.length
  return parseFloat(prom.toFixed(4))
})

const analisisADescartar = computed(() =>
  lote.value?.analisis_ley.filter(a => excluidos.value.has(a.id)) ?? [],
)

function abrirConfirmarGenerar() {
  justificacionGenerar.value = ''
  modalConfirmarGenerar.value = true
}

async function previsualizarCertLey() {
  previsualizandoLey.value = true
  try {
    await laboratorioApi.previewCertificadoLeyPdf(ipActual)
  } catch {
    ui.toast('Error al generar previsualización', 'error')
  } finally {
    previsualizandoLey.value = false
  }
}

async function confirmarYGuardar() {
  for (const id of excluidos.value) {
    const ok = await store.descartarLey(id, justificacionGenerar.value)
    if (!ok) {
      ui.toast(`Error al descartar análisis ${id}`, 'error')
      return
    }
  }
  excluidos.value = new Set()
  modalConfirmarGenerar.value = false

  lote.value = await store.cargarDetalleLote(ipActual)
  leyComercialCalc.value = null
  await recargarLeyComercial()

  generando.value = true
  try {
    const res = await laboratorioApi.guardarCertificadoLey(ipActual)
    certLeyGuardado.value = res.ruta
    ui.toast('Certificado guardado correctamente', 'success')
  } catch {
    ui.toast('Error al guardar certificado PDF', 'error')
  } finally {
    generando.value = false
  }
}

// ── Flujo rec: descartar + certificado ───────────────────────────────────────
const modalDescartarRec  = ref<number | null>(null)
const justificacionRec   = ref('')
const previsualizandoRec = ref(false)
const guardandoRec       = ref(false)
const certRecGuardado    = ref<string | null>(null)

const tieneRecuperacionVigente = computed(() =>
  lote.value?.analisis_recuperacion.some(a => a.vigente && a.estado === 'COMPLETADO') ?? false
)

async function previsualizarCertRec() {
  previsualizandoRec.value = true
  try {
    await laboratorioApi.previewCertificadoRecPdf(ipActual)
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al generar previsualización', 'error')
  } finally {
    previsualizandoRec.value = false
  }
}

async function guardarCertRecuperacion() {
  guardandoRec.value = true
  try {
    const res = await laboratorioApi.guardarCertificadoRec(ipActual)
    certRecGuardado.value = res.ruta
    ui.toast('Certificado de recuperación guardado', 'success')
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al guardar certificado', 'error')
  } finally {
    guardandoRec.value = false
  }
}

function toggleDescartarRec(id: number) {
  justificacionRec.value = ''
  modalDescartarRec.value = id
}

async function confirmarDescartarRec() {
  if (modalDescartarRec.value === null) return
  const j = justificacionRec.value.trim()
  if (!j) return
  const ok = await store.descartarRecuperacion(modalDescartarRec.value, j)
  if (ok) {
    modalDescartarRec.value = null
    lote.value = await store.cargarDetalleLote(ipActual)
  }
}

// ── Ley comercial ─────────────────────────────────────────────────────────────
const cargandoLeyComercial = ref(false)
const leyComercialCalc     = ref<LeyComercialCalc | null>(null)

watch(lote, async (l: LoteLabOut | null) => {
  if (l?.ley_planta != null && !leyComercialCalc.value) {
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

//actualizar value de ley cabeza con ley comercial
watch(leyComercialCalc, (nuevaLey) => {
  if (nuevaLey?.ley_comercial != null) {
    ley_cabeza.value = nuevaLey.ley_comercial
  }
})

//watch para certificados
watch(lote, (l) => {
  if (l?.cert_ley_url && !certLeyGuardado.value)
    certLeyGuardado.value = l.cert_ley_url
  if (l?.cert_rec_url && !certRecGuardado.value)
    certRecGuardado.value = l.cert_rec_url
}, { immediate: true })

// ── Agregar nueva ley ─────────────────────────────────────────────────────────
const modalAgregarLey = ref(false)
const cipSeleccionado = ref('')
const modoModalLey    = ref<'normal' | 'dirimencia'>('normal')

const cipsDisponiblesLey = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(
    c => c.tipo_muestra === 'Laboratorio'
      && !lote.value!.analisis_ley.some(a => a.cip === c.codigo_cip),
  )
})

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

function confirmarAgregarLey() {
  if (!cipSeleccionado.value) return
  const tipoPorUrl = modoModalLey.value === 'dirimencia' ? 'dirimencia' : 'externo'
  if (store.puedeImportarCert) {
    router.push(`/laboratorio/importar-ley/${cipSeleccionado.value}?ip=${ipActual}&tipo=${tipoPorUrl}`)
  } else {
    router.push(`/laboratorio/ley/${cipSeleccionado.value}?tipo=${tipoPorUrl}`)
  }
}

// ── Recuperación ──────────────────────────────────────────────────────────────
const modalRecup           = ref(false)
const cipRecupElegido      = ref<string | null>(null)
const labRecupElegida      = ref('')
const labsRecupDisponibles = ref<string[]>([])

const cipsRecuperacionDisponibles = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(
    c => (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno')
      && !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente),
  )
})

const cipRecupInterno = computed(() =>
  lote.value?.cips_detalle.find(
    c => c.tipo_muestra === 'RecuperacionInterno'
      && !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente),
  ),
)

const tienePendiente = computed(() =>
  lote.value?.analisis_recuperacion.some(a => a.estado === 'PENDIENTE' && a.vigente) ?? false,
)

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

function abrirModalRecup() {
  console.log('Ley Cabeza para recuperación:', ley_cabeza.value)
  cipRecupElegido.value = cipsRecuperacionDisponibles.value[0]?.codigo_cip ?? null
  labRecupElegida.value = cipsRecuperacionDisponibles.value[0]?.laboratorio
    ?? labsRecupDisponibles.value[0] ?? 'Paititi'
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
  const esInterno = labRecupElegida.value === 'El Dorado - Invermin Paititi' || labRecupElegida.value === 'Laboratorio Interno'
  if (esInterno) {
    await store.enviarRecuperacion(ipActual, { cip: cipRecupElegido.value, laboratorio: labRecupElegida.value, ley_cabeza: ley_cabeza.value })
  } else {
    try {
      const cips = await muestreoApi.obtenerEtiquetas(ipActual)
      const cipConId = cips.find(c => c.codigo_cip === cipRecupElegido.value)
      if (cipConId) await muestreoApi.actualizarLaboratorioCip(cipConId.id, labRecupElegida.value)
      ui.toast(`CIP marcado para ${labRecupElegida.value}. Suba el certificado cuando lo reciba.`, 'info')
    } catch {
      ui.toast('Error al asignar laboratorio', 'error')
    }
  }
  enviando.value = false
  lote.value = await store.cargarDetalleLote(ipActual)
}

// ── Alertas ───────────────────────────────────────────────────────────────────
const alertaDirimencia = computed(() => {
  if (!lote.value?.ley_planta || !lote.value?.ley_minero) return null
  if (lote.value.tiene_dirimencia) return null
  const diff = Math.abs(Number(lote.value.ley_planta) - Number(lote.value.ley_minero))
  return diff > 0.10 ? diff : null
})

// ── Ley minero ────────────────────────────────────────────────────────────────
const modalLeyMinero      = ref(false)
const guardandoLeyMinero  = ref(false)
const extrayendoMinero    = ref(false)
const archivoMinero       = ref<File | null>(null)
const errOcrMinero        = ref('')
const formLeyMinero = ref({
  laboratorio:    '',
  ley_fino:       null as number | null,
  ley_grueso:     null as number | null,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

async function extraerCertMinero(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  archivoMinero.value = file
  errOcrMinero.value = ''
  extrayendoMinero.value = true
  try {
    const res = await laboratorioApi.extraerCertificadoLey(file, formLeyMinero.value.laboratorio)
    if (res.ley_fino != null)    formLeyMinero.value.ley_fino    = res.ley_fino
    if (res.ley_grueso != null)  formLeyMinero.value.ley_grueso  = res.ley_grueso
    if (res.fecha_analisis)      formLeyMinero.value.fecha_analisis = res.fecha_analisis
    if (res.laboratorio && !formLeyMinero.value.laboratorio) formLeyMinero.value.laboratorio = res.laboratorio
    if (!res.ley_fino && !res.ley_grueso)
      errOcrMinero.value = 'No se pudieron extraer las leyes. Ingrese los valores manualmente.'
  } catch {
    errOcrMinero.value = 'Error al procesar el certificado. Ingrese los valores manualmente.'
  } finally {
    extrayendoMinero.value = false
  }
}

async function guardarLeyMinero() {
  if (!formLeyMinero.value.laboratorio.trim()) {
    ui.toast('Ingrese el nombre del laboratorio o minero', 'error'); return
  }
  if (formLeyMinero.value.ley_fino == null || formLeyMinero.value.ley_grueso == null) {
    ui.toast('Ingrese ambas leyes (fino y grueso)', 'error'); return
  }
  guardandoLeyMinero.value = true
  try {
    const nuevo = await laboratorioApi.registrarLeyPorIP(ipActual, {
      tipo_analisis:  'minero',
      laboratorio:    formLeyMinero.value.laboratorio,
      ley_fino:       formLeyMinero.value.ley_fino,
      ley_grueso:     formLeyMinero.value.ley_grueso,
      fecha_analisis: formLeyMinero.value.fecha_analisis,
    })
    if (archivoMinero.value) await laboratorioApi.subirCertificadoLey(nuevo.id, archivoMinero.value)
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

// ── Eliminar (soft delete) ────────────────────────────────────────────────────
async function eliminarLey(id: number) {
  const ok = await store.eliminarLey(id)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

async function eliminarRecuperacion(id: number) {
  const ok = await store.eliminarRecuperacion(id)
  if (ok) lote.value = await store.cargarDetalleLote(ipActual)
}

// ── Adjuntar certificados ─────────────────────────────────────────────────────
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

// ── Visor PDF ─────────────────────────────────────────────────────────────────
async function verCertificado(ruta: string | null | undefined) {
  if (!ruta) return
  try {
    const url = await laboratorioApi.obtenerUrlArchivoVirtual(ruta)
    window.open(url, '_blank')
  } catch {
    ui.toast('Error al descargar o visualizar el documento', 'error')
  }
}

// ── Remuestreo ────────────────────────────────────────────────────────────────
async function solicitarRemuestreo() {
  const ok = await ui.showConfirm({
    title: 'Solicitar Remuestreo',
    message: `Se creará un nuevo registro de prueba metalúrgica para ${ipActual}. `
      + 'El registro anterior se conserva para auditoría. ¿Confirmar?',
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

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(d?: string | null) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function tipoBadge(tipo: string) {
  const m: Record<string, string> = {
    planta: 'LAB INTERNO', externo: 'LAB EXTERNO', minero: 'LEY MINERO', dirimencia: 'DIRIMENCIA',
  }
  return m[tipo] ?? tipo.toUpperCase()
}

function toggleTab() {
  tabActual.value = tabActual.value === 'ley' ? 'rec' : 'ley'
}

// ── Carga inicial ─────────────────────────────────────────────────────────────
onMounted(async () => {
  cargando.value = true
  ;[lote.value, labsRecupDisponibles.value] = await Promise.all([
    store.cargarDetalleLote(ipActual),
    muestreoApi.listarLaboratorios().catch(() => ['Paititi', 'Minares South S.R.L.', 'El Dorado', 'Otro']),
  ])
  cargando.value = false
})
</script>

<style scoped>
.detalle-row-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
.detalle-item { display: flex; flex-direction: column; gap: 0.15rem; }
.di-label {
  font-size: 0.68rem; color: var(--color-text-faint);
  font-family: var(--font-mono); letter-spacing: 0.06em; text-transform: uppercase;
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
  transition: opacity 0.15s, border-color 0.15s;
}
.lab-card.descartado  { opacity: 0.45; border-style: dashed; }
.lab-card.excluido-local { opacity: 0.55; border-color: rgba(239,68,68,0.35); border-style: dashed; }

.lab-card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding-bottom: 0.5rem; border-bottom: 1px solid var(--color-border);
}
.lab-titulo {
  font-family: var(--font-mono); font-size: 0.72rem;
  letter-spacing: 0.08em; color: var(--color-text-muted); text-transform: uppercase;
}
.badge-excluido {
  font-size: 0.62rem; padding: 0.1rem 0.4rem;
  background: rgba(239,68,68,0.12); color: #f87171;
  border: 1px solid rgba(239,68,68,0.3); border-radius: 3px;
  font-family: var(--font-mono);
}

.lab-field { display: flex; justify-content: space-between; align-items: center; }
.lf-label { font-size: 0.68rem; color: var(--color-text-faint); font-family: var(--font-mono); letter-spacing: 0.05em; }
.lf-value { font-family: var(--font-mono); color: var(--color-text-muted); font-size: var(--text-md); }
.lf-value.highlight { color: var(--color-gold); font-size: var(--text-lg); }

.lab-card-footer {
  display: flex; gap: 0.5rem; flex-wrap: wrap;
  margin-top: auto; padding-top: 0.5rem; border-top: 1px solid var(--color-border);
}

.btn-danger-sm {
  font-size: 0.72rem; padding: 0.25rem 0.65rem;
  background: rgba(239,68,68,0.12); color: #f87171;
  border: 1px solid rgba(239,68,68,0.3); border-radius: 4px; cursor: pointer;
}
.btn-secondary-sm {
  font-size: 0.72rem; padding: 0.25rem 0.65rem;
  background: transparent; color: var(--color-text-muted);
  border: 1px solid var(--color-border); border-radius: 4px; cursor: pointer;
}
.btn-excluir-sm {
  font-size: 0.72rem; padding: 0.25rem 0.65rem;
  background: transparent; color: var(--color-text-muted);
  border: 1px solid var(--color-border); border-radius: 4px; cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.btn-excluir-sm--activo {
  background: rgba(239,68,68,0.12); color: #f87171; border-color: rgba(239,68,68,0.3);
}

.link-cert { font-size: 0.75rem; color: var(--color-gold); text-decoration: underline; cursor: pointer; }

.acciones-lote {
  display: flex; gap: 0.75rem; flex-wrap: wrap;
  align-items: center; margin: 0.5rem 0 1.5rem;
}
.info-inline { font-size: var(--text-sm); color: var(--color-text-faint); font-family: var(--font-mono); }

.dirimencia-alert {
  background: rgba(168,85,247,0.12); border: 1px solid rgba(168,85,247,0.4);
  border-radius: 6px; padding: 0.75rem 1rem; color: #c084fc; font-size: var(--text-sm);
}
.dirimencia-request-alert {
  background: rgba(234,179,8,0.10); border: 1px solid rgba(234,179,8,0.45);
  border-radius: 6px; padding: 0.75rem 1rem; color: #fbbf24; font-size: var(--text-sm);
  margin-bottom: 1rem; display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem;
}

.info-box { border-radius: 6px; padding: 0.75rem 1rem; font-size: var(--text-sm); margin-bottom: 1rem; }
.info-box.warning { background: rgba(234,179,8,0.08); border: 1px solid rgba(234,179,8,0.3); color: #fbbf24; }

.lc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.75rem; margin-bottom: 0.5rem; }
.lc-item { display: flex; flex-direction: column; gap: 0.15rem; }
.lc-label { font-size: 0.68rem; color: var(--color-text-faint); font-family: var(--font-mono); letter-spacing: 0.05em; text-transform: uppercase; }
.lc-valor { font-size: var(--text-md); color: var(--color-text); }
.lc-valor.mono { font-family: var(--font-mono); }
.lc-valor.gold { color: var(--color-gold); font-size: var(--text-lg); font-weight: 600; }

.badge-simulando {
  font-size: 0.6rem; padding: 0.1rem 0.4rem;
  background: rgba(234,179,8,0.15); color: #fbbf24;
  border: 1px solid rgba(234,179,8,0.35); border-radius: 3px;
  font-family: var(--font-mono); letter-spacing: 0.08em;
  vertical-align: middle; margin-left: 0.4rem;
}

.cert-guardado-info {
  font-size: 0.78rem; color: var(--color-success);
  margin-top: 0.6rem; padding: 0.4rem 0.75rem;
  background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25); border-radius: 5px;
}

.alerta-inline {
  color: var(--color-warning, #d97706);
  font-size: 0.82rem;
  font-weight: 500;
}

/* Descarte preview (modal confirmar+generar) */
.descarte-preview {
  background: rgba(239,68,68,0.06);
  border: 1px solid rgba(239,68,68,0.25);
  border-radius: 6px;
  padding: 0.85rem 1rem;
  margin-bottom: 0.25rem;
}
.dp-titulo { font-family: var(--font-mono); font-size: 0.66rem; letter-spacing: 0.1em; color: var(--color-text-faint); margin-bottom: 0.5rem; }
.dp-row { display: flex; justify-content: space-between; margin-bottom: 0.25rem; }
.dp-label { font-size: 0.78rem; color: var(--color-text-muted); }
.dp-val { font-family: var(--font-mono); font-size: 0.82rem; color: var(--color-text); }
.dp-val--changed { color: #f59e0b; font-weight: 600; }

.btn-warning-sm {
  font-size: 0.72rem; padding: 0.25rem 0.65rem;
  background: rgba(234,179,8,0.15); color: #fbbf24;
  border: 1px solid rgba(234,179,8,0.4); border-radius: 4px; cursor: pointer;
}
</style>
