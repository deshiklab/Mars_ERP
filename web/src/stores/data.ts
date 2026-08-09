/**
 * Data store — server snapshot (bootstrap) + CRM leads.
 */
import { defineStore } from 'pinia'
import { api, apiErrorText } from '@/api/client'
import type { Lead } from '@/api/types'

export interface DashboardStats {
  bookings: number
  leads: number
  employees: number
  dues: number
  serverTime: string
  pwaVersion: string
}

interface DataState {
  stats: DashboardStats | null
  leads: Lead[]
  leadsLoading: boolean
  error: string
}

export const useDataStore = defineStore('data', {
  state: (): DataState => ({
    stats: null,
    leads: [],
    leadsLoading: false,
    error: ''
  }),

  actions: {
    async loadDashboard(): Promise<void> {
      const r = await api.bootstrap()
      if (!r.ok || !r.data) {
        this.error = apiErrorText(r)
        return
      }
      const c = r.data.collections
      this.stats = {
        bookings: (c['bookings'] ?? []).length,
        leads: (c['leads'] ?? []).length,
        employees: (c['employees'] ?? []).length,
        dues: (c['dues'] ?? []).length,
        serverTime: r.data.meta.server_time,
        pwaVersion: r.data.meta.pwa_version
      }
    },

    async loadLeads(): Promise<void> {
      this.leadsLoading = true
      this.error = ''
      const r = await api.leadsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['leads']
        this.leads = Array.isArray(arr) ? (arr as Lead[]) : []
      } else {
        this.error = apiErrorText(r)
      }
      this.leadsLoading = false
    },

    async updateLeadStatus(id: string, status: string): Promise<boolean> {
      const r = await api.leadUpdateStatus(id, status)
      if (r.ok) {
        const lead = this.leads.find((l) => l.id === id)
        if (lead) lead.status = status
        return true
      }
      this.error = apiErrorText(r)
      return false
    }
  }
})
