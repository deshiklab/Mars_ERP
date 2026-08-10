<script setup lang="ts">
/**
 * EmployeeDetailDrawer — employee profile panel: avatar, identity,
 * contact, employment stats (dept, designation, join date, status),
 * salary breakdown, contract/insurance details.
 */
import { ref, watch } from 'vue'
import type { Employee } from '@/api/types'

const props = defineProps<{ employee: Employee | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()
const tab = ref('overview')
watch(() => props.employee, () => (tab.value = 'overview'))

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || '?'
}
function statusColor(s: string): string {
  return s === 'Active' ? '#2e7d32' : s === 'On Leave' ? '#e65100' : s === 'Resigned' ? '#c62828' : '#555'
}
</script>

<template>
  <div v-if="employee" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 520px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <div class="drawer-header" style="flex-shrink: 0">
        <h3>👤 {{ employee.name }}</h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto">
        <!-- identity header -->
        <div style="display: flex; gap: 12px; align-items: center; padding: 10px; background: #f8faff; border-radius: 8px; margin-bottom: 10px">
          <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #2f80ed, #56ccf2); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700">{{ initials(employee.name) }}</div>
          <div style="flex: 1">
            <div style="font-size: 14px; font-weight: 700; color: #222">{{ employee.name }}</div>
            <div style="font-size: 11px; color: #555">{{ employee.designation }} · {{ employee.dept }}</div>
            <div style="margin-top: 3px">
              <span class="pill" :style="{ background: statusColor(employee.status) + '22', color: statusColor(employee.status) }">{{ employee.status }}</span>
            </div>
          </div>
        </div>

        <!-- stats -->
        <div class="stats-row" style="grid-template-columns: 1fr 1fr">
          <div class="stat-card"><div class="label">📞 Phone</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ employee.phone || '—' }}</div></div>
          <div class="stat-card"><div class="label">✉ Email</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ employee.email || '—' }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">📅 Join Date</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ employee.joinDate || '—' }}</div></div>
          <div class="stat-card"><div class="label">💰 Salary</div><div style="font-size: 15px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ bdt(Number(employee.salary) || 0) }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">📄 Contract</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ employee.contract || '—' }}</div></div>
          <div class="stat-card"><div class="label">🛡 Insurance</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ employee.insurance || '—' }}</div></div>
        </div>

        <!-- actions -->
        <div style="margin-top: 14px; display: flex; gap: 6px; flex-wrap: wrap">
          <button class="action-btn" style="color: #2e7d32" @click="emit('status', 'Active')">✅ Mark Active</button>
          <button class="action-btn" style="color: #e65100" @click="emit('status', 'On Leave')">🏖 On Leave</button>
          <button class="action-btn" style="color: #c62828" @click="emit('status', 'Resigned')">✕ Resigned</button>
        </div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
        <button class="drawer-btn" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
