<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const otp = ref('')
const showOtp = ref(false)
const otpError = ref('')

async function onSignIn() {
  if (!email.value || !password.value) {
    auth.error = 'Enter your email and password'
    return
  }
  otpError.value = ''
  await auth.signIn(email.value, password.value)
  if (auth.needsOtp) showOtp.value = true
  if (auth.authenticated) router.push('/')
}

async function onVerify() {
  if (!/^\d{6}$/.test(otp.value.trim())) {
    otpError.value = 'Enter the 6-digit code from your authenticator app'
    return
  }
  otpError.value = ''
  await auth.submitOtp(otp.value)
  if (auth.authenticated) {
    showOtp.value = false
    router.push('/')
  }
}

function cancelOtp() {
  showOtp.value = false
  auth.phase = 'guest'
  auth.error = ''
  otp.value = ''
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-[#0d1b2a] via-[#1b263b] to-[#2f80ed] p-4">
    <div class="w-full max-w-sm rounded-2xl bg-white p-8 text-center shadow-2xl">
      <div class="mb-1 text-4xl">🏗️</div>
      <h1 class="text-lg font-bold text-slate-900">MARS Constech</h1>
      <p class="mb-6 mt-1 text-xs text-slate-400">REM ERP — Secure Sign In</p>

      <!-- Password stage -->
      <form v-if="!showOtp" class="space-y-4" @submit.prevent="onSignIn">
        <div class="text-left">
          <label class="mb-1 block text-xs font-medium text-slate-600">Email</label>
          <input
            v-model="email"
            type="email"
            autocomplete="username"
            placeholder="you@mars.com"
            class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-[#2f80ed] focus:ring-2 focus:ring-[#2f80ed]/20"
          />
        </div>
        <div class="text-left">
          <label class="mb-1 block text-xs font-medium text-slate-600">Password</label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-[#2f80ed] focus:ring-2 focus:ring-[#2f80ed]/20"
          />
        </div>

        <p v-if="auth.error" class="text-xs text-rose-600">{{ auth.error }}</p>
        <p class="text-left text-[10px] text-slate-400">Server: {{ $route.query.api ?? '/api/method/mars_constech.mars_constech.api' }}</p>

        <button
          type="submit"
          :disabled="auth.busy"
          class="w-full rounded-lg bg-[#2f80ed] py-2.5 text-sm font-semibold text-white transition hover:bg-[#1e6fd0] disabled:opacity-60"
        >
          {{ auth.busy ? '⏳ Signing in…' : '🔐 Sign In' }}
        </button>
      </form>

      <!-- OTP stage -->
      <div v-else class="space-y-4">
        <div class="text-3xl">🔐</div>
        <h2 class="text-sm font-semibold text-slate-800">Two-factor authentication</h2>
        <p class="text-xs text-slate-400">
          Enter the 6-digit code from your authenticator app.
        </p>
        <input
          v-model="otp"
          type="text"
          inputmode="numeric"
          autocomplete="one-time-code"
          maxlength="6"
          placeholder="••••••"
          class="mx-auto block w-40 rounded-lg border border-slate-200 px-3 py-2.5 text-center text-lg tracking-[0.4em] outline-none focus:border-[#2f80ed] focus:ring-2 focus:ring-[#2f80ed]/20"
        />
        <p v-if="otpError" class="text-xs text-rose-600">{{ otpError }}</p>
        <p v-else-if="auth.error" class="text-xs text-rose-600">{{ auth.error }}</p>
        <p class="text-[10px] text-slate-400">Codes refresh every 30s — if it fails, enter the new one.</p>

        <button
          :disabled="auth.busy"
          class="w-full rounded-lg bg-[#2f80ed] py-2.5 text-sm font-semibold text-white transition hover:bg-[#1e6fd0] disabled:opacity-60"
          @click="onVerify"
        >
          {{ auth.busy ? '⏳ Verifying…' : 'Verify' }}
        </button>
        <button class="w-full text-xs text-slate-400 hover:text-slate-600" @click="cancelOtp">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>
