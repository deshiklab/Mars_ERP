<script setup lang="ts">
/**
 * InvoiceDetailDrawer — invoice panel: header, client/project/unit,
 * line items table (desc, qty, rate, total), totals, status badge.
 */
import { computed, ref, watch } from 'vue'
import type { Invoice } from '@/api/types'

const props = defineProps<{ invoice: Invoice | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()
const tab = ref('overview')
watch(() => props.invoice, () => (tab.value = 'overview'))

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function statusColor(s: string): string {
  const map: Record<string, string> = { Draft: '#888', Sent: '#e65100', Paid: '#2e7d32', Overdue: '#c62828' }
  return map[s] ?? '#555'
}

const items = computed<{ desc: string; qty: number; rate: number }[]>(() => {
  const inv = props.invoice as unknown as { items?: { desc: string; qty: number; rate: number }[] }
  return inv?.items ?? []
})
const subtotal = computed(() => items.value.reduce((s, i) => s + (i.qty || 1) * (i.rate || 0), 0))
</script>

<template>
  <div v-if="invoice" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 520px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <div class="drawer-header" style="flex-shrink: 0">
        <h3 style="display: flex; align-items: center; gap: 8px">
          📄 {{ invoice.id }}
          <span class="pill" :style="{ background: statusColor(invoice.status) + '22', color: statusColor(invoice.status) }">{{ invoice.status }}</span>
        </h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto">
        <!-- header stats -->
        <div class="stats-row" style="grid-template-columns: 1fr 1fr">
          <div class="stat-card"><div class="label">Client</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ invoice.client || '—' }}</div></div>
          <div class="stat-card"><div class="label">Project</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ invoice.project || '—' }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">Unit</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ invoice.unit || '—' }}</div></div>
          <div class="stat-card"><div class="label">📅 Issued</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ invoice.issuedDate || '—' }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">💰 Amount</div><div style="font-size: 15px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ bdt(Number(invoice.amount) || 0) }}</div></div>
          <div class="stat-card"><div class="label">📅 Due Date</div><div style="font-size: 12px; font-weight: 600; color: #c62828; margin-top: 2px">{{ invoice.dueDate || '—' }}</div></div>
        </div>

        <!-- line items -->
        <div style="margin-top: 12px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 6px">🧾 Line Items</h3>
          <div class="table-wrap">
            <table class="rem-table" style="font-size: 10px; width: 100%">
              <thead><tr><th>Description</th><th class="num">Qty</th><th class="num">Rate</th><th class="num">Total</th></tr></thead>
              <tbody>
                <tr v-for="(it, i) in items" :key="i">
                  <td style="font-size: 10px; color: #333">{{ it.desc }}</td>
                  <td class="num">{{ it.qty || 1 }}</td>
                  <td class="num">{{ bdt(it.rate) }}</td>
                  <td class="num" style="font-weight: 700; color: #2f80ed">{{ bdt((it.qty || 1) * (it.rate || 0)) }}</td>
                </tr>
                <tr v-if="items.length">
                  <td colspan="3" style="text-align: right; font-weight: 700; color: #555">Subtotal</td>
                  <td class="num" style="font-weight: 700; color: #2e7d32">{{ bdt(subtotal) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="!items.length" style="text-align: center; padding: 20px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No line items.</div>
        </div>

        <!-- desc -->
        <div v-if="invoice.desc" style="margin-top: 10px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 4px">📝 Notes</h3>
          <div class="stat-card" style="font-size: 11px; color: #555">{{ invoice.desc }}</div>
        </div>

        <!-- actions -->
        <div style="margin-top: 14px; display: flex; gap: 6px; flex-wrap: wrap">
          <button class="action-btn" style="color: #2f80ed" @click="emit('status', 'Sent')">📨 Mark Sent</button>
          <button class="action-btn" style="color: #2e7d32" @click="emit('status', 'Paid')">✅ Mark Paid</button>
          <button class="action-btn" style="color: #c62828" @click="emit('status', 'Overdue')">⚠ Mark Overdue</button>
        </div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
        <button class="drawer-btn" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
