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
    const arr = r.data.collections['entities']
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
    Accepted: ['#e8f5e9', '#2e7d32'],
    Completed: ['#e8f5e9', '#2e7d32'],
    Done: ['#e8f5e9', '#2e7d32'],
    Paid: ['#e8f5e9', '#2e7d32'],
    Received: ['#e8f5e9', '#2e7d32'],
    Published: ['#e8f5e9', '#2e7d32'],
    Passed: ['#e8f5e9', '#2e7d32'],
    Resolved: ['#e8f5e9', '#2e7d32'],
    Fixed: ['#e8f5e9', '#2e7d32'],
    Open: ['#e8f5e9', '#2e7d32'],
    Sent: ['#fff8e1', '#ff8f00'],
    Pending: ['#fff8e1', '#ff8f00'],
    Draft: ['#f0f0f0', '#555'],
    'In Progress': ['#fff3e0', '#e65100'],
    'To Do': ['#f0f4ff', '#2f80ed'],
    'In Review': ['#fff8e1', '#ff8f00'],
    Scheduled: ['#f0f4ff', '#2f80ed'],
    Closed: ['#f0f0f0', '#555'],
    Inactive: ['#f0f0f0', '#555'],
    Rejected: ['#ffebee', '#c62828'],
    Failed: ['#ffebee', '#c62828'],
    Overdue: ['#ffebee', '#c62828']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const rows = computed(() => items.value)

const stats = computed(() => [
  { label: 'Entities', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Groups', value: String(new Set(rows.value.map((e: any) => e.group)).size), color: '#1565c0' },
  { label: 'Customers', value: String(rows.value.filter((e: any) => e.group === 'Customer' || e.group === 'Buyer').length), color: '#2e7d32' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Entity',
    sortable: false,
    renderHtml: (x) => `<div style='display:flex;align-items:center;gap:8px'><span style='width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#00695c,#2f80ed);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700'>${esc(x.name.split(' ').slice(0, 2).map((w: string) => w[0]).join(''))}</span><div><div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.email||'')} · ${esc(x.phone||'')}</div></div></div>`
  },
  {
    key: 'group',
    label: 'Group',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:#f0f4ff;color:#2f80ed'>${esc(x.group||'—')}</span>`
  },
  {
    key: 'occupation',
    label: 'Occupation',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.occupation||'—')}</span>`
  },
  {
    key: 'nationality',
    label: 'Nationality',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.nationality||'—')}</span>`
  },
  {
    key: 'nid',
    label: 'NID',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:9px;color:#888'>${esc(x.nid||'—')}</span>`
  },
  {
    key: 'priority',
    label: 'Priority',
    sortable: true,
    renderHtml: (x) => `<span style='font-weight:600;font-size:10px;color:${prioColor(x.priority)}'>${esc(x.priority||'—')}</span>`
  },])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Entities</span>
      <span class="page-subtitle">{{ rows.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search entities…"
    />
  </div>
</template>
