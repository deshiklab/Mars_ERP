<script setup lang="ts">
/**
 * NotificationsPanel — mirrors the HTML notifPanel slide-out:
 * header + filter tabs + grouped notifications.
 */
import { ref } from 'vue'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const tab = ref('all')

const notifs = [
  { icon: '💵', title: 'Payment received', body: 'BKG-00007 · ৳ 12.0 Lac received from Nasrin Akter', when: '10m ago', unread: true },
  { icon: '⚠️', title: 'Due overdue', body: 'Delwar Hossain — 212 days overdue (৳ 88.7 Lac)', when: '1h ago', unread: true },
  { icon: '🎯', title: 'New lead assigned', body: 'Laily Akhter assigned to you', when: '3h ago', unread: true },
  { icon: '📅', title: 'Site visit scheduled', body: 'Shahidul Islam · Ashulia Smart Town · Sat 10:00', when: '1d ago', unread: false },
  { icon: '✅', title: 'Booking confirmed', body: 'BKG-00012 — Kazi Nizam confirmed', when: '2d ago', unread: false }
]

const tabs = [
  { id: 'all', label: 'All' },
  { id: 'unread', label: 'Unread' },
  { id: 'payments', label: 'Payments' },
  { id: 'leads', label: 'Leads' }
]

function filtered() {
  if (tab.value === 'unread') return notifs.filter((n) => n.unread)
  if (tab.value === 'payments') return notifs.filter((n) => n.icon === '💵')
  if (tab.value === 'leads') return notifs.filter((n) => n.icon === '🎯')
  return notifs
}
</script>

<template>
  <!-- backdrop -->
  <div v-if="open" class="drawer-overlay active" style="justify-content: flex-start" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 380px; animation: none">
      <div class="drawer-header">
        <h3>🔔 Notifications <span style="font-size: 9px; color: #888">{{ notifs.filter((n) => n.unread).length }} unread</span></h3>
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
          :style="n.unread ? 'background:#f7faff' : ''"
        >
          <span style="font-size: 16px; width: 24px; text-align: center">{{ n.icon }}</span>
          <div style="flex: 1; min-width: 0">
            <div style="font-size: 11px; font-weight: 600; color: #333; display: flex; align-items: center; gap: 6px">
              {{ n.title }}
              <span v-if="n.unread" style="width: 6px; height: 6px; border-radius: 50%; background: #2f80ed; flex-shrink: 0"></span>
            </div>
            <div style="font-size: 10px; color: #888; margin-top: 1px">{{ n.body }}</div>
            <div style="font-size: 8px; color: #aaa; margin-top: 2px">{{ n.when }}</div>
          </div>
        </div>
        <div v-if="filtered().length === 0" style="padding: 24px; text-align: center; color: #999; font-size: 11px">
          No notifications
        </div>
      </div>
    </div>
  </div>
</template>
