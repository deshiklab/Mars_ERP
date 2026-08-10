<script setup lang="ts">
import { _t } from '@/i18n'
/**
 * StatsRow — mirrors the HTML PWA stats-row/stat-card grid.
 */
export interface StatItem {
  label: string
  value: string
  color?: string
  trend?: string
  onClick?: () => void
}

defineProps<{ stats: StatItem[] }>()
</script>

<template>
  <div class="stats-row" style="margin-bottom: 12px">
    <div
      v-for="s in stats"
      :key="s.label"
      class="stat-card"
      :style="s.onClick ? 'cursor:pointer' : ''"
      @click="s.onClick"
    >
      <div class="label">{{ _t(s.label) }}</div>
      <div class="value" :style="s.color ? `color:${s.color}` : ''">{{ s.value }}</div>
      <div v-if="s.trend" class="trend">{{ s.trend }}</div>
    </div>
  </div>
</template>
