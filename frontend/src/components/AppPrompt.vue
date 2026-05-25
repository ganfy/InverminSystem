<template>
    <Teleport to="body">
      <Transition name="confirm">
        <div v-if="ui.prompt" class="modal-overlay" @click.self="cancel">
          <div class="modal modal-sm confirm-modal">
            <div class="modal-header">
              <h2>{{ ui.prompt.title }}</h2>
            </div>
            <div class="modal-body">
              <p class="prompt-msg">{{ ui.prompt.message }}</p>
              <input
                ref="inputRef"
                v-model="inputValue"
                :type="ui.prompt.inputType ?? 'text'"
                :placeholder="ui.prompt.placeholder ?? ''"
                class="field-input prompt-input"
                @keydown.enter="confirm"
                @keydown.esc="cancel"
              />
            </div>
            <div class="modal-footer">
              <button class="btn-secondary" @click="cancel">Cancelar</button>
              <button
                class="btn-confirm"
                :disabled="!inputValue.trim()"
                @click="confirm"
              >
                {{ ui.prompt.confirmLabel ?? 'Confirmar' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const inputValue = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

watch(
() => ui.prompt,
async (val) => {
    if (val) {
    inputValue.value = ''
    await nextTick()
    inputRef.value?.focus()
    }
},
)

function confirm() {
if (!inputValue.value.trim()) return
ui.resolvePrompt(inputValue.value)
inputValue.value = ''
}

function cancel() {
ui.resolvePrompt(null)
inputValue.value = ''
}
</script>

<style scoped>
.prompt-msg {
color: var(--color-text-muted);
font-family: var(--font-mono);
font-size: var(--text-base);
line-height: 1.5;
margin: 0 0 0.75rem;
}

.prompt-input {
width: 100%;
margin-top: 0.25rem;
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
.btn-confirm:hover:not(:disabled) { background: var(--color-gold-light); }
.btn-confirm:disabled              { opacity: 0.45; cursor: not-allowed; }

.confirm-enter-active,
.confirm-leave-active { transition: opacity 0.2s ease; }
.confirm-enter-from,
.confirm-leave-to     { opacity: 0; }
</style>
