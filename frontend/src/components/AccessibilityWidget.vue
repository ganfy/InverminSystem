<template>
  <!-- Botón flotante -->
  <div class="a11y-widget" :class="{ 'a11y-widget--solar': isSolar }">
    <button
      id="a11y-toggle-btn"
      class="a11y-toggle"
      :class="{ 'a11y-toggle--active': open }"
      @click.stop="open = !open"
      :title="open ? 'Cerrar ajustes de visualización' : 'Ajustes de visualización'"
      aria-label="Ajustes de visualización"
    >
      <!-- Ícono dinámico según contraste activo -->
      <Sun v-if="isSolar" :size="18" />
      <Eye v-else :size="18" />
    </button>

    <!-- Panel de ajustes -->
    <Transition name="a11y-panel">
      <div
        v-if="open"
        class="a11y-panel"
        id="a11y-panel"
        @click.stop
      >
        <p class="a11y-section-label">TAMAÑO DE TEXTO</p>
        <div class="a11y-font-row">
          <button
            v-for="s in fontSizes"
            :key="s.value"
            class="a11y-font-btn"
            :class="{ 'a11y-font-btn--active': prefs.fontSize === s.value }"
            @click="store.setFontSize(s.value)"
            :title="s.label"
            :id="`a11y-font-${s.value}`"
          >
            {{ s.icon }}
          </button>
        </div>

        <div class="a11y-divider" />

        <p class="a11y-section-label">CONTRASTE</p>
        <div class="a11y-contrast-row">
          <button
            v-for="c in contrastModes"
            :key="c.value"
            class="a11y-contrast-btn"
            :class="{ 'a11y-contrast-btn--active': prefs.contrast === c.value }"
            @click="store.setContrast(c.value)"
            :title="c.desc"
            :id="`a11y-contrast-${c.value}`"
          >
            <component :is="c.icon" :size="14" />
            <span>{{ c.label }}</span>
          </button>
        </div>

        <!-- Nota de modo solar -->
        <p v-if="isSolar" class="a11y-solar-note">
          ☀ Modo solar activo
        </p>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Sun, Eye, Moon, Contrast, SunMedium } from 'lucide-vue-next'
import { useAccessibilityStore } from '@/stores/accessibility'
import type { FontSize, Contrast as ContrastType } from '@/stores/accessibility'

const store = useAccessibilityStore()
const prefs = computed(() => store.prefs)
const open  = ref(false)

const isSolar = computed(() => prefs.value.contrast === 'solar')

// ── Opciones de fuente ────────────────────────────────────────────────────────
const fontSizes: { value: FontSize; label: string; icon: string }[] = [
  { value: 'sm', label: 'Texto pequeño',   icon: 'A'  },
  { value: 'md', label: 'Texto normal',    icon: 'A'  },
  { value: 'lg', label: 'Texto grande',    icon: 'A'  },
  { value: 'xl', label: 'Texto muy grande',icon: 'A'  },
]

// ── Opciones de contraste ─────────────────────────────────────────────────────
const contrastModes: { value: ContrastType; label: string; desc: string; icon: any }[] = [
  { value: 'normal', label: 'Normal', desc: 'Diseño estándar',           icon: Moon       },
  { value: 'alto',   label: 'Alto',   desc: 'Mayor brillo y contraste',  icon: Contrast   },
  { value: 'solar',  label: 'Solar',  desc: 'Fondo claro — para el sol', icon: SunMedium  },
]

// ── Cerrar panel al hacer clic afuera ─────────────────────────────────────────
function onDocClick() {
  open.value = false
}
onMounted(()  => document.addEventListener('click', onDocClick))
onUnmounted(() => document.removeEventListener('click', onDocClick))
</script>

<style scoped>
/* ── Contenedor flotante ──────────────────────────────────────────────────── */
.a11y-widget {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 500;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

/* ── Botón disparador ────────────────────────────────────────────────────── */
.a11y-toggle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1.5px solid var(--color-border-focus);
  background: var(--color-bg-card);
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}

.a11y-toggle:hover,
.a11y-toggle--active {
  color: var(--color-gold);
  border-color: var(--color-gold);
  background: var(--color-bg-card);
  box-shadow: 0 0 0 3px var(--color-gold-bg), 0 2px 12px rgba(0,0,0,0.4);
}

/* Modo solar: el botón también cambia */
.a11y-widget--solar .a11y-toggle {
  border-color: #8a6820;
  background: #e8e0c8;
  color: #5a3800;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.a11y-widget--solar .a11y-toggle:hover,
.a11y-widget--solar .a11y-toggle--active {
  border-color: #6a4800;
  color: #3a2400;
  box-shadow: 0 0 0 3px rgba(106,72,0,0.15), 0 2px 10px rgba(0,0,0,0.2);
}

/* ── Panel de ajustes ────────────────────────────────────────────────────── */
.a11y-panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-focus);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  min-width: 200px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.45);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.a11y-section-label {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  letter-spacing: 0.18em;
  color: var(--color-text-faint);
  margin: 0;
}

.a11y-divider {
  height: 1px;
  background: var(--color-border);
  margin: 0.1rem 0;
}

/* ── Fila de fuentes ─────────────────────────────────────────────────────── */
.a11y-font-row {
  display: flex;
  gap: 0.35rem;
}

.a11y-font-btn {
  flex: 1;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0.3rem 0;
  font-family: var(--font-mono);
  transition: all 0.15s;
  /* Tamaño de fuente escalonado para que cada botón sea visualmente diferente */
  line-height: 1;
}

.a11y-font-btn:nth-child(1) { font-size: 0.65rem; }
.a11y-font-btn:nth-child(2) { font-size: 0.8rem;  }
.a11y-font-btn:nth-child(3) { font-size: 0.95rem; }
.a11y-font-btn:nth-child(4) { font-size: 1.1rem;  }

.a11y-font-btn:hover {
  border-color: var(--color-border-focus);
  color: var(--color-text);
}

.a11y-font-btn--active {
  border-color: var(--color-gold) !important;
  color: var(--color-gold) !important;
  background: var(--color-gold-bg) !important;
}

/* ── Fila de contrastes ──────────────────────────────────────────────────── */
.a11y-contrast-row {
  display: flex;
  gap: 0.35rem;
}

.a11y-contrast-btn {
  flex: 1;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0.4rem 0.3rem;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  letter-spacing: 0.05em;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.15s;
}

.a11y-contrast-btn:hover {
  border-color: var(--color-border-focus);
  color: var(--color-text);
}

.a11y-contrast-btn--active {
  border-color: var(--color-gold) !important;
  color: var(--color-gold) !important;
  background: var(--color-gold-bg) !important;
}

/* Solar active — acento diferente */
.a11y-contrast-btn[id="a11y-contrast-solar"].a11y-contrast-btn--active {
  border-color: #cf8020 !important;
  color: #cf8020 !important;
  background: rgba(207,128,32,0.12) !important;
}

/* Nota modo solar */
.a11y-solar-note {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: #b07020;
  letter-spacing: 0.08em;
  margin: 0;
  text-align: center;
  padding-top: 0.1rem;
}

/* ── Transición del panel ────────────────────────────────────────────────── */
.a11y-panel-enter-active,
.a11y-panel-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.a11y-panel-enter-from,
.a11y-panel-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.97);
}
</style>
