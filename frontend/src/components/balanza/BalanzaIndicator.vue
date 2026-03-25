<template>
    <div class="balanza-indicator" :class="indicatorClass">
      <!-- Estado de conexión -->
      <div class="balanza-status">
        <span class="balanza-dot" :class="dotClass" />
        <span class="balanza-status-text">{{ statusText }}</span>
        <span v-if="config" class="balanza-port">{{ config.puerto }}</span>
      </div>

      <!-- Lectura de peso -->
      <div class="balanza-peso-wrapper">
        <span class="balanza-peso" :class="{ 'balanza-peso--inestable': !estable && conectado }">
          {{ wsConectado && conectado ? pesoDisplay : '—' }}
        </span>
        <span class="balanza-unidad">{{ unidad }}</span>
      </div>

      <!-- Badge de estabilidad -->
      <div v-if="wsConectado && conectado" class="balanza-estabilidad">
        <span v-if="estable" class="badge badge--ok">Estable</span>
        <span v-else class="badge badge--warn">En movimiento</span>
      </div>

      <!-- Error detalle -->
      <p v-if="error && !wsConectado" class="balanza-error-msg">
        Agente no disponible — verificar que script esté corriendo
      </p>
      <p v-else-if="error" class="balanza-error-msg">
        {{ error }}
      </p>
    </div>
  </template>

  <script setup lang="ts">
  import { computed } from 'vue'
  import type { BalanzaConfig } from '@/composables/useBalanza'

  interface Props {
    pesoDisplay: string
    unidad: string
    estable: boolean
    conectado: boolean
    wsConectado: boolean
    error: string | null
    config: BalanzaConfig | null
  }

  const props = defineProps<Props>()

  const indicatorClass = computed(() => ({
    'balanza-indicator--ok':    props.wsConectado && props.conectado,
    'balanza-indicator--warn':  props.wsConectado && !props.conectado,
    'balanza-indicator--off':   !props.wsConectado,
  }))

  const dotClass = computed(() => ({
    'dot--green':  props.wsConectado && props.conectado,
    'dot--yellow': props.wsConectado && !props.conectado,
    'dot--gray':   !props.wsConectado,
  }))

  const statusText = computed(() => {
    if (!props.wsConectado) return 'Agente sin conexión'
    if (!props.conectado)   return 'Puerto serial sin respuesta'
    return 'Balanza conectada'
  })
  </script>

  <style scoped>
  .balanza-indicator {
  display: flex; flex-direction: column; gap: 6px;
  padding: 14px 18px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-card); /* Ajustado */
  min-width: 200px;
}

.balanza-indicator--ok   { border-color: var(--color-success); }
.balanza-indicator--warn { border-color: var(--color-warning); }
.balanza-indicator--off  { border-color: var(--color-border);  background: var(--color-bg-input); }

/* Status row */
.balanza-status {
  display: flex; align-items: center; gap: 8px;
  font-size: var(--text-xs); /* Ajustado */
  color: var(--color-text-muted);
}

.balanza-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.dot--green  { background: var(--color-success); box-shadow: 0 0 0 3px rgba(81, 161, 85, 0.3); } /* Ajustado */
.dot--yellow { background: var(--color-warning); box-shadow: 0 0 0 3px rgba(207, 151, 61, 0.3); } /* Ajustado */
.dot--gray   { background: var(--color-text-muted); }

.balanza-port {
  margin-left: auto;
  font-family: var(--font-mono);
  font-size: var(--text-xs); /* Ajustado */
  opacity: 0.7;
}

/* Peso */
.balanza-peso-wrapper { display: flex; align-items: baseline; gap: 6px; }

.balanza-peso {
  font-size: var(--text-xxl); /* Ajustado */
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--color-text); /* Ajustado */
  letter-spacing: -0.5px;
  transition: color 0.2s;
}
.balanza-peso--inestable { color: var(--color-warning); }

.balanza-unidad {
  font-size: var(--text-base); /* Ajustado */
  font-weight: 500;
  color: var(--color-text-muted);
}

/* Badges */
.badge {
  display: inline-block; padding: 2px 10px;
  border-radius: 100px; font-size: var(--text-xs); font-weight: 500;
}
.badge--ok   { background: var(--color-success-bg); color: var(--color-success); } /* Ajustado */
.badge--warn { background: rgba(207, 151, 61, 0.15); color: var(--color-warning); } /* Ajustado */

/* Error */
.balanza-error-msg { font-size: var(--text-xs); color: var(--color-error); margin: 0; }
  </style>
