/**
 * DataTable — full table toolkit mirroring the HTML PWA:
 * toolbar (rows info, Filter, CSV, Print, Columns), sortable headers,
 * column visibility, live search filter, row action menu (⋯), tabs,
 * pagination + page info + page-size.
 */
<script setup lang="ts">
import { computed, ref, watch } from 'vue'

export interface TableColumn<T> {
  key: string
  label: string
  sortable?: boolean
  width?: string
  render?: (row: T) => string
  /** raw HTML cell renderer (for pills/badges) — NOT escaped */
  renderHtml?: (row: T) => string
}

export interface TableAction {
  label: string
  icon?: string
  onClick: (row: Record<string, unknown>) => void
}

export interface TableTab {
  id: string
  label: string
  count?: number
}

const props = withDefaults(
  defineProps<{
    columns: TableColumn<any>[]
    rows: any[]
    tabs?: TableTab[]
    pageSizeOptions?: number[]
    defaultPageSize?: number
    actions?: TableAction[]
    searchPlaceholder?: string
  }>(),
  {
    tabs: () => [],
    pageSizeOptions: () => [10, 25, 50, 100],
    defaultPageSize: 10,
    actions: () => [],
    searchPlaceholder: 'Search…'
  }
)

const emit = defineEmits<{
  (e: 'tab-change', tab: string): void
  (e: 'action', action: TableAction, row: any): void
}>()

/* ── state ── */
const search = ref('')
const activeTab = ref(props.tabs[0]?.id ?? '')
const sortKey = ref<{ col: number; dir: 'asc' | 'desc' } | null>(null)
const hiddenCols = ref<Set<number>>(new Set())
const filterOpen = ref(false)
const colMenuOpen = ref(false)
const actionMenuRow = ref<number | null>(null)
const page = ref(1)
const pageSize = ref(props.defaultPageSize)

watch(
  () => props.tabs,
  (t) => {
    if (!activeTab.value && t.length) activeTab.value = t[0].id
  }
)

/* ── filtered + sorted + paged rows ── */
const visibleColumns = computed(() =>
  props.columns.map((c, i) => ({ col: c, i })).filter(({ i }) => !hiddenCols.value.has(i))
)

const cellText = (row: any, col: TableColumn<any>): string => {
  const v = col.render ? col.render(row) : String(row[col.key] ?? '')
  return v
}

const cellHtml = (row: any, col: TableColumn<any>): string =>
  col.renderHtml ? col.renderHtml(row) : cellText(row, col)

const filteredRows = computed(() => {
  let rows = props.rows
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    rows = rows.filter((r) =>
      props.columns.some((c) => cellText(r, c).toLowerCase().includes(q))
    )
  }
  if (sortKey.value) {
    const { col, dir } = sortKey.value
    const c = props.columns[col]
    const nums = rows.map((r) => cellText(r, c).replace(/[^0-9.]/g, '')).filter((v) => v)
    const isNum = nums.length > 0 && nums.every((v) => !Number.isNaN(parseFloat(v)))
    rows = [...rows].sort((a, b) => {
      const va = cellText(a, c)
      const vb = cellText(b, c)
      let cmp: number
      if (isNum) {
        cmp = (parseFloat(va.replace(/[^0-9.]/g, '')) || 0) - (parseFloat(vb.replace(/[^0-9.]/g, '')) || 0)
      } else {
        cmp = va < vb ? -1 : va > vb ? 1 : 0
      }
      return dir === 'asc' ? cmp : -cmp
    })
  }
  return rows
})

const totalRows = computed(() => filteredRows.value.length)
const pageCount = computed(() => Math.max(1, Math.ceil(totalRows.value / pageSize.value)))
const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})
const pageInfo = computed(() => {
  if (totalRows.value === 0) return '0 rows'
  const start = (page.value - 1) * pageSize.value + 1
  const end = Math.min(page.value * pageSize.value, totalRows.value)
  return `${start}–${end} of ${totalRows.value}`
})

watch([search, activeTab], () => (page.value = 1))
watch(pageCount, (pc) => {
  if (page.value > pc) page.value = pc
})

/* ── sort / columns ── */
function onHeaderClick(i: number, sortable?: boolean) {
  if (!sortable) return
  if (sortKey.value?.col === i) {
    sortKey.value = { col: i, dir: sortKey.value.dir === 'asc' ? 'desc' : 'asc' }
  } else {
    sortKey.value = { col: i, dir: 'asc' }
  }
}

function toggleColumn(i: number, show: boolean) {
  const s = new Set(hiddenCols.value)
  if (show) s.delete(i)
  else s.add(i)
  hiddenCols.value = s
}

/* ── export / print ── */
function exportCsv() {
  const rows = [props.columns.map((c) => c.label)]
  filteredRows.value.forEach((r) => {
    rows.push(props.columns.map((c) => cellText(r, c)))
  })
  const csv = rows.map((r) => r.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `rem-erp-${props.tabs[0]?.id ?? 'table'}-${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(a.href)
}

function printTable() {
  const clone = document.createElement('table')
  clone.innerHTML = `<thead><tr>${visibleColumns.value.map(({ col }) => `<th>${col.label}</th>`).join('')}</tr></thead>
    <tbody>${pagedRows.value
      .map(
        (r) =>
          `<tr>${visibleColumns.value.map(({ col }) => `<td>${cellText(r, col)}</td>`).join('')}</tr>`
      )
      .join('')}</tbody>`
  const w = window.open('', '_blank')
  if (!w) return
  w.document.write(`<html><head><title>REM ERP Report</title><style>
    body{font-family:Inter,Arial,sans-serif;padding:20px}
    table{width:100%;border-collapse:collapse;font-size:11px}
    th{background:#f8f9fa;text-align:left;padding:4px 8px;border-bottom:1px solid #e0e0e0;font-size:9px;text-transform:uppercase}
    td{padding:5px 8px;border-bottom:1px solid #f0f0f0}
    h2{font-size:16px;margin-bottom:10px;color:#333}
  </style></head><body><h2>${document.querySelector('.page-title')?.textContent ?? 'Report'}</h2>${clone.outerHTML}
  <p style="margin-top:10px;font-size:9px;color:#999">Generated by REM ERP</p></body></html>`)
  w.document.close()
  w.print()
}

/* ── row actions ── */
function rowAction(action: TableAction, row: Record<string, unknown>) {
  actionMenuRow.value = null
  // Views define actions with onClick (e.g. open a detail drawer) — the
  // menu must EXECUTE it, not just emit (the emit was never consumed).
  if (typeof action.onClick === 'function') action.onClick(row)
  emit('action', action, row)
}

defineExpose({ refresh: () => (page.value = 1) })
</script>

<template>
  <div class="card" style="margin-bottom: 12px">
    <!-- TABS -->
    <div v-if="tabs.length" style="display: flex; gap: 0; border-bottom: 1px solid #e8e8e8; padding: 0 8px; overflow-x: auto">
      <div
        v-for="t in tabs"
        :key="t.id"
        class="top-nav-item"
        :class="{ active: activeTab === t.id }"
        style="padding: 7px 12px"
        @click="activeTab = t.id; emit('tab-change', t.id)"
      >
        {{ t.label }}<span v-if="t.count !== undefined" style="margin-left: 4px; font-size: 9px; color: #888">({{ t.count }})</span>
      </div>
    </div>

    <!-- TOOLBAR -->
    <div class="tbl-toolbar" style="display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #e8e8e8; padding: 5px 10px; flex-wrap: wrap">
      <span class="tt-label" style="font-size: 10px; color: #888; font-weight: 600">{{ totalRows }} rows</span>
      <span style="flex: 1"></span>
      <button class="tt-btn" @click="filterOpen = !filterOpen">🔍 Filter</button>
      <button class="tt-btn" @click="exportCsv">📥 CSV</button>
      <button class="tt-btn" @click="printTable">🖨 Print</button>
      <button class="tt-btn" style="position: relative" @click="colMenuOpen = !colMenuOpen">👁 Columns</button>
    </div>

    <!-- FILTER PANEL -->
    <div v-if="filterOpen" class="filter-panel" style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-bottom: 1px solid #e8e8e8; flex-wrap: wrap">
      <span style="font-size: 10px; color: #888">Search:</span>
      <input
        v-model="search"
        class="form-input"
        :placeholder="searchPlaceholder"
        style="flex: 1; max-width: 220px"
      />
      <span style="font-size: 10px; color: #888">Sort:</span>
      <select
        class="form-input"
        style="max-width: 180px"
        :value="sortKey ? `${sortKey.col}_${sortKey.dir}` : ''"
        @change="
          (e) => {
            const v = (e.target as HTMLSelectElement).value
            if (v) {
              const [ci, dir] = v.split('_')
              sortKey = { col: parseInt(ci), dir: dir as 'asc' | 'desc' }
            } else sortKey = null
          }
        "
      >
        <option value="">Default</option>
        <option v-for="(c, i) in columns" :key="i" :value="`${i}_asc`">{{ c.label }} ↑</option>
        <option v-for="(c, i) in columns" :key="i" :value="`${i}_desc`">{{ c.label }} ↓</option>
      </select>
      <button class="fp-btn primary" style="padding: 3px 10px; font-size: 10px; border-radius: 4px; background: #2f80ed; color: #fff; border: none; cursor: pointer" @click="filterOpen = false">Apply</button>
      <button class="fp-btn secondary" style="padding: 3px 10px; font-size: 10px; border-radius: 4px; background: #fff; border: 1px solid #e0e0e0; cursor: pointer" @click="search = ''; sortKey = null">Clear</button>
    </div>

    <!-- COLUMN MENU -->
    <div v-if="colMenuOpen" style="position: absolute; z-index: 1000; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.12); padding: 8px; min-width: 160px; margin: 4px 0 0 60px">
      <div style="font-size: 10px; font-weight: 600; color: #555; margin-bottom: 4px">Toggle Columns</div>
      <label v-for="(c, i) in columns" :key="i" style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: #333; padding: 2px 0; cursor: pointer">
        <input type="checkbox" :checked="!hiddenCols.has(i)" @change="toggleColumn(i, ($event.target as HTMLInputElement).checked)" />
        {{ c.label }}
      </label>
    </div>

    <!-- TABLE -->
    <div class="table-wrap">
      <table class="rem-table">
        <colgroup>
          <col v-for="(c, i) in columns" :key="i" :class="{ hidden: hiddenCols.has(i) }" />
        </colgroup>
        <thead>
          <tr>
            <th
              v-for="(c, i) in columns"
              :key="i"
              :class="{ sortable: c.sortable !== false, hidden: hiddenCols.has(i) }"
              :style="c.width ? `width:${c.width}` : ''"
              @click="onHeaderClick(i, c.sortable !== false)"
            >
              {{ c.label }}
              <span v-if="c.sortable !== false" class="s-arrow" :class="sortKey?.col === i ? sortKey.dir : ''">
                {{ sortKey?.col === i ? (sortKey.dir === 'asc' ? '▲' : '▼') : '⇅' }}
              </span>
            </th>
            <th v-if="actions.length" style="width: 40px"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, ri) in pagedRows" :key="ri">
            <td v-for="(c, i) in visibleColumns" :key="i" :class="{ hidden: hiddenCols.has(c.i) }" v-html="cellHtml(r, c.col)"></td>
            <td v-if="actions.length" style="position: relative">
              <button class="rem-icon-btn" style="font-size: 13px" @click="actionMenuRow = actionMenuRow === ri ? null : ri">⋯</button>
              <div
                v-if="actionMenuRow === ri"
                style="position: absolute; right: 0; top: 100%; z-index: 1001; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.12); min-width: 150px; padding: 4px"
              >
                <div
                  v-for="a in actions"
                  :key="a.label"
                  style="display: flex; align-items: center; gap: 8px; padding: 6px 10px; font-size: 11px; color: #333; cursor: pointer; border-radius: 5px"
                  @mouseover="($event.currentTarget as HTMLElement).style.background = '#f0f4ff'"
                  @mouseout="($event.currentTarget as HTMLElement).style.background = ''"
                  @click="rowAction(a, r)"
                >
                  {{ a.icon ?? '·' }} {{ a.label }}
                </div>
              </div>
            </td>
          </tr>
          <tr v-if="pagedRows.length === 0">
            <td :colspan="columns.length + (actions.length ? 1 : 0)" style="text-align: center; color: #888; padding: 20px; font-size: 11px">
              No rows found
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PAGINATION + PAGE INFO -->
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; border-top: 1px solid #e8e8e8; font-size: 10px; color: #888">
      <div style="display: flex; align-items: center; gap: 6px">
        <span>Rows per page:</span>
        <select class="form-input" style="width: auto; padding: 2px 6px" :value="pageSize" @change="pageSize = parseInt(($event.target as HTMLSelectElement).value); page = 1">
          <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
        </select>
        <span>{{ pageInfo }}</span>
      </div>
      <div style="display: flex; align-items: center; gap: 4px">
        <button class="tt-btn" :disabled="page <= 1" @click="page--">‹</button>
        <span>{{ page }} / {{ pageCount }}</span>
        <button class="tt-btn" :disabled="page >= pageCount" @click="page++">›</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tt-btn {
  padding: 3px 10px;
  font-size: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #fff;
  color: #555;
  cursor: pointer;
  transition: all 0.15s;
}
.tt-btn:hover {
  background: #f5f5f5;
  border-color: #2f80ed;
  color: #2f80ed;
}
.tt-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.s-arrow {
  margin-left: 3px;
  font-size: 9px;
  color: #999;
}
.s-arrow.asc {
  color: #2f80ed;
}
.s-arrow.desc {
  color: #2f80ed;
}
th.sortable {
  cursor: pointer;
  user-select: none;
}
th.sortable:hover {
  color: #2f80ed;
}
</style>
