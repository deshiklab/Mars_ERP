<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <header class="flex items-center justify-between border-b border-slate-800 px-6 py-4">
      <div class="flex items-center gap-3">
        <span class="text-2xl">🏗️</span>
        <div>
          <h1 class="text-lg font-bold leading-tight">MARS Constech</h1>
          <p class="text-xs text-slate-400">REM ERP — Vue 3 PWA</p>
        </div>
      </div>
      <nav class="flex items-center gap-4 text-sm">
        <RouterLink to="/" class="text-slate-300 hover:text-white">Home</RouterLink>
        <RouterLink to="/about" class="text-slate-300 hover:text-white">About</RouterLink>
      </nav>
    </header>

    <main class="mx-auto max-w-5xl px-6 py-10">
      <RouterView />
    </main>
  </div>
</template>
