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
  <!-- Mirrors the HTML PWA gate: dark blue gradient, white rounded card -->
  <div
    style="
      position: fixed;
      inset: 0;
      z-index: 9999;
      background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 60%, #2f80ed 160%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Inter', Arial, sans-serif;
    "
  >
    <div
      style="
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
        width: 380px;
        max-width: 92vw;
        padding: 34px 32px;
        text-align: center;
      "
    >
      <div style="font-size: 40px; margin-bottom: 6px">🏗️</div>
      <div style="font-size: 19px; font-weight: 700; color: #0d1b2a">MARS Constech</div>
      <div style="font-size: 11px; color: #888; margin: 3px 0 20px">REM ERP — Secure Sign In</div>

      <!-- Password stage -->
      <form v-if="!showOtp" @submit.prevent="onSignIn">
        <div class="form-group" style="text-align: left">
          <label class="form-label">Email</label>
          <input v-model="email" type="email" class="form-input" placeholder="you@mars.com" autocomplete="username" style="padding: 10px 12px" />
        </div>
        <div class="form-group" style="text-align: left">
          <label class="form-label">Password</label>
          <input v-model="password" type="password" class="form-input" placeholder="••••••••" autocomplete="current-password" style="padding: 10px 12px" />
        </div>

        <p v-if="auth.error" style="font-size: 10px; color: #e53935; min-height: 14px; margin: 2px 0 8px">{{ auth.error }}</p>
        <p v-else style="font-size: 10px; color: #999; min-height: 14px; margin: 2px 0 8px; text-align: left">
          Server: /api/method/mars_constech.mars_constech.api
        </p>

        <button
          type="submit"
          :disabled="auth.busy"
          style="
            width: 100%;
            padding: 11px;
            font-size: 13px;
            background: #2f80ed;
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
          "
        >
          {{ auth.busy ? '⏳ Signing in…' : '🔐 Sign In' }}
        </button>

        <div style="font-size: 10px; color: #999; margin-top: 16px">
          New customer?
          <a href="javascript:void(0)" style="color: #2f80ed; font-weight: 600">Create an account</a>
        </div>
        <div style="font-size: 9px; color: #bbb; margin-top: 10px">2FA protected · sessions expire in 8h</div>
      </form>

      <!-- OTP stage -->
      <div v-else>
        <div style="font-size: 30px; margin-bottom: 6px">🔐</div>
        <div style="font-size: 13px; font-weight: 600; color: #222; margin-bottom: 4px">Two-factor authentication</div>
        <div style="font-size: 10px; color: #888; margin-bottom: 14px">
          Enter the 6-digit code from your authenticator app.
        </div>
        <input
          v-model="otp"
          type="text"
          inputmode="numeric"
          autocomplete="one-time-code"
          maxlength="6"
          placeholder="••••••"
          style="
            width: 150px;
            padding: 9px 10px;
            font-size: 18px;
            letter-spacing: 6px;
            text-align: center;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            outline: none;
          "
        />
        <p v-if="otpError" style="font-size: 10px; color: #e53935; margin-top: 8px">{{ otpError }}</p>
        <p v-else-if="auth.error" style="font-size: 10px; color: #e53935; margin-top: 8px">{{ auth.error }}</p>
        <p style="font-size: 9px; color: #999; margin-top: 4px">Codes refresh every 30s — if it fails, enter the new one.</p>

        <button
          :disabled="auth.busy"
          class="action-btn primary"
          style="width: 100%; padding: 11px; font-size: 13px; margin-top: 14px"
          @click="onVerify"
        >
          {{ auth.busy ? '⏳ Verifying…' : 'Verify' }}
        </button>
        <button class="action-btn" style="width: 100%; margin-top: 6px" @click="cancelOtp">Cancel</button>
      </div>
    </div>
  </div>
</template>
