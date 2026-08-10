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
    const arr = r.data.collections['documents']
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
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

const stats = computed(() => [
  { label: 'Documents', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Approved', value: String(rows.value.filter((d: any) => d.status === 'Approved').length), color: '#2e7d32' },
  { label: 'Pending', value: String(rows.value.filter((d: any) => d.status === 'Pending').length), color: '#ff8f00' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'title',
    label: 'Document',
    sortable: false,
    renderHtml: (x) => `<div style='display:flex;align-items:center;gap:6px'><span style='font-size:13px'>${x.type === 'PDF' ? '📄' : x.type === 'Image' ? '🖼️' : '📁'}</span><div><div style='font-weight:500;color:#333'>${esc(x.title)}</div><div style='font-size:9px;color:#888'>${esc(x.file||'')} · ${esc(x.fileSize||'')}</div></div></div>`
  },
  {
    key: 'category',
    label: 'Category',
    sortable: false,
    renderHtml: (x) => `<span class='pill' style='background:#f0f4ff;color:#2f80ed'>${esc(x.category||'—')}</span>`
  },
  {
    key: 'property',
    label: 'Property',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.property||'—')}</span>`
  },
  {
    key: 'date',
    label: 'Date',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.date||'—')}</span>`
  },
  {
    key: 'uploadedBy',
    label: 'Uploaded By',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.uploadedBy||'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Document Vault</span>
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
      search-placeholder="Search documents…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Document Vault'" @close="detailRec = null" :records="detailList" />
</template>
