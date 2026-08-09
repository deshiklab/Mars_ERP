<script setup lang="ts">
/**
 * CommandPalette — mirrors the HTML PWA cpOverlay:
 * Ctrl+K overlay with search, grouped actions, keyboard navigation.
 */
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { theme } from '@/i18n'

const route = useRoute()
const router = useRouter()
const open = ref(false)
const q = ref('')
const hl = ref(0)
const inputRef = ref<HTMLInputElement | null>(null)

interface Cmd {
  label: string
  icon: string
  sub: string
  group: string
  run: () => void
}

const commands: Cmd[] = [
  { label: '+ New Lead', icon: '🎯', sub: 'Capture a new lead', group: 'Actions', run: () => router.push('/leads') },
  { label: '+ New Booking', icon: '📝', sub: 'Create a booking', group: 'Actions', run: () => router.push('/bookings') },
  { label: '+ New Employee', icon: '👤', sub: 'Onboard an employee', group: 'Actions', run: () => router.push('/hr') },
  { label: '+ New Project', icon: '🏗️', sub: 'Create a project', group: 'Actions', run: () => router.push('/projects') },
  { label: 'Open Quick Add', icon: '➕', sub: 'Quick-add menu', group: 'Actions', run: () => router.push('/') },
  { label: 'Toggle Dark Mode', icon: '🌙', sub: 'Switch light / dark theme', group: 'System', run: () => theme.toggle() },
  { label: 'Go to Settings', icon: '⚙️', sub: 'System settings', group: 'System', run: () => router.push('/') },
  { label: 'Export All as CSV', icon: '📤', sub: 'Export current data', group: 'System', run: () => console.log('export') },
  { label: 'Go to Dashboard', icon: '📊', sub: 'Executive dashboard', group: 'Navigate', run: () => router.push('/') },
  { label: 'Go to CRM & Leads', icon: '🎯', sub: 'Sales pipeline', group: 'Navigate', run: () => router.push('/leads') },
  { label: 'Go to Bookings', icon: '📋', sub: 'All bookings', group: 'Navigate', run: () => router.push('/bookings') },
  { label: 'Go to Dues & Recovery', icon: '💰', sub: 'Collections', group: 'Navigate', run: () => router.push('/dues') },
  { label: 'Go to Projects', icon: '🏗️', sub: 'Construction projects', group: 'Navigate', run: () => router.push('/projects') },
  { label: 'Go to HR & Employees', icon: '👥', sub: 'People operations', group: 'Navigate', run: () => router.push('/hr') }
]

const groups = computed(() => {
  const out: { group: string; items: Cmd[] }[] = []
  const query = q.value.trim().toLowerCase()
  const filtered = query
    ? commands.filter((c) => (c.label + ' ' + c.sub + ' ' + c.group).toLowerCase().includes(query))
    : commands
  for (const c of filtered) {
    const g = out.find((x) => x.group === c.group)
    if (g) g.items.push(c)
    else out.push({ group: c.group, items: [c] })
  }
  return out
})

const flat = computed(() => groups.value.flatMap((g) => g.items))

function openPalette() {
  open.value = true
  hl.value = 0
  nextTick(() => inputRef.value?.focus())
}

function closePalette() {
  open.value = false
  q.value = ''
}

function run(c: Cmd) {
  closePalette()
  c.run()
}

function onKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    open.value ? closePalette() : openPalette()
  }
  if (!open.value) return
  if (e.key === 'Escape') closePalette()
  else if (e.key === 'ArrowDown') {
    e.preventDefault()
    hl.value = Math.min(flat.value.length - 1, hl.value + 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    hl.value = Math.max(0, hl.value - 1)
  } else if (e.key === 'Enter' && flat.value[hl.value]) {
    run(flat.value[hl.value])
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  // deep-link support: /?palette=1 opens the palette once routing resolves
  router.isReady().then(() => {
    if (router.currentRoute.value.query.palette === '1') openPalette()
  })
})
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))

defineExpose({ openPalette })
</script>

<template>
  <div
    v-if="open"
    style="
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.4);
      z-index: 9999;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding-top: 15vh;
    "
    @click.self="closePalette"
  >
    <div
      style="
        width: 100%;
        max-width: 560px;
        background: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 14px;
        box-shadow: 0 24px 64px rgba(0, 0, 0, 0.28);
        overflow: hidden;
        color: #333;
      "
    >
      <!-- input -->
      <div style="display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid #e8e8e8">
        <svg viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2" style="width: 16px; height: 16px">
          <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          ref="inputRef"
          v-model="q"
          placeholder="Type a command or search…"
          style="flex: 1; border: none; outline: none; font-size: 14px; background: transparent; color: #333"
          @keydown="onKeydown"
        />
        <span style="font-size: 9px; color: #999; border: 1px solid #ddd; border-radius: 4px; padding: 1px 5px">ESC</span>
      </div>

      <!-- results -->
      <div style="max-height: 380px; overflow-y: auto; padding: 6px">
        <template v-for="g in groups" :key="g.group">
          <div style="font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #999; padding: 8px 10px 3px">
            {{ g.group }}
          </div>
          <div
            v-for="c in g.items"
            :key="c.label"
            style="display: flex; align-items: center; gap: 9px; padding: 7px 10px; border-radius: 8px; cursor: pointer"
            :style="flat.indexOf(c) === hl ? 'background:#f0f4ff' : ''"
            @mouseenter="hl = flat.indexOf(c)"
            @click="run(c)"
          >
            <span style="font-size: 15px; width: 22px; text-align: center">{{ c.icon }}</span>
            <div style="flex: 1; min-width: 0">
              <div style="font-size: 12px; font-weight: 600; color: #333">{{ c.label }}</div>
              <div style="font-size: 10px; color: #888">{{ c.sub }}</div>
            </div>
          </div>
        </template>
        <div v-if="flat.length === 0" style="padding: 24px; text-align: center; color: #999; font-size: 12px">
          No commands match "{{ q }}"
        </div>
      </div>
    </div>
  </div>
</template>
