<script setup lang="ts">
/**
 * CsvImportView — CSV Import (System group): drag-drop / file picker
 * with module selector, sample format hint, progress simulation.
 */
import { computed, ref } from 'vue'
import { showToast } from '@/toast'

const modules = [
  { id: 'leads', label: 'CRM & Leads', sample: 'name,email,phone,source,status' },
  { id: 'bookings', label: 'Bookings', sample: 'id,client,property,unit,price,status' },
  { id: 'dues', label: 'Dues & Recovery', sample: 'customer,project,unit,totalPrice,paid,due' },
  { id: 'employees', label: 'HR & Employees', sample: 'name,designation,dept,phone,email,salary' },
  { id: 'inventory', label: 'Stock & Inventory', sample: 'item,category,qty,unit,price,status' },
  { id: 'projects', label: 'Projects', sample: 'name,type,location,status,progress,budget' }
]

const selected = ref('leads')
const fileName = ref('')
const dragging = ref(false)
const importing = ref(false)
const progress = ref(0)

const sample = computed(() => modules.find((m) => m.id === selected.value)?.sample ?? '')

function onFile(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) fileName.value = f.name
}

function startImport() {
  if (!fileName.value) {
    showToast('Choose a CSV file first', 'info')
    return
  }
  importing.value = true
  progress.value = 0
  const timer = setInterval(() => {
    progress.value += 10
    if (progress.value >= 100) {
      clearInterval(timer)
      importing.value = false
      showToast('✅ Import complete — ' + fileName.value, 'success')
      fileName.value = ''
    }
  }, 250)
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">CSV Import</span>
      <span class="page-subtitle">Bulk-import records from CSV files</span>
    </div>

    <div class="card" style="max-width: 560px">
      <div class="card-header"><h3>⬆ Upload CSV</h3></div>
      <div class="card-body">
        <!-- module selector -->
        <div style="margin-bottom: 12px">
          <label style="font-size: 10px; font-weight: 600; color: #555; display: block; margin-bottom: 4px">Target module</label>
          <select v-model="selected" style="width: 100%; padding: 7px 10px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 11px; outline: none">
            <option v-for="m in modules" :key="m.id" :value="m.id">{{ m.label }}</option>
          </select>
        </div>

        <!-- drop zone -->
        <label
          style="display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed #d0ddf0; border-radius: 10px; padding: 28px; cursor: pointer; transition: border-color .2s; background: #f8faff"
          :style="{ borderColor: dragging ? '#2f80ed' : '#d0ddf0' }"
          @dragover.prevent="dragging = true"
          @dragleave="dragging = false"
          @drop.prevent="dragging = false"
        >
          <span style="font-size: 30px">📄</span>
          <span style="font-size: 12px; font-weight: 600; color: #333; margin-top: 8px">{{ fileName || 'Drop your CSV here or click to browse' }}</span>
          <span style="font-size: 10px; color: #888; margin-top: 4px">.csv up to 5 MB</span>
          <input type="file" accept=".csv" style="display: none" @change="onFile" />
        </label>

        <!-- sample format -->
        <div style="margin-top: 10px; background: #f5f5f5; border-radius: 6px; padding: 8px 10px; font-size: 10px; color: #666">
          <span style="font-weight: 600; color: #555">Sample format:</span>
          <code style="display: block; margin-top: 3px; font-size: 9px; color: #2f80ed">{{ sample }}</code>
        </div>

        <!-- progress -->
        <div v-if="importing" style="margin-top: 12px">
          <div style="height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden">
            <div :style="{ width: progress + '%', background: '#2f80ed', height: '100%', transition: 'width .2s' }"></div>
          </div>
          <div style="font-size: 9px; color: #888; margin-top: 4px">Importing… {{ progress }}%</div>
        </div>

        <div style="margin-top: 14px; display: flex; gap: 8px">
          <button class="action-btn primary" :disabled="importing" @click="startImport">⬆ Start Import</button>
        </div>
      </div>
    </div>
  </div>
</template>
