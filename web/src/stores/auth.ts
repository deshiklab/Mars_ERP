/**
 * Auth store — two-step 2FA login state machine + role mapping.
 */
import { defineStore } from 'pinia'
import { api, apiErrorText } from '@/api/client'
import type { LoginSuccess } from '@/api/types'

export type PwaRole = 'Super Admin' | 'Sales Agent' | 'Site Engineer' | 'Finance' | 'Customer'
export type AuthPhase = 'guest' | 'password' | 'otp' | 'authenticated'

/** ERPNext role -> PWA role (Super Admin = full access). */
export function pwaRoleFor(roles: string[]): PwaRole {
  if (roles.includes('Administrator') || roles.includes('MARS Manager')) return 'Super Admin'
  if (roles.includes('MARS Agent')) return 'Sales Agent'
  if (roles.includes('MARS Customer') || roles.includes('Customer')) return 'Customer'
  return 'Super Admin'
}

/** Modules each PWA role may access (mirrors the vanilla PWA's ROLE_MODULES). */
export const ROLE_MODULES: Record<PwaRole, string[]> = {
  'Super Admin': ['dashboard', 'crm', 'bookings', 'dues', 'projects', 'finance', 'hr', 'stock', 'tasks'],
  'Sales Agent': ['dashboard', 'crm', 'bookings', 'dues', 'handover', 'tasks'],
  'Site Engineer': ['dashboard', 'projects', 'plots', 'contractors', 'qc', 'stock', 'tasks'],
  Finance: ['dashboard', 'finance', 'dues', 'approvals', 'bookings'],
  Customer: ['dashboard', 'bookings', 'dues', 'ticketing']
}

interface AuthState {
  phase: AuthPhase
  user: string
  fullName: string
  roles: string[]
  pwaRole: PwaRole
  tmpId: string
  pendingEmail: string
  pendingPassword: string
  error: string
  busy: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    phase: 'guest',
    user: '',
    fullName: '',
    roles: [],
    pwaRole: 'Super Admin',
    tmpId: '',
    pendingEmail: '',
    pendingPassword: '',
    error: '',
    busy: false
  }),

  getters: {
    authenticated: (s) => s.phase === 'authenticated',
    needsOtp: (s) => s.phase === 'otp',
    canAccess: (s) => (moduleId: string) =>
      s.pwaRole === 'Super Admin' || (ROLE_MODULES[s.pwaRole] ?? []).includes(moduleId)
  },

  actions: {
    /** Restore a stored session token at boot. */
    restore(): void {
      if (api.token) this.phase = 'authenticated'
    },

    async signIn(email: string, password: string): Promise<void> {
      this.busy = true
      this.error = ''
      try {
        const r = await api.login(email, password)
        if (r.ok && r.data && 'token' in r.data) {
          this.applySession(r.data)
        } else if (r.ok && r.data && 'two_factor_required' in r.data) {
          // Stage 1 challenge → ask for the OTP
          this.phase = 'otp'
          this.tmpId = r.data.tmp_id
          this.pendingEmail = email
          this.pendingPassword = password
          this.user = r.data.user
        } else {
          this.error = apiErrorText(r)
          this.phase = 'guest'
        }
      } catch (e) {
        this.error = e instanceof Error ? e.message : 'Sign-in failed'
        this.phase = 'guest'
      } finally {
        this.busy = false
      }
    },

    async submitOtp(otp: string): Promise<void> {
      if (!this.pendingEmail || !this.pendingPassword || !this.tmpId) {
        this.error = 'Session expired — sign in again'
        this.phase = 'guest'
        return
      }
      this.busy = true
      this.error = ''
      try {
        const r = await api.verifyOtp(this.pendingEmail, this.pendingPassword, otp.trim(), this.tmpId)
        if (r.ok && r.data && 'token' in r.data) {
          this.applySession(r.data)
        } else {
          this.error = apiErrorText(r)
        }
      } catch (e) {
        this.error = e instanceof Error ? e.message : 'Verification failed'
      } finally {
        this.busy = false
      }
    },

    applySession(d: LoginSuccess): void {
      api.token = d.token
      localStorage.setItem('rem_api_token', d.token)
      localStorage.setItem('rem_api_url', api.url)
      if (d.user) localStorage.setItem('rem_api_user', d.user)
      this.phase = 'authenticated'
      this.user = d.user
      this.fullName = d.full_name ?? d.user
      this.roles = d.roles ?? []
      this.pwaRole = pwaRoleFor(this.roles)
      this.tmpId = ''
      this.pendingEmail = ''
      this.pendingPassword = ''
    },

    async signOut(): Promise<void> {
      await api.logout()
      this.phase = 'guest'
      this.user = ''
      this.fullName = ''
      this.roles = []
      this.pwaRole = 'Super Admin'
    }
  }
})
