<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import BookingDetailDrawer from '@/components/BookingDetailDrawer.vue'
import type { TableAction, TableColumn, TableTab } from '@/components/DataTable.vue'
import type { Booking } from '@/api/types'

const route = useRoute()
const data = useDataStore()
const statusFilter = ref('')
const detail = ref<Booking | null>(null)
watch(
  () => route.query.bk,
  (v) => {
    if (v === '1' && !detail.value && data.bookings.length) detail.value = data.bookings[0]
  }
)


onMounted(() => {  data.loadBookings()
  .then(() => {
    if (route.query.bk === '1' && data.bookings.length) detail.value = data.bookings[0]
  })
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

function bdt(n: number): string {
  if (n >= 10000000) return `৳ ${(n / 10000000).toFixed(2)} Cr`
  if (n >= 100000) return `৳ ${(n / 100000).toFixed(1)} Lac`
  return `৳ ${n.toLocaleString()}`
}

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

const columns = computed<TableColumn<Booking>[]>(() => [
  {
    key: 'id',
    label: 'Booking',
    sortable: true,
    renderHtml: (b) =>
      `<div style="font-weight:600;color:#2f80ed">${esc(b.id)}</div><div style="font-size:9px;color:#888">${esc(b.date)} · ${esc(b.type)}</div>`
  },
  {
    key: 'client',
    label: 'Client',
    renderHtml: (b) => `<span style="font-weight:500;color:#333">${esc(b.client)}</span>`
  },
  {
    key: 'property',
    label: 'Property / Unit',
    renderHtml: (b) =>
      `<div style="color:#333">${esc(b.property)}</div><div style="font-size:9px;color:#888">${esc(b.unit)}</div>`
  },
  { key: 'price', label: 'Price', renderHtml: (b) => `<span style="font-size:10px;color:#555">${esc(b.price)}</span>` },
  {
    key: 'total_paid',
    label: 'Paid',
    sortable: true,
    renderHtml: (b) => `<span style="font-size:10px;color:#2e7d32;font-weight:600">${bdt(b.total_paid)}</span>`
  },
  {
    key: 'total_due',
    label: 'Due',
    sortable: true,
    renderHtml: (b) => `<span style="font-size:10px;color:#c62828;font-weight:600">${bdt(b.total_due)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (b) => {
      const s = statusStyle(b.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(b.status)}</span>`
    }
  }
])

const tabs = computed<TableTab[]>(() => [
  { id: 'all', label: 'All', count: data.bookings.length },
  { id: 'confirmed', label: 'Confirmed', count: data.bookings.filter((b) => b.status === 'Confirmed').length },
  { id: 'booked', label: 'Booked', count: data.bookings.filter((b) => b.status === 'Booked').length },
  { id: 'handed', label: 'Handed Over', count: data.bookings.filter((b) => b.status === 'Handed Over').length },
  { id: 'cancelled', label: 'Cancelled', count: data.bookings.filter((b) => b.status === 'Cancelled').length }
])

const tabRows = computed(() => {
  if (!statusFilter.value || statusFilter.value === 'all') return data.bookings
  const map: Record<string, string> = { confirmed: 'Confirmed', booked: 'Booked', handed: 'Handed Over', cancelled: 'Cancelled' }
  const st = map[statusFilter.value]
  return st ? data.bookings.filter((b) => b.status === st) : data.bookings
})

function onTabChange(tab: string) {
  statusFilter.value = tab
}

const actions = computed<TableAction[]>(() => [
  { label: 'View Details', icon: '👁', onClick: (r) => (detail.value = r as unknown as Booking) },
  { label: 'Mark Confirmed', icon: '✅', onClick: (r) => setStatus((r as unknown as Booking).id, 'Confirmed') },
  { label: 'Mark Handed Over', icon: '🔑', onClick: (r) => setStatus((r as unknown as Booking).id, 'Handed Over') },
  { label: 'Cancel Booking', icon: '❌', onClick: (r) => setStatus((r as unknown as Booking).id, 'Cancelled') }
])

async function setStatus(id: string, status: string) {
  await data.updateBookingStatus(id, status)
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Bookings</span>
      <span class="page-subtitle">
        {{ data.bookings.length }} bookings · {{ data.bookings.filter((b) => b.status === 'Confirmed').length }} confirmed
      </span>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.bookingsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading bookings…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="tabRows"
      :tabs="tabs"
      :actions="actions"
      search-placeholder="Search bookings, clients…"
      @tab-change="onTabChange"
    />

    <!-- Booking detail drawer (component) -->
    <BookingDetailDrawer :booking="detail" @close="detail = null" @status="(st: string) => detail && setStatus(detail.id, st)" />
  </div>
</template>
