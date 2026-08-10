<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { showToast } from '@/toast'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)

const statusOptions = ['Available', 'Reserved', 'Sold', 'Not Acquired']
const stageMap: Record<string, string> = { Available: 'available', Reserved: 'reserved', Sold: 'sold', 'Not Acquired': 'not_acquired' }

async function onStatusChange({ row, field, from, to }: { row: Record<string, unknown>; field: string; from: string; to: string }) {
  const id = String((row as { id?: string }).id ?? '')
  const r = await api.plotUpdateStatus(id, stageMap[to] ?? to)
  if (r.ok) {
    showToast(`Plot status → ${to}`, 'success')
  } else {
    ;(row as Record<string, unknown>)[field] = from
    showToast('Plot status update failed', 'error')
  }
}
const detailList = ref<Record<string, unknown>[]>([])

onMounted(() => {
  data.loadPlots()
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
    available: ['#e8f5e9', '#2e7d32'],
    reserved: ['#fff8e1', '#ff8f00'],
    sold: ['#ffebee', '#c62828'],
    not_acquired: ['#f0f0f0', '#555'],
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
  { label: 'Plots', value: String(data.plots.length), color: '#2f80ed' },
  { label: 'Available', value: String(data.plots.filter(p=>p.status==='available').length), color: '#2e7d32' },
  { label: 'Reserved', value: String(data.plots.filter(p=>p.status==='reserved').length), color: '#ff8f00' },
  { label: 'Sold', value: String(data.plots.filter(p=>p.status==='sold').length), color: '#c62828' },
  { label: 'Total', value: String(data.plots.length), color: '#2f80ed' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'plotNo',
    label: 'Plot No',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#333'>${esc(x.plotNo||'—')}</span>`
  },
  {
    key: 'location',
    label: 'Location',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.location||'—')}</span>`
  },
  {
    key: 'area',
    label: 'Area',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.area||'—')}</span>`
  },
  {
    key: 'price',
    label: 'Price',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${esc(x.price||'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])

const rows = computed(() => data.plots)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Plots</span>
      <span class="page-subtitle">{{ data.plots.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search plots…"
     :status-options="statusOptions" @status-change="onStatusChange" />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Plots'" @close="detailRec = null" :records="detailList" />
</template>
