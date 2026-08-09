<script setup lang="ts">
/**
 * RecentTray — mirrors the HTML recentTray: recently viewed items.
 * Items are tracked in localStorage; the tray opens from 🕘.
 */
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()
const router = useRouter()

const recent = ref<{ title: string; sub: string; path: string; icon: string; when: string }[]>([])

function load() {
  try {
    recent.value = JSON.parse(localStorage.getItem('sd_recent_vue') ?? '[]')
  } catch {
    recent.value = []
  }
}
watch(() => props.open, (o) => o && load(), { immediate: true })

/** Track a viewed item (called by views or the search). */
function trackRecent(title: string, sub: string, path: string, icon: string) {
  try {
    const list = JSON.parse(localStorage.getItem('sd_recent_vue') ?? '[]')
    list.unshift({ title, sub, path, icon, when: 'just now' })
    const dedup = list.filter((x: { path: string }, i: number, a: { path: string }[]) => a.findIndex((y) => y.path === x.path) === i)
    localStorage.setItem('sd_recent_vue', JSON.stringify(dedup.slice(0, 8)))
  } catch {
    /* ignore */
  }
}

defineExpose({ trackRecent })

function openItem(r: { path: string }) {
  emit('close')
  router.push(r.path)
}

function removeItem(i: number) {
  recent.value.splice(i, 1)
  localStorage.setItem('sd_recent_vue', JSON.stringify(recent.value))
}

function clearAll() {
  recent.value = []
  localStorage.removeItem('sd_recent_vue')
}
</script>

<template>
  <div
    v-if="open"
    style="
      position: fixed;
      top: 52px;
      right: 200px;
      width: 300px;
      background: #fff;
      border: 1px solid #e0e0e0;
      border-radius: 10px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
      z-index: 9999;
      overflow: hidden;
    "
  >
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-bottom: 1px solid #f0f0f0">
      <span style="font-size: 12px; font-weight: 700; color: #333">🕘 Recent Items</span>
      <span v-if="recent.length" style="font-size: 9px; color: #2f80ed; cursor: pointer" @click="clearAll">Clear all</span>
    </div>
    <div style="max-height: 300px; overflow-y: auto; padding: 6px">
      <div
        v-for="(r, i) in recent"
        :key="r.path"
        style="display: flex; align-items: center; gap: 10px; padding: 8px; border-radius: 6px; cursor: pointer"
        @mouseover="($event.currentTarget as HTMLElement).style.background = '#f0f4ff'"
        @mouseout="($event.currentTarget as HTMLElement).style.background = ''"
        @click="openItem(r)"
      >
        <span style="font-size: 14px; width: 22px; text-align: center">{{ r.icon }}</span>
        <div style="flex: 1; min-width: 0">
          <div style="font-size: 11px; font-weight: 600; color: #333">{{ r.title }}</div>
          <div style="font-size: 9px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ r.sub }}</div>
        </div>
        <span style="font-size: 9px; color: #999; cursor: pointer" @click.stop="removeItem(i)">✕</span>
      </div>
      <div v-if="recent.length === 0" style="padding: 20px; text-align: center; color: #999; font-size: 11px">
        No recent items yet<br /><span style="font-size: 9px">Items you open will appear here</span>
      </div>
    </div>
  </div>
</template>
