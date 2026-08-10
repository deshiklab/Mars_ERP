<script setup lang="ts">
/**
 * ProjectDetailDrawer — project panel: identity header, stats
 * (type/location/status/progress/budget/manager/plots), milestone
 * timeline (done/pending with dates), phase + description.
 */
import { computed, ref, watch } from 'vue'
import type { Project } from '@/api/types'

const props = defineProps<{ project: Project | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'status', status: string): void }>()
const tab = ref('overview')
watch(() => props.project, () => (tab.value = 'overview'))

const bdt = (n: number) => (n >= 10000000 ? `৳ ${(n / 10000000).toFixed(2)} Cr` : n >= 100000 ? `৳ ${(n / 100000).toFixed(1)} Lac` : `৳ ${n.toLocaleString()}`)

function statusColor(s: string): string {
  const map: Record<string, string> = {
    Active: '#2e7d32', Planning: '#2f80ed', Completed: '#2e7d32', 'On Hold': '#e65100',
    'Under Construction': '#2f80ed', Design: '#7b1fa2', Cancelled: '#c62828'
  }
  return map[s] ?? '#555'
}

const milestones = computed(() => {
  const p = props.project as unknown as { milestones?: { label: string; date: string; status: string }[] }
  return p?.milestones ?? []
})
const doneCount = () => milestones.value.filter((m) => m.status === 'done' || m.status === 'completed').length
</script>

<template>
  <div v-if="project" class="drawer-overlay active" style="justify-content: flex-end" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 540px; max-width: 100vw; height: 100%; max-height: 100vh; border-radius: 0; display: flex; flex-direction: column">
      <div class="drawer-header" style="flex-shrink: 0">
        <h3 style="display: flex; align-items: center; gap: 8px">
          🏗 {{ project.name }}
          <span class="pill" :style="{ background: statusColor(project.status) + '22', color: statusColor(project.status) }">{{ project.status }}</span>
        </h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>

      <div class="drawer-body" style="flex: 1; overflow-y: auto">
        <!-- stats -->
        <div class="stats-row" style="grid-template-columns: 1fr 1fr">
          <div class="stat-card"><div class="label">Type</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ project.type || '—' }}</div></div>
          <div class="stat-card"><div class="label">📍 Location</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ project.location || '—' }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">📅 Start</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ project.start || '—' }}</div></div>
          <div class="stat-card"><div class="label">🏁 End</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ project.end || '—' }}</div></div>
        </div>
        <div class="stats-row" style="grid-template-columns: 1fr 1fr; margin-top: 6px">
          <div class="stat-card"><div class="label">💰 Budget</div><div style="font-size: 14px; font-weight: 700; color: #2f80ed; margin-top: 2px">{{ bdt(Number(project.budget) || 0) }}</div></div>
          <div class="stat-card"><div class="label">👤 Manager</div><div style="font-size: 12px; font-weight: 600; margin-top: 2px">{{ project.manager || '—' }}</div></div>
        </div>

        <!-- progress -->
        <div style="margin-top: 10px">
          <div style="display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 4px">
            <span style="font-weight: 600; color: #555">Progress</span>
            <span style="font-weight: 700; color: #2f80ed">{{ project.progress }}%</span>
          </div>
          <div style="height: 7px; background: #f0f0f0; border-radius: 4px; overflow: hidden">
            <div :style="{ width: Math.min(100, Number(project.progress) || 0) + '%', background: 'linear-gradient(90deg, #2f80ed, #56ccf2)', height: '100%' }"></div>
          </div>
        </div>

        <!-- milestones timeline -->
        <div style="margin-top: 14px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 8px">🏁 Milestones ({{ doneCount() }}/{{ milestones.length }} done)</h3>
          <div v-for="(m, i) in milestones" :key="i" style="display: flex; gap: 10px; padding-bottom: 12px; position: relative">
            <div style="display: flex; flex-direction: column; align-items: center">
              <span
                style="width: 14px; height: 14px; border-radius: 50%; border: 2px solid; display: inline-flex; align-items: center; justify-content: center; font-size: 8px; flex-shrink: 0"
                :style="{ borderColor: m.status === 'done' ? '#2e7d32' : '#bdbdbd', background: m.status === 'done' ? '#2e7d32' : '#fff', color: '#fff' }"
              >{{ m.status === 'done' ? '✓' : '' }}</span>
              <span v-if="i < milestones.length - 1" style="width: 2px; flex: 1; background: #e0e0e0; margin-top: 2px"></span>
            </div>
            <div style="padding-bottom: 2px">
              <div style="font-size: 11px; font-weight: 600; color: #333">{{ m.label }}</div>
              <div style="font-size: 9px; color: #888">{{ m.date }} · <span :style="{ color: m.status === 'done' ? '#2e7d32' : '#e65100' }">{{ m.status === 'done' ? 'Done' : 'Pending' }}</span></div>
            </div>
          </div>
          <div v-if="!milestones.length" style="text-align: center; padding: 16px; color: #999; font-size: 11px; border: 2px dashed #e0e0e0; border-radius: 8px">No milestones yet.</div>
        </div>

        <!-- description -->
        <div v-if="project.desc" style="margin-top: 10px">
          <h3 style="font-size: 11px; font-weight: 600; color: #555; margin-bottom: 4px">📝 Description</h3>
          <div class="stat-card" style="white-space: pre-wrap; font-size: 11px; color: #555">{{ project.desc }}</div>
        </div>

        <!-- actions -->
        <div style="margin-top: 14px; display: flex; gap: 6px; flex-wrap: wrap">
          <button class="action-btn" style="color: #2f80ed" @click="emit('status', 'Under Construction')">🚧 Start Construction</button>
          <button class="action-btn" style="color: #e65100" @click="emit('status', 'On Hold')">⏸ On Hold</button>
          <button class="action-btn" style="color: #2e7d32" @click="emit('status', 'Completed')">✅ Complete</button>
        </div>
      </div>

      <div class="drawer-footer" style="flex-shrink: 0">
        <button class="drawer-btn" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
