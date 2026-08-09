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

export interface PipelineResponse<T> {
  [key: string]: T[] | number | string | undefined
}

/** Generic wrapped bridge error. */
export interface ApiError {
  error?: string
  exception?: string
  exc_type?: string
}
