<template>
    <div class="lote-card" :class="{ 'lote-en-proceso': !lote.pesaje?.peso_final }">
      <div class="lote-card-header">
        <span class="lote-ip">{{ lote.ip }} | Lote {{ lote.numero_lote }}</span>
        <div class="lote-acciones">
          <button
            v-if="isAdmin || lote.id === -1"
            class="btn-icon btn-secondary"
            title="Editar lote"
            :disabled="!isOnline && lote.id !== -1"
            @click="$emit('editar', lote)"
          ><Pencil :size="14" /></button>
          <button
            v-if="isAdmin || lote.id === -1"
            class="btn-icon btn-icon-danger btn-secondary"
            title="Eliminar lote"
            :disabled="!isOnline && lote.id !== -1"
            @click="$emit('eliminar', lote)"
          ><Trash :size="14" /></button>

          <span v-if="lote.local_only" class="badge-local-lote" title="Pendiente de sincronizar"><WifiOff :size="12" style="margin-right: 4px;" /> LOCAL</span>
          <span class="badge-lote-estado" :class="loteEstadoClass(lote)">{{ loteEstadoLabel(lote) }}</span>
        </div>
      </div>
      <div class="lote-card-body">
        <div class="lote-fila">
          <span class="lote-dato-label">BRUTO:</span>
          <span class="lote-dato-val">{{ lote.pesaje?.peso_inicial != null ? formatPesoPorModulo(lote.pesaje.peso_inicial, 'BALANZA', 3) : '…' }}</span>
        </div>
        <div class="lote-fila">
          <span class="lote-dato-label">TARA:</span>
          <span class="lote-dato-val">{{ lote.pesaje?.peso_final != null ? formatPesoPorModulo(lote.pesaje.peso_final, 'BALANZA', 3) : '…' }}</span>
        </div>
        <div class="lote-fila lote-neto">
          <span class="lote-dato-label">NETO:</span>
          <span class="lote-dato-val neto-val">{{ lote.peso_neto != null ? formatPesoPorModulo(lote.peso_neto, 'BALANZA', 3) : '…' }}</span>
        </div>
        <div v-if="lote.pesaje?.sacos" class="lote-fila">
          <span class="lote-dato-label">SACOS:</span>
          <span class="lote-dato-val">{{ lote.pesaje.sacos }}</span>
        </div>
        <div v-if="lote.pesaje?.granel" class="lote-fila">
          <span class="badge-propio">Granel</span>
        </div>
      </div>
      <div class="lote-card-footer">
        <button class="btn-secondary btn-sm" @click="$emit('verTicket', lote)" title="Ver ticket antes de imprimir"><Eye :size="14" style="margin-right: 4px;" /> Ver ticket</button>
        <button class="btn-secondary btn-sm" @click="$emit('imprimirTicket', lote)" title="Imprimir ticket"><Printer :size="14" style="margin-right: 4px;" /> Imprimir</button>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import type { LoteDetalle } from '@/api/balanza'
  import { formatPesoPorModulo, getUnidadPorModulo } from '@/utils/units'
  import { Pencil, Trash2, WifiOff, Eye, Printer, Trash } from 'lucide-vue-next'

  defineProps<{
    lote: LoteDetalle
    isAdmin: boolean
    isOnline: boolean
  }>()

  defineEmits(['editar', 'eliminar', 'verTicket', 'imprimirTicket'])

  function loteEstadoClass(lote: LoteDetalle) { return lote.pesaje?.peso_final != null ? 'lc-completado' : 'lc-en-proceso' }
  function loteEstadoLabel(lote: LoteDetalle) { return lote.pesaje?.peso_final != null ? 'Completado' : 'En proceso' }
  </script>

  <style scoped>
  /* ── Lotes ───────────────────────────────────────────────── */
.lote-card {
  background: var(--color-bg-card); border: 1px solid var(--color-border);
  border-radius: var(--radius-md); margin-bottom: .75rem; overflow: hidden;
}
.lote-en-proceso { border-color: rgba(220,160,20,.5); }
.lote-eliminado  { opacity: .45; }

/* Ajuste al header para que no se rompa si no hay espacio */
.lote-card-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 0.5rem;
  padding: .6rem 1rem; background: rgba(184,150,46,.06);
  border-bottom: 1px solid var(--color-border);
}

.lote-ip { font-family: var(--font-mono); font-size: .82rem; color: var(--color-gold); }

/* Ajuste al contenedor de acciones para que fluya bien */
.lote-acciones { display: flex; align-items: center; flex-wrap: wrap; gap: .4rem; }

/* NUEVO: Estilos específicos para los botones de ícono */
.btn-icon {
  display: inline-flex !important; align-items: center !important; justify-content: center !important;
  width: 26px !important; height: 26px !important; padding: 0 !important;
  font-size: 0.85rem !important; border-radius: 4px !important;
}
.btn-icon-danger:enabled:hover { color: var(--color-error) !important; border-color: var(--color-error) !important; }

.badge-lote-estado {
  font-family: var(--font-mono); font-size: .68rem; letter-spacing: .1em;
  padding: .2rem .5rem; border-radius: var(--radius-sm); white-space: nowrap;
}
.lc-completado { background: rgba(60,180,80,.15); color: #4ecf7a; border: 1px solid #4ecf7a; }
.lc-en-proceso { background: rgba(220,160,20,.12); color: var(--color-warning); border: 1px solid var(--color-warning); }
.badge-eliminado { background: rgba(220,60,60,.1); color: var(--color-error); border: 1px solid var(--color-error); }
.lote-card-body {
  padding: .75rem 1rem; display: grid;
  grid-template-columns: 1fr 1fr; gap: .3rem .75rem;
}
.lote-fila { display: flex; gap: .4rem; align-items: baseline; }
.lote-neto { grid-column: 1 / -1; margin-top: .2rem; }
.lote-dato-label { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text-muted); min-width: 45px; }
.lote-dato-val   { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--color-text); }
.neto-val        { font-size: var(--text-lg); color: var(--color-gold-light); font-weight: 600; }
.badge-propio    { font-size: var(--text-xs); padding: .15rem .4rem; background: var(--color-gold-bg); border-radius: 3px; color: var(--color-gold); }
.lote-card-footer {
  padding: .5rem 1rem; border-top: 1px solid var(--color-border);
  display: flex; justify-content: flex-end; gap: .5rem;
}
.badge-local-lote {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  letter-spacing: .1em;
  background: var(--color-offline-bg);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 3px;
  padding: 1px 5px;
}
.btn-sm { padding: .3rem .7rem; font-size: var(--text-xs); }
.lotes-eliminados { margin-top: .5rem; font-size: var(--text-md); color: var(--color-text-muted); }
.lotes-eliminados summary { cursor: pointer; padding: .3rem 0; }
</style>
