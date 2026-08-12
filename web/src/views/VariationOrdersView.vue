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
  data.loadVariation()
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
  { label: 'Variations', value: String(data.variations.length), color: '#2f80ed' },
  { label: 'Approved', value: String(data.variations.filter(v=>v.status==='Approved').length), color: '#2e7d32' },
  { label: 'Pending', value: String(data.variations.filter(v=>v.status==='Pending').length), color: '#ff8f00' }
])

const actBusy = ref(false)
const voAct = async (id: string, st: string) => {
  const v = rows.value.find((x: any) => String(x.id ?? '') === id)
  if (!v) return
  actBusy.value = true
  try {
    const r = await api.call('variation_orders_sync', { variationOrders: [{ id: v.id ?? '', project: v.project ?? '', title: v.title ?? '', originator: v.originator ?? '', status: st }] })
    if (r.ok) {
      showToast(`Variation ${st}`)

    } else {
      showToast('Update failed — ' + (r.error || 'server error'))
    }
  } finally {
    actBusy.value = false
  }
}
;(window as unknown as { __voAct?: (id: string, st: string) => void }).__voAct = voAct
const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'title',
    label: 'Title',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.title)}</div><div style='font-size:9px;color:#888'>${esc(x.project||'')}</div>`
  },
  {
    key: 'originator',
    label: 'Originator',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.originator||'—')}</span>`
  },
  {
    key: 'impact',
    label: 'Impact',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.impact||'—')}</span>`
  },
  {
    key: 'date',
    label: 'Date',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.date||'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x: any) => {
      const c = statusColor(x.status)
      let acts = ''
      if (x.status === 'Pending') acts = ` <button style="background:#2e7d32;color:#fff;border:0;border-radius:6px;padding:2px 8px;font-size:10px;cursor:pointer" onclick="event.stopPropagation();window.__voAct('${x.id}','Approved')">Approve</button> <button style="background:#d32f2f;color:#fff;border:0;border-radius:6px;padding:2px 8px;font-size:10px;cursor:pointer" onclick="event.stopPropagation();window.__voAct('${x.id}','Rejected')">Reject</button>`
      return `<span class="pill" style="background:${c.bg};color:${c.fg}">${esc(x.status)}</span>${acts}`
    }
  },
])


const rows = computed(() => data.variations)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Variation Orders</span>
      <span class="page-subtitle">{{ data.variations.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search variations…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Variation Orders'" @close="detailRec = null" :records="detailList" />
</template>
