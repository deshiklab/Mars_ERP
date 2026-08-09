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

// ── Session restore + 401 handling ────────────────────────────────────
const auth = useAuthStore()
auth.restore()

api.setOnUnauthorized(() => {
  // a dead session mid-flight → back to the login gate
  if (router.currentRoute.value.name !== 'login') {
    router.push('/login')
  }
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
