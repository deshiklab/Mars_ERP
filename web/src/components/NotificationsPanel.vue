<script setup lang="ts">
/**
 * NotificationsPanel — mirrors the HTML notifPanel slide-out:
 * header + filter tabs + grouped notifications.
 */
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/client'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const tab = ref('all')

interface ServerNotif {
  id: string
  title: string
  sub: string
  type: string
  time: number
  read: boolean
}

const notifs = ref<ServerNotif[]>([])
const router = useRouter()
const notifRoutes: Record<string, string> = { lead: '/leads', payment: '/finance', dues: '/dues', due: '/dues', booking: '/bookings', ticket: '/tickets', handover: '/handover', po: '/stock', employee: '/hr', warning: '/tasks', task: '/tasks', approval: '/approvals', add: '/dashboard' }
function goNotif(n: ServerNotif) {
  n.read = true
  const path = notifRoutes[n.type] || notifRoutes[n.type.split('_')[0]] || ''
  if (path) router.push(path)
  else emit('close')
}
function markAllRead() {
  notifs.value.forEach((n) => (n.read = true))
  persistRead()
}
function persistRead() {
  api.call('sync', { collections: { notifications: notifs.value } }).catch(() => {})
}


const notifIcons: Record<string, string> = {
  add: '✅',
  warning: '⚠️',
  lead: '🎯',
  payment: '💵',
  approval: '📝',
  due: '⏰',
  task: '📋'
}

function loadNotifs() {
  api.call<{ collections: Record<string, unknown> }>('bootstrap').then((r) => {
    if (r.ok && r.data) {
      const all = (r.data.collections.notifications as ServerNotif[]) ?? []
      notifs.value = all.slice(0, 30)
    }
  })
}

onMounted(loadNotifs)

const tabs = [
  { id: 'all', label: 'All' },
  { id: 'unread', label: 'Unread' },
  { id: 'payments', label: 'Payments' },
  { id: 'leads', label: 'Leads' }
]

function filtered() {
  if (tab.value === 'unread') return notifs.value.filter((n) => !n.read)
  if (tab.value === 'payments') return notifs.value.filter((n) => n.type === 'payment')
  if (tab.value === 'leads') return notifs.value.filter((n) => n.type === 'lead')
  return notifs.value
}
</script>

<template>
  <!-- backdrop -->
  <div v-if="open" class="drawer-overlay active" style="justify-content: flex-start" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 380px; animation: none">
      <div class="drawer-header">
        <h3>🔔 Notifications <span style="font-size: 9px; color: #888">{{ notifs.filter((n) => !n.read).length }} unread</span>
          <span v-if="notifs.some((n) => !n.read)" @click="markAllRead()" style="font-size: 9px; color: #2f80ed; cursor: pointer; margin-left: 8px">Mark all read</span>
        </h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <!-- tabs -->
      <div style="display: flex; gap: 4px; padding: 8px 12px; border-bottom: 1px solid #f0f0f0">
        <button
          v-for="t in tabs"
          :key="t.id"
          style="padding: 3px 10px; font-size: 10px; border: none; border-radius: 12px; cursor: pointer; font-weight: 600"
          :style="tab === t.id ? 'background:#2f80ed;color:#fff' : 'background:#f0f0f0;color:#666'"
          @click="tab = t.id"
        >{{ t.label }}</button>
      </div>

      <!-- list -->
      <div class="drawer-body" style="padding: 6px 10px">
        <div
          v-for="(n, i) in filtered()"
          :key="i"
          style="display: flex; align-items: flex-start; gap: 10px; padding: 9px 6px; border-bottom: 1px solid #f5f5f5; cursor: pointer"
          :style="!n.read ? 'background:#f7faff' : ''"
          @click="goNotif(n)"
        >
          <span style="font-size: 16px; width: 24px; text-align: center">{{ notifIcons[n.type] ?? '🔔' }}</span>
          <div style="flex: 1; min-width: 0">
            <div style="font-size: 11px; font-weight: 600; color: #333; display: flex; align-items: center; gap: 6px">
              {{ n.title }}
              <span v-if="!n.read" style="width: 6px; height: 6px; border-radius: 50%; background: #2f80ed; flex-shrink: 0"></span>
            </div>
            <div style="font-size: 10px; color: #888; margin-top: 1px">{{ n.sub }}</div>
            <div style="font-size: 8px; color: #aaa; margin-top: 2px">{{ new Date(n.time).toLocaleString() }}</div>
          </div>
        </div>
        <div v-if="filtered().length === 0" style="padding: 24px; text-align: center; color: #999; font-size: 11px">
          No notifications
        </div>
      </div>
    </div>
  </div>
</template>
