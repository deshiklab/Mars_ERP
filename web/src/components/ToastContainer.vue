<script setup lang="ts">
/**
 * ToastContainer — renders global toasts (top-right, slide-in).
 */
import { toastState } from '@/toast'

function bg(t: string): string {
  return t === 'success' ? '#2e7d32' : t === 'error' ? '#c62828' : '#2f80ed'
}
</script>

<template>
  <div style="position: fixed; top: 56px; right: 16px; z-index: 10000; display: flex; flex-direction: column; gap: 8px; pointer-events: none">
    <div
      v-for="t in toastState.toasts"
      :key="t.id"
      :style="{
        pointerEvents: 'auto',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: '#fff',
        border: '1px solid #e0e0e0',
        borderLeft: '4px solid ' + bg(t.type),
        borderRadius: '8px',
        boxShadow: '0 6px 20px rgba(0,0,0,0.15)',
        padding: '9px 14px',
        fontSize: '11px',
        color: '#333',
        minWidth: '220px',
        maxWidth: '360px',
        animation: 'toastIn 0.18s ease-out'
      }"
    >
      <span style="font-size: 14px">{{ t.type === 'success' ? '✅' : t.type === 'error' ? '⚠️' : 'ℹ️' }}</span>
      <span style="flex: 1">{{ t.msg }}</span>
    </div>
  </div>
</template>

<style scoped>
@keyframes toastIn {
  from { opacity: 0; transform: translateX(24px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
