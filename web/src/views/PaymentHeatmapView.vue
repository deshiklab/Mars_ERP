<script setup lang="ts">
/**
 * PaymentHeatmapView — mirrors the HTML renderPaymentHeatmap:
 * a ~12-week calendar grid aligned to Mondays, each day colored by
 * payment intensity (count of payments), with overdue markers and
 * a legend + totals.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'

interface DayCell { key: string; label: string; count: number; amt: number; overdue: boolean; inWindow: boolean }

const payments = ref<any[]>([])
const invoices = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    payments.value = (r.data.collections.payments as any[]) ?? []
    invoices.value = (r.data.collections.invoices as any[]) ?? []
  }
  loading.value = false
})

function pad(n: number) { return n < 10 ? '0' + n : '' + n }
function dayKey(d: Date) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) }

const cells = computed<DayCell[]>(() => {
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const end = new Date(today)
  const start = new Date(today)
  start.setDate(start.getDate() - 83)
  const dow = (start.getDay() + 6) % 7
  start.setDate(start.getDate() - dow)

  const counts: Record<string, { count: number; amt: number }> = {}
  payments.value.forEach((p) => {
    if (!p?.date) return
    const d = new Date(p.date)
    if (isNaN(d.getTime())) return
    if (d < start || d > end) return
    const k = dayKey(d)
    counts[k] = counts[k] || { count: 0, amt: 0 }
    counts[k].count++
    if (p.status === 'Cleared' || p.status === 'Paid') counts[k].amt += Number(p.amount) || 0
  })

  const overdueDays: Record<string, boolean> = {}
  invoices.value.forEach((inv) => {
    if (inv?.dueDate && inv.status === 'Overdue') {
      const d = new Date(inv.dueDate)
      if (!isNaN(d.getTime())) overdueDays[dayKey(d)] = true
    }
  })

  const out: DayCell[] = []
  const cursor = new Date(start)
  while (cursor <= end) {
    const k = dayKey(cursor)
    const c = counts[k]
    out.push({
      key: k,
      label: String(cursor.getDate()),
      count: c?.count ?? 0,
      amt: c?.amt ?? 0,
      overdue: !!overdueDays[k],
      inWindow: cursor >= new Date(start) && cursor <= today
    })
    cursor.setDate(cursor.getDate() + 1)
  }
  return out
})

const totals = computed(() => {
  let count = 0, amt = 0, overdue = 0
  cells.value.forEach((c) => {
    count += c.count
    amt += c.amt
    if (c.overdue) overdue++
  })
  return { count, amt, overdue }
})

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function intensity(count: number): string {
  if (count === 0) return '#f5f5f5'
  if (count === 1) return '#c8e6c9'
  if (count === 2) return '#81c784'
  if (count === 3) return '#4caf50'
  return '#1b5e20'
}

const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">🗓 Payment Heatmap</span>
      <span class="page-subtitle">{{ totals.count }} payments · {{ bdt(totals.amt) }} collected · {{ totals.overdue }} overdue days</span>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading payments…</p>

    <div v-else class="card" style="padding: 12px">
      <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px">
        <div
          v-for="d in dayNames"
          :key="d"
          style="text-align: center; font-size: 8px; color: #999; font-weight: 600; padding: 2px"
        >{{ d }}</div>
        <div
          v-for="c in cells"
          :key="c.key"
          :title="c.key + (c.count ? ' · ' + c.count + ' payment(s) · ' + bdt(c.amt) : '') + (c.overdue ? ' · OVERDUE' : '')"
          style="
            height: 30px;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            color: #555;
            position: relative;
          "
          :style="{ background: intensity(c.count), border: c.overdue ? '2px solid #c62828' : '1px solid #e8e8e8' }"
        >
          <span :style="{ color: c.count > 1 ? '#fff' : '#555', fontWeight: 600 }">{{ c.label }}</span>
          <span v-if="c.count" :style="{ color: c.count > 1 ? '#fff' : '#2e7d32', fontSize: '7px' }">{{ c.count }}</span>
          <span v-if="c.overdue" style="position: absolute; top: 1px; right: 2px; font-size: 8px">⚠️</span>
        </div>
      </div>

      <!-- legend -->
      <div style="display: flex; align-items: center; gap: 12px; margin-top: 10px; font-size: 9px; color: #888; flex-wrap: wrap">
        <span style="display: flex; align-items: center; gap: 4px"><span style="width: 12px; height: 12px; background: #f5f5f5; border-radius: 3px; border: 1px solid #e8e8e8"></span> None</span>
        <span style="display: flex; align-items: center; gap: 4px"><span style="width: 12px; height: 12px; background: #c8e6c9; border-radius: 3px"></span> 1</span>
        <span style="display: flex; align-items: center; gap: 4px"><span style="width: 12px; height: 12px; background: #81c784; border-radius: 3px"></span> 2</span>
        <span style="display: flex; align-items: center; gap: 4px"><span style="width: 12px; height: 12px; background: #4caf50; border-radius: 3px"></span> 3</span>
        <span style="display: flex; align-items: center; gap: 4px"><span style="width: 12px; height: 12px; background: #1b5e20; border-radius: 3px"></span> 4+</span>
        <span style="display: flex; align-items: center; gap: 4px"><span style="width: 12px; height: 12px; border: 2px solid #c62828; border-radius: 3px"></span> Overdue invoice</span>
      </div>
    </div>
  </div>
</template>
