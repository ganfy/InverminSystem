<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="t in ui.toasts"
          :key="t.id"
          class="toast"
          :class="t.type"
          @click="ui.removeToast(t.id)"
        >
          <span class="toast-icon">{{ icons[t.type] }}</span>
          <span class="toast-msg">{{ t.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()

const icons = {
  success: '✓',
  error:   '✕',
  warning: '⚠',
  info:    'ℹ',
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1.1rem;
  border-radius: 4px;
  border-left: 3px solid;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  min-width: 260px;
  max-width: 380px;
  cursor: pointer;
  pointer-events: all;
  backdrop-filter: blur(4px);
}

.toast.success {
  background: rgba(34, 197, 94, 0.12);
  border-color: #4ade80;
  color: #4ade80;
}
.toast.error {
  background: rgba(220, 38, 38, 0.12);
  border-color: #f87171;
  color: #f87171;
}
.toast.warning {
  background: rgba(234, 179, 8, 0.12);
  border-color: #fbbf24;
  color: #fbbf24;
}
.toast.info {
  background: rgba(14, 165, 233, 0.12);
  border-color: #38bdf8;
  color: #38bdf8;
}

.toast-icon { font-size: 0.9rem; flex-shrink: 0; }
.toast-msg  { line-height: 1.4; }

/* Transición */
.toast-enter-active { transition: all 0.25s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from   { opacity: 0; transform: translateX(40px); }
.toast-leave-to     { opacity: 0; transform: translateX(40px); }
</style>
