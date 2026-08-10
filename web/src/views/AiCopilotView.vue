<script setup lang="ts">
/**
 * AiCopilotView — the Communication & AI group's AI Copilot module.
 * Lightweight assistant chat that answers with real data summaries.
 */
import { computed, ref } from 'vue'
import { useDataStore } from '@/stores/data'

const data = useDataStore()
const messages = ref<{ role: 'user' | 'ai'; text: string }[]>([
  { role: 'ai', text: 'Hello! I am MARS AI Copilot. Ask me about your leads, bookings, dues, or stock — I can summarize from live data.' }
])
const draft = ref('')
const thinking = ref(false)

const stats = computed(() => data.stats)

function answer(q: string): string {
  const lq = q.toLowerCase()
  const s = stats.value
  if (lq.includes('lead') || lq.includes('crm')) return `You have ${data.leads.length} leads total. ${data.leads.filter((l) => l.status === 'New Inquiry').length} are New Inquiry, ${data.leads.filter((l) => l.status === 'Site Visit').length} at Site Visit, ${data.leads.filter((l) => l.status === 'Booking').length} at Booking.`
  if (lq.includes('booking')) return `There are ${data.bookings.length} bookings: ${data.bookings.filter((b) => b.status === 'Confirmed').length} confirmed, ${data.bookings.filter((b) => b.status === 'Pending Review').length} pending review.`
  if (lq.includes('due') || lq.includes('collection')) return `${data.dues.length} accounts have outstanding dues. ${data.dues.filter((d) => d.daysOverdue >= 60).length} are 60+ days overdue.`
  if (lq.includes('employee') || lq.includes('hr')) return `The company has ${data.employees.length} employees on record, ${data.employees.filter((e) => e.status === 'Active').length} active.`
  if (lq.includes('stock') || lq.includes('inventory')) return `Inventory has ${data.inventory.length} items with ${data.inventory.filter((i) => i.status !== 'Adequate').length} needing attention (low/out of stock).`
  if (lq.includes('project')) return `${data.projects.length} projects are tracked: ${data.projects.filter((p) => p.status === 'Active').length} active, ${data.projects.filter((p) => p.status === 'Planning').length} in planning.`
  if (lq.includes('finance') || lq.includes('invoice')) return `Finance shows ${data.invoices.length} invoices and ${data.payments.length} payments.`
  if (lq.includes('hello') || lq.includes('hi') || lq.includes('salam')) return 'Hello! Ask me about leads, bookings, dues, employees, stock, projects or finance.'
  return `I can summarize from live data: leads (${data.leads.length}), bookings (${data.bookings.length}), dues (${data.dues.length}), employees (${data.employees.length}), projects (${data.projects.length}), inventory (${data.inventory.length}). Try "how many leads?" or "dues status".`
}

function send() {
  const text = draft.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', text })
  draft.value = ''
  thinking.value = true
  setTimeout(() => {
    messages.value.push({ role: 'ai', text: answer(text) })
    thinking.value = false
  }, 500)
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">AI Copilot</span>
      <span class="page-subtitle">Ask questions — answers from live server data</span>
    </div>

    <div class="card" style="display: flex; flex-direction: column; height: 540px; padding: 0; overflow: hidden">
      <div style="padding: 10px 14px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 8px">
        <span style="width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #7b1fa2, #2f80ed); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px">🤖</span>
        <div>
          <div style="font-size: 12px; font-weight: 700; color: #333">MARS AI Copilot</div>
          <div style="font-size: 9px; color: #2e7d32">● Online — {{ data.leads.length }} leads · {{ data.bookings.length }} bookings loaded</div>
        </div>
      </div>

      <div style="flex: 1; overflow-y: auto; padding: 12px 14px; display: flex; flex-direction: column; gap: 8px">
        <div
          v-for="(m, i) in messages"
          :key="i"
          style="max-width: 80%; padding: 8px 12px; border-radius: 12px; font-size: 11px; line-height: 1.5; white-space: pre-wrap"
          :style="m.role === 'user' ? 'align-self:flex-end;background:#2f80ed;color:#fff;border-bottom-right-radius:2px' : 'align-self:flex-start;background:#f0f4ff;color:#333;border-bottom-left-radius:2px'"
        >{{ m.text }}</div>
        <div v-if="thinking" style="align-self: flex-start; background: #f0f4ff; color: #888; padding: 8px 12px; border-radius: 12px; font-size: 11px">Thinking…</div>
      </div>

      <div style="display: flex; gap: 8px; padding: 10px 14px; border-top: 1px solid #f0f0f0">
        <input v-model="draft" placeholder="Ask about leads, dues, bookings…" style="flex: 1; border: 1px solid #e0e0e0; border-radius: 18px; padding: 7px 14px; font-size: 11px; outline: none" @keydown.enter="send" />
        <button class="action-btn primary" @click="send">➤ Send</button>
      </div>
    </div>
  </div>
</template>
