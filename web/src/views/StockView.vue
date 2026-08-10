<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'
import type { PurchaseOrder, StockItem } from '@/api/types'

const route = useRoute()
const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const tab = ref('inventory')

onMounted(() => {
  data.loadInventory()
  data.loadPos()
  Promise.all([data.loadInventory(), data.loadPos()]).then(() => {
    if (route.query.d === '1' && data.inventory.length) detailRec.value = data.inventory[0] as unknown as Record<string, unknown>
  })
})

function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Adequate: ['#e8f5e9', '#2e7d32'],
    'Low Stock': ['#fff3e0', '#e65100'],
    'Out of Stock': ['#ffebee', '#c62828'],
    Ordered: ['#f0f4ff', '#2f80ed'],
    Approved: ['#e8f5e9', '#2e7d32'],
    Pending: ['#fff8e1', '#ff8f00'],
    Delivered: ['#e3f2fd', '#1565c0'],
    Received: ['#e3f2fd', '#1565c0']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))
const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

/* inventory table */
const invCols = computed<TableColumn<StockItem>[]>(() => [
  {
    key: 'item',
    label: 'Item',
    renderHtml: (x) => `<div style="font-weight:500;color:#333">${esc(x.item)}</div><div style="font-size:9px;color:#888">${esc(x.category)}</div>`
  },
  { key: 'site', label: 'Site', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.site)}</span>` },
  {
    key: 'qty',
    label: 'Qty',
    sortable: true,
    renderHtml: (x) => `<b style="font-size:11px;color:#333">${x.qty}</b> <span style="font-size:9px;color:#888">${esc(x.unit)}</span>`
  },
  {
    key: 'price',
    label: 'Price',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:10px;color:#555">${bdt(x.price)}</span>`
  },
  {
    key: 'value',
    label: 'Value',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:10px;color:#2e7d32;font-weight:600">${bdt(x.value)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = statusStyle(x.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(x.status)}</span>`
    }
  }
])

/* PO table */
const poCols = computed<TableColumn<PurchaseOrder>[]>(() => [
  {
    key: 'id',
    label: 'PO',
    sortable: true,
    renderHtml: (x) => `<div style="font-weight:600;color:#2f80ed">${esc(x.id)}</div><div style="font-size:9px;color:#888">${esc(x.date)}</div>`
  },
  { key: 'vendor', label: 'Vendor', renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:500">${esc(x.vendor)}</span>` },
  { key: 'site', label: 'Site', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.site)}</span>` },
  { key: 'items', label: 'Items', renderHtml: (x) => `<span style="font-size:10px;color:#555">${esc(x.items)}</span>` },
  {
    key: 'amount',
    label: 'Amount',
    sortable: true,
    renderHtml: (x) => `<span style="font-size:10px;color:#333;font-weight:600">${esc(x.fmt)}</span>`
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (x) => {
      const s = statusStyle(x.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(x.status)}</span>`
    }
  }
])

const invStats = computed(() => [
  { label: 'Items', value: String(data.inventory.length), color: '#2f80ed' },
  { label: 'Stock Value', value: bdt(data.inventory.reduce((s, i) => s + (i.value ?? 0), 0)), color: '#2e7d32' },
  { label: 'Low / Out', value: String(data.inventory.filter((i) => i.status !== 'Adequate').length), color: '#e65100' },
  { label: 'Purchase Orders', value: String(data.pos.length), color: '#1565c0' }
])
const actions = computed(() => [
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => (detailRec.value = r as Record<string, unknown>) }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Stock & Procurement</span>
      <span class="page-subtitle">{{ data.inventory.length }} items · {{ data.pos.length }} purchase orders</span>
    </div>

    <StatsRow :stats="invStats" />

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>

    <div v-if="tab === 'inventory'">
      <DataTable
      :actions="actions"
        :columns="invCols"
        :rows="data.inventory"
        :tabs="[{ id: 'all', label: 'All', count: data.inventory.length }]"
        search-placeholder="Search items, sites…"
      />
    </div>
    <div v-else>
      <DataTable
        :columns="poCols"
        :rows="data.pos"
        :tabs="[{ id: 'all', label: 'Purchase Orders', count: data.pos.length }]"
        search-placeholder="Search vendors, POs…"
      />
    </div>

    <!-- view toggle -->
    <div style="display: flex; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; margin-bottom: 10px; width: fit-content">
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, background: tab === 'inventory' ? '#f0f4ff' : '#fff', color: '#2f80ed' }" @click="tab = 'inventory'">📦 Inventory</button>
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, borderLeft: '1px solid #e0e0e0', background: tab === 'pos' ? '#f0f4ff' : '#fff', color: '#2f80ed' }" @click="tab = 'pos'">📄 Purchase Orders</button>
    </div>
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Stock & Procurement'" @close="detailRec = null" />
</template>
