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
  data.loadPartyLedger()
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
  { label: 'Parties', value: String(data.partyLedger.length), color: '#2f80ed' },
  { label: 'Receivables', value: String(data.partyLedger.filter(p=>p.type==='Customer').length), color: '#e65100' },
  { label: 'Payables', value: String(data.partyLedger.filter(p=>p.type!=='Customer').length), color: '#1565c0' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Party',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.name)}</div>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'out',
    label: 'Outstanding',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#c62828;font-weight:600'>${bdt(x.out)}</span>`
  },
  {
    key: 'dueDate',
    label: 'Due',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.dueDate||'—')}</span>`
  },])

const rows = computed(() => data.partyLedger)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Party Ledger</span>
      <span class="page-subtitle">{{ data.partyLedger.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search parties…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Party Ledger'" @close="detailRec = null" :records="detailList" />
</template>
