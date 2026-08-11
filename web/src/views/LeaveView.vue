<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import { showToast } from '@/toast'
import { api } from '@/api/client'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'

const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

onMounted(() => {
  data.loadLeave()
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
  { label: 'Requests', value: String(data.leave.length), color: '#2f80ed' },
  { label: 'Pending', value: String(data.leave.filter(l=>l.status==='Pending').length), color: '#ff8f00' },
  { label: 'Approved', value: String(data.leave.filter(l=>l.status==='Approved').length), color: '#2e7d32' }
])

const showApply = ref(false)
const apEmp = ref('')
const apType = ref('Annual')
const apFrom = ref(new Date().toISOString().slice(0, 10))
const apTo = ref(new Date().toISOString().slice(0, 10))
const apDays = ref(1)
const apReason = ref('')
const apBusy = ref(false)
const apMsg = ref('')
const apEmps = computed(() => data.employees)
async function submitApply() {
  if (!apEmp.value || !apFrom.value || !apTo.value) { apMsg.value = 'Employee, from and to dates are required'; return }
  apBusy.value = true; apMsg.value = ''
  const emp = data.employees.find((e) => e.id === apEmp.value)
  const r = await api.call('leave_sync', { leave: [{ employeeId: apEmp.value, employeeName: emp?.name || emp?.id || '', type: apType.value, from: apFrom.value, to: apTo.value, days: Number(apDays.value) || 1, reason: apReason.value, status: 'Pending' }] })
  apBusy.value = false
  if (r.ok) {
    await data.loadLeave()
    showApply.value = false
    showToast('Leave request submitted')
  } else {
    apMsg.value = 'Could not submit the request — check the server'
  }
}
async function decideLeave(lv: Record<string, unknown>, status: string) {
  const r = await api.call('leave_sync', { leave: [{ employeeId: String(lv.employeeId ?? lv.employee ?? ''), employeeName: String(lv.employeeName ?? ''), type: String(lv.type ?? lv.leave_type ?? 'Annual'), from: String(lv.from ?? lv.from_date ?? ''), to: String(lv.to ?? ''), days: Number(lv.days) || 0, reason: String(lv.reason ?? ''), status }] })
  if (r.ok) {
    await data.loadLeave()
    showToast('Leave ' + status.toLowerCase())
  } else {
    showToast('Could not update the request')
  }
}
(window as unknown as { __decideLeave: (id: string, status: string) => void }).__decideLeave = (id: string, status: string) => {
  const lv = data.leave.find((l) => String(l.id) === id)
  if (lv) decideLeave(lv as unknown as Record<string, unknown>, status)
}
const columns = computed<TableColumn<any>[]>(() => [
  {
    key: 'employeeName',
    label: 'Employee',
    sortable: false,
    renderHtml: (x) => `<div style='font-weight:500;color:#333'>${esc(x.employeeName)}</div><div style='font-size:9px;color:#888'>${esc(x.employeeId||'')}</div>`
  },
  {
    key: 'type',
    label: 'Type',
    sortable: false,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.type||'—')}</span>`
  },
  {
    key: 'from',
    label: 'From',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.from||'—')}</span>`
  },
  {
    key: 'to',
    label: 'To',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#555'>${esc(x.to||'—')}</span>`
  },
  {
    key: 'days',
    label: 'Days',
    sortable: true,
    renderHtml: (x) => `<span style='font-size:10px;color:#333;font-weight:600'>${esc(x.days??'—')}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => x.status === 'Pending'
      ? `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>
         <button onclick="event.stopPropagation();window.__decideLeave('${esc(String(x.id))}','Approved')" style="margin-left:6px;padding:3px 8px;background:#2e7d32;color:#fff;border:0;border-radius:4px;font-size:10px;cursor:pointer">✓ Approve</button>
         <button onclick="event.stopPropagation();window.__decideLeave('${esc(String(x.id))}','Rejected')" style="margin-left:4px;padding:3px 8px;background:#c62828;color:#fff;border:0;border-radius:4px;font-size:10px;cursor:pointer">✕ Reject</button>`
      : `<span class='pill' style='background:${statusColor(x.status).bg};color:${statusColor(x.status).fg}'>${esc(x.status||'—')}</span>`
  },])

const rows = computed(() => data.leave)
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = rows.value as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Leave Requests</span>
      <span class="page-subtitle">{{ data.leave.length }} records</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <DataTable
      :actions="actions"
      :columns="columns"
      :rows="rows"
      :tabs="[{ id: 'all', label: 'All', count: rows.length }]"
      search-placeholder="Search leave…"
    />
  </div>
    <div style="display: flex; justify-content: flex-end; margin: 6px 0">
      <button @click="showApply = true" style="padding: 6px 12px; background: #2F80ED; color: #fff; border: 0; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer">+ Apply leave</button>
    </div>
    <div v-if="showApply" class="drawer-sheet" style="z-index: 10001">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px">
        <span style="font-size: 13px; font-weight: 700">📅 Apply leave</span>
        <button @click="showApply = false" style="background: none; border: 0; font-size: 15px; cursor: pointer; color: #888">✕</button>
      </div>
      <label style="font-size: 10px; color: #888">EMPLOYEE</label>
      <select v-model="apEmp" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px">
        <option value="">— Select employee —</option>
        <option v-for="e in apEmps" :key="e.id" :value="e.id">{{ e.name || e.id }}</option>
      </select>
      <label style="font-size: 10px; color: #888">TYPE</label>
      <select v-model="apType" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px">
        <option>Annual</option>
        <option>Casual</option>
        <option>Sick</option>
        <option>Unpaid</option>
      </select>
      <div style="display: flex; gap: 8px">
        <div style="flex: 1"><label style="font-size: 10px; color: #888">FROM</label>
        <input v-model="apFrom" type="date" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" /></div>
        <div style="flex: 1"><label style="font-size: 10px; color: #888">TO</label>
        <input v-model="apTo" type="date" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" /></div>
        <div style="flex: 1"><label style="font-size: 10px; color: #888">DAYS</label>
        <input v-model="apDays" type="number" min="1" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" /></div>
      </div>
      <label style="font-size: 10px; color: #888">REASON</label>
      <input v-model="apReason" placeholder="Reason for leave" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; font-size: 12px; margin: 3px 0 8px" />
      <p v-if="apMsg" style="font-size: 11px; color: #c62828; margin: 4px 0">{{ apMsg }}</p>
      <button @click="submitApply" :disabled="apBusy" style="width: 100%; padding: 10px; background: #2F80ED; color: #fff; border: 0; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer">{{ apBusy ? 'Submitting…' : 'Submit request' }}</button>
    </div>
    <GenericDetailDrawer :record="detailRec"  :title="'Leave Requests'" @close="detailRec = null" :records="detailList" />
</template>
