<script setup lang="ts">
/**
 * SidebarFlyout (sb-flyout) — detailed tooltip panel on sidebar group
 * hover: group label + module list, mirrors the HTML PWA's group picker
 * intent with a richer flyout.
 */
import { useRouter } from 'vue-router'
import type { ShellGroup } from '@/shell/groups'
import { _t } from '@/i18n'

const props = defineProps<{ group: ShellGroup | null; x: number; y: number }>()
const router = useRouter()

function mods(g: ShellGroup) {
  return g.mods
}
</script>

<template>
  <div
    v-if="group"
    :style="{
      position: 'fixed',
      left: `${x}px`,
      top: `${y}px`,
      zIndex: 2000,
      width: '260px',
      background: '#fff',
      border: '1px solid #e0e0e0',
      borderLeft: '3px solid #2f80ed',
      borderRadius: '8px',
      boxShadow: '0 12px 32px rgba(0,0,0,.16)',
      padding: '10px 12px',
      animation: 'fadeIn .15s ease-out'
    }"
  >
    <div style="font-size: 12px; font-weight: 700; color: #0d1b2a">{{ _t(group.label) }}</div>
    <div style="font-size: 9px; color: #999; margin: 2px 0 8px">{{ group.mods.length }} modules</div>
    <div
      v-for="m in mods(group)"
      :key="m.id"
      style="
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 5px 8px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 11px;
        color: #333;
      "
      @mouseover="($event.currentTarget as HTMLElement).style.background = '#f0f4ff'"
      @mouseout="($event.currentTarget as HTMLElement).style.background = ''"
      @click="m.path && router.push(m.path)"
    >
      <span style="width: 6px; height: 6px; border-radius: 50%; background: #2f80ed"></span>
      <span style="flex: 1">{{ _t(m.label) }}</span>
      <span v-if="m.path" style="font-size: 8px; color: #2f80ed">›</span>
    </div>
  </div>
</template>
