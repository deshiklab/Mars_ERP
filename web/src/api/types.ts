/**
 * REM ERP — API type definitions (mirror of the Frappe bridge responses).
 */

/** Stage-1 login challenge (2FA required). */
export interface LoginChallenge {
  two_factor_required: boolean
  tmp_id: string
  verification?: { method: string; setup?: boolean }
  user: string
}

/** Stage-2 login success. */
export interface LoginSuccess {
  token: string
  full_name: string
  user: string
  roles: string[]
  session_expiry: string // e.g. "08:00"
}

export type LoginResponse = LoginChallenge | LoginSuccess

export interface BootstrapMeta {
  pwa_version: string
  session_expiry: string
  server_time: string
  settings: Record<string, unknown> | null
}

export interface BootstrapResponse {
  collections: Record<string, unknown[]>
  meta: BootstrapMeta
}

/** A CRM lead as returned by leads_pipeline. */
export interface Lead {
  id: string
  name: string
  email: string
  phone: string
  source: string
  status: string
  priority: 'High' | 'Medium' | 'Low'
  score: number
  nextFollowUp: string
  nextFollowUpRaw: string
  lastContact: string
  owner?: string
  notes?: string
  type?: string
  territory?: string
  property?: string
  value?: string
  paymentStatus?: string
  facingDir?: string
  floorPref?: string
  flatType?: string
  sizeSqFt?: string
  paymentPlan?: string
  brokerId?: string | null
  installments?: { date: string; amount: string; status: string }[]
  documents?: { name: string; type: string }[]
  activities?: { type: string; user: string; date: string; text: string }[]
  notesList?: { text: string; by: string; when: string }[]
}

/** A booking installment. */
export interface Installment {
  no: number
  date: string
  amount: number
  status: string
}

/** A REM Booking. */
export interface Booking {
  id: string
  client: string
  date: string
  property: string
  unit: string
  price: string
  advance: string
  status: string
  type: string
  terms: string
  schedStart: string
  total_paid: number
  total_due: number
  installments: Installment[]
}

/** A due/collection record. */
export interface Due {
  id: string
  customer: string
  phone: string
  project: string
  unit: string
  totalPrice: number
  paid: number
  due: number
  dueDate: string
  daysOverdue: number
  status: string
  bucket: string
  lastFollowUp?: string
  promises?: {
    date: string
    amount: number
    kept?: boolean
  }[]
}

/** An employee record. */
export interface Employee {
  id: string
  name: string
  designation: string
  dept: string
  phone: string
  email: string
  joinDate: string
  salary: number
  status: string
  contract: {
    type: string
    start: string
    end: string
    noticePeriod: number
    salaryClause: string
  }
  insurance: {
    provider: string
    policyNo: string
    coverage: number
    expiry: string
  }
}

/** A construction project. */
export interface Project {
  id: string
  name: string
  type: string
  location: string
  status: string
  progress: number
  budget: string
  manager: string
  plots: number
  start: string
  end: string
  phase: string
  desc?: string
  la_ref?: string
  milestones?: unknown[]
}

export interface PipelineResponse<T> {
  [key: string]: T[] | number | string | undefined
}

/** Generic wrapped bridge error. */
export interface ApiError {
  error?: string
  exception?: string
  exc_type?: string
}

/** A stock inventory item. */
export interface StockItem {
  id: string
  site: string
  item: string
  category: string
  qty: number
  unit: string
  price: number
  value: number
  status: string
  reorder: number
}

/** A purchase order. */
export interface PurchaseOrder {
  id: string
  date: string
  vendor: string
  site: string
  items: string
  amount: number
  fmt: string
  dueDate: string
  status: string
  category: string
}

/** A sales invoice. */
export interface Invoice {
  id: string
  client: string
  project: string
  unit: string
  amount: number
  status: string
  dueDate: string
  issuedDate: string
  desc: string
  items: unknown[]
}

/** A payment record. */
export interface Payment {
  id: string
  invoiceId: string
  client: string
  amount: number
  date: string
  method: string
  reference: string
  status: string
  notes: string
}

/** A chart-of-accounts entry. */
export interface CoaAccount {
  code: string
  name: string
  type: string
  balance: string
}

/** A contractor. */
export interface Contractor {
  id: string
  name: string
  specialty: string
  phone: string
  status: string
  rating?: number
  contracts?: number
}

/** A land/plot proposal. */
export interface Flat {
  id: string
  project?: string
  unit?: string
  floor?: string
  type?: string
  location?: string
  area?: string
  price?: string
  status: string
}
export interface Plot {
  id: string
  plotNo?: string
  location?: string
  area?: string
  price?: string
  status: string
}

/** A financial approval. */
export interface Approval {
  id: string
  title: string
  type?: string
  dept?: string
  requestedBy?: string
  amount: number
  date?: string
  status: string
}

/** A support ticket. */
/** A task record (bootstrap collections.tasks). */
export interface Task {
  id: number | string
  title: string
  status: string
  priority?: string
  project?: string
  assignee?: string
  deadline?: string
}

export interface Ticket {
  id: string
  subject: string
  project?: string
  type?: string
  customer?: string
  priority?: string
  date?: string
  status: string
}

/** A handover record. */
export interface Handover {
  id: string
  customer: string
  project?: string
  unit?: string
  type?: string
  totalValue: number
  paidAmount: number
  status: string
}

/** A work order. */
export interface WorkOrder {
  id: string
  title?: string
  name?: string
  project?: string
  assignee?: string
  assignedTo?: string
  status: string
}

/** A labor/worker. */
export interface Labor {
  id: string
  name: string
  category?: string
  site?: string
  salary: number
  rating?: number
  status: string
}

/** Equipment. */
export interface Equipment {
  id: string
  name: string
  model?: string
  type?: string
  site?: string
  operator?: string
  hours?: number
  fuelCost: number
  status: string
}

/** A variation order. */
export interface VariationOrder {
  id: string
  title: string
  project?: string
  originator?: string
  impact?: string
  date?: string
  status: string
}

/** Leave request. */
export interface LeaveReq {
  id: string
  employeeName: string
  type?: string
  from?: string
  to?: string
  days: number
  reason?: string
  status: string
}

/** Attendance record. */
export interface Attendance {
  id: string
  employeeName: string
  date?: string
  inTime?: string
  outTime?: string
  shift?: string
  status: string
}

/** Party ledger entry. */
export interface LedgerParty {
  name: string
  type: string
  out: number
  dueDate?: string
}

/** BOQ line. */
export interface BoqLine {
  id: string
  item: string
  category?: string
  project?: string
  qty: number
  rate: number
  unit?: string
  status: string
}

/** Investment. */
export interface Investment {
  id: string
  investorName: string
  project?: string
  amount: number
  rate: number
  startDate?: string
  tenureMonths?: number
  status: string
}

/** Loan. */
export interface Loan {
  id: string
  lender: string
  type?: string
  principal: number
  outstanding: number
  emi?: number
  rate: number
  status: string
}

/** Fixed asset. */
export interface FixedAsset {
  id: string
  name: string
  code?: string
  category?: string
  cost: number
  location?: string
  purchaseDate?: string
  status: string
}

/** Goods receipt. */
export interface Receipt {
  id: string
  item: string
  qty: number
  unit?: string
  amount: number
  date?: string
  poRef?: string
  grn?: string
  status?: string
}
/** A broker. */
export interface Broker {
  id: string
  name: string
  phone?: string
  region?: string
  tier?: string
  leadsReferred: number
  dealsClosed: number
  commissionPct?: number
  commissionPaid?: number
  joined?: string
  status: string
}

/** A complaint. */
export interface Complaint {
  id: string
  client: string
  project?: string
  unit?: string
  type?: string
  desc?: string
  priority?: string
  filedDate?: string
  resolvedDate?: string
  sla?: string
  satisfaction?: string
  assigned?: string
  status: string
}
