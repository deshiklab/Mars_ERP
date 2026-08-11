<template>
  <div class="fade-in" v-if="me">
    <!-- header -->
    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px">
      <div style="width: 46px; height: 46px; border-radius: 8px; background: linear-gradient(135deg, #2f80ed, #56ccf2); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; flex-shrink: 0">🏗</div>
      <div style="flex: 1; min-width: 0">
        <h2 style="margin: 0; font-size: 18px">{{ me }}</h2>
        <div style="color: #7f8fa6; font-size: 11px">Project 360 · {{ type || 'Residential' }} · {{ loc || '—' }} · {{ units.length }} units</div>
      </div>
      <button @click="router.push('/flats')" style="border: 1px solid #d5dbe6; background: #fff; color: #2f80ed; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer">🏢 All Flats</button>
    </div>

    <!-- numbers -->
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px">
      <div v-for="s in stats" :key="s.label" style="background: #fff; border: 1px solid #eef1f6; border-radius: 10px; padding: 10px">
        <div style="font-size: 16px; font-weight: 700">{{ s.value }}</div>
        <div style="color: #7f8fa6; font-size: 10px; margin-top: 2px">{{ s.label }}</div>
      </div>
    </div>

    <!-- units grid -->
    <div style="background: #fff; border: 1px solid #eef1f6; border-radius: 10px; padding: 12px; margin-bottom: 12px">
      <div style="font-weight: 600; font-size: 13px; margin-bottom: 8px">🏠 Units ({{ units.length }})</div>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)); gap: 6px" v-if="units.length">
        <div v-for="u in units" :key="u.id" :title="`${unitLabel(u)} — ${u.status || 'available'}`"
          style="border: 1px solid #eef1f6; border-radius: 8px; padding: 6px 8px; font-size: 11px; cursor: pointer"
          :style="{ background: unitColor(u) }" @click="router.push('/flats')">
          <div style="font-weight: 600">{{ unitLabel(u) }}</div>
          <div style="font-size: 10px; color: #555; text-transform: capitalize">{{ unitType(u) || u.status || 'available' }}</div>
        </div>
      </div>
      <div v-else style="color: #7f8fa6; font-size: 12px">No unit data yet — waiting for the server.</div>
    </div>

    <!-- bookings -->
    <div style="background: #fff; border: 1px solid #eef1f6; border-radius: 10px; padding: 12px; margin-bottom: 12px">
      <div style="font-weight: 600; font-size: 13px; margin-bottom: 8px">📄 Bookings ({{ bookings.length }})</div>
      <div v-if="bookings.length">
        <div v-for="b in bookings" :key="b.id" @click="router.push('/bookings')" style="display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid #f5f7fa; cursor: pointer; font-size: 12px">
          <span><b>{{ b.id }}</b> · {{ b.client }} · {{ b.unit || '—' }}</span>
          <span style="font-weight: 600">{{ bdt(Number(b.price)) }}</span>
        </div>
      </div>
      <div v-else style="color: #7f8fa6; font-size: 12px">No bookings yet.</div>
    </div>

    <!-- collections -->
    <div style="background: #fff; border: 1px solid #eef1f6; border-radius: 10px; padding: 12px">
      <div style="font-weight: 600; font-size: 13px; margin-bottom: 8px">💵 Collections</div>
      <div style="display: flex; gap: 18px; flex-wrap: wrap; font-size: 12px">
        <span>Advance collected: <b style="color: #27ae60">{{ bdt(advanceSum) }}</b></span>
        <span>Invoices issued: <b>{{ invoices.length }}</b> ({{ bdt(invSum) }})</span>
        <span>Paid invoices: <b>{{ paidInv.length }}</b></span>
        <span>Outstanding invoices: <b style="color: #d64545">{{ invSum - paidInvSum }}</b></span>
      </div>
      <div v-if="invoices.length" style="margin-top: 8px">
        <div v-for="iv in invoices" :key="iv.id" @click="router.push('/finance')" style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f7fa; cursor: pointer; font-size: 11px">
          <span>{{ iv.id }} · {{ iv.client }} · {{ iv.unit || '—' }}</span>
          <span><b>{{ bdt(iv.amount) }}</b> <span :style="{ color: iv.status === 'Paid' ? '#27ae60' : '#d64545', fontSize: 10 }">{{ iv.status }}</span></span>
        </div>
      </div>
    </div>
  </div>
  <div v-else style="color: #7f8fa6; padding: 20px; font-size: 13px">
    {{ loading ? 'Loading project…' : 'Project not found.' }}
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import type { Booking, Invoice } from '@/api/types'

const route = useRoute()
const router = useRouter()
const data = useDataStore()

const me = computed(() => String(route.params.name ?? '').toLowerCase().replace(/-/g, ' '))
const loading = ref(false)

const units = computed(() => {
  const m = me.value.trim().toLowerCase()
  if (!m) return []
  // flats (project-tagged units) take priority; otherwise the project's
  // land plots match by their id prefix (M- → Muktodhara, J- → Jolshiri)
  const tagged = data.flats.filter((f) => String(f.project ?? '').trim().toLowerCase() === m || String(f.project ?? '').includes(m))
  if (tagged.length) return tagged
  const ini = (m[0] || '').toUpperCase()
  return data.plots.filter((p) => String(p.id ?? '').toUpperCase().startsWith(ini))
})
const type = computed(() => (units.value[0] as { type?: string } | undefined)?.type ?? '')
const loc = computed(() => units.value[0]?.location ?? '')

const bookings = computed(() => {
  const m = me.value.trim().toLowerCase()
  if (!m) return []
  return data.bookings.filter((b) => String(b.property ?? '').trim().toLowerCase() === m)
})
const invoices = computed(() => {
  const m = me.value.trim().toLowerCase()
  if (!m) return []
  return data.invoices.filter((iv) => String(iv.project ?? '').trim().toLowerCase() === m)
})
const paidInv = computed(() => invoices.value.filter((iv) => iv.status === 'Paid'))
const paidInvSum = computed(() => paidInv.value.reduce((a, iv) => a + (Number(iv.amount) || 0), 0))
const invSum = computed(() => invoices.value.reduce((a, iv) => a + (Number(iv.amount) || 0), 0))
const advanceSum = computed(() => bookings.value.reduce((a, b) => a + (Number(b.advance) || 0), 0))

const stats = computed(() => [
  { label: 'Units', value: units.value.length },
  { label: 'Sold', value: units.value.filter((u) => /sold|reserved|booked/i.test(String(u.status ?? ''))).length },
  { label: 'Advance', value: bdt(advanceSum.value) },
  { label: 'Outstanding', value: bdt(invSum.value - paidInvSum.value) },
])

const unitLabel = (u: { id: string; unit?: string; plotNo?: string }) => u.unit || u.plotNo || u.id
const unitType = (u: { type?: string; area?: string }) => u.type || u.area || ''

const unitColor = (u: { status?: string }) => {
  const s = String(u.status ?? '').toLowerCase()
  if (/sold|booked/i.test(s)) return 'background: #e8f5e9; border-color: #c8e6c9;'
  if (/reserved/i.test(s)) return 'background: #fff8e1; border-color: #ffe0b2;'
  return 'background: #fff; border-color: #eef1f6;'
}

const bdt = (n: number) =>
  '৳ ' + (Number(n) || 0).toLocaleString('en-US', { maximumFractionDigits: 2 })

watch(() => route.params.name, () => { loading.value = false }, { immediate: true })
</script>
