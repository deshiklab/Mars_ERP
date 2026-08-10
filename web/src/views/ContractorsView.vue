<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'
import type { Contractor } from '@/api/types'

const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])

onMounted(() => {
  data.loadContractors()
})

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

const columns = computed<TableColumn<Contractor>[]>(() => [
  {
    key: 'name',
    label: 'Contractor',
    renderHtml: (x) =>
      `<div style="display:flex;align-items:center;gap:8px">
        <span style="width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,#e65100,#2f80ed);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700">${esc(x.name.split(' ').slice(0, 2).map((w) => w[0]).join(''))}</span>
        <span style="font-weight:500;color:#333">${esc(x.name)}</span>
      </div>`
  },
  { key: 'specialty', label: 'Specialty', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.specialty || '—')}</span>` },
  { key: 'phone', label: 'Phone', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.phone || '—')}</span>` },
  {
    key: 'rating',
    label: 'Rating',
    sortable: true,
    renderHtml: (x) =>
      x.rating
        ? `<span style="display:inline-flex;padding:1px 5px;border-radius:4px;font-size:9px;font-weight:600;background:#fff8e1;color:#e65100">⭐ ${x.rating}</span>`
        : '<span style="font-size:9px;color:#aaa">—</span>'
  },
  { key: 'contracts', label: 'Contracts', sortable: true, renderHtml: (x) => `<span style="font-size:10px;color:#333">${x.contracts ?? 0}</span>` },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = (x.status || '').toLowerCase()
      const bg = s === 'active' ? '#e8f5e9' : s === 'on hold' ? '#fff3e0' : '#ffebee'
      const fg = s === 'active' ? '#2e7d32' : s === 'on hold' ? '#e65100' : '#c62828'
      return `<span class="pill" style="background:${bg};color:${fg}">${esc(x.status || '—')}</span>`
    }
  }
])

const stats = computed(() => [
  { label: 'Contractors', value: String(data.contractors.length), color: '#2f80ed' },
  { label: 'Active', value: String(data.contractors.filter((c) => (c.status || '').toLowerCase() === 'active').length), color: '#2e7d32' },
  { label: 'On Hold', value: String(data.contractors.filter((c) => (c.status || '').toLowerCase() === 'on hold').length), color: '#e65100' }
])
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = data.contractors as Record<string, unknown>[] } }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Contractors</span>
      <span class="page-subtitle">{{ data.contractors.length }} contractors</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.contractorsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading contractors…</p>

    <DataTable
      :actions="actions"
      v-else
      :columns="columns"
      :rows="data.contractors"
      :tabs="[{ id: 'all', label: 'All', count: data.contractors.length }]"
      search-placeholder="Search contractors…"
    />
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Contractors'" @close="detailRec = null" :records="detailList" />
</template>
