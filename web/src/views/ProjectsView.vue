<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'
import { useDataStore } from '@/stores/data'
import DataTable from '@/components/DataTable.vue'
import ProjectDetailDrawer from '@/components/ProjectDetailDrawer.vue'
import type { TableAction, TableColumn, TableTab } from '@/components/DataTable.vue'
import type { Project } from '@/api/types'

const route = useRoute()
const data = useDataStore()
const detailProj = ref<Project | null>(null)

const tab = ref('all')
const detail = ref<Project | null>(null)

onMounted(async () => {
  data.loadProjects()
  if (route.query.pj === '1') {
    const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
    if (r.ok && r.data) {
      const arr = (r.data.collections.projects as any[]) ?? []
      if (arr.length) detailProj.value = arr[0] as unknown as Project
    }
  }
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

function progressColor(p: number): string {
  if (p >= 70) return '#2e7d32'
  if (p >= 40) return '#2f80ed'
  if (p > 0) return '#ff8f00'
  return '#e0e0e0'
}

const esc = (s: string) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c] as string))

const columns = computed<TableColumn<Project>[]>(() => [
  {
    key: 'name',
    label: 'Project',
    renderHtml: (p) =>
      `<div style="font-weight:500;color:#333">${esc(p.name)}</div><div style="font-size:9px;color:#888">${esc(p.id)}</div>`
  },
  { key: 'type', label: 'Type', renderHtml: (p) => `<span style="font-size:10px;color:#555">${esc(p.type)}</span>` },
  { key: 'location', label: 'Location', renderHtml: (p) => `<span style="font-size:10px;color:#555">${esc(p.location || '—')}</span>` },
  {
    key: 'progress',
    label: 'Progress',
    sortable: true,
    renderHtml: (p) =>
      `<div style="display:flex;align-items:center;gap:6px;min-width:90px">
        <div style="flex:1;height:4px;background:#e0e0e0;border-radius:2px;overflow:hidden">
          <div style="height:100%;border-radius:2px;background:${progressColor(p.progress)};width:${Math.min(100, p.progress)}%"></div>
        </div>
        <span style="font-size:9px;color:#888;font-weight:600">${p.progress}%</span>
      </div>`
  },
  { key: 'budget', label: 'Budget', renderHtml: (p) => `<span style="font-size:10px;color:#555">${esc(p.budget || '—')}</span>` },
  { key: 'manager', label: 'Manager', renderHtml: (p) => `<span style="font-size:10px;color:#555">${esc(p.manager || '—')}</span>` },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    renderHtml: (p) => {
      const s = statusStyle(p.status)
      return `<span class="pill" style="background:${s.bg};color:${s.fg}">${esc(p.status)}</span>`
    }
  }
])

const tabs = computed<TableTab[]>(() => [
  { id: 'all', label: 'All', count: data.projects.length },
  { id: 'progress', label: 'In Progress', count: data.projects.filter((p) => p.status === 'In Progress').length },
  { id: 'planning', label: 'Planning', count: data.projects.filter((p) => p.status === 'Planning').length },
  { id: 'completed', label: 'Completed', count: data.projects.filter((p) => p.status === 'Completed').length },
  { id: 'hold', label: 'On Hold', count: data.projects.filter((p) => p.status === 'On Hold').length }
])

const tabRows = computed(() => {
  if (tab.value === 'all') return data.projects
  const map: Record<string, string> = { progress: 'In Progress', planning: 'Planning', completed: 'Completed', hold: 'On Hold' }
  const st = map[tab.value]
  return st ? data.projects.filter((p) => p.status === st) : data.projects
})

function onTabChange(t: string) {
  tab.value = t
}

const actions = computed<TableAction[]>(() => [
  { label: 'View Details', icon: '🏗', onClick: (r) => (detailProj.value = r as unknown as Project) },
  { label: 'View Details', icon: '👁', onClick: (r) => (detail.value = r as unknown as Project) },
  { label: 'Open Acquisition', icon: '📋', onClick: (r) => (detail.value = r as unknown as Project) }
])
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px">
      <span class="page-title">Projects</span>
      <span class="page-subtitle">
        {{ data.projects.length }} projects · {{ data.projects.filter((p) => p.status === 'In Progress').length }} in progress
      </span>
    </div>

    <p v-if="data.error" style="font-size: 11px; color: #c62828; margin: 6px 0">{{ data.error }}</p>
    <p v-if="data.projectsLoading" style="font-size: 11px; color: #888; padding: 16px">Loading projects…</p>

    <DataTable
      v-else
      :columns="columns"
      :rows="tabRows"
      :tabs="tabs"
      :actions="actions"
      search-placeholder="Search projects…"
      @tab-change="onTabChange"
    />

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
    <ProjectDetailDrawer :project="detailProj" @close="detailProj = null" />
</template>
