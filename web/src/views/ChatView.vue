<script setup lang="ts">
/**
 * ChatView — workspace chat from bootstrap (channels + messages):
 * channel list on the left, message bubbles on the right.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

interface WsMsg {
  id: string
  channel: string
  sender: string
  role: string
  msg: string
  time: string
}

const auth = useAuthStore()
const channels = ref<string[]>([])
const messages = ref<WsMsg[]>([])
const active = ref('')
const loading = ref(true)
const draft = ref('')

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const msgs = (r.data.collections.workspace_chat as WsMsg[]) ?? []
    messages.value = msgs
    const chans = [...new Set(msgs.map((m) => m.channel))]
    channels.value = chans
    active.value = chans[0] ?? ''
  }
  loading.value = false
})

const activeMsgs = computed(() => messages.value.filter((m) => m.channel === active.value))
const me = computed(() => auth.user)

function send() {
  const text = draft.value.trim()
  if (!text) return
  messages.value.push({
    id: 'local-' + Date.now(),
    channel: active.value,
    sender: auth.fullName || auth.user,
    role: 'me',
    msg: text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  draft.value = ''
}

function bubbleColor(role: string, sender: string): string {
  if (role === 'me' || sender === me.value) return '#2f80ed'
  return '#f0f4ff'
}

function bubbleText(role: string, sender: string): string {
  if (role === 'me' || sender === me.value) return '#fff'
  return '#333'
}

function initials(name: string): string {
  return name.split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('') || '?'
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">Team Chat</span>
      <span class="page-subtitle">{{ channels.length }} channels · {{ messages.length }} messages</span>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading chat…</p>

    <div v-else class="card" style="display: flex; height: 520px; padding: 0; overflow: hidden">
      <!-- channels -->
      <div style="width: 180px; border-right: 1px solid #e8e8e8; overflow-y: auto">
        <div style="padding: 10px 12px; font-size: 10px; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: .5px">Channels</div>
        <div
          v-for="ch in channels"
          :key="ch"
          style="padding: 8px 12px; font-size: 11px; cursor: pointer; display: flex; align-items: center; gap: 6px"
          :style="active === ch ? 'background:#f0f4ff;color:#2f80ed;font-weight:600;border-left:3px solid #2f80ed' : 'color:#555'"
          @click="active = ch"
        >
          <span style="font-size: 13px">💬</span>{{ ch }}
        </div>
        <div v-if="channels.length === 0" style="padding: 16px; font-size: 10px; color: #999; text-align: center">No channels</div>
      </div>

      <!-- messages -->
      <div style="flex: 1; display: flex; flex-direction: column; min-width: 0">
        <div style="padding: 8px 14px; border-bottom: 1px solid #f0f0f0; font-size: 12px; font-weight: 700; color: #333; display: flex; align-items: center; gap: 6px">
          <span style="width: 8px; height: 8px; border-radius: 50%; background: #2e7d32; display: inline-block"></span>
          # {{ active }}
        </div>
        <div style="flex: 1; overflow-y: auto; padding: 12px 14px; display: flex; flex-direction: column; gap: 8px">
          <div
            v-for="m in activeMsgs"
            :key="m.id"
            style="display: flex; gap: 8px; align-items: flex-start; max-width: 78%"
            :style="m.role === 'me' || m.sender === me ? 'align-self:flex-end; flex-direction:row-reverse' : ''"
          >
            <span
              style="width: 26px; height: 26px; border-radius: 50%; background: linear-gradient(135deg, #7b1fa2, #2f80ed); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 700; flex-shrink: 0"
            >{{ initials(m.sender) }}</span>
            <div>
              <div v-if="m.role !== 'me' && m.sender !== me" style="font-size: 9px; color: #888; margin-bottom: 2px">{{ m.sender }}</div>
              <div
                style="padding: 7px 12px; border-radius: 12px; font-size: 11px; line-height: 1.5"
                :style="{ background: bubbleColor(m.role, m.sender), color: bubbleText(m.role, m.sender), borderBottomLeftRadius: m.role === 'me' || m.sender === me ? '12px' : '2px', borderBottomRightRadius: m.role === 'me' || m.sender === me ? '2px' : '12px' }"
              >{{ m.msg }}</div>
              <div style="font-size: 8px; color: #aaa; margin-top: 2px" :style="m.role === 'me' || m.sender === me ? 'text-align:right' : ''">{{ m.time }}</div>
            </div>
          </div>
          <div v-if="activeMsgs.length === 0" style="padding: 20px; text-align: center; color: #999; font-size: 11px">No messages in #{{ active }}</div>
        </div>
        <!-- composer -->
        <div style="display: flex; gap: 8px; padding: 10px 14px; border-top: 1px solid #f0f0f0">
          <input
            v-model="draft"
            placeholder="Type a message…"
            style="flex: 1; border: 1px solid #e0e0e0; border-radius: 18px; padding: 7px 14px; font-size: 11px; outline: none"
            @keydown.enter="send"
          />
          <button class="action-btn primary" @click="send">➤ Send</button>
        </div>
      </div>
    </div>
  </div>
</template>
