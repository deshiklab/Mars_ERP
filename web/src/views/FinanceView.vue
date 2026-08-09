<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'
import type { CoaAccount, Invoice, Payment } from '@/api/types'

const data = useDataStore()
const tab = ref('invoices')

onMounted(() => {
  data.loadInvoices()
  data.loadPayments()
  data.loadFinance()
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Paid: ['#e8f5e9', '#2e7d32'],
    Cleared: ['#e8f5e9', '#2e7d32'],
    Unpaid: ['#ffebee', '#c62828'],
    Overdue: ['#fff3e0', '#e65100'],
    Draft: ['#f0f0f0', '#555'],
    Pending: ['#fff8e1', '#ff8f00']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const invCols = computed<TableColumn<Invoice>[]>(() => [
  {
    key: 'id',
    label: 'Invoice',
    sortable: true,
    renderHtml: (x) => `<div style="font-weight:600;color:#2f80ed">${esc(x.id)}</div><div style="font-size:9px;color:#888">${esc(x.issuedDate)}</div>`
  },
  { key: 'client', label: 'Client', renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:500">${esc(x.client)}</span>` },
  { key: 'project', label: 'Project', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.project || '—')}</span>` },
  {
    key: 'amount',
    label: 'Amount',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:600">${bdt(x.amount)}</span>`
  },
  {
    key: 'dueDate',
    label: 'Due',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.dueDate)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = statusStyle(x.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(x.status)}</span>`
    }
  }
])

const payCols = computed<TableColumn<Payment>[]>(() => [
  {
    key: 'id',
    label: 'Payment',
    sortable: true,
    renderHtml: (x) => `<div style="font-weight:600;color:#2f80ed">${esc(x.id)}</div><div style="font-size:9px;color:#888">${esc(x.date)}</div>`
  },
  { key: 'client', label: 'Client', renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:500">${esc(x.client)}</span>` },
  {
    key: 'amount',
    label: 'Amount',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:10px;color:#2e7d32;font-weight:600">${bdt(x.amount)}</span>`
  },
  { key: 'method', label: 'Method', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.method || '—')}</span>` },
  { key: 'reference', label: 'Reference', renderHtml: (x) => `<span style="font-size:9px;color:#888">${esc(x.reference || '—')}</span>` },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = statusStyle(x.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(x.status)}</span>`
    }
  }
])

const coaCols = computed<TableColumn<CoaAccount>[]>(() => [
  {
    key: 'code',
    label: 'Code',
    sortable: true,
    renderHtml: (x) => `<span style="font-weight:600;color:#2f80ed;font-size:10px">${esc(x.code)}</span>`
  },
  { key: 'name', label: 'Account', renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:500">${esc(x.name)}</span>` },
  {
    key: 'type',
    label: 'Type',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:9px;color:#555">${esc(x.type)}</span>`
  },
  {
    key: 'balance',
    label: 'Balance',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:600">${esc(x.balance)}</span>`
  }
])

const finStats = computed(() => [
  { label: 'Invoices', value: String(data.invoices.length), color: '#2f80ed' },
  { label: 'Payments', value: String(data.payments.length), color: '#2e7d32' },
  { label: 'Collected', value: bdt(data.payments.reduce((s, p) => s + (p.amount ?? 0), 0)), color: '#2e7d32' },
  { label: 'Accounts', value: String(data.coa.length), color: '#1565c0' }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Finance</span>
      <span class="page-subtitle">{{ data.invoices.length }} invoices · {{ data.payments.length }} payments · {{ data.coa.length }} accounts</span>
    </div>

    <StatsRow :stats="finStats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <!-- tabs -->
    <div style="display: flex; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; margin-bottom: 10px; width: fit-content">
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, background: tab === 'invoices' ? '#f0f4ff' : '#fff', color: '#2f80ed' }" @click="tab = 'invoices'">🧾 Invoices</button>
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, borderLeft: '1px solid #e0e0e0', background: tab === 'payments' ? '#f0f4ff' : '#fff', color: '#2f80ed' }" @click="tab = 'payments'">💳 Payments</button>
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, borderLeft: '1px solid #e0e0e0', background: tab === 'coa' ? '#f0f4ff' : '#fff', color: '#2f80ed' }" @click="tab = 'coa'">📒 Chart of Accounts</button>
    </div>

    <DataTable v-if="tab === 'invoices'" :columns="invCols" :rows="data.invoices" search-placeholder="Search invoices, clients…" />
    <DataTable v-else-if="tab === 'payments'" :columns="payCols" :rows="data.payments" search-placeholder="Search payments, references…" />
    <DataTable v-else :columns="coaCols" :rows="data.coa" search-placeholder="Search accounts…" />
  </div>
</template>
