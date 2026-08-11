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
import { showToast } from '@/toast'

const auth = useAuthStore()
const bookings = ref<any[]>([])
const detailBk = ref<any | null>(null)
const payBusy = ref<string | null>(null)
async function payInst(bk: any, amt: number) {
  if (payBusy.value) return
  payBusy.value = 'x'
  const r = await api.call('booking_payment', { name: bk.id ?? bk.name, amount: amt, mode_of_payment: 'Online', reference_no: 'Portal-' + Date.now() })
  payBusy.value = null
  if (r.ok) {
    showToast('Installment paid — thank you!')
    const res = await api.call('bookings_pipeline', {})
    if (res.ok) bookings.value = ((res.data as any)?.bookings ?? (res.data as any) ?? []) as any[]
  } else {
    showToast('Payment failed — ' + String((r as unknown as { error?: string }).error || 'try again'))
  }
}
const bkPaid = (bk: any) => Number(bk?.paid ?? 0) || 0
const bkInsts = (bk: any) => Array.isArray(bk?.installments) ? (bk.installments as any[]) : []

const dues = ref<any[]>([])
const tickets = ref<any[]>([])
const payments = ref<any[]>([])
const invoices = ref<any[]>([])
const loading = ref(true)

const me = computed(() => String(auth.user || '').toLowerCase())
const myName = computed(() => String(auth.fullName || '').toLowerCase())

const mine = (arr: any[], nameField: string) => arr.filter((x) => {
  const n = String(x[nameField] || '').toLowerCase().trim()
  if (!n) return false
  return n.includes(me.value) || n.includes(myName.value) || me.value.includes(n)
})

const myBookings = computed(() => mine(bookings.value, 'client'))
const myDues = computed(() => mine(dues.value, 'customer'))
const myTickets = computed(() => mine(tickets.value, 'customer'))
const myPayments = computed(() => mine(payments.value, 'client'))
const myInvoices = computed(() => mine(invoices.value, 'client'))

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    bookings.value = (r.data.collections.bookings as any[]) ?? []
    dues.value = (r.data.collections.dues as any[]) ?? []
    tickets.value = (r.data.collections.supportTickets as any[]) ?? []
    payments.value = (r.data.collections.payments as any[]) ?? []
    invoices.value = (r.data.collections.invoices as any[]) ?? []
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

async function payInvoice(inv: any) {
  const r = await api.startPayment(inv.id)
  if (!r.ok || !r.data?.redirect) {
    showToast('⚠ Could not start payment' + ((r as { error?: string }).error ? ' — ' + (r as { error?: string }).error : ''))
    return
  }
  showToast('↗ Opening the payment gateway…')
  window.open(r.data.redirect, '_blank')
  setTimeout(() => {
    api.call<{ collections: Record<string, unknown> }>('bootstrap').then((rr) => {
      if (rr.ok && rr.data) payments.value = (rr.data.collections.payments as any[]) ?? []
    })
  }, 8000)
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
          <DataTable :columns="bookingCols" :rows="myBookings" search-placeholder="Search bookings…" :actions="[{ label: 'View', onClick: (r: any) => (detailBk = r) }]" />
        </div>
      </div>

      <!-- booking detail drawer -->
      <div v-if="detailBk" class="drawer-sheet" style="width: 640px; max-width: 100vw; padding: 16px; overflow-y: auto">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px">
          <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #2f80ed, #56ccf2); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px">🏠</div>
          <div style="flex: 1; min-width: 0">
            <div style="font-size: 14px; font-weight: 700">{{ detailBk.id ?? detailBk.name }}</div>
            <div style="font-size: 10px; color: #828282">{{ detailBk.property }} · {{ detailBk.unit || '—' }}</div>
          </div>
          <button style="border: 1px solid #ddd; background: #fff; border-radius: 8px; padding: 6px 10px; cursor: pointer; font-size: 11px" @click="detailBk = null">✕ Close</button>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px">
          <div class="stat-card"><div style="font-size: 9px; color: #828282">Price</div><div style="font-size: 13px; font-weight: 700">{{ bdt(Number(detailBk.price) || 0) }}</div></div>
          <div class="stat-card"><div style="font-size: 9px; color: #828282">Paid</div><div style="font-size: 13px; font-weight: 700; color: #27ae60">{{ bdt(bkPaid(detailBk)) }}</div></div>
          <div class="stat-card"><div style="font-size: 9px; color: #828282">Balance</div><div style="font-size: 13px; font-weight: 700; color: #c62828">{{ bdt(Math.max(0, Number(detailBk.price) - bkPaid(detailBk))) }}</div></div>
        </div>
        <h3 style="font-size: 11px; font-weight: 700; margin: 8px 0 6px">📅 Payment Schedule</h3>
        <div v-if="bkInsts(detailBk).length" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 10px">
          <div v-for="(inst, i) in bkInsts(detailBk)" :key="i" style="display: flex; align-items: center; gap: 8px; background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 8px 10px">
            <div style="flex: 1; min-width: 0">
              <div style="font-size: 11px; font-weight: 600">{{ inst.label || inst.title || ('Installment ' + (i + 1)) }}</div>
              <div style="font-size: 10px; color: #828282">Due {{ inst.date || inst.dueDate || '—' }}</div>
            </div>
            <div style="font-size: 12px; font-weight: 700">{{ bdt(Number(inst.amount) || 0) }}</div>
            <span v-if="String(inst.status || '').toLowerCase() === 'paid'" style="font-size: 10px; font-weight: 700; color: #27ae60; background: #eafaf1; padding: 3px 8px; border-radius: 10px">Paid ✓</span>
            <button v-else style="border: none; background: #2f80ed; color: #fff; border-radius: 8px; padding: 6px 12px; cursor: pointer; font-size: 11px; font-weight: 600" :disabled="payBusy !== null" @click="payInst(detailBk, Number(inst.amount) || 0)">{{ payBusy ? '…' : 'Pay' }}</button>
          </div>
        </div>
        <div v-else style="font-size: 11px; color: #828282; background: #fafafa; border: 1px dashed #ddd; border-radius: 8px; padding: 12px; margin-bottom: 10px">No installment schedule on this booking.</div>
        <h3 style="font-size: 11px; font-weight: 700; margin: 8px 0 6px">Status</h3>
        <span style="font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 12px; background: #eef4ff; color: #2f80ed">{{ detailBk.status }}</span>
      </div>
      <div class="card" style="margin-bottom: 10px">
        <div class="card-header"><h3>💰 My Dues</h3></div>
        <div class="card-body" style="padding: 0">
          <DataTable :columns="dueCols" :rows="myDues" search-placeholder="Search dues…" />
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3>💳 My Invoices</h3></div>
        <div v-if="!myInvoices.length" style="padding: 16px; text-align: center; color: #999; font-size: 11px">No invoices.</div>
        <div v-else style="display: flex; flex-direction: column; gap: 8px; padding: 8px 0">
          <div v-for="inv in myInvoices.slice(0, 8)" :key="inv.id"
            style="display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-bottom: 1px solid #f5f5f5">
            <div style="flex: 1; min-width: 0">
              <div style="font-size: 12px; font-weight: 600; color: #1f2937">{{ inv.id }}</div>
              <div style="font-size: 10px; color: #94a3b8">{{ inv.project }}{{ inv.unit ? ' · ' + inv.unit : '' }} · due {{ inv.dueDate }}</div>
            </div>
            <div style="font-size: 11px; font-weight: 700; color: #1f2937">৳{{ Number(inv.amount || 0).toLocaleString() }}</div>
            <span v-if="String(inv.status || '').toLowerCase() === 'paid'"
              style="font-size: 10px; padding: 3px 8px; border-radius: 10px; background: #dcfce7; color: #166534; font-weight: 600">Paid</span>
            <button v-else @click="payInvoice(inv)"
              style="border: 0; background: #2f80ed; color: #fff; font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 8px; cursor: pointer">Pay</button>
          </div>
        </div>
        <div class="card-header" style="margin-top: 4px"><h3>🎫 My Tickets</h3></div>
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
