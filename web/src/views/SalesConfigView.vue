<script setup lang="ts">
/**
 * SalesConfigView — mirrors the HTML renderSalesConfig:
 * stats (Territories/Sales Targets/Pipeline Stages/Jul target),
 * territories list, sales targets with progress bars, pipeline
 * stages chips, and plot pricing rates table.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import StatsRow from '@/components/StatsRow.vue'

const territories = ref<any[]>([])
const targets = ref<any[]>([])
const stages = ref<any[]>([])
const rates = ref<Record<string, any>>({})
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const sc = (r.data.collections.sales_config as any) ?? {}
    territories.value = sc.territories ?? []
    targets.value = sc.targets ?? []
    stages.value = sc.stages ?? []
    const pp = (r.data.collections.plot_pricing as any) ?? {}
    rates.value = pp.rates ?? {}
  }
  loading.value = false
})

const julTarget = computed(() => targets.value.filter((t) => t.month === '2026-07').reduce((s, t) => s + (t.target ?? 0), 0))

const stats = computed(() => [
  { label: 'Territories', value: String(territories.value.length), color: '#1565c0' },
  { label: 'Sales Targets', value: String(targets.value.length), color: '#2e7d32' },
  { label: 'Pipeline Stages', value: String(stages.value.length), color: '#7b1fa2' },
  { label: 'Jul 2026 Target', value: bdt(julTarget.value), color: '#e65100' }
])

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(1)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

const maxTarget = computed(() => Math.max(...targets.value.map((t) => t.target ?? 0), 1))
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">Sales Config</span>
      <span class="page-subtitle">Territories · Targets · Pipeline stages · Plot pricing</span>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading config…</p>

    <template v-else>
      <StatsRow :stats="stats" />

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px">
        <!-- territories -->
        <div class="card">
          <div class="card-header"><h3>🌍 Territories</h3></div>
          <div class="card-body">
            <div v-for="t in territories" :key="t.id" style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f5f5">
              <span style="font-size: 11px; font-weight: 500; color: #333">{{ t.name }}</span>
              <span class="pill" style="background: #f0f4ff; color: #2f80ed">{{ t.region || '—' }}</span>
            </div>
            <div v-if="!territories.length" style="text-align: center; padding: 16px; color: #999; font-size: 11px">No territories.</div>
          </div>
        </div>

        <!-- pipeline stages -->
        <div class="card">
          <div class="card-header"><h3>🔷 Pipeline Stages</h3></div>
          <div class="card-body">
            <div style="display: flex; flex-wrap: wrap; gap: 4px">
              <span
                v-for="s in stages"
                :key="s.name"
                class="pill"
                :style="{ background: (s.color || '#2f80ed') + '22', color: s.color || '#2f80ed' }"
              >{{ s.name }}</span>
            </div>
            <div v-if="!stages.length" style="text-align: center; padding: 16px; color: #999; font-size: 11px">No stages.</div>
          </div>
        </div>
      </div>

      <!-- sales targets -->
      <div class="card" style="margin-bottom: 8px">
        <div class="card-header"><h3>🎯 Sales Targets</h3></div>
        <div class="card-body">
          <div v-for="t in targets" :key="t.id" style="padding: 6px 0; border-bottom: 1px solid #f5f5f5">
            <div style="display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 3px">
              <span style="font-weight: 600; color: #333">{{ t.salesperson }}</span>
              <span style="color: #888">{{ t.month }}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px">
              <div style="flex: 1; height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden">
                <div :style="{ width: Math.min(100, ((t.target ?? 0) / maxTarget) * 100) + '%', background: '#2f80ed', height: '100%' }"></div>
              </div>
              <span style="font-size: 10px; font-weight: 700; color: #2f80ed; white-space: nowrap">{{ bdt(t.target) }}</span>
            </div>
          </div>
          <div v-if="!targets.length" style="text-align: center; padding: 16px; color: #999; font-size: 11px">No targets.</div>
        </div>
      </div>

      <!-- plot pricing rates -->
      <div class="card">
        <div class="card-header"><h3>💰 Plot Pricing Rates (per katha)</h3></div>
        <div class="card-body" style="padding: 0">
          <div class="table-wrap">
            <table class="rem-table" style="font-size: 10px; width: 100%">
              <thead><tr><th>Grade</th><th class="num">Katha Rate</th><th class="num">Corner %</th><th class="num">Road %</th></tr></thead>
              <tbody>
                <tr v-for="(r, grade) in rates" :key="grade">
                  <td><span class="pill" style="background: #f0f4ff; color: #2f80ed">{{ grade }}</span></td>
                  <td class="num" style="font-weight: 700; color: #2e7d32">{{ bdt(r.katha) }}</td>
                  <td class="num">+{{ r.cornerPct }}%</td>
                  <td class="num">+{{ r.roadPct }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
