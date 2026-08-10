<script setup lang="ts">
/**
 * BrokerDetailDrawer — broker profile: avatar + tier, region,
 * contact, stats (leads referred, deals closed, commission %),
 * commission paid, joined, status actions.
 */
import { computed, ref, watch } from 'vue'
import type { Broker } from '@/api/types'

const props = defineProps<{ broker: Broker | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()
const tab = ref('overview')
watch(() => props.broker, () => (tab.value = 'overview'))

function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || '?'
}
function tierColor(t: string | undefined): string {
  const map: Record<string, string> = { Platinum: '#7b1fa2', Gold: '#e65100', Silver: '#546e7a', Bronze: '#8d6e63' }
  return map[t ?? ''] ?? '#2f80ed'
}
function statusColor(s: string | undefined): string {
  return s === 'Active' ? '#2e7d32' : s === 'Inactive' ? '#888' : s === 'Suspended' ? '#c62828' : '#555'
}
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

const commissionPaidNum = computed(() => {
  const raw = String(props.broker?.commissionPaid ?? '').replace(/[৳,\s]/g, '')
  const m = raw.match(/^([0-9.]+)(L|Cr)?$/i)
  if (!m) return 0
  return m[2] ? (m[2].toLowerCase() === 'cr' ? parseFloat(m[1]) * 10000000 : parseFloat(m[1]) * 100000) : parseFloat(m[1])
})
</script>

<template>
  <div v-if="broker" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 500px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <div class="drawer-header" style="flex-shrink: 0">
        <h3>🤝 {{ broker.name }}</h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto">
        <!-- identity -->
        <div style="display: flex; gap: 12px; align-items: center; padding: 10px; background: #f8faff; border-radius: 8px; margin-bottom: 10px">
          <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #7b1fa2, #2f80ed); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 700">{{ initials(broker.name) }}</div>
          <div style="flex: 1">
            <div style="font-size: 14px; font-weight: 700; color: #222">{{ broker.name }}</div>
            <div style="font-size: 11px; color: #555">{{ broker.region }} · {{ broker.phone }}</div>
            <div style="margin-top: 3px; display: flex; gap: 4px">
              <span class="pill" :style="{ background: tierColor(broker.tier) + '22', color: tierColor(broker.tier) }">⭐ {{ broker.tier }}</span>
              <span class="pill" :style="{ background: statusColor(broker.status) + '22', color: statusColor(broker.status) }">{{ broker.status }}</span>
            </div>
          </div>
        </div>

        <!-- stats -->
        <div class="stats-row" style="grid-template-columns: 1fr 1fr">
          <div class="stat-card"><div class="label">🎯 Leads Referred</div><div style="font-size: 16px; font-weight: 700; color: #2f80ed; margin-top: 2px">{{ broker.leadsReferred ?? 0 }}</div></div>
          <div class="stat-card"><div class="label">📈 Deals Closed</div><div style="font-size: 16px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ broker.dealsClosed ?? 0 }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">💰 Commission Rate</div><div style="font-size: 14px; font-weight: 700; color: #7b1fa2; margin-top: 2px">{{ broker.commissionPct ?? 0 }}%</div></div>
          <div class="stat-card"><div class="label">💵 Commission Paid</div><div style="font-size: 14px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ bdt(commissionPaidNum) }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">📅 Joined</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ broker.joined || '—' }}</div></div>
          <div class="stat-card"><div class="label">🆔 ID</div><div style="font-size: 12px; font-weight: 600; color: #2f80ed; margin-top: 2px">{{ broker.id }}</div></div>
        </div>

        <!-- conversion estimate -->
        <div style="margin-top: 12px">
          <div style="display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 4px">
            <span style="font-weight: 600; color: #555">Conversion rate</span>
            <span style="font-weight: 700; color: #2e7d32">{{ broker.leadsReferred ? Math.round(((broker.dealsClosed ?? 0) / broker.leadsReferred) * 100) : 0 }}%</span>
          </div>
          <div style="height: 7px; background: #f0f0f0; border-radius: 4px; overflow: hidden">
            <div :style="{ width: broker.leadsReferred ? Math.min(100, ((broker.dealsClosed ?? 0) / broker.leadsReferred) * 100) + '%' : '0%', background: 'linear-gradient(90deg, #7b1fa2, #2f80ed)', height: '100%' }"></div>
          </div>
        </div>

        <!-- actions -->
        <div style="margin-top: 14px; display: flex; gap: 6px; flex-wrap: wrap">
          <button class="action-btn" style="color: #2e7d32" @click="emit('status', 'Active')">✅ Mark Active</button>
          <button class="action-btn" style="color: #888" @click="emit('status', 'Inactive')">⏸ Mark Inactive</button>
          <button class="action-btn" style="color: #c62828" @click="emit('status', 'Suspended')">🚫 Suspend</button>
        </div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
        <button class="drawer-btn" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
