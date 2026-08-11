<script setup lang="ts">
/**
 * BookingDetailDrawer — mirrors the HTML PWA showDetailPanel('Booking'):
 * detail stats row + Payment Summary + Payment Schedule with
 * Paid/Overdue/Upcoming badges and terms/progress header.
 */
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '@/api/client'
import { useDataStore } from '@/stores/data'
import { showToast } from '@/toast'
import type { Booking } from '@/api/types'

const props = defineProps<{ booking: Booking | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()
const tab = ref('overview')
const schedules = ref<any[]>([])

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    schedules.value = (r.data.collections.booking_schedules as any[]) ?? []
  }
})
watch(() => props.booking, () => (tab.value = 'overview'))

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

/** Parse a formatted ৳ string (e.g. "৳ 1.8 Cr", "৳ 5,00,000") into a number. */
const num = (v: unknown): number => {
  if (typeof v === 'number') return v
  const str = String(v ?? '').replace(/[৳,\s]/g, '')
  const m = str.match(/^([0-9.]+)(Cr|Lac)?$/i)
  if (!m) return 0
  const n = parseFloat(m[1])
  return m[2] ? (m[2].toLowerCase() === 'cr' ? n * 10000000 : n * 100000) : n
}

function statusColor(s: string): string {
  const map: Record<string, string> = {
    Confirmed: '#2e7d32', 'Pending Review': '#e65100', Booked: '#2f80ed',
    'Handed Over': '#2e7d32', Cancelled: '#c62828', Paid: '#2e7d32',
    Overdue: '#c62828', Upcoming: '#e65100'
  }
  return map[s] ?? '#555'
}

const installments = computed(() => {
  const b = props.booking
  if (!b) return []
  // real schedule from booking_schedules collection
  const sched = schedules.value.find((s: any) => String(s.bookingId || s.id || s.booking) === String(b.id))
  if (sched?.installments?.length) {
    return (sched.installments as { no?: string; date: string; amount: number; status: string }[]).map((x: any, i: number) => ({ no: x.no ?? String(i + 1), date: x.date, amount: Number(x.amount) || 0, status: x.status }))
  }
  return computed_installments()
})
function computed_installments(): { no: string; date: string; amount: number; status: string }[] {
  const b = props.booking
  const list = (b as unknown as { installments?: { no?: string; date: string; amount: number; status: string }[] })?.installments as { no?: string; date: string; amount: number; status: string }[] | undefined
  if (list?.length) return list.map((x, i) => ({ no: x.no ?? String(i + 1), date: x.date, amount: x.amount, status: x.status }))
  // derive a default schedule: advance then 12 monthly of the remainder
  if (!b || !b.price) return []
  const total = num(b.price)
  const adv = num(b.advance ?? b.total_paid)
  const rem = total - adv
  const rows: { no: string; date: string; amount: number; status: string }[] = [{ no: '1', date: b.date || '—', amount: adv, status: 'Paid' }]
  if (rem > 0) {
    const m = Math.round(rem / 12)
    for (let i = 0; i < 12; i++) {
      rows.push({ no: String(i + 2), date: 'Monthly ' + (i + 1), amount: m, status: i === 0 ? 'Upcoming' : 'Upcoming' })
    }
  }
  return rows.slice(0, 13)
}

const paidCount = computed(() => installments.value.filter((i) => i.status === 'Paid').length)
const paidAmt = computed(() => installments.value.filter((i) => i.status === 'Paid').reduce((s, i) => s + (i.amount || 0), 0))
const totalAmt = computed(() => installments.value.reduce((s, i) => s + (i.amount || 0), 0))

const data = useDataStore()
const payAmt = ref('')
const payMode = ref('Cash')
const payRef = ref('')
const payBusy = ref(false)
const payErr = ref('')
const bookingPayments = computed(() => {
  const inv = (props.booking as unknown as { sales_invoice?: string; salesInvoice?: string }).sales_invoice ?? (props.booking as unknown as { sales_invoice?: string; salesInvoice?: string }).salesInvoice ?? ''
  if (!inv) return []
  return data.payments
    .filter((p) => String((p as unknown as { invoiceId?: string }).invoiceId ?? '') === inv)
    .map((p) => ({
      id: String((p as unknown as { id?: string }).id ?? ''),
      date: String((p as unknown as { date?: string }).date ?? '—'),
      method: String((p as unknown as { method?: string }).method ?? (p as unknown as { mode_of_payment?: string }).mode_of_payment ?? 'Cash'),
      amount: Number((p as unknown as { amount?: number }).amount) || 0,
    }))
})
const recPaymentsTotal = computed(() => bookingPayments.value.reduce((s2, p) => s2 + (Number((p as unknown as { amount?: number }).amount) || 0), 0))
async function recordPayment() {
  const amt = Number(payAmt.value)
  if (!amt || amt <= 0) {
    payErr.value = 'Enter a valid amount'
    return
  }
  payBusy.value = true
  payErr.value = ''
  try {
    const r = await api.call<{ payment_entry?: string; amount?: number }>('booking_payment', {
      name: props.booking?.id ?? '',
      amount: amt,
      mode_of_payment: payMode.value,
      reference_no: payRef.value || undefined,
    })
    if (r.ok) {
      payAmt.value = ''
      payRef.value = ''
      payBusy.value = false
      showToast('Payment recorded — ' + (r.data?.payment_entry ?? 'PE-' + String(amt)), 'success')
      await data.loadPayments()
    } else {
      payErr.value = 'Payment failed — ' + ((r as unknown as { error?: string }).error || 'server error')
    }
  } catch (e) {
    payErr.value = 'Payment failed — ' + String(e)
  }
  payBusy.value = false
}
const pct = computed(() => (totalAmt.value ? Math.round((paidAmt.value / totalAmt.value) * 100) : 0))

const today = new Date().toISOString().slice(0, 10)
function instStatus(i: { date: string; amount: number; status: string }): { label: string; color: string; overdue: boolean } {
  if (i.status === 'Paid') return { label: 'Paid', color: '#2e7d32', overdue: false }
  const over = i.date !== '—' && i.date < today && !i.date.startsWith('Monthly')
  return over ? { label: 'Overdue', color: '#c62828', overdue: true } : { label: i.status || 'Upcoming', color: '#e65100', overdue: false }
}
</script>

<template>
  <div v-if="booking" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 540px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <div class="drawer-header" style="flex-shrink: 0">
        <h3 style="display: flex; align-items: center; gap: 8px">
          📋 Booking: {{ booking.id }}
          <span class="pill" :style="{ background: statusColor(booking.status) + '22', color: statusColor(booking.status) }">{{ booking.status }}</span>
        </h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto">
        <!-- detail stats -->
        <div class="stats-row" style="grid-template-columns: repeat(auto-fill, minmax(130px, 1fr))">
          <div class="stat-card"><div class="label">Client</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ booking.client }}</div></div>
          <div class="stat-card"><div class="label">Property</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ booking.property }}</div></div>
          <div class="stat-card"><div class="label">Unit</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ booking.unit || '—' }}</div></div>
          <div class="stat-card"><div class="label">Date</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ booking.date || '—' }}</div></div>
          <div class="stat-card"><div class="label">Type</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ booking.type || '—' }}</div></div>
        </div>

        <!-- payment summary -->
        <div style="margin-top: 12px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 6px">Payment Summary</h3>
          <div class="stats-row" style="grid-template-columns: 1fr 1fr 1fr">
            <div class="stat-card"><div class="label">Total Price</div><div style="font-size: 13px; font-weight: 700; color: #333; margin-top: 2px">{{ bdt(num(booking.price)) }}</div></div>
            <div class="stat-card"><div class="label">Advance Paid</div><div style="font-size: 13px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ bdt(num(booking.advance ?? booking.total_paid)) }}</div></div>
            <div class="stat-card"><div class="label">Due</div><div style="font-size: 13px; font-weight: 700; color: #c62828; margin-top: 2px">{{ bdt(num(booking.price) - num(booking.advance ?? booking.total_paid)) }}</div></div>
          </div>
        </div>

        <!-- payment schedule -->
        <div style="margin-top: 12px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 6px">💰 Recorded Payments</h3>
          <div v-if="bookingPayments.length" style="display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px">
            <div v-for="p in bookingPayments" :key="p.id + '-' + p.amount" style="display: flex; align-items: center; justify-content: space-between; font-size: 11px">
              <span style="color: #555">{{ p.date }} · {{ p.method }}</span>
              <span style="font-weight: 700; color: #2e7d32">{{ bdt(p.amount) }}</span>
            </div>
          </div>
          <div v-else style="font-size: 11px; color: #999; margin-bottom: 8px">No payments recorded against this booking yet.</div>
          <div style="background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 8px; margin-bottom: 10px">
            <div style="font-size: 11px; font-weight: 700; color: #333; margin-bottom: 6px">📥 Record a payment</div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap">
              <input v-model="payAmt" type="number" placeholder="Amount (৳)" style="flex: 1 1 90px; min-width: 0; padding: 5px 8px; font-size: 11px; border: 1px solid #ddd; border-radius: 6px" />
              <select v-model="payMode" style="padding: 5px 6px; font-size: 11px; border: 1px solid #ddd; border-radius: 6px; background: #fff">
                <option>Cash</option><option>Bank Transfer</option><option>bKash</option><option>Check</option>
              </select>
              <input v-model="payRef" placeholder="Ref no (optional)" style="flex: 1 1 120px; min-width: 0; padding: 5px 8px; font-size: 11px; border: 1px solid #ddd; border-radius: 6px" />
            </div>
            <div v-if="payErr" style="font-size: 10px; color: #c62828; margin-top: 4px">{{ payErr }}</div>
            <button :disabled="payBusy" @click="recordPayment" style="margin-top: 6px; background: #2e7d32; color: #fff; border: none; border-radius: 6px; padding: 5px 14px; font-size: 11px; font-weight: 600; cursor: pointer; width: 100%">
              {{ payBusy ? 'Recording…' : 'Record payment' }}
            </button>
          </div>
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 6px">Payment Schedule</h3>
          <div style="padding: 10px; background: #fff; border: 1px solid #e8e8e8; border-radius: 6px">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px">
              <span style="font-size: 10px; font-weight: 600; color: #2f80ed">{{ booking.terms || 'Payment Plan' }}</span>
              <span style="font-size: 9px; color: #555">{{ paidCount }}/{{ installments.length }} paid · {{ bdt(paidAmt) }} of {{ bdt(totalAmt) }}</span>
            </div>
            <!-- progress -->
            <div style="height: 4px; background: #e0e0e0; border-radius: 2px; overflow: hidden; margin-bottom: 6px">
              <div :style="{ width: pct + '%', background: '#2e7d32', height: '100%' }"></div>
            </div>
            <div class="table-wrap">
              <table class="rem-table" style="font-size: 10px; width: 100%">
                <thead><tr><th>#</th><th>Date</th><th class="num">Amount</th><th>Status</th></tr></thead>
                <tbody>
                  <tr v-for="(i, idx) in installments" :key="idx">
                    <td style="padding: 3px; font-size: 9px; color: #888">{{ i.no }}</td>
                    <td style="padding: 3px; font-size: 9px" :style="{ color: instStatus(i).overdue ? '#c62828' : '#555' }">{{ i.date }}{{ instStatus(i).overdue ? ' ⚠' : '' }}</td>
                    <td style="padding: 3px; font-size: 9px; text-align: right; font-weight: 600">{{ bdt(i.amount) }}</td>
                    <td style="padding: 3px">
                      <span class="badge-status" :style="{ background: instStatus(i).color + '22', color: instStatus(i).color, padding: '1px 6px', borderRadius: '4px', fontSize: '8px', fontWeight: 600 }">{{ instStatus(i).label }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- status actions -->
        <div style="margin-top: 14px; display: flex; gap: 6px; flex-wrap: wrap">
          <button class="action-btn" style="color: #2e7d32" @click="emit('status', 'Confirmed')">✅ Confirm</button>
          <button class="action-btn" style="color: #2f80ed" @click="emit('status', 'Booked')">📋 Booked</button>
          <button class="action-btn" style="color: #2e7d32" @click="emit('status', 'Handed Over')">🔑 Hand Over</button>
          <button class="action-btn" style="color: #c62828" @click="emit('status', 'Cancelled')">✕ Cancel</button>
        </div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
        <button class="drawer-btn" @click="emit('close')">Close</button>
        <button class="drawer-btn primary" @click="emit('status', 'Confirmed')">✓ Confirm</button>
      </div>
    </div>
  </div>
</template>
