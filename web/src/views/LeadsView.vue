<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import type { TableColumn, TableAction, TableTab } from '@/components/DataTable.vue'
import type { Lead } from '@/api/types'

const data = useDataStore()
const statusFilter = ref('')
const showAddDrawer = ref(false)
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
  { label: 'View Details', icon: '👁', onClick: () => {} },
  { label: 'Mark Site Visit', icon: '📍', onClick: (r) => setStatus(r as unknown as Lead, 'Site Visit') },
  { label: 'Mark Negotiation', icon: '🤝', onClick: (r) => setStatus(r as unknown as Lead, 'Negotiation') },
  { label: 'Mark Booking', icon: '✅', onClick: (r) => setStatus(r as unknown as Lead, 'Booking') },
  { label: 'Mark Lost', icon: '❌', onClick: (r) => setStatus(r as unknown as Lead, 'Lost') },
  { label: 'Delete', icon: '🗑', onClick: (r) => console.log('delete', (r as unknown as Lead).id) }
])

async function setStatus(l: Lead, status: string) {
  await data.updateLeadStatus(l.id, status)
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
      <span class="page-title">CRM & Leads</span>
      <span class="page-subtitle">{{ data.leads.length }} leads · server-synced</span>
      <div style="margin-left: auto">
        <button class="action-btn primary" @click="openAddDrawer">+ Add Lead</button>
      </div>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.leadsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading leads…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="tabRows"
      :tabs="tabs"
      :actions="actions"
      search-placeholder="Search leads, source, status…"
      @tab-change="onTabChange"
    />

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
