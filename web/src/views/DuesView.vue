<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { showToast } from '@/toast'
import { useDataStore } from '@/stores/data'
import { _t } from '@/i18n'
import DataTable from '@/components/DataTable.vue'
import DueDetailDrawer from '@/components/DueDetailDrawer.vue'
import type { TableAction, TableColumn, TableTab } from '@/components/DataTable.vue'
import type { Due } from '@/api/types'

const route = useRoute()
const data = useDataStore()
const detailDue = ref<Due | null>(null)
const tab = ref('all')

onMounted(() => {
  data.loadDues().then(() => {
    if (route.query.due === '1' && data.dues.length) detailDue.value = data.dues[0]
  })
})

const buckets = ['0-30 Days', '31-60 Days', '60+ Days']

function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Critical: ['#ffebee', '#c62828'],
    Overdue: ['#fff3e0', '#e65100'],
    Current: ['#e8f5e9', '#2e7d32'],
    Paid: ['#e3f2fd', '#1565c0']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

function bucketStyle(bucket: string): { bg: string; fg: string } {
  if (bucket === '60+ Days') return { bg: '#ffebee', fg: '#c62828' }
  if (bucket === '31-60 Days') return { bg: '#fff3e0', fg: '#e65100' }
  return { bg: '#e8f5e9', fg: '#2e7d32' }
}

function bdt(n: number): string {
  if (n >= 10000000) return `৳ ${(n / 10000000).toFixed(2)} Cr`
  if (n >= 100000) return `৳ ${(n / 100000).toFixed(1)} Lac`
  return `৳ ${n.toLocaleString()}`
}

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

const totalDue = computed(() => tabRows.value.reduce((s, d) => s + (d.due ?? 0), 0))

const columns = computed<TableColumn<Due>[]>(() => [
  {
    key: 'customer',
    label: 'Customer',
    renderHtml: (d) =>
      `<div style="font-weight:500;color:#333">${esc(d.customer)}</div><div style="font-size:9px;color:#888">${esc(d.id)} · ${esc(d.phone)}</div>`
  },
  {
    key: 'project',
    label: 'Project / Unit',
    renderHtml: (d) =>
      `<div style="color:#333">${esc(d.project)}</div><div style="font-size:9px;color:#888">${esc(d.unit)}</div>`
  },
  {
    key: 'totalPrice',
    label: 'Total',
    sortable: true,
    renderHtml: (d) => `<span style="font-size:10px;color:#555">${bdt(d.totalPrice)}</span>`
  },
  {
    key: 'paid',
    label: 'Paid',
    sortable: true,
    renderHtml: (d) => `<span style="font-size:10px;color:#2e7d32;font-weight:600">${bdt(d.paid)}</span>`
  },
  {
    key: 'due',
    label: 'Due',
    sortable: true,
    renderHtml: (d) => `<span style="font-size:10px;color:#c62828;font-weight:700">${bdt(d.due)}</span>`
  },
  {
    key: 'dueDate',
    label: 'Due Date',
    sortable: true,
    renderHtml: (d) =>
      `<div style="font-size:10px;color:#555">${esc(d.dueDate)}</div>` +
      (d.daysOverdue > 0 ? `<div style="font-size:9px;color:#c62828">${d.daysOverdue}d overdue</div>` : '')
  },
  {
    key: 'bucket',
    label: 'Bucket',
    renderHtml: (d) => {
      const s = bucketStyle(d.bucket)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(d.bucket)}</span>`
    }
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (d) => {
      const s = statusStyle(d.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(d.status)}</span>`
    }
  }
])

const tabs = computed<TableTab[]>(() => [
  { id: 'all', label: 'All', count: data.dues.length },
  { id: 'critical', label: 'Critical', count: data.dues.filter((d) => d.status === 'Critical').length },
  { id: 'overdue', label: 'Overdue', count: data.dues.filter((d) => d.status === 'Overdue').length },
  { id: 'current', label: 'Current', count: data.dues.filter((d) => d.status === 'Current').length },
  { id: 'paid', label: 'Paid', count: data.dues.filter((d) => d.status === 'Paid').length }
])

const tabRows = computed(() => {
  if (tab.value === 'all') return data.dues
  const map: Record<string, string> = { critical: 'Critical', overdue: 'Overdue', current: 'Current', paid: 'Paid' }
  const st = map[tab.value]
  return st ? data.dues.filter((d) => d.status === st) : data.dues
})

function onTabChange(t: string) {
  tab.value = t
}

const aging = computed(() => {
  const buckets = [
    { label: '0–30 d', min: 0, max: 30, color: '#2e7d32', n: 0, amt: 0 },
    { label: '31–60 d', min: 31, max: 60, color: '#ff8f00', n: 0, amt: 0 },
    { label: '61–90 d', min: 61, max: 90, color: '#e65100', n: 0, amt: 0 },
    { label: '90+ d', min: 91, max: 1e9, color: '#c62828', n: 0, amt: 0 },
  ]
  data.dues.forEach((d) => {
    const days = Number(d.daysOverdue) || 0
    const b = buckets.find((x) => days >= x.min && days <= x.max)
    if (b) {
      b.n += 1
      b.amt += Number(d.due) || 0
    }
  })
  const total = Math.max(buckets.reduce((s, b) => s + b.amt, 0), 1)
  return { buckets, total }
})

const actions = computed<TableAction[]>(() => [
  { label: 'View Details', icon: '👁', onClick: (r) => (detailDue.value = r as unknown as Due) },
  { label: 'Mark Current', icon: '🟢', onClick: (r) => onDueStatus('Current') },
  { label: 'Mark Overdue', icon: '🟠', onClick: (r) => onDueStatus('Overdue') },
  { label: 'Mark Critical', icon: '🔴', onClick: (r) => onDueStatus('Critical') },
  { label: 'Mark Paid', icon: '✅', onClick: (r) => onDueStatus('Paid') }
])

function onDueStatus(st: string) {
  if (st === 'Paid') {
    showToast('Record the payment in Accounts & Finance (Payments) — the due bucket updates automatically', 'info')
  } else {
    showToast(`Bucket is auto-derived from payment age — ${st} is not set manually`, 'info')
  }
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Dues & Collections</span>
      <span class="page-subtitle">{{ data.dues.length }} accounts · total due {{ bdt(totalDue) }}</span>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <!-- AGING STRIP -->
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px">
      <div v-for="b in aging.buckets" :key="b.label" style="flex: 1; min-width: 130px; background: #fff; border: 1px solid #e8eef5; border-radius: 8px; padding: 8px 10px">
        <div style="display: flex; align-items: center; gap: 6px">
          <span :style="{ width: '8px', height: '8px', borderRadius: '4px', background: b.color }"></span>
          <span style="font-size: 9px; color: #666">{{ b.label }}</span>
        </div>
        <div style="font-size: 13px; font-weight: 700; margin-top: 2px">{{ b.n }} <span style="font-size: 8px; font-weight: 400; color: #999">{{ _t('accounts') }}</span></div>
        <div style="font-size: 9px; color: #555">{{ bdt(b.amt) }}</div>
        <div style="height: 4px; border-radius: 2px; background: #f0f3f7; margin-top: 5px; overflow: hidden">
          <div :style="{ width: (b.amt / aging.total) * 100 + '%', background: b.color, height: '100%' }"></div>
        </div>
      </div>
    </div>

    <p v-if="data.duesLoading" style="font-size: 11px; color: #888; padding: 16px">Loading dues…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="tabRows"
      :tabs="tabs"
      :actions="actions"
      search-placeholder="Search customers, projects…"
      @tab-change="onTabChange"
     :status-editable="false" />
  </div>
    <!-- Due detail drawer -->
    <DueDetailDrawer
      :due="detailDue"
      @close="detailDue = null"
      @status="onDueStatus"
      @updated="data.loadDues()"
    />

</template>
