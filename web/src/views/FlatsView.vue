<script setup lang="ts">
/**
 * FlatsView — mirrors the HTML renderPropertiesUnits:
 * stats row (Available/Booked/Under Payment/Reserved/Sold/Total),
 * project tabs (Dashboard/All/Project A…), unit grid with status
 * colors, unit cards (id, type, size, floor, price, status).
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import StatsRow from '@/components/StatsRow.vue'

interface Unit { id: string; status: string; price: number; size: string; floor: number; type: string }
interface Prop { id: string; name: string; location: string; type: string; status: string; units: Unit[]; totalFloors: number; totalUnits: number }

const props_ = ref<Prop[]>([])
const loading = ref(true)
const activeProject = ref('all')

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    const list = (r.data.collections.properties as any[]) ?? []
    props_.value = list.map((p) => ({
      ...p,
      units: (p.units ?? []).map((u: any) => ({
        id: String(u.id ?? ''),
        status: u.status ?? 'Available',
        price: Number(u.price) || 0,
        size: u.size ?? '',
        floor: u.floor ?? 0,
        type: u.type ?? ''
      }))
    }))
  }
  loading.value = false
})

const totalUnits = computed(() => props_.value.reduce((s, p) => s + p.units.length, 0))
const totalValue = computed(() => props_.value.reduce((s, p) => s + p.units.reduce((s2, u) => s2 + u.price, 0), 0))
const countBy = (st: string) => props_.value.reduce((s, p) => s + p.units.filter((u) => u.status === st).length, 0)

const stats = computed(() => [
  { label: '🟢 Available', value: String(countBy('Available')), color: '#4caf50' },
  { label: '🔵 Booked', value: String(countBy('Booked')), color: '#2196f3' },
  { label: '🟣 Under Payment', value: String(countBy('Under Payment')), color: '#9c27b0' },
  { label: '🟡 Reserved', value: String(countBy('Reserved')), color: '#ff9800' },
  { label: '🔴 Sold', value: String(countBy('Sold')), color: '#e53935' },
  { label: '📊 Total Units', value: String(totalUnits.value), color: '#2f80ed' }
])

const projects = computed(() => [{ id: 'all', name: 'All Projects' }, ...props_.value.map((p) => ({ id: p.id, name: p.name }))])

const visibleUnits = computed(() => {
  const list = activeProject.value === 'all' ? props_.value : props_.value.filter((p) => p.id === activeProject.value)
  return list.flatMap((p) => p.units.map((u) => ({ ...u, project: p.name })))
})

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

const statusStyle = (st: string): { bg: string; fg: string } => {
  const map: Record<string, { bg: string; fg: string }> = {
    Available: { bg: '#e8f5e9', fg: '#2e7d32' },
    Booked: { bg: '#e3f2fd', fg: '#1565c0' },
    'Under Payment': { bg: '#f3e5f5', fg: '#7b1fa2' },
    Reserved: { bg: '#fff8e1', fg: '#e65100' },
    Sold: { bg: '#ffebee', fg: '#c62828' }
  }
  return map[st] ?? { bg: '#f5f5f5', fg: '#555' }
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">🏢 Flats & Units</span>
      <span class="page-subtitle">{{ props_.length }} projects · {{ totalUnits }} units · {{ bdt(totalValue) }} total value</span>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading units…</p>

    <template v-else>
      <StatsRow :stats="stats" />

      <!-- project tabs -->
      <div class="toolbar" style="margin: 8px 0 6px">
        <div class="tabs">
          <div
            v-for="p in projects"
            :key="p.id"
            class="tab"
            :class="{ active: activeProject === p.id }"
            style="font-size: 10px; padding: 5px 12px"
            @click="activeProject = p.id"
          >{{ p.name }}</div>
        </div>
      </div>

      <!-- unit grid -->
      <div class="card" style="padding: 10px">
        <div style="display: flex; flex-wrap: wrap; gap: 6px">
          <div
            v-for="u in visibleUnits"
            :key="u.id + u.project"
            style="
              width: 148px;
              border: 1px solid #e8e8e8;
              border-radius: 8px;
              padding: 8px 10px;
              background: #fff;
              border-left: 3px solid;
            "
            :style="{ borderLeftColor: statusStyle(u.status).fg }"
          >
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span style="font-size: 12px; font-weight: 700; color: #222">{{ u.id }}</span>
              <span style="font-size: 8px; padding: 1px 5px; border-radius: 4px; font-weight: 600" :style="{ background: statusStyle(u.status).bg, color: statusStyle(u.status).fg }">{{ u.status }}</span>
            </div>
            <div style="font-size: 9px; color: #888; margin-top: 2px">{{ u.type }} · Floor {{ u.floor }}</div>
            <div style="font-size: 9px; color: #555">{{ u.size }}</div>
            <div style="font-size: 11px; font-weight: 700; color: #2f80ed; margin-top: 3px">{{ bdt(u.price) }}</div>
          </div>
        </div>
        <div v-if="!visibleUnits.length" style="text-align: center; padding: 28px; color: #999; font-size: 11px">No units in this project.</div>
      </div>
    </template>
  </div>
</template>
