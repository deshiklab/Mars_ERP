<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import { _t } from '@/i18n'

const data = useDataStore()
const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  data.loadDashboard()
  data.loadBookings()
  data.loadLeads()
  data.loadDues()
})

const stats = computed(() => {
  const s = data.stats
  return [
    { label: _t('Active Bookings'), value: s ? String(s.bookings) : '—', color: '', trend: '' },
    { label: _t('Hot Leads'), value: s ? String(s.leads) : '—', color: '#e53935', trend: '+3 this week' },
    { label: _t('Employees'), value: s ? String(s.employees) : '—', color: '', trend: '' },
    { label: _t('Dues'), value: s ? String(s.dues) : '—', color: '#c62828', trend: '' }
  ]
})

const quick = computed(() =>
  [
    { title: _t('CRM & Leads'), count: '', module: 'crm', path: '/leads', bg: '#fff3e0', fg: '#e65100', icon: '🎯' },
    { title: _t('Bookings'), count: '', module: 'bookings', path: '/bookings', bg: '#e3f2fd', fg: '#1565c0', icon: '📋' },
    { title: _t('Dues & Recovery'), count: '', module: 'dues', path: '/dues', bg: '#fce4ec', fg: '#c62828', icon: '💰' },
    { title: _t('Projects'), count: '', module: 'projects', path: '/projects', bg: '#e0f2f1', fg: '#00695c', icon: '🏗️' },
    { title: _t('HR & Employees'), count: '', module: 'hr', path: '/hr', bg: '#f3e5f5', fg: '#7b1fa2', icon: '👥' }
  ].filter((q) => auth.canAccess(q.module))
)

function gotoQuick(q: { path: string }) {
  router.push(q.path)
}

/* ── widgets ── */
/** My Tasks — top 5 non-done (derived from leads needing follow-up for now). */
const myTasks = computed(() =>
  data.leads
    .filter((l) => l.status === 'New Inquiry' || l.status === 'Site Visit')
    .slice(0, 5)
    .map((l) => ({
      title: `Follow up: ${l.name}`,
      status: l.status,
      priority: l.priority
    }))
)

const recentBookings = computed(() => data.bookings.slice(0, 5))
const hotLeads = computed(() =>
  [...data.leads]
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
    .slice(0, 5)
)
const duesReminders = computed(() =>
  data.dues
    .filter((d) => d.status !== 'Paid')
    .sort((a, b) => b.daysOverdue - a.daysOverdue)
    .slice(0, 5)
)

function statusColor(s: string): string {
  const map: Record<string, string> = {
    'New Inquiry': '#1565c0',
    Contacted: '#2f80ed',
    'Site Visit': '#e65100',
    Negotiation: '#ff8f00',
    Booking: '#2e7d32',
    Confirmed: '#2e7d32',
    Overdue: '#e65100',
    Critical: '#c62828',
    Paid: '#1565c0'
  }
  return map[s] ?? '#555'
}

function bdt(n: number): string {
  if (n >= 10000000) return `৳ ${(n / 10000000).toFixed(2)} Cr`
  if (n >= 100000) return `৳ ${(n / 100000).toFixed(1)} Lac`
  return `৳ ${n.toLocaleString()}`
}

function printReport() {
  window.print()
}
</script>

<template>
  <div class="fade-in">
    <div class="page-title">{{ _t('Dashboard') }}</div>
    <div class="page-subtitle">
      REM ERP v{{ data.stats?.pwaVersion ?? '—' }} · {{ _t('Role') }}: {{ auth.pwaRole }} ·
      {{ data.stats ? new Date(data.stats.serverTime).toLocaleString() : 'loading…' }}
    </div>

    <div style="margin: 8px 0">
      <button class="action-btn primary" style="padding: 3px 12px; font-size: 10px" @click="printReport">🖨 {{ _t('Print Report') }}</button>
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

    <!-- MY TASKS -->
    <div class="card" style="margin-bottom: 10px">
      <div class="card-header">
        <h3>📋 {{ _t('My Tasks') }} <span style="font-size: 9px; font-weight: 400; color: #888; margin-left: 6px">{{ myTasks.length }} pending</span></h3>
        <span style="font-size: 10px; color: #2f80ed; cursor: pointer" @click="router.push('/leads')">{{ _t('View All') }} →</span>
      </div>
      <div class="card-body" style="padding: 6px 10px">
        <div v-if="myTasks.length === 0" style="padding: 10px; text-align: center; color: #999; font-size: 11px">All tasks completed! 🎉</div>
        <div
          v-for="t in myTasks"
          :key="t.title"
          style="display: flex; align-items: center; gap: 6px; padding: 4px 0; border-bottom: 1px solid #f5f5f5; font-size: 11px"
        >
          <span style="width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0" :style="{ background: t.priority === 'High' ? '#e53935' : t.priority === 'Medium' ? '#ff9800' : '#999' }"></span>
          <span style="flex: 1; color: #333">{{ t.title }}</span>
          <span style="font-size: 9px; color: #888">{{ t.status }}</span>
        </div>
      </div>
    </div>

    <!-- WIDGET GRID: Recent Bookings + Hot Leads + Dues -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px">
      <!-- RECENT BOOKINGS -->
      <div class="card">
        <div class="card-header"><h3>{{ _t('Recent Bookings') }}</h3></div>
        <div class="card-body" style="padding: 0">
          <div class="table-wrap">
            <table class="rem-table">
              <thead>
                <tr><th>ID</th><th>Client</th><th>Property</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="b in recentBookings" :key="b.id" style="cursor: pointer" @click="router.push('/bookings')">
                  <td style="font-weight: 500">{{ b.id }}</td>
                  <td>{{ b.client }}</td>
                  <td>{{ b.property }}</td>
                  <td>
                    <span class="pill" :style="{ background: statusColor(b.status) + '22', color: statusColor(b.status) }">{{ b.status }}</span>
                  </td>
                </tr>
                <tr v-if="recentBookings.length === 0">
                  <td colspan="4" style="text-align: center; color: #999; padding: 14px; font-size: 10px">No bookings yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- HOT LEADS -->
      <div class="card">
        <div class="card-header"><h3>{{ _t('Hot Leads') }}</h3></div>
        <div class="card-body" style="padding: 0">
          <div class="table-wrap">
            <table class="rem-table">
              <thead>
                <tr><th>Name</th><th>Score</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="l in hotLeads" :key="l.id" style="cursor: pointer" @click="router.push('/leads')">
                  <td style="font-weight: 500">{{ l.name }}</td>
                  <td>
                    <span class="pill" style="background: #eef3ff; color: #2f80ed">{{ l.score }}</span>
                  </td>
                  <td>
                    <span class="pill" :style="{ background: statusColor(l.status) + '22', color: statusColor(l.status) }">{{ l.status }}</span>
                  </td>
                </tr>
                <tr v-if="hotLeads.length === 0">
                  <td colspan="3" style="text-align: center; color: #999; padding: 14px; font-size: 10px">No leads yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- DUES REMINDERS -->
    <div class="card" style="margin-bottom: 10px">
      <div class="card-header">
        <h3>⏰ {{ _t('Dues Reminders') }} <span style="font-size: 9px; font-weight: 400; color: #888; margin-left: 6px">{{ duesReminders.length }} unpaid</span></h3>
        <span style="font-size: 10px; color: #2f80ed; cursor: pointer" @click="router.push('/dues')">{{ _t('View All') }} →</span>
      </div>
      <div class="card-body" style="padding: 6px 10px">
        <div
          v-for="d in duesReminders"
          :key="d.id"
          style="display: flex; align-items: center; gap: 8px; padding: 5px 0; border-bottom: 1px solid #f5f5f5; font-size: 11px"
        >
          <span style="font-size: 12px">{{ d.daysOverdue >= 60 ? '🔴' : d.daysOverdue >= 30 ? '🟠' : '🟡' }}</span>
          <span style="flex: 1; color: #333">{{ d.customer }} — {{ d.project }}</span>
          <b style="font-size: 10px; color: #c62828">{{ bdt(d.due) }}</b>
          <span style="font-size: 9px; color: #e65100">{{ d.daysOverdue }}d overdue</span>
        </div>
        <div v-if="duesReminders.length === 0" style="padding: 10px; text-align: center; color: #999; font-size: 11px">All caught up! 🎉</div>
      </div>
    </div>

    <!-- SESSION -->
    <div class="card">
      <div class="card-header"><h3>👤 {{ _t('Session') }}</h3></div>
      <div class="card-body" style="font-size: 11px; color: #555; line-height: 1.8">
        <div><b style="color: #333">{{ auth.fullName || auth.user }}</b> · {{ auth.pwaRole }}</div>
        <div style="color: #888; font-size: 10px">
          {{ _t('Server roles') }}: {{ auth.roles.join(', ') || '—' }} · {{ _t('Session expires in 8h') }}
        </div>
      </div>
    </div>
  </div>
</template>
