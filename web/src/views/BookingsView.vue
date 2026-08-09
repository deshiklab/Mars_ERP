<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import type { Booking } from '@/api/types'

const data = useDataStore()
const statusFilter = ref('')
const detail = ref<Booking | null>(null)

onMounted(() => {
  data.loadBookings()
})

const statusOptions = ['Inquiry', 'Booked', 'Confirmed', 'Under Construction', 'Handed Over', 'Cancelled']

function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Inquiry: ['#f0f4ff', '#2f80ed'],
    Booked: ['#fff8e1', '#ff8f00'],
    Confirmed: ['#e8f5e9', '#2e7d32'],
    'Under Construction': ['#fff3e0', '#e65100'],
    'Handed Over': ['#e3f2fd', '#1565c0'],
    Cancelled: ['#ffebee', '#c62828']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const filtered = computed(() => {
  if (!statusFilter.value) return data.bookings
  return data.bookings.filter((b) => b.status === statusFilter.value)
})

function bdt(n: number): string {
  if (n >= 10000000) return `৳ ${(n / 10000000).toFixed(2)} Cr`
  if (n >= 100000) return `৳ ${(n / 100000).toFixed(1)} Lac`
  return `৳ ${n.toLocaleString()}`
}

async function setStatus(id: string, event: Event) {
  const status = (event.target as HTMLSelectElement).value
  await data.updateBookingStatus(id, status)
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Bookings</span>
      <span class="page-subtitle">{{ data.bookings.length }} bookings · {{ data.bookings.filter((b) => b.status === 'Confirmed').length }} confirmed</span>
      <div style="margin-left: auto">
        <select
          v-model="statusFilter"
          style="padding: 3px 8px; font-size: 10px; border: 1px solid #e0e0e0; border-radius: 6px; outline: none; color: #555; background: #fff"
        >
          <option value="">All statuses</option>
          <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.bookingsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading bookings…</p>

    <div v-else class="card">
      <div class="table-wrap">
        <table class="rem-table">
          <thead>
            <tr>
              <th>Booking</th>
              <th>Client</th>
              <th>Property / Unit</th>
              <th>Price</th>
              <th>Paid</th>
              <th>Due</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in filtered" :key="b.id" style="cursor: pointer" @click="detail = b">
              <td style="font-weight: 600; color: #2f80ed">{{ b.id }}</td>
              <td>
                <div style="font-weight: 500; color: #333">{{ b.client }}</div>
                <div style="font-size: 9px; color: #888">{{ b.date }} · {{ b.type }}</div>
              </td>
              <td>
                <div style="color: #333">{{ b.property }}</div>
                <div style="font-size: 9px; color: #888">{{ b.unit }}</div>
              </td>
              <td style="font-size: 10px; color: #555">{{ b.price }}</td>
              <td style="font-size: 10px; color: #2e7d32; font-weight: 600">{{ bdt(b.total_paid) }}</td>
              <td style="font-size: 10px; color: #c62828; font-weight: 600">{{ bdt(b.total_due) }}</td>
              <td @click.stop>
                <select
                  :value="b.status"
                  :style="{
                    padding: '1px 3px',
                    fontSize: '9px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    maxWidth: '110px',
                    background: statusStyle(b.status).bg,
                    color: statusStyle(b.status).fg,
                    fontWeight: 600,
                    outline: 'none'
                  }"
                  @change="setStatus(b.id, $event)"
                >
                  <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
                </select>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="7" style="text-align: center; color: #888; padding: 20px; font-size: 11px">No bookings found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Booking detail drawer -->
    <div v-if="detail" class="drawer-overlay active" @click.self="detail = null">
      <div class="drawer-sheet">
        <div class="drawer-header">
          <h3>{{ detail.id }} — {{ detail.client }}</h3>
          <div class="drawer-close" @click="detail = null">✕</div>
        </div>
        <div class="drawer-body">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; font-size: 11px">
            <div><span style="color: #888">Property:</span> <b>{{ detail.property }}</b></div>
            <div><span style="color: #888">Unit:</span> <b>{{ detail.unit }}</b></div>
            <div><span style="color: #888">Type:</span> {{ detail.type }}</div>
            <div><span style="color: #888">Date:</span> {{ detail.date }}</div>
            <div><span style="color: #888">Price:</span> {{ detail.price }}</div>
            <div><span style="color: #888">Advance:</span> {{ detail.advance }}</div>
            <div style="color: #2e7d32"><span style="color: #888">Paid:</span> <b>{{ bdt(detail.total_paid) }}</b></div>
            <div style="color: #c62828"><span style="color: #888">Due:</span> <b>{{ bdt(detail.total_due) }}</b></div>
          </div>

          <h4 style="font-size: 12px; color: #333; margin: 14px 0 8px">Installment schedule</h4>
          <div class="table-wrap">
            <table class="rem-table">
              <thead>
                <tr><th>#</th><th>Date</th><th>Amount</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr v-for="inst in detail.installments" :key="inst.no">
                  <td>{{ inst.no }}</td>
                  <td>{{ inst.date }}</td>
                  <td>{{ bdt(inst.amount) }}</td>
                  <td>
                    <span
                      class="pill"
                      :style="inst.status === 'Paid' ? 'background:#e8f5e9;color:#2e7d32' : 'background:#fff3e0;color:#e65100'"
                    >{{ inst.status }}</span>
                  </td>
                </tr>
                <tr v-if="!detail.installments || detail.installments.length === 0">
                  <td colspan="4" style="text-align: center; color: #888; padding: 14px; font-size: 10px">No installments</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="drawer-footer">
          <button class="drawer-btn" @click="detail = null">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>
