<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import KanbanBoard from '@/components/KanbanBoard.vue'
import StatsRow from '@/components/StatsRow.vue'
import LeadDetailDrawer from '@/components/LeadDetailDrawer.vue'
import type { TableAction, TableColumn, TableTab } from '@/components/DataTable.vue'
import type { KanbanCard, KanbanColumn } from '@/components/KanbanBoard.vue'
import type { Lead } from '@/api/types'
import { _t } from '@/i18n'

const data = useDataStore()
const route = useRoute()
const statusFilter = ref('')
const viewMode = ref<'table' | 'kanban'>(route.query.view === 'kanban' ? 'kanban' : 'table')
const showAddDrawer = ref(false)
const detailLead = ref<Lead | null>(null)
const newLead = ref({ name: '', email: '', phone: '', source: 'Website', priority: 'Medium' })

onMounted(() => {
  data.loadLeads()
})

const statusOptions = ['New Inquiry', 'Contacted', 'Site Visit', 'Negotiation', 'Booking', 'Lost']
const sources = ['Website', 'Facebook', 'Referral', 'Walk-in', 'Agent', 'Bikroy', 'NRB Direct', 'Cold Call']

function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    'New Inquiry': ['#e3f2fd', '#1565c0'],
    Contacted: ['#f0f4ff', '#2f80ed'],
    'Site Visit': ['#fff3e0', '#e65100'],
    Negotiation: ['#fff8e1', '#ff8f00'],
    Booking: ['#e8f5e9', '#2e7d32'],
    Lost: ['#ffebee', '#c62828']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

function priorityColor(p: string): string {
  return p === 'High' ? '#c62828' : p === 'Medium' ? '#e65100' : '#888'
}

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

/* ── stats row ── */
const leadStats = computed(() => [
  { label: _t('Total Leads'), value: String(data.leads.length), color: '#2f80ed' },
  { label: _t('New Inquiry'), value: String(data.leads.filter((l) => l.status === 'New Inquiry').length), color: '#1565c0' },
  { label: _t('Site Visit'), value: String(data.leads.filter((l) => l.status === 'Site Visit').length), color: '#e65100' },
  { label: _t('Negotiation'), value: String(data.leads.filter((l) => l.status === 'Negotiation').length), color: '#ff8f00' },
  { label: _t('Booking'), value: String(data.leads.filter((l) => l.status === 'Booking').length), color: '#2e7d32' },
  { label: _t('Lost'), value: String(data.leads.filter((l) => l.status === 'Lost').length), color: '#c62828' }
])

/* ── table ── */
const columns = computed<TableColumn<Lead>[]>(() => [
  {
    key: 'name',
    label: 'Lead',
    renderHtml: (l) =>
      `<div style="font-weight:500;color:#333">${esc(l.name)}</div><div style="font-size:9px;color:#888">${esc(l.email)} · ${esc(l.phone)}</div>`
  },
  {
    key: 'source',
    label: 'Source',
    renderHtml: (l) =>
      `<span style="display:inline-flex;align-items:center;gap:3px;padding:1px 6px;border-radius:8px;background:#f0f4ff;color:#2f80ed;font-weight:600">${esc(l.source)}</span>`
  },
  {
    key: 'priority',
    label: 'Priority',
    sortable: true,
    renderHtml: (l) => `<span style="font-weight:600;font-size:10px;color:${priorityColor(l.priority)}">${esc(l.priority)}</span>`
  },
  {
    key: 'score',
    label: 'Score',
    sortable: true,
    renderHtml: (l) =>
      `<span style="display:inline-flex;padding:1px 5px;border-radius:4px;font-size:9px;font-weight:600;background:#eef3ff;color:#2f80ed">${l.score ?? '—'}</span>`
  },
  {
    key: 'follow_up',
    label: 'Follow-up',
    renderHtml: (l) => `<span style="font-size:9px;font-weight:500;color:#888">${esc(l.follow_up ?? '—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (l) => {
      const s = statusStyle(l.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(l.status)}</span>`
    }
  }
])

const tabs = computed<TableTab[]>(() => [
  { id: 'all', label: 'All', count: data.leads.length },
  { id: 'new', label: 'New', count: data.leads.filter((l) => l.status === 'New Inquiry').length },
  { id: 'visit', label: 'Site Visit', count: data.leads.filter((l) => l.status === 'Site Visit').length },
  { id: 'booking', label: 'Booking', count: data.leads.filter((l) => l.status === 'Booking').length },
  { id: 'lost', label: 'Lost', count: data.leads.filter((l) => l.status === 'Lost').length }
])

const tabRows = computed(() => {
  if (!statusFilter.value || statusFilter.value === 'all') return data.leads
  const map: Record<string, string> = { new: 'New Inquiry', visit: 'Site Visit', booking: 'Booking', lost: 'Lost' }
  const st = map[statusFilter.value]
  return st ? data.leads.filter((l) => l.status === st) : data.leads
})

function onTabChange(tab: string) {
  statusFilter.value = tab
}

const actions = computed<TableAction[]>(() => [
  { label: 'View Details', icon: '👁', onClick: (r) => (detailLead.value = r as unknown as Lead) },
  { label: 'Mark Site Visit', icon: '📍', onClick: (r) => setStatus((r as unknown as Lead).id, 'Site Visit') },
  { label: 'Mark Negotiation', icon: '🤝', onClick: (r) => setStatus((r as unknown as Lead).id, 'Negotiation') },
  { label: 'Mark Booking', icon: '✅', onClick: (r) => setStatus((r as unknown as Lead).id, 'Booking') },
  { label: 'Mark Lost', icon: '❌', onClick: (r) => setStatus((r as unknown as Lead).id, 'Lost') },
  { label: 'Delete', icon: '🗑', onClick: (r) => console.log('delete', (r as unknown as Lead).id) }
])

/* ── kanban ── */
const kanbanCols: KanbanColumn[] = [
  { id: 'New Inquiry', label: 'New Inquiry', bg: '#e3f2fd', fg: '#1565c0', next: 'Contacted' },
  { id: 'Contacted', label: 'Contacted', bg: '#f0f4ff', fg: '#2f80ed', next: 'Site Visit' },
  { id: 'Site Visit', label: 'Site Visit', bg: '#fff3e0', fg: '#e65100', next: 'Negotiation' },
  { id: 'Negotiation', label: 'Negotiation', bg: '#fff8e1', fg: '#ff8f00', next: 'Booking' },
  { id: 'Booking', label: 'Booking', bg: '#e8f5e9', fg: '#2e7d32' },
  { id: 'Lost', label: 'Lost', bg: '#ffebee', fg: '#c62828' }
]

const kanbanCards = computed<KanbanCard[]>(() =>
  data.leads.map((l) => ({
    id: l.id,
    title: l.name,
    subtitle: l.email || l.phone,
    meta: `${l.source} · ${l.follow_up ?? ''}`,
    status: l.status,
    pills: [
      { text: String(l.score ?? ''), color: l.score >= 50 ? '#2e7d32' : l.score >= 25 ? '#e65100' : '#888' },
      { text: l.priority, color: priorityColor(l.priority) }
    ]
  }))
)

async function kanbanMove(cardId: string, status: string) {
  await setStatus(cardId, status)
}

async function setStatus(id: string, status: string) {
  await data.updateLeadStatus(id, status)
}

function openAddDrawer() {
  newLead.value = { name: '', email: '', phone: '', source: 'Website', priority: 'Medium' }
  showAddDrawer.value = true
}

async function saveLead() {
  if (!newLead.value.name.trim()) {
    data.error = 'Lead name is required'
    return
  }
  showAddDrawer.value = false
  data.error = ''
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">{{ _t('CRM & Leads') }}</span>
      <span class="page-subtitle">{{ data.leads.length }} leads · server-synced</span>
      <div style="margin-left: auto; display: flex; gap: 6px">
        <div style="display: flex; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden">
          <button
            class="action-btn"
            :style="{ border: 'none', borderRadius: 0, background: viewMode === 'table' ? '#f0f4ff' : '#fff', color: '#2f80ed' }"
            @click="viewMode = 'table'"
          >☰ Table</button>
          <button
            class="action-btn"
            :style="{ border: 'none', borderRadius: 0, borderLeft: '1px solid #e0e0e0', background: viewMode === 'kanban' ? '#f0f4ff' : '#fff', color: '#2f80ed' }"
            @click="viewMode = 'kanban'"
          >▤ Kanban</button>
        </div>
        <button class="action-btn primary" @click="openAddDrawer">+ Add Lead</button>
      </div>
    </div>

    <!-- STATS ROW -->
    <StatsRow :stats="leadStats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.leadsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading leads…</p>

    <template v-else>
      <!-- TABLE VIEW -->
      <DataTable
        v-if="viewMode === 'table'"
        :columns="columns"
        :rows="tabRows"
        :tabs="tabs"
        :actions="actions"
        search-placeholder="Search leads, source, status…"
        @tab-change="onTabChange"
      />

      <!-- KANBAN VIEW -->
      <div v-else class="card" style="padding: 8px">
        <KanbanBoard
          :columns="kanbanCols"
          :cards="kanbanCards"
          @move="kanbanMove"
          @edit="openAddDrawer"
          @delete="(c) => console.log('delete', c.id)"
        />
      </div>
    </template>

    <!-- Lead detail drawer -->
    <LeadDetailDrawer :lead="detailLead" @close="detailLead = null" @status="(st: string) => detailLead && setStatus(detailLead.id, st)" />

    <!-- Add-lead drawer -->
    <div v-if="showAddDrawer" class="drawer-overlay active">
      <div class="drawer-sheet">
        <div class="drawer-header">
          <h3>Add Lead</h3>
          <div class="drawer-close" @click="showAddDrawer = false">✕</div>
        </div>
        <div class="drawer-body">
          <div class="form-group">
            <label class="form-label">Full name *</label>
            <input v-model="newLead.name" class="form-input" placeholder="e.g. Rahman Khan" />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="newLead.email" type="email" class="form-input" placeholder="rahman@example.com" />
          </div>
          <div class="form-group">
            <label class="form-label">Phone</label>
            <input v-model="newLead.phone" class="form-input" placeholder="+880 1XXX-XXXXXX" />
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px">
            <div class="form-group">
              <label class="form-label">Source</label>
              <select v-model="newLead.source" class="form-input">
                <option v-for="s in sources" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Priority</label>
              <select v-model="newLead.priority" class="form-input">
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
        </div>
        <div class="drawer-footer">
          <button class="drawer-btn" @click="showAddDrawer = false">Cancel</button>
          <button class="drawer-btn primary" @click="saveLead">Save Lead</button>
        </div>
      </div>
    </div>
  </div>
</template>
