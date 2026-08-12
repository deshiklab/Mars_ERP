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
async function receiptInspect(name: string, status: string) {
  const r = await api.call('receipt_inspect', { name, status })
  if (r.ok) {
    showToast(`Inspection → ${status}`)
    await data.loadReceipts()
  } else {
    showToast('Inspection update failed — ' + (r.error || 'server error'))
  }
}
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

onMounted(() => {
  data.loadReceipts()
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
  { label: 'Receipts', value: String(data.receipts.length), color: '#2f80ed' },
  { label: 'Qty Received', value: String(data.receipts.reduce((s,r)=>s+(r.qty??0),0)), color: '#2e7d32' },
  { label: 'PO Linked', value: String(data.receipts.filter(r=>r.poRef).length), color: '#1565c0' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'item',
    label: 'Item',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.item)}</div><div style='font-size:9px;color:#888'>${esc(x.poRef||'')} · ${esc(x.grn||'')}</div>`
  },
  {
    key: 'qty',
    label: 'Qty',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${esc(x.qty??'—')} ${esc(x.unit||'')}</span>`
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
    key: 'receivedBy',
    label: 'Received By',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.receivedBy||'—')}</span>`
  },])

const rows = computed(() => data.receipts)
const actions = computed(() => [
  { label: '✓ Pass', icon: '✅', show: (r: any) => String(r.inspection ?? '') !== 'Pass', onClick: (r: unknown) => receiptInspect(String((r as any).id ?? ''), 'Pass') },
  { label: '✕ Fail', icon: '⛔', show: (r: any) => String(r.inspection ?? '') !== 'Fail', onClick: (r: unknown) => receiptInspect(String((r as any).id ?? ''), 'Fail') },
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Goods Receipts</span>
      <span class="page-subtitle">{{ data.receipts.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search receipts…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Goods Receipts'" @close="detailRec = null" :records="detailList" />
</template>
