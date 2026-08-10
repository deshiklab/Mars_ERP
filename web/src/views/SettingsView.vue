<script setup lang="ts">
/**
 * SettingsView — mirrors the HTML PWA System Settings tab:
 * toggles from settings_get, save via settings_set.
 */
import { computed, onMounted, ref } from 'vue'
import { api, apiErrorText } from '@/api/client'
import { showToast } from '@/toast'
import { _t } from '@/i18n'

interface Settings {
  pwa_version?: string
  api_base_override?: string
  auto_connect?: boolean
  push_on_save?: boolean
  auto_heal?: boolean
  live_land?: boolean
  session_expiry?: string
  last_connected_user?: string
  last_sync_time?: string
}

const settings = ref<Settings>({})
const loading = ref(true)
const saving = ref(false)
const synced = ref(false)

async function load() {
  loading.value = true
  const r = await api.call<Settings>('settings_get')
  if (r.ok && r.data) {
    settings.value = r.data
  } else {
    showToast('Failed to load settings', 'error')
  }
  loading.value = false
}

async function save() {
  saving.value = true
  const r = await api.call<Settings>('settings_set', {
    auto_connect: settings.value.auto_connect,
    push_on_save: settings.value.push_on_save,
    auto_heal: settings.value.auto_heal,
    live_land: settings.value.live_land
  })
  saving.value = false
  if (r.ok) {
    showToast('Settings saved', 'success')
    synced.value = true
  } else {
    showToast('Save failed: ' + apiErrorText(r), 'error')
  }
}

const toggleItems = computed(() => [
  { key: 'auto_connect', label: 'Auto-connect to server', sub: 'Automatically connect to the Frappe bridge on launch', icon: '🔌' },
  { key: 'push_on_save', label: 'Push on save', sub: 'Sync changes to the server immediately when saved', icon: '📤' },
  { key: 'auto_heal', label: 'Auto-heal connection', sub: 'Retry dropped connections automatically', icon: '🩹' },
  { key: 'live_land', label: 'Live land data', sub: 'Pull live land acquisition data', icon: '🗺️' }
])

function setToggle(key: string, v: boolean) {
  ;(settings.value as Record<string, unknown>)[key] = v
}

onMounted(load)
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">{{ _t('System Settings') }}</span>
      <span class="page-subtitle">PWA v{{ settings.pwa_version ?? '—' }}</span>
      <div style="margin-left: auto; display: flex; gap: 8px">
        <button class="action-btn" @click="load">↻ Reload</button>
        <button class="action-btn primary" :disabled="saving" @click="save">{{ saving ? 'Saving…' : '💾 Save' }}</button>
      </div>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading settings…</p>

    <div v-else style="max-width: 640px">
      <!-- toggles -->
      <div class="card" style="margin-bottom: 12px">
        <div class="card-header"><h3>⚙️ Preferences</h3></div>
        <div class="card-body" style="padding: 4px 12px">
          <div
            v-for="t in toggleItems"
            :key="t.key"
            style="display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid #f5f5f5"
          >
            <span style="font-size: 16px">{{ t.icon }}</span>
            <div style="flex: 1">
              <div style="font-size: 12px; font-weight: 600; color: #333">{{ t.label }}</div>
              <div style="font-size: 10px; color: #888">{{ t.sub }}</div>
            </div>
            <button
              style="width: 40px; height: 22px; border-radius: 12px; border: none; cursor: pointer; position: relative; transition: background 0.15s"
              :style="{ background: settings[t.key as keyof Settings] ? '#2f80ed' : '#ddd' }"
              @click="setToggle(t.key, !settings[t.key as keyof Settings])"
            >
              <span
                style="position: absolute; top: 2px; width: 18px; height: 18px; border-radius: 50%; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.2); transition: left 0.15s"
                :style="{ left: settings[t.key as keyof Settings] ? '20px' : '2px' }"
              ></span>
            </button>
          </div>
        </div>
      </div>

      <!-- connection info -->
      <div class="card" style="margin-bottom: 12px">
        <div class="card-header"><h3>🔗 Connection</h3></div>
        <div class="card-body" style="font-size: 11px; color: #555; line-height: 1.9">
          <div style="display: flex; justify-content: space-between">
            <span style="color: #888">API base override</span>
            <b style="color: #333">{{ settings.api_base_override || '(default)' }}</b>
          </div>
          <div style="display: flex; justify-content: space-between">
            <span style="color: #888">Session expiry</span>
            <b style="color: #333">{{ settings.session_expiry }}</b>
          </div>
          <div style="display: flex; justify-content: space-between">
            <span style="color: #888">Last connected user</span>
            <b style="color: #333">{{ settings.last_connected_user || '—' }}</b>
          </div>
          <div style="display: flex; justify-content: space-between">
            <span style="color: #888">Last sync</span>
            <b style="color: #333">{{ settings.last_sync_time || '—' }}</b>
          </div>
        </div>
      </div>

      <p v-if="synced" style="font-size: 11px; color: #2e7d32">✓ Saved successfully</p>
    </div>
  </div>
</template>
