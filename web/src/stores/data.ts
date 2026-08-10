/**
 * Data store — server snapshot + CRM + bookings + dues + HR + projects.
 */
import { defineStore } from 'pinia'
import { api, apiErrorText } from '@/api/client'
import type { Approval, Attendance, BoqLine, Booking, CoaAccount, Contractor, Due, Employee, Equipment, FixedAsset, Handover, Investment, Invoice, Labor, Lead, LeaveReq, LedgerParty, Loan, Payment, Plot, Project, PurchaseOrder, Receipt, StockItem, Ticket, VariationOrder, WorkOrder } from '@/api/types'

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
    plots: Plot[]
  plotsLoading: boolean
    approvals: Approval[]
  approvalsLoading: boolean
    tickets: Ticket[]
  ticketsLoading: boolean
    handover: Handover[]
  handoverLoading: boolean
    workOrders: WorkOrder[]
  workOrdersLoading: boolean
    labor: Labor[]
  laborLoading: boolean
    equipment: Equipment[]
  equipmentLoading: boolean
    variations: VariationOrder[]
  variationsLoading: boolean
    leave: LeaveReq[]
  leaveLoading: boolean
    attendance: Attendance[]
  attendanceLoading: boolean
    partyLedger: LedgerParty[]
  partyLedgerLoading: boolean
    boq: BoqLine[]
  boqLoading: boolean
    investments: Investment[]
  investmentsLoading: boolean
    loans: Loan[]
  loansLoading: boolean
    fixedAssets: FixedAsset[]
  fixedAssetsLoading: boolean
    receipts: Receipt[]
  receiptsLoading: boolean
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
    plots: [],
    approvals: [],
    tickets: [],
    handover: [],
    workOrders: [],
    labor: [],
    equipment: [],
    variations: [],
    leave: [],
    attendance: [],
    partyLedger: [],
    boq: [],
    investments: [],
    loans: [],
    fixedAssets: [],
    receipts: [],
    plotsLoading: false,
    approvalsLoading: false,
    ticketsLoading: false,
    handoverLoading: false,
    workOrdersLoading: false,
    laborLoading: false,
    equipmentLoading: false,
    variationsLoading: false,
    leaveLoading: false,
    attendanceLoading: false,
    partyLedgerLoading: false,
    boqLoading: false,
    investmentsLoading: false,
    loansLoading: false,
    fixedAssetsLoading: false,
    receiptsLoading: false,
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
    },

    async loadPlots(): Promise<void> {
      this.plotsLoading = true
      const r = await api.plotsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['plots']
        this.plots = Array.isArray(arr) ? (arr as Plot[]) : []
      } else this.error = apiErrorText(r)
      this.plotsLoading = false
    },
    async loadApprovals(): Promise<void> {
      this.approvalsLoading = true
      const r = await api.approvalsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['approvals']
        this.approvals = Array.isArray(arr) ? (arr as Approval[]) : []
      } else this.error = apiErrorText(r)
      this.approvalsLoading = false
    },
    async loadTickets(): Promise<void> {
      this.ticketsLoading = true
      const r = await api.ticketsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['tickets']
        this.tickets = Array.isArray(arr) ? (arr as Ticket[]) : []
      } else this.error = apiErrorText(r)
      this.ticketsLoading = false
    },
    async loadHandover(): Promise<void> {
      this.handoverLoading = true
      const r = await api.handoverPipeline()
      if (r.ok && r.data) {
        const arr = r.data['handover']
        this.handover = Array.isArray(arr) ? (arr as Handover[]) : []
      } else this.error = apiErrorText(r)
      this.handoverLoading = false
    },
    async loadWork(): Promise<void> {
      this.workOrdersLoading = true
      const r = await api.work_ordersPipeline()
      if (r.ok && r.data) {
        const arr = r.data['work']
        this.workOrders = Array.isArray(arr) ? (arr as WorkOrder[]) : []
      } else this.error = apiErrorText(r)
      this.workOrdersLoading = false
    },
    async loadLabor(): Promise<void> {
      this.laborLoading = true
      const r = await api.laborPipeline()
      if (r.ok && r.data) {
        const arr = r.data['labor']
        this.labor = Array.isArray(arr) ? (arr as Labor[]) : []
      } else this.error = apiErrorText(r)
      this.laborLoading = false
    },
    async loadEquipment(): Promise<void> {
      this.equipmentLoading = true
      const r = await api.equipmentPipeline()
      if (r.ok && r.data) {
        const arr = r.data['equipment']
        this.equipment = Array.isArray(arr) ? (arr as Equipment[]) : []
      } else this.error = apiErrorText(r)
      this.equipmentLoading = false
    },
    async loadVariation(): Promise<void> {
      this.variationsLoading = true
      const r = await api.variation_ordersPipeline()
      if (r.ok && r.data) {
        const arr = r.data['variation']
        this.variations = Array.isArray(arr) ? (arr as VariationOrder[]) : []
      } else this.error = apiErrorText(r)
      this.variationsLoading = false
    },
    async loadLeave(): Promise<void> {
      this.leaveLoading = true
      const r = await api.leavePipeline()
      if (r.ok && r.data) {
        const arr = r.data['leave']
        this.leave = Array.isArray(arr) ? (arr as LeaveReq[]) : []
      } else this.error = apiErrorText(r)
      this.leaveLoading = false
    },
    async loadAttendance(): Promise<void> {
      this.attendanceLoading = true
      const r = await api.attendancePipeline()
      if (r.ok && r.data) {
        const arr = r.data['attendance']
        this.attendance = Array.isArray(arr) ? (arr as Attendance[]) : []
      } else this.error = apiErrorText(r)
      this.attendanceLoading = false
    },
    async loadParty(): Promise<void> {
      this.partyLedgerLoading = true
      const r = await api.party_ledgerPipeline()
      if (r.ok && r.data) {
        const arr = r.data['party']
        this.partyLedger = Array.isArray(arr) ? (arr as LedgerParty[]) : []
      } else this.error = apiErrorText(r)
      this.partyLedgerLoading = false
    },
    async loadBoq(): Promise<void> {
      this.boqLoading = true
      const r = await api.boqPipeline()
      if (r.ok && r.data) {
        const arr = r.data['boq']
        this.boq = Array.isArray(arr) ? (arr as BoqLine[]) : []
      } else this.error = apiErrorText(r)
      this.boqLoading = false
    },
    async loadInvestments(): Promise<void> {
      this.investmentsLoading = true
      const r = await api.investmentsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['investments']
        this.investments = Array.isArray(arr) ? (arr as Investment[]) : []
      } else this.error = apiErrorText(r)
      this.investmentsLoading = false
    },
    async loadLoans(): Promise<void> {
      this.loansLoading = true
      const r = await api.loansPipeline()
      if (r.ok && r.data) {
        const arr = r.data['loans']
        this.loans = Array.isArray(arr) ? (arr as Loan[]) : []
      } else this.error = apiErrorText(r)
      this.loansLoading = false
    },
    async loadFixed(): Promise<void> {
      this.fixedAssetsLoading = true
      const r = await api.fixed_assetsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['fixed']
        this.fixedAssets = Array.isArray(arr) ? (arr as FixedAsset[]) : []
      } else this.error = apiErrorText(r)
      this.fixedAssetsLoading = false
    },
    async loadReceipts(): Promise<void> {
      this.receiptsLoading = true
      const r = await api.receiptsPipeline()
      if (r.ok && r.data) {
        const arr = r.data['receipts']
        this.receipts = Array.isArray(arr) ? (arr as Receipt[]) : []
      } else this.error = apiErrorText(r)
      this.receiptsLoading = false
    }
  }
})
