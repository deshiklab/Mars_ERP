<script setup lang="ts">
/**
 * SalesConfigView — mirrors the HTML renderSalesConfig:
 * stats (Territories/Sales Targets/Pipeline Stages/Jul target),
 * territories list, sales targets with progress bars, pipeline
 * stages chips, and plot pricing rates table.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { showToast } from '@/toast'
import StatsRow from '@/components/StatsRow.vue'

const territories = ref<any[]>([])
const targets = ref<any[]>([])
const stages = ref<any[]>([])
const rates = ref<Record<string, any>>({})
const loading = ref(true)

const settings = ref<Record<string, unknown>>({})
const busy = ref(false)
const saved = ref(false)
async function saveSettings() {
  busy.value = true; saved.value = false
  try {
    const res = await api.call('settings_set', { settings: { ...settings.value } })
    if (res.ok) { saved.value = true; showToast('Settings saved'); setTimeout(() => (saved.value = false), 2500) }
    else showToast('Save failed — ' + (res.error || 'server error'))
  } finally { busy.value = false }
}
onMounted(async () => {
  const r = await api.call('settings_get')
  if (r.ok) settings.value = (r.data as any) ?? {}
})
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
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-bottom: 12px">
      <div>
        <h2 class="page-title" style="margin: 0 0 2px">⚙️ Sales & System Config</h2>
        <span class="page-subtitle">Server-backed connection & workflow settings</span>
      </div>
      <button class="btn primary" :disabled="busy" @click="saveSettings" style="padding: 6px 18px; font-size: 12px">
        {{ busy ? 'Saving…' : '💾 Save settings' }}
      </button>
    </div>
    <div v-if="saved" style="background:#e8f5e9;color:#2e7d32;padding:8px 12px;border-radius:6px;font-size:12px;margin-bottom:10px">✓ Settings saved to the server</div>
    <div class="card" style="max-width: 560px">
      <div class="card-header"><h3>Connection</h3></div>
      <div style="padding: 12px 16px">
        <label style="font-size: 11px; color: #555; display: block; margin-bottom: 4px">API base override (leave empty for auto)</label>
        <input v-model="settings.api_base_override" placeholder="https://erp.mars-constech.com" style="width: 100%; padding: 7px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px" />
      </div>
      <div class="card-header"><h3>Workflow toggles</h3></div>
      <div style="padding: 12px 16px; display: flex; flex-direction: column; gap: 10px">
        <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer">
          <input type="checkbox" v-model="settings.auto_connect" style="width: 15px; height: 15px" /> Auto-connect to the server on load
        </label>
        <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer">
          <input type="checkbox" v-model="settings.push_on_save" style="width: 15px; height: 15px" /> Push changes to the server on save
        </label>
        <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer">
          <input type="checkbox" v-model="settings.auto_heal" style="width: 15px; height: 15px" /> Auto-heal stale API connections
        </label>
        <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer">
          <input type="checkbox" v-model="settings.live_land" style="width: 15px; height: 15px" /> Live land-acquisition updates
        </label>
      </div>
    </div>
  </div>
</template>
