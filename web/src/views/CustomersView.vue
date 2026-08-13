<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import DataTable from '@/components/DataTable.vue'
import CustomerDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const items = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const arr = r.data.collections['customers']
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
const custRec = ref<any | null>(null)
const custBusy = ref(false)
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

const stats = computed(() => [
  { label: 'Customers', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Active', value: String(rows.value.filter((c: any) => c.status === 'Active').length), color: '#2e7d32' },
  { label: 'With Dues', value: String(rows.value.filter((c: any) => (c.duesNum ?? 0) > 0).length), color: '#e65100' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Customer',
    sortable: false,
    renderHtml: (x) => `<div style='display:flex;align-items:center;gap:8px'><span style='width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#2f80ed,#56ccf2);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700'>${esc(x.name.split(' ').slice(0, 2).map((w: string) => w[0]).join(''))}</span><div><div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.email||'')} · ${esc(x.phone||'')}</div></div></div>`
  },
  {
    key: 'property',
    label: 'Property',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.property||'—')}</span>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:#f0f4ff;color:#2f80ed'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'payments',
    label: 'Payments',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333'>${esc(x.payments??0)}</span>`
  },
  {
    key: 'dues',
    label: 'Dues',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:${x.duesNum > 0 ? '#c62828' : '#2e7d32'};font-weight:600'>${esc(x.dues||'Tk0')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])
const custStatus = async (st: string) => {
  if (!custRec.value || custBusy.value) return
  custBusy.value = true
  try {
    const next = [...rows.value].map((x: any) => (String(x.id ?? '') === String(custRec.value?.id ?? '') ? { ...x, status: st } : x))
    const res = await api.sync({ customers: next })
    if (res.ok) {
      items.value = next as any[]
      custRec.value = { ...custRec.value, status: st }
    }
  } finally {
    custBusy.value = false
  }
}

const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { custRec.value = r as any; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Customers</span>
      <span class="page-subtitle">{{ rows.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading…</p>

    <DataTable
      :actions="actions"
      v-else
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search customers…"
    />
    <CustomerDetailDrawer :record="custRec" :title="'Customer'" :records="detailList" @close="custRec = null" />
  </div>
</template>
