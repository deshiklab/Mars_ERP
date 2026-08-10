<script setup lang="ts">
/**
 * CustomerPortalView — customer-facing portal: their bookings, dues,
 * tickets and payments, filtered by the logged-in customer's name/email.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import DataTable from '@/components/DataTable.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const auth = useAuthStore()
const bookings = ref<any[]>([])
const dues = ref<any[]>([])
const tickets = ref<any[]>([])
const payments = ref<any[]>([])
const loading = ref(true)

const me = computed(() => String(auth.user || '').toLowerCase())
const myName = computed(() => String(auth.fullName || '').toLowerCase())

const mine = (arr: any[], nameField: string) => arr.filter((x) => {
  const n = String(x[nameField] || '').toLowerCase()
  return n.includes(me.value) || n.includes(myName.value) || me.value.includes(n)
})

const myBookings = computed(() => mine(bookings.value, 'client'))
const myDues = computed(() => mine(dues.value, 'customer'))
const myTickets = computed(() => mine(tickets.value, 'customer'))
const myPayments = computed(() => mine(payments.value, 'client'))

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    bookings.value = (r.data.collections.bookings as any[]) ?? []
    dues.value = (r.data.collections.dues as any[]) ?? []
    tickets.value = (r.data.collections.supportTickets as any[]) ?? []
    payments.value = (r.data.collections.payments as any[]) ?? []
  }
  loading.value = false
})

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)
const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

function statusColor(s: string): string {
  const map: Record<string, string> = {
    Confirmed: '#2e7d32', Paid: '#2e7d32', Cleared: '#2e7d32', Resolved: '#2e7d32',
    'Pending Review': '#e65100', Pending: '#e65100', Open: '#c62828', Overdue: '#c62828'
  }
  return map[s] ?? '#555'
}

const stats = computed(() => [
  { label: 'My Bookings', value: String(myBookings.value.length), color: '#2f80ed' },
  { label: 'My Dues', value: bdt(myDues.value.reduce((s: number, d: any) => s + (d.due ?? 0), 0)), color: '#c62828' },
  { label: 'My Tickets', value: String(myTickets.value.length), color: '#e65100' },
  { label: 'My Payments', value: String(myPayments.value.length), color: '#2e7d32' }
])

const bookingCols = computed<TableColumn<any>[]>(() => [
  {
    key: 'id',
    label: 'Booking',
    sortable: true,
    renderHtml: (x) => `<div style="font-weight:600;color:#2f80ed">${esc(x.id)}</div><div style="font-size:9px;color:#888">${esc(x.date || '')}</div>`
  },
  { key: 'property', label: 'Property', renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:500">${esc(x.property)}</span>` },
  { key: 'unit', label: 'Unit', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.unit || '—')}</span>` },
  { key: 'price', label: 'Price', sortable: true, renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:600">${bdt(x.price)}</span>` },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class="pill" style="background:${statusColor(x.status)}22;color:${statusColor(x.status)}">${esc(x.status)}</span>`
  }
])

const dueCols = computed<TableColumn<any>[]>(() => [
  { key: 'project', label: 'Project', renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:500">${esc(x.project)}</span>` },
  { key: 'unit', label: 'Unit', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.unit || '—')}</span>` },
  { key: 'due', label: 'Due', sortable: true, renderHtml: (x) => `<span style="font-size:11px;color:#c62828;font-weight:700">${bdt(x.due)}</span>` },
  { key: 'dueDate', label: 'Due Date', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.dueDate || '—')}</span>` },
  { key: 'daysOverdue', label: 'Overdue', sortable: true, renderHtml: (x) => `<span style="font-size:10px;color:${x.daysOverdue > 0 ? '#c62828' : '#2e7d32'}">${x.daysOverdue > 0 ? x.daysOverdue + 'd' : '—'}</span>` }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">Customer Portal</span>
      <span class="page-subtitle">Welcome, {{ auth.fullName || auth.user }}</span>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading your portal…</p>

    <template v-else>
      <StatsRow :stats="stats" />

      <div class="card" style="margin-bottom: 10px">
        <div class="card-header"><h3>📋 My Bookings</h3></div>
        <div class="card-body" style="padding: 0">
          <DataTable :columns="bookingCols" :rows="myBookings" search-placeholder="Search bookings…" />
        </div>
      </div>

      <div class="card" style="margin-bottom: 10px">
        <div class="card-header"><h3>💰 My Dues</h3></div>
        <div class="card-body" style="padding: 0">
          <DataTable :columns="dueCols" :rows="myDues" search-placeholder="Search dues…" />
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>🎫 My Tickets</h3></div>
        <div class="card-body" style="padding: 6px 10px">
          <div v-for="t in myTickets" :key="t.id" style="display: flex; align-items: center; gap: 8px; padding: 7px 0; border-bottom: 1px solid #f5f5f5">
            <span style="font-size: 13px">🎫</span>
            <div style="flex: 1; min-width: 0">
              <div style="font-size: 11px; font-weight: 500; color: #333">{{ t.subject }}</div>
              <div style="font-size: 9px; color: #888">{{ t.id }} · {{ t.date }}</div>
            </div>
            <span class="pill" :style="{ background: statusColor(t.status) + '22', color: statusColor(t.status) }">{{ t.status }}</span>
          </div>
          <div v-if="!myTickets.length" style="padding: 16px; text-align: center; color: #999; font-size: 11px">No tickets.</div>
        </div>
      </div>
    </template>
  </div>
</template>
