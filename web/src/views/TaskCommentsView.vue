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
    const arr = r.data.collections['task_comments']
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
  { label: 'Comments', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Authors', value: String(new Set(rows.value.map((c: any) => c.author)).size), color: '#1565c0' },
  { label: 'With Attachments', value: String(rows.value.filter((c: any) => (c.attachments?.length ?? 0) > 0).length), color: '#e65100' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'taskId',
    label: 'Task',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.taskId||'—')}</span>`
  },
  {
    key: 'author',
    label: 'Author',
    sortable: false,
    renderHtml: (x) => `<span class='pill' style='background:#f0f4ff;color:#2f80ed'>${esc(x.author||'—')}</span>`
  },
  {
    key: 'text',
    label: 'Comment',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;display:block;max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap'>${esc(x.text||'')}</span>`
  },
  {
    key: 'time',
    label: 'Time',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.time||'—')}</span>`
  },
  {
    key: 'attachments',
    label: 'Attachments',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:${(x.attachments?.length ?? 0) > 0 ? '#e65100' : '#888'}'>${x.attachments?.length ?? 0}</span>`
  },])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Task Comments</span>
      <span class="page-subtitle">{{ rows.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search comments…"
    />
  </div>
</template>
