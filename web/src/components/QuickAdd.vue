<script setup lang="ts">
/**
 * QuickAdd — mirrors the HTML PWA quickAddDropdown: tabs (All/CRM/Bookings/
 * Finance/HR), search, item grid. Opens from the topbar + button.
 */
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const open = ref(false)
const q = ref('')
const tab = ref('all')

const items = [
  { label: 'New Lead', icon: '🎯', tab: 'crm', path: '/leads' },
  { label: 'New Booking', icon: '📋', tab: 'bookings', path: '/bookings' },
  { label: 'New Project', icon: '🏗️', tab: 'projects', path: '/projects' },
  { label: 'New Employee', icon: '👥', tab: 'hr', path: '/hr' },
  { label: 'Record Payment', icon: '💰', tab: 'finance', path: '/dues' },
  { label: 'New Due Entry', icon: '🧾', tab: 'finance', path: '/dues' },
  { label: 'Print Report', icon: '🖨', tab: 'all', path: '' },
  { label: 'Export CSV', icon: '📥', tab: 'all', path: '' },
  { label: 'Toggle Theme', icon: '🌙', tab: 'all', path: '' }
]

const tabs = [
  { id: 'all', label: 'All' },
  { id: 'crm', label: 'CRM' },
  { id: 'bookings', label: 'Bookings' },
  { id: 'projects', label: 'Projects' },
  { id: 'hr', label: 'HR' },
  { id: 'finance', label: 'Finance' }
]

const filtered = computed(() => {
  let list = items
  if (tab.value !== 'all') list = list.filter((i) => i.tab === tab.value || i.tab === 'all')
  if (q.value.trim()) {
    const lq = q.value.trim().toLowerCase()
    list = list.filter((i) => i.label.toLowerCase().includes(lq))
  }
  return list
})

function pick(item: { label: string; icon: string; tab: string; path: string }) {
  open.value = false
  q.value = ''
  if (item.path) router.push(item.path)
}

function setTab(t: string) {
  tab.value = t
}
</script>

<template>
  <div style="position: relative">
    <button class="rem-icon-btn" title="Quick Add" style="font-weight: 700; font-size: 16px; color: #2f80ed" @click="open = !open">+</button>

    <div
      v-if="open"
      style="
        position: fixed;
        top: 52px;
        right: 160px;
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
      <!-- header + search -->
      <div style="padding: 10px 12px; border-bottom: 1px solid #f0f0f0">
        <div style="display: flex; align-items: center; gap: 8px">
          <span style="font-size: 12px; font-weight: 700; color: #333">⚡ Quick Add</span>
          <input
            v-model="q"
            placeholder="Search actions..."
            style="flex: 1; border: 1px solid #e0e0e0; border-radius: 6px; padding: 4px 8px; font-size: 11px; outline: none"
          />
        </div>
      </div>

      <!-- tabs -->
      <div style="display: flex; gap: 4px; padding: 8px 12px; border-bottom: 1px solid #f0f0f0; flex-wrap: wrap">
        <button
          v-for="t in tabs"
          :key="t.id"
          style="
            padding: 3px 10px;
            font-size: 10px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
          "
          :style="tab === t.id ? 'background:#2f80ed;color:#fff' : 'background:#f0f0f0;color:#666'"
          @click="setTab(t.id)"
        >{{ t.label }}</button>
      </div>

      <!-- grid -->
      <div style="max-height: 300px; overflow-y: auto; padding: 8px; display: grid; grid-template-columns: 1fr 1fr; gap: 6px">
        <div
          v-for="(item, i) in filtered"
          :key="i"
          style="
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            border: 1px solid #eee;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.12s;
          "
          @mouseover="($event.currentTarget as HTMLElement).style.borderColor = '#2f80ed'"
          @mouseout="($event.currentTarget as HTMLElement).style.borderColor = ''"
          @click="pick(item)"
        >
          <span style="font-size: 15px">{{ item.icon }}</span>
          <span style="font-size: 11px; font-weight: 500; color: #333">{{ item.label }}</span>
        </div>
        <div v-if="filtered.length === 0" style="grid-column: 1/-1; text-align: center; color: #999; font-size: 11px; padding: 16px">
          No actions match
        </div>
      </div>
    </div>
  </div>
</template>
