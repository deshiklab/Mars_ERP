<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const items = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const arr = r.data.collections['suppliers']
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
const detailRec = ref<Record<string, unknown> | null>(null)

const stats = computed(() => [
  { label: 'Suppliers', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Active', value: String(rows.value.filter((s: any) => s.status === 'Active').length), color: '#2e7d32' },
  { label: 'Orders', value: String(rows.value.reduce((s: number, x: any) => s + (x.totalOrders ?? 0), 0)), color: '#1565c0' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Supplier',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.contact||'')} · ${esc(x.phone||'')}</div>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: false,
    renderHtml: (x) => `<span class='pill' style='background:#f0f4ff;color:#2f80ed'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'items',
    label: 'Items',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.items||'—')}</span>`
  },
  {
    key: 'rating',
    label: 'Rating',
    sortable: true,
    renderHtml: (x) => `<span style='display:inline-flex;padding:1px 5px;border-radius:4px;font-size:9px;font-weight:600;background:#fff8e1;color:#e65100'>⭐ ${esc(x.rating??'—')}</span>`
  },
  {
    key: 'totalOrders',
    label: 'Orders',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333'>${esc(x.totalOrders??0)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => (detailRec.value = r as Record<string, unknown>) }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Suppliers</span>
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
      search-placeholder="Search suppliers…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Suppliers'" @close="detailRec = null" />
</template>
