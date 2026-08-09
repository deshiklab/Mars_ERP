<script setup lang="ts">
/**
 * KanbanBoard — mirrors the HTML PWA renderCRMKanban:
 * status columns with colored headers + counts, cards with
 * edit/delete/advance, drag between columns.
 */
import { ref } from 'vue'

export interface KanbanColumn {
  id: string
  label: string
  bg: string
  fg: string
  next?: string
}

export interface KanbanCard {
  id: string
  title: string
  subtitle?: string
  meta?: string
  pills?: { text: string; color: string; bg?: string }[]
  status: string
}

const props = withDefaults(
  defineProps<{
    columns: KanbanColumn[]
    cards: KanbanCard[]
    minColWidth?: number
  }>(),
  { minColWidth: 170 }
)

const emit = defineEmits<{
  (e: 'move', cardId: string, status: string): void
  (e: 'open', card: KanbanCard): void
  (e: 'edit', card: KanbanCard): void
  (e: 'delete', card: KanbanCard): void
  (e: 'advance', card: KanbanCard): void
}>()

const dragged = ref<string | null>(null)

function cardsFor(colId: string): KanbanCard[] {
  return props.cards.filter((c) => c.status === colId)
}

function onDragStart(card: KanbanCard) {
  dragged.value = card.id
}

function onDragEnd() {
  dragged.value = null
}

function onDrop(status: string) {
  if (dragged.value) emit('move', dragged.value, status)
  dragged.value = null
}

function pillStyle(p: { text: string; color: string; bg?: string }) {
  return {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '2px',
    padding: '0 5px',
    borderRadius: '6px',
    fontSize: '7px',
    fontWeight: 600,
    background: p.bg ?? `${p.color}22`,
    color: p.color,
    border: `1px solid ${p.color}55`
  }
}
</script>

<template>
  <div style="display: flex; gap: 8px; overflow-x: auto; flex: 1; min-height: 300px">
    <div
      v-for="col in columns"
      :key="col.id"
      class="kanban-col"
      :style="{ minWidth: `${minColWidth}px`, flex: '1' }"
      @dragover.prevent
      @drop="onDrop(col.id)"
    >
      <div
        style="
          padding: 5px 8px;
          font-size: 9px;
          font-weight: 600;
          color: v-bind('col.fg');
          background: v-bind('col.bg');
          border-radius: 6px 6px 0 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        "
      >
        <span>{{ col.label }}</span>
        <span
          style="
            background: v-bind('col.fg');
            color: #fff;
            border-radius: 10px;
            padding: 0 6px;
            font-size: 9px;
          "
        >{{ cardsFor(col.id).length }}</span>
      </div>
      <div style="flex: 1; overflow-y: auto; padding: 4px">
        <template v-if="cardsFor(col.id).length">
          <div
            v-for="card in cardsFor(col.id)"
            :key="card.id"
            class="kanban-card"
            draggable="true"
            :style="{ marginBottom: '4px', cursor: 'pointer', position: 'relative' }"
            @dragstart="onDragStart(card)"
            @dragend="onDragEnd"
            @click="emit('open', card)"
          >
            <div style="display: flex; justify-content: space-between; align-items: flex-start">
              <div style="font-size: 10px; font-weight: 600">{{ card.title }}</div>
              <div style="display: flex; gap: 2px">
                <span
                  style="color: #2f80ed; cursor: pointer; font-size: 8px"
                  @click.stop="emit('edit', card)"
                >✎</span>
                <span
                  style="color: #e53935; cursor: pointer; font-size: 8px"
                  @click.stop="emit('delete', card)"
                >✕</span>
              </div>
            </div>
            <div v-if="card.subtitle" style="font-size: 9px; color: #888; margin-top: 2px">{{ card.subtitle }}</div>
            <div v-if="card.meta" style="font-size: 9px; color: #888">{{ card.meta }}</div>
            <div style="margin-top: 3px; display: flex; gap: 2px; align-items: center; flex-wrap: wrap">
              <span v-for="(p, i) in card.pills ?? []" :key="i" :style="pillStyle(p)">{{ p.text }}</span>
              <span
                v-if="col.next"
                style="
                  color: #2e7d32;
                  cursor: pointer;
                  font-size: 8px;
                  font-weight: 600;
                  padding: 1px 4px;
                  background: #e8f5e9;
                  border-radius: 3px;
                "
                @click.stop="emit('advance', card)"
              >▶</span>
            </div>
          </div>
        </template>
        <div v-else style="padding: 12px; text-align: center; color: #bbb; font-size: 9px">No leads here</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kanban-col {
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
}

.kanban-card {
  padding: 7px 9px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-left: 3px solid #b0bec5;
  border-radius: 4px;
  transition: box-shadow 0.12s, transform 0.12s;
}

.kanban-card:hover {
  border-color: #cfd8dc;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}
</style>
