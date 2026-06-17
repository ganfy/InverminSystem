import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// ── Tipos ─────────────────────────────────────────────────────────────────────
export type FontSize = 'sm' | 'md' | 'lg' | 'xl'
export type Contrast = 'normal' | 'alto' | 'solar'

export interface AccessibilityPrefs {
  fontSize: FontSize
  contrast: Contrast
}

// ── Escalas de fuente (multiplicador sobre los valores base de variables.css) ──
const FONT_SCALES: Record<FontSize, number> = {
  sm:  0.90,
  md:  1.00,  // default — idéntico al diseño actual
  lg:  1.15,
  xl:  1.35,
}

// ── Valores base de variables.css (en rem) ────────────────────────────────────
const BASE_SIZES = {
  xs:    0.65,
  sm:    0.75,
  md:    0.85,
  base:  1.00,
  lg:    1.30,
  xl:    1.60,
  xxl:   2.00,
  xxxl:  2.50,
  title: 8.00,
}

// ── Paletas de contraste ───────────────────────────────────────────────────────
// Solo se sobreescriben las variables necesarias; el resto queda intacto.
const CONTRAST_PALETTES: Record<Contrast, Record<string, string>> = {
  normal: {
    // Sin cambios: restaura los valores originales de variables.css
    '--color-bg':           '#1a1a14',
    '--color-bg-card':      '#23231a',
    '--color-bg-input':     '#1a1a12',
    '--color-border':       '#3a3a28',
    '--color-border-focus': '#9c843b',
    '--color-text':         '#d4c47a',
    '--color-text-muted':   '#8a8762',
    '--color-text-dim':     '#6b6b50',
    '--color-text-faint':   '#4a4a36',
    '--color-gold':         '#b39028',
    '--color-gold-light':   'rgba(172,145,69,0.78)',
  },
  alto: {
    // Texto más brillante, fondos ligeramente más claros, bordes más visibles
    '--color-bg':           '#1e1e16',
    '--color-bg-card':      '#2a2a20',
    '--color-bg-input':     '#1e1e14',
    '--color-border':       '#5a5a3a',
    '--color-border-focus': '#c8a84a',
    '--color-text':         '#f0e090',
    '--color-text-muted':   '#b8b480',
    '--color-text-dim':     '#909060',
    '--color-text-faint':   '#686848',
    '--color-gold':         '#d4aa30',
    '--color-gold-light':   'rgba(212,170,48,0.9)',
  },
  solar: {
    // Inversión completa: fondo claro, texto oscuro — máxima legibilidad al sol
    '--color-bg':           '#f0ead8',
    '--color-bg-card':      '#e8e0c8',
    '--color-bg-input':     '#ddd5bc',
    '--color-border':       '#a89870',
    '--color-border-focus': '#7a6020',
    '--color-text':         '#1a1a0a',
    '--color-text-muted':   '#3a3820',
    '--color-text-dim':     '#5a5840',
    '--color-text-faint':   '#7a7860',
    '--color-gold':         '#6a4800',
    '--color-gold-light':   'rgba(100,72,0,0.85)',
  },
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function storageKey(userId: string | number): string {
  return `accessibility_prefs_${userId}`
}

function loadPrefs(userId: string | number): AccessibilityPrefs {
  try {
    const raw = localStorage.getItem(storageKey(userId))
    if (raw) return JSON.parse(raw) as AccessibilityPrefs
  } catch {}
  return { fontSize: 'md', contrast: 'normal' }
}

function savePrefs(userId: string | number, prefs: AccessibilityPrefs) {
  try {
    localStorage.setItem(storageKey(userId), JSON.stringify(prefs))
  } catch {}
}

// ── Aplicar variables CSS al :root ────────────────────────────────────────────
function applyToDom(prefs: AccessibilityPrefs) {
  const root = document.documentElement
  const scale = FONT_SCALES[prefs.fontSize]

  // Fuentes escaladas
  for (const [key, base] of Object.entries(BASE_SIZES)) {
    root.style.setProperty(`--text-${key}`, `${(base * scale).toFixed(4)}rem`)
  }

  // Paleta de contraste
  const palette = CONTRAST_PALETTES[prefs.contrast]
  for (const [prop, value] of Object.entries(palette)) {
    root.style.setProperty(prop, value)
  }

  // Clase en body para estilos que no se pueden hacer solo con variables
  // (ej. ajustes de sombras en modo solar)
  root.classList.remove('a11y-normal', 'a11y-alto', 'a11y-solar')
  root.classList.add(`a11y-${prefs.contrast}`)
}

// ── Store ─────────────────────────────────────────────────────────────────────
export const useAccessibilityStore = defineStore('accessibility', () => {
  const prefs   = ref<AccessibilityPrefs>({ fontSize: 'md', contrast: 'normal' })
  const userId  = ref<string | null>(null)

  /** Llamar después de autenticar al usuario. */
  function init(uid: string | number) {
    userId.value = String(uid)
    prefs.value  = loadPrefs(uid)
    applyToDom(prefs.value)
  }

  /** Llamar al hacer logout para resetear al diseño original. */
  function reset() {
    userId.value = null
    prefs.value  = { fontSize: 'md', contrast: 'normal' }
    applyToDom(prefs.value)
  }

  function setFontSize(size: FontSize) {
    prefs.value = { ...prefs.value, fontSize: size }
    _persist()
  }

  function setContrast(contrast: Contrast) {
    prefs.value = { ...prefs.value, contrast }
    _persist()
  }

  function _persist() {
    applyToDom(prefs.value)
    if (userId.value) savePrefs(userId.value, prefs.value)
  }

  // Aplicar cada vez que cambien las prefs (por si alguien las muta directamente)
  watch(prefs, () => applyToDom(prefs.value), { deep: true })

  return {
    prefs,
    userId,
    init,
    reset,
    setFontSize,
    setContrast,
  }
})
