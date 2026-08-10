<script setup lang="ts">
/**
 * GenericDetailDrawer — universal record detail panel.
 * Renders any record's fields as a key-value stats grid (skips
 * id/empty/array fields), with a title + optional subtitle.
 * Used by views without a dedicated drawer so every table row has
 * a working View Details action.
 */
import { computed, ref, watch } from 'vue'

const props = defineProps<{
  record: Record<string, unknown> | null
  title: string
  titleField?: string
}>()
const emit = defineEmits<{ (e: 'close'): void }>()
const tab = ref('overview')
watch(() => props.record, () => (tab.value = 'overview'))

const SKIP = new Set(['id', 'Id', 'ID', 'avatar', 'created_at', 'updated_at', 'notesList', 'activities', 'documents', 'installments', 'promises', 'milestones', 'items', 'lines', 'units', 'collections'])

const MONEY_RE = /price|amount|paid|due|budget|salary|value|cost|commission|fee|balance|net|gross|total|rate|invest|advance/i

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

const fields = computed(() => {
  const rec = props.record
  if (!rec) return []
  return Object.entries(rec)
    .filter(([k, v]) => !SKIP.has(k) && fmt(v) !== '—' && typeof v !== 'object')
    .map(([k, v]) => ({
      label: k.replace(/([A-Z])/g, ' $1').replace(/^./, (c) => c.toUpperCase()),
      value: MONEY_RE.test(k) && typeof v === 'number' ? fmtMoney(String(v)) : fmt(v)
    }))
    .slice(0, 24)
})

const title = computed(() => {
  if (props.titleField && props.record) return String((props.record as Record<string, unknown>)[props.titleField] ?? '') || props.title
  return props.title
})

function valueColor(label: string, value: string): string {
  const l = label.toLowerCase()
  const isMoney = /price|amount|paid|due|budget|salary|value|cost|commission|fee|balance|net|gross|total|rate/.test(l)
  if (isMoney && /^-?\d/.test(value.replace(/[৳,\s]/g, ''))) {
    const num = parseFloat(value.replace(/[৳,\s]/g, ''))
    if (/due|overdue|pending|payable/.test(l)) return '#c62828'
    if (/paid|received|cleared/.test(l)) return '#2e7d32'
    return '#2f80ed'
  }
  const lv = l + value.toLowerCase()
  if (/active|confirmed|paid|done|completed|approved|cleared|available|resolved|published|success/.test(lv)) return '#2e7d32'
  if (/overdue|cancel|lost|failed|rejected|critical|absent|suspended|expired/.test(lv)) return '#c62828'
  if (/pending|draft|sent|review|hold|reserved|planned|upcoming|due|in progress/.test(lv)) return '#e65100'
  if (/status/.test(l)) return '#2f80ed'
  return '#333'
}
</script>

<template>
  <div v-if="record" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 500px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <div class="drawer-header" style="flex-shrink: 0">
        <h3>📋 {{ title }}</h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto">
        <div class="stats-row" style="grid-template-columns: 1fr 1fr">
          <div v-for="f in fields" :key="f.label" class="stat-card" style="min-width: 0">
            <div class="label" style="font-size: 9px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ f.label }}</div>
            <div style="font-size: 11px; font-weight: 600; margin-top: 2px; word-break: break-word" :style="{ color: valueColor(f.label, f.value) }">{{ f.value }}</div>
          </div>
        </div>
        <div v-if="!fields.length" style="text-align: center; padding: 32px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No details available.</div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
        <button class="drawer-btn" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
