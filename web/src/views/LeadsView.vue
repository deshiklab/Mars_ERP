<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import type { Lead } from '@/api/types'

const data = useDataStore()
const statusFilter = ref('')
const showAddDrawer = ref(false)
const newLead = ref({ name: '', email: '', phone: '', source: 'Website', priority: 'Medium' })

onMounted(() => {
  data.loadLeads()
})

const statusOptions = ['New Inquiry', 'Contacted', 'Site Visit', 'Negotiation', 'Booking', 'Lost']

const sources = ['Website', 'Facebook', 'Referral', 'Walk-in', 'Agent', 'Bikroy', 'NRB Direct', 'Cold Call']

/** Status pill colors — mirrors leadBadgeColor/status colors in the HTML PWA. */
function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    'New Inquiry': ['#e3f2fd', '#1565c0'],
    Contacted: ['#f0f4ff', '#2f80ed'],
    'Site Visit': ['#fff3e0', '#e65100'],
    Negotiation: ['#fff8e1', '#ff8f00'],
    Booking: ['#e8f5e9', '#2e7d32'],
    Lost: ['#ffebee', '#c62828']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

function priorityColor(p: string): string {
  return p === 'High' ? '#c62828' : p === 'Medium' ? '#e65100' : '#888'
}

const filtered = computed(() => {
  if (!statusFilter.value) return data.leads
  return data.leads.filter((l) => l.status === statusFilter.value)
})

async function setStatus(leadId: string, event: Event) {
  const status = (event.target as HTMLSelectElement).value
  await data.updateLeadStatus(leadId, status)
}

function openAddDrawer() {
  newLead.value = { name: '', email: '', phone: '', source: 'Website', priority: 'Medium' }
  showAddDrawer.value = true
}

/** Mirrors the HTML PWA askFields modal flow (server call stubbed to sync). */
async function saveLead() {
  if (!newLead.value.name.trim()) {
    data.error = 'Lead name is required'
    return
  }
  // TODO: wire to a server create-lead endpoint when available
  showAddDrawer.value = false
  data.error = ''
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">CRM & Leads</span>
      <span class="page-subtitle">{{ data.leads.length }} leads · server-synced</span>
      <div style="margin-left: auto; display: flex; gap: 6px">
        <select
          v-model="statusFilter"
          style="padding: 3px 8px; font-size: 10px; border: 1px solid #e0e0e0; border-radius: 6px; outline: none; color: #555; background: #fff"
        >
          <option value="">All statuses</option>
          <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
        </select>
        <button class="action-btn primary" @click="openAddDrawer">+ Add Lead</button>
      </div>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.leadsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading leads…</p>

    <!-- Table: mirrors the HTML PWA table-wrap/rem-table -->
    <div v-else class="card">
      <div class="table-wrap">
        <table class="rem-table">
          <thead>
            <tr>
              <th>Lead</th>
              <th>Source</th>
              <th>Priority</th>
              <th>Score</th>
              <th>Follow-up</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in filtered" :key="l.id">
              <td>
                <div style="font-weight: 500; color: #333">{{ l.name }}</div>
                <div style="font-size: 9px; color: #888">{{ l.email }} · {{ l.phone }}</div>
              </td>
              <td style="font-size: 10px; color: #555">
                <span
                  style="display: inline-flex; align-items: center; gap: 3px; padding: 1px 6px; border-radius: 8px; background: #f0f4ff; color: #2f80ed; font-weight: 600"
                >
                  {{ l.source }}
                </span>
              </td>
              <td style="font-weight: 600; font-size: 10px" :style="{ color: priorityColor(l.priority) }">
                {{ l.priority }}
              </td>
              <td>
                <span
                  style="display: inline-flex; align-items: center; gap: 2px; padding: 1px 5px; border-radius: 4px; font-size: 9px; font-weight: 600; background: #eef3ff; color: #2f80ed"
                >
                  {{ l.score ?? '—' }}
                </span>
              </td>
              <td style="font-size: 9px; font-weight: 500; color: #888">{{ l.follow_up ?? '—' }}</td>
              <td>
                <select
                  :value="l.status"
                  :style="{
                    padding: '1px 3px',
                    fontSize: '9px',
                    border: '1px solid #e0e0e0',
                    borderRadius: '3px',
                    cursor: 'pointer',
                    maxWidth: '100px',
                    background: statusStyle(l.status).bg,
                    color: statusStyle(l.status).fg,
                    fontWeight: 600,
                    outline: 'none'
                  }"
                  @change="setStatus(l.id, $event)"
                >
                  <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
                </select>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="6" style="text-align: center; color: #888; padding: 20px; font-size: 11px">
                No leads found
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add-lead drawer: mirrors the HTML PWA drawer modal -->
    <div v-if="showAddDrawer" class="drawer-overlay active">
      <div class="drawer-sheet">
        <div class="drawer-header">
          <h3>Add Lead</h3>
          <div class="drawer-close" @click="showAddDrawer = false">✕</div>
        </div>
        <div class="drawer-body">
          <div class="form-group">
            <label class="form-label">Full name *</label>
            <input v-model="newLead.name" class="form-input" placeholder="e.g. Rahman Khan" />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="newLead.email" type="email" class="form-input" placeholder="rahman@example.com" />
          </div>
          <div class="form-group">
            <label class="form-label">Phone</label>
            <input v-model="newLead.phone" class="form-input" placeholder="+880 1XXX-XXXXXX" />
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px">
            <div class="form-group">
              <label class="form-label">Source</label>
              <select v-model="newLead.source" class="form-input">
                <option v-for="s in sources" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Priority</label>
              <select v-model="newLead.priority" class="form-input">
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
        </div>
        <div class="drawer-footer">
          <button class="drawer-btn" @click="showAddDrawer = false">Cancel</button>
          <button class="drawer-btn primary" @click="saveLead">Save Lead</button>
        </div>
      </div>
    </div>
  </div>
</template>
