<script setup lang="ts">
/**
 * LeadDetailDrawer v2 — full lead-panel mirroring the HTML PWA leadSlideOut:
 * header (avatar + name + badges), 10 tabs (Profile, Proposals, Tasks,
 * Attachments, Reminders, Notes, Activity Log, Chat/Contact, Invoices,
 * Payments), score bar, status action buttons.
 */
import { computed, ref, watch } from 'vue'
import { useDataStore } from '@/stores/data'
import type { Lead } from '@/api/types'

const props = defineProps<{ lead: Lead | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()
const data = useDataStore()

const tab = ref('profile')
watch(() => props.lead, () => (tab.value = 'profile'))

const tabs = [
  { id: 'profile', label: 'Profile' },
  { id: 'proposals', label: 'Proposals' },
  { id: 'tasks', label: 'Tasks' },
  { id: 'attachments', label: 'Attachments' },
  { id: 'reminders', label: 'Reminders' },
  { id: 'notes', label: 'Notes' },
  { id: 'activities', label: 'Activity Log' },
  { id: 'invoices', label: 'Invoices' },
  { id: 'payments', label: 'Payments' }
]

function badgeColor(v: string | undefined): string {
  const map: Record<string, string> = {
    'New Inquiry': '#1565c0', Contacted: '#2f80ed', 'Site Visit': '#e65100',
    Negotiation: '#7b1fa2', Booking: '#2e7d32', Lost: '#c62828', Junk: '#888',
    High: '#c62828', Medium: '#e65100', Low: '#888', Local: '#2f80ed', NRB: '#7b1fa2',
    Website: '#1565c0', Facebook: '#1e88e5', Referral: '#2e7d32', 'Walk-in': '#00838f',
    Agent: '#e65100', Bikroy: '#f9a825', 'NRB Direct': '#7b1fa2', 'Cold Call': '#546e7a'
  }
  return map[v ?? ''] ?? '#2f80ed'
}

function scoreColor(s: number): string {
  return s >= 80 ? '#2e7d32' : s >= 60 ? '#1565c0' : s >= 40 ? '#e65100' : '#888'
}

const score = computed(() => props.lead?.score ?? 0)
const scoreLabel = computed(() => (score.value >= 80 ? '🔥 Hot' : score.value >= 60 ? '⭐ Warm' : '💤 Cold'))
const isLost = computed(() => props.lead?.status === 'Lost' || props.lead?.status === 'Junk')

function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || '?'
}

const noteDraft = ref('')
function addNote() {
  const t = noteDraft.value.trim()
  if (!t || !props.lead) return
  ;(props.lead as unknown as Record<string, unknown>).notesList = [
    ...(((props.lead as unknown as Record<string, unknown>).notesList as unknown[]) ?? []),
    { text: t, by: 'You', when: 'just now' }
  ]
  noteDraft.value = ''
}
</script>

<template>
  <div v-if="lead" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 580px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0">
      <!-- HEADER -->
      <div class="lead-header" style="padding: 12px 14px; border-bottom: 1px solid #e8e8e8">
        <div style="display: flex; justify-content: space-between; align-items: flex-start">
          <div style="display: flex; gap: 10px; align-items: center">
            <div
              style="width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #2f80ed, #56ccf2); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700"
            >{{ initials(lead.name) }}</div>
            <div>
              <div style="margin-bottom: 3px; display: flex; gap: 4px; flex-wrap: wrap">
                <span class="lead-badge" :style="{ background: badgeColor(lead.type) + '15', color: badgeColor(lead.type), border: '1px solid ' + badgeColor(lead.type) }">{{ lead.type }}</span>
                <span class="lead-badge" :style="{ background: badgeColor(lead.status) + '15', color: badgeColor(lead.status), border: '1px solid ' + badgeColor(lead.status) }">{{ isLost ? lead.status.toUpperCase() : lead.status }}</span>
                <span v-if="lead.source" class="lead-badge" :style="{ background: badgeColor(lead.source) + '15', color: badgeColor(lead.source), border: '1px solid ' + badgeColor(lead.source) }">{{ lead.source }}</span>
                <span v-if="lead.priority === 'High'" class="lead-badge" style="background: #ffebee; color: #c62828; border: 1px solid #ffcdd2">🔥 HIGH</span>
              </div>
              <div style="font-size: 14px; font-weight: 700; color: #222">{{ lead.name }}</div>
              <div style="font-size: 11px; color: #2f80ed; margin-top: 1px">{{ lead.property || 'No property selected' }}</div>
            </div>
          </div>
          <span style="cursor: pointer; color: #999; font-size: 16px; padding: 3px" @click="emit('close')">✕</span>
        </div>
      </div>

      <!-- TABS -->
      <div style="display: flex; gap: 0; border-bottom: 1px solid #e8e8e8; padding: 0 8px; overflow-x: auto">
        <div
          v-for="t in tabs"
          :key="t.id"
          class="top-nav-item"
          :class="{ active: tab === t.id }"
          style="padding: 7px 10px; font-size: 10px; white-space: nowrap"
          @click="tab = t.id"
        >{{ t.label }}</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto; padding: 12px 14px">
        <!-- PROFILE -->
        <div v-if="tab === 'profile'">
          <div class="stats-row" style="grid-template-columns: 1fr 1fr">
            <div class="stat-card"><div class="label">📞 Phone</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.phone || '—' }}</div></div>
            <div class="stat-card"><div class="label">✉ Email</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.email || '—' }}</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">🎯 Target Value</div><div style="font-size: 16px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ lead.value || '—' }}</div></div>
            <div class="stat-card"><div class="label">📊 Lead Score</div><div style="font-size: 16px; font-weight: 700; margin-top: 2px; color: scoreColor(score)">{{ score }} / 100</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">👤 Owner</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.owner || '—' }}</div></div>
            <div class="stat-card"><div class="label">📅 Next Follow-up</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px; color: #e65100">{{ lead.follow_up || '—' }}</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">🏘 Property Interest</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px; color: #2f80ed">{{ lead.property || '—' }}</div></div>
            <div class="stat-card"><div class="label">📍 Source</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.source || '—' }}</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">📐 Size</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.sizeSqFt || '—' }}</div></div>
            <div class="stat-card"><div class="label">💰 Payment Plan</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.paymentPlan || '—' }}</div></div>
          </div>

          <!-- score bar -->
          <div style="margin-top: 8px">
            <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 4px">🔥 Lead Score</h3>
            <div style="height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden">
              <div :style="{ width: score + '%', background: scoreColor(score), height: '100%', borderRadius: '3px', transition: 'width .3s' }"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 8px; color: #999; margin-top: 2px">
              <span>{{ score }}/100</span><span>{{ scoreLabel }}</span>
            </div>
          </div>

          <!-- notes -->
          <div v-if="(lead as any).notes" style="margin-top: 8px">
            <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 4px">📝 Notes/Description</h3>
            <div class="stat-card" style="white-space: pre-wrap">{{ (lead as any).notes }}</div>
          </div>

          <div style="margin-top: 12px; display: flex; gap: 6px">
            <button class="action-btn primary" @click="emit('status', 'Booking')">✓ Mark Booking</button>
            <button class="action-btn" @click="emit('status', 'Site Visit')">📍 Site Visit</button>
            <button class="action-btn" @click="emit('status', 'Negotiation')">🤝 Negotiation</button>
            <button class="action-btn" style="color: #c62828" @click="emit('status', 'Lost')">✕ Lost</button>
          </div>
        </div>

        <!-- INSTALLMENTS / payments-ish (converted leads) -->
        <div v-else-if="tab === 'payments'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">💰 Installments / Payments</h3>
          <div v-if="(lead as any).installments?.length" class="installment-item" v-for="(ins, i) in (lead as any).installments" :key="i" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div>
              <div style="font-size: 11px; font-weight: 600">{{ ins.date }}</div>
            </div>
            <div style="text-align: right">
              <div style="font-size: 11px; font-weight: 600; color: #333">{{ ins.amount }}</div>
              <span class="lead-badge" :style="{ background: (ins.status === 'Paid' ? '#e8f5e9' : ins.status === 'Overdue' ? '#ffebee' : '#fff8e1'), color: (ins.status === 'Paid' ? '#2e7d32' : ins.status === 'Overdue' ? '#c62828' : '#e65100') }">{{ ins.status }}</span>
            </div>
          </div>
          <div v-if="!(lead as any).installments?.length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No payments recorded yet.</div>
        </div>

        <!-- ATTACHMENTS -->
        <div v-else-if="tab === 'attachments'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">📎 Attachments</h3>
          <div v-for="(doc, i) in (lead as any).documents || []" :key="i" class="doc-item" style="display: flex; align-items: center; gap: 8px; padding: 7px 0; border-bottom: 1px solid #f5f5f5">
            <span style="width: 28px; height: 28px; border-radius: 6px; background: #f0f4ff; display: flex; align-items: center; justify-content: center; font-size: 12px">📄</span>
            <div style="flex: 1">
              <div style="font-size: 11px; font-weight: 500; color: #333">{{ doc.name }}</div>
              <div style="font-size: 9px; color: #888">{{ doc.type }}</div>
            </div>
          </div>
          <div v-if="!((lead as any).documents || []).length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No attachments yet.</div>
        </div>

        <!-- ACTIVITIES -->
        <div v-else-if="tab === 'activities'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">📊 Activity Log</h3>
          <div v-for="(a, i) in (lead as any).activities || []" :key="i" style="display: flex; align-items: center; gap: 8px; padding: 7px 0; border-bottom: 1px solid #f5f5f5">
            <span style="font-size: 14px">{{ a.type === 'Call' ? '📞' : a.type === 'Meeting' ? '👥' : a.type === 'Note' ? '📝' : '📌' }}</span>
            <div style="flex: 1">
              <div style="font-size: 11px; color: #333">{{ a.text }}</div>
              <div style="font-size: 9px; color: #888">{{ a.user }} · {{ a.date }}</div>
            </div>
          </div>
          <div v-if="!((lead as any).activities || []).length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No activity yet.</div>
        </div>

        <!-- NOTES -->
        <div v-else-if="tab === 'notes'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">📝 Internal Notes</h3>
          <div style="padding: 6px 10px; background: #fff; border: 1px solid #e8e8e8; border-radius: 6px; margin-bottom: 8px">
            <textarea v-model="noteDraft" placeholder="Write a quick note..." style="width: 100%; border: none; outline: none; font-size: 11px; resize: vertical; min-height: 40px"></textarea>
            <button class="mini-btn" style="margin-top: 4px" @click="addNote">+ Add Note</button>
          </div>
          <div v-for="(n, i) in (lead as any).notesList || []" :key="i" style="padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div style="font-size: 11px; color: #333">{{ n.text }}</div>
            <div style="font-size: 9px; color: #888">{{ n.by }} · {{ n.when }}</div>
          </div>
          <div v-if="!((lead as any).notesList || []).length" style="text-align: center; padding: 20px; color: #999; font-size: 11px">No notes yet.</div>
        </div>

        <!-- Remaining tabs: simple empty states -->
        <div v-else style="text-align: center; padding: 36px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">
          {{ tab === 'proposals' ? '📋' : tab === 'tasks' ? '✅' : tab === 'reminders' ? '🔔' : '📄' }} No {{ tabs.find((t) => t.id === tab)?.label.toLowerCase() }} yet.
        </div>
      </div>

      <div class="drawer-footer">
        <button class="drawer-btn" @click="emit('close')">Close</button>
        <button class="drawer-btn primary" @click="emit('status', 'Booking')">✓ Mark Booking</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lead-badge {
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 8px;
  font-weight: 600;
  display: inline-block;
}
.mini-btn {
  padding: 3px 10px;
  font-size: 10px;
  border: 1px solid #2f80ed;
  color: #2f80ed;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}
.mini-btn:hover {
  background: #f0f4ff;
}
</style>
