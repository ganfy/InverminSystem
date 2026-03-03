import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id:      number
  message: string
  type:    ToastType
}

export interface ConfirmOptions {
  title:         string
  message:       string
  confirmLabel?: string
  danger?:       boolean
}

export const useUiStore = defineStore('ui', () => {
  // ── Toasts ────────────────────────────────────────────────
  const toasts = ref<Toast[]>([])
  let nextId = 0

  function toast(message: string, type: ToastType = 'info') {
    const id = ++nextId
    toasts.value.push({ id, message, type })
    setTimeout(() => removeToast(id), 3500)
  }

  function removeToast(id: number) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  // ── Confirm ───────────────────────────────────────────────
  const confirm = ref<ConfirmOptions | null>(null)
  let resolveFn: ((value: boolean) => void) | null = null

  function showConfirm(opts: ConfirmOptions): Promise<boolean> {
    confirm.value = opts
    return new Promise(resolve => {
      resolveFn = resolve
    })
  }

  function resolveConfirm(value: boolean) {
    confirm.value = null
    resolveFn?.(value)
    resolveFn = null
  }

  return {
    toasts, toast, removeToast,
    confirm, showConfirm, resolveConfirm,
  }
})
