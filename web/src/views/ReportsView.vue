<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const items = ref<any[]>([])
const payments = ref<any[]>([])
const invoices = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const arr = r.data.collections['bi_reports']
    items.value = Array.isArray(arr) ? arr : []
    payments.value = (r.data.collections.payments as any[]) ?? []
    invoices.value = (r.data.collections.invoices as any[]) ?? []
  }
  loading.value = false
})

/** Monthly collections: group cleared/paid payments by YYYY-MM. */
const monthly = computed(() => {
  const map: Record<string, { month: string; amt: number; count: number }> = {}
  payments.value.forEach((p) => {
    if (!p?.date) return
    const m = String(p.date).slice(0, 7)
    if (!/^\d{4}-\d{2}$/.test(m)) return
    map[m] = map[m] || { month: m, amt: 0, count: 0 }
    if (p.status === 'Cleared' || p.status === 'Paid') {
      map[m].amt += Number(p.amount) || 0
      map[m].count++
    }
  })
  const total = payments.value.reduce((s, p) => s + (Number(p.amount) || 0), 0)
  return { rows: Object.values(map).sort((a, b) => a.month.localeCompare(b.month)), total }
})

const chartStats = computed(() => [
  { label: '📄 Reports', value: String(items.value.length), color: '#2f80ed' },
  { label: '💳 Collections', value: bdt(monthly.value.total), color: '#2e7d32' },
  { label: '📅 Months', value: String(monthly.value.rows.length), color: '#1565c0' },
  { label: '🧾 Invoices', value: String(invoices.value.length), color: '#e65100' }
])

const maxMonth = computed(() => Math.max(...monthly.value.rows.map((r) => r.amt), 1))
const monthLabel = (m: string) => {
  const names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const [y, mo] = m.split('-')
  return names[parseInt(mo, 10) - 1] + ' ' + y.slice(2)
}

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
    Open: ['#e8f5e9', '#2e7d32'],
    Sent: ['#fff8e1', '#ff8f00'],
    Pending: ['#fff8e1', '#ff8f00'],
    Draft: ['#f0f0f0', '#555'],
    'In Progress': ['#fff3e0', '#e65100'],
    'To Do': ['#f0f4ff', '#2f80ed'],
    Upcoming: ['#f0f4ff', '#2f80ed'],
    Scheduled: ['#f0f4ff', '#2f80ed'],
    Closed: ['#f0f0f0', '#555'],
    Inactive: ['#f0f0f0', '#555'],
    Rejected: ['#ffebee', '#c62828'],
    Overdue: ['#ffebee', '#c62828']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const rows = computed(() => items.value)
const detailRec = ref<Record<string, unknown> | null>(null)

const stats = computed(() => [
  { label: 'Reports', value: String(rows.value.length), color: '#2f80ed' },
  { label: 'Published', value: String(rows.value.filter((r: any) => r.status === 'Published').length), color: '#2e7d32' },
  { label: 'Draft', value: String(rows.value.filter((r: any) => r.status === 'Draft').length), color: '#ff8f00' }
])

const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'name',
    label: 'Report',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.name)}</div><div style='font-size:9px;color:#888'>${esc(x.desc||'')}</div>`
  },
  {
    key: 'category',
    label: 'Category',
    sortable: false,
    renderHtml: (x) => `<span class='pill' style='background:#f0f4ff;color:#2f80ed'>${esc(x.category||'—')}</span>`
  },
  {
    key: 'chart',
    label: 'Chart',
    sortable: false,
    renderHtml: (x) => {
      const c = x.chart
      const name = typeof c === 'string' ? c : c && typeof c === 'object' ? (c.name || c.type || 'Chart') : '—'
      return `<span style='font-size:10px;color:#555'>${esc(name)}</span>`
    }
  },
  {
    key: 'period',
    label: 'Period',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.period||'—')}</span>`
  },
  {
    key: 'updated',
    label: 'Updated',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.updated||'—')}</span>`
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
      <span class="page-title">BI Reports</span>
      <span class="page-subtitle">{{ rows.length }} records</span>
    </div>

    <StatsRow :stats="chartStats" />

      <!-- monthly collection chart -->
      <div class="card" style="margin-bottom: 10px">
        <div class="card-header"><h3>💳 Monthly Collections</h3></div>
        <div class="card-body" style="padding: 12px">
          <div v-if="monthly.rows.length" style="display: flex; align-items: flex-end; gap: 14px; min-height: 130px; padding: 6px 2px 0; overflow-x: auto">
            <div v-for="r in monthly.rows" :key="r.month" style="display: flex; flex-direction: column; align-items: center; gap: 4px; flex-shrink: 0">
              <span style="font-size: 9px; font-weight: 700; color: #2e7d32">{{ bdt(r.amt) }}</span>
              <div :style="{ height: Math.max(6, (r.amt / maxMonth) * 90) + 'px', width: 42, background: 'linear-gradient(180deg, #2f80ed, #56ccf2)', borderRadius: '5px 5px 0 0' }" :title="r.month + ' · ' + bdt(r.amt)"></div>
              <span style="font-size: 8px; color: #888">{{ monthLabel(r.month) }}</span>
              <span style="font-size: 8px; color: #999">{{ r.count }} txns</span>
            </div>
          </div>
          <div v-else style="text-align: center; padding: 20px; color: #999; font-size: 11px">No collection data for the chart.</div>
        </div>
      </div>

      <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading…</p>

    <DataTable
      :actions="actions"
      v-else
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search reports…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'BI Reports'" @close="detailRec = null" />
</template>
