<script setup lang="ts">
/**
 * LicenseView — License & SLA (System group): license card,
 * fees, payment installments, implementation checklist.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'

const lic = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const raw = (r.data.collections.license as any) ?? null
    lic.value = raw ? {
      ...raw,
      installments: typeof raw.installments === 'string' ? safeParse(raw.installments) : (raw.installments ?? []),
      checklist: typeof raw.checklist === 'string' ? safeParse(raw.checklist) : (raw.checklist ?? [])
    } : null
  }
  loading.value = false
})

function safeParse(s: string): any[] {
  try { const v = JSON.parse(s.replace(/'/g, '"')); return Array.isArray(v) ? v : [] } catch { return [] }
}

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)
const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

const isExpired = computed(() => lic.value?.expires && lic.value.expires < new Date().toISOString().slice(0, 10))
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">License & SLA</span>
      <span class="page-subtitle">License details · fees · implementation checklist</span>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading license…</p>

    <template v-else-if="lic">
      <!-- license card -->
      <div class="card" style="margin-bottom: 10px; background: linear-gradient(135deg, #0d1b2a, #1b263b); color: #fff">
        <div class="card-body" style="padding: 14px">
          <div style="display: flex; justify-content: space-between; align-items: flex-start">
            <div>
              <div style="font-size: 16px; font-weight: 700">{{ esc(lic.product) }}</div>
              <div style="font-size: 11px; opacity: 0.8; margin-top: 2px">{{ esc(lic.client) }}</div>
              <div style="font-size: 10px; color: #56ccf2; margin-top: 6px; font-family: monospace">{{ esc(lic.licenseKey) }}</div>
            </div>
            <span class="pill" style="background: #e8f5e9; color: #2e7d32; font-size: 10px">{{ esc(lic.status) }}</span>
          </div>
          <div style="display: flex; gap: 18px; margin-top: 12px; font-size: 10px; flex-wrap: wrap">
            <span>📅 Issued: <b>{{ esc(lic.issued) }}</b></span>
            <span>⏳ Expires: <b :style="{ color: isExpired ? '#ff8a80' : '#a5d6a7' }">{{ esc(lic.expires) }}</b></span>
            <span>🖥 Server Fee: <b>{{ bdt(Number(lic.serverFee) || 0) }}</b></span>
            <span>🛠 Support Fee: <b>{{ bdt(Number(lic.supportFee) || 0) }}</b></span>
            <span>📄 Contract: <b>{{ bdt(Number(lic.contract) || 0) }}</b></span>
          </div>
        </div>
      </div>

      <!-- installments + checklist -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px">
        <div class="card">
          <div class="card-header"><h3>💳 Payment Installments</h3></div>
          <div class="card-body">
            <div v-for="ins in lic.installments" :key="ins.no" style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f5f5f5">
              <div>
                <div style="font-size: 11px; font-weight: 600; color: #333">{{ ins.label }}</div>
                <div style="font-size: 9px; color: #888">Due {{ ins.due }}</div>
              </div>
              <div style="text-align: right">
                <div style="font-size: 11px; font-weight: 700; color: #2f80ed">{{ bdt(Number(ins.amount) || 0) }}</div>
                <span class="pill" :style="{ background: ins.status === 'Paid' ? '#e8f5e9' : '#fff8e1', color: ins.status === 'Paid' ? '#2e7d32' : '#e65100' }">{{ ins.status }}</span>
              </div>
            </div>
            <div v-if="!lic.installments.length" style="text-align: center; padding: 14px; color: #999; font-size: 11px">No installments.</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header"><h3>✅ Implementation Checklist</h3></div>
          <div class="card-body">
            <div v-for="c in lic.checklist" :key="c.id" style="display: flex; gap: 8px; align-items: flex-start; padding: 6px 0; border-bottom: 1px solid #f5f5f5">
              <span style="font-size: 11px; color: c.done ? '#2e7d32' : '#bdbdbd'">{{ c.done ? '✅' : '⬜' }}</span>
              <div style="flex: 1">
                <div style="font-size: 11px; color: #333">{{ c.title }}</div>
                <div style="font-size: 9px; color: #888">Due {{ c.due }}</div>
              </div>
            </div>
            <div v-if="!lic.checklist.length" style="text-align: center; padding: 14px; color: #999; font-size: 11px">No checklist items.</div>
          </div>
        </div>
      </div>
    </template>

    <div v-else style="text-align: center; padding: 40px; color: #999; font-size: 12px">No license data.</div>
  </div>
</template>
