<template>
  <Teleport to="body">
    <Transition name="confirm">
      <div v-if="ui.confirm" class="modal-overlay" @click.self="ui.resolveConfirm(false)">
        <div class="modal modal-sm confirm-modal">
          <div class="modal-header">
            <h2>{{ ui.confirm.title }}</h2>
          </div>
          <div class="modal-body">
            <p class="confirm-msg">{{ ui.confirm.message }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="ui.resolveConfirm(false)">
              Cancelar
            </button>
            <button
              class="btn-confirm"
              :class="{ danger: ui.confirm.danger }"
              @click="ui.resolveConfirm(true)"
            >
              {{ ui.confirm.confirmLabel ?? 'Confirmar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<style scoped>
.confirm-msg {
  color: var(--color-text-muted);
  font-family: var(--font-mono);
  font-size: var(--text-base);
  line-height: 1.5;
  margin: 0;
}

.btn-confirm {
  padding: 0.5rem 1.25rem;
  border-radius: 3px;
  border: none;
  font-family: var(--font-mono);
  font-size: var(--text-md);
  font-weight: 600;
  cursor: pointer;
  background: var(--color-gold);
  color: #1a1a14;
  transition: background 0.15s;
}
.btn-confirm:hover         { background: var(--color-gold-light); }
.btn-confirm.danger        { background: rgba(220,38,38,0.8); color: #fff; }
.btn-confirm.danger:hover  { background: rgba(220,38,38,1); }

.confirm-enter-active,
.confirm-leave-active { transition: opacity 0.2s ease; }
.confirm-enter-from,
.confirm-leave-to     { opacity: 0; }
</style>
