<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import type { Employee } from '@/api/types'

const data = useDataStore()
const deptFilter = ref('')
const detail = ref<Employee | null>(null)

onMounted(() => {
  data.loadEmployees()
})

const depts = computed(() => [...new Set(data.employees.map((e) => e.dept).filter(Boolean))])

const filtered = computed(() => {
  if (!deptFilter.value) return data.employees
  return data.employees.filter((e) => e.dept === deptFilter.value)
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
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">HR & Employees</span>
      <span class="page-subtitle">{{ data.employees.length }} employees · {{ data.employees.filter((e) => e.status === 'active').length }} active</span>
      <div style="margin-left: auto">
        <select
          v-model="deptFilter"
          style="padding: 3px 8px; font-size: 10px; border: 1px solid #e0e0e0; border-radius: 6px; outline: none; color: #555; background: #fff"
        >
          <option value="">All departments</option>
          <option v-for="d in depts" :key="d" :value="d">{{ d }}</option>
        </select>
      </div>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.employeesLoading" style="font-size: 11px; color: #888; padding: 16px">Loading employees…</p>

    <div v-else class="card">
      <div class="table-wrap">
        <table class="rem-table">
          <thead>
            <tr>
              <th>Employee</th>
              <th>Designation</th>
              <th>Dept</th>
              <th>Contact</th>
              <th>Joined</th>
              <th>Salary</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in filtered" :key="e.id" style="cursor: pointer" @click="detail = e">
              <td>
                <div style="display: flex; align-items: center; gap: 8px">
                  <span
                    style="width: 26px; height: 26px; border-radius: 50%; background: linear-gradient(135deg, #2f80ed, #0d1b2a); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700"
                  >{{ e.name.split(' ').slice(0, 2).map((w) => w[0]).join('') }}</span>
                  <span style="font-weight: 500; color: #333">{{ e.name }}</span>
                </div>
              </td>
              <td style="font-size: 10px; color: #555">{{ e.designation }}</td>
              <td style="font-size: 10px; color: #555">{{ e.dept }}</td>
              <td>
                <div style="font-size: 10px; color: #555">{{ e.phone }}</div>
                <div style="font-size: 9px; color: #888">{{ e.email }}</div>
              </td>
              <td style="font-size: 10px; color: #555">
                {{ e.joinDate }}
                <div style="font-size: 9px; color: #888">{{ monthsBetween(e.joinDate) }}mo tenure</div>
              </td>
              <td style="font-size: 10px; color: #333; font-weight: 600">{{ bdt(e.salary) }}</td>
              <td>
                <span class="pill" :style="{ background: statusStyle(e.status).bg, color: statusStyle(e.status).fg }">
                  {{ e.status }}
                </span>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="7" style="text-align: center; color: #888; padding: 20px; font-size: 11px">No employees found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

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
          <div style="font-size: 11px; color: #555; line-height: 1.8" v-if="detail.contract">
            <div><span style="color: #888">Type:</span> {{ detail.contract.type }}</div>
            <div><span style="color: #888">Period:</span> {{ detail.contract.start }} → {{ detail.contract.end || '—' }}</div>
            <div><span style="color: #888">Notice period:</span> {{ detail.contract.noticePeriod ?? '—' }} days</div>
          </div>

          <h4 style="font-size: 12px; color: #333; margin: 14px 0 8px">Insurance</h4>
          <div style="font-size: 11px; color: #555; line-height: 1.8" v-if="detail.insurance">
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
</template>
