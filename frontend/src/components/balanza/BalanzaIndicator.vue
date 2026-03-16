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
        Agente no disponible — verificar que balanza_agent.py está corriendo
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
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 14px 18px;
    border-radius: 10px;
    border: 1.5px solid var(--color-border);
    background: var(--color-surface);
    min-width: 200px;
  }

  .balanza-indicator--ok   { border-color: var(--color-success); background: var(--color-success-bg); }
  .balanza-indicator--warn { border-color: var(--color-warning); background: var(--color-warning-bg); }
  .balanza-indicator--off  { border-color: var(--color-border);  background: var(--color-surface-muted); }

  /* Status row */
  .balanza-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--color-text-muted);
  }

  .balanza-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .dot--green  { background: var(--color-success); box-shadow: 0 0 0 3px var(--color-success-light); }
  .dot--yellow { background: var(--color-warning); box-shadow: 0 0 0 3px var(--color-warning-light); }
  .dot--gray   { background: var(--color-text-muted); }

  .balanza-port {
    margin-left: auto;
    font-family: var(--font-mono);
    font-size: 11px;
    opacity: 0.7;
  }

  /* Peso */
  .balanza-peso-wrapper {
    display: flex;
    align-items: baseline;
    gap: 6px;
  }

  .balanza-peso {
    font-size: 32px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    color: var(--color-text-primary);
    letter-spacing: -0.5px;
    transition: color 0.2s;
  }

  .balanza-peso--inestable {
    color: var(--color-warning-text);
  }

  .balanza-unidad {
    font-size: 16px;
    font-weight: 500;
    color: var(--color-text-muted);
  }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 500;
  }
  .badge--ok   { background: var(--color-success-light); color: var(--color-success-dark); }
  .badge--warn { background: var(--color-warning-light); color: var(--color-warning-dark); }

  /* Error */
  .balanza-error-msg {
    font-size: 11px;
    color: var(--color-danger-text);
    margin: 0;
  }
  </style>
