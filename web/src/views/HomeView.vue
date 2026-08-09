<script setup lang="ts">
import { ref } from 'vue'

const online = ref(navigator.onLine)

window.addEventListener('online', () => (online.value = true))
window.addEventListener('offline', () => (online.value = false))
</script>

<template>
  <section>
    <h2 class="text-2xl font-bold">REM ERP — Vue 3 PWA</h2>
    <p class="mt-3 max-w-2xl text-sm leading-relaxed text-slate-300">
      Modern frontend for the MARS Constech ERP, built with Vue&nbsp;3,
      TypeScript, Tailwind&nbsp;CSS&nbsp;v4 and Vite, installable as a
      Progressive Web App with offline-first data sync.
    </p>

    <div class="mt-6 flex flex-wrap gap-3 text-xs">
      <span class="rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1">⚡ Vite</span>
      <span class="rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1">🟦 TypeScript</span>
      <span class="rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1">🎨 Tailwind v4</span>
      <span class="rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1">🔷 Vue 3</span>
      <span class="rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1">📱 PWA</span>
    </div>

    <div class="mt-8 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
      <p class="text-sm font-semibold">Connection status</p>
      <p class="mt-2 text-sm">
        <span
          class="mr-2 inline-block h-2.5 w-2.5 rounded-full"
          :class="online ? 'bg-emerald-400' : 'bg-rose-400'"
        ></span>
        {{ online ? 'Online — API sync uses NetworkFirst' : 'Offline — serving from cache (StaleWhileRevalidate)' }}
      </p>
    </div>
  </section>
</template>
