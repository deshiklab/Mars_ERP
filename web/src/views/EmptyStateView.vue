<script setup lang="ts">
/**
 * EmptyStateView — graceful placeholder for modules that have no
 * data collection yet. Reads the module id from the route and shows
 * a branded "coming soon" state.
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { GROUPS } from '@/shell/groups'
import { _t } from '@/i18n'

const route = useRoute()
const router = useRouter()

const modId = computed(() => String(route.params.module ?? 'module'))

const info = computed(() => {
  for (const g of GROUPS) {
    const m = g.mods.find((x) => x.id === modId.value)
    if (m) return { group: g, module: m }
  }
  return { group: GROUPS[0], module: { id: modId.value, label: modId.value } }
})

const label = computed(() => _t(info.value.module.label))
const groupLabel = computed(() => _t(info.value.group.label))

function goDashboard() {
  router.push('/')
}
</script>

<template>
  <div class="fade-in" style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; text-align: center">
    <div
      style="
        width: 84px;
        height: 84px;
        border-radius: 20px;
        background: linear-gradient(135deg, #f0f4ff, #e3edff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 38px;
        margin-bottom: 18px;
      "
    >📭</div>
    <div style="font-size: 17px; font-weight: 700; color: #222">{{ label }}</div>
    <div style="font-size: 11px; color: #888; margin-top: 6px; max-width: 380px">
      This module is part of <b>{{ groupLabel }}</b> but doesn't have live data yet.
      Once records are synced from the ERP, they'll appear here.
    </div>
    <div
      style="
        margin-top: 16px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 10px;
        color: #2f80ed;
        background: #f0f4ff;
        border: 1px solid #d0ddf0;
        border-radius: 12px;
        padding: 4px 12px;
      "
    >🔄 Waiting for server data</div>
    <div style="margin-top: 20px; display: flex; gap: 8px">
      <button class="action-btn" @click="goDashboard">📊 Go to Dashboard</button>
      <button class="action-btn primary" @click="router.back()">← Back</button>
    </div>
  </div>
</template>
