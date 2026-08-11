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
  data.loadEquipment()
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
  { label: 'Equipment', value: String(data.equipment.length), color: '#2f80ed' },
  { label: 'Operational', value: String(data.equipment.filter(e=>e.status==='Operational'||e.status==='Available').length), color: '#2e7d32' },
  { label: 'In Service', value: String(data.equipment.filter(e=>e.status==='In Service'||e.status==='Maintenance').length), color: '#e65100' }
])

const eqBusy = ref(false)
;(window as unknown as { __eqAct: (id: string, st: string) => void }).__eqAct = async (id: string, st: string) => {
  if (eqBusy.value) return
  eqBusy.value = true
  try {
    const e = data.equipment.find((x) => String(x.id ?? '') === id)
    if (!e) return
    const r = await api.call('equipment_sync', { equipment: [{ id: e.id ?? '', name: e.name ?? '', model: e.model ?? '', site: e.site ?? '', operator: e.operator ?? '', status: st }] })
    if (r.ok) { showToast('Equipment ' + st); await data.loadCollection('equipment') }
    else showToast('Update failed — ' + (r.error || 'server error'))
  } finally { eqBusy.value = false }
}
const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Equipment',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.model||'')} · ${esc(x.type||'')}</div>`
  },
  {
    key: 'site',
    label: 'Site',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.site||'—')}</span>`
  },
  {
    key: 'operator',
    label: 'Operator',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.operator||'—')}</span>`
  },
  {
    key: 'hours',
    label: 'Hours',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333'>${esc(x.hours??'—')}</span>`
  },
  {
    key: 'fuelCost',
    label: 'Fuel Cost',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${bdt(x.fuelCost)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s2 = statusColor(x.status)
      let acts = ''
      if (x.status === 'Operational') acts = ` <button style="border:0;border-radius:4px;padding:2px 7px;font-size:10px;cursor:pointer;background:#f57c00;color:#fff" onclick="event.stopPropagation();window.__eqAct('${x.id}','Maintenance')">Maintenance</button>`
      else if (x.status === 'Maintenance') acts = ` <button style="border:0;border-radius:4px;padding:2px 7px;font-size:10px;cursor:pointer;background:#2e7d32;color:#fff" onclick="event.stopPropagation();window.__eqAct('${x.id}','Operational')">Back in service</button><button style="border:0;border-radius:4px;padding:2px 7px;font-size:10px;cursor:pointer;background:#c62828;color:#fff;margin-left:3px" onclick="event.stopPropagation();window.__eqAct('${x.id}','Idle')">Idle</button>`
      return `<span class='pill' style='background:${s2.bg};color:${s2.fg}'>${x.status}</span>${acts}`
    }
  },])

const rows = computed(() => data.equipment)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Equipment & Machinery</span>
      <span class="page-subtitle">{{ data.equipment.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search equipment…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Equipment & Machinery'" @close="detailRec = null" :records="detailList" />
</template>
