<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import { api } from '@/api/client'
import { showToast } from '@/toast'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

onMounted(() => {
  data.loadAttendance()
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function statusColor(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Active: ['#e8f5e9', '#2e7d32'],
    Available: ['#e8f5e9', '#2e7d32'],
    Approved: ['#e8f5e9', '#2e7d32'],
    Completed: ['#e8f5e9', '#2e7d32'],
    'Handed Over': ['#e3f2fd', '#1565c0'],
    Resolved: ['#e8f5e9', '#2e7d32'],
    Closed: ['#e8f5e9', '#2e7d32'],
    Paid: ['#e8f5e9', '#2e7d32'],
    Present: ['#e8f5e9', '#2e7d32'],
    'In Use': ['#e8f5e9', '#2e7d32'],
    Inactive: ['#f0f0f0', '#555'],
    Pending: ['#fff8e1', '#ff8f00'],
    'In Progress': ['#fff3e0', '#e65100'],
    Open: ['#ffebee', '#c62828'],
    Absent: ['#ffebee', '#c62828'],
    Half: ['#fff3e0', '#e65100'],
    Late: ['#fff3e0', '#e65100'],
    'On Leave': ['#fff3e0', '#e65100'],
    'On Hold': ['#fff3e0', '#e65100'],
    Rejected: ['#ffebee', '#c62828'],
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const stats = computed(() => [
  { label: 'Records', value: String(data.attendance.length), color: '#2f80ed' },
  { label: 'Present', value: String(data.attendance.filter(a=>a.status==='Present').length), color: '#2e7d32' },
  { label: 'Absent', value: String(data.attendance.filter(a=>a.status==='Absent').length), color: '#c62828' },
  { label: 'Half Day', value: String(data.attendance.filter(a=>a.status==='Half Day').length), color: '#ef6c00' },
  { label: 'Leave', value: String(data.attendance.filter(a=>a.status==='Leave').length), color: '#6a1b9a' }
])

const showMark = ref(false)
const mkEmp = ref('')
const mkDate = ref(new Date().toISOString().slice(0, 10))
const mkStatus = ref('Present')
const mkShift = ref('Day')
const mkIn = ref('')
const mkOut = ref('')
const mkNotes = ref('')
const mkBusy = ref(false)
const mkMsg = ref('')
async function submitMark() {
  if (!mkEmp.value || !mkDate.value) { mkMsg.value = 'Employee and date are required'; return }
  mkBusy.value = true; mkMsg.value = ''
  const emp = data.employees.find((e) => e.id === mkEmp.value)
  const r = await api.call('attendance_sync', { attendance: [{ employeeId: mkEmp.value, employeeName: emp?.name || emp?.id || '', date: mkDate.value, status: mkStatus.value, shift: mkShift.value, inTime: mkIn.value, outTime: mkOut.value, notes: mkNotes.value }] })
  mkBusy.value = false
  if (r.ok) {
    await data.loadAttendance()
    showMark.value = false
    showToast('Attendance marked for ' + mkDate.value)
  } else {
    mkMsg.value = 'Could not mark attendance — check the server'
  }
}
const mkEmps = computed(() => data.employees)
const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'employeeName',
    label: 'Employee',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.employeeName)}</div><div style='font-size:9px;color:#888'>${esc(x.employeeId||'')}</div>`
  },
  {
    key: 'date',
    label: 'Date',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.date||'—')}</span>`
  },
  {
    key: 'inTime',
    label: 'In',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.inTime||'—')}</span>`
  },
  {
    key: 'outTime',
    label: 'Out',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.outTime||'—')}</span>`
  },
  {
    key: 'shift',
    label: 'Shift',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.shift||'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])

const rows = computed(() => data.attendance)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Attendance & Leave</span>
      <span class="page-subtitle">{{ data.attendance.length }} records</span>
    </div>

    <div style="display: flex; justify-content: flex-end; margin: 6px 0">
      <button @click="showMark = true" style="padding: 6px 12px; background: #2F80ED; color: #fff; border: 0; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer">+ Mark attendance</button>
    </div>
    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search attendance…"
    />
  </div>
    <div v-if="showMark" class="drawer-sheet" style="z-index: 10001">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px">
        <span style="font-size: 13px; font-weight: 700">📝 Mark attendance</span>
        <button @click="showMark = false" style="background: none; border: 0; font-size: 15px; cursor: pointer; color: #888">✕</button>
      </div>
      <label style="font-size: 10px; color: #888">EMPLOYEE</label>
      <select v-model="mkEmp" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px">
        <option value="">— Select employee —</option>
        <option v-for="e in mkEmps" :key="e.id" :value="e.id">{{ e.name || e.id }}</option>
      </select>
      <label style="font-size: 10px; color: #888">DATE</label>
      <input v-model="mkDate" type="date" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" />
      <label style="font-size: 10px; color: #888">STATUS</label>
      <select v-model="mkStatus" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px">
        <option>Present</option>
        <option>Absent</option>
        <option>Half Day</option>
        <option>Leave</option>
      </select>
      <div style="display: flex; gap: 8px">
        <div style="flex: 1"><label style="font-size: 10px; color: #888">SHIFT</label>
        <input v-model="mkShift" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" /></div>
        <div style="flex: 1"><label style="font-size: 10px; color: #888">IN</label>
        <input v-model="mkIn" type="time" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" /></div>
        <div style="flex: 1"><label style="font-size: 10px; color: #888">OUT</label>
        <input v-model="mkOut" type="time" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" /></div>
      </div>
      <label style="font-size: 10px; color: #888">NOTES</label>
      <input v-model="mkNotes" placeholder="Optional note" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" />
      <p v-if="mkMsg" style="font-size: 11px; color: #c62828; margin: 4px 0">{{ mkMsg }}</p>
      <button @click="submitMark" :disabled="mkBusy" style="width: 100%; padding: 10px; background: #2F80ED; color: #fff; border: 0; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer">{{ mkBusy ? 'Saving…' : 'Save attendance' }}</button>
    </div>
    <GenericDetailDrawer :record="detailRec"  :title="'Attendance & Leave'" @close="detailRec = null" :records="detailList" />
</template>
