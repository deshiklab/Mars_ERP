<template>
  <div v-if="customer" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 720px; max-width: 96vw">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px">
        <h3 style="margin: 0">👤 Customer — <span style="color: #2f80ed">{{ customer.name }}</span></h3>
        <span style="cursor: pointer; color: #999; font-size: 16px; padding: 3px" @click="emit('close')">✕</span>
      </div>

      <!-- header -->
      <div style="display: flex; gap: 12px; align-items: center; background: #f5f7fa; border: 1px solid #e7ebf0; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; flex-wrap: wrap">
        <div style="width: 40px; height: 40px; border-radius: 50%; background: #2f80ed; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px">{{ (customer.name || '?').slice(0, 1) }}</div>
        <div style="flex: 1; min-width: 160px">
          <div style="font-weight: 600; font-size: 13px">{{ customer.name }}</div>
          <div style="font-size: 10px; color: #888; margin-top: 2px">{{ customer.property || '—' }} · {{ customer.project || '' }}</div>
        </div>
        <span class="pill" style="font-size: 10px" :style="{ background: statusStyle(customer.status).bg, color: statusStyle(customer.status).fg }">{{ customer.status || 'Active' }}</span>
        <a v-if="customer.phone" :href="'tel:' + customer.phone" style="text-decoration: none; font-size: 11px; color: #2f80ed">📞 {{ customer.phone }}</a>
        <a v-if="customer.email" :href="'mailto:' + customer.email" style="text-decoration: none; font-size: 11px; color: #2f80ed">✉ {{ customer.email }}</a>
      </div>

      <!-- stats -->
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 10px">
        <div style="background: #fff; border: 1px solid #e7ebf0; border-radius: 8px; padding: 8px 10px">
          <div style="font-size: 9px; color: #888; text-transform: uppercase">Property Value</div>
          <div style="font-weight: 700; font-size: 13px; margin-top: 3px">{{ bdt(customer.propertyValue ?? 0) }}</div>
        </div>
        <div style="background: #fff; border: 1px solid #e7ebf0; border-radius: 8px; padding: 8px 10px">
          <div style="font-size: 9px; color: #888; text-transform: uppercase">Down Payment</div>
          <div style="font-weight: 700; font-size: 13px; margin-top: 3px">{{ bdt(customer.downPayment ?? 0) }}</div>
        </div>
        <div style="background: #fff; border: 1px solid #e7ebf0; border-radius: 8px; padding: 8px 10px">
          <div style="font-size: 9px; color: #888; text-transform: uppercase">Outstanding</div>
          <div style="font-weight: 700; font-size: 13px; margin-top: 3px; color: #d64545">{{ bdt(customer.dues ?? 0) }}</div>
        </div>
        <div style="background: #fff; border: 1px solid #e7ebf0; border-radius: 8px; padding: 8px 10px">
          <div style="font-size: 9px; color: #888; text-transform: uppercase">Payments Made</div>
          <div style="font-weight: 700; font-size: 13px; margin-top: 3px">{{ (customer.payments || []).length }} × {{ bdt(customer.lastPayment ?? 0) }}</div>
        </div>
      </div>

      <!-- tabs -->
      <div style="display: flex; gap: 4px; margin-bottom: 8px">
        <button v-for="t in tabs" :key="t" class="action-btn" :style="tab === t ? 'background:#2f80ed;color:#fff' : ''" @click="tab = t">{{ t }}</button>
      </div>

      <!-- payments tab -->
      <div v-if="tab === 'Payments'" style="max-height: 320px; overflow: auto">
        <div v-if="!payments.length" style="text-align: center; color: #aaa; font-size: 11px; padding: 24px">No payments recorded yet</div>
        <div v-for="p in payments" :key="p.date + p.amount" style="display: flex; justify-content: space-between; border-bottom: 1px solid #f0f2f5; padding: 8px 4px; font-size: 11px">
          <span>{{ p.date }} <span style="color: #888">· {{ p.mode }}</span></span>
          <span style="font-weight: 600">{{ bdt(p.amount ?? 0) }}</span>
        </div>
      </div>

      <!-- dues tab -->
      <div v-else-if="tab === 'Dues'" style="max-height: 320px; overflow: auto">
        <div v-if="!dues.length" style="text-align: center; color: #aaa; font-size: 11px; padding: 24px">No dues — all paid up 🎉</div>
        <div v-for="d in dues" :key="d.dueNo" style="display: flex; justify-content: space-between; border-bottom: 1px solid #f0f2f5; padding: 8px 4px; font-size: 11px; align-items: center">
          <span>#{{ d.dueNo }} <span style="color: #888">· due {{ d.dueDate }}</span></span>
          <span style="font-weight: 600; color: #d64545">{{ bdt(d.amount ?? 0) }}</span>
        </div>
      </div>

      <!-- bookings tab -->
      <div v-else style="max-height: 320px; overflow: auto">
        <div v-if="!bookings.length" style="text-align: center; color: #aaa; font-size: 11px; padding: 24px">No bookings on record</div>
        <div v-for="b in bookings" :key="b.id" style="display: flex; justify-content: space-between; border-bottom: 1px solid #f0f2f5; padding: 8px 4px; font-size: 11px; align-items: center">
          <span><b>{{ b.id }}</b> <span style="color: #888">· {{ b.property || b.flat || '' }} · {{ b.project || '' }}</span></span>
          <span style="font-weight: 600">{{ bdt(b.price ?? b.total ?? 0) }}</span>
        </div>
      </div>

      <!-- status -->
      <div style="display: flex; gap: 8px; margin-top: 12px; align-items: center">
        <span style="font-size: 11px; color: #888">Status:</span>
        <select class="form-select" style="font-size: 12px" :value="customer.status || 'Active'" @change="onStatus($event)">
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
          <option value="Blocked">Blocked</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ customer: any | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 1000 ? `৳ ${(n / 1000).toFixed(1)}K` : `৳ ${n.toLocaleString('en-IN')}`)

const statusStyle = (s?: string) => {
  const map: Record<string, { bg: string; fg: string }> = {
    Active: { bg: '#e6f4ea', fg: '#1e7e34' },
    Inactive: { bg: '#f0f2f5', fg: '#5b6472' },
    Blocked: { bg: '#fdeaea', fg: '#c0392b' },
  }
  return map[s || 'Active'] || { bg: '#f0f2f5', fg: '#5b6472' }
}

const tabs = ['Payments', 'Dues', 'Bookings']
const tab = ref('Payments')

const payments = computed(() => (props.customer?.payments || []).slice().reverse())
const dues = computed(() => (props.customer?.dues || []).slice())

const bookings = computed(() => {
  const all = (props as any).bookings || []
  const n = String(props.customer?.name || '').toLowerCase()
  return all.filter((b: any) => String(b.customer_name || '').toLowerCase() === n)
})

const onStatus = (e: Event) => {
  const v = (e.target as HTMLSelectElement).value
  if (v && v !== (props.customer?.status || 'Active')) emit('status', v)
}
</script>