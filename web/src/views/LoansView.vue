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
  data.loadLoans()
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
  { label: 'Loans', value: String(data.loans.length), color: '#2f80ed' },
  { label: 'Outstanding', value: String(bdt(data.loans.reduce((s,l)=>s+(l.outstanding??0),0))), color: '#c62828' },
  { label: 'EMI Total', value: String(bdt(data.loans.reduce((s,l)=>s+(l.emi??0),0))), color: '#e65100' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'lender',
    label: 'Lender',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.lender)}</div><div style='font-size:9px;color:#888'>${esc(x.type||'')}</div>`
  },
  {
    key: 'principal',
    label: 'Principal',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${bdt(x.principal)}</span>`
  },
  {
    key: 'outstanding',
    label: 'Outstanding',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#c62828;font-weight:600'>${bdt(x.outstanding)}</span>`
  },
  {
    key: 'emi',
    label: 'EMI',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${bdt(x.emi)}</span>`
  },
  {
    key: 'rate',
    label: 'Rate',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.rate??'—')}%</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])

const rows = computed(() => data.loans)
const loanClose = async (r: unknown) => {
  const x = r as Record<string, unknown>
  if (!x.lender || x.status === 'Closed') return
  const res = await api.call('loans_sync', { loans: [{ lender: String(x.lender ?? ''), type: (['External', 'Internal', 'Other'].includes(String(x.type ?? '')) ? String(x.type) : 'Other'), status: 'Closed' }] })
  if (res.ok) { showToast('Loan marked as closed'); await data.loadLoans() }
  else showToast('Failed — ' + (res.error || 'server error'))
}
const actions = computed(() => [
  { label: 'Close Loan', icon: '✓', show: (r: unknown) => (r as Record<string, unknown>).status !== 'Closed', onClick: (r: unknown) => loanClose(r) },
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Loans</span>
      <span class="page-subtitle">{{ data.loans.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search loans…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Loans'" @close="detailRec = null" :records="detailList" />
</template>
