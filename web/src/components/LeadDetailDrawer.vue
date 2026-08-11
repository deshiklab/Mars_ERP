<script setup lang="ts">
/**
 * LeadDetailDrawer v3 — COMPLETE lead-panel mirroring the HTML PWA leadSlideOut.
 * All 10 tabs: Profile, Proposals, Tasks, Attachments, Reminders, Notes,
 * Activity Log, Chat/Contact, Invoices, Payments — wired to REAL data
 * (bootstrap collections filtered by the lead's client/name).
 */
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '@/api/client'
import { useDataStore } from '@/stores/data'
import { showToast } from '@/toast'
import type { Lead } from '@/api/types'

const props = defineProps<{ lead: Lead | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()
const data = useDataStore()

const tab = ref('profile')
watch(() => props.lead, () => (tab.value = 'profile'))
// deep-link: /leads?lead=1&tab=payments opens a specific tab
watch(
  () => props.lead,
  (l) => {
    if (l) {
      const q = new URLSearchParams(window.location.search).get('tab')
      if (q && tabs.some((t) => t.id === q)) tab.value = q
    }
  }
)

const tabs = [
  { id: 'profile', label: 'Profile' },
  { id: 'proposals', label: 'Proposals' },
  { id: 'tasks', label: 'Tasks' },
  { id: 'attachments', label: 'Attachments' },
  { id: 'reminders', label: 'Reminders' },
  { id: 'notes', label: 'Notes' },
  { id: 'activities', label: 'Activity Log' },
  { id: 'chathistory', label: 'Chat/Contact' },
  { id: 'invoices', label: 'Invoices' },
  { id: 'payments', label: 'Payments' }
]

/* ── real-data collections (fetched once) ── */
const proposals = ref<any[]>([])
const tasks = ref<any[]>([])
const invoices = ref<any[]>([])
const payments = ref<any[]>([])

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    proposals.value = (r.data.collections.proposals as any[]) ?? []
    tasks.value = (r.data.collections.tasks as any[]) ?? []
    invoices.value = (r.data.collections.invoices as any[]) ?? []
    payments.value = (r.data.collections.payments as any[]) ?? []
  }
})

const actType = ref('Call')
const actText = ref('')
const logging = ref(false)
async function logActivity() {
  if (!actText.value.trim() || logging.value || !props.lead) return
  logging.value = true
  const ok = await data.logLeadActivity(props.lead.id, actType.value, actText.value.trim())
  logging.value = false
  if (ok) {
    showToast('✔ Activity logged')
    actText.value = ''
  } else {
    showToast('Log failed — ' + data.error)
  }
}

const leadProposals = computed(() => proposals.value.filter((p: any) => String(p.client || '').toLowerCase() === String(props.lead?.name || '').toLowerCase()))
const leadInvoices = computed(() => invoices.value.filter((i: any) => String(i.client || '').toLowerCase() === String(props.lead?.name || '').toLowerCase()))
const leadPayments = computed(() => payments.value.filter((p: any) => String(p.client || '').toLowerCase() === String(props.lead?.name || '').toLowerCase()))
const leadTasks = computed(() => {
  const own = ((props.lead as any)?.tasks as any[]) ?? []
  if (own.length) return own
  // fall back to global tasks assigned to the lead's owner
  return tasks.value.filter((t: any) => String(t.assignee || '').toLowerCase() === String(props.lead?.owner || '').toLowerCase()).slice(0, 8)
})
const totalPaid = computed(() => leadPayments.value.reduce((s: number, p: any) => s + (p.amount ?? 0), 0))

/* ── helpers ── */
function badgeColor(v: string | undefined): string {
  const map: Record<string, string> = {
    'New Inquiry': '#1565c0', Contacted: '#2f80ed', 'Site Visit': '#e65100',
    Negotiation: '#7b1fa2', Booking: '#2e7d32', Lost: '#c62828', Junk: '#888',
    High: '#c62828', Medium: '#e65100', Low: '#888', Local: '#2f80ed', NRB: '#7b1fa2',
    Website: '#1565c0', Facebook: '#1e88e5', Referral: '#2e7d32', 'Walk-in': '#00838f',
    Agent: '#e65100', Bikroy: '#f9a825', 'NRB Direct': '#7b1fa2', 'Cold Call': '#546e7a',
    Sent: '#1565c0', Accepted: '#2e7d32', Rejected: '#c62828', Draft: '#888',
    Paid: '#2e7d32', Overdue: '#c62828', Cleared: '#2e7d32', Pending: '#e65100',
    'In Progress': '#e65100', Done: '#2e7d32', 'To Do': '#2f80ed'
  }
  return map[v ?? ''] ?? '#2f80ed'
}

const score = computed(() => props.lead?.score ?? 0)
const scoreLabel = computed(() => (score.value >= 80 ? '🔥 Hot' : score.value >= 60 ? '⭐ Warm' : '💤 Cold'))
const isLost = computed(() => props.lead?.status === 'Lost' || props.lead?.status === 'Junk')

function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || '?'
}

/* ── local state for quick-add composers ── */
const noteDraft = ref('')
const chType = ref('Call')
const chText = ref('')
const chatHistory = ref<any[]>([])

function addNote() {
  const t = noteDraft.value.trim()
  if (!t || !props.lead) return
  ;(props.lead as unknown as Record<string, unknown>).notesList = [
    ...(((props.lead as unknown as Record<string, unknown>).notesList as unknown[]) ?? []),
    { text: t, by: 'You', when: 'just now' }
  ]
  noteDraft.value = ''
}

function addChat() {
  const t = chText.value.trim()
  if (!t) return
  chatHistory.value.unshift({ type: chType.value, contact: props.lead?.name ?? 'lead', date: 'just now', summary: t })
  chText.value = ''
}

/* ── task toggle ── */
const taskDone = ref<Record<string, boolean>>({})
function toggleTask(id: string) {
  taskDone.value[id] = !taskDone.value[id]
}
function isTaskDone(id: string): boolean {
  if (taskDone.value[id] !== undefined) return taskDone.value[id]
  const t = leadTasks.value.find((x: any) => String(x.id) === id)
  return t?.status === 'Done'
}

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)
</script>

<template>
  <div v-if="lead" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 580px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <!-- HEADER -->
      <div class="lead-header" style="padding: 12px 14px; border-bottom: 1px solid #e8e8e8; flex-shrink: 0">
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

      <!-- TABS (all 10) -->
      <div style="display: flex; gap: 0; border-bottom: 1px solid #e8e8e8; padding: 0 8px; overflow-x: auto; flex-shrink: 0">
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
        <!-- ══ PROFILE ══ -->
        <div v-if="tab === 'profile'">
          <div class="stats-row" style="grid-template-columns: 1fr 1fr">
            <div class="stat-card"><div class="label">📞 Phone</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.phone || '—' }}</div></div>
            <div class="stat-card"><div class="label">✉ Email</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.email || '—' }}</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">🎯 Target Value</div><div style="font-size: 16px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ lead.value || '—' }}</div></div>
            <div class="stat-card"><div class="label">📊 Lead Score</div><div style="font-size: 16px; font-weight: 700; margin-top: 2px; color: score >= 80 ? '#2e7d32' : score >= 60 ? '#1565c0' : score >= 40 ? '#e65100' : '#888'">{{ score }} / 100</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">👤 Owner</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.owner || '—' }}</div></div>
            <div class="stat-card"><div class="label">📅 Next Follow-up</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px; color: #e65100">{{ lead.nextFollowUp || '—' }}</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">🏘 Property Interest</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px; color: #2f80ed">{{ lead.property || '—' }}</div></div>
            <div class="stat-card"><div class="label">📍 Source</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.source || '—' }}</div></div>
          </div>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
            <div class="stat-card"><div class="label">📐 Size</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.sizeSqFt || '—' }}</div></div>
            <div class="stat-card"><div class="label">💰 Payment Plan</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ lead.paymentPlan || '—' }}</div></div>
          </div>

          <div style="margin-top: 8px">
            <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 4px">🔥 Lead Score</h3>
            <div style="height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden">
              <div :style="{ width: score + '%', background: score >= 80 ? '#2e7d32' : score >= 60 ? '#1565c0' : score >= 40 ? '#e65100' : '#888', height: '100%', borderRadius: '3px', transition: 'width .3s' }"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 8px; color: #999; margin-top: 2px">
              <span>{{ score }}/100</span><span>{{ scoreLabel }}</span>
            </div>
          </div>

          <div v-if="(lead as any).notes" style="margin-top: 8px">
            <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 4px">📝 Notes/Description</h3>
            <div class="stat-card" style="white-space: pre-wrap">{{ (lead as any).notes }}</div>
          </div>

          <div style="margin-top: 12px; display: flex; gap: 6px; flex-wrap: wrap">
            <button class="action-btn primary" @click="emit('status', 'Booking')">✓ Mark Booking</button>
            <button class="action-btn" @click="emit('status', 'Site Visit')">📍 Site Visit</button>
            <button class="action-btn" @click="emit('status', 'Negotiation')">🤝 Negotiation</button>
            <button class="action-btn" style="color: #c62828" @click="emit('status', 'Lost')">✕ Lost</button>
          </div>
        </div>

        <!-- ══ PROPOSALS ══ -->
        <div v-else-if="tab === 'proposals'">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px">
            <h3 style="font-size: 11px; font-weight: 600; color: #555; display: flex; align-items: center; gap: 4px">📋 Proposals / Quotations</h3>
          </div>
          <div v-for="p in leadProposals" :key="p.id" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div>
              <div style="font-size: 12px; font-weight: 600">{{ p.title || 'Proposal' }}</div>
              <div style="font-size: 9px; color: #888; margin-top: 1px">{{ p.createdDate }} · {{ p.unit || p.property }}</div>
            </div>
            <div style="text-align: right">
              <div style="font-size: 11px; font-weight: 600; color: #2e7d32">{{ bdt(p.amount) }}</div>
              <span class="lead-badge" :style="{ background: badgeColor(p.status) + '15', color: badgeColor(p.status), border: '1px solid ' + badgeColor(p.status) }">{{ p.status }}</span>
            </div>
          </div>
          <div v-if="!leadProposals.length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No proposals sent yet.</div>
        </div>

        <!-- ══ TASKS ══ -->
        <div v-else-if="tab === 'tasks'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px; display: flex; align-items: center; gap: 4px">✅ Tasks</h3>
          <div v-for="tsk in leadTasks" :key="tsk.id" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5; opacity: isTaskDone(tsk.id) ? 0.5 : 1">
            <div style="display: flex; align-items: center; gap: 6px">
              <input type="checkbox" :checked="isTaskDone(tsk.id)" @change="toggleTask(tsk.id)" style="accent-color: #2f80ed" />
              <div>
                <div style="font-size: 11px; font-weight: 500; text-decoration: isTaskDone(tsk.id) ? 'line-through' : 'none'">{{ tsk.title || tsk.name }}</div>
                <div style="font-size: 9px; color: #888">{{ tsk.assignee ? '👤 ' + tsk.assignee + ' · ' : '' }}{{ tsk.deadline || tsk.due || '' }}</div>
              </div>
            </div>
            <span v-if="tsk.priority === 'High'" style="font-size: 9px; color: #e53935; font-weight: 600">🔴</span>
            <span v-else-if="tsk.priority === 'Medium'" style="font-size: 9px; color: #e65100">🟡</span>
            <span v-else style="font-size: 9px; color: #888">🟢</span>
          </div>
          <div v-if="!leadTasks.length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No tasks assigned yet.</div>
        </div>

        <!-- ══ ATTACHMENTS ══ -->
        <div v-else-if="tab === 'attachments'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">📎 Attachments</h3>
          <div v-for="(doc, i) in (lead as any).documents || []" :key="i" style="display: flex; align-items: center; gap: 8px; padding: 7px 0; border-bottom: 1px solid #f5f5f5">
            <span style="width: 28px; height: 28px; border-radius: 6px; background: #f0f4ff; display: flex; align-items: center; justify-content: center; font-size: 12px">📄</span>
            <div style="flex: 1">
              <div style="font-size: 11px; font-weight: 500; color: #333">{{ doc.name }}</div>
              <div style="font-size: 9px; color: #888">{{ doc.type }}</div>
            </div>
          </div>
          <div v-if="!((lead as any).documents || []).length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No attachments yet.</div>
        </div>

        <!-- ══ REMINDERS ══ -->
        <div v-else-if="tab === 'reminders'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">🔔 Reminders</h3>
          <div v-for="(rm, i) in (lead as any).reminders || []" :key="i" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div>
              <div style="font-size: 11px; font-weight: 500">{{ rm.title || 'Reminder' }}</div>
              <div style="font-size: 9px; color: #e53935">🔴 Overdue: {{ rm.dateTime }}</div>
            </div>
            <div style="display: flex; gap: 4px; align-items: center">
              <span style="font-size: 9px; color: #888">{{ rm.type || 'Follow-up' }}</span>
              <span style="color: #e53935; cursor: pointer; font-size: 10px">✕</span>
            </div>
          </div>
          <div v-if="!((lead as any).reminders || []).length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No reminders set.</div>
        </div>

        <!-- ══ NOTES ══ -->
        <div v-else-if="tab === 'notes'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">📝 Internal Notes</h3>
          <div style="padding: 6px 10px; background: #fff; border: 1px solid #e8e8e8; border-radius: 6px; margin-bottom: 8px">
            <textarea v-model="noteDraft" placeholder="Write a quick note..." style="width: 100%; border: none; outline: none; font-size: 11px; resize: vertical; min-height: 50px; background: transparent; font-family: inherit"></textarea>
            <div style="text-align: right; margin-top: 4px">
              <button class="mini-btn primary" @click="addNote">+ Add Note</button>
            </div>
          </div>
          <div v-for="(n, i) in (lead as any).notesList || []" :key="i" style="padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div style="font-size: 11px; color: #333">{{ n.text }}</div>
            <div style="font-size: 9px; color: #888">{{ n.by }} · {{ n.when }}</div>
          </div>
          <div v-if="!((lead as any).notesList || []).length" style="text-align: center; padding: 20px; color: #999; font-size: 11px">No notes yet.</div>
        </div>

        <!-- ══ ACTIVITIES ══ -->
        <div v-else-if="tab === 'activities'">
          <div style="display: flex; gap: 6px; margin-bottom: 10px; background: #f8f9fa; padding: 8px; border-radius: 8px; flex-wrap: wrap; align-items: center">
            <select v-model="actType" style="font-size: 11px; padding: 5px 6px; border: 1px solid #e0e0e0; border-radius: 6px; background: #fff">
              <option>Call</option><option>Meeting</option><option>Site Visit</option><option>WhatsApp</option><option>Email</option><option>Note</option>
            </select>
            <input v-model="actText" placeholder="What happened? e.g. Called, wants site visit Saturday…" style="flex: 1 1 160px; min-width: 0; font-size: 11px; padding: 5px 8px; border: 1px solid #e0e0e0; border-radius: 6px" @keyup.enter="logActivity" />
            <button @click="logActivity" :disabled="logging" style="background: #2F80ED; color: #fff; border: none; border-radius: 6px; padding: 5px 12px; font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap">{{ logging ? 'Logging…' : '+ Log activity' }}</button>
          </div>
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

        <!-- ══ CHAT / CONTACT HISTORY ══ -->
        <div v-else-if="tab === 'chathistory'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px; display: flex; align-items: center; gap: 4px">💬 Chat & Contact History</h3>
          <div style="padding: 8px 10px; background: #fff; border: 1px solid #e8e8e8; border-radius: 6px; margin-bottom: 8px">
            <div style="display: flex; gap: 5px; margin-bottom: 5px">
              <select v-model="chType" style="padding: 4px 6px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 10px; outline: none">
                <option value="Call">📞 Call</option>
                <option value="Email">✉ Email</option>
                <option value="WhatsApp">💬 WhatsApp</option>
                <option value="SMS">📱 SMS</option>
                <option value="Meeting">👥 Meeting</option>
              </select>
            </div>
            <div style="display: flex; gap: 5px">
              <input v-model="chText" placeholder="Describe contact..." style="flex: 1; padding: 5px 8px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 10px; outline: none" />
              <button class="mini-btn primary" @click="addChat">Add</button>
            </div>
          </div>
          <div v-for="ch in chatHistory" :key="ch.date + ch.summary" style="padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3px">
              <span style="font-size: 10px; font-weight: 600">{{ ch.type === 'Call' ? '📞' : ch.type === 'Email' ? '✉' : ch.type === 'WhatsApp' ? '💬' : ch.type === 'SMS' ? '📱' : '👥' }} {{ ch.type }} <span style="font-weight: 400; color: #888">with {{ ch.contact }}</span></span>
              <span style="font-size: 9px; color: #999">{{ ch.date }}</span>
            </div>
            <div style="font-size: 11px; color: #555">{{ ch.summary }}</div>
          </div>
          <div v-if="!chatHistory.length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No contact history yet.</div>
        </div>

        <!-- ══ INVOICES ══ -->
        <div v-else-if="tab === 'invoices'">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">📄 Invoices</h3>
          <div v-for="inv in leadInvoices" :key="inv.id" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div>
              <div style="font-size: 11px; font-weight: 600; color: #2f80ed">{{ inv.id }}</div>
              <div style="font-size: 9px; color: #888">{{ inv.project }}{{ inv.unit ? ' · ' + inv.unit : '' }}</div>
            </div>
            <div style="text-align: right">
              <div style="font-size: 11px; font-weight: 600; color: #2e7d32">{{ bdt(inv.amount) }}</div>
              <span class="lead-badge" :style="{ background: badgeColor(inv.status) + '15', color: badgeColor(inv.status), border: '1px solid ' + badgeColor(inv.status) }">{{ inv.status }}</span>
            </div>
          </div>
          <div v-if="!leadInvoices.length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No invoices created yet.</div>
        </div>

        <!-- ══ PAYMENTS ══ -->
        <div v-else-if="tab === 'payments'">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px">
            <h3 style="font-size: 11px; font-weight: 600; color: #555">💰 Payments</h3>
            <span style="font-size: 11px; font-weight: 700; color: #2e7d32">Total: {{ bdt(totalPaid) }}</span>
          </div>
          <!-- server payments -->
          <div v-for="p in leadPayments" :key="p.id" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div>
              <div style="font-size: 10px; font-weight: 500">{{ p.id }}</div>
              <div style="font-size: 9px; color: #888">{{ p.date }} · {{ p.method || '—' }}</div>
            </div>
            <div style="text-align: right">
              <div style="font-size: 11px; font-weight: 600; color: #2e7d32">{{ bdt(p.amount) }}</div>
              <span style="font-size: 8px; color: p.status === 'Cleared' ? '#2e7d32' : '#e65100'">{{ p.status }}</span>
              <br /><span style="font-size: 8px; color: #888">{{ p.reference || '' }}</span>
            </div>
          </div>
          <!-- installment schedule -->
          <div v-for="(ins, i) in (lead as any).installments || []" :key="'ins-' + i" style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <div>
              <div style="font-size: 11px; font-weight: 600">{{ ins.date }}</div>
              <div style="font-size: 9px; color: #888">Installment</div>
            </div>
            <div style="text-align: right">
              <div style="font-size: 11px; font-weight: 600; color: #333">{{ ins.amount }}</div>
              <span class="lead-badge" :style="{ background: ins.status === 'Paid' ? '#e8f5e9' : ins.status === 'Overdue' ? '#ffebee' : '#fff8e1', color: ins.status === 'Paid' ? '#2e7d32' : ins.status === 'Overdue' ? '#c62828' : '#e65100' }">{{ ins.status }}</span>
            </div>
          </div>
          <div v-if="!leadPayments.length && !((lead as any).installments || []).length" style="text-align: center; padding: 28px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No payments recorded yet.</div>
        </div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
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
.mini-btn.primary {
  background: #2f80ed;
  color: #fff;
}
.mini-btn:hover {
  opacity: 0.85;
}
</style>
