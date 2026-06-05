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
          <label class="rec-label">LEY MÍNIMA <span class="rec-label-hint">(suave)</span></label>
          <div class="rec-input-wrap">
            <input v-model.number="params.leyMin" type="number" min="0" step="0.01"
                   class="rec-input" placeholder="ej. 0.30" />
            <span class="rec-unit">oz/tc</span>
          </div>
        </div>
        <div class="rec-param-group">
          <label class="rec-label">% REC. MÍNIMO <span class="rec-label-hint">(suave)</span></label>
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

      <!-- Nota sobre modo flexible -->
      <p v-if="(params.leyMin || params.recMin) && buscado" class="rec-nota">
        <Info :size="12" style="flex-shrink:0" />
        Los filtros de ley y recuperación son <strong>indicativos</strong>. Se muestran todas las combinaciones posibles ordenadas por ajuste a los parámetros.
      </p>

      <!-- Sin resultados (realmente sin lotes disponibles) -->
      <div v-if="buscado && !resultados.length" class="rec-vacio">
        No hay lotes disponibles con TMS &gt; 0. Verifica que los lotes estén habilitados y tengan muestreo registrado.
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

          <!-- Badge de ajuste a parámetros -->
          <div
            class="rec-match-badge"
            :class="matchClass(res.matchPct)"
            :title="`Ajuste a parámetros: ${res.matchPct}%`"
          >
            {{ res.matchPct }}%
          </div>

          <!-- Contador lotes -->
          <div class="rec-stat">
            <span class="rec-stat-lbl">LOTES</span>
            <span class="rec-stat-val">{{ res.lotes.length }}</span>
          </div>

          <!-- TMS total con delta -->
          <div class="rec-stat">
            <span class="rec-stat-lbl">TMS TOTAL</span>
            <span class="rec-stat-val">{{ fmtNum(res.preview.total_tms, 2) }} T</span>
            <span v-if="params.tmsObj" class="rec-stat-delta"
                  :class="deltaClass(res.preview.total_tms, params.tmsObj)">
              {{ deltaLabel(res.preview.total_tms, params.tmsObj) }}
            </span>
          </div>

          <!-- Ley ponderada -->
          <div class="rec-stat">
            <span class="rec-stat-lbl">LEY POND.</span>
            <span class="rec-stat-val"
                  :class="params.leyMin && res.preview.ley_ponderada != null && res.preview.ley_ponderada < params.leyMin ? 'rec-val-warn' : ''">
              {{ res.preview.ley_ponderada != null ? fmtNum(res.preview.ley_ponderada, 4) : '—' }}
            </span>
            <span class="rec-stat-unit">oz/tc</span>
            <span
              v-if="params.leyMin && res.preview.ley_ponderada != null"
              class="rec-stat-delta"
              :class="res.preview.ley_ponderada >= params.leyMin ? 'delta-ok' : 'delta-bad'"
            >
              {{ deltaLeyLabel(res.preview.ley_ponderada, params.leyMin) }}
            </span>
          </div>

          <!-- Recuperación -->
          <div class="rec-stat">
            <span class="rec-stat-lbl">% REC.</span>
            <span class="rec-stat-val"
                  :class="params.recMin && res.preview.rec_promedio != null && res.preview.rec_promedio < params.recMin ? 'rec-val-warn' : ''">
              {{ res.preview.rec_promedio != null ? fmtNum(res.preview.rec_promedio, 1) + '%' : '—' }}
            </span>
            <span
              v-if="params.recMin && res.preview.rec_promedio != null"
              class="rec-stat-delta"
              :class="res.preview.rec_promedio >= params.recMin ? 'delta-ok' : 'delta-bad'"
            >
              {{ deltaRecLabel(res.preview.rec_promedio, params.recMin) }}
            </span>
          </div>

          <!-- % Llampo -->
          <div class="rec-stat">
            <span class="rec-stat-lbl">% LLAMPO</span>
            <span class="rec-stat-val"
                  :class="params.llampoMax && res.preview.pct_llampo != null && res.preview.pct_llampo > params.llampoMax ? 'rec-val-warn' : ''">
              {{ res.preview.pct_llampo != null ? fmtNum(res.preview.pct_llampo, 1) + '%' : '0%' }}
            </span>
            <span
              v-if="params.llampoMax && res.preview.pct_llampo != null"
              class="rec-stat-delta"
              :class="res.preview.pct_llampo <= params.llampoMax ? 'delta-ok' : 'delta-bad'"
            >
              {{ deltaLlampoLabel(res.preview.pct_llampo, params.llampoMax) }}
            </span>
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
import { Wand2, ChevronDown, Search, Check, Info } from 'lucide-vue-next'
import type { LoteDisponibleOut } from '@/api/rumas'

// ── Props & Emits ──────────────────────────────────────────────────────────────
const props = defineProps<{
  lotes: LoteDisponibleOut[]
}>()

const emit = defineEmits<{
  (e: 'aplicar', ips: string[]): void
}>()

// ── Estado local ───────────────────────────────────────────────────────────────
const expandido     = ref(false)
const buscando      = ref(false)
const buscado       = ref(false)
const comboAplicada = ref<number | null>(null)

const params = reactive({
  tmsObj:    null as number | null,
  leyMin:    null as number | null,
  recMin:    null as number | null,
  llampoMax: null as number | null,
})

interface Preview {
  total_tms:    number
  ley_ponderada: number | null
  rec_promedio:  number | null
  pct_llampo:    number | null
}

interface Resultado {
  lotes:    LoteDisponibleOut[]
  preview:  Preview
  score:    number
  matchPct: number  // 0–100: qué tan cerca está de los parámetros objetivo
}

const resultados = ref<Resultado[]>([])

// ── Algoritmo ──────────────────────────────────────────────────────────────────

function calcPreview(lotes: LoteDisponibleOut[]): Preview {
  const total_tms = lotes.reduce((s, l) => s + (l.tms ?? 0), 0)
  let sumTmsLey = 0, sumLeyTms = 0
  let sumTmsRec = 0, sumRec = 0
  let llampoTms = 0

  for (const l of lotes) {
    const tms = l.tms ?? 0
    if (l.ley_avg != null)  { sumLeyTms += l.ley_avg * tms;  sumTmsLey += tms }
    if (l.rec_porc != null) { sumRec    += l.rec_porc * tms; sumTmsRec += tms }
    if (l.tipo_material?.toUpperCase().includes('LLAMPO')) llampoTms += tms
  }

  return {
    total_tms:     +total_tms.toFixed(3),
    ley_ponderada: sumTmsLey > 0 ? +(sumLeyTms / sumTmsLey).toFixed(4) : null,
    rec_promedio:  sumTmsRec > 0 ? +(sumRec    / sumTmsRec).toFixed(2) : null,
    pct_llampo:    total_tms > 0 ? +(llampoTms / total_tms * 100).toFixed(1) : null,
  }
}

/**
 * Score numérico (0–1) y matchPct (0–100) para una combinación.
 * matchPct mide qué fracción de los parámetros objetivo se cumple.
 * Score pondera calidad + proximidad al objetivo.
 */
function calcScore(preview: Preview): { score: number; matchPct: number } {
  let score = 0
  let factores = 0
  let cumplidos = 0
  let totalParams = 0

  // Proximidad al TMS objetivo (40%)
  if (params.tmsObj && params.tmsObj > 0 && preview.total_tms > 0) {
    const delta = Math.abs(preview.total_tms - params.tmsObj) / params.tmsObj
    const s = Math.max(0, 1 - delta)   // 1 = exacto, 0 = ≥100% de diferencia
    score   += s * 0.40
    factores += 0.40
    totalParams++
    if (delta <= 0.10) cumplidos++ // dentro del ±10%
  }

  // Calidad de ley (35%)
  if (preview.ley_ponderada != null) {
    const ref = params.leyMin ?? 0.30  // referencia de normalización
    const leyNorm = Math.min(preview.ley_ponderada / Math.max(ref, 0.10), 1)
    score    += leyNorm * 0.35
    factores += 0.35
    if (params.leyMin != null) {
      totalParams++
      if (preview.ley_ponderada >= params.leyMin) cumplidos++
    }
  }

  // Recuperación (25%)
  if (preview.rec_promedio != null) {
    const ref = params.recMin ?? 90
    const recNorm = Math.min(preview.rec_promedio / Math.max(ref, 1), 1)
    score    += recNorm * 0.25
    factores += 0.25
    if (params.recMin != null) {
      totalParams++
      if (preview.rec_promedio >= params.recMin) cumplidos++
    }
  }

  // Penalizar si pct_llampo supera el máximo
  if (params.llampoMax != null && preview.pct_llampo != null) {
    totalParams++
    if (preview.pct_llampo <= params.llampoMax) {
      cumplidos++
    } else {
      // penalización suave (no bloqueante)
      const exceso = (preview.pct_llampo - params.llampoMax) / 100
      score = Math.max(0, score - exceso * 0.30)
    }
  }

  const finalScore = factores > 0 ? score / factores : 0
  const matchPct   = totalParams > 0 ? Math.round((cumplidos / totalParams) * 100) : 100

  return { score: finalScore, matchPct }
}

/**
 * Rellena codiciosamente hasta alcanzar tmsObj±tolerancia.
 * Si hay objetivo, para cuando alcanza el objetivo o cuando agregar el siguiente
 * lote haría que se pase demasiado.
 */
function greedyFill(sorted: LoteDisponibleOut[], toleranciaArriba = 1.10): LoteDisponibleOut[] {
  const tmsObj = params.tmsObj
  const combo: LoteDisponibleOut[] = []
  let acc = 0
  for (const l of sorted) {
    const nextAcc = acc + (l.tms ?? 0)
    // Si hay objetivo y ya alcanzamos el mínimo, ver si vale la pena agregar más
    if (tmsObj != null && acc >= tmsObj * 0.90) {
      // Solo agregar si no nos pasamos de la tolerancia
      if (nextAcc > tmsObj * toleranciaArriba) break
    }
    combo.push(l)
    acc = nextAcc
    if (tmsObj != null && acc >= tmsObj * toleranciaArriba) break
  }
  return combo
}

/**
 * Genera hasta 6 combinaciones con distintas estrategias deterministas.
 * Incluye ventanas de búsqueda para mayor diversidad.
 */
function generarCombinaciones(candidatos: LoteDisponibleOut[]): Resultado[] {
  if (!candidatos.length) return []

  // Filtrar llampo si hay límite (preferir candidatos dentro del límite pero sin excluir)
  const sinExcesoDeLlampo = params.llampoMax != null
    ? candidatos.filter(l => !l.tipo_material?.toUpperCase().includes('LLAMPO'))
    : []

  type SortFn = (a: LoteDisponibleOut, b: LoteDisponibleOut) => number

  // Estrategias deterministas con diversidad real
  const estrategias: Array<{ fn: SortFn; pool?: LoteDisponibleOut[]; tolerancia?: number }> = [
    // 1. Mejor ley ponderada primero
    { fn: (a, b) => (b.ley_avg ?? 0) - (a.ley_avg ?? 0) },
    // 2. Mejor recuperación primero
    { fn: (a, b) => (b.rec_porc ?? 0) - (a.rec_porc ?? 0) },
    // 3. Mejor calidad combinada (ley × rec)
    { fn: (a, b) => ((b.ley_avg ?? 0) * (b.rec_porc ?? 0)) - ((a.ley_avg ?? 0) * (a.rec_porc ?? 0)) },
    // 4. Lotes grandes primero (minimiza cantidad de lotes)
    { fn: (a, b) => (b.tms ?? 0) - (a.tms ?? 0) },
    // 5. Lotes más antiguos primero (gestión de inventario)
    { fn: (a, b) => (b.dias_almacen ?? 0) - (a.dias_almacen ?? 0) },
    // 6. Ley alta + tolerancia más ajustada (para evitar pasarse del TMS)
    { fn: (a, b) => (b.ley_avg ?? 0) - (a.ley_avg ?? 0), tolerancia: 1.03 },
    // 7. Sin llampo + mejor ley (si hay límite de llampo)
    ...(sinExcesoDeLlampo.length > 0
      ? [{ fn: (a: LoteDisponibleOut, b: LoteDisponibleOut) => (b.ley_avg ?? 0) - (a.ley_avg ?? 0), pool: sinExcesoDeLlampo }]
      : []
    ),
    // 8. Sin llampo + mejor recuperación
    ...(sinExcesoDeLlampo.length > 0
      ? [{ fn: (a: LoteDisponibleOut, b: LoteDisponibleOut) => (b.rec_porc ?? 0) - (a.rec_porc ?? 0), pool: sinExcesoDeLlampo }]
      : []
    ),
  ]

  const vistas = new Set<string>()
  const todos: Resultado[] = []

  for (const { fn, pool, tolerancia } of estrategias) {
    const fuente = pool ?? candidatos
    const sorted = [...fuente].sort(fn)
    const combo  = greedyFill(sorted, tolerancia ?? 1.10)
    if (!combo.length) continue

    const key = combo.map(l => l.ip).sort().join(',')
    if (vistas.has(key)) continue
    vistas.add(key)

    const preview             = calcPreview(combo)
    const { score, matchPct } = calcScore(preview)
    todos.push({ lotes: combo, preview, score, matchPct })
  }

  return todos
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
}

async function buscar() {
  buscando.value      = true
  buscado.value       = false
  comboAplicada.value = null
  resultados.value    = []

  await new Promise(r => setTimeout(r, 40))

  // Solo excluir lotes sin TMS (sin muestreo): no tienen datos para calcular
  const candidatos = props.lotes.filter(l => l.tms != null && l.tms > 0)

  resultados.value = generarCombinaciones(candidatos)
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

/** Diferencia de ley vs mínimo requerido (oz/tc) */
function deltaLeyLabel(actual: number, minimo: number): string {
  const diff = actual - minimo
  return `${diff >= 0 ? '+' : ''}${diff.toFixed(4)} oz/tc`
}

/** Diferencia de recuperación vs mínimo requerido (puntos porcentuales) */
function deltaRecLabel(actual: number, minimo: number): string {
  const diff = actual - minimo
  return `${diff >= 0 ? '+' : ''}${diff.toFixed(1)} pp`
}

/** Diferencia de % llampo vs máximo permitido */
function deltaLlampoLabel(actual: number, maximo: number): string {
  const diff = actual - maximo
  return `${diff >= 0 ? '+' : ''}${diff.toFixed(1)} pp`
}

function matchClass(pct: number): string {
  if (pct >= 100) return 'match-full'
  if (pct >= 75)  return 'match-good'
  if (pct >= 50)  return 'match-partial'
  return 'match-low'
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
.rec-toggle-icon  { flex-shrink: 0; opacity: 0.8; }

.rec-badge {
  margin-left: auto;
  background: rgba(184,150,46,0.18);
  color: var(--color-gold-light);
  border-radius: 10px;
  padding: 1px 8px;
  font-size: var(--text-xs);
  letter-spacing: 0.05em;
}

.rec-chevron { color: var(--color-text-muted); transition: transform 0.2s; flex-shrink: 0; }
.rec-chevron--up { transform: rotate(180deg); }

/* ── Body ── */
.rec-body {
  border-top: 1px solid var(--color-border);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* ── Nota modo flexible ── */
.rec-nota {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  background: rgba(184,150,46,0.05);
  border: 1px solid rgba(184,150,46,0.15);
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.75rem;
  margin: 0;
}
.rec-nota strong { color: var(--color-gold); }

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
.rec-label-hint {
  font-size: 9px;
  opacity: 0.6;
  letter-spacing: 0.05em;
}
.rec-input-wrap { position: relative; display: flex; align-items: center; }
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
.rec-combo:hover            { border-color: rgba(184,150,46,0.3); background: rgba(184,150,46,0.03); }
.rec-combo--activa          { border-color: var(--color-gold); background: rgba(184,150,46,0.06); }

.rec-rank {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-faint);
  min-width: 22px;
  flex-shrink: 0;
}

/* ── Match badge ── */
.rec-match-badge {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 10px;
  flex-shrink: 0;
  letter-spacing: 0.04em;
}
.match-full    { background: rgba(34,197,94,0.18);  color: var(--color-success); border: 1px solid rgba(34,197,94,0.3); }
.match-good    { background: rgba(184,150,46,0.18); color: var(--color-gold);    border: 1px solid rgba(184,150,46,0.3); }
.match-partial { background: rgba(234,179,8,0.18);  color: #ca8a04;              border: 1px solid rgba(234,179,8,0.3); }
.match-low     { background: rgba(239,68,68,0.12);  color: var(--color-error);   border: 1px solid rgba(239,68,68,0.25); }

/* ── Stats ── */
.rec-combo-stats { display: flex; gap: 1.2rem; flex-wrap: wrap; flex: 1; align-items: flex-end; }
.rec-stat        { display: flex; flex-direction: column; gap: 0.1rem; min-width: 60px; }
.rec-stat-lbl    { font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.16em; color: var(--color-text-faint); }
.rec-stat-val    { font-family: var(--font-mono); font-size: var(--text-md); font-weight: 700; color: var(--color-text); }
.rec-stat-unit   { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-faint); }
.rec-stat-delta  { font-family: var(--font-mono); font-size: var(--text-xs); }
.delta-ok        { color: var(--color-success); }
.delta-warn      { color: var(--color-warning); }
.delta-bad       { color: var(--color-error); }
.rec-val-warn    { color: var(--color-warning) !important; }

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
.rec-aplicar--applied { background: var(--color-success) !important; border-color: var(--color-success) !important; }

/* ── Responsive ── */
@media (max-width: 700px) {
  .rec-params     { flex-direction: column; }
  .rec-combo-stats { gap: 0.75rem; }
}
</style>
