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
  follow_up: string
  last_contact: string
  owner?: string
  notes?: string
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
  promises?: string
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
