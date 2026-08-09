<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { GROUPS, groupForPath, moduleForPath } from '@/shell/groups'
import type { ShellGroup, ShellModule } from '@/shell/groups'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const activeGroupId = ref('executive')
const activeModuleId = ref('dashboard')

/* ── sidebar + top tabs (mirror switchGroup) ── */
const visibleGroups = computed(() => GROUPS.filter((g) => auth.canAccess(g.module)))

function visibleMods(g: ShellGroup): ShellModule[] {
  return g.mods.filter((m) => auth.canAccess(g.module))
}

function switchGroup(g: ShellGroup) {
  activeGroupId.value = g.id
  const mods = visibleMods(g)
  if (mods.length === 0) return
  const first = mods.find((m) => m.path) ?? mods[0]
  switchModule(first)
}

function switchModule(m: ShellModule) {
  activeModuleId.value = m.id
  if (m.path) router.push(m.path)
}

/* sync active group/module from the current route */
function syncFromRoute() {
  const g = groupForPath(route.path)
  if (g) {
    activeGroupId.value = g.id
    const m = moduleForPath(route.path)
    if (m) activeModuleId.value = m.id
  }
}
syncFromRoute()

const activeGroup = computed(() => GROUPS.find((g) => g.id === activeGroupId.value) ?? GROUPS[0])
const activeModule = computed(() => activeGroup.value.mods.find((m) => m.id === activeModuleId.value))
const topTabs = computed(() => visibleMods(activeGroup.value))

/* ── helpers ── */
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

async function signOut() {
  await auth.signOut()
  router.push('/login')
}

function exportCsv() {
  const blob = new Blob([['module,rows\nleads,0'].join('\n')], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'rem-erp-export.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}
</script>

<template>
  <div class="app-shell">
    <!-- ═══ SIDEBAR (mirrors the HTML PWA: SVG icons, separators) ═══ -->
    <aside class="rem-sidebar">
      <div class="rem-sidebar-logo" @click="router.push('/')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
        </svg>
        <div class="rem-sidebar-brand">REM ERP</div>
      </div>
      <div class="rem-sidebar-scroll">
        <template v-for="(g, i) in visibleGroups" :key="g.id">
          <div v-if="i > 0" class="rem-sidebar-sep"></div>
          <button
            class="rem-sidebar-item"
            :class="{ active: activeGroupId === g.id }"
            :title="g.label"
            @click="switchGroup(g)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 18px; height: 18px" v-html="g.svg"></svg>
          </button>
          <div class="rem-sidebar-label">{{ g.label.split(' & ')[0] }}</div>
        </template>
      </div>
    </aside>

    <!-- ═══ MAIN COLUMN ═══ -->
    <div style="display: flex; flex-direction: column; flex: 1; min-width: 0">
      <!-- TOP BAR: title + top tabs + actions -->
      <header class="rem-topbar" style="gap: 8px; padding: 0 10px">
        <span class="rem-topbar-title" style="font-size: 11px">🏗️ MARS Constech</span>

        <div class="top-nav" style="display: flex; align-items: center; gap: 2px; flex: 1; overflow-x: auto">
          <div
            v-for="m in topTabs"
            :key="m.id"
            class="top-nav-item"
            :class="{ active: activeModuleId === m.id }"
            @click="switchModule(m)"
          >
            {{ m.label }}
          </div>
        </div>

        <div class="top-actions" style="display: flex; align-items: center; gap: 2px; position: relative">
          <button class="rem-icon-btn" title="Keyboard Shortcuts">⌨</button>
          <button class="rem-icon-btn" title="Quick Add" style="font-weight: 700; font-size: 16px; color: #2f80ed">+</button>
          <button class="rem-icon-btn" title="Print Report">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 15px; height: 15px">
              <path d="M6 9V2h12v7" /><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" /><path d="M6 14h12v8H6z" />
            </svg>
          </button>
          <button class="rem-icon-btn" title="Export All as CSV" @click="exportCsv">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 15px; height: 15px">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </button>
          <button class="rem-icon-btn" title="Toggle Dark Mode">🌙</button>
          <button class="rem-icon-btn" title="Theme Palette">🎨</button>
          <button class="rem-icon-btn" title="Notifications" style="position: relative">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 15px; height: 15px">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
          </button>
          <button class="rem-icon-btn" title="More" style="font-weight: 700">⋯</button>
          <button class="rem-icon-btn" title="Sync all with server (Shift+click = force full refresh)" style="color: #2f80ed">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="width: 15px; height: 15px">
              <path d="M23 4v6h-6" /><path d="M1 20v-6h6" /><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
          </button>
          <button class="rem-icon-btn" title="Fullscreen" @click="toggleFullscreen">⛶</button>
          <div class="rem-user-chip" style="margin-left: 4px" title="User Profile" @click="router.push('/login')">
            <span class="chip-avatar">{{ initials(auth.fullName || auth.user) }}</span>
          </div>
        </div>
      </header>

      <!-- CONTENT -->
      <main class="rem-content" style="flex: 1; overflow-y: auto; padding: 12px 16px">
        <RouterView />
      </main>

      <!-- ═══ FOOTER: breadcrumb strip (REM ERP › Group › Module) ═══ -->
      <div
        class="app-footer"
        style="height: 28px; min-height: 28px; background: #fff; border-top: 1px solid #e8e8e8; display: flex; align-items: center; padding: 0 12px; font-size: 10px; color: #888; justify-content: space-between"
      >
        <div class="breadcrumb" style="display: flex; align-items: center; gap: 4px">
          <span class="crumb-part" style="cursor: pointer; color: #2f80ed; font-weight: 600" @click="router.push('/')">REM ERP</span>
          <span class="crumb-sep">›</span>
          <span class="crumb-part" style="cursor: pointer" @click="switchGroup(activeGroup)">{{ activeGroup.label }}</span>
          <span class="crumb-sep">›</span>
          <span class="crumb-part" style="cursor: pointer">{{ activeModule?.label ?? '' }}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px">
          <span style="cursor: pointer" title="Toggle Theme">🌙</span>
          <span style="color: #e0e0e0">|</span>
          <span
            id="footerRoleBtn"
            style="cursor: pointer; font-size: 10px; font-weight: 600; color: #2f80ed; padding: 1px 6px; border: 1px solid #d0d8e8; border-radius: 4px"
            title="User Profile"
            @click="router.push('/login')"
          >{{ initials(auth.fullName || auth.user) }}</span>
          <button class="action-btn" style="padding: 1px 8px; font-size: 9px" @click="signOut">⎋ Sign Out</button>
        </div>
      </div>
    </div>
  </div>
</template>
