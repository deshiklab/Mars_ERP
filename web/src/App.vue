<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
import { GROUPS, groupForPath, moduleForPath } from '@/shell/groups'
import type { ShellGroup, ShellModule } from '@/shell/groups'
import { i18n, _t, theme } from '@/i18n'
import { api } from '@/api/client'
import { showToast } from '@/toast'
import NotificationsPanel from '@/components/NotificationsPanel.vue'
import RecentTray from '@/components/RecentTray.vue'
import CommandPalette from '@/components/CommandPalette.vue'
import ShortcutsModal from '@/components/ShortcutsModal.vue'
import ToastContainer from '@/components/ToastContainer.vue'
import ProfilePanel from '@/components/ProfilePanel.vue'
import GlobalSearch from '@/components/GlobalSearch.vue'
import QuickAdd from '@/components/QuickAdd.vue'
import SidebarFlyout from '@/components/SidebarFlyout.vue'

const auth = useAuthStore()
const data = useDataStore()
const router = useRouter()
const route = useRoute()

theme.init()
const paletteRef = ref<InstanceType<typeof CommandPalette> | null>(null)
const profileOpen = ref(false)
const shortcutsOpen = ref(false)
const notifOpen = ref(false)
const syncingAll = ref(false)
const lastSync = ref(0)
const unreadCount = ref(0)

async function globalSyncAll(force = false) {
  if (syncingAll.value) {
    showToast('Sync already in progress…', 'info')
    return
  }
  const now = Date.now()
  if (!force && now - lastSync.value < 60000) {
    showToast('Everything is up to date (synced <1min ago). Shift+click to force.', 'success')
    return
  }
  syncingAll.value = true
  showToast('Syncing modules from ERPNext…', 'info')
  try {
    const eps = ['leads', 'bookings', 'dues', 'employees', 'projects', 'inventory', 'pos', 'invoices', 'payments', 'contractors', 'labor', 'equipment', 'attendance', 'leave']
    await Promise.all(eps.map((e) => data.loadCollection(e).catch(() => null)))
    lastSync.value = Date.now()
    showToast('✅ Synced ' + eps.length + ' modules', 'success')
  } catch {
    showToast('Sync failed', 'error')
  }
  syncingAll.value = false
}

function loadUnread() {
  api.call<{ collections: Record<string, unknown> }>('bootstrap').then((r) => {
    if (r.ok && r.data) {
      const all = (r.data.collections.notifications as { read?: boolean }[]) ?? []
      unreadCount.value = all.filter((n) => !n.read).length
    }
  })
}
loadUnread()
const recentOpen = ref(false)
const activeGroupId = ref('executive')
const activeModuleId = ref('dashboard')

/* ── text size + content zoom ── */
const zoom = ref(100)
function fontStep(d: number) {
  const cur = parseFloat(getComputedStyle(document.documentElement).fontSize) || 14
  const px = Math.round(cur + d)
  document.documentElement.style.fontSize = `${Math.min(24, Math.max(11, px))}px`
}
function changeZoom(d: number) {
  zoom.value = Math.min(150, Math.max(60, zoom.value + d))
  const main = document.querySelector('.rem-content') as HTMLElement | null
  if (main) main.style.zoom = zoom.value === 100 ? '' : `${zoom.value}%`
}
function resetZoom() {
  zoom.value = 100
  const main = document.querySelector('.rem-content') as HTMLElement | null
  if (main) main.style.zoom = ''
}
function toggleFullScreen() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen()
  else if (document.exitFullscreen) document.exitFullscreen()
}

/* ── sidebar + top tabs ── */
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
  else router.push('/empty/' + m.id)
}

watch(
  () => route.path,
  (path) => {
    const g = groupForPath(path)
    if (g) {
      activeGroupId.value = g.id
      const m = moduleForPath(path)
      if (m) activeModuleId.value = m.id
    }
  },
  { immediate: true }
)

// open the command palette via deep-link ?palette=1 (after mount —
// the ref is null during setup, and the initial query doesn't change)
onMounted(() => {
  if (route.query.palette === '1') paletteRef.value?.openPalette()
})
watch(
  () => route.query.palette,
  (v) => {
    if (v === '1') paletteRef.value?.openPalette()
  }
)

const activeGroup = computed(() => GROUPS.find((g) => g.id === activeGroupId.value) ?? GROUPS[0])
const activeModule = computed(() => activeGroup.value.mods.find((m) => m.id === activeModuleId.value))
const topTabs = computed(() => visibleMods(activeGroup.value))

/* ── sidebar flyout ── */
const flyout = ref<{ group: ShellGroup; x: number; y: number } | null>(null)

function showFlyout(g: ShellGroup, e: MouseEvent) {
  flyout.value = { group: g, x: 76, y: Math.min(e.clientY - 20, window.innerHeight - 260) }
}
function hideFlyout() {
  flyout.value = null
}

/* ── helpers ── */
function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || 'U'
}

async function signOut() {
  await auth.signOut()
  router.push('/login')
}

function printReport() {
  window.print()
}

function exportCsv() {
  const rows: string[][] = [['module', 'count']]
  const sets: Record<string, unknown[]> = {
    leads: data.leads,
    bookings: data.bookings,
    dues: data.dues,
    employees: data.employees,
    projects: data.projects,
    inventory: data.inventory,
    pos: data.pos,
    invoices: data.invoices,
    payments: data.payments
  }
  for (const [k, v] of Object.entries(sets)) rows.push([k, String(v.length)])
  const csv = rows.map((r) => r.map((c) => '"' + String(c).replace(/"/g, '""') + '"').join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'rem-erp-export-' + new Date().toISOString().slice(0, 10) + '.csv'
  a.click()
  URL.revokeObjectURL(a.href)
}

/* ── global keyboard shortcuts (mirrors HTML PWA) ── */
let _gPending = false
let _gTime = 0
const _G_MAP: Record<string, string> = {
  c: '/customers', b: '/bookings', p: '/flats', f: '/finance',
  l: '/leads', h: '/employees', d: '/', s: '/stock', a: '/analytics'
}
function _isTypingTarget(e: KeyboardEvent): boolean {
  const t = e.target as HTMLElement | null
  return !!t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable)
}
onMounted(() => {
  window.addEventListener('keydown', (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      shortcutsOpen.value = false
      return
    }
    if (_isTypingTarget(e)) return
    if (e.key === '?') { e.preventDefault(); shortcutsOpen.value = true; return }
    if (e.key === '/') { e.preventDefault(); paletteRef.value?.openPalette(); return }
    if (e.key === 'g' || e.key === 'G') { _gPending = true; _gTime = Date.now(); e.preventDefault(); return }
    if (_gPending) {
      _gPending = false
      if (Date.now() - _gTime <= 1000 && _G_MAP[e.key.toLowerCase()]) {
        e.preventDefault()
        router.push(_G_MAP[e.key.toLowerCase()])
      }
    }
  })
})

</script>

<template>
  <div class="app-shell">
    <!-- ═══ SIDEBAR ═══ -->
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
            :title="_t(g.label)"
            @mouseenter="showFlyout(g, $event)"
            @mouseleave="hideFlyout"
            @click="switchGroup(g)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 18px; height: 18px" v-html="g.svg"></svg>
          </button>
          <div class="rem-sidebar-label">{{ _t(g.label.split(' & ')[0]) }}</div>
        </template>
      </div>
    </aside>

    <!-- SIDEBAR FLYOUT (sb-flyout) -->
    <SidebarFlyout :group="flyout?.group ?? null" :x="flyout?.x ?? 0" :y="flyout?.y ?? 0" @mouseleave="hideFlyout" />

    <!-- ═══ MAIN COLUMN ═══ -->
    <div style="display: flex; flex-direction: column; flex: 1; min-width: 0">
      <!-- TOP BAR -->
      <header class="rem-topbar" style="gap: 10px; padding: 0 12px">
        <span class="rem-topbar-title" style="font-size: 11px">🏗️ MARS Constech</span>

        <!-- GLOBAL SEARCH -->
        <GlobalSearch />

        <div class="top-nav" style="display: flex; align-items: center; gap: 2px; flex: 1; overflow-x: auto">
          <div
            v-for="m in topTabs"
            :key="m.id"
            class="top-nav-item"
            :class="{ active: activeModuleId === m.id }"
            @click="switchModule(m)"
          >
            {{ _t(m.label) }}
          </div>
        </div>

        <div class="top-actions" style="display: flex; align-items: center; gap: 2px; position: relative">
          <button class="rem-icon-btn" title="Keyboard Shortcuts (?)" @click="shortcutsOpen = true">⌨</button>
          <QuickAdd />
          <button class="rem-icon-btn" title="Print Report" @click="printReport">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 15px; height: 15px">
              <path d="M6 9V2h12v7" /><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" /><path d="M6 14h12v8H6z" />
            </svg>
          </button>
          <button class="rem-icon-btn" title="Export All as CSV" @click="exportCsv">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 15px; height: 15px">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </button>
          <button class="rem-icon-btn" :title="theme.dark ? 'Light Mode' : 'Dark Mode'" @click="theme.toggle()">{{ theme.dark ? '☀️' : '🌙' }}</button>
          <button class="rem-icon-btn" title="Theme Palette">🎨</button>
          <button class="rem-icon-btn" title="Notifications" style="position: relative" @click="notifOpen = true">
            <span v-if="unreadCount > 0" style="position: absolute; top: 0; right: 0; background: #c62828; color: #fff; border-radius: 8px; font-size: 7px; font-weight: 700; padding: 0 4px; line-height: 12px">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width: 15px; height: 15px">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
          </button>
          <button class="rem-icon-btn" title="Recent Items" style="position: relative; font-size: 15px; line-height: 1" @click="recentOpen = !recentOpen">🕘</button>
          <button class="rem-icon-btn" title="More" style="font-weight: 700">⋯</button>
          <button class="rem-icon-btn" title="Sync all with server (Shift+click = force full refresh)" style="color: #2f80ed" :class="{ spinning: syncingAll }" @click="globalSyncAll($event.shiftKey)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="width: 15px; height: 15px">
              <path d="M23 4v6h-6" /><path d="M1 20v-6h6" /><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
          </button>
          <button class="rem-icon-btn" title="Fullscreen" @click="toggleFullScreen">⛶</button>
          <div class="rem-user-chip" style="margin-left: 4px" title="User Profile" @click="profileOpen = true">
            <span class="chip-avatar">{{ initials(auth.fullName || auth.user) }}</span>
          </div>
        </div>
      </header>

      <!-- CONTENT -->
      <main class="rem-content" style="flex: 1; overflow-y: auto; padding: 12px 16px">
        <RouterView />
      </main>

      <!-- ═══ FOOTER ═══ -->
      <div
        class="app-footer"
        style="height: 28px; min-height: 28px; background: #fff; border-top: 1px solid #e8e8e8; display: flex; align-items: center; padding: 0 12px; font-size: 10px; color: #888; justify-content: space-between; position: sticky; bottom: 0; z-index: 20"
      >
        <div class="breadcrumb" style="display: flex; align-items: center; gap: 4px">
          <span class="crumb-part" style="cursor: pointer; color: #2f80ed; font-weight: 600" @click="router.push('/')">REM ERP</span>
          <span class="crumb-sep">›</span>
          <span class="crumb-part" style="cursor: pointer" @click="switchGroup(activeGroup)">{{ _t(activeGroup.label) }}</span>
          <span class="crumb-sep">›</span>
          <span class="crumb-part" style="cursor: pointer">{{ _t(activeModule?.label ?? '') }}</span>
        </div>

        <div style="display: flex; align-items: center; gap: 5px">
          <span class="ft-textsize" style="display: flex; align-items: center; gap: 2px; font-weight: 700; color: #555; font-size: 10px">A</span>
          <button class="ft-textsize" title="Decrease text size" style="padding: 1px 5px; border: 1px solid #e0e0e0; border-radius: 4px; background: #fff; cursor: pointer; font-size: 10px; color: #555" @click="fontStep(-1)">−</button>
          <button class="ft-textsize" title="Increase text size" style="padding: 2px 6px; border: 1px solid #e0e0e0; border-radius: 4px; background: #fff; cursor: pointer; font-size: 11px; color: #555" @click="fontStep(1)">+</button>
          <span class="ft-textsize" style="color: #e0e0e0">|</span>
          <button title="Decrease zoom" style="padding: 1px 5px; border: 1px solid #e0e0e0; border-radius: 4px; background: #fff; cursor: pointer; font-size: 10px; color: #555" @click="changeZoom(-10)">−</button>
          <span id="zoomLabel" title="Reset zoom" style="cursor: pointer; font-weight: 600; min-width: 36px; text-align: center; font-size: 11px" @click="resetZoom">{{ zoom }}%</span>
          <button title="Increase zoom" style="padding: 2px 6px; border: 1px solid #e0e0e0; border-radius: 4px; background: #fff; cursor: pointer; font-size: 11px; color: #555" @click="changeZoom(10)">+</button>
          <span style="color: #e0e0e0">|</span>
          <button title="Fullscreen" style="padding: 2px 6px; border: 1px solid #e0e0e0; border-radius: 4px; background: #fff; cursor: pointer; font-size: 10px; color: #555" @click="toggleFullScreen">⛶</button>
          <span class="ft-extra" style="color: #e0e0e0">|</span>
          <span
            id="footerLangBtn"
            title="বাংলা / English"
            style="cursor: pointer; font-size: 9px; font-weight: 700; color: #555; padding: 1px 5px; border: 1px solid #d0d8e8; border-radius: 4px"
            @click="i18n.toggle()"
          >{{ i18n.lang === 'bn' ? 'বাং' : 'EN' }}</span>
          <span class="ft-extra" :title="theme.dark ? 'Light Mode' : 'Dark Mode'" style="cursor: pointer; font-size: 12px; padding: 1px 4px; border-radius: 3px" @click="theme.toggle()">{{ theme.dark ? '☀️' : '🌙' }}</span>
          <span class="ft-extra" style="color: #e0e0e0">|</span>
          <span
            id="footerRoleBtn"
            style="cursor: pointer; font-size: 10px; font-weight: 600; color: #2f80ed; padding: 1px 6px; border: 1px solid #d0d8e8; border-radius: 4px"
            title="User Profile"
            @click="profileOpen = true"
          >{{ initials(auth.fullName || auth.user) }}</span>
          <button class="action-btn" style="padding: 1px 8px; font-size: 9px" @click="signOut">{{ _t('Sign Out') }}</button>
        </div>
      </div>
    </div>
      <ToastContainer />
    <ProfilePanel :open="profileOpen" @close="profileOpen = false" />
    <ShortcutsModal :open="shortcutsOpen" @close="shortcutsOpen = false" />
    <!-- Command palette -->
    <CommandPalette ref="paletteRef" />
    <!-- Notifications + Recent panels -->
    <NotificationsPanel :open="notifOpen" @close="notifOpen = false" />
    <RecentTray :open="recentOpen" @close="recentOpen = false" />
  </div>
</template>
