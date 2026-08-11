<template>
  <div class="fade-in" v-if="me">
    <!-- header -->
    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px">
      <div style="width: 46px; height: 46px; border-radius: 50%; background: #2F80ED; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; flex: 0 0 auto">{{ initials(me.name) }}</div>
      <div style="flex: 1; min-width: 200px">
        <div style="font-size: 15px; font-weight: 700">{{ me.name }}</div>
        <div style="font-size: 11px; color: #667085">{{ me.designation || 'Team Member' }} · {{ me.dept || '—' }} · <span :style="{ color: me.status === 'Active' ? '#27ae60' : '#d64545' }">{{ me.status || '—' }}</span></div>
        <div style="font-size: 11px; color: #667085; margin-top: 2px">{{ me.phone }} · {{ me.email }}</div>
      </div>
      <div style="display: flex; gap: 6px; flex-wrap: wrap">
        <a :href="'tel:' + me.phone" style="...">📞 Call</a>
        <a :href="'mailto:' + me.email" style="...">✉ Email</a>
      </div>
    </div>
    <!-- stats -->
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px">
      <div class="stat-card" style="flex: 1; min-width: 120px"><div style="font-size: 17px; font-weight: 700">{{ bdt(me.salary ?? 0) }}</div><div style="font-size: 10px; color: #667085">Salary</div></div>
      <div class="stat-card" style="flex: 1; min-width: 120px"><div style="font-size: 17px; font-weight: 700; color: #2F80ED">{{ attendRate }}%</div><div style="font-size: 10px; color: #667085">Attendance (30d)</div></div>
      <div class="stat-card" style="flex: 1; min-width: 120px"><div style="font-size: 17px; font-weight: 700">{{ pendLeaves }}</div><div style="font-size: 10px; color: #667085">Pending leaves</div></div>
      <div class="stat-card" style="flex: 1; min-width: 120px"><div style="font-size: 17px; font-weight: 700; color: #e67e22">{{ daysLate }}</div><div style="font-size: 10px; color: #667085">Late days (30d)</div></div>
    </div>
    <!-- tabs -->
    <div class="top-nav" style="margin-bottom: 10px; display: flex; gap: 4px; overflow-x: auto">
      <button v-for="t in tabs" :key="t.id" class="top-nav-item" :class="{ active: tab === t.id }" @click="tab = t.id" style="border: none; background: none; cursor: pointer; white-space: nowrap; font-size: 11px; padding: 6px 10px">{{ t.label }} ({{ t.count }})</button>
    </div>
    <div v-if="tab === 'attendance'" class="table-wrap">
      <table class="dt">
        <thead><tr><th>Date</th><th>Status</th><th>Shift</th><th>In / Out</th></tr></thead>
        <tbody>
          <tr v-for="a in myAttendance" :key="a.id">
            <td>{{ a.date }}</td>
            <td><span class="pill" :style="{ background: statusColor(a.status).bg, color: statusColor(a.status).fg }">{{ a.status }}</span></td>
            <td>{{ a.shift || '—' }}</td>
            <td>{{ a.inTime || '—' }} / {{ a.outTime || '—' }}</td>
          </tr>
          <tr v-if="!myAttendance.length"><td colspan="4" style="text-align: center; color: #98a2b3; padding: 14px">No attendance records for this employee</td></tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="tab === 'leaves'" class="table-wrap">
      <table class="dt">
        <thead><tr><th>Type</th><th>From</th><th>To</th><th>Days</th><th>Status</th><th>Reason</th></tr></thead>
        <tbody>
          <tr v-for="l in myLeaves" :key="l.id">
            <td>{{ l.type }}</td>
            <td>{{ l.from }}</td>
            <td>{{ l.to }}</td>
            <td>{{ l.days }}</td>
            <td><span class="pill" :style="lvStyle(l.status)">{{ l.status }}</span></td>
            <td style="color: #667085">{{ l.reason }}</td>
          </tr>
          <tr v-if="!myLeaves.length"><td colspan="6" style="text-align: center; color: #98a2b3; padding: 14px">No leave records for this employee</td></tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="tab === 'payroll'">
      <div class="stat-card" style="padding: 12px; margin-bottom: 8px">
        <div style="font-size: 12px; font-weight: 600; margin-bottom: 8px">💰 Payroll snapshot</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px">
          <div>Base salary: <b>{{ bdt(me.salary ?? 0) }}</b></div>
          <div>Contract: <b>{{ me.contract?.type || '—' }}</b></div>
          <div>Joined: <b>{{ me.joinDate || '—' }}</b></div>
          <div>Designation: <b>{{ me.designation || '—' }}</b></div>
          <div>Department: <b>{{ me.dept || '—' }}</b></div>
          <div>Status: <b>{{ me.status || '—' }}</b></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

interface EmpRec {
  id: string
  name: string
  designation?: string
  dept?: string
  phone?: string
  email?: string
  joinDate?: string
  salary?: number
  status?: string
  contract?: { type?: string; start?: string }
}

const route = useRoute()
const router = useRouter()
const data = useDataStore()
const me = computed(() => {
  const q = String(route.params.name ?? '')
  const name = decodeURIComponent(q).toLowerCase().trim()
  if (!name) return null
  const arr = (data.employees as unknown as { id: string; name: string }[]) ?? []
  return (arr.find((e) => String(e.name ?? '').toLowerCase().trim() === name) ?? null) as unknown as EmpRec | null
})
const tab = ref('attendance')
const tabs = computed(() => [
  { id: 'attendance', label: 'Attendance', count: myAttendance.value.length },
  { id: 'leaves', label: 'Leaves', count: myLeaves.value.length },
  { id: 'payroll', label: 'Payroll', count: 1 },
])
const mine = (arr: unknown[], key: string) =>
  (arr ?? []).filter((x) => String((x as Record<string, unknown>)[key] ?? '').toLowerCase().trim() === String(me.value?.name ?? '').toLowerCase().trim())
const myAttendance = computed(() =>
  mine(data.attendance as unknown[], 'employeeName').map((a) => {
    const r = a as Record<string, unknown>
    return { id: String(r.id ?? ''), date: String(r.date ?? ''), status: String(r.status ?? ''), shift: String(r.shift ?? ''), inTime: String(r.inTime ?? ''), outTime: String(r.outTime ?? '') }
  }))
const myLeaves = computed(() =>
  (mine(data.leave as unknown[], 'employeeName') as unknown[]).map((l) => {
    const r = l as Record<string, unknown>
    return { id: String(r.id ?? ''), type: String(r.type ?? r.leave_type ?? ''), from: String(r.from ?? ''), to: String(r.to ?? ''), days: Number(r.days ?? 1), status: String(r.status ?? ''), reason: String(r.reason ?? '') }
  }))
const attendRate = computed(() => {
  const rows = myAttendance.value
  if (!rows.length) return 0
  const present = rows.filter((a) => ['Present', 'Half Day'].includes(String((a as Record<string, unknown>).status ?? ''))).length
  return Math.round((present / rows.length) * 100)
})
const pendLeaves = computed(() => myLeaves.value.filter((l) => String((l as Record<string, unknown>).status ?? '') === 'Pending').length)
const daysLate = computed(() => myAttendance.value.filter((a) => a.status === 'Late').length)
const initials = (n: string) => n.split(' ').map((p) => p[0]).join('').slice(0, 2).toUpperCase()
const statusColor = (s: string) => ({ Present: { bg: '#eafaf1', fg: '#27ae60' }, Absent: { bg: '#fdecea', fg: '#d64545' }, Late: { bg: '#fef5e7', fg: '#e67e22' }, 'Half Day': { bg: '#fef5e7', fg: '#e67e22' }, Leave: { bg: '#eaf1fe', fg: '#2F80ED' } })[s] || { bg: '#eef2f6', fg: '#667085' }
const lvStyle = (s: string) => ({ Approved: { background: '#eafaf1', color: '#27ae60' }, Pending: { background: '#fef5e7', color: '#e67e22' }, Rejected: { background: '#fdecea', color: '#d64545' } })[s] || { background: '#eef2f6', color: '#667085' }
</script>