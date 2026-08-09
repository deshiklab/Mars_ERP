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

export interface PipelineResponse<T> {
  [key: string]: T[] | number | string | undefined
}

/** Generic wrapped bridge error. */
export interface ApiError {
  error?: string
  exception?: string
  exc_type?: string
}
