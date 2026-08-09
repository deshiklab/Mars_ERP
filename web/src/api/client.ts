/**
 * REM ERP — typed API client for the Frappe bridge.
 *
 * Auth model (mirrors the vanilla PWA): the token is a Frappe sid passed as a
 * query param (?sid=...), credentials 'omit' — CSRF-immune by design.
 * The API base is RELATIVE (/api/method/mars_constech.mars_constech.api):
 * same-origin when served by Frappe, proxied by Vite in dev.
 */
import type {
  ApiError,
  Booking,
  BootstrapResponse,
  Due,
  Employee,
  Lead,
  LoginResponse,
  PipelineResponse,
  Project
} from './types'

const BASE = '/api/method/mars_constech.mars_constech.api'

export interface ApiResult<T = unknown> {
  status: number
  ok: boolean
  data: T | null
  ms?: number
}

class ApiClient {
  token: string
  url: string
  private onUnauthorized: (() => void) | null = null

  constructor() {
    this.token = localStorage.getItem('rem_api_token') ?? ''
    this.url = localStorage.getItem('rem_api_url') ?? BASE
  }

  setOnUnauthorized(fn: () => void): void {
    this.onUnauthorized = fn
  }

  private base(): string {
    return this.url.replace(/\/+$/, '')
  }

  private async request<T>(
    endpoint: string,
    opts: { method?: string; body?: Record<string, unknown>; query?: string; timeout?: number } = {}
  ): Promise<ApiResult<T>> {
    const { method = 'GET', body, query = '', timeout = 20000 } = opts
    const path = `.${endpoint}${query ? (query.startsWith('?') ? query : `?${query}`) : ''}`
    // sid-param auth (login/index/signup are guest — the bridge whitelists them)
    const guest = ['login', 'signup', 'index'].includes(endpoint)
    const full = this.base() + path + (this.token && !guest ? `${path.includes('?') ? '&' : '?'}sid=${encodeURIComponent(this.token)}` : '')

    const controller = typeof AbortController !== 'undefined' ? new AbortController() : null
    const timer = controller ? setTimeout(() => controller.abort(), timeout) : null
    try {
      const res = await fetch(full, {
        method,
        headers: method !== 'GET' && method !== 'DELETE' ? { 'Content-Type': 'application/json' } : {},
        credentials: 'omit',
        signal: controller ? controller.signal : undefined,
        body: body !== undefined ? JSON.stringify(body) : undefined
      })
      if (timer) clearTimeout(timer)
      if (res.status === 401) {
        this.token = ''
        localStorage.removeItem('rem_api_token')
        if (this.onUnauthorized) this.onUnauthorized()
      }
      const data = await res.json().catch(() => ({}))
      const unwrapped = (data && typeof data.message !== 'undefined' ? data.message : data) as T
      return { status: res.status, ok: res.status >= 200 && res.status < 300, data: unwrapped }
    } catch (err) {
      if (timer) clearTimeout(timer)
      const msg = err instanceof Error ? err.message : 'network error'
      return { status: 0, ok: false, data: { error: msg } as unknown as T }
    }
  }

  /** Two-step 2FA login. Stage 1 returns a challenge; call verifyOtp next. */
  async login(email: string, password: string, timeout = 10000): Promise<ApiResult<LoginResponse>> {
    return this.request<LoginResponse>('login', { method: 'POST', body: { email, password }, timeout })
  }

  /** Stage 2 — confirm the OTP from the authenticator app. */
  async verifyOtp(
    email: string,
    password: string,
    otp: string,
    tmpId: string,
    timeout = 10000
  ): Promise<ApiResult<LoginResponse>> {
    return this.request<LoginResponse>('login', {
      method: 'POST',
      body: { email, password, otp, tmp_id: tmpId },
      timeout
    })
  }

  async logout(): Promise<void> {
    if (this.token) await this.request('logout')
    this.token = ''
    localStorage.removeItem('rem_api_token')
  }

  async bootstrap(): Promise<ApiResult<BootstrapResponse>> {
    return this.request<BootstrapResponse>('bootstrap')
  }

  async leadsPipeline(): Promise<ApiResult<PipelineResponse<Lead>>> {
    return this.request<PipelineResponse<Lead>>('leads_pipeline')
  }

  async leadUpdateStatus(id: string, status: string): Promise<ApiResult<{ ok: boolean }>> {
    return this.request<{ ok: boolean }>('lead_update_status', { method: 'POST', body: { id, status } })
  }

  async bookingsPipeline(): Promise<ApiResult<PipelineResponse<Booking>>> {
    return this.request<PipelineResponse<Booking>>('bookings_pipeline')
  }

  async bookingUpdateStatus(id: string, status: string): Promise<ApiResult<{ ok: boolean }>> {
    return this.request<{ ok: boolean }>('booking_update_status', { method: 'POST', body: { id, status } })
  }

  async duesPipeline(): Promise<ApiResult<PipelineResponse<Due>>> {
    return this.request<PipelineResponse<Due>>('dues_pipeline')
  }

  async duesUpdate(id: string, status: string, paid?: number): Promise<ApiResult<{ ok: boolean }>> {
    const body: Record<string, unknown> = { id, status }
    if (paid !== undefined) body.paid = paid
    return this.request<{ ok: boolean }>('dues_update', { method: 'POST', body })
  }

  async employeesPipeline(): Promise<ApiResult<PipelineResponse<Employee>>> {
    return this.request<PipelineResponse<Employee>>('employees_pipeline')
  }

  async projectsPipeline(): Promise<ApiResult<PipelineResponse<Project>>> {
    return this.request<PipelineResponse<Project>>('projects_pipeline')
  }

  async sync(collection: string): Promise<ApiResult<{ rows: number }>> {
    return this.request<{ rows: number }>('sync', { method: 'POST', body: { [collection]: [] } })
  }
}

/** Singleton — mirrors how the PWA uses a single API object. */
export const api = new ApiClient()

/** Error text helper for UI display. */
export function apiErrorText(result: ApiResult): string {
  const d = (result.data ?? {}) as ApiError
  return d.error ?? d.exception ?? `Request failed (${result.status === 0 ? 'network' : result.status})`
}
