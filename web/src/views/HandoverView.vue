<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const data = useDataStore()

onMounted(() => {
  data.loadHandover()
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
  { label: 'Handovers', value: String(data.handover.length), color: '#2f80ed' },
  { label: 'Pending', value: String(data.handover.filter(h=>h.status==='Pending').length), color: '#ff8f00' },
  { label: 'Completed', value: String(data.handover.filter(h=>h.status==='Completed'||h.status==='Handed Over').length), color: '#2e7d32' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'customer',
    label: 'Customer',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.customer)}</div><div style='font-size:9px;color:#888'>${esc(x.project||'')} ${esc(x.unit||'')}</div>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'totalValue',
    label: 'Value',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${bdt(x.totalValue)}</span>`
  },
  {
    key: 'paidAmount',
    label: 'Paid',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#2e7d32;font-weight:600'>${bdt(x.paidAmount)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])

const rows = computed(() => data.handover)
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Handover & Post-Sales</span>
      <span class="page-subtitle">{{ data.handover.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search handovers…"
    />
  </div>
</template>
