<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import GenericDetailDrawer from '@/components/GenericDetailDrawer.vue'
import StatsRow from '@/components/StatsRow.vue'
import type { TableColumn } from '@/components/DataTable.vue'
import type { PurchaseOrder, StockItem } from '@/api/types'
import { api } from '@/api/client'
import { showToast } from '@/toast'

const route = useRoute()
const router = useRouter()
const data = useDataStore()
const detailRec = ref<Record<string, unknown> | null>(null)
const detailList = ref<Record<string, unknown>[]>([])
const tab = ref(String(route.query.tab ?? 'inventory').toLowerCase())
function setTab(t: string) {
  tab.value = t
  void router.replace({ query: { ...route.query, tab: t } })
}

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
      const b = (st: string, lbl: string, col: string) =>
        `<button onclick="event.stopPropagation();window.__poAct('${x.id}','${st}')" style="font-size:9px;font-weight:700;color:#fff;background:${col};border:none;border-radius:8px;padding:2px 7px;cursor:pointer;margin-left:4px">${lbl}</button>`
      let acts = ''
      if (x.status === 'Pending Approval') acts = b('Approved', '✓ Approve', '#2e7d32') + b('Cancelled', '✕', '#d64545')
      else if (x.status === 'Approved') acts = b('Delivered', '📦 Delivered', '#2f80ed')
      else if (x.status === 'Delivered') acts = b('Completed', '✓ Complete', '#2e7d32')
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(x.status)}</span>${acts}`
    }
  }
])

/* PO table */
const showPo = ref(false)
const showIt = ref(false)
const poBusy = ref(false)
const poFields = ref({ vendor: '', category: '', site: '', date: '', due: '', amount: '' })
const itFields = ref({ item: '', unit: '', site: '', qty: '', value: '' })
const vendors = computed(() => Array.from(new Set((data.pos as { vendor?: string }[]).map((p) => p.vendor || '').filter(Boolean))))
const sites = computed(() => Array.from(new Set((data.pos as { site?: string }[]).map((p) => p.site || '').filter(Boolean))))

async function poAct(id: string, status: string) {
  const row = (data.pos as { id?: string }[]).find((p) => p.id === id)
  if (!row) return
  poBusy.value = true
  const r = await api.call('po_sync', { pos: [{ id, vendor: (row as { vendor?: string }).vendor || '', date: (row as { date?: string }).date || '', dueDate: (row as { dueDate?: string }).dueDate || '', site: (row as { site?: string }).site || '', category: (row as { category?: string }).category || '', amount: (row as { amount?: number }).amount || 0, status }] })
  poBusy.value = false
  if (r.ok) {
    await data.loadPos()
    showToast(`PO ${id} → ${status}`)
  } else showToast('PO update failed — try again')
}

async function submitPo() {
  poBusy.value = true
  const r = await api.call('po_sync', { pos: [{ id: 'PO-' + Date.now().toString().slice(-6), vendor: poFields.value.vendor, category: poFields.value.category, site: poFields.value.site, date: poFields.value.date, dueDate: poFields.value.due, amount: Number(poFields.value.amount) || 0, status: 'Pending Approval' }] })
  poBusy.value = false
  if (r.ok) { await data.loadPos(); showPo.value = false; showToast('Purchase order created') }
  else showToast('Could not create PO')
}

async function submitItem() {
  poBusy.value = true
  const r = await api.call('inventory_sync', { inventory: [{ id: 'ITM-' + Date.now().toString().slice(-6), item: itFields.value.item, unit: itFields.value.unit || 'Nos', site: itFields.value.site, qty: Number(itFields.value.qty) || 0, value: Number(itFields.value.value) || 0 }] })
  poBusy.value = false
  if (r.ok) { await data.loadInventory(); showIt.value = false; showToast('Item added to inventory') }
  else showToast('Could not add item')
}

;(window as unknown as { __poAct: (id: string, status: string) => void }).__poAct = poAct

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
  { label: 'View Details', icon: '👁', onClick: (r: unknown) => { detailRec.value = r as Record<string, unknown>; detailList.value = data.inventory as Record<string, unknown>[] } }
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
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, background: tab === 'inventory' ? '#f0f4ff' : '#fff', color: '#2f80ed' }" @click="setTab('inventory')">📦 Inventory</button>
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, borderLeft: '1px solid #e0e0e0', background: tab === 'pos' ? '#f0f4ff' : '#fff', color: '#2f80ed' }" @click="setTab('pos')">📄 Purchase Orders</button>
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, borderLeft: '1px solid #e0e0e0', background: '#fff', color: '#2e7d32' }" @click="showPo = true">+ New PO</button>
      <button class="action-btn" :style="{ border: 'none', borderRadius: 0, borderLeft: '1px solid #e0e0e0', background: '#fff', color: '#2e7d32' }" @click="showIt = true">+ New Item</button>
    </div>
  </div>
    <GenericDetailDrawer :record="detailRec" :title="'Stock & Procurement'" @close="detailRec = null" :records="detailList" />

    <!-- New PO drawer -->
    <div v-if="showPo" class="drawer-sheet" style="position: fixed; top: 0; right: 0; width: 720px; max-width: 100%; height: 100%; background: #fff; z-index: 10001; box-shadow: -4px 0 20px rgba(0,0,0,.15); overflow-y: auto">
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid #eee">
        <h3 style="margin: 0; font-size: 14px">📄 New Purchase Order</h3>
        <button class="action-btn" @click="showPo = false">✕</button>
      </div>
      <div style="padding: 16px; display: flex; flex-direction: column; gap: 10px">
        <input v-model="poFields.vendor" placeholder="Vendor name *" style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" list="po-vendors" />
        <datalist id="po-vendors"><option v-for="v in vendors" :key="v" :value="v" /></datalist>
        <input v-model="poFields.category" placeholder="Category (e.g. Cement, Steel…)" style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
        <input v-model="poFields.site" placeholder="Site" style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" list="po-sites" />
        <datalist id="po-sites"><option v-for="s in sites" :key="s" :value="s" /></datalist>
        <div style="display: flex; gap: 8px">
          <input v-model="poFields.date" type="date" style="flex: 1; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
          <input v-model="poFields.due" type="date" style="flex: 1; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
        </div>
        <input v-model="poFields.amount" type="number" placeholder="Amount (৳)" style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
        <button class="action-btn" style="background: #2e7d32; color: #fff" :disabled="poBusy || !poFields.vendor" @click="submitPo">{{ poBusy ? 'Saving…' : 'Create PO' }}</button>
      </div>
    </div>

    <!-- New Item drawer -->
    <div v-if="showIt" class="drawer-sheet" style="position: fixed; top: 0; right: 0; width: 720px; max-width: 100%; height: 100%; background: #fff; z-index: 10001; box-shadow: -4px 0 20px rgba(0,0,0,.15); overflow-y: auto">
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid #eee">
        <h3 style="margin: 0; font-size: 14px">📦 New Inventory Item</h3>
        <button class="action-btn" @click="showIt = false">✕</button>
      </div>
      <div style="padding: 16px; display: flex; flex-direction: column; gap: 10px">
        <input v-model="itFields.item" placeholder="Item name *" style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
        <input v-model="itFields.unit" placeholder="Unit (Nos, Bags, Cft…)" style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
        <input v-model="itFields.site" placeholder="Site" style="padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" list="po-sites" />
        <div style="display: flex; gap: 8px">
          <input v-model="itFields.qty" type="number" placeholder="Quantity" style="flex: 1; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
          <input v-model="itFields.value" type="number" placeholder="Value (৳)" style="flex: 1; padding: 8px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px" />
        </div>
        <button class="action-btn" style="background: #2e7d32; color: #fff" :disabled="poBusy || !itFields.item" @click="submitItem">{{ poBusy ? 'Saving…' : 'Add Item' }}</button>
      </div>
    </div>
</template>
