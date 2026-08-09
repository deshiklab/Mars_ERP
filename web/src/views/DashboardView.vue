<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'

const data = useDataStore()
const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  data.loadDashboard()
})

/** Stats row — mirrors renderDashboard (available/sold/reserved plots are
    omitted when the plots collection is empty; core cards always shown). */
const stats = computed(() => {
  const s = data.stats
  return [
    { label: 'Active Bookings', value: s ? String(s.bookings) : '—', color: '', trend: '' },
    { label: 'Hot Leads', value: s ? String(s.leads) : '—', color: '#e53935', trend: '+3 this week' },
    { label: 'Employees', value: s ? String(s.employees) : '—', color: '', trend: '' },
    { label: 'Dues', value: s ? String(s.dues) : '—', color: '#c62828', trend: '' }
  ]
})

/** Quick cards — mirrors the HTML dashboard-quick grid. */
const quick = [
  { title: 'CRM & Leads', count: '', module: 'crm', path: '/leads', bg: '#fff3e0', fg: '#e65100', icon: '🎯' },
  { title: 'Bookings', count: '', module: 'bookings', path: '/bookings', bg: '#e3f2fd', fg: '#1565c0', icon: '📋' },
  { title: 'Dues & Recovery', count: '', module: 'dues', path: '/dues', bg: '#fce4ec', fg: '#c62828', icon: '💰' },
  { title: 'Projects', count: '', module: 'projects', path: '/projects', bg: '#e0f2f1', fg: '#00695c', icon: '🏗️' },
  { title: 'HR & Employees', count: '', module: 'hr', path: '/hr', bg: '#f3e5f5', fg: '#7b1fa2', icon: '👥' }
].filter((q) => auth.canAccess(q.module))

function gotoQuick(q: { path: string }) {
  router.push(q.path)
}

function printReport() {
  window.print()
}
</script>

<template>
  <div class="fade-in">
    <div class="page-title">Dashboard</div>
    <div class="page-subtitle">
      REM ERP v{{ data.stats?.pwaVersion ?? '—' }} · Role: {{ auth.pwaRole }} ·
      {{ data.stats ? new Date(data.stats.serverTime).toLocaleString() : 'loading…' }}
    </div>

    <div style="margin: 8px 0">
      <button class="action-btn primary" style="padding: 3px 12px; font-size: 10px" @click="printReport">🖨 Print Report</button>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <!-- STATS ROW -->
    <div class="stats-row" style="margin-bottom: 12px">
      <div v-for="c in stats" :key="c.label" class="stat-card">
        <div class="label">{{ c.label }}</div>
        <div class="value" :style="c.color ? `color:${c.color}` : ''">{{ c.value }}</div>
        <div v-if="c.trend" class="trend">{{ c.trend }}</div>
      </div>
    </div>

    <!-- QUICK CARDS -->
    <div class="dashboard-quick">
      <div v-for="q in quick" :key="q.title" class="quick-card" @click="gotoQuick(q)">
        <div class="icon" :style="{ background: q.bg, color: q.fg }">{{ q.icon }}</div>
        <div class="info">
          <div class="title">{{ q.title }}</div>
          <div class="count">{{ q.count }}</div>
        </div>
      </div>
    </div>

    <!-- SESSION CARD -->
    <div class="card">
      <div class="card-header"><h3>👤 Session</h3></div>
      <div class="card-body" style="font-size: 11px; color: #555; line-height: 1.8">
        <div><b style="color: #333">{{ auth.fullName || auth.user }}</b> · {{ auth.pwaRole }}</div>
        <div style="color: #888; font-size: 10px">
          Server roles: {{ auth.roles.join(', ') || '—' }} · Session expires in 8h
        </div>
      </div>
    </div>
  </div>
</template>
