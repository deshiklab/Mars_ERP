<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const data = useDataStore()

onMounted(() => {
  data.loadBrokers()
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
  { label: 'Brokers', value: String(data.brokers.length), color: '#2f80ed' },
  { label: 'Active', value: String(data.brokers.filter(b=>b.status==='Active').length), color: '#2e7d32' },
  { label: 'Deals Closed', value: String(data.brokers.reduce((s,b)=>s+(b.dealsClosed??0),0)), color: '#e65100' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Broker',
    sortable: false,
    renderHtml: (x) => `<div style='display:flex;align-items:center;gap:8px'><span style='width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#e65100,#2f80ed);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700'>${esc(x.name.split(' ').slice(0, 2).map((w: string) => w[0]).join(''))}</span><div><div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.phone||'')}</div></div></div>`
  },
  {
    key: 'region',
    label: 'Region',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.region||'—')}</span>`
  },
  {
    key: 'tier',
    label: 'Tier',
    sortable: true,
    renderHtml: (x) => `<span style='display:inline-flex;padding:1px 6px;border-radius:8px;font-size:9px;font-weight:600;background:#f3e5f5;color:#7b1fa2'>${esc(x.tier||'—')}</span>`
  },
  {
    key: 'leadsReferred',
    label: 'Leads',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333'>${esc(x.leadsReferred??0)}</span>`
  },
  {
    key: 'dealsClosed',
    label: 'Deals',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#2e7d32;font-weight:600'>${esc(x.dealsClosed??0)}</span>`
  },
  {
    key: 'commissionPct',
    label: 'Commission',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.commissionPct??'—')}%</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])

const rows = computed(() => data.brokers)
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Brokers</span>
      <span class="page-subtitle">{{ data.brokers.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search brokers…"
    />
  </div>
</template>
