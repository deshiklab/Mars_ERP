import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { api } from './api/client'
import { useAuthStore } from './stores/auth'

// ── PWA / service worker registration ────────────────────────────────
// vite-plugin-pwa (registerType: 'autoUpdate') — new SW installs and the
// app reloads automatically to the latest build.
import { registerSW } from 'virtual:pwa-register'

const updateSW = registerSW({
  immediate: true,
  onNeedRefresh() {
    updateSW(true)
  },
  onOfflineReady() {
    console.info('[PWA] App ready to work offline')
  }
})

// ── App bootstrap ─────────────────────────────────────────────────────
// IMPORTANT: pinia must be installed BEFORE any useAuthStore() call —
// calling a store without an active pinia throws and kills the whole app
// (the blank-white-screen bug).
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Session restore + 401 handling (pinia is active now).
const auth = useAuthStore()
auth.restore()

api.setOnUnauthorized(() => {
  // a dead session mid-flight → back to the login gate (reset the phase
  // FIRST or the auth guard sees authenticated=true and bounces back)
  auth.$patch({ phase: 'guest', user: '', fullName: '', roles: [], tmpId: '', pendingEmail: '', pendingPassword: '', error: '' })
  if (router.currentRoute.value.name !== 'login') {
    router.push('/login')
  }
})

app.mount('#app')
