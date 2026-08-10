<script setup lang="ts">
/**
 * ShortcutsModal — the HTML PWA ⌨ Keyboard Shortcuts help.
 */
defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const shortcuts = [
  ['⌘K / Ctrl+K', 'Open global search'],
  ['Ctrl+Shift+K', 'Open command palette'],
  ['g then c', 'Go to Customers'],
  ['g then b', 'Go to Bookings'],
  ['g then p', 'Go to Flats & Units'],
  ['g then f', 'Go to Finance'],
  ['g then l', 'Go to CRM & Leads'],
  ['g then h', 'Go to HR'],
  ['n', 'New item for current module'],
  ['?', 'Show this help'],
  ['Esc', 'Close palette / tray / menus'],
  ['Alt+N', 'Quick add']
]
</script>

<template>
  <div v-if="open" class="drawer-overlay active" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 420px">
      <div class="drawer-header">
        <h3>⌨ Keyboard Shortcuts</h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>
      <div class="drawer-body" style="font-size: 11px; color: #666; line-height: 1.9">
        <div
          v-for="s in shortcuts"
          :key="s[0]"
          style="display: flex; justify-content: space-between; gap: 12px; padding: 4px 2px; border-bottom: 1px dashed #eee"
        >
          <span style="font-weight: 600; color: #2f80ed; white-space: nowrap">{{ s[0] }}</span>
          <span style="text-align: right; color: #555">{{ s[1] }}</span>
        </div>
      </div>
      <div class="drawer-footer">
        <button class="drawer-btn primary" @click="emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>
