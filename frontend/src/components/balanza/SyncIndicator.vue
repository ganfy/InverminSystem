<template>
    <div class="sync-indicator" :class="rootClass" :title="tooltip">
      <!-- Dot de estado -->
      <span class="sync-dot" :class="dotClass"></span>

      <!-- Texto principal -->
      <span class="sync-label">{{ labelText }}</span>

      <!-- Badge de pendientes -->
      <span v-if="pendientes > 0" class="sync-badge">
        {{ pendientes }}
      </span>

      <!-- Spinner cuando sincroniza -->
      <span v-if="sincronizando" class="sync-spinner"></span>

      <!-- Botón manual de sync (solo si hay pendientes y hay red) -->
      <button
        v-if="pendientes > 0 && online && !sincronizando"
        class="sync-btn-manual"
        title="Sincronizar ahora"
        @click.stop="$emit('sync')"
      ><RefreshCw :size="12" /></button>
    </div>
  </template>

  <script setup lang="ts">
  import { computed } from 'vue'
  import { AlertTriangle, RefreshCw } from 'lucide-vue-next'

  interface Props {
    online: boolean
    sincronizando: boolean
    pendientes: number
    ipsRestantes: number
    ultimoSync: string | null
    errorSync: string | null
    mostrarIps?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    mostrarIps: false
  })
  defineEmits<{ sync: [] }>()

  const rootClass = computed(() => ({
    'sync--online':       props.online && props.pendientes === 0,
    'sync--pendiente':    props.online && props.pendientes > 0,
    'sync--offline':      !props.online,
    'sync--error':        !!props.errorSync,
    'sync--sincronizando': props.sincronizando,
    'sync--warning':      !props.online && props.mostrarIps && props.ipsRestantes > 0 && props.ipsRestantes <= 10,
  }))

  const dotClass = computed(() => ({
    'dot--green':  props.online && props.pendientes === 0 && !props.errorSync,
    'dot--amber': (props.online && props.pendientes > 0) ||
            (!props.online && props.mostrarIps && props.ipsRestantes <= 10 && props.ipsRestantes > 0),
    'dot--red':   !props.online && (!props.mostrarIps || props.ipsRestantes === 0 || !!props.errorSync),
    'dot--pulse':  props.sincronizando,
  }))

  const labelText = computed(() => {
    if (props.sincronizando) return 'Sincronizando…'
    if (!props.online) {
      if (props.mostrarIps) {
        if (props.ipsRestantes === 0)  return 'Sin IPs — reconectar'
        if (props.ipsRestantes <= 10)  return `Solo ${props.ipsRestantes} IPs disp.`
        return `Offline · ${props.ipsRestantes} IPs disp.`
      }
      return 'Offline'
    }
    if (props.pendientes > 0) return `${props.pendientes} pendiente${props.pendientes > 1 ? 's' : ''}`
      return 'En línea'
  })

  const tooltip = computed(() => {
    const lines: string[] = []
    if (!props.online)      lines.push('Sin conexión a internet')
    if (props.pendientes)   lines.push(`${props.pendientes} sesión(es) sin sincronizar`)
    if (props.errorSync)    lines.push(`Error: ${props.errorSync}`)
    if (props.ultimoSync)   lines.push(`Último sync: ${props.ultimoSync}`)
    if (props.ipsRestantes && props.mostrarIps) lines.push(`IPs disponibles offline: ${props.ipsRestantes}`)
    return lines.join('\n') || 'Sistema sincronizado'
  })
  </script>

  <style scoped>
  .sync-indicator {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 100px;
    font-family: var(--font-mono);
    font-size: 11px;
    border: 1px solid transparent;
    cursor: default;
    user-select: none;
    transition: background .2s, border-color .2s;
  }

  /* Estados */
  .sync--online     { background: rgba(60,180,80,.1);  border-color: rgba(60,180,80,.3);  color: #4ecf7a; }
  .sync--pendiente  { background: rgba(220,160,20,.1); border-color: rgba(220,160,20,.3); color: var(--color-warning); }
  .sync--offline    { background: rgba(220,60,60,.1);  border-color: rgba(220,60,60,.3);  color: var(--color-error); }
  .sync--error      { background: rgba(220,60,60,.15); border-color: rgba(220,60,60,.4);  color: var(--color-error); }
  .sync--warning { background: rgba(220,160,20,.1); border-color: rgba(220,160,20,.3); color: var(--color-warning); }

  /* Dot */
/* Dot */
.sync-dot {
  display: block; /* Obliga al navegador a darle volumen */
  width: 8px; /* Un pelín más grande para que destaque */
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot--green { background-color: #4ecf7a !important; }
.dot--amber { background-color: var(--color-warning, #dca014) !important; }
.dot--red   { background-color: var(--color-error, #dc3c3c) !important; }

  @keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: .3; }
  }
  .dot--pulse { animation: pulse-dot .8s ease-in-out infinite; }

  /* Badge de pendientes */
  .sync-badge {
    background: var(--color-warning);
    color: #000;
    font-size: 10px;
    font-weight: 600;
    padding: 0 5px;
    border-radius: 100px;
    min-width: 16px;
    text-align: center;
  }

  /* Spinner inline */
  @keyframes spin { to { transform: rotate(360deg); } }
  .sync-spinner {
    display: inline-block;
    width: 10px;
    height: 10px;
    border: 1.5px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin .6s linear infinite;
  }

  /* Botón manual */
  .sync-btn-manual {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    font-size: 12px;
    padding: 0 2px;
    opacity: .8;
    transition: opacity .15s;
  }
  .sync-btn-manual:hover { opacity: 1; }
  </style>
