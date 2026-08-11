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
  data.loadApprovals()
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
  { label: 'Approvals', value: String(data.approvals.length), color: '#2f80ed' },
  { label: 'Pending', value: String(data.approvals.filter(a=>a.status==='Pending').length), color: '#ff8f00' },
  { label: 'Approved', value: String(data.approvals.filter(a=>a.status==='Approved').length), color: '#2e7d32' }
])

const apprBusy = ref(false)
const decideAppr = async (a: any, st: string) => {
  if (apprBusy.value) return
  apprBusy.value = true
  try {
    const r = await api.call('approvals_sync', { approvals: [{ ref: a.id ?? '', title: a.title ?? '', type: a.type ?? '', requestedBy: a.requestedBy ?? '', date: a.date ?? '', status: st }] })
    if (r.ok) {
      await data.loadApprovals()
      showToast(`Approval ${st}`)
    } else {
      showToast('Update failed — ' + (r.error || 'server error'))
    }
  } finally {
    apprBusy.value = false
  }
}
;(window as unknown as { __apprAct: (id: string, st: string) => void }).__apprAct = (id: string, st: string) => {
  const a = data.approvals.find((x) => String(x.id ?? '') === id)
  if (a) void decideAppr(a, st)
}
const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'title',
    label: 'Title',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.title)}</div><div style='font-size:9px;color:#888'>${esc(x.type||'')} · ${esc(x.dept||'')}</div>`
  },
  {
    key: 'requestedBy',
    label: 'Requested By',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.requestedBy||'—')}</span>`
  },
  {
    key: 'amount',
    label: 'Amount',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${bdt(x.amount)}</span>`
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
      if (s === 'Pending') acts = ` <button style="border:0;border-radius:4px;font-size:9px;font-weight:700;padding:2px 6px;cursor:pointer;color:#fff;background:#27ae60;margin-left:4px" onclick="event.stopPropagation();window.__apprAct('${x.id}','Approved')">✓</button><button style="border:0;border-radius:4px;font-size:9px;font-weight:700;padding:2px 6px;cursor:pointer;color:#fff;background:#e74c3c;margin-left:4px" onclick="event.stopPropagation();window.__apprAct('${x.id}','Rejected')">✕</button>`
      return `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(s)}</span>${acts}`
    }
  },])

const rows = computed(() => data.approvals)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Financial Approvals</span>
      <span class="page-subtitle">{{ data.approvals.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search approvals…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Financial Approvals'" @close="detailRec = null" :records="detailList" />
</template>
