/**
 * Data store — server snapshot + CRM + bookings + dues + HR + projects.
 */
import { defineStore } from 'pinia'
import { api, apiErrorText } from '@/api/client'
import type { Booking, CoaAccount, Contractor, Due, Employee, Invoice, Lead, Payment, Project, PurchaseOrder, StockItem } from '@/api/types'

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
  bookings: Booking[]
  bookingsLoading: boolean
  dues: Due[]
  duesLoading: boolean
  employees: Employee[]
  employeesLoading: boolean
  projects: Project[]
  projectsLoading: boolean
  inventory: StockItem[]
  inventoryLoading: boolean
  pos: PurchaseOrder[]
  posLoading: boolean
  invoices: Invoice[]
  invoicesLoading: boolean
  payments: Payment[]
  paymentsLoading: boolean
  coa: CoaAccount[]
  coaLoading: boolean
  contractors: Contractor[]
  contractorsLoading: boolean
  error: string
}

export const useDataStore = defineStore('data', {
  state: (): DataState => ({
    stats: null,
    leads: [],
    leadsLoading: false,
    bookings: [],
    bookingsLoading: false,
    dues: [],
    duesLoading: false,
    employees: [],
    employeesLoading: false,
    projects: [],
    projectsLoading: false,
    inventory: [],
    inventoryLoading: false,
    pos: [],
    posLoading: false,
    invoices: [],
    invoicesLoading: false,
    payments: [],
    paymentsLoading: false,
    coa: [],
    coaLoading: false,
    contractors: [],
    contractorsLoading: false,
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
    },

    async loadBookings(): Promise<void> {
      this.bookingsLoading = true
      this.error = ''
      const r = await api.bookingsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['bookings']
        this.bookings = Array.isArray(arr) ? (arr as Booking[]) : []
      } else {
        this.error = apiErrorText(r)
      }
      this.bookingsLoading = false
    },

    async updateBookingStatus(id: string, status: string): Promise<boolean> {
      const r = await api.bookingUpdateStatus(id, status)
      if (r.ok) {
        const b = this.bookings.find((x) => x.id === id)
        if (b) b.status = status
        return true
      }
      this.error = apiErrorText(r)
      return false
    },

    async loadDues(): Promise<void> {
      this.duesLoading = true
      this.error = ''
      const r = await api.duesPipeline()
      if (r.ok && r.data) {
        const arr = r.data['dues']
        this.dues = Array.isArray(arr) ? (arr as Due[]) : []
      } else {
        this.error = apiErrorText(r)
      }
      this.duesLoading = false
    },

    async updateDueStatus(id: string, status: string): Promise<boolean> {
      const r = await api.duesUpdate(id, status)
      if (r.ok) {
        const d = this.dues.find((x) => x.id === id)
        if (d) d.status = status
        return true
      }
      this.error = apiErrorText(r)
      return false
    },

    async loadEmployees(): Promise<void> {
      this.employeesLoading = true
      this.error = ''
      const r = await api.employeesPipeline()
      if (r.ok && r.data) {
        const arr = r.data['employees']
        this.employees = Array.isArray(arr) ? (arr as Employee[]) : []
      } else {
        this.error = apiErrorText(r)
      }
      this.employeesLoading = false
    },

    async loadProjects(): Promise<void> {
      this.projectsLoading = true
      this.error = ''
      const r = await api.projectsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['projects']
        this.projects = Array.isArray(arr) ? (arr as Project[]) : []
      } else {
        this.error = apiErrorText(r)
      }
      this.projectsLoading = false
    },

    async loadInventory(): Promise<void> {
      this.inventoryLoading = true
      const r = await api.inventoryPipeline()
      if (r.ok && r.data) {
        const arr = r.data['inventory']
        this.inventory = Array.isArray(arr) ? (arr as StockItem[]) : []
      } else this.error = apiErrorText(r)
      this.inventoryLoading = false
    },

    async loadPos(): Promise<void> {
      this.posLoading = true
      const r = await api.poPipeline()
      if (r.ok && r.data) {
        const arr = r.data['pos']
        this.pos = Array.isArray(arr) ? (arr as PurchaseOrder[]) : []
      } else this.error = apiErrorText(r)
      this.posLoading = false
    },

    async loadFinance(): Promise<void> {
      this.coaLoading = true
      const r = await api.financePipeline()
      if (r.ok && r.data) {
        const arr = r.data['coa']
        this.coa = Array.isArray(arr) ? (arr as CoaAccount[]) : []
      } else this.error = apiErrorText(r)
      this.coaLoading = false
    },

    async loadInvoices(): Promise<void> {
      this.invoicesLoading = true
      const r = await api.invoicesPipeline()
      if (r.ok && r.data) {
        const arr = r.data['invoices']
        this.invoices = Array.isArray(arr) ? (arr as Invoice[]) : []
      } else this.error = apiErrorText(r)
      this.invoicesLoading = false
    },

    async loadPayments(): Promise<void> {
      this.paymentsLoading = true
      const r = await api.paymentsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['payments']
        this.payments = Array.isArray(arr) ? (arr as Payment[]) : []
      } else this.error = apiErrorText(r)
      this.paymentsLoading = false
    },

    async loadContractors(): Promise<void> {
      this.contractorsLoading = true
      const r = await api.contractorsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['contractors']
        this.contractors = Array.isArray(arr) ? (arr as Contractor[]) : []
      } else this.error = apiErrorText(r)
      this.contractorsLoading = false
    }
  }
})
