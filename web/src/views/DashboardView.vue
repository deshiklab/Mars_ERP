<script setup lang="ts">
import { onMounted } from 'vue'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'

const data = useDataStore()
const auth = useAuthStore()

onMounted(() => {
  data.loadDashboard()
})

const cards = [
  { label: 'Active Bookings', key: 'bookings' as const, icon: '📋', value: (v: number) => String(v), trend: '' },
  { label: 'Hot Leads', key: 'leads' as const, icon: '🎯', value: (v: number) => String(v), trend: '+3 this week' },
  { label: 'Employees', key: 'employees' as const, icon: '👥', value: (v: number) => String(v), trend: '' },
  { label: 'Dues', key: 'dues' as const, icon: '💰', value: (v: number) => String(v), trend: '' }
]
</script>

<template>
  <div class="fade-in">
    <div style="margin-bottom: 10px">
      <span class="page-title">Dashboard</span>
      <span class="page-subtitle">
        REM ERP v{{ data.stats?.pwaVersion ?? '—' }} · Role: {{ auth.pwaRole }} ·
        {{ data.stats ? new Date(data.stats.serverTime).toLocaleString() : 'loading…' }}
      </span>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 8px 0">{{ data.error }}</p>

    <!-- Stats row: mirrors the HTML PWA grid -->
    <div class="stats-row" style="margin-bottom: 12px">
      <div v-for="c in cards" :key="c.key" class="stat-card" :title="c.label">
        <div class="label">{{ c.icon }} {{ c.label }}</div>
        <div class="value">{{ data.stats ? c.value(data.stats[c.key]) : '—' }}</div>
        <div v-if="c.trend" class="trend">{{ c.trend }}</div>
      </div>
    </div>

    <!-- Signed-in card -->
    <div class="card">
      <div class="card-header">
        <h3>👤 Session</h3>
      </div>
      <div class="card-body" style="font-size: 11px; color: #555; line-height: 1.8">
        <div><b style="color: #333">{{ auth.fullName || auth.user }}</b> · {{ auth.pwaRole }}</div>
        <div style="color: #888; font-size: 10px">
          Server roles: {{ auth.roles.join(', ') || '—' }} · Session expires in 8h
        </div>
      </div>
    </div>
  </div>
</template>
