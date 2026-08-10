<script setup lang="ts">
/**
 * DueDetailDrawer — mirrors the HTML PWA openDuesDetail:
 * stats-row (customer/phone/project/unit/total/paid/due/due date/
 * overdue) + Payment Promises table (date, amount, Kept/Broken/
 * Awaiting) + status actions.
 */
import { ref, watch } from 'vue'
import { useDataStore } from '@/stores/data'
import { showToast } from '@/toast'
import type { Due } from '@/api/types'

const data = useDataStore()
const props = defineProps<{ due: Due | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void; (e: 'updated'): void }>()
const fuNotes = ref('')
const prDate = ref('')
const prAmount = ref('')
const busy = ref(false)

async function logFollowUp() {
  if (!props.due || !fuNotes.value.trim()) {
    showToast('Enter follow-up notes first', 'error')
    return
  }
  busy.value = true
  const ok = await data.recordDueUpdate(props.due.id, {
    lastFollowUp: new Date().toISOString().slice(0, 10),
    notes: fuNotes.value.trim(),
  })
  busy.value = false
  if (ok) {
    showToast('Follow-up logged on the server', 'success')
    fuNotes.value = ''
    emit('updated')
  } else showToast('Could not save follow-up', 'error')
}

async function setPromise() {
  if (!props.due || !prDate.value || !prAmount.value) {
    showToast('Enter a promise date and amount', 'error')
    return
  }
  busy.value = true
  const ok = await data.recordDueUpdate(props.due.id, {
    promiseDate: prDate.value,
    promiseAmount: Number(prAmount.value),
  })
  busy.value = false
  if (ok) {
    showToast('Payment promise set on the server', 'success')
    prDate.value = ''
    prAmount.value = ''
    emit('updated')
  } else showToast('Could not save promise', 'error')
}
const tab = ref('overview')
watch(() => props.due, () => (tab.value = 'overview'))

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function promiseColor(kept: boolean | undefined): string {
  return kept === true ? '#2e7d32' : kept === false ? '#c62828' : '#e65100'
}
function promiseLabel(kept: boolean | undefined): string {
  return kept === true ? '✓ Kept' : kept === false ? '✕ Broken' : 'Awaiting'
}
function bucketColor(b: string): string {
  const map: Record<string, string> = {
    '0-30 Days': '#2e7d32', '31-60 Days': '#e65100', '60-90 Days': '#e65100', '90+ Days': '#c62828',
    '0-30': '#2e7d32', '31-60': '#e65100', '60+': '#c62828', Critical: '#c62828', Overdue: '#e65100', Current: '#2e7d32'
  }
  return map[b ?? ''] ?? '#555'
}
</script>

<template>
  <div v-if="due" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 540px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <div class="drawer-header" style="flex-shrink: 0">
        <h3 style="display: flex; align-items: center; gap: 8px">
          💰 Dues: {{ due.customer }}
          <span class="pill" :style="{ background: bucketColor(due.bucket) + '22', color: bucketColor(due.bucket) }">{{ due.bucket || due.status }}</span>
        </h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto">
        <!-- stats row -->
        <div class="stats-row" style="grid-template-columns: repeat(auto-fill, minmax(130px, 1fr))">
          <div class="stat-card"><div class="label">Customer</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ due.customer }}</div></div>
          <div class="stat-card"><div class="label">Phone</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ due.phone || '—' }}</div></div>
          <div class="stat-card"><div class="label">Project</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ due.project }}</div></div>
          <div class="stat-card"><div class="label">Unit</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ due.unit || '—' }}</div></div>
          <div class="stat-card"><div class="label">Total Price</div><div style="font-size: 13px; font-weight: 700; color: #333; margin-top: 2px">{{ bdt(due.totalPrice) }}</div></div>
          <div class="stat-card"><div class="label">Paid</div><div style="font-size: 13px; font-weight: 700; color: #2e7d32; margin-top: 2px">{{ bdt(due.paid) }}</div></div>
          <div class="stat-card"><div class="label">Due</div><div style="font-size: 13px; font-weight: 700; color: #c62828; margin-top: 2px">{{ bdt(due.due) }}</div></div>
          <div class="stat-card"><div class="label">Due Date</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ due.dueDate || '—' }}</div></div>
          <div class="stat-card"><div class="label">Overdue</div><div style="font-size: 12px; font-weight: 700; color: #c62828; margin-top: 2px">{{ due.daysOverdue }} days</div></div>
          <div class="stat-card"><div class="label">Last Follow-up</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ due.lastFollowUp || '—' }}</div></div>
        </div>

        <!-- payment promises -->
        <div style="margin-top: 12px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 6px">Payment Promises</h3>
          <div v-if="due.promises?.length" class="table-wrap">
            <table class="rem-table" style="font-size: 10px; width: 100%">
              <thead><tr><th>Date</th><th class="num">Amount</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-for="(p, i) in due.promises" :key="i">
                  <td>{{ p.date }}</td>
                  <td class="num">৳ {{ p.amount.toLocaleString('en-IN') }}</td>
                  <td><span :style="{ color: promiseColor(p.kept) }">{{ promiseLabel(p.kept) }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else style="text-align: center; padding: 24px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No payment promises.</div>
        </div>

        <!-- follow-up / promise form -->
        <div style="margin-top: 12px; background: #f8fafc; border: 1px solid #e5edf5; border-radius: 8px; padding: 10px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 6px">📌 Follow-up / Promise</h3>
          <input v-model="fuNotes" placeholder="Follow-up notes…" style="width: 100%; box-sizing: border-box; padding: 7px 9px; font-size: 10px; border: 1px solid #d9e2ec; border-radius: 6px; margin-bottom: 6px; background: #fff" />
          <button class="action-btn" style="color: #1565c0" :disabled="busy" @click="logFollowUp">💬 Log Follow-up</button>
          <div style="display: flex; gap: 6px; margin-top: 8px">
            <input v-model="prDate" type="date" style="flex: 1; padding: 6px 8px; font-size: 10px; border: 1px solid #d9e2ec; border-radius: 6px; background: #fff" />
            <input v-model="prAmount" type="number" placeholder="৳ amount" style="flex: 1; padding: 6px 8px; font-size: 10px; border: 1px solid #d9e2ec; border-radius: 6px; background: #fff" />
          </div>
          <button class="action-btn" style="color: #e65100; margin-top: 6px" :disabled="busy" @click="setPromise">📅 Set Payment Promise</button>
        </div>

        <!-- status actions -->
        <div style="margin-top: 14px; display: flex; gap: 6px; flex-wrap: wrap">
          <button class="action-btn" @click="emit('status', 'Current')">🟢 Mark Current</button>
          <button class="action-btn" style="color: #e65100" @click="emit('status', 'Overdue')">🟠 Mark Overdue</button>
          <button class="action-btn" style="color: #c62828" @click="emit('status', 'Critical')">🔴 Mark Critical</button>
          <button class="action-btn" style="color: #2e7d32" @click="emit('status', 'Paid')">✅ Mark Paid</button>
        </div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
        <button class="drawer-btn" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
