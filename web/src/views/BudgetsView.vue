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
    const arr = r.data.collections['project_budgets']
    items.value = Array.isArray(arr) ? arr : []
  }
  loading.value = false
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

/** Parse a formatted ৳ string (e.g. "৳ 2.1 Cr", "৳ 5,00,000") into a number. */
const num = (v: unknown): number => {
  if (typeof v === 'number') return v
  const str = String(v ?? '').replace(/[৳,\s]/g, '')
  const m = str.match(/^([0-9.]+)(Cr|Lac)?$/i)
  if (!m) return 0
  const n = parseFloat(m[1])
  return m[2] ? (m[2].toLowerCase() === 'cr' ? n * 10000000 : n * 100000) : n
}

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
  { label: 'Budgets', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Total Allocated', value: String(bdt(rows.value.reduce((s: number, b: any) => s + num(b.budget), 0))), color: '#1565c0' },
  { label: 'Total Spent', value: String(bdt(rows.value.reduce((s: number, b: any) => s + num(b.spent), 0))), color: '#c62828' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Budget',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.type||'')}</div>`
  },
  {
    key: 'budget',
    label: 'Allocated',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${bdt(num(x.budget))}</span>`
  },
  {
    key: 'spent',
    label: 'Spent',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#c62828;font-weight:600'>${bdt(num(x.spent))}</span>`
  },
  {
    key: 'allocated',
    label: 'Utilization',
    sortable: true,
    renderHtml: (x) => `<div style='min-width:120px'><div style='background:#f0f0f0;border-radius:4px;height:10px;overflow:hidden'><div style='width:${Math.min(100, (num(x.spent) / num(x.budget) * 100) || 0)}%;background:${(num(x.spent) / num(x.budget)) > 0.9 ? '#c62828' : '#2f80ed'};height:100%;border-radius:4px'></div></div><span style='font-size:8px;color:#888'>${Math.round((num(x.spent) / num(x.budget) * 100) || 0)}%</span></div>`
  },
  {
    key: 'progress',
    label: 'Progress',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.progress??'—')}%</span>`
  },])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Project Budgets</span>
      <span class="page-subtitle">{{ rows.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search budgets…"
    />
  </div>
</template>
