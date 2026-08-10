<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

onMounted(() => {
  data.loadComplaints()
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
function prioColor(p: string): string {
  return p === 'High' ? '#c62828' : p === 'Medium' ? '#e65100' : '#888'
}

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
    Present: ['#e8f5e9', '#2e7d32'],
    'In Use': ['#e8f5e9', '#2e7d32'],
    Inactive: ['#f0f0f0', '#555'],
    Pending: ['#fff8e1', '#ff8f00'],
    'In Progress': ['#fff3e0', '#e65100'],
    Open: ['#ffebee', '#c62828'],
    Absent: ['#ffebee', '#c62828'],
    Half: ['#fff3e0', '#e65100'],
    Late: ['#fff3e0', '#e65100'],
    'On Leave': ['#fff3e0', '#e65100'],
    'On Hold': ['#fff3e0', '#e65100'],
    Rejected: ['#ffebee', '#c62828'],
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const stats = computed(() => [
  { label: 'Complaints', value: String(data.complaints.length), color: '#2f80ed' },
  { label: 'Open', value: String(data.complaints.filter(c=>c.status==='Open').length), color: '#e65100' },
  { label: 'Resolved', value: String(data.complaints.filter(c=>c.status==='Resolved'||c.status==='Closed').length), color: '#2e7d32' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'client',
    label: 'Client',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.client)}</div><div style='font-size:9px;color:#888'>${esc(x.project||'')} ${esc(x.unit||'')}</div>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'priority',
    label: 'Priority',
    sortable: true,
    renderHtml: (x) => `<span style='font-weight:600;font-size:10px;color:${prioColor(x.priority)}'>${esc(x.priority||'—')}</span>`
  },
  {
    key: 'sla',
    label: 'SLA',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.sla||'—')}</span>`
  },
  {
    key: 'filedDate',
    label: 'Filed',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.filedDate||'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])

const rows = computed(() => data.complaints)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Complaints & Issues</span>
      <span class="page-subtitle">{{ data.complaints.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search complaints…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Complaints & Issues'" @close="detailRec = null" :records="detailList" />
</template>
