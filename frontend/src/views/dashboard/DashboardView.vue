<template>
  <div class="dashboard-page">

    <header class="page-header">
      <div class="header-title-row">
        <LayoutDashboard class="header-icon" :size="26" />
        <div>
          <h1 class="page-title">Dashboard</h1>
          <span class="last-sync" v-if="lastUpdate">Actualizado {{ lastUpdate }}</span>
        </div>
      </div>
      <button class="btn-secondary btn-refresh" @click="recargar" :disabled="cargando">
        <RefreshCw :size="16" :class="{ spinner: cargando }" style="margin-right:0.4rem" />
        ACTUALIZAR
      </button>
    </header>

    <section class="kpi-grid">
      <div 
        class="kpi-card gold-accent kpi-card-interactive" 
        :class="{ active: filtroKpi === 'au_real_100' }"
        @click="aplicarFiltroKpi('au_real_100')"
        title="Au Real 100%: Total de gramos de oro contenido. Fórmula: Σ(TMS × Ley Promedio gr/TM). Clic para ver los lotes que suman a esta métrica."
      >
        <div class="kpi-info">
          <span class="kpi-label">Au Real 100%</span>
          <span class="kpi-value">{{ data?.kpis.au_real_100 ? fmtNum(data.kpis.au_real_100) : '0.00' }}g</span>
        </div>
        <Zap class="kpi-icon" :size="32" />
      </div>
      <div 
        class="kpi-card gold-accent kpi-card-interactive"
        :class="{ active: filtroKpi === 'au_real_rec' }"
        @click="aplicarFiltroKpi('au_real_rec')"
        title="Au Real Rec.: Oro recuperable esperado. Fórmula: Σ(TMS × Ley Promedio gr/TM × % Recuperación). Clic para ver los lotes."
      >
        <div class="kpi-info">
          <span class="kpi-label">Au Real Rec.</span>
          <span class="kpi-value">{{ data?.kpis.au_real_rec ? fmtNum(data.kpis.au_real_rec) : '0.00' }}g</span>
        </div>
        <TrendingUp class="kpi-icon" :size="32" />
      </div>
      <div 
        class="kpi-card kpi-card-interactive"
        :class="{ active: filtroKpi === 'tmh_stock' }"
        @click="aplicarFiltroKpi('tmh_stock')"
        title="TMH en Stock: Total de Toneladas Métricas Húmedas. Clic para ver todos los lotes."
      >
        <div class="kpi-info">
          <span class="kpi-label">TMH en Stock</span>
          <span class="kpi-value highlight">{{ data?.kpis.tmh_stock.toFixed(2) }} TM</span>
        </div>
        <Scale class="kpi-icon" :size="32" />
      </div>
      <div 
        class="kpi-card kpi-card-interactive"
        :class="{ active: filtroKpi === 'tms_stock' }"
        @click="aplicarFiltroKpi('tms_stock')"
        title="TMS en Stock: Total de Toneladas Métricas Secas (descontando humedad). Clic para ver los lotes con humedad registrada."
      >
        <div class="kpi-info">
          <span class="kpi-label">TMS en Stock</span>
          <span class="kpi-value">{{ data?.kpis.tms_stock.toFixed(2) }} TM</span>
        </div>
        <Database class="kpi-icon" :size="32" />
      </div>
      <div 
        class="kpi-card kpi-card-interactive"
        :class="{ active: filtroKpi === 'oz_stock' }"
        @click="aplicarFiltroKpi('oz_stock')"
        title="Oz en Stock: Equivalente en onzas del Au Real 100%. Fórmula: (Au Real 100% / 31.1035). Clic para ver los lotes."
      >
        <div class="kpi-info">
          <span class="kpi-label">Oz en Stock</span>
          <span class="kpi-value">{{ data?.kpis.oz_stock.toFixed(2) }} oz</span>
        </div>
        <Coins class="kpi-icon" :size="32" />
      </div>

      <div 
        class="kpi-card kpi-card-interactive"
        :class="{ active: filtroKpi === 'oz_habilitados' }"
        @click="aplicarFiltroKpi('oz_habilitados')"
        title="Oz Disponibles Ruma: Onzas en lotes habilitados o volados que no han sido asignados a ninguna ruma. Clic para ver lotes."
      >
        <div class="kpi-info">
          <span class="kpi-label">Oz Disponibles Ruma</span>
          <span class="kpi-value highlight">{{ (data?.kpis.oz_habilitados ?? 0).toFixed(3) }} oz</span>
        </div>
        <Layers class="kpi-icon" :size="32" />
      </div>
    </section>

    <div class="tabs-bar">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: tabActual === tab.key }"
        @click="tabActual = tab.key"
      >
        <component :is="tab.icon" :size="15" style="margin-right:0.35rem" />
        {{ tab.label }}
        <span v-if="tab.count != null" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <div v-if="cargando" class="estado-tabla">
      <span class="spinner" style="margin-right:0.5rem" /> Cargando…
    </div>

    <template v-else-if="tabActual === 'lotes'">
      <div class="filtros-bar">
        <div class="field" style="width:160px">
          <label class="field-label">ESTADO</label>
          <select class="field-input field-select" v-model="filtroEstadoLote">
            <option value="">Todos</option>
            <option value="RECEPCIONADO">Recepcionado</option>
            <option value="ASIGNADO_RUMA">Asignado Ruma</option>
            <option value="LIQUIDADO">Liquidado</option>
            <option value="FACTURADO">Facturado</option>
            <option value="PAGADO">Pagado</option>
          </select>
        </div>
        <div class="field" style="width:160px">
          <label class="field-label">ANÁLISIS</label>
          <select class="field-input field-select" v-model="filtroAnalisis">
            <option value="">Todos</option>
            <option value="LISTO">Listo para liquidar</option>
            <option value="FALTA_MUESTREO">Falta humedad</option>
            <option value="FALTA_REC">Falta recuperación</option>
            <option value="FALTA_LEY">Falta ley</option>
            <option value="SIN_DATOS">Sin datos</option>
          </select>
        </div>
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <div class="search-wrapper">
            <Search :size="15" class="search-icon" />
            <input
              type="text"
              class="field-input search-input"
              v-model="busquedaLote"
              placeholder="IP, proveedor…"
            />
          </div>
        </div>

        <div style="display:flex;align-items:flex-end">
          <button class="btn-export" @click="exportarExcel('lotes')">
            <Download :size="13" /> Excel
          </button>
        </div>
      </div>
      <div class="table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>LOTE</th>
              <th class="align-right">TMH</th>
              <th class="align-right">TMS</th>
              <th class="align-right">%H₂O</th>
              <th>PROVEEDOR</th>
              <th>RUC</th>
              <th class="align-right">LEY PROM.</th>
              <th class="align-right">% REC.</th>
              <th>ACOPIADOR</th>
              <th class="align-center th-analisis">
                ANÁLISIS
                <span class="th-help-wrap">
                  <HelpCircle :size="12" class="th-help-icon" />
                  <div class="th-tooltip">
                    <div class="tooltip-row"><span class="t-badge t-listo">LISTO</span><span>Datos completos para liquidar</span></div>
                    <div class="tooltip-row"><span class="t-badge t-humedad">FALTA HUMEDAD</span><span>Sin resultado de muestreo</span></div>
                    <div class="tooltip-row"><span class="t-badge t-ley">FALTA LEY</span><span>Sin análisis de ley</span></div>
                    <div class="tooltip-row"><span class="t-badge t-rec">FALTA REC.</span><span>Sin análisis de recuperación</span></div>
                    <div class="tooltip-row"><span class="t-badge t-sin">SIN DATOS</span><span>Sin ningún dato registrado</span></div>
                  </div>
                </span>
              </th>
              <th class="align-center">ESTADO</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="lotesFiltrados.length === 0">
              <td colspan="11" class="empty-state">Sin lotes para los filtros seleccionados.</td>
            </tr>
            <tr
              v-for="lote in lotesFiltrados" :key="lote.ip"
              class="tabla-row"
              :class="[urgenciaFila(lote), canViewTrazabilidad ? 'clickable' : '']"
              :style="canViewTrazabilidad ? 'cursor:pointer' : ''"
              @click="canViewTrazabilidad && abrirTrazabilidad(lote.ip)"
            >
              <td class="td-mono gold">{{ lote.ip }}</td>
              <td class="align-right td-mono">{{ lote.tmh.toFixed(3) }}</td>
              <td class="align-right td-mono">{{ lote.tms?.toFixed(3) ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.h2o_porc != null ? lote.h2o_porc + '%' : '—' }}</td>
              <td class="td-truncate" :title="lote.proveedor">{{ lote.proveedor }}</td>
              <td class="td-mono td-muted">{{ lote.ruc ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.ley_avg?.toFixed(4) ?? '—' }}</td>
              <td class="align-right td-mono">{{ lote.rec_porc != null ? lote.rec_porc + '%' : '—' }}</td>
              <td class="td-truncate td-muted" :title="lote.acopiador || ''">{{ lote.acopiador || '—' }}</td>
              <td class="align-center">
                <div class="celda-analisis">
                  <span class="badge-analisis" :class="badgeAnalisis(lote)">
                    {{ labelAnalisis(lote) }}
                  </span>
                  <div class="tags-secundarios">
                    <span
                      v-if="lote.volado"
                      class="tag-sec tag-volado"
                      :title="`Ley baja — ${lote.dias_almacen}d en almacén. Auto-habilita a los 30 días.`"
                    >VOLADO · {{ lote.dias_almacen }}d</span>
                    <span
                      v-if="lote.dirimencia"
                      class="tag-sec tag-dirimencia"
                      title="Este lote tiene o tuvo análisis de dirimencia"
                    >DIRIM</span>
                    <span
                      v-if="['ASIGNADO_RUMA', 'LIQUIDADO', 'FACTURADO', 'PAGADO'].includes(lote.estado) || !!lote.ruma_codigo"
                      class="tag-sec tag-en-ruma"
                      :title="lote.ruma_codigo ? 'Asignado a ' + lote.ruma_codigo : 'Lote ya asignado a ruma'"
                    >{{ labelEnRuma(lote) }}</span>
                    <span
                      v-else-if="lote.habilitado_ruma"
                      class="tag-sec tag-habilitado"
                      title="Habilitado para ingresar a ruma"
                    >RUMA ✓</span>
                    <span
                      v-if="lote.tiene_rec_pendiente"
                      class="tag-sec tag-remu"
                      title="Recuperación preliminar disponible — hay un segundo análisis pendiente"
                    >REMU <Hourglass :size="11"/></span>
                  </div>
                </div>
              </td>
              <td class="align-center">
                <span class="badge-estado" :class="badgeLote(lote.estado)">{{ lote.estado }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span class="table-count">{{ lotesFiltrados.length }} de {{ data?.lotes.length ?? 0 }} lotes</span>
      </div>
    </template>

    <template v-else-if="tabActual === 'acopiadores'">
      <div class="matrix-section-header">
        <div class="title-group">
          <Scale class="section-icon" :size="22" />
          <div>
            <h2>Análisis de Toneladas Húmedas (TMH) por Acopiador</h2>
            <p class="section-subtitle">Volumen mensualizado acumulado de la campaña actual</p>
          </div>
        </div>
        <button class="btn-export-premium" @click="exportarExcel('acopiadores')">
          <Download :size="14" />
          <span>Exportar Matriz (.xlsx)</span>
        </button>
      </div>

      <div class="matrix-table-scroll-container">
        <table class="matrix-table-premium">
          <thead>
            <tr>
              <th class="sticky-column text-left">Acopiador</th>
              <th class="align-right">Ene</th>
              <th class="align-right">Feb</th>
              <th class="align-right">Mar</th>
              <th class="align-right">Abr</th>
              <th class="align-right">May</th>
              <th class="align-right">Jun</th>
              <th class="align-right">Jul</th>
              <th class="align-right">Ago</th>
              <th class="align-right">Set</th>
              <th class="align-right">Oct</th>
              <th class="align-right">Nov</th>
              <th class="align-right">Dic</th>
              <th class="total-column-header align-right">Total General</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data?.acopiadores_tmh" :key="item.acopiador" class="matrix-row">
              <td class="sticky-column font-bold text-left acopiador-cell">
                <span class="acopiador-avatar-sm">{{ (item.acopiador || 'S').charAt(0) }}</span>
                <span class="acopiador-text">{{ item.acopiador || 'SIN ACOPIADOR' }}</span>
              </td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.enero > 0 }">{{ formatVolume(item.enero) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.febrero > 0 }">{{ formatVolume(item.febrero) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.marzo > 0 }">{{ formatVolume(item.marzo) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.abril > 0 }">{{ formatVolume(item.abril) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.mayo > 0 }">{{ formatVolume(item.mayo) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.junio > 0 }">{{ formatVolume(item.junio) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.julio > 0 }">{{ formatVolume(item.julio) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.agosto > 0 }">{{ formatVolume(item.agosto) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.septiembre > 0 }">{{ formatVolume(item.septiembre) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.octubre > 0 }">{{ formatVolume(item.octubre) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.noviembre > 0 }">{{ formatVolume(item.noviembre) }}</td>
              <td class="align-right td-mono volume-cell" :class="{ 'has-value': item.diciembre > 0 }">{{ formatVolume(item.diciembre) }}</td>
              <td class="total-column font-bold align-right td-mono highlight-gold-cell">{{ formatVolume(item.total) }}</td>
            </tr>
            <tr class="totals-row-premium">
              <td class="sticky-column text-left font-bold totals-title-cell">TOTAL GENERAL</td>
              <td v-for="mes in mesesClaves" :key="mes" class="align-right td-mono totals-month-cell">
                {{ formatVolume(calcularTotalMes(mes)) }}
              </td>
              <td class="total-column font-bold align-right td-mono highlight-gold-cell-total">{{ formatVolume(totalGeneralMatriz) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template v-else-if="tabActual === 'liquidaciones'">
      <div class="filtros-bar">
        <div class="field" style="width:160px">
          <label class="field-label">ESTADO</label>
          <select class="field-input field-select" v-model="filtroEstadoLiq">
            <option value="">Todos</option>
            <option value="GENERADA">Generada</option>
            <option value="FACTURADA">Facturada</option>
            <option value="PAGADA">Pagada</option>
          </select>
        </div>
        <div class="field" style="flex:1;min-width:200px">
          <label class="field-label">BÚSQUEDA</label>
          <div class="search-wrapper">
            <Search :size="15" class="search-icon" />
            <input
              type="text"
              class="field-input search-input"
              v-model="busquedaLiq"
              placeholder="N° liquidación, proveedor…"
            />
          </div>
        </div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn-primary ready btn-con-icono" @click="router.push('/liquidaciones/nueva')">
            <PlusCircle :size="16" />
            Nueva
          </button>
        </div>
      </div>

      <div v-if="liqStore.cargando" class="estado-tabla">
        <span class="spinner" style="margin-right:0.5rem" /> Cargando liquidaciones…
      </div>
      <div class="table-wrapper" v-else>
        <table class="data-table">
          <thead>
            <tr>
              <th>N° LIQUIDACIÓN</th>
              <th>PROVEEDOR</th>
              <th>ACOPIADOR</th>
              <th class="align-center">LOTES</th>
              <th class="align-right">SPOT USD</th>
              <th class="align-right">TOTAL USD</th>
              <th class="align-center">ESTADO</th>
              <th>FECHA</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="liquidacionesFiltradas.length === 0">
              <td colspan="9" class="empty-state">Sin liquidaciones registradas.</td>
            </tr>
            <tr
              v-for="liq in liquidacionesFiltradas"
              :key="liq.id"
              class="tabla-row clickable"
              @click="router.push(`/liquidaciones/${liq.id}`)"
            >
              <td class="td-mono" style="color:var(--color-gold)">{{ liq.numero_liquidacion }}</td>
              <td>
                <span class="nombre-bold">{{ liq.proveedor_razon_social }}</span>
                <span v-if="liq.proveedor_ruc" class="ruc-sub">{{ liq.proveedor_ruc }}</span>
              </td>
              <td class="td-muted">{{ liq.acopiador_nombre }}</td>
              <td class="align-center">
                <span class="badge-count-sm">{{ liq.count_lotes }}</span>
              </td>
              <td class="align-right td-mono">${{ fmtNum(liq.spot_usd) }}</td>
              <td class="align-right td-mono" style="color:var(--color-gold);font-weight:700">
                ${{ fmtNum(liq.total_usd) }}
              </td>
              <td class="align-center">
                <span class="badge-estado" :class="badgeLiq(liq.estado)">{{ liq.estado }}</span>
              </td>
              <td class="td-mono td-muted" style="font-size:var(--text-sm)">{{ fmtDate(liq.fecha_creacion) }}</td>
              <td @click.stop>
                <button
                  class="btn-accion"
                  title="Descargar PDF"
                  @click="descargarPDF(liq.id.toString())"
                >
                  <Download :size="14" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span class="table-count">{{ liquidacionesFiltradas.length }} de {{ liqStore.lista.length }} liquidaciones</span>
      </div>
    </template>

    <template v-else-if="tabActual === 'alertas'">
      <div v-if="alertasLoading" class="estado-carga">
        <RefreshCw class="spin" :size="20" /> Evaluando alertas…
      </div>

      <template v-else-if="alertasData">

        <!-- Resumen de severidades -->
        <div class="alertas-header">
          <div class="sev-pill pill-critica">
            <span class="pill-num">{{ alertasData.total_criticas }}</span>
            <span class="pill-lbl">Críticas</span>
          </div>
          <div class="sev-pill pill-alta">
            <span class="pill-num">{{ alertasData.total_altas }}</span>
            <span class="pill-lbl">Altas</span>
          </div>
          <div class="sev-pill pill-media">
            <span class="pill-num">{{ alertasData.total_medias }}</span>
            <span class="pill-lbl">Medias</span>
          </div>
          <div style="flex:1"/>
          <button class="btn-export" @click="cargarAlertas">
            <RefreshCw :size="13" /> Actualizar
          </button>
        </div>

        <!-- Filtros -->
        <div class="filtros-bar">
          <div class="field" style="width:160px">
            <label class="field-label">TIPO</label>
            <select v-model="filtroTipo" class="field-input field-select">
              <option value="TODOS">Todos</option>
              <option v-for="(lbl, key) in TIPO_LABELS" :key="key" :value="key">{{ lbl }}</option>
            </select>
          </div>
          <div class="field" style="width:160px">
            <label class="field-label">SEVERIDAD</label>
            <select v-model="filtroSev" class="field-input field-select">
              <option value="TODOS">Todas</option>
              <option value="CRITICA">Crítica</option>
              <option value="ALTA">Alta</option>
              <option value="MEDIA">Media</option>
            </select>
          </div>
        </div>

        <!-- Sin alertas -->
        <div v-if="!alertasFiltradas.length" class="empty-state" style="margin-top:2rem">
          <CheckCircle2 :size="36" class="icon-sin-alertas" />
          <p>Sin alertas para los filtros seleccionados</p>
        </div>

        <!-- Lista de alertas -->
        <div v-else class="alertas-list">
          <div
            v-for="a in alertasFiltradas" :key="`${a.ip}-${a.tipo}`"
            class="alerta-card"
            :class="`alerta-${a.severidad.toLowerCase()}`"
          >
            <div class="alerta-top">
              <component
                :is="TIPO_ICONOS[a.tipo] ?? ICONO_FALLBACK"
                :size="17"
                class="alerta-icono-svg"
              />
              <div class="alerta-meta">
                <span class="alerta-tipo">{{ TIPO_LABELS[a.tipo] }}</span>
                <span class="badge-sev" :class="`sev-${a.severidad.toLowerCase()}`">
                  {{ a.severidad }}
                </span>
              </div>
              <span class="alerta-ip font-mono">{{ a.ip }}</span>
            </div>
            <p class="alerta-desc">{{ a.descripcion }}</p>
            <div class="alerta-footer">
              <span class="text-muted" style="font-size:var(--text-xs)">
                {{ a.proveedor }}
                <template v-if="a.acopiador && a.acopiador !== a.proveedor">
                  · {{ a.acopiador }}
                </template>
              </span>
              <span class="alerta-horas font-mono">
                {{ a.horas_retraso >= 48
                    ? `${(a.horas_retraso/24).toFixed(1)} días`
                    : `${a.horas_retraso}h` }}
              </span>
            </div>
          </div>
        </div>

        <!-- Editor de umbrales (solo Admin/Gerencia) -->
        <details class="umbrales-panel" v-if="umbralEdit && puedeEditarUmbrales">
          <summary class="umbrales-summary">
            <Settings :size="13" />
            Configurar umbrales de alerta
          </summary>
          <div class="umbrales-grid">
            <div class="umbral-row">
              <label>Pesaje → Muestreo (horas)</label>
              <input type="number" min="1" v-model.number="umbralEdit.horas_pesado_muestreo" class="umbral-input"/>
            </div>
            <div class="umbral-row">
              <label>Muestreo → Ley (horas)</label>
              <input type="number" min="1" v-model.number="umbralEdit.horas_muestreo_ley" class="umbral-input"/>
            </div>
            <div class="umbral-row">
              <label>Ley → Recuperación (horas)</label>
              <input type="number" min="1" v-model.number="umbralEdit.horas_ley_recuperacion" class="umbral-input"/>
            </div>
            <div class="umbral-row">
              <label>Volado sin ruma (días)</label>
              <input type="number" min="1" v-model.number="umbralEdit.dias_volado_stock" class="umbral-input"/>
            </div>
          </div>
          <button class="btn-export" :disabled="guardandoCfg" @click="guardarConfig"
            style="margin-top:0.75rem; border-color: var(--color-gold); color: var(--color-gold)">
            {{ guardandoCfg ? 'Guardando…' : 'Guardar umbrales' }}
          </button>
        </details>

      </template>
    </template>

    <template v-else>
      <div class="actions-header-bar">
        <span class="actions-label">EXPORTAR REPORTES</span>
        <div class="actions-group">
          <button class="btn-export-premium" @click="exportarExcel('lotes')">
            <Download :size="14" />
            <span>Lotes (.xlsx)</span>
          </button>
          <button class="btn-export-premium" @click="exportarExcel('acopiadores')">
            <Download :size="14" />
            <span>Acopiadores (.xlsx)</span>
          </button>
          <button class="btn-export-premium btn-print" @click="imprimirVista">
            <Printer :size="14" />
            <span>Imprimir PDF</span>
          </button>
        </div>
      </div>

      <div class="charts-grid">

        <!-- Donut: Pipeline de Análisis -->
        <div class="analytics-card">
          <div class="card-header-mini">
            <h3>Pipeline de Análisis</h3>
            <span class="font-mono text-muted-badge">{{ totalLotes }} lotes totales</span>
          </div>
          <div class="donut-layout">
            <!-- SVG Donut -->
            <div class="donut-wrap">
              <svg :viewBox="`0 0 100 100`" width="150" height="150">
                <g transform="rotate(-90 50 50)">
                  <circle cx="50" cy="50" :r="DONUT_R" fill="none"
                    stroke="rgba(255,255,255,0.03)" stroke-width="12"/>
                  <circle
                    v-for="seg in donutSegments" :key="seg.label"
                    cx="50" cy="50" :r="DONUT_R" fill="none"
                    :stroke="seg.color" stroke-width="12"
                    :stroke-dasharray="`${seg.dash} ${DONUT_CIRC}`"
                    :stroke-dashoffset="`-${seg.offset}`"
                    class="donut-segment-transition"
                  />
                </g>
              </svg>
              <div class="donut-center">
                <span class="donut-val">{{ totalLotes }}</span>
                <span class="donut-lbl">lotes</span>
              </div>
            </div>
            <!-- Legend -->
            <div class="donut-legend">
              <div v-for="seg in donutSegments" :key="seg.label" class="legend-row">
                <span class="legend-dot" :style="{ background: seg.color }"></span>
                <span class="legend-label">{{ seg.label }}</span>
                <span class="legend-count font-mono">{{ seg.value }}</span>
                <span class="legend-pct font-mono">{{ seg.pct }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Barras: Estados de Lotes -->
        <div class="analytics-card">
          <div class="card-header-mini">
            <h3>Estados de Lotes</h3>
            <span class="font-mono text-muted-badge">Distribución operativa</span>
          </div>
          <div class="bars-list">
            <div v-for="(item, estado) in distribucionEstados" :key="estado" class="bar-row">
              <div class="bar-label">
                <span class="badge-estado" :class="badgeLote(estado.toString())">{{ estado }}</span>
              </div>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :class="badgeLote(estado.toString())"
                  :style="{ width: `${item.porcentaje}%` }"
                ></div>
              </div>
              <div class="bar-stats font-mono">
                <span class="bar-count-val">{{ item.count }}</span>
                <span class="bar-pct-val">{{ item.porcentaje }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabla: Resumen por Acopiador -->
        <div class="analytics-card analytics-card--wide" v-if="data?.acopiadores_stats?.length">
          <div class="card-header-mini">
            <h3>Desempeño por Acopiador</h3>
            <span class="font-mono text-muted-badge">Acumulado Campaña</span>
          </div>
          <div class="table-premium-wrapper">
            <table class="data-table-premium">
              <thead>
                <tr>
                  <th>ACOPIADOR</th>
                  <th class="align-center">LOTES</th>
                  <th>TONELADAS SECAS (TMS)</th>
                  <th class="align-right">OZ EN STOCK</th>
                  <th class="align-right">LEY PROMEDIO</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in data.acopiadores_stats" :key="s.acopiador" class="tabla-row-premium">
                  <td class="td-acopiador">
                    <span class="acopiador-avatar">{{ s.acopiador.charAt(0) }}</span>
                    <span class="acopiador-name">{{ s.acopiador }}</span>
                  </td>
                  <td class="align-center">
                    <span class="badge-lotes-count font-mono">{{ s.lotes }}</span>
                  </td>
                  <td>
                    <div class="premium-bar-wrap">
                      <div class="premium-bar-track">
                        <div class="premium-bar-fill" :style="{ width: `${(s.tms / maxAcopiadorTms) * 100}%` }"></div>
                      </div>
                      <span class="premium-bar-val font-mono">{{ s.tms.toFixed(2) }} <span class="unit-label">TM</span></span>
                    </div>
                  </td>
                  <td class="align-right td-mono highlight-gold">{{ s.oz.toFixed(3) }} <span class="unit-label-dim">oz</span></td>
                  <td class="align-right td-mono font-bold">{{ s.ley_prom?.toFixed(3) ?? '—' }} <span class="unit-label-dim">g/T</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
    <span class="last-sync"> *Cifras reiniciadas desde el último cierre de campaña</span>

    <!-- Drawer de trazabilidad -->
    <TrazabilidadLoteDrawer
      :ip="ipTrazabilidad"
      :open="drawerOpen"
      @close="drawerOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, markRaw, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Zap, TrendingUp, Scale, Database, Coins, Search,
  RefreshCw, Layers, FileText, PlusCircle, Download, LayoutDashboard,
  Hourglass, Printer, Package, Droplets, FlaskConical, Timer,
  Settings, AlertTriangle, HelpCircle, CheckCircle2,
} from 'lucide-vue-next'
import { dashboardApi, type DashboardResponse,
  type LoteDashboard,
 } from '@/api/dashboard'
import { useLiquidacionesStore } from '@/stores/liquidaciones'
import { useUiStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { descargarPDF } from '@/api/liquidaciones'
import type { AlertaItem, AlertasConfig, AlertasResponse} from '@/api/dashboard'
import TrazabilidadLoteDrawer from '@/components/dashboard/TrazabilidadLoteDrawer.vue'

const router   = useRouter()
const liqStore = useLiquidacionesStore()
const ui       = useUiStore()
const auth     = useAuthStore()

// ── Trazabilidad drawer ───────────────────────────────────────────────
const drawerOpen       = ref(false)
const ipTrazabilidad   = ref<string | null>(null)
const canViewTrazabilidad   = computed(() => auth.puede('RUMAS',      'VIEW'))
const puedeEditarUmbrales   = computed(() => auth.puede('DASHBOARD',   'UPDATE'))
function abrirTrazabilidad(ip: string) {
  ipTrazabilidad.value = ip
  drawerOpen.value = true
}

// ── Data ─────────────────────────────────────────────────────────────
const data       = ref<DashboardResponse | null>(null)
const cargando   = ref(true)
const lastUpdate = ref<string | null>(null)

// ── Tabs ──────────────────────────────────────────────────────────────
type TabKey = 'resumen' | 'lotes' | 'liquidaciones' | 'acopiadores' | 'alertas'
const tabActual = ref<TabKey>('resumen')

const tabs = computed(() => [
  { key: 'resumen'        as TabKey, label: 'Resumen',       icon: markRaw(LayoutDashboard), count: null },
  { key: 'lotes'          as TabKey, label: 'Lotes',         icon: markRaw(Layers),           count: lotesFiltrados.value.length || null },
  { key: 'liquidaciones'  as TabKey, label: 'Liquidaciones', icon: markRaw(FileText),          count: liqStore.lista.length || null },
  { key: 'acopiadores'    as TabKey, label: 'Acopiadores',   icon: markRaw(Scale),            count: data.value?.acopiadores_tmh?.length || null },
  { key: 'alertas'        as TabKey, label: 'Alertas',       icon: markRaw(FileText),         count: totalAlertas.value || null },
])

// Mapeo ordenado de meses de claves de la estructura de datos
const mesesClaves = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
] as const;

// Estado
const alertasData = ref<AlertasResponse | null>(null)
const alertasLoading = ref(false)
const filtroTipo = ref<string>('TODOS')
const filtroSev = ref<string>('TODOS')
const umbralEdit = ref<AlertasConfig | null>(null)
const guardandoCfg = ref(false)

const formatVolume = (val: number) => {
  if (!val || val === 0) return '-';
  return val.toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

// Funciones computadas para calcular la fila inferior de totales dinámicos basados en "data"
const calcularTotalMes = (mes: typeof mesesClaves[number]): number => {
  if (!data.value?.acopiadores_tmh) return 0;
  return data.value.acopiadores_tmh.reduce((acc, current) => acc + (current[mes] || 0), 0);
};

const totalGeneralMatriz = computed(() => {
  if (!data.value?.acopiadores_tmh) return 0;
  return data.value.acopiadores_tmh.reduce((acc, current) => acc + (current.total || 0), 0);
});

function labelEnRuma(lote: LoteDashboard) {
  if (lote.ruma_codigo) {
    const parts = lote.ruma_codigo.split('-')
    const numStr = parts[parts.length - 1]
    const num = Number(numStr)
    if (!isNaN(num)) return `EN RUMA ${num}`
    return `EN RUMA`
  }
  return 'EN RUMA'
}

// ── Filtros ───────────────────────────────────────────────────────────
const busquedaLote     = ref('')
const filtroEstadoLote = ref('')
const busquedaLiq      = ref('')
const filtroEstadoLiq  = ref('')
const filtroAnalisis   = ref('')
const filtroKpi        = ref<string | null>(null)

function aplicarFiltroKpi(kpi: string) {
  if (filtroKpi.value === kpi) {
    filtroKpi.value = null // Toggle off
  } else {
    filtroKpi.value = kpi
    filtroEstadoLote.value = ''
    filtroAnalisis.value = ''
    busquedaLote.value = ''
    if (tabActual.value !== 'lotes') {
      tabActual.value = 'lotes'
    }
  }
}

// ── Computed ──────────────────────────────────────────────────────────
const lotesFiltrados = computed(() => {
  if (!data.value) return []
  return data.value.lotes.filter(l => {
    if (filtroEstadoLote.value) {
      if (filtroEstadoLote.value === 'ASIGNADO_RUMA') {
        const enRuma = ['ASIGNADO_RUMA', 'LIQUIDADO', 'FACTURADO', 'PAGADO'].includes(l.estado) || !!l.ruma_codigo
        if (!enRuma) return false
      } else {
        if (l.estado !== filtroEstadoLote.value) return false
      }
    }
    
    if (filtroAnalisis.value && l.estado_analisis !== filtroAnalisis.value) return false
    
    if (filtroKpi.value) {
      if (filtroKpi.value === 'tms_stock') {
        if (l.tms == null) return false
      } else if (filtroKpi.value === 'au_real_100' || filtroKpi.value === 'oz_stock') {
        if (l.tms == null || l.ley_avg == null) return false
      } else if (filtroKpi.value === 'au_real_rec') {
        if (l.tms == null || l.ley_avg == null || l.rec_porc == null) return false
      } else if (filtroKpi.value === 'oz_habilitados') {
        const enRuma = ['ASIGNADO_RUMA', 'LIQUIDADO', 'FACTURADO', 'PAGADO'].includes(l.estado) || !!l.ruma_codigo
        if (enRuma || !l.habilitado_ruma) return false
      }
    }

    const q = busquedaLote.value.toLowerCase()
    if (!q) return true
    return l.ip.toLowerCase().includes(q) || l.proveedor.toLowerCase().includes(q)
  })
})

const liquidacionesFiltradas = computed(() => {
  const q = busquedaLiq.value.trim().toLowerCase()
  return liqStore.lista.filter(l => {
    if (filtroEstadoLiq.value && l.estado !== filtroEstadoLiq.value) return false
    if (!q) return true
    return (
      l.numero_liquidacion.toLowerCase().includes(q) ||
      l.proveedor_razon_social.toLowerCase().includes(q) ||
      (l.proveedor_ruc?.includes(q) ?? false)
    )
  })
})

// ── Total global de lotes en memoria ──────────────────────────────────
const totalLotes = computed(() => data.value?.lotes.length || 0)

// ── Agrupación computada para Gráfico de Estados Operativos ──────────
const distribucionEstados = computed(() => {
  if (!data.value || totalLotes.value === 0) return {}

  const grupos: Record<string, number> = {}
  data.value.lotes.forEach(lote => {
    grupos[lote.estado] = (grupos[lote.estado] || 0) + 1
  })

  const resultado: Record<string, { count: number; porcentaje: string }> = {}
  Object.keys(grupos).forEach(key => {
    const count = grupos[key] ?? 0
    resultado[key] = {
      count,
      porcentaje: ((count / (totalLotes.value ?? 1)) * 100).toFixed(1)
    }
  })
  return resultado
})

// ── Agrupación computada para Gráfico de Pipeline de Análisis ────────
const distribucionAnalisis = computed(() => {
  if (!data.value || totalLotes.value === 0) return {}

  const grupos: Record<string, number> = {}
  data.value.lotes.forEach(lote => {
    grupos[lote.estado_analisis] = (grupos[lote.estado_analisis] || 0) + 1
  })

  const resultado: Record<string, { count: number; porcentaje: string }> = {}
  Object.keys(grupos).forEach(key => {
    const count = grupos[key] ?? 0
    resultado[key] = {
      count,
      porcentaje: ((count / (totalLotes.value ?? 1)) * 100).toFixed(1)
    }
  })
  return resultado
})

// ── Actions ───────────────────────────────────────────────────────────
async function cargarDashboard() {
  cargando.value = true
  try {
    data.value   = await dashboardApi.getResumen()
    lastUpdate.value = new Date().toLocaleTimeString('es-PE')
  } catch (e) {
    console.error('Error cargando dashboard', e)
  } finally {
    cargando.value = false
  }
}

async function recargar() {
  await Promise.all([cargarDashboard(), liqStore.cargarLista()])
}

// ── Formatters ────────────────────────────────────────────────────────
function fmtNum(v: number, d = 2) {
  return Number(v).toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d })
}
function fmtDate(s: string) {
  if (!s) return '-'
  return new Date(s).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// ── Export helpers ────────────────────────────────────────────────────
function fechaHoy() {
  return new Date().toISOString().slice(0, 10)
}

function descargarCSV(rows: Record<string, unknown>[], nombre: string) {
  if (!rows.length) return
  const headers = Object.keys(rows[0] ?? {})
  const sep = ';' // Excel es-PE usa punto y coma
  const csv = [
    headers.join(sep),
    ...rows.map(r =>
      headers.map(h => {
        const v = r[h] ?? ''
        return typeof v === 'string' && v.includes(sep) ? `"${v}"` : String(v)
      }).join(sep)
    ),
  ].join('\r\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = `${nombre}.csv`; a.click()
  URL.revokeObjectURL(url)
}

function exportarLotesCSV() {
  const rows = lotesFiltrados.value.map(l => ({
    'Lote (IP)': l.ip,
    'TMH': l.tmh,
    'TMS': l.tms ?? '',
    '%H2O': l.h2o_porc ?? '',
    'Proveedor': l.proveedor,
    'RUC': l.ruc ?? '',
    'Ley Prom oz/TC': l.ley_avg ?? '',
    '% Rec': l.rec_porc ?? '',
    'Acopiador': l.acopiador ?? '',
    'Estado': l.estado,
    'Analisis': labelAnalisis(l.estado_analisis),
    'Dias Almacen': l.dias_almacen,
    'Habilitado Ruma': l.habilitado_ruma ? 'Si' : 'No',
    'Volado': l.volado ? 'Si' : 'No',
    'Dirimencia': l.dirimencia ? 'Si' : 'No',
  }))
  descargarCSV(rows, `lotes_paititi_${fechaHoy()}`)
}

function exportarAcopiadoresCSV() {
  const rows = (data.value?.acopiadores_tmh ?? []).map(a => ({
    'Acopiador': a.acopiador,
    'Ene': a.enero, 'Feb': a.febrero, 'Mar': a.marzo, 'Abr': a.abril,
    'May': a.mayo, 'Jun': a.junio, 'Jul': a.julio, 'Ago': a.agosto,
    'Set': a.septiembre, 'Oct': a.octubre, 'Nov': a.noviembre, 'Dic': a.diciembre,
    'Total TMH': a.total,
  }))
  descargarCSV(rows, `acopiadores_tmh_${fechaHoy()}`)
}

function exportarResumenCSV() {
  const k = data.value?.kpis
  if (!k) return
  const kpiRows = [
    { Indicador: 'Au Real 100%', Valor: k.au_real_100, Unidad: 'gr' },
    { Indicador: 'Au Real con Recuperacion', Valor: k.au_real_rec, Unidad: 'gr' },
    { Indicador: 'TMH en Stock', Valor: k.tmh_stock, Unidad: 'TM' },
    { Indicador: 'TMS en Stock', Valor: k.tms_stock, Unidad: 'TM' },
    { Indicador: 'Oz en Stock', Valor: k.oz_stock, Unidad: 'oz' },
    { Indicador: 'Oz Disponibles para Ruma', Valor: k.oz_habilitados, Unidad: 'oz' },
  ]
  descargarCSV(kpiRows, `resumen_gerencia_${fechaHoy()}`)
}

function imprimirVista() {
  window.print()
}

// ── Donut Chart (análisis pipeline) ─────────────────────────────────
const DONUT_R    = 40
const DONUT_CIRC = +(2 * Math.PI * DONUT_R).toFixed(4)  // 251.3274

interface DonutSeg { label: string; value: number; color: string; pct: number; dash: number; offset: number }

const donutSegments = computed((): DonutSeg[] => {
  const c = data.value?.analisis_conteo
  if (!c) return []
  const items = [
    { label: 'Listo',         value: c.listo,          color: '#22c55e' },
    { label: 'Falta Rec.',    value: c.falta_rec,       color: '#f59e0b' },
    { label: 'Falta Ley',     value: c.falta_ley,       color: '#60a5fa' },
    { label: 'Falta Muestreo',value: c.falta_muestreo,  color: '#c084fc' },
    { label: 'Sin datos',     value: c.sin_datos,       color: '#475569' },
  ].filter(i => i.value > 0)
  const total = items.reduce((s, i) => s + i.value, 0)
  if (!total) return []
  let acc = 0
  return items.map(i => {
    const dash = (i.value / total) * DONUT_CIRC
    const seg: DonutSeg = { ...i, pct: +(i.value / total * 100).toFixed(1), dash, offset: acc }
    acc += dash
    return seg
  })
})

// Max TMS para normalizar mini-bars de acopiadores
const maxAcopiadorTms = computed(() =>
  Math.max(...(data.value?.acopiadores_stats.map(a => a.tms) ?? [1]), 1)
)

function urgenciaFila(l: LoteDashboard): string {
  if (l.estado_analisis === 'LISTO') return 'row-listo'
  if (l.dias_almacen >= 30 && l.estado_analisis !== 'LISTO') return 'row-urgente'
  if (l.estado_analisis === 'SIN_DATOS') return 'row-sin-datos'
  return ''
}

// ── Export ───────────────────────────────────────────────────────────
async function exportarExcel(tipo: 'lotes' | 'acopiadores') {
  const clave = await ui.showPrompt({
    title: 'Proteger Excel',
    message: 'Ingresa tu contraseña para cifrar el archivo:',
    inputType: 'password',
    placeholder: '••••••••',
    confirmLabel: 'Descargar',
  })
  if (!clave) return
  try {
    await dashboardApi.exportar(tipo, clave)
    ui.toast('Excel generado y protegido', 'success')
  } catch {
    ui.toast('Error al generar el Excel', 'error')
  }
}

// Alertas

async function cargarAlertas() {
  alertasLoading.value = true
  try {
    alertasData.value = await dashboardApi.getAlertas()
    umbralEdit.value = { ...alertasData.value.config }
  } finally {
    alertasLoading.value = false
  }
}

async function guardarConfig() {
  if (!umbralEdit.value) return
  guardandoCfg.value = true
  try {
    await dashboardApi.updateAlertasConfig(umbralEdit.value)
    ui.toast('Umbrales actualizados', 'success')
    await cargarAlertas()
  } catch {
    ui.toast('Error al guardar umbrales', 'error')
  } finally {
    guardandoCfg.value = false
  }
}

const alertasFiltradas = computed(() => {
  if (!alertasData.value) return []
  return alertasData.value.alertas.filter(a =>
    (filtroTipo.value === 'TODOS' || a.tipo === filtroTipo.value) &&
    (filtroSev.value  === 'TODOS' || a.severidad === filtroSev.value)
  )
})

const totalAlertas = computed(() =>
  (alertasData.value?.total_criticas ?? 0) +
  (alertasData.value?.total_altas    ?? 0) +
  (alertasData.value?.total_medias   ?? 0)
)

const TIPO_LABELS: Record<string, string> = {
  VOLADO_STOCK:         'Volado en stock',
  RETRASO_MUESTREO:     'Sin muestreo',
  RETRASO_LEY:          'Sin ley',
  RETRASO_RECUPERACION: 'Sin recuperación',
}

const TIPO_ICONOS: Record<string, object> = {
  VOLADO_STOCK: markRaw(Package),
  RETRASO_MUESTREO: markRaw(Droplets),
  RETRASO_LEY: markRaw(FlaskConical),
  RETRASO_RECUPERACION: markRaw(Timer),
}
const ICONO_FALLBACK = markRaw(AlertTriangle)

// Cargar alertas cuando se activa el tab
watch(tabActual, (tab) => {
  if (tab === 'alertas' && !alertasData.value) cargarAlertas()
})

function badgeLote(estado: string) {
  const m: Record<string, string> = {
    RECEPCIONADO: 'en-proceso', ASIGNADO_RUMA: 'parcial',
    LIQUIDADO: 'completado', FACTURADO: 'pendiente', PAGADO: 'pagado',
  }
  return m[estado] ?? 'en-proceso'
}

function badgeLiq(estado: string) {
  return {
    BORRADOR:  'badge-borrador',
    GENERADA:  'badge-generada',
    FACTURADA: 'badge-facturada',
    PAGADA:    'badge-pagada',
  }[estado] ?? 'badge-generada'
}
function badgeAnalisis(lote: LoteDashboard): string {
  if (lote.estado_analisis === 'LISTO' && ['LIQUIDADO', 'FACTURADO', 'PAGADO'].includes(lote.estado)) {
    return 'analisis-completo'
  }
  return {
      SIN_DATOS:       'analisis-sin-datos',
      FALTA_MUESTREO:  'analisis-falta-muestreo',
      FALTA_LEY:       'analisis-falta-ley',
      FALTA_REC:       'analisis-falta-rec',
      LISTO:           'analisis-listo',
  }[lote.estado_analisis] ?? 'analisis-sin-datos'
}
function labelAnalisis(lote: LoteDashboard): string {
  if (lote.estado_analisis === 'LISTO' && ['LIQUIDADO', 'FACTURADO', 'PAGADO'].includes(lote.estado)) {
    return 'COMPLETO'
  }
  return {
    SIN_DATOS: 'Sin datos',
    FALTA_MUESTREO: 'Falta humedad',
    FALTA_LEY: 'Falta ley',
    FALTA_REC: 'Falta recuperación',
    LISTO:     'Listo para liquidar',
  }[lote.estado_analisis] ?? lote.estado_analisis
}

onMounted(() => {
  cargarDashboard()
  liqStore.cargarLista()
  cargarAlertas()
})
</script>

<style scoped>
.dashboard-page {
  padding: var(--page-padding);
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.page-header { display: flex; justify-content: space-between; align-items: flex-end; }
.last-sync { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-muted); }
.btn-refresh { display: flex; align-items: center; }

/* KPIs */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.kpi-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover { 
  transform: translateY(-3px); 
  border-color: var(--color-border-focus);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3); 
}
.kpi-card.active {
  border-color: var(--color-gold) !important;
  box-shadow: 0 0 0 1px var(--color-gold), 0 4px 15px rgba(179, 144, 40, 0.2);
  background: linear-gradient(135deg, var(--color-bg-card) 0%, rgba(179, 144, 40, 0.05) 100%);
}
.kpi-card-interactive {
  cursor: pointer;
}
.gold-accent { border-left: 3px solid var(--color-gold); }
.kpi-info { display: flex; flex-direction: column; gap: 0.25rem; }
.kpi-label {
  font-family: var(--font-main); font-size: var(--text-xs); font-weight: 700;
  color: var(--color-text-muted); letter-spacing: 0.08em; text-transform: uppercase;
}
.kpi-value { font-family: var(--font-mono); font-size: var(--text-xl); font-weight: 700; color: var(--color-text); }
.kpi-value.highlight { color: var(--color-gold); }
.kpi-icon { color: var(--color-text-muted); opacity: 0.3; transition: opacity 0.2s, color 0.2s; }
.kpi-card:hover .kpi-icon { opacity: 0.7; color: var(--color-gold); }

/* Tabs */
.tabs-bar {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  gap: 0;
}
.tab-btn {
  display: flex; align-items: center;
  background: transparent; border: none;
  color: var(--color-text-muted);
  padding: 0.6rem 1.25rem;
  font-size: var(--text-md); font-family: var(--font-mono);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  letter-spacing: 0.06em;
}
.tab-btn.active { color: var(--color-gold); border-bottom-color: var(--color-gold); }
.tab-btn:hover:not(.active) { color: var(--color-text); }
.tab-count {
  margin-left: 0.4rem;
  background: rgba(179,144,40,0.12); border: 1px solid rgba(179,144,40,0.25);
  color: var(--color-gold); font-size: var(--text-xs);
  padding: 0.05rem 0.45rem; border-radius: 99px; font-family: var(--font-mono);
}

/* Filtros */
.filtros-bar { display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-end; }
.search-wrapper { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--color-text-muted); pointer-events: none; }
.search-input { padding-left: 32px; }
.btn-con-icono { display: flex; align-items: center; gap: 0.4rem; padding: 0.6rem 1rem; min-height: 40px; }

/* Tabla */
.table-wrapper { overflow-x: auto; border: 1px solid var(--color-border); border-radius: var(--radius-sm); background: var(--color-bg-card); }
.data-table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
.data-table thead tr { background: rgba(179,144,40,0.06); border-bottom: 1px solid var(--color-border); }
.data-table th {
  padding: 0.65rem 1rem; text-align: left;
  font-family: var(--font-mono); font-size: var(--text-xs);
  letter-spacing: 0.12em; color: var(--color-text-muted); text-transform: uppercase; white-space: nowrap;
}
.data-table td { padding: 0.7rem 1rem; border-bottom: 1px solid rgba(58,58,40,0.3); color: var(--color-text); }
.tabla-row { transition: background 0.1s; }
.tabla-row:hover { background: rgba(179,144,40,0.03); }
.tabla-row.clickable { cursor: pointer; }

.td-mono   { font-family: var(--font-mono); }
.td-muted  { color: var(--color-text-muted); }
.td-truncate { max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gold { color: var(--color-gold); font-weight: bold; }
.align-right  { text-align: right !important; }
.align-center { text-align: center !important; }

.nombre-bold { display: block; font-weight: 600; }
.ruc-sub     { display: block; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-dim); }

/* Matriz de Totales (Excel Style) */
.matrix-table th { padding: 10px 8px; font-size: 11px; }
.matrix-table td { padding: 10px 8px; }
.total-cell { background-color: rgba(148, 163, 184, 0.12) !important; font-weight: bold; }
.totals-row { background-color: rgba(179,144,40,0.08); font-weight: 700; border-top: 2px solid var(--color-gold); }

/* Grid de Gráficos del Resumen */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.analytics-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  transition: border-color 0.2s ease;
}

.analytics-card:hover {
  border-color: rgba(179, 144, 40, 0.3);
}

.card-header-mini {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(179,144,40,0.12);
  padding-bottom: 0.75rem;
}

.card-header-mini h3 {
  font-size: var(--text-md);
  font-weight: 700;
  color: var(--color-text);
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.chart-container-bars {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.chart-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.row-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 180px;
  min-width: 180px;
}

.row-count {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.progress-bar-bg {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 999px;
  width: 0;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.row-pct {
  width: 50px;
  text-align: right;
  font-size: var(--text-xs);
  font-weight: bold;
  color: var(--color-gold);
}

/* Soporte de compatibilidad de colores para los fondos de las barras */
.progress-bar-fill.parcial      { background: var(--color-gold) !important; }
.progress-bar-fill.completado   { background: #4ade80 !important; }
.progress-bar-fill.pagado       { background: #22c55e !important; }
.progress-bar-fill.pendiente    { background: var(--color-error) !important; }

.progress-bar-fill.analisis-sin-datos     { background: var(--color-text-muted) !important; }
.progress-bar-fill.analisis-falta-ley     { background: #3b82f6 !important; }
.progress-bar-fill.analisis-falta-rec     { background: #f59e0b !important; }
.progress-bar-fill.analisis-listo         { background: #22c55e !important; }
.progress-bar-fill.analisis-falta-muestreo { background: #a855f7 !important; }

.transition-all {
  transition: all 0.4s ease-in-out;
}

/* Badges estado */
.badge-estado {
  padding: 0.2rem 0.55rem; border-radius: 2px;
  font-size: var(--text-xs); font-weight: 700; font-family: var(--font-mono);
  letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap;
}
.en-proceso  { background: rgba(14, 165, 233, 0.15);  color: #38bdf8;  border: 1px solid rgba(14, 165, 233, 0.25); }
.parcial     { background: var(--color-gold-bg);      color: var(--color-gold);     border: 1px solid rgba(179,144,40,0.25); }
.completado  { background: var(--color-success-bg);   color: #4ade80;               border: 1px solid rgba(81,161,85,0.25); }
.pagado      { background: var(--color-success-bg);   color: #4ade80;               border: 1px solid rgba(81,161,85,0.25); }
.pendiente   { background: var(--color-error-bg);     color: var(--color-error);    border: 1px solid rgba(165,71,61,0.25); }

.badge-count-sm {
  display: inline-block; padding: 0.1rem 0.5rem;
  background: rgba(179,144,40,0.1); border: 1px solid rgba(179,144,40,0.25);
  border-radius: 2px; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-gold);
}

/* Badge análisis */
.celda-analisis { display: flex; flex-direction: column; align-items: center; gap: 0.3rem; }
.badge-analisis {
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 3px;
  font-size: 0.68rem; font-family: var(--font-mono); font-weight: 700;
  letter-spacing: 0.06em; white-space: nowrap;
}
.analisis-sin-datos { background: rgba(148,163,184,0.1);  color: var(--color-text-muted); }
.analisis-falta-ley    { background: rgba(59,130,246,0.15);  color: #60a5fa; border: 1px solid rgba(59,130,246,0.25); }
.analisis-falta-rec { background: rgba(245,158,11,0.15);  color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
.analisis-listo     { background: rgba(34,197,94,0.15);   color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
.analisis-completo  { background: rgba(34,197,94,0.05);   color: #15803d; border: 1px solid rgba(34,197,94,0.15); }
.analisis-falta-muestreo { background: rgba(168,85,247,0.12); color: #c084fc; border: 1px solid rgba(168,85,247,0.25); }

/* Tags secundarios */
.tags-secundarios { display: flex; gap: 0.25rem; flex-wrap: wrap; justify-content: center; }
.tag-sec {
  display: inline-block; padding: 0.1rem 0.4rem; border-radius: 2px;
  font-size: 0.62rem; font-family: var(--font-mono); font-weight: 600;
  letter-spacing: 0.04em; cursor: default; white-space: nowrap;
}
.tag-volado     { background: var(--color-volado-bg);  color: var(--color-volado); border: 1px solid rgba(68, 122, 239, 0.2); }
.tag-dirimencia { background: var(--color-dirimencia-bg);  color: var(--color-dirimencia); border: 1px solid rgba(168, 85, 247, 0.2); }
.tag-habilitado { background: rgba(34,197,94,0.1);    color: #4ade80; border: 1px solid rgba(34,197,94,0.15); }
.tag-en-ruma    { background: rgba(148,163,184,0.1); color: var(--color-text-muted); border: 1px solid rgba(148,163,184,0.2); }
.tag-remu { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }

.btn-accion {
  background: transparent; border: 1px solid var(--color-border);
  color: var(--color-text-muted); width: 28px; height: 28px;
  border-radius: var(--radius-sm); cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center; transition: all 0.15s;
}
.btn-accion:hover { border-color: var(--color-gold); color: var(--color-gold); }

/* Footer tabla */
.table-footer { display: flex; justify-content: flex-end; padding: 0.5rem 1rem; border-top: 1px solid var(--color-border); }
.table-count  { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--color-text-faint); }

/* Empty / loading */
.estado-tabla { text-align: center; padding: 3rem; font-family: var(--font-mono); font-size: var(--text-md); color: var(--color-text-muted); display: flex; align-items: center; justify-content: center; }
.empty-state  { text-align: center; padding: 2.5rem; color: var(--color-text-faint); font-family: var(--font-mono); font-size: var(--text-md); font-style: italic; }
.icon-sin-alertas { color: #4ade80; margin-bottom: 0.75rem; }

/* ── Tooltip leyenda de análisis ──────────────────────────── */
.th-analisis { position: relative; }
.th-help-wrap {
  display: inline-flex; align-items: center; position: relative; margin-left: 4px; cursor: default;
}
.th-help-icon { color: var(--color-text-muted); vertical-align: middle; }
.th-tooltip {
  display: none;
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.6rem 0.75rem;
  min-width: 240px;
  z-index: 50;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
.th-help-wrap:hover .th-tooltip { display: flex; flex-direction: column; gap: 0.35rem; }
.tooltip-row {
  display: flex; align-items: center; gap: 0.6rem;
  font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-muted);
  white-space: nowrap;
}
.t-badge {
  display: inline-block; padding: 0.1rem 0.5rem; border-radius: 2px;
  font-size: 0.62rem; font-weight: 700; letter-spacing: 0.06em; white-space: nowrap;
}
.t-listo   { background: rgba(34,197,94,0.15);   color: #4ade80;  border: 1px solid rgba(34,197,94,0.25); }
.t-humedad { background: rgba(168,85,247,0.12);  color: #c084fc;  border: 1px solid rgba(168,85,247,0.25); }
.t-ley     { background: rgba(59,130,246,0.15);  color: #60a5fa;  border: 1px solid rgba(59,130,246,0.25); }
.t-rec     { background: rgba(245,158,11,0.15);  color: #f59e0b;  border: 1px solid rgba(245,158,11,0.25); }
.t-sin     { background: rgba(148,163,184,0.1);  color: var(--color-text-muted); }


.spinner { animation: spin 0.8s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Export bar */
.export-bar { display: flex; gap: 0.5rem; justify-content: flex-end; }
.btn-export {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.35rem 0.8rem; border-radius: var(--radius-sm);
  border: 1px solid var(--color-border); background: transparent;
  color: var(--color-text-muted); font-size: var(--text-xs);
  font-family: var(--font-mono); cursor: pointer; transition: all 0.15s;
}
.btn-export:hover { border-color: var(--color-gold); color: var(--color-gold); }

/* Wide card (acopiadores) */
.analytics-card--wide { grid-column: 1 / -1; }

/* Donut */
.donut-layout { display: flex; align-items: center; gap: 2rem; padding-top: 0.5rem; flex-wrap: wrap; }
.donut-wrap   { position: relative; width: 150px; height: 150px; flex-shrink: 0; }
.donut-center {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  text-align: center; pointer-events: none;
}
.donut-val { display: block; font-size: 1.8rem; font-weight: 700; font-family: var(--font-mono); color: var(--color-gold); }
.donut-lbl { display: block; font-size: var(--text-xs); color: var(--color-text-muted); margin-top: -4px; text-transform: uppercase; letter-spacing: 0.05em; }

.donut-legend { display: flex; flex-direction: column; gap: 0.6rem; flex: 1; min-width: 180px; }
.legend-row { 
  display: flex; align-items: center; gap: 0.6rem; 
  padding: 0.25rem 0.5rem; border-radius: 4px;
  background: rgba(255,255,255,0.01);
  border: 1px solid rgba(255,255,255,0.02);
  transition: transform 0.15s, background-color 0.15s;
}
.legend-row:hover {
  transform: translateX(3px);
  background: rgba(255, 255, 255, 0.03);
}
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-label { flex: 1; font-size: var(--text-sm); color: var(--color-text-muted); }
.legend-count { font-size: var(--text-sm); color: var(--color-text); min-width: 28px; text-align: right; font-weight: 700; }
.legend-pct { font-size: var(--text-xs); color: var(--color-gold-light); min-width: 40px; text-align: right; }

.donut-segment-transition {
  transition: stroke-dashoffset 0.6s ease-in-out, stroke 0.3s;
}

/* Barras estados (reemplaza progress-bar-*) */
.bars-list { display: flex; flex-direction: column; gap: 1rem; padding-top: 0.5rem; }
.bar-row { display: flex; align-items: center; gap: 0.75rem; }
.bar-label { width: 120px; min-width: 120px; }
.bar-track {
  flex: 1; height: 12px; background: rgba(255,255,255,0.03);
  border: 1px solid var(--color-border); border-radius: 6px; overflow: hidden;
}
.bar-fill {
  height: 100%; border-radius: 6px; width: 0;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-fill.parcial     { background: linear-gradient(90deg, var(--color-gold), var(--color-gold-light)); }
.bar-fill.completado  { background: linear-gradient(90deg, #51a155, #4ade80); }
.bar-fill.pagado      { background: linear-gradient(90deg, #22c55e, #10b981); }
.bar-fill.pendiente   { background: linear-gradient(90deg, var(--color-error), #ef4444); }

.bar-stats {
  display: flex;
  justify-content: space-between;
  width: 70px;
  min-width: 70px;
  font-size: var(--text-sm);
}
.bar-count-val {
  color: var(--color-text);
  font-weight: 700;
}
.bar-pct-val {
  color: var(--color-gold);
  font-weight: 600;
  text-align: right;
  flex: 1;
}

/* Urgencia filas lotes */
.row-listo    { background: rgba(34, 197, 94,  0.02) !important; }
.row-urgente  { background: rgba(245, 158, 11, 0.04) !important; border-left: 2px solid var(--color-warning); }
.row-sin-datos{ background: rgba(148, 163, 184, 0.02) !important; }
.row-urgente td:first-child { padding-left: calc(1rem - 2px); }

/* Print */
@media print {
  .tabs-bar, .filtros-bar, .export-bar, .btn-refresh, .actions-header-bar, .matrix-section-header button { display: none !important; }
  .dashboard-page { padding: 0; }
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  .analytics-card, .table-wrapper, .matrix-table-scroll-container { break-inside: avoid; }
}

/* Tab badge */
.tab-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 18px; height: 18px; border-radius: 9px;
  font-size: 10px; font-weight: 700; padding: 0 4px; margin-left: 5px;
}
.badge-critica { background: #ef4444; color: #fff; }
.badge-alta    { background: #f59e0b; color: #000; }

/* Severity pills */
.alertas-header { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.sev-pill {
  display: flex; flex-direction: column; align-items: center;
  padding: 0.5rem 1.25rem; border-radius: var(--radius-sm);
  border: 1px solid; min-width: 80px;
}
.sev-pill .pill-num { font-size: 1.5rem; font-weight: 700; font-family: var(--font-mono); line-height: 1; }
.sev-pill .pill-lbl { font-size: var(--text-xs); margin-top: 2px; }
.pill-critica { border-color: #ef4444; color: #ef4444; }
.pill-alta    { border-color: #f59e0b; color: #f59e0b; }
.pill-media   { border-color: #facc15; color: #facc15; }

/* Alert cards */
.alertas-list { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.75rem; }
.alerta-card {
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  padding: 0.75rem 1rem; border-left-width: 3px;
  background: rgba(255,255,255,0.02);
}
.alerta-critica { border-left-color: #ef4444; }
.alerta-alta    { border-left-color: #f59e0b; }
.alerta-media   { border-left-color: #facc15; }

.alerta-top { display: flex; align-items: center; gap: 0.6rem; }
.alerta-icono { font-size: 1.1rem; }
.alerta-meta  { display: flex; align-items: center; gap: 0.5rem; flex: 1; }
.alerta-tipo  { font-size: var(--text-sm); font-weight: 600; color: var(--color-text); }
.alerta-ip    { font-size: var(--text-sm); color: var(--color-gold); }

.badge-sev { font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 3px; }
.sev-critica { background: rgba(239,68,68,.15);  color: #ef4444; }
.sev-alta    { background: rgba(245,158,11,.15); color: #f59e0b; }
.sev-media   { background: rgba(250,204,21,.12); color: #facc15; }

.alerta-desc {
  margin: 0.35rem 0 0.5rem 1.7rem;
  font-size: var(--text-sm); color: var(--color-text-muted);
}
.alerta-footer {
  display: flex; align-items: center; justify-content: space-between;
  margin-left: 1.7rem;
}
.alerta-horas { font-size: var(--text-xs); color: var(--color-text-muted); }

/* Umbrales panel */
.umbrales-panel {
  margin-top: 2rem; border: 1px solid var(--color-border);
  border-radius: var(--radius-sm); padding: 0.75rem 1rem;
}
.umbrales-panel summary {
  cursor: pointer; font-size: var(--text-sm);
  color: var(--color-text-muted); user-select: none;
}
.umbrales-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.75rem; }
.umbral-row { display: flex; flex-direction: column; gap: 0.25rem; }
.umbral-row label { font-size: var(--text-xs); color: var(--color-text-muted); }
.umbral-input {
  padding: 0.3rem 0.5rem; border-radius: var(--radius-sm);
  border: 1px solid var(--color-border); background: transparent;
  color: var(--color-text); font-family: var(--font-mono); font-size: var(--text-sm);
  width: 100%;
}
.umbral-input:focus { outline: none; border-color: var(--color-gold); }

.alerta-icono-svg {
  flex-shrink: 0;
  color: var(--color-text-muted);
  margin-top: 1px;          /* alineación vertical con el texto */
}

.alerta-critica .alerta-icono-svg { color: #ef4444; }
.alerta-alta    .alerta-icono-svg { color: #f59e0b; }
.alerta-media   .alerta-icono-svg { color: #facc15; }

.umbrales-summary {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  user-select: none;
  list-style: none;       /* quita el triángulo nativo en algunos browsers */
}
.umbrales-summary::-webkit-details-marker { display: none; }

/* ── ESTILOS PREMIUM PARA LA PESTAÑA DE RESUMEN Y ACOPIADORES ── */
.actions-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(179, 144, 40, 0.02);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.75rem 1.25rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.actions-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  letter-spacing: 0.1em;
  color: var(--color-text-muted);
  font-weight: 600;
}
.actions-group {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.btn-export-premium {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-focus);
  background: transparent;
  color: var(--color-gold);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 34px;
}
.btn-export-premium:hover {
  background: var(--color-gold-bg);
  border-color: var(--color-gold);
  transform: translateY(-1px);
}
.btn-export-premium.btn-print {
  border-color: var(--color-border);
  color: var(--color-text-muted);
}
.btn-export-premium.btn-print:hover {
  border-color: var(--color-gold);
  color: var(--color-gold);
  background: rgba(179, 144, 40, 0.04);
}

.text-muted-badge {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: rgba(138, 135, 98, 0.08);
  color: var(--color-text-muted);
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  border: 1px solid rgba(58, 58, 40, 0.3);
}

/* Tabla Desempeño Acopiadores Premium */
.table-premium-wrapper {
  overflow-x: auto;
  width: 100%;
}
.data-table-premium {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}
.data-table-premium th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  letter-spacing: 0.1em;
  color: var(--color-text-muted);
  text-transform: uppercase;
  border-bottom: 2px solid var(--color-border);
}
.data-table-premium td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(58, 58, 40, 0.35);
  color: var(--color-text);
  vertical-align: middle;
}
.tabla-row-premium {
  transition: background 0.15s;
}
.tabla-row-premium:hover {
  background: rgba(179, 144, 40, 0.03);
}
.td-acopiador {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
  color: var(--color-text);
}
.acopiador-avatar {
  width: 26px;
  height: 26px;
  background: rgba(179, 144, 40, 0.08);
  color: var(--color-gold);
  border: 1px solid rgba(179, 144, 40, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: var(--text-sm);
}
.badge-lotes-count {
  background: rgba(179, 144, 40, 0.06);
  border: 1px solid rgba(179, 144, 40, 0.2);
  color: var(--color-gold);
  padding: 0.15rem 0.55rem;
  border-radius: 3px;
  font-size: var(--text-xs);
  display: inline-block;
}

.premium-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.premium-bar-track {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow: hidden;
  max-width: 140px;
}
.premium-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-gold), var(--color-gold-light));
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.premium-bar-val {
  font-size: var(--text-sm);
  color: var(--color-text);
  min-width: 75px;
  font-weight: 600;
}
.unit-label {
  font-size: var(--text-xs);
  color: var(--color-text-dim);
  margin-left: 0.1rem;
}
.unit-label-dim {
  font-size: var(--text-xs);
  color: var(--color-text-dim);
  font-weight: normal;
}
.highlight-gold {
  color: var(--color-gold);
  font-weight: 700;
}

/* Matriz de Volumen Acopiadores Scrollable con Sticky */
.matrix-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  gap: 1rem;
  flex-wrap: wrap;
}
.matrix-section-header .title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.matrix-section-header h2 {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  color: var(--color-text-primary);
  margin: 0;
}

.matrix-table-scroll-container {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  max-width: 100%;
  scrollbar-width: thin;
  scrollbar-color: var(--color-border-focus) var(--color-bg-card);
}

.matrix-table-scroll-container::-webkit-scrollbar {
  height: 8px;
}
.matrix-table-scroll-container::-webkit-scrollbar-track {
  background: var(--color-bg-card);
}
.matrix-table-scroll-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}
.matrix-table-scroll-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-focus);
}

.matrix-table-premium {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: var(--text-sm);
}

.matrix-table-premium th {
  padding: 0.85rem 1rem;
  background: rgba(179, 144, 40, 0.05);
  color: var(--color-gold);
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.matrix-table-premium td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(58, 58, 40, 0.35);
  color: var(--color-text);
  white-space: nowrap;
}

.sticky-column {
  position: sticky;
  left: 0;
  background: var(--color-bg-card) !important;
  z-index: 5;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.4);
  border-right: 1px solid var(--color-border) !important;
}

.matrix-row {
  transition: background 0.15s;
}
.matrix-row:hover {
  background: rgba(179, 144, 40, 0.02);
}
.matrix-row:hover .sticky-column {
  background: #28281e !important; /* Ligeramente destacado en hover */
}

.acopiador-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 200px;
}

.acopiador-avatar-sm {
  width: 20px;
  height: 20px;
  background: rgba(179, 144, 40, 0.08);
  color: var(--color-gold);
  border: 1px solid rgba(179, 144, 40, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 10px;
}

.volume-cell {
  color: var(--color-text-dim);
  opacity: 0.45;
  transition: opacity 0.15s, color 0.15s;
}
.volume-cell.has-value {
  color: var(--color-text) !important;
  opacity: 1 !important;
}

.total-column-header {
  border-left: 1px solid var(--color-border) !important;
  background: rgba(179, 144, 40, 0.08) !important;
}

.total-column {
  border-left: 1px solid var(--color-border) !important;
  background: rgba(179, 144, 40, 0.02) !important;
}

.highlight-gold-cell {
  color: var(--color-gold) !important;
  font-weight: 700 !important;
}

.totals-row-premium {
  background: rgba(179, 144, 40, 0.06);
  font-weight: 700;
  border-top: 2px solid var(--color-gold);
}
.totals-row-premium td {
  border-bottom: none;
  color: var(--color-text) !important;
}
.totals-row-premium:hover .sticky-column {
  background: rgba(179, 144, 40, 0.06) !important;
}

.totals-title-cell {
  font-family: var(--font-mono);
  color: var(--color-gold) !important;
  letter-spacing: 0.05em;
}

.highlight-gold-cell-total {
  color: var(--color-gold) !important;
  font-weight: 800 !important;
  font-size: 0.95rem !important;
  background: rgba(179, 144, 40, 0.15) !important;
  border-left: 1px solid var(--color-border) !important;
  box-shadow: inset 0 0 10px rgba(179, 144, 40, 0.1);
}
</style>
