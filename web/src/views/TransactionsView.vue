<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import DataTable from '@/components/DataTable.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const items = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const arr = r.data.collections['transactions']
    items.value = Array.isArray(arr) ? arr : []
  }
  loading.value = false
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function prioColor(p: string): string {
  return p === 'High' ? '#c62828' : p === 'Medium' ? '#e65100' : '#888'
}

function statusColor(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Active: ['#e8f5e9', '#2e7d32'],
    Available: ['#e8f5e9', '#2e7d32'],
    Approved: ['#e8f5e9', '#2e7d32'],
    Completed: ['#e8f5e9', '#2e7d32'],
    Done: ['#e8f5e9', '#2e7d32'],
    'In Progress': ['#fff3e0', '#e65100'],
    'To Do': ['#f0f4ff', '#2f80ed'],
    Paid: ['#e8f5e9', '#2e7d32'],
    Received: ['#e8f5e9', '#2e7d32'],
    Present: ['#e8f5e9', '#2e7d32'],
    Resolved: ['#e8f5e9', '#2e7d32'],
    Closed: ['#e8f5e9', '#2e7d32'],
    Pending: ['#fff8e1', '#ff8f00'],
    Open: ['#ffebee', '#c62828'],
    Inactive: ['#f0f0f0', '#555'],
    Canceled: ['#ffebee', '#c62828'],
    Rejected: ['#ffebee', '#c62828'],
    Overdue: ['#ffebee', '#c62828']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const rows = computed(() => items.value)

const stats = computed(() => [
  { label: 'Transactions', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Inflow', value: String(bdt(rows.value.filter((t: any) => t.type === 'Inflow').reduce((s: number, t: any) => s + (t.amount ?? 0), 0))), color: '#2e7d32' },
  { label: 'Outflow', value: String(bdt(rows.value.filter((t: any) => t.type === 'Outflow').reduce((s: number, t: any) => s + (t.amount ?? 0), 0))), color: '#c62828' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:${x.type==='Inflow' ? '#2e7d32' : '#c62828'}'>${esc(x.id)}</div><div style='font-size:9px;color:#888'>${esc(x.date||'')}</div>`
  },
  {
    key: 'desc',
    label: 'Description',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.desc||'—')}</div><div style='font-size:9px;color:#888'>${esc(x.project||'')} · ${esc(x.category||'')}</div>`
  },
  {
    key: 'client',
    label: 'Client',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.client||'—')}</span>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${x.type==='Inflow' ? '#e8f5e9' : '#ffebee'};color:${x.type==='Inflow' ? '#2e7d32' : '#c62828'}'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'amount',
    label: 'Amount',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:11px;color:${x.type==='Inflow' ? '#2e7d32' : '#c62828'};font-weight:700'>${esc(x.fmt||bdt(x.amount))}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Cash Flow</span>
      <span class="page-subtitle">{{ rows.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search transactions…"
    />
  </div>
</template>
