<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px">
      <h2 style="font-size: 15px; font-weight: 700; margin: 0">📅 Follow-up Center</h2>
      <span style="font-size: 10px; color: #888; background: #f0f2f5; padding: 2px 8px; border-radius: 10px">{{ todayStr }}</span>
    </div>
    <div style="display: flex; gap: 6px; margin: 8px 0 12px; flex-wrap: wrap">
      <span style="font-size: 10px; color: #d64545; background: #fdeeee; padding: 2px 8px; border-radius: 10px">🔴 {{ overdueLeads.length }} overdue</span>
      <span style="font-size: 10px; color: #e67e00; background: #fff7e6; padding: 2px 8px; border-radius: 10px">🟡 {{ todayLeads.length }} today</span>
      <span style="font-size: 10px; color: #27ae60; background: #eafaf1; padding: 2px 8px; border-radius: 10px">🟢 {{ upcomingPromises.length }} promises</span>
    </div>

    <div class="card" style="background: #fff; border: 1px solid #eef0f3; border-radius: 10px; padding: 12px; margin-bottom: 12px">
      <div style="font-size: 12px; font-weight: 700; color: #333; margin-bottom: 8px">🔴 Overdue follow-ups ({{ overdueLeads.length }})</div>
      <div v-if="!overdueLeads.length" style="color: #999; font-size: 11px; padding: 8px 0">All caught up — no overdue follow-ups. 👏</div>
      <div v-for="l in overdueLeads" :key="'o' + l.id" @click="goLead(l)" style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #fdeeee; color: #d64545; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0">{{ initials(l.name) }}</div>
        <div style="flex: 1; min-width: 0">
          <div style="font-size: 12px; font-weight: 600; color: #222">{{ l.name }} <span style="font-size: 10px; color: #888">· {{ l.phone }}</span></div>
          <div style="font-size: 10px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ l.source }} · due {{ l.nextFollowUp }}</div>
        </div>
        <span style="font-size: 10px; font-weight: 700; color: #d64545; background: #fdeeee; padding: 2px 8px; border-radius: 10px; white-space: nowrap">{{ overdueDays(l.nextFollowUpRaw) }}d late</span>
        <span style="font-size: 10px; padding: 2px 8px; border-radius: 10px; background: #f0f2f5; color: #555; white-space: nowrap">{{ l.status }}</span>
      </div>
    </div>

    <div class="card" style="background: #fff; border: 1px solid #eef0f3; border-radius: 10px; padding: 12px; margin-bottom: 12px">
      <div style="font-size: 12px; font-weight: 700; color: #333; margin-bottom: 8px">🟡 Today ({{ todayLeads.length }})</div>
      <div v-if="!todayLeads.length" style="color: #999; font-size: 11px; padding: 8px 0">No follow-ups scheduled for today.</div>
      <div v-for="l in todayLeads" :key="'t' + l.id" @click="goLead(l)" style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #fff7e6; color: #e67e00; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0">{{ initials(l.name) }}</div>
        <div style="flex: 1; min-width: 0">
          <div style="font-size: 12px; font-weight: 600; color: #222">{{ l.name }} <span style="font-size: 10px; color: #888">· {{ l.phone }}</span></div>
          <div style="font-size: 10px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ l.source }} · last contact {{ l.lastContact || '—' }}</div>
        </div>
        <span style="font-size: 10px; padding: 2px 8px; border-radius: 10px; background: #f0f2f5; color: #555; white-space: nowrap">{{ l.status }}</span>
      </div>
    </div>

    <div class="card" style="background: #fff; border: 1px solid #eef0f3; border-radius: 10px; padding: 12px">
      <div style="font-size: 12px; font-weight: 700; color: #333; margin-bottom: 8px">🟢 Upcoming payment promises ({{ upcomingPromises.length }})</div>
      <div v-if="!upcomingPromises.length" style="color: #999; font-size: 11px; padding: 8px 0">No open payment promises.</div>
      <div v-for="(p, i) in upcomingPromises" :key="'p' + i" @click="goDue(p.due)" style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; cursor: pointer">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: #eafaf1; color: #27ae60; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0">💵</div>
        <div style="flex: 1; min-width: 0">
          <div style="font-size: 12px; font-weight: 600; color: #222">{{ p.customer }} <span style="font-size: 10px; color: #888">· {{ p.project }}</span></div>
          <div style="font-size: 10px; color: #888">Promise {{ bdt(p.amount) }} on {{ p.date }}</div>
        </div>
        <span style="font-size: 10px; font-weight: 700; color: #27ae60; background: #eafaf1; padding: 2px 8px; border-radius: 10px; white-space: nowrap">{{ p.kept ? 'Kept ✓' : 'Open' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'

const data = useDataStore()
const router = useRouter()

const todayStr = new Date().toISOString().slice(0, 10)
const bdt = (n: number) => '৳' + (Number(n) || 0).toLocaleString('en-IN')

const openStatus = (s: string) => !['Converted', 'Lost'].includes(s)

const sortedLeads = computed(() =>
  [...data.leads].sort((a, b) => String(a.nextFollowUpRaw || '9999').localeCompare(String(b.nextFollowUpRaw || '9999')))
)

const overdueLeads = computed(() =>
  sortedLeads.value.filter((l) => l.nextFollowUp && l.nextFollowUp < todayStr && openStatus(l.status))
)
const todayLeads = computed(() =>
  sortedLeads.value.filter((l) => l.nextFollowUpRaw && l.nextFollowUpRaw === todayStr && openStatus(l.status))
)
const upcomingPromises = computed(() => {
  const out: { customer: string; project: string; amount: number; date: string; kept?: boolean; due: string }[] = []
  for (const d of data.dues) {
    for (const p of d.promises || []) {
      if (!p.kept && p.date >= todayStr) out.push({ customer: d.customer, project: d.project, amount: p.amount, date: p.date, kept: p.kept, due: d.id })
    }
  }
  return out.sort((a, b) => a.date.localeCompare(b.date))
})

const initials = (n: string) => (n || '?').split(' ').map((p) => p[0]).join('').slice(0, 2).toUpperCase()
const overdueDays = (d: string) => Math.max(0, Math.round((Date.now() - new Date(d).getTime()) / 86400000))
const goLead = (l: { id: string }) => router.push({ path: '/leads', query: { lead: l.id } })
const goDue = (id: string) => router.push({ path: '/dues', query: { due: id } })
</script>
