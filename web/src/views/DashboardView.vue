<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import { _t } from '@/i18n'
import BookingDetailDrawer from '@/components/BookingDetailDrawer.vue'
import LeadDetailDrawer from '@/components/LeadDetailDrawer.vue'
import DueDetailDrawer from '@/components/DueDetailDrawer.vue'
import type { Booking, Lead, Due } from '@/api/types'

const data = useDataStore()
const auth = useAuthStore()
const router = useRouter()
const detailBooking = ref<Booking | null>(null)
const detailLead = ref<Lead | null>(null)
const detailDue = ref<Due | null>(null)

onMounted(() => {
  data.loadDashboard()
  data.loadBookings()
  data.loadLeads()
  data.loadDues()
  data.loadPayments()
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

const thisWeek = computed(() => {
  const now = Date.now()
  const week = 7 * 86400000
  const leadsNew = data.leads.filter((l) => {
    const t = new Date(String((l as { dateContacted?: unknown }).dateContacted ?? '')).getTime()
    return !isNaN(t) && now - t <= week
  }).length
  const payNew = data.payments.filter((p) => {
    const t = new Date(String(p.date ?? '')).getTime()
    return !isNaN(t) && now - t <= week
  }).length
  const payAmt = data.payments.filter((p) => {
    const t = new Date(String(p.date ?? '')).getTime()
    return !isNaN(t) && now - t <= week
  }).reduce((s, p) => s + (Number(p.amount) || 0), 0)
  const bkNew = data.bookings.filter((b) => {
    const t = new Date(String((b as { date?: unknown }).date ?? '')).getTime()
    return !isNaN(t) && now - t <= week
  }).length
  return { leadsNew, payNew, payAmt, bkNew }
})

const revenueTrend = computed(() => {
  const map: Record<string, number> = {}
  data.payments.forEach((p) => {
    const d = String(p.date ?? '')
    if (!d) return
    const m = d.slice(0, 7)
    map[m] = (map[m] || 0) + (Number(p.amount) || 0)
  })
  const months = Object.keys(map).sort()
  const rows = months.slice(-6).map((m) => ({ month: m, amt: map[m] }))
  const max = Math.max(...rows.map((r) => r.amt), 1)
  const names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const lab = (m: string) => { const [y, mo] = m.split('-'); return `${names[Number(mo) - 1] ?? mo} '${y.slice(2)}` }
  return { rows, max, lab, total: rows.reduce((s, r) => s + r.amt, 0) }
})

const duePipeline = computed(() => {
  const t = data.dues.length
  const crit = data.dues.filter((d) => d.status === 'Critical').length
  const over = data.dues.filter((d) => d.status === 'Overdue').length
  const curr = data.dues.filter((d) => d.status === 'Current').length
  const pct = (n: number) => (t ? Math.round((n / t) * 100) : 0)
  return { t, crit, over, curr, pct }
})

const pendingApprovals = computed(() => (data.approvals as any[]).filter((a: any) => a.status === 'Pending').length)
const openTickets = computed(() => (data.tickets as any[]).filter((t: any) => t.status === 'Open' || t.status === 'Replied').length)
const pendingLeaves = computed(() => (data.leave as any[]).filter((l: any) => l.status === 'Pending').length)
const quick = computed(() =>
  [
    { title: _t('CRM & Leads'), count: String((data.leads as any[]).length), module: 'crm', path: '/leads', bg: '#fff3e0', fg: '#e65100', icon: '🎯' },
    { title: _t('Bookings'), count: String((data.bookings as any[]).length), module: 'bookings', path: '/bookings', bg: '#e3f2fd', fg: '#1565c0', icon: '📋' },
    { title: _t('Dues & Recovery'), count: String((data.dues as any[]).length), module: 'dues', path: '/dues', bg: '#fce4ec', fg: '#c62828', icon: '💰' },
    { title: _t('Projects'), count: String((data.projects as any[]).length), module: 'projects', path: '/projects', bg: '#e0f2f1', fg: '#00695c', icon: '🏗️' },
    { title: _t('Approvals'), count: String(pendingApprovals.value), module: 'approvals', path: '/approvals', bg: '#e8f5e9', fg: '#2e7d32', icon: '⚡' },
    { title: _t('Tickets'), count: String(openTickets.value), module: 'support', path: '/tickets', bg: '#fff8e1', fg: '#f57f17', icon: '🎫' },
    { title: _t('Leave requests'), count: String(pendingLeaves.value), module: 'hr', path: '/leave', bg: '#f3e5f5', fg: '#7b1fa2', icon: '🌴' },
    { title: _t('HR & Employees'), count: String((data.employees as any[]).length), module: 'hr', path: '/hr', bg: '#ede7f6', fg: '#4527a0', icon: '👥' }
  ].filter((q) => auth.canAccess(q.module))
)

function gotoQuick(q: { path: string }) {
  router.push(q.path)
}

/* ── widgets ── */
/** My Tasks — top 5 non-done (derived from leads needing follow-up for now). */
const myTasks = computed(() =>
  [...data.tasks]
    .filter((t) => t.status !== 'Done' && t.status !== 'Completed')
    .sort((a, b) => (a.priority === 'High' ? 0 : 1) - (b.priority === 'High' ? 0 : 1))
    .slice(0, 5)
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

    <!-- THIS-WEEK CHIPS -->
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px">
      <div style="flex: 1; min-width: 120px; background: #f7faff; border: 1px solid #e3edff; border-radius: 8px; padding: 8px 10px; display: flex; align-items: center; gap: 8px">
        <span style="font-size: 15px">🎯</span>
        <div><div style="font-size: 14px; font-weight: 700; color: #1565c0">{{ thisWeek.leadsNew }}</div><div style="font-size: 8px; color: #888">{{ _t('New leads this week') }}</div></div>
      </div>
      <div style="flex: 1; min-width: 120px; background: #f7faff; border: 1px solid #e3edff; border-radius: 8px; padding: 8px 10px; display: flex; align-items: center; gap: 8px">
        <span style="font-size: 15px">💵</span>
        <div><div style="font-size: 14px; font-weight: 700; color: #2e7d32">{{ bdt(thisWeek.payAmt) }}</div><div style="font-size: 8px; color: #888">{{ thisWeek.payNew }} {{ _t('payments this week') }}</div></div>
      </div>
      <div style="flex: 1; min-width: 120px; background: #f7faff; border: 1px solid #e3edff; border-radius: 8px; padding: 8px 10px; display: flex; align-items: center; gap: 8px">
        <span style="font-size: 15px">📄</span>
        <div><div style="font-size: 14px; font-weight: 700; color: #2f80ed">{{ thisWeek.bkNew }}</div><div style="font-size: 8px; color: #888">{{ _t('new bookings this week') }}</div></div>
      </div>
    </div>

    <!-- TREND + PIPELINE WIDGETS -->
    <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 10px; margin-bottom: 10px">
      <div class="card">
        <div class="card-header"><h3>📈 {{ _t('Revenue Trend') }} <span style="font-size: 9px; font-weight: 400; color: #888">{{ _t('Collections') }}: {{ bdt(revenueTrend.total) }}</span></h3></div>
        <div class="card-body" style="padding: 12px 10px 6px">
          <div v-if="revenueTrend.rows.length" style="display: flex; align-items: flex-end; gap: 8px; height: 90px; padding: 0 4px">
            <div v-for="r in revenueTrend.rows" :key="r.month" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%">
              <div :style="{ width: '60%', height: Math.max((r.amt / revenueTrend.max) * 62, 3) + 'px', background: 'linear-gradient(180deg, #4d94f0, #2f80ed)', borderRadius: '3px 3px 0 0', minWidth: '10px' }" :title="bdt(r.amt)"></div>
              <div style="font-size: 8px; color: #666; margin-top: 3px">{{ revenueTrend.lab(r.month) }}</div>
            </div>
          </div>
          <div v-else style="text-align: center; color: #999; padding: 20px; font-size: 10px">{{ _t('No payments yet') }}</div>
        </div>
      </div>
      <div class="card">
        <div class="card-header"><h3>⏰ {{ _t('Due Pipeline') }}</h3></div>
        <div class="card-body" style="padding: 10px">
          <div style="display: flex; gap: 8px; margin-bottom: 8px">
            <div style="flex: 1; text-align: center; padding: 6px; border-radius: 6px; background: #ffebee"><div style="font-size: 16px; font-weight: 700; color: #c62828">{{ duePipeline.crit }}</div><div style="font-size: 8px; color: #c62828">{{ _t('Critical') }}</div></div>
            <div style="flex: 1; text-align: center; padding: 6px; border-radius: 6px; background: #fff3e0"><div style="font-size: 16px; font-weight: 700; color: #e65100">{{ duePipeline.over }}</div><div style="font-size: 8px; color: #e65100">{{ _t('Overdue') }}</div></div>
            <div style="flex: 1; text-align: center; padding: 6px; border-radius: 6px; background: #e8f5e9"><div style="font-size: 16px; font-weight: 700; color: #2e7d32">{{ duePipeline.curr }}</div><div style="font-size: 8px; color: #2e7d32">{{ _t('Current') }}</div></div>
          </div>
          <div style="display: flex; height: 10px; border-radius: 5px; overflow: hidden; background: #eee">
            <div :style="{ width: duePipeline.pct(duePipeline.crit) + '%', background: '#c62828' }" :title="'Critical ' + duePipeline.crit"></div>
            <div :style="{ width: duePipeline.pct(duePipeline.over) + '%', background: '#ff8f00' }" :title="'Overdue ' + duePipeline.over"></div>
            <div :style="{ width: duePipeline.pct(duePipeline.curr) + '%', background: '#2e7d32' }" :title="'Current ' + duePipeline.curr"></div>
          </div>
          <div style="font-size: 8px; color: #888; margin-top: 5px; text-align: center">{{ duePipeline.t }} {{ _t('accounts tracked') }}</div>
        </div>
      </div>
    </div>

    <!-- MY TASKS -->
    <div class="card" style="margin-bottom: 10px">
      <div class="card-header">
        <h3>📋 {{ _t('My Tasks') }} <span style="font-size: 9px; font-weight: 400; color: #888; margin-left: 6px">{{ myTasks.length }} pending</span></h3>
        <span style="font-size: 10px; color: #2f80ed; cursor: pointer" @click="router.push('/tasks')">{{ _t('View All') }} →</span>
      </div>
      <div class="card-body" style="padding: 6px 10px">
        <div v-if="myTasks.length === 0" style="padding: 10px; text-align: center; color: #999; font-size: 11px">All tasks completed! 🎉</div>
        <div
          v-for="t in myTasks"
          :key="t.title"
          style="display: flex; align-items: center; gap: 6px; padding: 4px 0; border-bottom: 1px solid #f5f5f5; font-size: 11px; cursor: pointer"
          @click="router.push('/tasks')"
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
                <tr v-for="b in recentBookings" :key="b.id" style="cursor: pointer" @click="detailBooking = b">
                  <td style="font-weight: 500; color: #2f80ed">{{ b.id }}</td>
                  <td style="color: #2f80ed">{{ b.client }}</td>
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
                <tr v-for="l in hotLeads" :key="l.id" style="cursor: pointer" @click="detailLead = l">
                  <td style="font-weight: 500; color: #2f80ed">{{ l.name }}</td>
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
          style="display: flex; align-items: center; gap: 8px; padding: 5px 0; border-bottom: 1px solid #f5f5f5; font-size: 11px; cursor: pointer"
          @click="detailDue = d"
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
    <BookingDetailDrawer :booking="detailBooking" @close="detailBooking = null" />
    <LeadDetailDrawer :lead="detailLead" @close="detailLead = null" />
    <DueDetailDrawer :due="detailDue" @close="detailDue = null" />
</template>
