<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import { api } from '@/api/client'
import { showToast } from '@/toast'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

onMounted(() => {
  data.loadTickets()
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function statusColor(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Active: ['#e8f5e9', '#2e7d32'],
    Available: ['#e8f5e9', '#2e7d32'],
    Approved: ['#e8f5e9', '#2e7d32'],
    Completed: ['#e8f5e9', '#2e7d32'],
    'Handed Over': ['#e3f2fd', '#1565c0'],
    Resolved: ['#e8f5e9', '#2e7d32'],
    Closed: ['#e8f5e9', '#2e7d32'],
    Paid: ['#e8f5e9', '#2e7d32'],
    Inactive: ['#f0f0f0', '#555'],
    Pending: ['#fff8e1', '#ff8f00'],
    'In Progress': ['#fff3e0', '#e65100'],
    Open: ['#ffebee', '#c62828'],
    'In Service': ['#fff3e0', '#e65100'],
    Maintenance: ['#fff3e0', '#e65100'],
    'On Leave': ['#fff3e0', '#e65100'],
    Booked: ['#fff3e0', '#e65100'],
    'On Hold': ['#fff3e0', '#e65100'],
    Rejected: ['#ffebee', '#c62828'],
    Canceled: ['#ffebee', '#c62828']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

function prioColor(p: string): string {
  return p === 'High' ? '#c62828' : p === 'Medium' ? '#e65100' : '#888'
}

const stats = computed(() => [
  { label: 'Tickets', value: String(data.tickets.length), color: '#2f80ed' },
  { label: 'Open', value: String(data.tickets.filter(t=>t.status==='Open').length), color: '#e65100' },
  { label: 'Resolved', value: String(data.tickets.filter(t=>t.status==='Resolved'||t.status==='Closed').length), color: '#2e7d32' }
])

const actBusy = ref(false)
async function tktAct(id: string, status: string, ev?: MouseEvent) {
  if (ev) ev.stopPropagation()
  if (actBusy.value) return
  const t = data.tickets.find((x) => x.id === id)
  if (!t) return
  actBusy.value = true
  try {
    const r = await api.call('tickets_sync', { tickets: [{ id: '', subject: String(t.subject ?? ''), customer: String(t.customer ?? ''), status, priority: String(t.priority ?? 'Medium'), type: String(t.type ?? 'Enquiry') }] })
    if (r.ok) {
      t.status = status
      showToast(`Ticket ${status}`)
      await data.loadTickets()
    } else showToast('Update failed', 'error')
  } finally { actBusy.value = false }
}
;(window as unknown as { __tktAct: (id: string, s: string, e?: MouseEvent) => void }).__tktAct = tktAct
const showNew = ref(false)
const nf = ref({ subject: '', customer: '', type: 'Enquiry', priority: 'Medium', desc: '' })
const nfBusy = ref(false)
async function createTicket() {
  if (!nf.value.subject.trim() || !nf.value.customer.trim()) { showToast('Subject and customer are required', 'error'); return }
  nfBusy.value = true
  try {
    const r = await api.call('tickets_sync', { tickets: [{ id: '', subject: nf.value.subject.trim(), customer: nf.value.customer.trim(), type: nf.value.type, priority: nf.value.priority, desc: nf.value.desc.trim(), status: 'Open' }] })
    if (r.ok) { showToast('Ticket created'); showNew.value = false; nf.value = { subject: '', customer: '', type: 'Enquiry', priority: 'Medium', desc: '' }; await data.loadTickets() }
    else showToast('Create failed', 'error')
  } finally { nfBusy.value = false }
}
const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'subject',
    label: 'Subject',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.subject)}</div><div style='font-size:9px;color:#888'>${esc(x.project||'')} · ${esc(x.type||'')}</div>`
  },
  {
    key: 'customer',
    label: 'Customer',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.customer||'—')}</span>`
  },
  {
    key: 'priority',
    label: 'Priority',
    sortable: true,
    renderHtml: (x) => `<span style='font-weight:600;font-size:10px;color:${prioColor(x.priority)}'>${esc(x.priority||'—')}</span>`
  },
  {
    key: 'date',
    label: 'Date',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.date||'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = x.status || '—'
      let acts = ''
      if (s === 'Open') acts = ` <button style="border:0;background:#1565c0;color:#fff;font-size:9px;border-radius:6px;padding:2px 6px;cursor:pointer" onclick="event.stopPropagation();window.__tktAct('${x.id}','Replied',event)">⚙ Start</button> <button style="border:0;background:#2e7d32;color:#fff;font-size:9px;border-radius:6px;padding:2px 6px;cursor:pointer" onclick="event.stopPropagation();window.__tktAct('${x.id}','Resolved',event)">✓ Resolve</button>`
      else if (s === 'Replied') acts = ` <button style="border:0;background:#2e7d32;color:#fff;font-size:9px;border-radius:6px;padding:2px 6px;cursor:pointer" onclick="event.stopPropagation();window.__tktAct('${x.id}','Resolved',event)">✓ Resolve</button>`
      else if (s === 'Resolved') acts = ` <button style="border:0;background:#455a64;color:#fff;font-size:9px;border-radius:6px;padding:2px 6px;cursor:pointer" onclick="event.stopPropagation();window.__tktAct('${x.id}','Closed',event)">✔ Close</button>`
      return `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(s)}</span>${acts}`
    }
  },])

const rows = computed(() => data.tickets)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Ticketing & Issue</span>
      <span class="page-subtitle">{{ data.tickets.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <div style="display: flex; align-items: center; gap: 8px; margin: 8px 0">
      <button class="btn-ghost" style="font-size: 11px" @click="showNew = true">➕ New Ticket</button>
    </div>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search tickets…"
    />
  </div>
    <div v-if="showNew" class="drawer-overlay active" @click.self="showNew = false">
      <div class="drawer-sheet" style="width: 460px">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px">
          <h3 style="font-size: 13px; margin: 0">➕ New Ticket</h3>
          <div class="drawer-close" @click="showNew = false">✕</div>
        </div>
        <div style="display: grid; gap: 8px; font-size: 11px">
          <input v-model="nf.subject" placeholder="Subject" class="drawer-input" />
          <input v-model="nf.customer" placeholder="Customer name" class="drawer-input" />
          <select v-model="nf.type" class="drawer-input">
            <option v-for="t in ['Enquiry', 'Complaint', 'Defect', 'Quality', 'Documentation', 'Service Request']" :key="t">{{ t }}</option>
          </select>
          <select v-model="nf.priority" class="drawer-input">
            <option v-for="p in ['Low', 'Medium', 'High', 'Urgent']" :key="p">{{ p }}</option>
          </select>
          <textarea v-model="nf.desc" placeholder="Description" rows="3" class="drawer-input" style="resize: vertical"></textarea>
          <button class="btn-primary" style="font-size: 11px" :disabled="nfBusy" @click="createTicket">Create ticket</button>
        </div>
      </div>
    </div>
    <GenericDetailDrawer :record="detailRec" :title="'Ticketing & Issue'" @close="detailRec = null" :records="detailList" />
</template>
