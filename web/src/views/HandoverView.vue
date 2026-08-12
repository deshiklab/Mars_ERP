<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import { api } from '@/api/client'
import { showToast } from '@/toast'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const route = useRoute()
const router = useRouter()
const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])
const tab = ref(String(route.query.tab ?? 'dashboard').toLowerCase())
function setTab(t: string) {
  tab.value = t
  void router.replace({ query: { ...route.query, tab: t } })
}

const hnd = computed(() => data.handover)
const hndStats = computed(() => {
  const t = hnd.value.length
  const done = hnd.value.filter((h) => h.status === 'Completed').length
  const sched = hnd.value.filter((h) => h.status === 'Handover Scheduled').length
  const insp = hnd.value.filter((h) => h.status === 'Inspection Pending').length
  const ong = hnd.value.filter((h) => h.status === 'Construction Ongoing').length
  const snags = hnd.value.reduce((s, h) => s + (Number((h as { snags?: unknown }).snags) || 0), 0)
  const totalValue = hnd.value.reduce((s, h) => s + (Number(h.totalValue) || 0), 0)
  const paid = hnd.value.reduce((s, h) => s + (Number(h.paidAmount) || 0), 0)
  const pct = (n: number) => (t ? Math.round((n / t) * 100) : 0)
  return {
    t, done, sched, insp, ong, snags, totalValue, paid,
    outstanding: totalValue - paid,
    bars: [
      { label: 'Completed', n: done, color: '#2e7d32' },
      { label: 'Handover Scheduled', n: sched, color: '#ff8f00' },
      { label: 'Inspection Pending', n: insp, color: '#c62828' },
      { label: 'Construction Ongoing', n: ong, color: '#1565c0' }
    ].map((b) => ({ ...b, pct: pct(b.n) }))
  }
})

onMounted(() => {
  data.loadHandover()
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
  { label: 'Handovers', value: String(data.handover.length), color: '#2f80ed' },
  { label: 'Pending', value: String(data.handover.filter(h=>h.status==='Pending').length), color: '#ff8f00' },
  { label: 'Completed', value: String(data.handover.filter(h=>h.status==='Completed'||h.status==='Handed Over').length), color: '#2e7d32' }
])


const hoBusy = ref(false)
const decideHo = async (id: string, st: string) => {
  if (hoBusy.value) return
  hoBusy.value = true
  try {
    const h = data.handover.find((x) => String(x.id ?? '') === id)
    if (!h) return
    const r = await api.call('handover_sync', { handover: [{ id: h.id ?? '', unit: h.unit ?? '', customer: h.customer ?? '', project: h.project ?? '', type: (h.type === 'Flat' ? 'Apartment' : h.type === 'Plot' ? 'Plot' : h.type === 'Commercial' ? 'Commercial' : 'Other'), status: st }] })
    if (r.ok) {
      showToast('Handover ' + st)
      await data.loadCollection('handover')
    } else showToast('Update failed - ' + (r.error || 'server error'))
  } finally {
    hoBusy.value = false
  }
}
;(window as unknown as { __hoAct: (id: string, st: string) => void }).__hoAct = decideHo
const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    renderHtml: (x) => `<div style='font-weight:600;color:#2f80ed'>${esc(x.id)}</div>`
  },
  {
    key: 'customer',
    label: 'Customer',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.customer)}</div><div style='font-size:9px;color:#888'>${esc(x.project||'')} ${esc(x.unit||'')}</div>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'totalValue',
    label: 'Value',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${bdt(x.totalValue)}</span>`
  },
  {
    key: 'paidAmount',
    label: 'Paid',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#2e7d32;font-weight:600'>${bdt(x.paidAmount)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = x.status || '—'
      let acts = ''
      if (s === 'Construction Ongoing') acts = `<button style="margin-left:6px;border:0;border-radius:4px;padding:2px 7px;font-size:9px;cursor:pointer;background:#2f80ed;color:#fff" onclick="event.stopPropagation();window.__hoAct('${x.id}','Handover Scheduled')">⚙ Schedule</button><button style="margin-left:4px;border:0;border-radius:4px;padding:2px 7px;font-size:9px;cursor:pointer;background:#27ae60;color:#fff" onclick="event.stopPropagation();window.__hoAct('${x.id}','Completed')">✓ Complete</button>`
      else if (s === 'Inspection Pending' || s === 'Handover Scheduled') acts = `<button style="margin-left:6px;border:0;border-radius:4px;padding:2px 7px;font-size:9px;cursor:pointer;background:#27ae60;color:#fff" onclick="event.stopPropagation();window.__hoAct('${x.id}','Completed')">✓ Complete</button>`
      return `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(s)}</span>${acts}`
    }
  },])

const rows = computed(() => data.handover)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Handover & Post-Sales</span>
      <span class="page-subtitle">{{ data.handover.length }} records</span>
    <div class="tabs" style="margin: 6px 0">
      <div class="tab" :class="{ active: tab === 'dashboard' }" @click="setTab('dashboard')">📊 Dashboard</div>
      <div class="tab" :class="{ active: tab === 'pipeline' }" @click="setTab('pipeline')">🏭 Handover Pipeline</div>
    </div>

    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    
    <template v-if="tab === 'dashboard'">
      <StatsRow :stats="[
        { label: 'Total Units', value: String(hndStats.t), color: '#1565c0' },
        { label: 'Completed', value: String(hndStats.done), color: '#2e7d32' },
        { label: 'Scheduled', value: String(hndStats.sched), color: hndStats.sched ? '#ff8f00' : '#999' },
        { label: 'Inspection', value: String(hndStats.insp), color: hndStats.insp ? '#c62828' : '#999' },
        { label: 'Open Snags', value: String(hndStats.snags), color: hndStats.snags ? '#c62828' : '#999' },
        { label: 'Portfolio', value: bdt(hndStats.totalValue), color: '#7b1fa2' }
      ]" />
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px">
        <div class="card">
          <div class="card-header"><h3>Pipeline Status Breakdown</h3></div>
          <div class="card-body" style="padding: 8px">
            <div v-for="b in hndStats.bars" :key="b.label" style="display: flex; align-items: center; gap: 6px; padding: 3px 0">
              <div style="font-size: 9px; width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ b.label }}</div>
              <div style="flex: 1; height: 8px; background: #e8e8e8; border-radius: 4px; overflow: hidden">
                <div :style="{ height: '100%', width: b.pct + '%', background: b.color, borderRadius: '4px' }"></div>
              </div>
              <div style="font-size: 9px; font-weight: 600; width: 30px; text-align: right">{{ b.n }}</div>
            </div>
            <div v-if="hndStats.t === 0" style="text-align: center; color: #999; font-size: 10px; padding: 10px">No handover records yet</div>
          </div>
        </div>
        <div class="card">
          <div class="card-header"><h3>Financial Summary</h3></div>
          <div class="card-body" style="padding: 10px; text-align: center">
            <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 8px">
              <div style="text-align: center">
                <div style="font-size: 18px; font-weight: 700; color: #2e7d32">{{ bdt(hndStats.totalValue) }}</div>
                <div style="font-size: 8px; color: #888">Total Value</div>
              </div>
              <div style="text-align: center">
                <div style="font-size: 18px; font-weight: 700; color: #1565c0">{{ bdt(hndStats.paid) }}</div>
                <div style="font-size: 8px; color: #888">Collected</div>
              </div>
              <div style="text-align: center">
                <div style="font-size: 18px; font-weight: 700; color: #e65100">{{ bdt(hndStats.outstanding) }}</div>
                <div style="font-size: 8px; color: #888">Outstanding</div>
              </div>
            </div>
            <div style="height: 8px; background: #e8e8e8; border-radius: 4px; overflow: hidden; margin: 0 20px">
              <div :style="{ height: '100%', width: (hndStats.totalValue ? Math.round((hndStats.paid / hndStats.totalValue) * 100) : 0) + '%', background: '#2f80ed' }"></div>
            </div>
            <div style="font-size: 8px; color: #888; margin-top: 4px">Collection rate: {{ hndStats.totalValue ? Math.round((hndStats.paid / hndStats.totalValue) * 100) : 0 }}%</div>
          </div>
        </div>
      </div>
    </template>
    <template v-if="tab === 'pipeline'">
<DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search handovers…"
    />
    </template>
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Handover & Post-Sales'" @close="detailRec = null" :records="detailList" />
</template>
