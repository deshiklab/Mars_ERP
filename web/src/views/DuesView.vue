<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'

const data = useDataStore()
const bucketFilter = ref('')

onMounted(() => {
  data.loadDues()
})

const buckets = ['0-30 Days', '31-60 Days', '60+ Days']

function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Critical: ['#ffebee', '#c62828'],
    Overdue: ['#fff3e0', '#e65100'],
    Current: ['#e8f5e9', '#2e7d32'],
    Paid: ['#e3f2fd', '#1565c0']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const filtered = computed(() => {
  if (!bucketFilter.value) return data.dues
  return data.dues.filter((d) => d.bucket === bucketFilter.value)
})

const totalDue = computed(() => filtered.value.reduce((s, d) => s + (d.due ?? 0), 0))

function bdt(n: number): string {
  if (n >= 10000000) return `৳ ${(n / 10000000).toFixed(2)} Cr`
  if (n >= 100000) return `৳ ${(n / 100000).toFixed(1)} Lac`
  return `৳ ${n.toLocaleString()}`
}

function fupColor(days: string | undefined): string {
  if (!days) return '#888'
  const d = parseInt(days, 10)
  if (Number.isNaN(d)) return '#888'
  if (d <= 3) return '#2e7d32'
  if (d <= 7) return '#e65100'
  return '#c62828'
}

async function setStatus(id: string, event: Event) {
  const status = (event.target as HTMLSelectElement).value
  await data.updateDueStatus(id, status)
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Dues & Collections</span>
      <span class="page-subtitle">{{ data.dues.length }} accounts · total due {{ bdt(totalDue) }}</span>
      <div style="margin-left: auto">
        <select
          v-model="bucketFilter"
          style="padding: 3px 8px; font-size: 10px; border: 1px solid #e0e0e0; border-radius: 6px; outline: none; color: #555; background: #fff"
        >
          <option value="">All buckets</option>
          <option v-for="b in buckets" :key="b" :value="b">{{ b }}</option>
        </select>
      </div>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.duesLoading" style="font-size: 11px; color: #888; padding: 16px">Loading dues…</p>

    <div v-else class="card">
      <div class="table-wrap">
        <table class="rem-table">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Project / Unit</th>
              <th>Total</th>
              <th>Paid</th>
              <th>Due</th>
              <th>Due Date</th>
              <th>Bucket</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in filtered" :key="d.id">
              <td>
                <div style="font-weight: 500; color: #333">{{ d.customer }}</div>
                <div style="font-size: 9px; color: #888">{{ d.id }} · {{ d.phone }}</div>
              </td>
              <td>
                <div style="color: #333">{{ d.project }}</div>
                <div style="font-size: 9px; color: #888">{{ d.unit }}</div>
              </td>
              <td style="font-size: 10px; color: #555">{{ bdt(d.totalPrice) }}</td>
              <td style="font-size: 10px; color: #2e7d32; font-weight: 600">{{ bdt(d.paid) }}</td>
              <td style="font-size: 10px; color: #c62828; font-weight: 700">{{ bdt(d.due) }}</td>
              <td style="font-size: 10px; color: #555">
                {{ d.dueDate }}
                <div v-if="d.daysOverdue > 0" style="font-size: 9px; color: #c62828">{{ d.daysOverdue }}d overdue</div>
              </td>
              <td>
                <span class="pill" :style="{ background: d.bucket === '60+ Days' ? '#ffebee' : d.bucket === '31-60 Days' ? '#fff3e0' : '#e8f5e9', color: d.bucket === '60+ Days' ? '#c62828' : d.bucket === '31-60 Days' ? '#e65100' : '#2e7d32' }">
                  {{ d.bucket }}
                </span>
              </td>
              <td>
                <select
                  :value="d.status"
                  :style="{
                    padding: '1px 3px',
                    fontSize: '9px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    maxWidth: '90px',
                    background: statusStyle(d.status).bg,
                    color: statusStyle(d.status).fg,
                    fontWeight: 600,
                    outline: 'none'
                  }"
                  @change="setStatus(d.id, $event)"
                >
                  <option value="Current">Current</option>
                  <option value="Overdue">Overdue</option>
                  <option value="Critical">Critical</option>
                  <option value="Paid">Paid</option>
                </select>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="8" style="text-align: center; color: #888; padding: 20px; font-size: 11px">No dues found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
