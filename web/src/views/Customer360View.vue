<template>
  <div class="fade-in" v-if="me">
    <!-- header -->
    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px">
      <div style="width: 46px; height: 46px; border-radius: 12px; background: linear-gradient(135deg, #2f80ed, #9b51e0); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 17px; flex-shrink: 0">{{ initials }}</div>
      <div style="flex: 1; min-width: 0">
        <h2 class="page-title" style="margin: 0">{{ me }}</h2>
        <div style="font-size: 10px; color: #8b90a0; margin-top: 2px">
          {{ lead ? lead.source : '' }}{{ lead && lead.source ? ' · ' : '' }}{{ _t('Customer 360') }} · {{ _t('last contact') }} {{ lead ? (lead.last_contact || '—') : '—' }}
        </div>
      </div>
      <div style="display: flex; gap: 6px; flex-wrap: wrap">
        <a v-if="lead && lead.phone" :href="'tel:' + (lead.phone || '').replace(/[^0-9+]/g, '')" style="background:#eaf2fe;color:#2f80ed;padding:6px 12px;border-radius:8px;font-size:11px;font-weight:600;text-decoration:none">📞 {{ lead.phone }}</a>
        <a v-if="lead && lead.email" :href="'mailto:' + lead.email" style="background:#eaf2fe;color:#2f80ed;padding:6px 12px;border-radius:8px;font-size:11px;font-weight:600;text-decoration:none">✉ {{ lead.email }}</a>
        <button @click="router.push('/leads?lead=' + (lead ? lead.id : ''))" style="background:#2f80ed;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-size:11px;font-weight:600;cursor:pointer">{{ _t('Open lead') }}</button>
      </div>
    </div>

    <!-- numbers -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px">
      <div style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:10px 12px">
        <div style="font-size:9px;color:#8b90a0;text-transform:uppercase;letter-spacing:.4px">{{ _t('Total paid') }}</div>
        <div style="font-size:16px;font-weight:700;color:#1f2937">{{ bdt(totalPaid) }}</div>
      </div>
      <div style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:10px 12px">
        <div style="font-size:9px;color:#8b90a0;text-transform:uppercase;letter-spacing:.4px">{{ _t('Outstanding') }}</div>
        <div style="font-size:16px;font-weight:700;color:#d64545">{{ bdt(outstanding) }}</div>
      </div>
      <div style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:10px 12px">
        <div style="font-size:9px;color:#8b90a0;text-transform:uppercase;letter-spacing:.4px">{{ _t('Bookings') }}</div>
        <div style="font-size:16px;font-weight:700;color:#1f2937">{{ myBookings.length }}</div>
      </div>
      <div style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:10px 12px">
        <div style="font-size:9px;color:#8b90a0;text-transform:uppercase;letter-spacing:.4px">{{ _t('Open leads') }}</div>
        <div style="font-size:16px;font-weight:700;color:#1f2937">{{ openLeads.length }}</div>
      </div>
    </div>

    <!-- journey timeline -->
    <div style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:12px 14px;margin-bottom:12px">
      <h3 style="margin:0 0 10px;font-size:12px;color:#1f2937">🛣 {{ _t('Customer journey') }}</h3>
      <div v-if="journey.length === 0" style="font-size:11px;color:#8b90a0">{{ _t('No journey events yet') }}</div>
      <div v-for="(e, i) in journey" :key="i" style="display:flex;gap:10px;position:relative;padding-bottom:10px">
        <div style="width:20px;height:20px;border-radius:50%;background:#eaf2fe;color:#2f80ed;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0">{{ e.icon }}</div>
        <div style="flex:1;min-width:0;font-size:11px">
          <span style="font-weight:600;color:#1f2937">{{ e.title }}</span>
          <span style="color:#8b90a0"> · {{ e.detail }}</span>
          <span style="color:#b0b5c4;font-size:10px"> · {{ e.date }}</span>
        </div>
      </div>
    </div>

    <!-- tabs -->
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
      <button v-for="t in tabs" :key="t.id" @click="setTab(t.id)" :style="{ background: tab === t.id ? '#2f80ed' : '#fff', color: tab === t.id ? '#fff' : '#4b5563', border: '1px solid ' + (tab === t.id ? '#2f80ed' : '#e5e7eb'), padding: '6px 12px', borderRadius: 8, fontSize: 11, fontWeight: 600, cursor: 'pointer' }">{{ t.label }} <span style="opacity:.75">({{ t.count }})</span></button>
    </div>

    <div v-if="tab === 'leads'" style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:4px 0">
      <div v-for="l in myLeads" :key="l.id" style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-bottom:1px solid #f5f6f8;font-size:11px;cursor:pointer" @click="router.push('/leads?lead=' + l.id)">
        <span style="font-weight:600;color:#1f2937;flex:1">{{ l.id }}</span>
        <span style="color:#8b90a0">{{ l.source || '' }}</span>
        <span :style="{ background: l.status === 'Lost' ? '#fee2e2' : '#eaf2fe', color: l.status === 'Lost' ? '#d64545' : '#2f80ed', padding: '2px 8px', borderRadius: 10, fontWeight: 600 }">{{ l.status }}</span>
      </div>
      <div v-if="myLeads.length === 0" style="padding:12px;font-size:11px;color:#8b90a0">{{ _t('No leads') }}</div>
    </div>

    <div v-if="tab === 'bookings'" style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:4px 0">
      <div v-for="b in myBookings" :key="b.id" style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-bottom:1px solid #f5f6f8;font-size:11px;cursor:pointer" @click="router.push('/bookings?bk=' + b.id)">
        <span style="font-weight:600;color:#1f2937;flex:1">🧾 {{ b.id }}</span>
        <span style="color:#8b90a0">{{ b.property }} {{ b.unit }}</span>
        <span style="color:#2f80ed;font-weight:600">{{ bdt(Number(b.price) || 0) }}</span>
        <span :style="{ background: b.status === 'Cancelled' ? '#fee2e2' : '#eaf2fe', color: b.status === 'Cancelled' ? '#d64545' : '#2f80ed', padding: '2px 8px', borderRadius: 10, fontWeight: 600 }">{{ b.status }}</span>
      </div>
      <div v-if="myBookings.length === 0" style="padding:12px;font-size:11px;color:#8b90a0">{{ _t('No bookings') }}</div>
    </div>

    <div v-if="tab === 'invoices'" style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:4px 0">
      <div v-for="inv in myInvoices" :key="inv.id" style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-bottom:1px solid #f5f6f8;font-size:11px;cursor:pointer" @click="router.push('/finance')">
        <span style="font-weight:600;color:#1f2937;flex:1">🧾 {{ inv.id }}</span>
        <span style="color:#8b90a0">{{ inv.project }} {{ inv.unit }}</span>
        <span style="color:#2f80ed;font-weight:600">{{ bdt(inv.amount) }}</span>
        <span :style="{ background: inv.status === 'Paid' ? '#dcfce7' : inv.status === 'Overdue' ? '#fee2e2' : '#fef3c7', color: inv.status === 'Paid' ? '#16a34a' : inv.status === 'Overdue' ? '#d64545' : '#b45309', padding: '2px 8px', borderRadius: 10, fontWeight: 600 }">{{ inv.status }}</span>
      </div>
      <div v-if="myInvoices.length === 0" style="padding:12px;font-size:11px;color:#8b90a0">{{ _t('No invoices') }}</div>
    </div>

    <div v-if="tab === 'payments'" style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:4px 0">
      <div v-for="p in myPayments" :key="p.id" style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-bottom:1px solid #f5f6f8;font-size:11px;cursor:pointer" @click="router.push('/finance')">
        <span style="font-weight:600;color:#1f2937;flex:1">💵 {{ p.id }}</span>
        <span style="color:#8b90a0">{{ p.date }} · {{ p.method }}</span>
        <span style="color:#16a34a;font-weight:600">+{{ bdt(p.amount) }}</span>
      </div>
      <div v-if="myPayments.length === 0" style="padding:12px;font-size:11px;color:#8b90a0">{{ _t('No payments') }}</div>
    </div>

    <div v-if="tab === 'dues'" style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:4px 0">
      <div v-for="d in myDues" :key="d.id" style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-bottom:1px solid #f5f6f8;font-size:11px;cursor:pointer" @click="router.push('/dues?due=' + d.id)">
        <span style="font-weight:600;color:#1f2937;flex:1">⚠ {{ d.id }}</span>
        <span style="color:#8b90a0">{{ d.project || '' }}</span>
        <span style="color:#d64545;font-weight:600">{{ bdt(dueAmt(d)) }}</span>
        <span :style="{ background: d.status === 'Critical' ? '#fee2e2' : d.status === 'Overdue' ? '#fef3c7' : '#eaf2fe', color: d.status === 'Critical' ? '#d64545' : d.status === 'Overdue' ? '#b45309' : '#2f80ed', padding: '2px 8px', borderRadius: 10, fontWeight: 600 }">{{ d.status }}</span>
      </div>
      <div v-if="myDues.length === 0" style="padding:12px;font-size:11px;color:#8b90a0">{{ _t('No dues') }}</div>
    </div>

    <div v-if="tab === 'tickets'" style="background:#fff;border:1px solid #eef0f4;border-radius:12px;padding:4px 0">
      <div v-for="t in myTickets" :key="t.id" style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-bottom:1px solid #f5f6f8;font-size:11px;cursor:pointer" @click="router.push('/tickets')">
        <span style="font-weight:600;color:#1f2937;flex:1">{{ t.subject }}</span>
        <span style="color:#8b90a0">{{ t.date || '' }}</span>
        <span :style="{ background: t.status === 'Closed' ? '#dcfce7' : '#fef3c7', color: t.status === 'Closed' ? '#16a34a' : '#b45309', padding: '2px 8px', borderRadius: 10, fontWeight: 600 }">{{ t.status }}</span>
      </div>
      <div v-if="myTickets.length === 0" style="padding:12px;font-size:11px;color:#8b90a0">{{ _t('No tickets') }}</div>
    </div>
  </div>
  <div v-else style="padding: 40px; text-align: center; color: #8b90a0; font-size: 12px">{{ _t('Customer not found') }}</div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { _t } from '@/i18n'

const route = useRoute()
const router = useRouter()
const data = useDataStore()

const bdt = (n: number) => (n ? '৳' + (n / 10000000).toFixed(2) + ' Cr' : '৳0')
const dueAmt = (d: unknown) => Number((d as { due?: number }).due) || 0

const me = computed(() => String(route.params.name || '').trim())
const mine = (rows: { client?: string; customer?: string }[]) =>
  me.value ? rows.filter((r) => String(r.client || r.customer || '').toLowerCase() === me.value.toLowerCase()) : []

const myLeads = computed(() => (me.value ? data.leads.filter((l) => l.name.toLowerCase() === me.value.toLowerCase()) : []))
const lead = computed(() => myLeads.value[0] || null)
const openLeads = computed(() => myLeads.value.filter((l) => l.status !== 'Converted' && l.status !== 'Lost'))
const myBookings = computed(() => mine(data.bookings) as typeof data.bookings)
const myInvoices = computed(() => mine(data.invoices) as typeof data.invoices)
const myPayments = computed(() => mine(data.payments) as typeof data.payments)
const myDues = computed(() => mine(data.dues) as typeof data.dues)
const myTickets = computed(() => mine(data.tickets) as typeof data.tickets)

const totalPaid = computed(() => myPayments.value.reduce((s, p) => s + (Number(p.amount) || 0), 0))
const outstanding = computed(() => myDues.value.reduce((s, d) => s + (Number((d as { amount?: number }).amount) || 0), 0))

const initials = computed(() =>
  me.value
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
)

const journey = computed(() => {
  const ev: { icon: string; title: string; detail: string; date: string; t: number }[] = []
  for (const l of myLeads.value) ev.push({ icon: '🧭', title: l.status, detail: l.source || '', date: l.last_contact || '', t: Date.parse(l.last_contact || '') || 0 })
  for (const b of myBookings.value) ev.push({ icon: '📄', title: 'Booking ' + b.id, detail: b.property + ' ' + b.unit, date: b.date || '', t: Date.parse(b.date || '') || 0 })
  for (const inv of myInvoices.value) ev.push({ icon: '🧾', title: inv.id + ' · ' + inv.status, detail: (inv.project || '') + ' ' + (inv.unit || ''), date: inv.dueDate || inv.issuedDate || '', t: Date.parse(inv.dueDate || inv.issuedDate || '') || 0 })
  for (const p of myPayments.value) ev.push({ icon: '💵', title: 'Payment ' + p.id, detail: p.method + ' · ' + (p.reference || ''), date: p.date || '', t: Date.parse(p.date || '') || 0 })
  return ev.sort((a, b) => b.t - a.t).slice(0, 10)
})

const tabs = computed(() => [
  { id: 'leads', label: 'Leads', count: myLeads.value.length },
  { id: 'bookings', label: 'Bookings', count: myBookings.value.length },
  { id: 'invoices', label: 'Invoices', count: myInvoices.value.length },
  { id: 'payments', label: 'Payments', count: myPayments.value.length },
  { id: 'dues', label: 'Dues', count: myDues.value.length },
  { id: 'tickets', label: 'Tickets', count: myTickets.value.length },
])
const tab = ref('leads')
function setTab(t: string) {
  tab.value = t
  void router.replace({ query: { ...route.query, tab: t } })
}
watch(
  () => route.query.tab,
  (t) => {
    if (t && tabs.value.some((x) => x.id === t)) tab.value = String(t)
  },
  { immediate: true }
)
</script>
