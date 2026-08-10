<script setup lang="ts">
/**
 * FormModal — drawer form helper mirroring the HTML PWA askFields():
 * a field list renders as a drawer with Save/Cancel; emits the values.
 */
import { reactive, watch } from 'vue'

export interface FormField {
  name: string
  label: string
  type?: 'text' | 'number' | 'select' | 'date' | 'textarea' | 'email'
  options?: string[]
  required?: boolean
  placeholder?: string
}

const props = defineProps<{
  open: boolean
  title: string
  fields: FormField[]
  initial?: Record<string, string>
}>()

const emit = defineEmits<{ (e: 'close'): void; (e: 'save', values: Record<string, string>): void }>()

const values = reactive<Record<string, string>>({})

watch(
  () => [props.open, props.fields, props.initial],
  () => {
    for (const f of props.fields) values[f.name] = props.initial?.[f.name] ?? ''
  },
  { immediate: true }
)

function save() {
  emit('save', { ...values })
  emit('close')
}
</script>

<template>
  <div v-if="open" class="drawer-overlay active" @click.self="emit('close')">
    <div class="drawer-sheet" style="width: 460px">
      <div class="drawer-header">
        <h3>{{ title }}</h3>
        <div class="drawer-close" @click="emit('close')">✕</div>
      </div>
      <div class="drawer-body">
        <div v-for="f in fields" :key="f.name" class="form-group" style="margin-bottom: 12px">
          <label class="form-label">{{ f.label }}{{ f.required ? ' *' : '' }}</label>
          <select v-if="f.type === 'select'" v-model="values[f.name]" class="form-input">
            <option value="" disabled>— select —</option>
            <option v-for="o in f.options ?? []" :key="o" :value="o">{{ o }}</option>
          </select>
          <textarea v-else-if="f.type === 'textarea'" v-model="values[f.name]" class="form-input" rows="3" :placeholder="f.placeholder ?? ''"></textarea>
          <input
            v-else
            v-model="values[f.name]"
            :type="f.type === 'number' ? 'number' : f.type === 'date' ? 'date' : f.type === 'email' ? 'email' : 'text'"
            class="form-input"
            :placeholder="f.placeholder ?? ''"
          />
        </div>
      </div>
      <div class="drawer-footer">
        <button class="drawer-btn" @click="emit('close')">Cancel</button>
        <button class="drawer-btn primary" @click="save">Save</button>
      </div>
    </div>
  </div>
</template>
