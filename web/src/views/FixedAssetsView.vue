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
  data.loadFixedAssets()
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


const faBusy = ref(false)
const decideFa = async (id: string, st: string) => {
  if (faBusy.value) return
  faBusy.value = true
  try {
    const a = data.fixedAssets.find((x) => String(x.id ?? '') === id)
    if (!a) return
    const r = await api.call('fixed_assets_sync', { assets: [{ id: a.id ?? '', name: a.name ?? '', category: a.category ?? '', cost: a.cost ?? 0, status: st }] })
    if (r.ok) {
      showToast('Asset ' + st)
      await data.loadCollection('fixedAssets')
    } else showToast('Update failed - ' + (r.error || 'server error'))
  } finally {
    faBusy.value = false
  }
}
;(window as unknown as { __faAct: (id: string, st: string) => void }).__faAct = decideFa
const stats = computed(() => [
  { label: 'Assets', value: String(data.fixedAssets.length), color: '#2f80ed' },
  { label: 'Total Cost', value: String(bdt(data.fixedAssets.reduce((s,a)=>s+(a.cost??0),0))), color: '#2e7d32' },
  { label: 'In Use', value: String(data.fixedAssets.filter(a=>a.status==='In Use').length), color: '#1565c0' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Asset',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.code||'')} · ${esc(x.category||'')}</div>`
  },
  {
    key: 'location',
    label: 'Location',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.location||'—')}</span>`
  },
  {
    key: 'cost',
    label: 'Cost',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${bdt(x.cost)}</span>`
  },
  {
    key: 'purchaseDate',
    label: 'Purchased',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.purchaseDate||'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = x.status || '—'
      let acts = ''
      if (s === 'In Use') acts = `<button style="margin-left:6px;border:0;border-radius:4px;padding:2px 7px;font-size:9px;cursor:pointer;background:#f39c12;color:#fff" onclick="event.stopPropagation();window.__faAct('${x.id}','Under Repair')">🔧 Repair</button><button style="margin-left:4px;border:0;border-radius:4px;padding:2px 7px;font-size:9px;cursor:pointer;background:#e74c3c;color:#fff" onclick="event.stopPropagation();window.__faAct('${x.id}','Disposed')">🗑 Dispose</button>`
      else if (s === 'Under Repair') acts = `<button style="margin-left:6px;border:0;border-radius:4px;padding:2px 7px;font-size:9px;cursor:pointer;background:#27ae60;color:#fff" onclick="event.stopPropagation();window.__faAct('${x.id}','In Use')">✓ Back</button>`
      return `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(s)}</span>${acts}`
    }
  },])

const rows = computed(() => data.fixedAssets)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Fixed Assets</span>
      <span class="page-subtitle">{{ data.fixedAssets.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search assets…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Fixed Assets'" @close="detailRec = null" :records="detailList" />
</template>
