<script setup lang="ts">
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

onMounted(() => {
  // a 401 mid-session should drop us back to the login gate
  // (wired in main.ts via api.setOnUnauthorized)
})

async function signOut() {
  await auth.signOut()
  router.push('/login')
}

const nav = [
  { to: '/', label: 'Dashboard', icon: '📊', module: 'dashboard' },
  { to: '/leads', label: 'CRM & Leads', icon: '🎯', module: 'crm' }
]
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <header class="flex items-center justify-between border-b border-slate-800 px-6 py-4">
      <RouterLink to="/" class="flex items-center gap-3">
        <span class="text-2xl">🏗️</span>
        <div>
          <h1 class="text-lg font-bold leading-tight">MARS Constech</h1>
          <p class="text-xs text-slate-400">REM ERP — Vue 3 PWA</p>
        </div>
      </RouterLink>
      <div class="flex items-center gap-4 text-sm">
        <nav v-if="auth.authenticated" class="flex items-center gap-1">
          <RouterLink
            v-for="n in nav.filter((x) => auth.canAccess(x.module))"
            :key="n.to"
            :to="n.to"
            class="rounded-lg px-3 py-1.5 text-xs"
            :class="route.path === n.to ? 'bg-slate-800 text-white' : 'text-slate-300 hover:text-white'"
          >
            {{ n.icon }} {{ n.label }}
          </RouterLink>
        </nav>
        <div v-if="auth.authenticated" class="flex items-center gap-3 border-l border-slate-800 pl-4">
          <div class="text-right">
            <p class="text-xs font-semibold text-slate-200">{{ auth.fullName || auth.user }}</p>
            <p class="text-[10px] text-slate-500">{{ auth.pwaRole }}</p>
          </div>
          <button
            class="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800"
            @click="signOut"
          >
            ⎋ Sign Out
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-6 py-10">
      <RouterView />
    </main>
  </div>
</template>
