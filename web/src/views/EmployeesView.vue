<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import EmployeeDetailDrawer from '@/components/EmployeeDetailDrawer.vue'
import type { TableAction, TableColumn, TableTab } from '@/components/DataTable.vue'
import type { Employee } from '@/api/types'

const route = useRoute()
const router = useRouter()
const data = useDataStore()
const detailEmp = ref<Employee | null>(null)
const tab = ref(String(route.query.tab ?? 'all').toLowerCase())
const detail = ref<Employee | null>(null)

onMounted(() => {
  data.loadEmployees()
})

function statusStyle(status: string): { bg: string; fg: string } {
  const s = (status || '').toLowerCase()
  if (s === 'active') return { bg: '#e8f5e9', fg: '#2e7d32' }
  if (s === 'on leave') return { bg: '#fff8e1', fg: '#ff8f00' }
  if (s === 'inactive' || s === 'resigned' || s === 'terminated') return { bg: '#ffebee', fg: '#c62828' }
  return { bg: '#f0f4ff', fg: '#2f80ed' }
}

function bdt(n: number): string {
  if (n >= 100000) return `৳ ${(n / 100000).toFixed(1)} Lac`
  return `৳ ${n.toLocaleString()}`
}

function monthsBetween(from: string): number {
  const d = new Date(from)
  if (Number.isNaN(d.getTime())) return 0
  return Math.max(0, Math.floor((Date.now() - d.getTime()) / (30.44 * 24 * 3600 * 1000)))
}

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

const avatar = (name: string) =>
  `<span style="width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#2f80ed,#0d1b2a);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700">${esc(name.split(' ').slice(0, 2).map((w) => w[0]).join(''))}</span>`

const columns = computed<TableColumn<Employee>[]>(() => [
  {
    key: 'name',
    label: 'Employee',
    renderHtml: (e) =>
      `<div style="display:flex;align-items:center;gap:8px">${avatar(e.name)}<span style="font-weight:500;color:#333">${esc(e.name)}</span></div>`
  },
  { key: 'designation', label: 'Designation', renderHtml: (e) => `<span style="font-size:10px;color:#555">${esc(e.designation)}</span>` },
  { key: 'dept', label: 'Dept', renderHtml: (e) => `<span style="font-size:10px;color:#555">${esc(e.dept)}</span>` },
  {
    key: 'phone',
    label: 'Contact',
    renderHtml: (e) =>
      `<div style="font-size:10px;color:#555">${esc(e.phone)}</div><div style="font-size:9px;color:#888">${esc(e.email)}</div>`
  },
  {
    key: 'joinDate',
    label: 'Joined',
    sortable: true,
    renderHtml: (e) =>
      `<div style="font-size:10px;color:#555">${esc(e.joinDate)}</div><div style="font-size:9px;color:#888">${monthsBetween(e.joinDate)}mo tenure</div>`
  },
  {
    key: 'salary',
    label: 'Salary',
    sortable: true,
    renderHtml: (e) => `<span style="font-size:10px;color:#333;font-weight:600">${bdt(e.salary)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (e) => {
      const s = statusStyle(e.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(e.status)}</span>`
    }
  }
])

const depts = computed(() => [...new Set(data.employees.map((e) => e.dept).filter(Boolean))])

const tabs = computed<TableTab[]>(() => [
  { id: 'all', label: 'All', count: data.employees.length },
  { id: 'active', label: 'Active', count: data.employees.filter((e) => e.status === 'active').length },
  { id: 'onleave', label: 'On Leave', count: data.employees.filter((e) => e.status === 'on leave').length },
  ...depts.value.slice(0, 4).map((d) => ({ id: d, label: d.split(' - ')[0], count: data.employees.filter((e) => e.dept === d).length }))
])

const tabRows = computed(() => {
  if (tab.value === 'all') return data.employees
  if (tab.value === 'active') return data.employees.filter((e) => e.status === 'active')
  if (tab.value === 'onleave') return data.employees.filter((e) => e.status === 'on leave')
  return data.employees.filter((e) => e.dept === tab.value)
})

function onTabChange(t: string) {
  void router.replace({ query: { ...route.query, tab: t } })
  tab.value = t
}

const actions = computed<TableAction[]>(() => [
  { label: 'View Profile', icon: '👤', onClick: (r) => (detailEmp.value = r as unknown as Employee) },
  { label: 'View Profile', icon: '👁', onClick: (r) => (detail.value = r as unknown as Employee) },
  { label: 'View Contract', icon: '📄', onClick: (r) => (detail.value = r as unknown as Employee) },
  { label: 'Mark On Leave', icon: '🏖', onClick: (r) => (detail.value = r as unknown as Employee) }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">HR & Employees</span>
      <span class="page-subtitle">
        {{ data.employees.length }} employees · {{ data.employees.filter((e) => e.status === 'active').length }} active
      </span>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.employeesLoading" style="font-size: 11px; color: #888; padding: 16px">Loading employees…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="tabRows"
      :tabs="tabs"
      :actions="actions"
      search-placeholder="Search employees, departments…"
      @tab-change="onTabChange"
    />

    <!-- Employee detail drawer -->
    <div v-if="detail" class="drawer-overlay active" @click.self="detail = null">
      <div class="drawer-sheet">
        <div class="drawer-header">
          <h3>{{ detail.name }} — {{ detail.designation }}</h3>
          <div class="drawer-close" @click="detail = null">✕</div>
        </div>
        <div class="drawer-body">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; font-size: 11px">
            <div><span style="color: #888">Department:</span> <b>{{ detail.dept }}</b></div>
            <div><span style="color: #888">Phone:</span> {{ detail.phone }}</div>
            <div><span style="color: #888">Email:</span> {{ detail.email }}</div>
            <div><span style="color: #888">Joined:</span> {{ detail.joinDate }}</div>
            <div><span style="color: #888">Salary:</span> <b>{{ bdt(detail.salary) }}</b></div>
            <div><span style="color: #888">Status:</span>
              <span class="pill" :style="{ background: statusStyle(detail.status).bg, color: statusStyle(detail.status).fg }">{{ detail.status }}</span>
            </div>
          </div>

          <h4 style="font-size: 12px; color: #333; margin: 14px 0 8px">Contract</h4>
          <div v-if="detail.contract" style="font-size: 11px; color: #555; line-height: 1.8">
            <div><span style="color: #888">Type:</span> {{ detail.contract.type }}</div>
            <div><span style="color: #888">Period:</span> {{ detail.contract.start }} → {{ detail.contract.end || '—' }}</div>
            <div><span style="color: #888">Notice period:</span> {{ detail.contract.noticePeriod ?? '—' }} days</div>
          </div>

          <h4 style="font-size: 12px; color: #333; margin: 14px 0 8px">Insurance</h4>
          <div v-if="detail.insurance" style="font-size: 11px; color: #555; line-height: 1.8">
            <div><span style="color: #888">Provider:</span> {{ detail.insurance.provider }}</div>
            <div><span style="color: #888">Policy:</span> {{ detail.insurance.policyNo }}</div>
            <div><span style="color: #888">Coverage:</span> <b style="color: #2e7d32">{{ bdt(detail.insurance.coverage) }}</b></div>
            <div><span style="color: #888">Expires:</span> {{ detail.insurance.expiry }}</div>
          </div>
        </div>
        <div class="drawer-footer">
          <button class="drawer-btn" @click="detail = null">Close</button>
        </div>
      </div>
    </div>
  </div>
    <EmployeeDetailDrawer :employee="detailEmp" @close="detailEmp = null" />
</template>
