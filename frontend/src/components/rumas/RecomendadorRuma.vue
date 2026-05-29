<template>
    <div class="recomendador">

      <!-- Toggle header -->
      <button class="rec-toggle" @click="expandido = !expandido">
        <Wand2 :size="15" class="rec-toggle-icon" />
        <span>BÚSQUEDA DE COMBINACIONES</span>
        <span class="rec-badge" v-if="resultados.length">{{ resultados.length }} sugerencia{{ resultados.length !== 1 ? 's' : '' }}</span>
        <ChevronDown :size="15" class="rec-chevron" :class="{ 'rec-chevron--up': expandido }" />
      </button>

      <div v-if="expandido" class="rec-body">

        <!-- Parámetros de búsqueda -->
        <div class="rec-params">
          <div class="rec-param-group">
            <label class="rec-label">TMS OBJETIVO</label>
            <div class="rec-input-wrap">
              <input v-model.number="params.tmsObj" type="number" min="0" step="0.5"
                     class="rec-input" placeholder="ej. 80" />
              <span class="rec-unit">T</span>
            </div>
          </div>
          <div class="rec-param-group">
            <label class="rec-label">LEY MÍNIMA</label>
            <div class="rec-input-wrap">
              <input v-model.number="params.leyMin" type="number" min="0" step="0.01"
                     class="rec-input" placeholder="ej. 0.30" />
              <span class="rec-unit">oz/tc</span>
            </div>
          </div>
          <div class="rec-param-group">
            <label class="rec-label">% REC. MÍNIMO</label>
            <div class="rec-input-wrap">
              <input v-model.number="params.recMin" type="number" min="0" max="100" step="1"
                     class="rec-input" placeholder="ej. 88" />
              <span class="rec-unit">%</span>
            </div>
          </div>
          <div class="rec-param-group">
            <label class="rec-label">% LLAMPO MÁX.</label>
            <div class="rec-input-wrap">
              <input v-model.number="params.llampoMax" type="number" min="0" max="100" step="5"
                     class="rec-input" placeholder="ej. 30" />
              <span class="rec-unit">%</span>
            </div>
          </div>
          <button class="btn-primary rec-buscar ready" @click="buscar" :disabled="buscando">
            <span v-if="buscando" class="spinner" />
            <Search v-else :size="14" />
            Buscar
          </button>
        </div>

        <!-- Sin resultados -->
        <div v-if="buscado && !resultados.length" class="rec-vacio">
          No se encontraron combinaciones con los parámetros indicados.
          Prueba relajando los filtros.
        </div>

        <!-- Resultados -->
        <div v-if="resultados.length" class="rec-resultados">
          <div class="rec-resultados-header">
            <span class="rec-resultados-titulo">TOP {{ resultados.length }} COMBINACIONES</span>
            <span class="rec-resultados-hint">Haz clic en "Aplicar" para seleccionar los lotes</span>
          </div>

          <div
            v-for="(res, idx) in resultados"
            :key="idx"
            class="rec-combo"
            :class="{ 'rec-combo--activa': comboAplicada === idx }"
          >
            <!-- Ranking badge -->
            <div class="rec-rank">#{{ idx + 1 }}</div>

            <!-- Stats de la combinación -->
            <div class="rec-combo-stats">
              <div class="rec-stat">
                <span class="rec-stat-lbl">LOTES</span>
                <span class="rec-stat-val">{{ res.lotes.length }}</span>
              </div>
              <div class="rec-stat">
                <span class="rec-stat-lbl">TMS TOTAL</span>
                <span class="rec-stat-val">{{ fmtNum(res.preview.total_tms, 2) }} T</span>
                <span v-if="params.tmsObj" class="rec-stat-delta"
                      :class="deltaClass(res.preview.total_tms, params.tmsObj)">
                  {{ deltaLabel(res.preview.total_tms, params.tmsObj) }}
                </span>
              </div>
              <div class="rec-stat">
                <span class="rec-stat-lbl">LEY POND.</span>
                <span class="rec-stat-val">{{ res.preview.ley_ponderada != null ? fmtNum(res.preview.ley_ponderada, 4) : '—' }}</span>
                <span class="rec-stat-unit">oz/tc</span>
              </div>
              <div class="rec-stat">
                <span class="rec-stat-lbl">% REC.</span>
                <span class="rec-stat-val">{{ res.preview.rec_promedio != null ? fmtNum(res.preview.rec_promedio, 1) + '%' : '—' }}</span>
              </div>
              <div class="rec-stat">
                <span class="rec-stat-lbl">% LLAMPO</span>
                <span class="rec-stat-val">{{ res.preview.pct_llampo != null ? fmtNum(res.preview.pct_llampo, 1) + '%' : '0%' }}</span>
              </div>
              <div class="rec-stat rec-stat--score">
                <span class="rec-stat-lbl">SCORE</span>
                <span class="rec-stat-val gold">{{ (res.score * 100).toFixed(0) }}</span>
              </div>
            </div>

            <!-- IPs de la combinación -->
            <div class="rec-combo-ips">
              <span v-for="ip in res.lotes.map(l => l.ip)" :key="ip" class="rec-ip-tag">
                {{ ip }}
              </span>
            </div>

            <!-- Botón aplicar -->
            <button
              class="btn-primary rec-aplicar ready"
              :class="{ 'rec-aplicar--applied': comboAplicada === idx }"
              @click="aplicar(res.lotes, idx)"
            >
              <Check v-if="comboAplicada === idx" :size="13" />
              <span v-else>Aplicar</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { ref, reactive } from 'vue'
  import { Wand2, ChevronDown, Search, Check } from 'lucide-vue-next'
  import type { LoteDisponibleOut } from '@/api/rumas'

  // ── Props & Emits ──────────────────────────────────────────────────────────────
  const props = defineProps<{
    lotes: LoteDisponibleOut[]
  }>()

  const emit = defineEmits<{
    (e: 'aplicar', ips: string[]): void
  }>()

  // ── Estado local ───────────────────────────────────────────────────────────────
  const expandido    = ref(false)
  const buscando     = ref(false)
  const buscado      = ref(false)
  const comboAplicada = ref<number | null>(null)

  const params = reactive({
    tmsObj:    null as number | null,
    leyMin:    null as number | null,
    recMin:    null as number | null,
    llampoMax: null as number | null,
  })

  interface Preview {
    total_tms: number
    ley_ponderada: number | null
    rec_promedio: number | null
    pct_llampo: number | null
  }

  interface Resultado {
    lotes: LoteDisponibleOut[]
    preview: Preview
    score: number
  }

  const resultados = ref<Resultado[]>([])

  // ── Algoritmo ──────────────────────────────────────────────────────────────────

  function calcPreview(lotes: LoteDisponibleOut[]): Preview {
    const total_tms = lotes.reduce((s, l) => s + (l.tms ?? 0), 0)
    // Ley ponderada: Σ(ley × tms) / Σ(tms con ley)
    let sumTmsLey = 0, sumLeyTms = 0
    let sumTmsRec = 0, sumRec = 0
    let llampoTms = 0

    for (const l of lotes) {
      const tms = l.tms ?? 0
      if (l.ley_avg != null) { sumLeyTms += l.ley_avg * tms; sumTmsLey += tms }
      if (l.rec_porc != null) { sumRec += l.rec_porc * tms; sumTmsRec += tms }
      if (l.tipo_material?.toUpperCase().includes('LLAMPO')) llampoTms += tms
    }

    return {
      total_tms: +total_tms.toFixed(3),
      ley_ponderada: sumTmsLey > 0 ? +(sumLeyTms / sumTmsLey).toFixed(4) : null,
      rec_promedio:  sumTmsRec > 0 ? +(sumRec / sumTmsRec).toFixed(2) : null,
      pct_llampo:    total_tms > 0 ? +(llampoTms / total_tms * 100).toFixed(1) : null,
    }
  }

  function calcScore(preview: Preview, tmsObj: number | null): number {
    // Puntúa qué tan bien se ajusta la combinación a los parámetros
    let score = 0
    let factores = 0

    // Proximidad al TMS objetivo (40%)
    if (tmsObj && tmsObj > 0 && preview.total_tms > 0) {
      const delta = Math.abs(preview.total_tms - tmsObj) / tmsObj
      score += (1 - Math.min(delta, 1)) * 0.40
      factores += 0.40
    }

    // Calidad de ley (35%)
    if (preview.ley_ponderada != null) {
      // Normaliza: ley típica 0.10 - 0.60 oz/tc
      const leyNorm = Math.min(preview.ley_ponderada / 0.50, 1)
      score += leyNorm * 0.35
      factores += 0.35
    }

    // Recuperación (25%)
    if (preview.rec_promedio != null) {
      const recNorm = Math.min(preview.rec_promedio / 95, 1)
      score += recNorm * 0.25
      factores += 0.25
    }

    return factores > 0 ? score / factores : 0
  }

  /** Rellena codiciosamente hasta alcanzar tmsObj */
  function greedyFill(sorted: LoteDisponibleOut[], tmsObj: number | null): LoteDisponibleOut[] {
    const combo: LoteDisponibleOut[] = []
    let acc = 0
    for (const l of sorted) {
      if (tmsObj == null || acc < tmsObj * 1.05) {
        combo.push(l)
        acc += l.tms ?? 0
        if (tmsObj != null && acc >= tmsObj * 1.05) break
      }
    }
    return combo
  }

  /** Genera combinaciones con distintas estrategias de ordenamiento */
  function generarCombinaciones(candidatos: LoteDisponibleOut[], tmsObj: number | null): Resultado[] {
    if (!candidatos.length) return []

    const estrategias: Array<(a: LoteDisponibleOut, b: LoteDisponibleOut) => number> = [
      (a, b) => (b.ley_avg ?? 0) - (a.ley_avg ?? 0),                            // mejor ley primero
      (a, b) => (b.rec_porc ?? 0) - (a.rec_porc ?? 0),                          // mejor rec primero
      (a, b) => ((b.ley_avg ?? 0) * (b.rec_porc ?? 0)) - ((a.ley_avg ?? 0) * (a.rec_porc ?? 0)), // mejor calidad combinada
      (a, b) => (b.tms ?? 0) - (a.tms ?? 0),                                    // lotes grandes primero
      (a, b) => (a.tms ?? 0) - (b.tms ?? 0),                                    // lotes chicos primero (precisión)
      (a, b) => (b.dias_almacen ?? 0) - (a.dias_almacen ?? 0),                  // más antiguos primero
      // Dos shuffles aleatorios para diversidad
      () => Math.random() - 0.5,
      () => Math.random() - 0.5,
    ]

    const vistas = new Set<string>()
    const resultados: Resultado[] = []

    for (const estrategia of estrategias) {
      const sorted = [...candidatos].sort(estrategia)
      const combo  = greedyFill(sorted, tmsObj)
      if (!combo.length) continue

      const key = combo.map(l => l.ip).sort().join(',')
      if (vistas.has(key)) continue
      vistas.add(key)

      const preview = calcPreview(combo)
      const score   = calcScore(preview, tmsObj)
      resultados.push({ lotes: combo, preview, score })
    }

    // Ordenar por score descendente
    return resultados
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
  }

  async function buscar() {
    buscando.value = true
    buscado.value  = false
    comboAplicada.value = null
    resultados.value = []

    // Simula tick async para que el spinner se muestre
    await new Promise(r => setTimeout(r, 40))

    // Filtra candidatos válidos
    const candidatos = props.lotes.filter(l => {
      if (!l.tms || l.tms <= 0) return false
      if (params.leyMin != null && (l.ley_avg == null || l.ley_avg < params.leyMin)) return false
      if (params.recMin != null && (l.rec_porc == null || l.rec_porc < params.recMin)) return false
      return true
    })

    let combos = generarCombinaciones(candidatos, params.tmsObj ?? null)

    // Post-filtro: % llampo máximo
    if (params.llampoMax != null) {
      combos = combos.filter(r => (r.preview.pct_llampo ?? 0) <= params.llampoMax!)
    }

    resultados.value = combos
    buscado.value    = true
    buscando.value   = false
  }

  function aplicar(lotes: LoteDisponibleOut[], idx: number) {
    comboAplicada.value = idx
    emit('aplicar', lotes.map(l => l.ip))
  }

  // ── Helpers UI ─────────────────────────────────────────────────────────────────
  function fmtNum(v: number | null | undefined, dec = 2) {
    if (v == null) return '—'
    return new Intl.NumberFormat('es-PE', { minimumFractionDigits: dec, maximumFractionDigits: dec }).format(v)
  }

  function deltaLabel(actual: number, objetivo: number): string {
    const diff = actual - objetivo
    const pct  = ((diff / objetivo) * 100).toFixed(1)
    return `${diff >= 0 ? '+' : ''}${pct}%`
  }

  function deltaClass(actual: number, objetivo: number): string {
    const pct = Math.abs((actual - objetivo) / objetivo)
    if (pct <= 0.05) return 'delta-ok'
    if (pct <= 0.12) return 'delta-warn'
    return 'delta-bad'
  }
  </script>

  <style scoped>
  @import '@/assets/base.css';

  /* ── Contenedor ── */
  .recomendador {
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-bg-card);
    margin-bottom: 1rem;
    overflow: hidden;
  }

  /* ── Toggle ── */
  .rec-toggle {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    width: 100%;
    padding: 0.65rem 1.1rem;
    background: rgba(184, 150, 46, 0.04);
    border: none;
    border-bottom: 1px solid transparent;
    cursor: pointer;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.18em;
    color: var(--color-gold);
    text-align: left;
    transition: background 0.15s;
  }
  .rec-toggle:hover { background: rgba(184, 150, 46, 0.08); }
  .rec-toggle-icon { flex-shrink: 0; opacity: 0.8; }

  .rec-badge {
    margin-left: auto;
    background: rgba(184,150,46,0.18);
    color: var(--color-gold-light);
    border-radius: 10px;
    padding: 1px 8px;
    font-size: var(--text-xs);
    letter-spacing: 0.05em;
  }

  .rec-chevron {
    color: var(--color-text-muted);
    transition: transform 0.2s;
    flex-shrink: 0;
  }
  .rec-chevron--up { transform: rotate(180deg); }

  /* ── Body ── */
  .rec-body {
    border-top: 1px solid var(--color-border);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* ── Params row ── */
  .rec-params {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    align-items: flex-end;
  }

  .rec-param-group {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    min-width: 110px;
    flex: 1;
  }

  .rec-label {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.14em;
    color: var(--color-text-muted);
  }

  .rec-input-wrap {
    position: relative;
    display: flex;
    align-items: center;
  }

  .rec-input {
    width: 100%;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    color: var(--color-text);
    font-family: var(--font-mono);
    font-size: var(--text-md);
    padding: 0.4rem 2.6rem 0.4rem 0.65rem;
    outline: none;
    transition: border-color 0.15s;
  }
  .rec-input:focus { border-color: var(--color-gold); }
  .rec-input::placeholder { color: var(--color-text-faint); }

  .rec-unit {
    position: absolute;
    right: 0.55rem;
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    pointer-events: none;
  }

  .rec-buscar {
    align-self: flex-end;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.45rem 1.1rem;
    font-size: var(--text-sm);
    min-height: 34px;
    white-space: nowrap;
    flex-shrink: 0;
  }

  /* ── Vacío ── */
  .rec-vacio {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    text-align: center;
    padding: 1rem;
  }

  /* ── Resultados ── */
  .rec-resultados-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.6rem;
  }
  .rec-resultados-titulo {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    letter-spacing: 0.18em;
    color: var(--color-gold);
    font-weight: 700;
  }
  .rec-resultados-hint {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-faint);
  }

  /* ── Combo card ── */
  .rec-combo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.7rem 0.9rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-bg);
    transition: border-color 0.15s, background 0.15s;
    flex-wrap: wrap;
  }
  .rec-combo:hover { border-color: rgba(184,150,46,0.3); background: rgba(184,150,46,0.03); }
  .rec-combo--activa {
    border-color: var(--color-gold);
    background: rgba(184,150,46,0.06);
  }

  .rec-rank {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-faint);
    min-width: 22px;
    flex-shrink: 0;
  }

  .rec-combo-stats {
    display: flex;
    gap: 1.2rem;
    flex-wrap: wrap;
    flex: 1;
    align-items: flex-end;
  }

  .rec-stat {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    min-width: 60px;
  }
  .rec-stat--score { min-width: 48px; }

  .rec-stat-lbl {
    font-family: var(--font-mono);
    font-size: 9px;
    letter-spacing: 0.16em;
    color: var(--color-text-faint);
  }
  .rec-stat-val {
    font-family: var(--font-mono);
    font-size: var(--text-md);
    font-weight: 700;
    color: var(--color-text);
  }
  .rec-stat-val.gold { color: var(--color-gold); }
  .rec-stat-unit {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-faint);
  }
  .rec-stat-delta {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
  }
  .delta-ok   { color: var(--color-success); }
  .delta-warn { color: var(--color-warning); }
  .delta-bad  { color: var(--color-error); }

  /* ── IPs tags ── */
  .rec-combo-ips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    width: 100%;
    order: 10;
    padding-top: 0.35rem;
    border-top: 1px solid rgba(58,58,40,0.3);
    margin-top: 0.1rem;
  }
  .rec-ip-tag {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    background: rgba(184,150,46,0.08);
    border: 1px solid rgba(184,150,46,0.15);
    border-radius: 2px;
    padding: 1px 5px;
  }

  /* ── Botón aplicar ── */
  .rec-aplicar {
    flex-shrink: 0;
    padding: 0.4rem 0.85rem;
    font-size: var(--text-sm);
    min-height: 30px;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    align-self: flex-start;
  }
  .rec-aplicar--applied {
    background: var(--color-success) !important;
    border-color: var(--color-success) !important;
  }

  /* ── Responsive ── */
  @media (max-width: 700px) {
    .rec-params { flex-direction: column; }
    .rec-combo-stats { gap: 0.75rem; }
  }
  </style>
