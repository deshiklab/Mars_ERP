<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDataStore } from '@/stores/data'
import type { Project } from '@/api/types'

const data = useDataStore()
const statusFilter = ref('')
const detail = ref<Project | null>(null)

onMounted(() => {
  data.loadProjects()
})

const statuses = ['In Progress', 'Planning', 'Completed', 'On Hold']

function statusStyle(status: string): { bg: string; fg: string } {
  const map: Record<string, [string, string]> = {
    'In Progress': ['#e8f5e9', '#2e7d32'],
    Planning: ['#f0f4ff', '#2f80ed'],
    Completed: ['#e3f2fd', '#1565c0'],
    'On Hold': ['#fff3e0', '#e65100']
  }
  const [bg, fg] = map[status] ?? ['#f0f0f0', '#555']
  return { bg, fg }
}

const filtered = computed(() => {
  if (!statusFilter.value) return data.projects
  return data.projects.filter((p) => p.status === statusFilter.value)
})

function progressColor(p: number): string {
  if (p >= 70) return '#2e7d32'
  if (p >= 40) return '#2f80ed'
  if (p > 0) return '#ff8f00'
  return '#e0e0e0'
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Projects</span>
      <span class="page-subtitle">{{ data.projects.length }} projects · {{ data.projects.filter((p) => p.status === 'In Progress').length }} in progress</span>
      <div style="margin-left: auto">
        <select
          v-model="statusFilter"
          style="padding: 3px 8px; font-size: 10px; border: 1px solid #e0e0e0; border-radius: 6px; outline: none; color: #555; background: #fff"
        >
          <option value="">All statuses</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.projectsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading projects…</p>

    <div v-else class="card">
      <div class="table-wrap">
        <table class="rem-table">
          <thead>
            <tr>
              <th>Project</th>
              <th>Type</th>
              <th>Location</th>
              <th>Progress</th>
              <th>Budget</th>
              <th>Manager</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in filtered" :key="p.id" style="cursor: pointer" @click="detail = p">
              <td>
                <div style="font-weight: 500; color: #333">{{ p.name }}</div>
                <div style="font-size: 9px; color: #888">{{ p.id }}</div>
              </td>
              <td style="font-size: 10px; color: #555">{{ p.type }}</td>
              <td style="font-size: 10px; color: #555">{{ p.location || '—' }}</td>
              <td style="min-width: 90px">
                <div style="display: flex; align-items: center; gap: 6px">
                  <div style="flex: 1; height: 4px; background: #e0e0e0; border-radius: 2px; overflow: hidden">
                    <div style="height: 100%; border-radius: 2px; transition: width 0.3s" :style="{ width: `${Math.min(100, p.progress)}%`, background: progressColor(p.progress) }"></div>
                  </div>
                  <span style="font-size: 9px; color: #888; font-weight: 600">{{ p.progress }}%</span>
                </div>
              </td>
              <td style="font-size: 10px; color: #555">{{ p.budget || '—' }}</td>
              <td style="font-size: 10px; color: #555">{{ p.manager || '—' }}</td>
              <td>
                <span class="pill" :style="{ background: statusStyle(p.status).bg, color: statusStyle(p.status).fg }">
                  {{ p.status }}
                </span>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="7" style="text-align: center; color: #888; padding: 20px; font-size: 11px">No projects found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Project detail drawer -->
    <div v-if="detail" class="drawer-overlay active" @click.self="detail = null">
      <div class="drawer-sheet">
        <div class="drawer-header">
          <h3>{{ detail.name }}</h3>
          <div class="drawer-close" @click="detail = null">✕</div>
        </div>
        <div class="drawer-body">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; font-size: 11px">
            <div><span style="color: #888">Type:</span> <b>{{ detail.type }}</b></div>
            <div><span style="color: #888">Status:</span>
              <span class="pill" :style="{ background: statusStyle(detail.status).bg, color: statusStyle(detail.status).fg }">{{ detail.status }}</span>
            </div>
            <div><span style="color: #888">Location:</span> {{ detail.location || '—' }}</div>
            <div><span style="color: #888">Phase:</span> {{ detail.phase || '—' }}</div>
            <div><span style="color: #888">Budget:</span> <b>{{ detail.budget || '—' }}</b></div>
            <div><span style="color: #888">Plots:</span> {{ detail.plots ?? 0 }}</div>
            <div><span style="color: #888">Start:</span> {{ detail.start || '—' }}</div>
            <div><span style="color: #888">End:</span> {{ detail.end || '—' }}</div>
          </div>

          <h4 style="font-size: 12px; color: #333; margin: 14px 0 8px">Progress</h4>
          <div style="display: flex; align-items: center; gap: 8px">
            <div style="flex: 1; height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden">
              <div style="height: 100%; border-radius: 3px" :style="{ width: `${Math.min(100, detail.progress)}%`, background: progressColor(detail.progress) }"></div>
            </div>
            <b style="font-size: 12px">{{ detail.progress }}%</b>
          </div>

          <p v-if="detail.desc" style="font-size: 11px; color: #555; margin-top: 12px; line-height: 1.6">{{ detail.desc }}</p>
        </div>
        <div class="drawer-footer">
          <button class="drawer-btn" @click="detail = null">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>
