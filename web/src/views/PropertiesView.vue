<script setup lang="ts">
/**
 * PropertiesView — projects with unit inventories from bootstrap:
 * project cards with unit grids (Available/Booked/Sold/Reserved pills).
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { useDataStore } from '@/stores/data'
import StatsRow from '@/components/StatsRow.vue'
import { _t } from '@/i18n'

interface Unit {
  id: string
  number: string
  floor: number
  type: string
  size: string
  price: number
  facing: string
  status: string
  customer?: string
  bookingId?: string
}

interface Property {
  id: string
  name: string
  location: string
  type: string
  totalFloors: number
  totalUnits: number
  status: string
  startDate?: string
  endDate?: string
  units: Unit[]
}

const data = useDataStore()
const properties = ref<Property[]>([])
const loading = ref(true)
const openProject = ref<string | null>(null)

onMounted(async () => {
  const r = await api.call<Record<string, unknown>>('bootstrap')
  if (r.ok && r.data) {
    const props = (r.data as unknown as { properties?: Property[] }).properties
    properties.value = props ?? []
  }
  loading.value = false
})

const stats = computed(() => {
  const allUnits = properties.value.flatMap((p) => p.units)
  return [
    { label: _t('Projects'), value: String(properties.value.length), color: '#2f80ed' },
    { label: 'Total Units', value: String(allUnits.length), color: '#1565c0' },
    { label: 'Available', value: String(allUnits.filter((u) => u.status === 'Available').length), color: '#2e7d32' },
    { label: 'Sold', value: String(allUnits.filter((u) => u.status === 'Sold').length), color: '#7b1fa2' }
  ]
})

function unitStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    Available: ['#e8f5e9', '#2e7d32'],
    Booked: ['#fff8e1', '#ff8f00'],
    Reserved: ['#f3e5f5', '#7b1fa2'],
    Sold: ['#e3f2fd', '#1565c0'],
    'Under Payment': ['#fff3e0', '#e65100']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">Properties & Units</span>
      <span class="page-subtitle">{{ properties.length }} projects · {{ properties.reduce((s, p) => s + p.units.length, 0) }} units</span>
    </div>

    <StatsRow :stats="stats" />

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading properties…</p>

    <div v-else style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px">
      <div v-for="p in properties" :key="p.id" class="card" style="margin-bottom: 0">
        <div class="card-header" style="cursor: pointer" @click="openProject = openProject === p.id ? null : p.id">
          <h3 style="display: flex; align-items: center; gap: 8px">
            <span style="font-size: 14px">{{ p.type === 'Apartment' ? '🏢' : p.type === 'Plot' ? '🗺️' : '🏗️' }}</span>
            {{ p.name }}
            <span class="pill" :style="{ background: (p.status === 'Active' ? '#e8f5e9' : '#fff8e1'), color: (p.status === 'Active' ? '#2e7d32' : '#ff8f00') }" style="font-size: 8px">{{ p.status }}</span>
          </h3>
          <span style="font-size: 10px; color: #888">{{ p.location }} · {{ p.totalUnits }} units · {{ p.startDate }} – {{ p.endDate }}</span>
        </div>
        <div class="card-body" style="padding: 6px 10px">
          <div v-if="openProject === p.id" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 5px">
            <div
              v-for="u in p.units"
              :key="u.id"
              :title="`${u.type} ${u.size} · ${bdt(u.price)} · ${u.customer ?? '—'}`"
              style="border: 1px solid #eee; border-radius: 6px; padding: 4px 6px; cursor: pointer; text-align: center"
            >
              <div style="font-size: 10px; font-weight: 700; color: #333">{{ u.number }}</div>
              <div style="font-size: 8px; color: #888">{{ u.type }}</div>
              <div style="font-size: 8px; color: #888">{{ u.size }}</div>
              <span class="pill" :style="{ background: unitStyle(u.status).bg, color: unitStyle(u.status).fg }" style="font-size: 7px; margin-top: 2px">{{ u.status }}</span>
            </div>
          </div>
          <div v-else style="font-size: 10px; color: #999; text-align: center; padding: 6px">
            Click to expand unit inventory ({{ p.units.length }} units)
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
