<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'

const data = useDataStore()
const statusFilter = ref('')

onMounted(() => {
  data.loadLeads()
})

const statusOptions = ['New Inquiry', 'Site Visit', 'Negotiation', 'Booking', 'Lost']

function statusColor(status: string): string {
  const map: Record<string, string> = {
    'New Inquiry': 'bg-sky-500/15 text-sky-300',
    'Site Visit': 'bg-amber-500/15 text-amber-300',
    Negotiation: 'bg-orange-500/15 text-orange-300',
    Booking: 'bg-emerald-500/15 text-emerald-300',
    Lost: 'bg-rose-500/15 text-rose-300'
  }
  return map[status] ?? 'bg-slate-500/15 text-slate-300'
}

function priorityColor(p: string): string {
  return p === 'High' ? 'text-rose-400' : p === 'Medium' ? 'text-amber-400' : 'text-slate-400'
}

function filtered() {
  if (!statusFilter.value) return data.leads
  return data.leads.filter((l) => l.status === statusFilter.value)
}

async function setStatus(leadId: string, event: Event) {
  const status = (event.target as HTMLSelectElement).value
  await data.updateLeadStatus(leadId, status)
}
</script>

<template>
  <section>
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold">CRM & Leads</h2>
        <p class="mt-1 text-xs text-slate-400">{{ data.leads.length }} leads from the server</p>
      </div>
      <select
        v-model="statusFilter"
        class="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-slate-300 outline-none"
      >
        <option value="">All statuses</option>
        <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <p v-if="data.error" class="mt-2 text-xs text-rose-400">{{ data.error }}</p>
    <p v-if="data.leadsLoading" class="mt-6 text-sm text-slate-400">Loading leads…</p>

    <div v-else class="mt-6 overflow-x-auto rounded-xl border border-slate-800">
      <table class="w-full text-left text-sm">
        <thead class="border-b border-slate-800 bg-slate-900/80 text-xs uppercase tracking-wide text-slate-400">
          <tr>
            <th class="px-4 py-3">Lead</th>
            <th class="px-4 py-3">Source</th>
            <th class="px-4 py-3">Priority</th>
            <th class="px-4 py-3">Score</th>
            <th class="px-4 py-3">Follow-up</th>
            <th class="px-4 py-3">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/70">
          <tr v-for="l in filtered()" :key="l.id" class="hover:bg-slate-900/40">
            <td class="px-4 py-3">
              <p class="font-medium text-slate-200">{{ l.name }}</p>
              <p class="text-xs text-slate-500">{{ l.email }} · {{ l.phone }}</p>
            </td>
            <td class="px-4 py-3 text-slate-300">{{ l.source }}</td>
            <td class="px-4 py-3 font-semibold" :class="priorityColor(l.priority)">
              {{ l.priority }}
            </td>
            <td class="px-4 py-3 text-slate-300">{{ l.score ?? '—' }}</td>
            <td class="px-4 py-3 text-xs text-slate-400">{{ l.follow_up ?? '—' }}</td>
            <td class="px-4 py-3">
              <select
                :value="l.status"
                class="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1.5 text-xs outline-none"
                :class="statusColor(l.status)"
                @change="setStatus(l.id, $event)"
              >
                <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
              </select>
            </td>
          </tr>
          <tr v-if="filtered().length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-sm text-slate-500">
              No leads found
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
