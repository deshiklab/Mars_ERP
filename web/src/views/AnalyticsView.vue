<script setup lang="ts">
/**
 * AnalyticsView — charts from live data (CSS bars, no canvas):
 * lead pipeline, booking status, dues buckets, cash flow in/out.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useDataStore } from '@/stores/data'
import StatsRow from '@/components/StatsRow.vue'
import { _t } from '@/i18n'

const data = useDataStore()
const loading = ref(true)

onMounted(async () => {
  await Promise.all([data.loadLeads(), data.loadBookings(), data.loadDues(), data.loadFinance()])
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) transactions.value = (r.data.collections.transactions as any[]) ?? []
  loading.value = false
})

const transactions = ref<any[]>([])

/* lead pipeline chart */
const leadStages = computed(() => {
  const stages = ['New Inquiry', 'Contacted', 'Site Visit', 'Negotiation', 'Booking', 'Lost']
  return stages.map((s) => ({ label: s, count: data.leads.filter((l) => l.status === s).length }))
})
const maxLeads = computed(() => Math.max(1, ...leadStages.value.map((s) => s.count)))

/* booking status chart */
const bookingStages = computed(() => {
  const counts = new Map<string, number>()
  data.bookings.forEach((b) => counts.set(b.status, (counts.get(b.status) ?? 0) + 1))
  return [...counts.entries()].map(([label, count]) => ({ label, count }))
})
const maxBookings = computed(() => Math.max(1, ...bookingStages.value.map((s) => s.count)))

/* dues buckets */
const dueBuckets = computed(() => {
  const b = (lo: number, hi?: number) =>
    data.dues.filter((d) => d.daysOverdue >= lo && (hi === undefined || d.daysOverdue < hi)).length
  return [
    { label: '0–30d', count: b(0, 31), color: '#2e7d32' },
    { label: '31–60d', count: b(31, 61), color: '#ff8f00' },
    { label: '60–90d', count: b(61, 91), color: '#e65100' },
    { label: '90d+', count: b(91), color: '#c62828' }
  ]
})
const maxDue = computed(() => Math.max(1, ...dueBuckets.value.map((s) => s.count)))

/* cash flow */
const cashFlow = computed(() => {
  const inflow = transactions.value.filter((t) => t.type === 'Inflow').reduce((s: number, t: any) => s + (t.amount ?? 0), 0)
  const outflow = transactions.value.filter((t) => t.type === 'Outflow').reduce((s: number, t: any) => s + (t.amount ?? 0), 0)
  const pct = inflow + outflow > 0 ? Math.round((inflow / (inflow + outflow)) * 100) : 50
  return { inflow, outflow, pct }
})

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

const stats = computed(() => [
  { label: _t('Hot Leads'), value: String(data.leads.length), color: '#2f80ed' },
  { label: 'Bookings', value: String(data.bookings.length), color: '#1565c0' },
  { label: 'Dues', value: String(data.dues.length), color: '#c62828' },
  { label: 'Net Cash', value: bdt(cashFlow.value.inflow - cashFlow.value.outflow), color: cashFlow.value.inflow >= cashFlow.value.outflow ? '#2e7d32' : '#c62828' }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">Analytics</span>
      <span class="page-subtitle">Live KPIs from the bridge</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading analytics…</p>

    <div v-else style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px">
      <!-- LEAD PIPELINE -->
      <div class="card">
        <div class="card-header"><h3>🎯 Lead Pipeline</h3></div>
        <div class="card-body" style="padding: 10px 14px">
          <div v-for="s in leadStages" :key="s.label" style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px">
            <span style="width: 80px; font-size: 10px; color: #555; text-align: right">{{ s.label }}</span>
            <div style="flex: 1; background: #f0f0f0; border-radius: 4px; height: 16px; overflow: hidden">
              <div :style="{ width: (s.count / maxLeads * 100) + '%', background: s.count > 0 ? '#2f80ed' : '#eee', height: '100%', borderRadius: '4px', transition: 'width .4s' }"></div>
            </div>
            <span style="width: 28px; font-size: 11px; font-weight: 700; color: #333">{{ s.count }}</span>
          </div>
        </div>
      </div>

      <!-- BOOKING STATUS -->
      <div class="card">
        <div class="card-header"><h3>📋 Bookings by Status</h3></div>
        <div class="card-body" style="padding: 10px 14px">
          <div v-for="s in bookingStages" :key="s.label" style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px">
            <span style="width: 90px; font-size: 10px; color: #555; text-align: right">{{ s.label }}</span>
            <div style="flex: 1; background: #f0f0f0; border-radius: 4px; height: 16px; overflow: hidden">
              <div :style="{ width: (s.count / maxBookings * 100) + '%', background: '#2e7d32', height: '100%', borderRadius: '4px', transition: 'width .4s' }"></div>
            </div>
            <span style="width: 28px; font-size: 11px; font-weight: 700; color: #333">{{ s.count }}</span>
          </div>
        </div>
      </div>

      <!-- DUES BUCKETS -->
      <div class="card">
        <div class="card-header"><h3>⏰ Dues Aging</h3></div>
        <div class="card-body" style="padding: 10px 14px">
          <div v-for="s in dueBuckets" :key="s.label" style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px">
            <span style="width: 60px; font-size: 10px; color: #555; text-align: right">{{ s.label }}</span>
            <div style="flex: 1; background: #f0f0f0; border-radius: 4px; height: 16px; overflow: hidden">
              <div :style="{ width: (s.count / maxDue * 100) + '%', background: s.color, height: '100%', borderRadius: '4px', transition: 'width .4s' }"></div>
            </div>
            <span style="width: 28px; font-size: 11px; font-weight: 700; color: #333">{{ s.count }}</span>
          </div>
        </div>
      </div>

      <!-- CASH FLOW -->
      <div class="card">
        <div class="card-header"><h3>💰 Cash Flow ({{ transactions.length }} txns)</h3></div>
        <div class="card-body" style="padding: 10px 14px">
          <div style="display: flex; gap: 10px; margin-bottom: 10px">
            <div style="flex: 1; text-align: center; background: #e8f5e9; border-radius: 8px; padding: 10px">
              <div style="font-size: 9px; color: #2e7d32">INFLOW</div>
              <div style="font-size: 14px; font-weight: 700; color: #2e7d32">{{ bdt(cashFlow.inflow) }}</div>
            </div>
            <div style="flex: 1; text-align: center; background: #ffebee; border-radius: 8px; padding: 10px">
              <div style="font-size: 9px; color: #c62828">OUTFLOW</div>
              <div style="font-size: 14px; font-weight: 700; color: #c62828">{{ bdt(cashFlow.outflow) }}</div>
            </div>
          </div>
          <div style="display: flex; background: #f0f0f0; border-radius: 6px; height: 20px; overflow: hidden">
            <div :style="{ width: cashFlow.pct + '%', background: '#2e7d32', height: '100%' }"></div>
            <div :style="{ width: (100 - cashFlow.pct) + '%', background: '#c62828', height: '100%' }"></div>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 9px; color: #888; margin-top: 4px">
            <span>▲ {{ cashFlow.pct }}% inflow</span>
            <span>{{ 100 - cashFlow.pct }}% outflow ▼</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
