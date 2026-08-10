<script setup lang="ts">
/**
 * ProfilePanel — mirrors the HTML PWA user profile panel:
 * avatar, name, email, role chip, server roles, session info, Sign Out.
 */
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { _t } from '@/i18n'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const auth = useAuthStore()
const router = useRouter()

function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || 'U'
}

async function signOut() {
  emit('close')
  await auth.signOut()
  router.push('/login')
}
</script>

<template>
  <div v-if="open" class="drawer-overlay active" style="justify-content: flex-start" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 360px; animation: none">
      <!-- header -->
      <div style="padding: 20px 16px; text-align: center; border-bottom: 1px solid #f0f0f0; background: linear-gradient(135deg, #0d1b2a, #1b263b)">
        <div
          style="
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2f80ed, #56ccf2);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            font-weight: 700;
            margin: 0 auto;
            border: 3px solid rgba(255, 255, 255, 0.3);
          "
        >{{ initials(auth.fullName || auth.user) }}</div>
        <div style="color: #fff; font-size: 14px; font-weight: 700; margin-top: 10px">{{ auth.fullName || auth.user }}</div>
        <div style="color: rgba(255, 255, 255, 0.7); font-size: 11px; margin-top: 2px">{{ auth.user }}</div>
        <div style="margin-top: 8px">
          <span style="background: #2f80ed; color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 600">{{ auth.pwaRole }}</span>
        </div>
      </div>

      <!-- body -->
      <div class="drawer-body" style="font-size: 11px; color: #555; line-height: 1.9">
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f5f5">
          <span style="color: #888">{{ _t('Role') }}</span>
          <b style="color: #333">{{ auth.pwaRole }}</b>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f5f5">
          <span style="color: #888">{{ _t('Server roles') }}</span>
          <b style="color: #333; text-align: right">{{ auth.roles.join(', ') || '—' }}</b>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f5f5">
          <span style="color: #888">{{ _t('Session') }}</span>
          <b style="color: #2e7d32">Active · 8h</b>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0">
          <span style="color: #888">PWA Version</span>
          <b style="color: #333">3.1.1</b>
        </div>
      </div>

      <div class="drawer-footer" style="display: flex; gap: 8px">
        <button class="drawer-btn" style="flex: 1" @click="emit('close')">Close</button>
        <button class="drawer-btn" style="flex: 1; background: #c62828; color: #fff; border-color: #c62828" @click="signOut">{{ _t('Sign Out') }}</button>
      </div>
    </div>
  </div>
</template>
