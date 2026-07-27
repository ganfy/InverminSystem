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
        </div>

        <div v-if="lote.tiene_dirimencia" class="dirimencia-alert" style="margin-top:0.75rem">
          <AlertTriangle :size="16" /> Este lote tiene análisis de dirimencia - prevalece sobre todos los demás
        </div>
      </section>

      <!-- ═══════════════════════════════════════ TAB LEY ═══════════════════════════════════════ -->
      <template v-if="tabActual === 'ley'">

        <!-- Toggle Au / Ag -->
        <div class="material-toggle-bar">
          <span class="mtog-label">MATERIAL:</span>
          <div class="mtog-group">
            <button :class="['mtog-btn', { active: materialFiltro === 'Au' }]" @click="materialFiltro = 'Au'">Au — Oro</button>
            <button :class="['mtog-btn', 'mtog-btn--ag', { active: materialFiltro === 'Ag' }]" @click="materialFiltro = 'Ag'"><span class="ag-dot" style="margin-right:0.2rem">Ag</span> Plata</button>
          </div>
          <span v-if="materialFiltro === 'Ag' && leyAgDesdeRecuperacion" class="ag-registered">
            <span class="ag-dot">Ag</span>
            {{ Number(leyAgDesdeRecuperacion).toFixed(3) }} Gr/TM
          </span>
        </div>

        <div class="labs-grid">
          <div
            v-for="a in analisisFiltrado"
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
            <!-- Au: triple sampling con ambas unidades -->
            <template v-if="a.material !== 'Ag'">
              <div class="lab-field">
                <span class="lf-label">MALLA +140:</span>
                <span class="lf-value">
                  {{ fmtOz(a.ley_grueso) }} oz/TC
                  <span class="lf-unit-alt">/ {{ ozToGt(a.ley_grueso) }} g/TM</span>
                </span>
              </div>
              <div class="lab-field">
                <span class="lf-label">MALLA −140:</span>
                <span class="lf-value">
                  {{ fmtOz(a.ley_fino) }} oz/TC
                  <span class="lf-unit-alt">/ {{ ozToGt(a.ley_fino) }} g/TM</span>
                </span>
              </div>
              <div class="lab-field">
                <span class="lf-label">LEY Au (OZ/TC):</span>
                <span class="lf-value highlight">{{ fmtOz(a.ley_final) }}</span>
              </div>
              <div class="lab-field">
                <span class="lf-label">LEY Au (GR/TM):</span>
                <span class="lf-value" style="color:var(--color-gold)">{{ fmtGt(a.ley_gr_tm) }}</span>
              </div>
            </template>

            <!-- Ag: ley directa -->
            <template v-else>
              <div class="lab-field">
                <span class="lf-label">LEY Ag (OZ/TC):</span>
                <span class="lf-value highlight" style="color:#60a5fa">{{ fmtOz(a.ley_final) }}</span>
              </div>
              <div class="lab-field">
                <span class="lf-label">LEY Ag (G/TM):</span>
                <span class="lf-value" style="color:#93c5fd">{{ fmtGt(a.ley_gr_tm) }}</span>
              </div>
            </template>

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

          <div v-if="analisisFiltrado.length === 0" class="estado-tabla sin-datos">
            Sin análisis de {{ materialFiltro === 'Au' ? 'oro' : 'plata' }} registrados
          </div>
        </div>

        <section class="card" v-if="tieneAnalisisLeyVigente">
          <h2 class="card-titulo" style="display:flex;justify-content:space-between;align-items:center">
            <span>
              LEY PLANTA
              <span v-if="excluidos.size > 0" class="badge-simulando">SIMULANDO</span>
            </span>
            <div style="display:flex; flex-direction: column; align-items: flex-end; gap:0.5rem">
              <!-- Selección de columnas -->
              <div style="display:flex; gap:0.75rem; font-size:0.75rem; color:var(--color-text); margin-bottom: 0.25rem;">
                <label style="display:flex; align-items:center; gap:0.25rem; cursor:pointer">
                  <input type="checkbox" value="ley_au_oz" v-model="columnasCertLey" /> Au (Oz/Tc)
                </label>
                <label style="display:flex; align-items:center; gap:0.25rem; cursor:pointer">
                  <input type="checkbox" value="ley_au_gr" v-model="columnasCertLey" /> Au (g/TM)
                </label>
                <label style="display:flex; align-items:center; gap:0.25rem; cursor:pointer">
                  <input type="checkbox" value="ley_ag_oz" v-model="columnasCertLey" /> Ag (Oz/Tc)
                </label>
                <label style="display:flex; align-items:center; gap:0.25rem; cursor:pointer">
                  <input type="checkbox" value="ley_ag_gr" v-model="columnasCertLey" /> Ag (g/TM)
                </label>
              </div>

              <div style="display:flex;gap:0.5rem">
                <button
                  class="btn-secondary"
                  style="font-size:0.75rem;padding:0.35rem 0.9rem"
                  @click="previsualizarCertLey"
                  :disabled="previsualizandoLey || leyPlantaSimulada === null || columnasCertLey.length === 0"
                  title="Abrir previsualización del certificado"
                >
                <span v-if="previsualizandoLey" class="spinner" style="margin-right:0.4rem"></span>
                <span v-else><Eye /> Previsualizar</span>
              </button>
              <button
                v-if="certLeyGuardado"
                class="btn-secondary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="verCertificado(certLeyGuardado)"
                title="Ver el último PDF generado"
              >
                <File /> Ver último PDF
              </button>
              <button
                v-if="!certLeyGuardado || puedeRegenerarCerts"
                class="btn-primary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="abrirConfirmarGenerar"
                :disabled="generando || leyPlantaSimulada === null"
                :title="certLeyGuardado ? 'Regenerar certificado (sobreescribe el anterior)' : 'Guardar certificado PDF definitivo'"
              >
                  <span v-if="generando" class="spinner" style="margin-right:0.4rem"></span>
                  {{ certLeyGuardado ? 'Regenerar PDF' : 'Guardar PDF definitivo' }}
                </button>
              </div>
            </div>
          </h2>

          <div v-if="cargandoLeyComercial" class="estado-tabla">
            <span class="spinner" style="margin-right:0.5rem"></span> Calculando...
          </div>

          <template v-else-if="leyComercialCalc">
            <div class="lc-grid">
              <!-- Ley Planta — solo lab propio -->
              <div class="lc-item">
                <span class="lc-label">
                  LEY PLANTA
                  <span style="font-size:0.7rem;color:var(--color-text-faint)">(lab propio)</span>
                  <span v-if="excluidos.size > 0" class="badge-simulando" style="margin-left:0.4rem;font-size:0.6rem">SIM</span>
                </span>
                <span class="lc-valor mono" :class="{ gold: excluidos.size === 0 }">
                  {{ leyPlantaSoloSimulada != null ? Number(leyPlantaSoloSimulada).toFixed(4) : '-' }} oz/TC
                  <span v-if="excluidos.size > 0 && leyComercialCalc?.ley_planta_solo != null"
                    style="font-size:0.7rem;color:var(--color-text-faint);margin-left:0.35rem">
                    (antes: {{ Number(leyComercialCalc.ley_planta_solo).toFixed(4) }})
                  </span>
                </span>
              </div>

              <!-- Ley Externo — labs externos (si hay) -->
              <div class="lc-item" v-if="leyComercialCalc?.ley_externo != null">
                <span class="lc-label">
                  LEY EXTERNO
                  <span style="font-size:0.7rem;color:var(--color-text-faint)">(labs externos)</span>
                </span>
                <span class="lc-valor mono">{{ Number(leyComercialCalc.ley_externo).toFixed(4) }} oz/TC</span>
              </div>

              <div v-if="leyComercialCalc?.ley_externo != null"
                style="grid-column:1/-1;border-top:1px dashed var(--color-border);opacity:0.4;margin:0.1rem 0" />

              <!-- Ley Comercial -->
              <div class="lc-item">
                <span class="lc-label">
                  LEY COMERCIAL
                  <span style="font-size:0.7rem;color:var(--color-text-faint)">(a entregar)</span>
                </span>
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

              <!-- Ley Minero -->
              <div class="lc-item" v-if="leyComercialCalc?.ley_minero != null">
                <span class="lc-label">LEY MINERO:</span>
                <span class="lc-valor mono">{{ Number(leyComercialCalc.ley_minero).toFixed(4) }} oz/TC</span>
              </div>

              <div v-if="leyComercialCalc?.ley_promedio != null"
                style="grid-column:1/-1;border-top:1px solid var(--color-border);opacity:0.5;margin:0.1rem 0" />

              <!-- Ley Promedio — resultado final para liquidación -->
              <div class="lc-item" v-if="leyComercialCalc?.ley_promedio != null">
                <span class="lc-label">
                  LEY PROMEDIO
                  <span v-if="leyComercialCalc.tiene_dirimencia"
                    style="font-size:0.7rem;color:var(--color-warning);margin-left:0.3rem">
                    (clamp dirimencia)
                  </span>
                  <span v-else style="font-size:0.7rem;color:var(--color-text-faint);margin-left:0.3rem">
                    (comercial + minero) / 2
                  </span>
                </span>
                <span class="lc-valor mono" style="color:var(--color-gold);font-weight:700;font-size:1.05em">
                  {{ Number(leyComercialCalc.ley_promedio).toFixed(4) }} oz/TC
                </span>
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
            ✓ Certificado de ley generado
            <span v-if="!puedeRegenerarCerts" style="font-size:0.72rem;color:var(--color-text-faint);margin-left:0.4rem">
              — solo Admin y Gerencia pueden regenerarlo
            </span>
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
          <button v-if="materialFiltro === 'Au'" class="btn-primary" @click="abrirModalAgregarLeyNormal">
            + Registrar nueva ley
          </button>
          <button v-if="materialFiltro === 'Ag'" class="btn-primary btn-ag" @click="abrirModalAgregarLeyAg">
            <span class="ag-dot">Ag</span> Registrar Ley Ag
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
                de la ley comercial, se habilitará la solicitud de dirimencia.
              </p>

              <!-- Certificado opcional -->
              <div class="field" style="margin-bottom:0.75rem">
                <label class="field-label">
                  CERTIFICADO
                  <span style="font-weight:400;opacity:.65;margin-left:0.3rem">(opcional — pre-llena los campos)</span>
                </label>
                <label
                  class="upload-zone-sm"
                  :class="{ uploading: extrayendoMinero }"
                  style="display:flex;align-items:center;gap:0.5rem;padding:0.6rem 0.75rem;
                        border:1px dashed var(--color-border);border-radius:6px;cursor:pointer"
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

              <!-- Laboratorio con autocomplete -->
              <div class="field" style="margin-bottom:0.75rem">
                <label class="field-label">LABORATORIO / ORIGEN</label>
                <input
                  class="field-input"
                  v-model="formLeyMinero.laboratorio"
                  list="labs-minero-list"
                  placeholder="Ej: Laboratorio del Minero"
                  autocomplete="off"
                />
                <datalist id="labs-minero-list">
                  <option v-for="lab in labsConocidos" :key="lab" :value="lab" />
                </datalist>
              </div>

              <!-- Toggle: modo de ingreso -->
              <div style="display:flex;gap:0;margin-bottom:0.75rem;border:1px solid var(--color-border);border-radius:6px;overflow:hidden">
                <button
                  type="button"
                  class="btn-toggle-tab"
                  :class="{ active: !formLeyMinero.modoFinal }"
                  style="flex:1;padding:0.45rem;font-size:0.78rem;border:none;cursor:pointer;
                        background:transparent;transition:background .15s"
                  @click="toggleModoFinal(false)"
                >
                  Fino + Grueso
                </button>
                <button
                  type="button"
                  class="btn-toggle-tab"
                  :class="{ active: formLeyMinero.modoFinal }"
                  style="flex:1;padding:0.45rem;font-size:0.78rem;border:none;border-left:1px solid var(--color-border);
                        cursor:pointer;background:transparent;transition:background .15s"
                  @click="toggleModoFinal(true)"
                >
                  Solo Ley Final
                </button>
              </div>

              <!-- Modo: Fino + Grueso -->
              <template v-if="!formLeyMinero.modoFinal">
                <div class="form-grid" style="grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:0.75rem">
                  <div class="field">
                    <label class="field-label">LEY FINO — malla -140 (Oz/TC)</label>
                    <input type="number" class="field-input" style="font-family:var(--font-mono)"
                      v-model.number="formLeyMinero.ley_fino"
                      step="0.0001" min="0" placeholder="0.0000" />
                  </div>
                  <div class="field">
                    <label class="field-label">LEY GRUESO — malla +140 (Oz/TC)</label>
                    <input type="number" class="field-input" style="font-family:var(--font-mono)"
                      v-model.number="formLeyMinero.ley_grueso"
                      step="0.0001" min="0" placeholder="0.0000" />
                  </div>
                </div>

                <!-- Preview ley_final calculada -->
                <div
                  v-if="formLeyMinero.ley_final != null"
                  style="background:var(--color-bg-alt);border:1px solid var(--color-border);border-radius:6px;
                        padding:0.5rem 0.75rem;margin-bottom:0.75rem;display:flex;
                        justify-content:space-between;align-items:center"
                >
                  <span style="font-size:0.78rem;color:var(--color-text-muted)">LEY FINAL (fino + grueso):</span>
                  <span style="font-family:var(--font-mono);color:var(--color-gold);font-weight:600">
                    {{ formLeyMinero.ley_final.toFixed(4) }} oz/TC
                  </span>
                </div>
              </template>

              <!-- Modo: Solo Ley Final -->
              <template v-else>
                <div class="field" style="margin-bottom:0.75rem">
                  <label class="field-label">LEY FINAL (Oz/TC)</label>
                  <input
                    type="number"
                    class="field-input"
                    style="font-family:var(--font-mono);font-size:1.05em"
                    v-model.number="formLeyMinero.ley_final"
                    step="0.0001" min="0" placeholder="0.0000"
                  />
                  <p style="font-size:0.75rem;color:var(--color-text-faint);margin-top:0.3rem">
                    Se registrará como ley_fino = ley_final, ley_grueso = 0.
                  </p>
                </div>
              </template>

              <!-- Fecha -->
              <div class="field">
                <label class="field-label">FECHA ANÁLISIS</label>
                <input type="date" class="field-input" v-model="formLeyMinero.fecha_analisis" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="modalLeyMinero = false">Cancelar</button>
              <button
                class="btn-primary"
                :disabled="!formLeyMinero.fecha_analisis || formLeyMinero.ley_fino == null || formLeyMinero.ley_grueso == null || guardandoLeyMinero"
                @click="guardarLeyMinero"
              >
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

        <div class="labs-grid" v-if="analisisRecuperacionList.length > 0">
          <div
            v-for="(a, i) in analisisRecuperacionList"
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

            <div v-if="a.estado === 'PENDIENTE'" class="lab-field" style="color:#f59e0b;font-size:0.75rem;margin-bottom:0.15rem">
              <Hourglass :size="13" style="margin-right:0.3rem;flex-shrink:0" />
              <span>Análisis en proceso — esperando resultado del laboratorio</span>
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
              <span class="lf-value highlight">{{ a.recuperacion != null ? Number(a.recuperacion).toFixed(2) + '%' : '-' }}</span>
            </div>
            <div class="lab-field" v-if="a.solucion_ag_g_m3 != null">
              <span class="lf-label">Ag SOLUCIÓN:</span>
              <span class="lf-value" style="color:#60a5fa">
                {{ Number(a.solucion_ag_g_m3).toFixed(4) }} g/m³
              </span>
            </div>

            <div
              v-if="a.ley_cola !== null && a.ley_cabeza !== null && Number(a.ley_cola) >= Number(a.ley_cabeza)"
              class="alerta-warning"
              style="margin-top:0.5rem; display:flex; align-items:center; gap:0.5rem"
            >
              <AlertTriangle :size="14" />
              <span>Advertencia: Ley cola mayor o igual a ley cabeza</span>
            </div>

            <div v-if="a.certificado_url" class="lab-field">
              <span class="lf-label">CERTIFICADO:</span>
              <a href="#" @click.prevent="verCertificado(a.certificado_url)" class="link-cert">Ver PDF</a>
            </div>

            <div class="lab-card-footer" v-if="!a.eliminado && !a.agrupado">
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
            <button
              class="btn-danger-sm"
              style="font-size:0.72rem;padding:0.25rem 0.65rem"
              @click="cancelarEnvioExterno(c.codigo_cip)"
              title="Revertir destino — el CIP vuelve a estar disponible"
            >
              Cancelar envío
            </button>
          </div>
        </div>

        <!-- Sección: certificado de recuperación comercial -->
        <section class="card" v-if="tieneRecuperacionVigente">
          <h2 class="card-titulo" style="display:flex;justify-content:space-between;align-items:center">
            <span>CERTIFICADO DE RECONOCIMIENTO</span>
            <div style="display:flex;gap:0.5rem;align-items:center">
              <button
                v-if="certReconocimientoGuardado"
                class="btn-secondary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="verCertificado(certReconocimientoGuardado)"
                title="Ver el último PDF generado"
              >
                <File /> Ver último PDF
              </button>
              <button
                v-if="!certReconocimientoGuardado || puedeRegenerarCerts"
                class="btn-primary"
                style="font-size:0.75rem;padding:0.35rem 0.9rem"
                @click="guardarCertReconocimientoFn"
                :disabled="guardandoReconocimiento"
                :title="certReconocimientoGuardado ? 'Regenerar certificado' : 'Guardar certificado PDF definitivo'"
              >
                <span v-if="guardandoReconocimiento" class="spinner" style="margin-right:0.4rem"></span>
                {{ certReconocimientoGuardado ? 'Regenerar PDF' : 'Guardar PDF' }}
              </button>
            </div>
          </h2>
          <p style="font-size:0.8rem;color:var(--color-text-muted);margin-bottom:1rem">
            Certificado de reconocimiento de pulpa. Seleccione las columnas a incluir en el PDF:
          </p>
          <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;font-size:0.8rem;padding:0.75rem;background:var(--color-bg-alt);border:1px solid var(--color-border);border-radius:6px">
            <label style="display:flex;align-items:center;gap:0.4rem;cursor:pointer">
              <input type="checkbox" value="ley_cabeza_au" v-model="columnasReconocimiento" /> Ley Cabeza Au
            </label>
            <label style="display:flex;align-items:center;gap:0.4rem;cursor:pointer">
              <input type="checkbox" value="ley_cola_au" v-model="columnasReconocimiento" /> Ley Cola Au
            </label>
            <label style="display:flex;align-items:center;gap:0.4rem;cursor:pointer">
              <input type="checkbox" value="liquido_au" v-model="columnasReconocimiento" /> Ley Líquido Au
            </label>
            <label style="display:flex;align-items:center;gap:0.4rem;cursor:pointer">
              <input type="checkbox" value="ley_ag" v-model="columnasReconocimiento" /> Ley Cola Ag
            </label>
            <label style="display:flex;align-items:center;gap:0.4rem;cursor:pointer">
              <input type="checkbox" value="liquido_ag" v-model="columnasReconocimiento" /> Solución Ag
            </label>
            <label style="display:flex;align-items:center;gap:0.4rem;cursor:pointer">
              <input type="checkbox" value="recuperacion" v-model="columnasReconocimiento" /> % Recuperación
            </label>
          </div>
          <div v-if="certReconocimientoGuardado" class="cert-guardado-info">
            ✓ Certificado de reconocimiento generado
            <span v-if="!puedeRegenerarCerts" style="font-size:0.72rem;color:var(--color-text-faint);margin-left:0.4rem">
              — solo Admin y Gerencia pueden regenerarlo
            </span>
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

    <!-- Modal: registrar ley Ag -->
    <div v-if="modalAgAnalisisId !== null" class="modal-overlay" @click.self="modalAgAnalisisId = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2 style="display:flex;align-items:center;gap:0.5rem">
            <span class="ag-badge-modal">Ag</span> Registrar Ley de Plata
          </h2>
          <button class="btn-cerrar" @click="modalAgAnalisisId = null"><X :size="18" /></button>
        </div>
        <div class="modal-body">
          <p style="font-size:0.78rem;color:var(--color-text-muted);margin-bottom:1rem">
            Corrección en blanco: <code style="font-family:var(--font-mono)">0.1444 mg</code> (fija) ·
            Fórmula: <code style="font-family:var(--font-mono)">((Au+Ag − Au − 0.1444) × 1000) / Peso</code>
          </p>

          <div class="form-grid" style="grid-template-columns:1fr 1fr;margin-bottom:1rem">
            <div class="field">
              <label class="field-label">SEÑAL Au+Ag (mg) *</label>
              <input type="number" step="0.0001" min="0" class="field-input"
                v-model.number="formAg.au_ag_mg" placeholder="Ej: 2.3450" />
            </div>
            <div class="field">
              <label class="field-label">SEÑAL Au PURA (mg) *</label>
              <input type="number" step="0.0001" min="0" class="field-input"
                v-model.number="formAg.au_mg" placeholder="Ej: 0.1230" />
            </div>
            <div class="field">
              <label class="field-label">PESO MUESTRA (g) *</label>
              <input type="number" step="0.01" min="0.01" class="field-input"
                v-model.number="formAg.peso_muestra" placeholder="Ej: 29.16" />
            </div>
            <div class="field">
              <label class="field-label">LABORATORIO *</label>
              <input class="field-input" v-model="formAg.laboratorio" placeholder="Laboratorio" />
            </div>
            <div class="field" style="grid-column:1/-1">
              <label class="field-label">FECHA ANÁLISIS</label>
              <input type="date" class="field-input" v-model="formAg.fecha_analisis" />
            </div>
          </div>

          <!-- Preview -->
          <div v-if="previewAg" class="ag-preview-inline">
            <div class="ag-preview-row">
              <span class="ag-preview-label">Neto (mg)</span>
              <span class="ag-preview-val">{{ previewAg.neto.toFixed(4) }}</span>
            </div>
            <div class="ag-preview-row">
              <span class="ag-preview-label">Ley Ag (g/TM)</span>
              <span class="ag-preview-val" style="color:var(--color-gold);font-size:var(--text-lg)">
                {{ previewAg.ley_gr_tm.toFixed(3) }}
              </span>
            </div>
            <div class="ag-preview-row">
              <span class="ag-preview-label">Ley Ag (Oz/TC)</span>
              <span class="ag-preview-val">{{ previewAg.ley_oz_tc.toFixed(4) }}</span>
            </div>
          </div>

          <p v-if="agErr" class="error-msg" style="margin-top:0.75rem">{{ agErr }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="modalAgAnalisisId = null">Cancelar</button>
          <button
            class="btn-primary"
            :disabled="!previewAg || !formAg.laboratorio.trim() || agGuardando"
            @click="guardarAg"
          >
            <span v-if="agGuardando" class="spinner" style="margin-right:0.4rem"></span>
            Guardar Ley Ag
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
import { AlertTriangle, Eye, Hourglass, TriangleAlert, X, File} from 'lucide-vue-next'
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
const tabActual      = ref<'ley' | 'rec'>('ley')
const materialFiltro = ref<'Au' | 'Ag'>('Au')
const analisisAgCache = ref<import('@/types/laboratorio').AnalisisLeyOut[]>([])
const cargandoAg      = ref(false)

const analisisFiltrado = computed(() => {
  if (!lote.value) return []
  if (materialFiltro.value === 'Ag') return analisisAgCache.value
  return lote.value.analisis_ley.filter(a =>
    a.material !== 'Ag')
})

watch(materialFiltro, async (mat) => {
  if (mat === 'Ag' && analisisAgCache.value.length === 0) {
    cargandoAg.value = true
    try {
      const res = await laboratorioApi.detalleLote(ipActual, 'Ag')
      analisisAgCache.value = res.analisis_ley
    } catch {
      ui.toast('Error al cargar análisis Ag', 'error')
    } finally {
      cargandoAg.value = false
    }
  }
})

// ── Flujo ley: exclusión local + guardar ──────────────────────────────────────
const excluidos             = ref<Set<number>>(new Set())
const modalConfirmarGenerar = ref(false)
const justificacionGenerar  = ref('')
const generando             = ref(false)
const previsualizandoLey    = ref(false)
const certLeyGuardado       = ref<string | null>(null)

const ley_cabeza = ref<number | null>(null)

// ── Ag: modal inline ──────────────────────────────────────────────────────────
const modalAgAnalisisId = ref<number | null>(null)  // analisis Au sobre el que se registra Ag
const agGuardando       = ref(false)
const agErr             = ref('')
const formAg = ref({
  au_ag_mg:       null as number | null,
  au_mg:          null as number | null,
  peso_muestra:   null as number | null,
  laboratorio:    '',
  fecha_analisis: new Date().toISOString().split('T')[0],
})

// Helpers
function fmtOz(v: number | string | null | undefined): string {
  if (v == null) return '-'
  return Number(v).toFixed(4)   // oz/TC
}

// Convierte oz/TC → g/TM (para ley_fino y ley_grueso que vienen en oz/TC)
function ozToGt(v: number | string | null | undefined): string {
  if (v == null) return '-'
  return (Number(v) * 34.2857).toFixed(3)
}

// Formatea un valor ya en g/TM (ley_gr_tm que viene calculado del backend)
function fmtGt(v: number | string | null | undefined): string {
  if (v == null) return '-'
  return Number(v).toFixed(3)
}

const leyAgDesdeRecuperacion = computed(() => lote.value?.ley_ag_gr_tm ?? null)

function toggleExcluido(id: number) {
  const s = new Set(excluidos.value)
  s.has(id) ? s.delete(id) : s.add(id)
  excluidos.value = s
}

// Simula ley_planta_solo (solo tipo 'planta') para display con exclusiones
const leyPlantaSoloSimulada = computed<number | null>(() => {
  if (!lote.value) return null
  if (excluidos.value.size === 0)
    return leyComercialCalc.value?.ley_planta_solo ?? null
  const vigentes = lote.value.analisis_ley.filter(
    a => a.vigente && !a.eliminado && !excluidos.value.has(a.id)
      && a.tipo_analisis === 'planta' && a.material !== 'Ag',
  )
  if (vigentes.length === 0) return null
  const prom = vigentes.reduce((acc, a) => acc + Number(a.ley_final), 0) / vigentes.length
  return parseFloat(prom.toFixed(4))
})

// ¿Tiene algún análisis Au vigente (cualquier tipo)? Controla visibilidad del card
const tieneAnalisisLeyVigente = computed(() => {
  if (!lote.value) return false
  return lote.value.analisis_ley.some(
    a => a.vigente && !a.eliminado && a.material !== 'Ag',
  )
})

// Base para deshabilitar botones: average(planta+externo), o dirimencia como fallback
const leyPlantaSimulada = computed<number | null>(() => {
  if (!lote.value) return null
  if (excluidos.value.size === 0) {
    if (lote.value.ley_planta != null) return Number(lote.value.ley_planta)
    // Fallback para casos con solo dirimencia (legacy): usar ley_planta del endpoint
    return leyComercialCalc.value?.ley_planta ?? null
  }
  const vigentes = lote.value.analisis_ley.filter(
    a => a.vigente && !a.eliminado && !excluidos.value.has(a.id)
      && (a.tipo_analisis === 'planta' || a.tipo_analisis === 'externo')
      && a.material !== 'Ag',
  )
  if (vigentes.length === 0) return null
  const prom = vigentes.reduce((acc, a) => acc + Number(a.ley_final), 0) / vigentes.length
  return parseFloat(prom.toFixed(4))
})

const analisisADescartar = computed(() =>
lote.value?.analisis_ley.filter(a => excluidos.value.has(a.id)) ?? [],
)

// leyPromedio: (planta + minero) / 2, o ley dirimencia si tiene dirimencia
const leyPromedio = computed<number | null>(() => {
if (!lote.value) return null
if (lote.value.tiene_dirimencia && leyComercialCalc.value) {
  return leyComercialCalc.value.ley_comercial   // dirimencia prevalece
}
const planta = leyPlantaSimulada.value
const minero = lote.value.ley_minero != null ? Number(lote.value.ley_minero) : null
if (planta == null || minero == null) return null
return parseFloat(((planta + minero) / 2).toFixed(4))
})

function abrirConfirmarGenerar() {
  justificacionGenerar.value = ''
  modalConfirmarGenerar.value = true
}

async function previsualizarCertLey() {
  previsualizandoLey.value = true
  try {
    await laboratorioApi.previewCertificadoLeyPdf(ipActual, columnasCertLey.value)
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

  // Limpiar cache de Ag si se descartó alguno
  const hayAgDescartado = (lote.value?.analisis_ley ?? []).some(
    a => a.material === 'Ag' && a.eliminado
  )
  if (hayAgDescartado) {
    analisisAgCache.value = []
  }

  await recargarLeyComercial()

  generando.value = true
  try {
    const res = await laboratorioApi.guardarCertificadoLey(ipActual, columnasCertLey.value)
    certLeyGuardado.value = res.ruta
    ui.toast('Certificado guardado correctamente', 'success')
  } catch {
    ui.toast('Error al guardar certificado PDF', 'error')
  } finally {
    generando.value = false
  }
}

// Plata
const BLANK_AG = 0.1444
const previewAg = computed(() => {
  const { au_ag_mg, au_mg, peso_muestra } = formAg.value
  if (au_ag_mg == null || au_mg == null || !peso_muestra || peso_muestra <= 0) return null
  const neto      = Math.max(0, au_ag_mg - au_mg - BLANK_AG)
  const ley_gr_tm = parseFloat(((neto * 1000) / peso_muestra).toFixed(3))
  const ley_oz_tc = parseFloat((ley_gr_tm / 34.2857).toFixed(4))
  return { neto, ley_gr_tm, ley_oz_tc }
})

function abrirModalAg(analisisAuId: number, labDefault: string) {
  formAg.value = {
    au_ag_mg: null, au_mg: null, peso_muestra: null,
    laboratorio: labDefault,
    fecha_analisis: new Date().toISOString().split('T')[0],
  }
  agErr.value = ''
  modalAgAnalisisId.value = analisisAuId
}

async function guardarAg() {
  if (!modalAgAnalisisId.value || !previewAg.value) return
  const { au_ag_mg, au_mg, peso_muestra, laboratorio, fecha_analisis } = formAg.value
  if (!au_ag_mg || !au_mg || !peso_muestra || !laboratorio.trim()) {
    agErr.value = 'Complete todos los campos requeridos'; return
  }
  agGuardando.value = true
  agErr.value = ''
  try {
    await laboratorioApi.registrarLeyAg(modalAgAnalisisId.value, {
      au_ag_mg, au_mg, peso_muestra, laboratorio, fecha_analisis: fecha_analisis || null,
    })
    ui.toast(`Ley Ag registrada: ${previewAg.value.ley_gr_tm.toFixed(3)} g/TM`, 'success')
    modalAgAnalisisId.value = null
    lote.value = await store.cargarDetalleLote(ipActual)

    analisisAgCache.value = []  // forzar recarga en próxima visita al tab Ag
    // disparar recarga inmediata si seguimos en tab Ag
    if (materialFiltro.value === 'Ag') {
      const res = await laboratorioApi.detalleLote(ipActual, 'Ag')
      analisisAgCache.value = res.analisis_ley
    }
  } catch (e: any) {
    agErr.value = e?.response?.data?.detail ?? 'Error al guardar'
  } finally {
    agGuardando.value = false
  }
}

// ── Flujo rec: descartar + certificado ───────────────────────────────────────
const modalDescartarRec  = ref<number | null>(null)
const justificacionRec   = ref('')
const guardandoReconocimiento  = ref(false)
const certReconocimientoGuardado = ref<string | null>(null)
const columnasReconocimiento = ref<string[]>(['cabeza', 'cola', 'liquido', 'recuperacion', 'ag'])
const columnasCertLey = ref<string[]>(['ley_au_oz', 'ley_ag_oz'])

const tieneRecuperacionVigente = computed(() =>
  lote.value?.analisis_recuperacion.some(a => a.vigente && a.estado === 'COMPLETADO') ?? false
)

async function guardarCertReconocimientoFn() {
  guardandoReconocimiento.value = true
  try {
    const res = await laboratorioApi.guardarCertReconocimiento(ipActual, columnasReconocimiento.value)
    certReconocimientoGuardado.value = res.ruta
    ui.toast('Certificado de reconocimiento guardado', 'success')
  } catch (e: any) {
    ui.toast(e?.response?.data?.detail ?? 'Error al guardar certificado', 'error')
  } finally {
    guardandoReconocimiento.value = false
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
  if (l != null && tieneAnalisisLeyVigente.value && !leyComercialCalc.value) {
    cargandoLeyComercial.value = true
    try {
      leyComercialCalc.value = await laboratorioApi.getLeyComercial(ipActual)
    } catch { } finally {
      cargandoLeyComercial.value = false
    }
  }
}, { immediate: true })

async function recargarLeyComercial() {
  if (!tieneAnalisisLeyVigente.value) return
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

const puedeRegenerarCerts = computed(() => {
  const rol = auth.user?.rol
  return rol === 'Admin' || rol === 'Gerencia'
})

//watch para certificados
watch(lote, (l) => {
  if (l?.cert_ley_url)             certLeyGuardado.value = l.cert_ley_url
  if (l?.cert_reconocimiento_url)  certReconocimientoGuardado.value = l.cert_reconocimiento_url
  }, { immediate: true })

// ── Agregar nueva ley ─────────────────────────────────────────────────────────
const modalAgregarLey = ref(false)
const cipSeleccionado = ref('')
const modoModalLey    = ref<'normal' | 'dirimencia'>('normal')

const cipsDisponiblesLey = computed(() => {
  if (!lote.value) return []
  if (materialFiltro.value === 'Ag') {
    // Ag reutiliza CIPs de recuperación. Bloquear solo si ya hay Ag vigente en ese CIP.
    return lote.value.cips_detalle.filter(c =>
      c.tipo_muestra === 'RecuperacionInterno'
      && !lote.value!.analisis_ley.some(
        a => a.cip === c.codigo_cip && a.material === 'Ag' && a.vigente,
      ),
    )
  }
  // Au: CIPs Laboratorio sin análisis Au previo
  return lote.value.cips_detalle.filter(c =>
    c.tipo_muestra === 'Laboratorio'
    && !lote.value!.analisis_ley.some(a => a.cip === c.codigo_cip && a.material !== 'Ag'),
  )
})

function abrirModalAgregarLeyNormal() {
  modoModalLey.value = 'normal'
  cipSeleccionado.value = ''
  modalAgregarLey.value = true
}

function abrirModalAgregarLeyAg() {
  materialFiltro.value = 'Ag'
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
  const matQ = materialFiltro.value === 'Ag' ? '&material=Ag' : ''
  if (store.puedeImportarCert && materialFiltro.value !== 'Ag') {
    router.push(`/laboratorio/importar-ley/${cipSeleccionado.value}?ip=${ipActual}&tipo=${tipoPorUrl}`)
  } else {
    router.push(`/laboratorio/ley/${cipSeleccionado.value}?tipo=${tipoPorUrl}${matQ}`)
  }
}

// ── Recuperación ──────────────────────────────────────────────────────────────
const modalRecup           = ref(false)
const cipRecupElegido      = ref<string | null>(null)
const labRecupElegida      = ref('')
const labsRecupDisponibles = ref<string[]>([])

const internos = new Set(['Paititi', 'Laboratorio Interno', 'El Dorado - Invermin Paititi'])

const cipsRecuperacionDisponibles = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(
    c => (c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno')
      && !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente)
      && !(c.laboratorio && !internos.has(c.laboratorio)),  // bloqueado si ya envió a externo
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

const cipsExternosPendienteCert = computed(() => {
  if (!lote.value) return []
  return lote.value.cips_detalle.filter(c => {
    const esRec = c.tipo_muestra === 'RecuperacionInterno' || c.tipo_muestra === 'RecuperacionExterno'
    const tieneLabExterno = c.laboratorio && !internos.has(c.laboratorio)
    const sinVigente = !lote.value!.analisis_recuperacion.some(a => a.cip === c.codigo_cip && a.vigente)
    return esRec && tieneLabExterno && sinVigente
  })
})

const analisisRecuperacionList = computed(() => {
  if (!lote.value) return []
  if (!['Comercial', 'JefeComercial'].includes(auth.user?.rol ?? '')) return lote.value.analisis_recuperacion

  // Comercial view: agrupar por CIP para unificar SOLIDOS y SOLUCION
  const agrupados = new Map<string, any>()
  
  for (const a of lote.value.analisis_recuperacion) {
    if (!a.cip) {
      agrupados.set(`no-cip-${a.id}`, { ...a })
      continue
    }
    
    if (agrupados.has(a.cip)) {
      const existing = agrupados.get(a.cip)
      if (a.ley_cola !== null) existing.ley_cola = a.ley_cola
      if (a.ley_liquido !== null) existing.ley_liquido = a.ley_liquido
      if (a.recuperacion !== null) existing.recuperacion = a.recuperacion
      if (a.solucion_ag_g_m3 !== null) existing.solucion_ag_g_m3 = a.solucion_ag_g_m3
      if (a.estado === 'PENDIENTE') existing.estado = 'PENDIENTE'
      existing.agrupado = true
    } else {
      agrupados.set(a.cip, { ...a, agrupado: false })
    }
  }
  return Array.from(agrupados.values())
})

function getLeyAgPorCip(cip: string) {
  if (!lote.value) return '-'
  const ag = lote.value.analisis_ley.find(l => l.cip === cip && l.material === 'Ag' && l.vigente)
  return ag ? `${Number(ag.ley_fino).toFixed(4)}` : '-'
}

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

async function cancelarEnvioExterno(cipCodigo: string) {
  const ok = await ui.showConfirm({
    title: 'Cancelar envío externo',
    message: `¿Cancelar el envío de ${cipCodigo}? El CIP quedará disponible para asignar a otro destino.`,
    confirmLabel: 'Cancelar envío',
  })
  if (!ok) return
  try {
    const cips = await muestreoApi.obtenerEtiquetas(ipActual)
    const cipConId = cips.find(c => c.codigo_cip === cipCodigo)
    if (cipConId) await muestreoApi.actualizarLaboratorioCip(cipConId.id, '')
    lote.value = await store.cargarDetalleLote(ipActual)
    ui.toast('Envío cancelado. CIP disponible nuevamente.', 'success')
  } catch {
    ui.toast('Error al cancelar el envío', 'error')
  }
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
  ley_final:      null as number | null,
  modoFinal:      false,
  fecha_analisis: new Date().toISOString().split('T')[0],
})

const labsConocidos = computed<string[]>(() => {
  if (!lote.value) return []
  const nombres = lote.value.analisis_ley
    .map(a => a.laboratorio)
    .filter((l): l is string => !!l)
  return [...new Set(nombres)]
})


// Auto-calcular ley_final cuando cambian fino o grueso
watch(
  () => [formLeyMinero.value.ley_fino, formLeyMinero.value.ley_grueso],
  ([fino, grueso]) => {
    if (formLeyMinero.value.modoFinal) return
    if (fino != null && grueso != null)
      formLeyMinero.value.ley_final = parseFloat((fino + grueso).toFixed(4))
    else
      formLeyMinero.value.ley_final = null
  },
)

function toggleModoFinal(val: boolean) {
  formLeyMinero.value.modoFinal = val
  formLeyMinero.value.ley_final = null
  formLeyMinero.value.ley_fino = null
  formLeyMinero.value.ley_grueso = null
}
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
    // Si el cert solo trajo ley_final (sin fino/grueso), cambiar a modoFinal
    if (res.ley_fino == null && res.ley_grueso == null && res.ley_final != null) {
      formLeyMinero.value.modoFinal  = true
      formLeyMinero.value.ley_final  = res.ley_final
    }
    if (!res.ley_fino && !res.ley_grueso && !res.ley_final)
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

  let ley_fino: number
  let ley_grueso: number

  if (formLeyMinero.value.modoFinal) {
    if (!formLeyMinero.value.ley_final) {
      ui.toast('Ingrese la ley final', 'error'); return
    }
    ley_fino   = formLeyMinero.value.ley_final   // ley_final = ley_fino + 0
    ley_grueso = 0
  } else {
    if (formLeyMinero.value.ley_fino == null || formLeyMinero.value.ley_grueso == null) {
      ui.toast('Ingrese ambas leyes (fino y grueso)', 'error'); return
    }
    ley_fino   = formLeyMinero.value.ley_fino
    ley_grueso = formLeyMinero.value.ley_grueso
  }
  guardandoLeyMinero.value = true
  try {
    const nuevo = await laboratorioApi.registrarLeyPorIP(ipActual, {
      tipo_analisis:  'minero',
      laboratorio:    formLeyMinero.value.laboratorio,
      ley_fino,
      ley_grueso,
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

.btn-toggle-tab {
  color: var(--color-text-muted);
}
.btn-toggle-tab.active {
  background: var(--color-primary-muted, color-mix(in srgb, var(--color-gold) 15%, transparent));
  color: var(--color-gold);
  font-weight: 600;
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

/* Ag button - mismo shape que btn-primary, color índigo */
:deep(.btn-primary.btn-ag) {
  background: #4f46e5;
  color: #fff;
}
:deep(.btn-primary.btn-ag:not(:disabled)) {
  background: #4338ca;
}
:deep(.btn-primary.btn-ag:hover:not(:disabled)) {
  background: #6366f1;
}
.ag-dot {
  background: #6366f1; color: #fff;
  border-radius: 3px; padding: 0px 4px;
  font-size: 0.62rem; font-weight: 700;
}
.ag-registered {
  display: inline-flex; align-items: center; gap: 0.35rem;
  font-size: 0.72rem; color: #a5b4fc;
  font-family: var(--font-mono); padding: 0.25rem 0.5rem;
  background: rgba(99,102,241,0.08);
  border: 1px solid rgba(99,102,241,0.2); border-radius: 4px;
}
.ag-edit-btn {
  background: none; border: none; cursor: pointer;
  color: #818cf8; font-size: 0.8rem; padding: 0 0 0 2px;
}
.ag-badge-modal {
  background: #6366f1; color: #fff;
  border-radius: 4px; padding: 1px 8px;
  font-size: 0.8rem; font-weight: 700;
}
.ag-preview-inline {
  background: rgba(99,102,241,0.07);
  border: 1px solid rgba(99,102,241,0.25);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  display: flex; gap: 1.5rem; flex-wrap: wrap;
}
.ag-preview-row { display: flex; flex-direction: column; gap: 0.15rem; }
.ag-preview-label {
  font-size: 0.65rem; font-family: var(--font-mono);
  color: var(--color-text-faint); text-transform: uppercase; letter-spacing: 0.05em;
}
.ag-preview-val { font-family: var(--font-mono); font-size: var(--text-md); }
.lf-unit-alt {
  font-size: 0.65rem;
  color: var(--color-text-faint);
  margin-left: 0.3rem;
  font-family: var(--font-mono);
}

/* Material toggle Au/Ag */
.material-toggle-bar {
  display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
  margin-bottom: 0.75rem; padding: 0.4rem 0;
}
.mtog-label {
  font-size: 0.65rem; font-family: var(--font-mono);
  color: var(--color-text-faint); letter-spacing: 0.08em;
}
.mtog-group {
  display: flex; border: 1px solid var(--color-border); border-radius: 6px; overflow: hidden;
}
.mtog-btn {
  padding: 0.3rem 0.85rem; font-size: 0.75rem; font-family: var(--font-mono);
  background: transparent; color: var(--color-text-muted);
  border: none; cursor: pointer; transition: background 0.15s, color 0.15s;
}
.mtog-btn + .mtog-btn { border-left: 1px solid var(--color-border); }
.mtog-btn.active { background: rgba(184,151,75,0.15); color: var(--color-gold); font-weight: 600; }
.mtog-btn--ag.active { background: rgba(99,102,241,0.15); color: #a5b4fc; }

.alerta-warning {
  background: rgba(255, 160, 0, 0.1);
  border: 1px solid rgba(255, 160, 0, 0.4);
  border-radius: 4px;
  padding: 0.6rem 0.9rem;
  color: #ffa000;
  font-size: var(--text-sm);
}
</style>
