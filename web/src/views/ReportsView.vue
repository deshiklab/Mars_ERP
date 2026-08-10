<script setup lang="ts">
/**
 * ReportsView — 5-tab Reports & Dashboards (HTML parity):
 * Sales Pipeline (funnel + sources), Payment Collection (monthly chart),
 * Occupancy (units by status), Revenue vs Expense, Bulk Export.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useDataStore } from '@/stores/data'
import { showToast } from '@/toast'

const data = useDataStore()
const tab = ref('pipeline')
const period = ref('all')

const items = ref<any[]>([])
const payments = ref<any[]>([])
const invoices = ref<any[]>([])
const loading = ref(true)
const props_ = ref<{ units: { id: string; status: string; price: number }[] }[]>([])

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const arr = r.data.collections['bi_reports']
    items.value = Array.isArray(arr) ? (arr as any[]) : []
    payments.value = (r.data.collections.payments as any[]) ?? []
    invoices.value = (r.data.collections.invoices as any[]) ?? []
    const plist = (r.data.collections.properties as any[]) ?? []
    props_.value = plist.map((p) => ({
      units: (p.units ?? []).map((u: any) => ({ id: String(u.id ?? ''), status: String(u.status ?? 'Available'), price: Number(u.price) || 0 }))
    }))
  }
  loading.value = false
  data.loadLeads()
  data.loadBookings()
  data.loadDues()
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function inPeriod(d: string): boolean {
  if (period.value === 'all' || !d) return true
  const t = new Date(d).getTime()
  if (isNaN(t)) return true
  const days = period.value === '30d' ? 30 : period.value === '90d' ? 90 : 365
  return Date.now() - t <= days * 86400000
}

/* ── tab 1: SALES PIPELINE ── */
const funnelStages = ['New Inquiry', 'Site Visit', 'Negotiation', 'Booking', 'Downpayment', 'Installments', 'Converted', 'Lost']
const pipe = computed(() => {
  const leads = data.leads
  const conv = leads.filter((l) => l.status === 'Converted').length
  const lost = leads.filter((l) => l.status === 'Lost').length
  const active = leads.length - conv - lost
  const winRate = leads.length ? Math.round((conv / leads.length) * 100) : 0
  const pipeVal = leads.reduce((s, l) => s + (Number((l as { value?: unknown }).value) || 0), 0)
  const stages = funnelStages.map((st) => {
    const ls = leads.filter((l) => l.status === st)
    return { s: st, count: ls.length, pct: leads.length ? Math.round((ls.length / leads.length) * 100) : 0 }
  })
  const srcMap: Record<string, number> = {}
  leads.forEach((l) => { const k = String((l as { source?: unknown }).source || 'Unknown'); srcMap[k] = (srcMap[k] || 0) + 1 })
  const sources = Object.keys(srcMap).map((k) => ({ k, count: srcMap[k] })).sort((a, b) => b.count - a.count).slice(0, 8)
  return { total: leads.length, active, conv, lost, winRate, pipeVal, stages, sources }
})

/* ── tab 2: PAYMENT COLLECTION ── */
const monthly = computed(() => {
  const map: Record<string, { amt: number; count: number }> = {}
  payments.value.filter((p) => inPeriod(String(p.date))).forEach((p) => {
    const m = String(p.date).slice(0, 7)
    if (!map[m]) map[m] = { amt: 0, count: 0 }
    map[m].amt += Number(p.amount) || 0
    map[m].count++
  })
  const rows = Object.keys(map).sort().map((m) => ({ month: m, amt: map[m].amt, count: map[m].count }))
  return { rows, total: rows.reduce((s, r) => s + r.amt, 0) }
})
const maxMonth = computed(() => Math.max(...monthly.value.rows.map((r) => r.amt), 1))
const monthLabel = (m: string) => {
  const names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const [y, mo] = m.split('-')
  return `${names[Number(mo) - 1] ?? mo} '${y.slice(2)}`
}

/* ── tab 3: OCCUPANCY ── */
const occ = computed(() => {
  const flats = props_.value.flatMap((p) => p.units)
  const counts: Record<string, number> = {}
  flats.forEach((f) => { const k = String(f.status || 'unknown'); counts[k] = (counts[k] || 0) + 1 })
  const order = ['available', 'booked', 'reserved', 'sold', 'under_payment', 'Under Payment', 'Booked', 'Available', 'Reserved', 'Sold']
  const rows = order
    .filter((k) => counts[k])
    .map((k) => ({ k, n: counts[k] }))
    .concat(Object.keys(counts).filter((k) => !order.includes(k)).map((k) => ({ k, n: counts[k] })))
  const occupied = ['sold', 'booked', 'reserved', 'Booked', 'Reserved', 'Sold', 'Under Payment', 'under_payment'].reduce((s, k) => s + (counts[k] || 0), 0)
  const occPct = flats.length ? Math.round((occupied / flats.length) * 100) : 0
  return { total: flats.length, occupied, occPct, rows }
})
const occColor = (k: string) => (/available/i.test(k) ? '#2e7d32' : /sold/i.test(k) ? '#c62828' : /reserved/i.test(k) ? '#ff8f00' : /booked|under/i.test(k) ? '#2f80ed' : '#999')

/* ── tab 4: REVENUE vs EXPENSE ── */
const revExp = computed(() => {
  const byMonth: Record<string, { rev: number; exp: number }> = {}
  payments.value.filter((p) => inPeriod(String(p.date))).forEach((p) => {
    const m = String(p.date).slice(0, 7)
    if (!byMonth[m]) byMonth[m] = { rev: 0, exp: 0 }
    byMonth[m].rev += Number(p.amount) || 0
  })
  invoices.value.filter((i) => inPeriod(String(i.date))).forEach((i) => {
    const m = String(i.date).slice(0, 7)
    if (!byMonth[m]) byMonth[m] = { rev: 0, exp: 0 }
    byMonth[m].exp += Number(i.totalValue) || 0
  })
  const rows = Object.keys(byMonth).sort().map((m) => ({ month: m, ...byMonth[m] }))
  const rev = rows.reduce((s, r) => s + r.rev, 0)
  const exp = rows.reduce((s, r) => s + r.exp, 0)
  const max = Math.max(...rows.flatMap((r) => [r.rev, r.exp]), 1)
  return { rows, rev, exp, net: rev - exp, max }
})

/* ── tab 5: BULK EXPORT ── */
function exportCSV(name: string, rows: Record<string, unknown>[]) {
  if (!rows.length) { showToast('No data to export', 'info'); return }
  const cols = Array.from(new Set(rows.flatMap((r) => Object.keys(r)))).slice(0, 12)
  const csv = [cols.join(','), ...rows.map((r) => cols.map((c) => `"${String(r[c] ?? '').replace(/"/g, '""')}"`).join(','))].join('\n')
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  const a = document.createElement('a')
  a.href = url
  a.download = `${name}.csv`
  a.click()
  URL.revokeObjectURL(url)
  showToast(`Exported ${rows.length} rows`, 'success')
}
</script>

<template>
  <div class="fade-in">
    <div class="page-title">📊 Reports &amp; Dashboards</div>
    <div class="page-subtitle">{{ period === 'all' ? 'All Time' : period === '30d' ? 'Last 30 Days' : period === '90d' ? 'Last 90 Days' : 'Year To Date' }} · live from ERP data</div>

    <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 8px">
      <span v-for="t in [['pipeline', '📈 Sales Pipeline'], ['collection', '💰 Payment Collection'], ['occupancy', '🏢 Occupancy'], ['revenue', '📊 Revenue vs Expense'], ['export', '📤 Bulk Export']]" :key="t[0]"
        class="qa-tab" style="padding: 4px 12px; font-size: 10px; font-weight: 600; border-radius: 6px; cursor: pointer; margin-right: 4px"
        :style="tab === t[0] ? 'background: #2F80ED; color: #fff' : 'background: #f0f0f0; color: #666'"
        @click="tab = t[0]">{{ t[1] }}</span>
      <div style="flex: 1"></div>
      <select v-model="period" style="padding: 4px 8px; font-size: 10px; border: 1px solid #e0e0e0; border-radius: 6px; background: transparent">
        <option value="all">All Time</option>
        <option value="30d">Last 30 Days</option>
        <option value="90d">Last 90 Days</option>
        <option value="ytd">Year To Date</option>
      </select>
    </div>

    <div v-if="loading" style="text-align: center; color: #999; padding: 30px; font-size: 11px">Loading…</div>

    <!-- ═══ 1. SALES PIPELINE ═══ -->
    <template v-if="tab === 'pipeline'">
      <div class="stats-row" style="margin-bottom: 8px">
        <div class="stat-card"><div class="label">Total Leads</div><div class="value" style="color: #2F80ED">{{ pipe.total }}</div></div>
        <div class="stat-card"><div class="label">Active Pipeline</div><div class="value" style="color: #1565c0">{{ pipe.active }}</div></div>
        <div class="stat-card"><div class="label">Converted</div><div class="value" style="color: #2e7d32">{{ pipe.conv }}</div></div>
        <div class="stat-card"><div class="label">Win Rate</div><div class="value" style="color: #7b1fa2">{{ pipe.winRate }}%</div></div>
        <div class="stat-card"><div class="label">Pipeline Value</div><div class="value" style="color: #00838f">{{ bdt(pipe.pipeVal) }}</div></div>
        <div class="stat-card"><div class="label">Lost / Junk</div><div class="value" style="color: #c62828">{{ pipe.lost }}</div></div>
      </div>
      <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 8px">
        <div class="card">
          <div class="card-header"><h3>🔻 Funnel by Stage</h3></div>
          <div class="card-body" style="padding: 10px">
            <div v-for="st in pipe.stages" :key="st.s" style="display: flex; align-items: center; gap: 6px; padding: 3px 0">
              <div style="font-size: 9px; width: 110px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ st.s }}</div>
              <div style="flex: 1; height: 9px; background: #eef1f5; border-radius: 4px; overflow: hidden">
                <div :style="{ height: '100%', width: (st.pct || 0.5) + '%', minWidth: st.count ? '6px' : '0', background: st.s === 'Converted' ? '#2e7d32' : st.s === 'Lost' ? '#c62828' : '#2f80ed', borderRadius: '4px' }"></div>
              </div>
              <div style="font-size: 9px; font-weight: 600; width: 24px; text-align: right">{{ st.count }}</div>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header"><h3>🏆 Top Sources</h3></div>
          <div class="card-body" style="padding: 0">
            <table class="rem-table" style="border: none">
              <thead><tr><th>Source</th><th class="num">Leads</th></tr></thead>
              <tbody>
                <tr v-for="s in pipe.sources" :key="s.k"><td>{{ s.k }}</td><td class="num" style="font-weight: 600">{{ s.count }}</td></tr>
                <tr v-if="!pipe.sources.length"><td colspan="2" style="text-align: center; color: #999; padding: 20px">No data</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══ 2. PAYMENT COLLECTION ═══ -->
    <template v-if="tab === 'collection'">
      <div class="stats-row" style="margin-bottom: 8px">
        <div class="stat-card"><div class="label">Collected</div><div class="value" style="color: #2e7d32">{{ bdt(monthly.total) }}</div></div>
        <div class="stat-card"><div class="label">Months</div><div class="value" style="color: #1565c0">{{ monthly.rows.length }}</div></div>
        <div class="stat-card"><div class="label">Transactions</div><div class="value" style="color: #2f80ed">{{ payments.length }}</div></div>
      </div>
      <div class="card">
        <div class="card-header"><h3>💵 Monthly Collections</h3></div>
        <div class="card-body" style="padding: 14px 10px 6px">
          <div v-if="monthly.rows.length" style="display: flex; align-items: flex-end; gap: 10px; height: 170px; padding: 0 6px">
            <div v-for="r in monthly.rows" :key="r.month" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%">
              <div style="font-size: 9px; font-weight: 600; color: #1565c0; margin-bottom: 2px">{{ bdt(r.amt) }}</div>
              <div :style="{ width: '70%', height: Math.max((r.amt / maxMonth) * 130, 3) + 'px', background: 'linear-gradient(180deg, #4d94f0, #2f80ed)', borderRadius: '4px 4px 0 0', minWidth: '14px' }"></div>
              <div style="font-size: 9px; color: #666; margin-top: 4px">{{ monthLabel(r.month) }}</div>
              <div style="font-size: 8px; color: #aaa">{{ r.count }} txns</div>
            </div>
          </div>
          <div v-else style="text-align: center; color: #999; padding: 30px; font-size: 11px">No payments in this period</div>
        </div>
      </div>
    </template>

    <!-- ═══ 3. OCCUPANCY ═══ -->
    <template v-if="tab === 'occupancy'">
      <div class="stats-row" style="margin-bottom: 8px">
        <div class="stat-card"><div class="label">Total Units</div><div class="value" style="color: #1565c0">{{ occ.total }}</div></div>
        <div class="stat-card"><div class="label">Occupied</div><div class="value" style="color: #2e7d32">{{ occ.occupied }}</div></div>
        <div class="stat-card"><div class="label">Occupancy</div><div class="value" style="color: #7b1fa2">{{ occ.occPct }}%</div></div>
      </div>
      <div class="card">
        <div class="card-header"><h3>🏢 Units by Status</h3></div>
        <div class="card-body" style="padding: 12px">
          <div v-for="r in occ.rows" :key="r.k" style="display: flex; align-items: center; gap: 6px; padding: 4px 0">
            <div style="font-size: 9px; width: 130px; text-transform: capitalize; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ r.k }}</div>
            <div style="flex: 1; height: 10px; background: #eef1f5; border-radius: 4px; overflow: hidden">
              <div :style="{ height: '100%', width: (occ.total ? Math.round((r.n / occ.total) * 100) : 0) + '%', background: occColor(r.k), borderRadius: '4px' }"></div>
            </div>
            <div style="font-size: 9px; font-weight: 600; width: 24px; text-align: right">{{ r.n }}</div>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══ 4. REVENUE vs EXPENSE ═══ -->
    <template v-if="tab === 'revenue'">
      <div class="stats-row" style="margin-bottom: 8px">
        <div class="stat-card"><div class="label">Revenue (payments)</div><div class="value" style="color: #2e7d32">{{ bdt(revExp.rev) }}</div></div>
        <div class="stat-card"><div class="label">Invoiced</div><div class="value" style="color: #e65100">{{ bdt(revExp.exp) }}</div></div>
        <div class="stat-card"><div class="label">Net</div><div class="value" :style="{ color: revExp.net >= 0 ? '#2e7d32' : '#c62828' }">{{ bdt(revExp.net) }}</div></div>
      </div>
      <div class="card">
        <div class="card-header"><h3>📊 Revenue vs Invoiced by Month</h3></div>
        <div class="card-body" style="padding: 14px 10px 6px">
          <div v-if="revExp.rows.length" style="display: flex; align-items: flex-end; gap: 12px; height: 170px; padding: 0 6px">
            <div v-for="r in revExp.rows" :key="r.month" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%">
              <div style="display: flex; align-items: flex-end; gap: 3px; height: 135px">
                <div :style="{ width: '16px', height: Math.max((r.rev / revExp.max) * 125, 2) + 'px', background: '#2e7d32', borderRadius: '3px 3px 0 0' }" :title="'Rev ' + bdt(r.rev)"></div>
                <div :style="{ width: '16px', height: Math.max((r.exp / revExp.max) * 125, 2) + 'px', background: '#e65100', borderRadius: '3px 3px 0 0' }" :title="'Inv ' + bdt(r.exp)"></div>
              </div>
              <div style="font-size: 9px; color: #666; margin-top: 4px">{{ monthLabel(r.month) }}</div>
            </div>
          </div>
          <div v-else style="text-align: center; color: #999; padding: 30px; font-size: 11px">No data in this period</div>
          <div style="display: flex; justify-content: center; gap: 14px; margin-top: 8px; font-size: 9px; color: #666">
            <span><span style="display: inline-block; width: 9px; height: 9px; background: #2e7d32; border-radius: 2px; margin-right: 4px"></span>Revenue</span>
            <span><span style="display: inline-block; width: 9px; height: 9px; background: #e65100; border-radius: 2px; margin-right: 4px"></span>Invoiced</span>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══ 5. BULK EXPORT ═══ -->
    <template v-if="tab === 'export'">
      <div class="card">
        <div class="card-header"><h3>📤 Bulk Export</h3></div>
        <div class="card-body" style="padding: 14px">
          <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px">
            <button class="action-btn secondary" @click="exportCSV('leads', data.leads as unknown as Record<string, unknown>[])">🎯 Leads ({{ data.leads.length }})</button>
            <button class="action-btn secondary" @click="exportCSV('bookings', data.bookings as unknown as Record<string, unknown>[])">📄 Bookings ({{ data.bookings.length }})</button>
            <button class="action-btn secondary" @click="exportCSV('dues', data.dues as unknown as Record<string, unknown>[])">⏰ Dues ({{ data.dues.length }})</button>
            <button class="action-btn secondary" @click="exportCSV('payments', payments)">💵 Payments ({{ payments.length }})</button>
            <button class="action-btn secondary" @click="exportCSV('invoices', invoices)">🧾 Invoices ({{ invoices.length }})</button>
            <button class="action-btn secondary" @click="exportCSV('projects', data.projects as unknown as Record<string, unknown>[])">🏗 Projects ({{ data.projects.length }})</button>
          </div>
          <div style="font-size: 9px; color: #888; margin-top: 10px">CSV downloads of the live server data — opens in Excel / Google Sheets.</div>
        </div>
      </div>
    </template>
  </div>
</template>
