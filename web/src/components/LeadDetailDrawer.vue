<script setup lang="ts">
/**
 * LeadDetailDrawer — mirrors the HTML PWA leadSlideOut panel:
 * Profile / Notes / Activities / Reminders tabs with a stat row.
 */
import { ref, watch } from 'vue'
import type { Lead } from '@/api/types'

const props = defineProps<{ lead: Lead | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()

const tab = ref('profile')

watch(
  () => props.lead,
  () => (tab.value = 'profile')
)

const tabs = [
  { id: 'profile', label: 'Profile' },
  { id: 'notes', label: 'Notes' },
  { id: 'activities', label: 'Activity Log' },
  { id: 'reminders', label: 'Reminders' }
]

function statusColor(s: string): string {
  const map: Record<string, string> = {
    'New Inquiry': '#1565c0',
    Contacted: '#2f80ed',
    'Site Visit': '#e65100',
    Negotiation: '#ff8f00',
    Booking: '#2e7d32',
    Lost: '#c62828'
  }
  return map[s] ?? '#555'
}

const notes = ref<{ text: string; by: string; when: string }[]>([
  { text: 'Called — interested in 3BHK in Ashulia. Will visit site Saturday.', by: 'Shamim Reza', when: '2d ago' },
  { text: 'Sent brochure + price list via WhatsApp.', by: 'CRM Bot', when: '5d ago' }
])

const activities = ref<{ icon: string; text: string; when: string }[]>([
  { icon: '📞', text: 'Call logged — 12 min, discussed payment plan', when: '2d ago' },
  { icon: '📧', text: 'Email sent — project brochure (Jolshiri Abason)', when: '5d ago' },
  { icon: '🎯', text: 'Lead created from Facebook', when: '9d ago' }
])

const reminders = ref<{ text: string; when: string }[]>([
  { text: 'Follow up — site visit confirmation', when: '2026-08-12' },
  { text: 'Send payment plan options', when: '2026-08-14' }
])
</script>

<template>
  <div v-if="lead" class="drawer-overlay active" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 560px">
      <div class="drawer-header">
        <h3>{{ lead.name }}</h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <!-- Tabs -->
      <div style="display: flex; gap: 0; border-bottom: 1px solid #e8e8e8; padding: 0 8px">
        <div
          v-for="t in tabs"
          :key="t.id"
          class="top-nav-item"
          :class="{ active: tab === t.id }"
          style="padding: 7px 12px; font-size: 11px"
          @click="tab = t.id"
        >{{ t.label }}</div>
      </div>

      <div class="drawer-body">
        <!-- PROFILE -->
        <div v-if="tab === 'profile'">
          <div class="stats-row" style="grid-template-columns: 1fr 1fr">
            <div class="stat-card">
              <div class="label">📞 Phone</div>
              <div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.phone || '—' }}</div>
            </div>
            <div class="stat-card">
              <div class="label">✉ Email</div>
              <div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.email || '—' }}</div>
            </div>
          </div>

          <div style="margin-top: 12px; font-size: 11px; color: #555; line-height: 2">
            <div><span style="color: #888">Source:</span> <b>{{ lead.source }}</b></div>
            <div><span style="color: #888">Status:</span>
              <span class="pill" :style="{ background: statusColor(lead.status) + '22', color: statusColor(lead.status) }">{{ lead.status }}</span>
            </div>
            <div><span style="color: #888">Priority:</span>
              <b :style="{ color: lead.priority === 'High' ? '#c62828' : lead.priority === 'Medium' ? '#e65100' : '#888' }">{{ lead.priority }}</b>
            </div>
            <div><span style="color: #888">Score:</span> <b style="color: #2f80ed">{{ lead.score }}</b></div>
            <div><span style="color: #888">Follow-up:</span> {{ lead.follow_up || '—' }}</div>
            <div><span style="color: #888">Last contact:</span> {{ lead.last_contact || '—' }}</div>
          </div>

          <div style="margin-top: 12px; display: flex; gap: 6px">
            <button class="action-btn primary" @click="emit('status', 'Booking')">✓ Mark Booking</button>
            <button class="action-btn" @click="emit('status', 'Site Visit')">📍 Site Visit</button>
            <button class="action-btn" @click="emit('status', 'Lost')">✕ Lost</button>
          </div>
        </div>

        <!-- NOTES -->
        <div v-else-if="tab === 'notes'">
          <div v-for="(n, i) in notes" :key="i" style="padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div style="font-size: 11px; color: #333">{{ n.text }}</div>
            <div style="font-size: 9px; color: #888; margin-top: 2px">{{ n.by }} · {{ n.when }}</div>
          </div>
          <div v-if="notes.length === 0" style="padding: 16px; text-align: center; color: #999; font-size: 11px">No notes</div>
        </div>

        <!-- ACTIVITIES -->
        <div v-else-if="tab === 'activities'">
          <div v-for="(a, i) in activities" :key="i" style="display: flex; align-items: center; gap: 8px; padding: 7px 0; border-bottom: 1px solid #f5f5f5">
            <span style="font-size: 14px">{{ a.icon }}</span>
            <span style="flex: 1; font-size: 11px; color: #333">{{ a.text }}</span>
            <span style="font-size: 9px; color: #888">{{ a.when }}</span>
          </div>
        </div>

        <!-- REMINDERS -->
        <div v-else>
          <div v-for="(r, i) in reminders" :key="i" style="display: flex; align-items: center; gap: 8px; padding: 7px 0; border-bottom: 1px solid #f5f5f5">
            <span style="font-size: 13px">⏰</span>
            <span style="flex: 1; font-size: 11px; color: #333">{{ r.text }}</span>
            <span style="font-size: 9px; color: #e65100">{{ r.when }}</span>
          </div>
        </div>
      </div>

      <div class="drawer-footer">
        <button class="drawer-btn" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
