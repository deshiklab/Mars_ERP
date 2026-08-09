import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// ── PWA / service worker registration ────────────────────────────────
// vite-plugin-pwa (registerType: 'autoUpdate') generates the worker and the
// virtual `virtual:pwa-register` module. Calling registerSW() wires the
// auto-update lifecycle: the new SW installs, activates, and the app is
// reloaded automatically to pick up the latest build.
import { registerSW } from 'virtual:pwa-register'

const updateSW = registerSW({
  immediate: true,
  onNeedRefresh() {
    // A new version is ready (autoUpdate keeps the old one serving until
    // this resolves) — we auto-reload for a seamless experience.
    updateSW(true)
  },
  onOfflineReady() {
    console.info('[PWA] App ready to work offline')
  }
})

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
