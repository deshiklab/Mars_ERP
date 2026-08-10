<script setup lang="ts">
/**
 * GenericDetailDrawer — universal record detail panel (v2).
 * Renders any record's fields as a key-value stats grid, with:
 * - smart coloring (money blue, paid/active green, overdue/cancelled red…)
 * - money auto-format ৳ Cr/Lac
 * - copy value on click (toast feedback)
 * - prev/next record navigation when `records` is passed
 * - status pill in the header, copy-ID button
 * - Esc / overlay-click to close, sticky header + footer, scrollable body
 * - Print button
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { showToast } from '@/toast'

const props = withDefaults(
  defineProps<{
    record: Record<string, unknown> | null
    title: string
    records?: Record<string, unknown>[]
  }>(),
  { records: () => [] }
)
const emit = defineEmits<{ (e: 'close'): void }>()

const SKIP = new Set(['id', '_id', 'key', 'children', '$$hashKey'])
const MONEY_RE = /price|amount|paid|due|budget|salary|value|cost|commission|fee|balance|net|gross|total|rate|invest|advance|payment/i

/* ── record + navigation ── */
const curIdx = ref(0)
watch(
  () => props.record,
  (r) => {
    if (!r) return
    if (props.records.length) {
      const i = props.records.findIndex(
        (x) => x === r || (x as { id?: string }).id === (r as { id?: string }).id
      )
      curIdx.value = i >= 0 ? i : 0
    } else {
      curIdx.value = 0
    }
  },
  { immediate: true }
)
const display = computed(() => {
  if (props.records.length && curIdx.value >= 0) return props.records[curIdx.value]
  return props.record
})
function nav(dir: number) {
  if (!props.records.length) return
  curIdx.value = (curIdx.value + dir + props.records.length) % props.records.length
}

/* ── fields ── */
const fields = computed(() => {
  const rec = display.value
  if (!rec) return []
  const seen = new Set<string>()
  return Object.entries(rec)
    .filter(([k, v]) => {
      if (SKIP.has(k) || seen.has(k)) return false
      seen.add(k)
      if (v === null || v === undefined || v === '') return false
      if (Array.isArray(v)) return false
      if (typeof v === 'object') return false
      return true
    })
    .slice(0, 24)
    .map(([k, v]) => ({
      label: k.replace(/([A-Z])/g, ' $1').replace(/^./, (c) => c.toUpperCase()),
      value: v
    }))
})

const status = computed(() => String((display.value as { status?: unknown })?.status ?? '').toLowerCase())
const statusPill = computed(() => {
  if (!status.value) return ''
  const s = status.value
  if (/active|confirmed|paid|done|completed|cleared|approved|ok/.test(s)) return { text: s, color: '#2e7d32' }
  if (/overdue|cancel|lost|failed|critical|expired|rejected/.test(s)) return { text: s, color: '#c62828' }
  if (/pending|draft|sent|review|hold|in progress|in_progress|warning/.test(s)) return { text: s, color: '#e65100' }
  return { text: s, color: '#2f80ed' }
})

function fmtMoney(s: string): string {
  const n = parseFloat(s.replace(/[৳,$\s]/g, ''))
  if (isNaN(n)) return s
  return n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString('en-IN')}`
}
function fmt(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—'
  if (typeof v === 'object') return ''
  const s = String(v)
  if (s.length > 120) return s.slice(0, 120) + '…'
  return s
}
function valueColor(label: string, v: unknown): string {
  const s = String(v).toLowerCase()
  if (MONEY_RE.test(label)) {
    if (/due|payable|overdue/.test(label)) return '#c62828'
    if (/paid|received|cleared/.test(label)) return '#2e7d32'
    return '#2f80ed'
  }
  if (/active|confirmed|paid|done|completed|approved|cleared/.test(s)) return '#2e7d32'
  if (/overdue|cancel|lost|failed|critical|expired|rejected|low/.test(s)) return '#c62828'
  if (/pending|draft|sent|review|hold|warning/.test(s)) return '#e65100'
  return '#333'
}
function fieldValue(f: { label: string; value: unknown }): string {
  if (MONEY_RE.test(f.label) && typeof f.value === 'number') return fmtMoney(String(f.value))
  return fmt(f.value)
}
function recordId(): string {
  const rec = display.value as { id?: string; name?: string } | null
  return String(rec?.id ?? rec?.name ?? '')
}

/* ── copy ── */
async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    showToast(`Copied: ${text.slice(0, 42)}`, 'success')
  } catch {
    showToast('Copy failed — select the text manually', 'error')
  }
}

/* ── print ── */
function printDrawer() {
  window.print()
}

/* ── close on Esc ── */
function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div v-if="record" class="drawer-overlay active" @click.self="emit('close')">
    <div class="drawer-sheet" style="display: flex; flex-direction: column; width: 560px">
      <!-- header -->
      <div style="padding: 14px 16px; border-bottom: 1px solid #e8e8e8; display: flex; align-items: center; gap: 10px">
        <div style="font-size: 15px">📋</div>
        <div style="flex: 1; min-width: 0">
          <div style="font-size: 13px; font-weight: 700; color: #222; display: flex; align-items: center; gap: 8px">
            <span class="ellipsis">{{ title }}</span>
            <span
              v-if="statusPill"
              :style="{
                background: statusPill.color + '18',
                color: statusPill.color,
                border: '1px solid ' + statusPill.color,
                fontSize: '9px',
                fontWeight: 600,
                padding: '1px 7px',
                borderRadius: '9px'
              }"
            >{{ statusPill.text }}</span>
            <button
              title="Copy record ID"
              style="background: none; border: 1px solid #e0e0e0; border-radius: 5px; font-size: 10px; color: #2f80ed; padding: 1px 6px; cursor: pointer"
              @click="copyText(recordId())"
            >#{{ recordId() || 'copy' }}</button>
          </div>
          <div style="font-size: 10px; color: #999; margin-top: 2px">
            {{ fields.length }} fields
            <template v-if="records.length > 1"> · record {{ curIdx + 1 }} of {{ records.length }}</template>
          </div>
        </div>
        <button class="rem-icon-btn" title="Close (Esc)" style="font-size: 15px" @click="emit('close')">✕</button>
      </div>

      <!-- nav arrows -->
      <div v-if="records.length > 1" style="display: flex; gap: 6px; padding: 8px 16px; border-bottom: 1px solid #f0f0f0; background: #fafbff">
        <button class="rem-icon-btn" title="Previous record (←)" style="font-size: 12px" @click="nav(-1)">◀</button>
        <button class="rem-icon-btn" title="Next record (→)" style="font-size: 12px" @click="nav(1)">▶</button>
        <span style="font-size: 10px; color: #888; margin-left: 6px; align-self: center">{{ curIdx + 1 }} / {{ records.length }}</span>
      </div>

      <!-- body -->
      <div style="flex: 1; overflow-y: auto; padding: 14px 16px">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px">
          <div
            v-for="f in fields"
            :key="f.label"
            class="stat-card"
            style="cursor: pointer; user-select: none"
            :title="'Click to copy: ' + fieldValue(f)"
            @click="copyText(fieldValue(f))"
          >
            <div style="font-size: 9px; color: #888; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 3px">{{ f.label }}</div>
            <div :style="{ fontSize: '12px', fontWeight: 600, color: valueColor(f.label, f.value), wordBreak: 'break-word' }">
              {{ fieldValue(f) }}
            </div>
          </div>
        </div>
        <p style="font-size: 9px; color: #bbb; margin-top: 10px; text-align: center">Click any value to copy it</p>
      </div>

      <!-- footer -->
      <div style="padding: 10px 16px; border-top: 1px solid #e8e8e8; display: flex; gap: 8px; justify-content: flex-end">
        <button class="action-btn" style="font-size: 11px" @click="printDrawer">🖨 Print</button>
        <button class="action-btn primary" style="font-size: 11px" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
