/**
 * Toast — global toast notifications mirroring the HTML PWA showToast.
 * Usage: import { toast } from '@/toast'; toast.show('Saved', 'success')
 */
import { reactive } from 'vue'

export type ToastType = 'success' | 'error' | 'info'

interface ToastItem {
  id: number
  msg: string
  type: ToastType
}

export const toastState = reactive<{ toasts: ToastItem[] }>({ toasts: [] })

let nextId = 1

export function showToast(msg: string, type: ToastType = 'info', duration = 2600) {
  const id = nextId++
  toastState.toasts.push({ id, msg, type })
  setTimeout(() => {
    const i = toastState.toasts.findIndex((t) => t.id === id)
    if (i >= 0) toastState.toasts.splice(i, 1)
  }, duration)
}

export const toast = { show: showToast, success: (m: string) => showToast(m, 'success'), error: (m: string) => showToast(m, 'error'), info: (m: string) => showToast(m, 'info') }
