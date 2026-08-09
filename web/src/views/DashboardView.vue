<script setup lang="ts">
import { onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'

const data = useDataStore()
const auth = useAuthStore()

onMounted(() => {
  data.loadDashboard()
})

const cards = [
  { label: 'Bookings', key: 'bookings' as const, icon: '📋', color: 'text-emerald-400' },
  { label: 'Leads', key: 'leads' as const, icon: '🎯', color: 'text-sky-400' },
  { label: 'Employees', key: 'employees' as const, icon: '👥', color: 'text-violet-400' },
  { label: 'Dues', key: 'dues' as const, icon: '💰', color: 'text-amber-400' }
]
</script>

<template>
  <section>
    <h2 class="text-2xl font-bold">Dashboard</h2>
    <p v-if="data.stats" class="mt-1 text-xs text-slate-400">
      Server: {{ data.stats.serverTime }} · PWA v{{ data.stats.pwaVersion }}
    </p>
    <p v-else-if="data.error" class="mt-2 text-xs text-rose-400">{{ data.error }}</p>

    <div class="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
      <div
        v-for="c in cards"
        :key="c.key"
        class="rounded-xl border border-slate-800 bg-slate-900/60 p-5"
      >
        <div class="flex items-center justify-between">
          <span class="text-2xl">{{ c.icon }}</span>
          <span class="text-[10px] uppercase tracking-wide text-slate-500">{{ c.label }}</span>
        </div>
        <p class="mt-3 text-3xl font-bold" :class="c.color">
          {{ data.stats ? data.stats[c.key] : '—' }}
        </p>
      </div>
    </div>

    <div class="mt-8 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
      <p class="text-sm font-semibold">Signed in as</p>
      <p class="mt-2 text-sm text-slate-300">
        <span class="mr-2 inline-block h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
        {{ auth.fullName || auth.user }} · {{ auth.pwaRole }}
      </p>
    </div>
  </section>
</template>
