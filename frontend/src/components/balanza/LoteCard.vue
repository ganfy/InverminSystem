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
          >✎</button>
          <button
            v-if="isAdmin || lote.id === -1"
            class="btn-icon btn-icon-danger btn-secondary"
            title="Eliminar lote"
            :disabled="!isOnline && lote.id !== -1"
            @click="$emit('eliminar', lote)"
          >✕</button>

          <span v-if="lote.local_only" class="badge-local-lote" title="Pendiente de sincronizar">⚡ LOCAL</span>
          <span class="badge-lote-estado" :class="loteEstadoClass(lote)">{{ loteEstadoLabel(lote) }}</span>
        </div>
      </div>
      <div class="lote-card-body">
        <div class="lote-fila">
          <span class="lote-dato-label">BRUTO:</span>
          <span class="lote-dato-val">{{ lote.pesaje?.peso_inicial != null ? fmtTm(lote.pesaje.peso_inicial) + ' TM' : '…' }}</span>
        </div>
        <div class="lote-fila">
          <span class="lote-dato-label">TARA:</span>
          <span class="lote-dato-val">{{ lote.pesaje?.peso_final != null ? fmtTm(lote.pesaje.peso_final) + ' TM' : '…' }}</span>
        </div>
        <div class="lote-fila lote-neto">
          <span class="lote-dato-label">NETO:</span>
          <span class="lote-dato-val neto-val">{{ lote.peso_neto != null ? fmtTm(lote.peso_neto) + ' TM' : '…' }}</span>
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
        <button class="btn-secondary btn-sm" @click="$emit('verTicket', lote)" title="Ver ticket antes de imprimir">👁 Ver ticket</button>
        <button class="btn-secondary btn-sm" @click="$emit('imprimirTicket', lote)" title="Imprimir ticket">🖨 Imprimir</button>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import type { LoteDetalle } from '@/api/balanza'

  defineProps<{
    lote: LoteDetalle
    isAdmin: boolean
    isOnline: boolean
  }>()

  defineEmits(['editar', 'eliminar', 'verTicket', 'imprimirTicket'])

  function fmtTm(n: number | string) { return Number(n).toFixed(3) }
  function loteEstadoClass(lote: LoteDetalle) { return lote.pesaje?.peso_final != null ? 'lc-completado' : 'lc-en-proceso' }
  function loteEstadoLabel(lote: LoteDetalle) { return lote.pesaje?.peso_final != null ? 'Completado' : 'En proceso' }
  </script>
