<script setup lang="ts">
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function signOut() {
  await auth.signOut()
  router.push('/login')
}

function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || 'U'
}

function toggleFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    document.documentElement.requestFullscreen()
  }
}

/** Groups mirroring the HTML PWA sidebar (id, label, icon, module, path). */
const groups = [
  { id: 'executive', label: 'Executive', icon: '📊', module: 'dashboard', path: '/' },
  { id: 'sales_crm', label: 'Sales & CRM', icon: '🎯', module: 'crm', path: '/leads' },
  { id: 'land_projects', label: 'Projects', icon: '🏗️', module: 'projects', path: '/projects' },
  { id: 'construction', label: 'Engineering & Construction', icon: '🔧', module: 'dashboard' },
  { id: 'finance_admin', label: 'Accounts & Finance', icon: '💰', module: 'dues', path: '/dues' },
  { id: 'hr_admin', label: 'Admin & Operations', icon: '💼', module: 'hr', path: '/hr' },
  { id: 'collaboration', label: 'Collaboration', icon: '🤝', module: 'dashboard' }
]

function visibleGroups() {
  return groups.filter((g) => auth.canAccess(g.module))
}

function isActive(g: { path?: string; module: string }): boolean {
  if (g.path) return route.path === g.path
  return false
}

function gotoGroup(g: { path?: string; module: string }) {
  router.push(g.path ?? '/')
}
</script>

<template>
  <div class="app-shell">
    <!-- SIDEBAR: 72px, mirrors the HTML PWA -->
    <aside class="rem-sidebar">
      <div class="rem-sidebar-logo" @click="router.push('/')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
        </svg>
        <div class="rem-sidebar-brand">REM ERP</div>
      </div>
      <div class="rem-sidebar-scroll">
        <template v-for="(g, i) in visibleGroups()" :key="g.id">
          <div v-if="i > 0" class="rem-sidebar-sep"></div>
          <button
            class="rem-sidebar-item"
            :class="{ active: isActive(g) }"
            :title="g.label"
            @click="gotoGroup(g)"
          >
            {{ g.icon }}
          </button>
          <div class="rem-sidebar-label">{{ g.label.split(' & ')[0] }}</div>
        </template>
      </div>
    </aside>

    <!-- MAIN COLUMN -->
    <div style="display: flex; flex-direction: column; flex: 1; min-width: 0">
      <!-- TOP BAR -->
      <header class="rem-topbar">
        <span class="rem-topbar-title">🏗️ MARS Constech</span>
        <div style="font-size: 10px; color: #888">{{ route.meta.title ?? '' }}</div>
        <div class="rem-topbar-actions">
          <button class="rem-icon-btn" title="Notifications">🔕</button>
          <button class="rem-icon-btn" title="Fullscreen" @click="toggleFullscreen">⛶</button>
          <div class="rem-user-chip" title="User Profile" @click="router.push('/login')">
            <span class="chip-avatar">{{ initials(auth.fullName || auth.user) }}</span>
            <span>{{ auth.fullName || auth.user }}</span>
          </div>
          <button class="action-btn" @click="signOut">⎋ Sign Out</button>
        </div>
      </header>

      <!-- CONTENT -->
      <main class="rem-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>
