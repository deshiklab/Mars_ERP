<script setup lang="ts">
/**
 * GlobalSearch — mirrors the HTML PWA #searchBar/#searchDropdown:
 * Ctrl+K focus, live search across the loaded data store, dropdown
 * results grouped by module, keyboard navigation.
 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'

const router = useRouter()
const data = useDataStore()

const open = ref(false)
const q = ref('')
const inputRef = ref<HTMLInputElement | null>(null)
const hl = ref(0)

interface Hit {
  module: string
  title: string
  sub: string
  path: string
  icon: string
}

const searchIndex = computed<Hit[]>(() => {
  const idx: Hit[] = []
  data.leads.forEach((l) =>
    idx.push({ module: 'CRM & Leads', title: l.name, sub: `${l.email} · ${l.phone} · ${l.status}`, path: '/leads', icon: '🎯' })
  )
  data.bookings.forEach((b) =>
    idx.push({ module: 'Bookings', title: `${b.id} — ${b.client}`, sub: `${b.property} ${b.unit} · ${b.status}`, path: '/bookings', icon: '📋' })
  )
  data.dues.forEach((d) =>
    idx.push({ module: 'Dues & Recovery', title: d.customer, sub: `${d.project} ${d.unit} · due ${d.due}`, path: '/dues', icon: '💰' })
  )
  data.employees.forEach((e) =>
    idx.push({ module: 'HR', title: e.name, sub: `${e.designation} · ${e.dept}`, path: '/hr', icon: '💼' })
  )
  data.projects.forEach((p) =>
    idx.push({ module: 'Projects', title: p.name, sub: `${p.type} · ${p.status}`, path: '/projects', icon: '🏗️' })
  )
  return idx
})

const results = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return []
  return searchIndex.value
    .filter((h) => (h.title + ' ' + h.sub + ' ' + h.module).toLowerCase().includes(query))
    .slice(0, 24)
})

function onKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    open.value = true
    nextTick(() => inputRef.value?.focus())
  }
  if (!open.value) return
  if (e.key === 'Escape') {
    open.value = false
    q.value = ''
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    hl.value = Math.min(results.value.length - 1, hl.value + 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    hl.value = Math.max(0, hl.value - 1)
  } else if (e.key === 'Enter' && results.value[hl.value]) {
    openHit(results.value[hl.value])
  }
}

function openHit(h: Hit) {
  open.value = false
  q.value = ''
  router.push(h.path)
}

function onDocumentClick(e: MouseEvent) {
  const t = e.target as HTMLElement
  if (!t.closest('#searchWrap') && !t.closest('#searchDropdown')) open.value = false
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  document.addEventListener('click', onDocumentClick)
  // preload all module data so search covers everything
  data.loadLeads()
  data.loadBookings()
  data.loadDues()
  data.loadEmployees()
  data.loadProjects()
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  document.removeEventListener('click', onDocumentClick)
})
</script>

<template>
  <div id="searchWrap" style="position: relative">
    <div
      id="searchBar"
      style="
        display: flex;
        align-items: center;
        gap: 6px;
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 3px 8px;
        cursor: pointer;
        min-width: 220px;
      "
      @click="open = true; nextTick(() => inputRef?.focus())"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 13px; height: 13px; color: #888">
        <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <input
        ref="inputRef"
        v-model="q"
        placeholder="Search anything..."
        style="border: none; outline: none; background: transparent; font-size: 11px; flex: 1; color: #333"
        @focus="open = true"
      />
      <span style="font-size: 9px; color: #999; border: 1px solid #ddd; border-radius: 4px; padding: 0 4px">⌘K</span>
    </div>

    <!-- DROPDOWN -->
    <div
      id="searchDropdown"
      v-if="open"
      style="
        position: absolute;
        top: calc(100% + 8px);
        left: 0;
        width: 380px;
        max-width: 92vw;
        background: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
        z-index: 9999;
        overflow: hidden;
      "
    >
      <div style="display: flex; align-items: center; gap: 8px; padding: 10px; border-bottom: 1px solid #f0f0f0">
        <svg viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2" style="width: 14px; height: 14px">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          v-model="q"
          placeholder="Search leads, projects, bookings..."
          style="border: none; outline: none; font-size: 12px; flex: 1; color: #333"
          @keydown="onKeydown"
        />
        <span style="cursor: pointer; color: #999; font-size: 13px; padding: 2px" @click="open = false">✕</span>
      </div>

      <div style="max-height: 320px; overflow-y: auto">
        <div v-if="!q" style="padding: 24px; text-align: center; color: #999; font-size: 11px">
          <div style="font-size: 22px; margin-bottom: 6px">🔍</div>
          Type to search across leads, projects, bookings & more
        </div>
        <div
          v-for="(h, i) in results"
          :key="i"
          style="
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            cursor: pointer;
            border-left: 2px solid transparent;
          "
          :style="i === hl ? 'background:#f0f4ff;border-left-color:#2f80ed' : ''"
          @mouseenter="hl = i"
          @click="openHit(h)"
        >
          <span style="width: 28px; height: 28px; border-radius: 6px; background: #f5f5f5; display: flex; align-items: center; justify-content: center; font-size: 13px">{{ h.icon }}</span>
          <div style="flex: 1; min-width: 0">
            <div style="font-size: 11px; font-weight: 600; color: #333">{{ h.title }}</div>
            <div style="font-size: 9px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ h.sub }}</div>
          </div>
          <span style="font-size: 8px; color: #999; border: 1px solid #eee; border-radius: 4px; padding: 1px 4px; white-space: nowrap">{{ h.module }}</span>
        </div>
        <div v-if="q && results.length === 0" style="padding: 24px; text-align: center; color: #999; font-size: 11px">
          No results for "{{ q }}"
        </div>
      </div>

      <div style="display: flex; justify-content: space-between; padding: 6px 12px; border-top: 1px solid #f0f0f0; font-size: 9px; color: #999">
        <span>{{ results.length }} results</span>
        <span>↑↓ Navigate · ↩ Open · ⎋ Close</span>
      </div>
    </div>
  </div>
</template>
