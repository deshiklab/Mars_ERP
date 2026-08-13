<script setup lang="ts">
/**
 * PermissionsView — user & role matrix (System group):
 * users with role chips + permission groups grid.
 */
import { computed, onMounted, ref } from 'vue'
import { api } from '@/api/client'
import { showToast } from '@/toast'

const users = ref<any[]>([])

const roleBusy = ref(false)
async function toggleRole(u: any, role: string, has: boolean) {
  if (roleBusy.value) return
  roleBusy.value = true
  try {
    const res = await api.call('user_role_update', { user: u.email ?? u.id, role, add: has ? 0 : 1 })
    if (res.ok) {
      if (has) u.roles = (u.roles ?? []).filter((r: string) => r !== role)
      else u.roles = [...(u.roles ?? []), role]
      showToast(has ? 'Role removed' : 'Role granted')
    } else showToast('Update failed — ' + (res.error || 'server error'))
  } finally { roleBusy.value = false }
}
const loading = ref(true)

onMounted(async () => {
  const r = await api.call<{ collections: Record<string, unknown> }>('bootstrap')
  if (r.ok && r.data) {
    users.value = (r.data.collections.users as any[]) ?? []
  }
  loading.value = false
})

const permGroups = [
  { name: 'Executive', perms: ['View Dashboard', 'View Analytics', 'View Reports'] },
  { name: 'Sales & CRM', perms: ['View Leads', 'Edit Leads', 'View Customers', 'View Proposals'] },
  { name: 'Bookings', perms: ['View Bookings', 'Edit Bookings', 'View Dues', 'View Handover'] },
  { name: 'Projects', perms: ['View Projects', 'Edit Projects', 'View Plots', 'View Units'] },
  { name: 'Finance', perms: ['View Invoices', 'Record Payments', 'View Ledger', 'Approve'] },
  { name: 'HR & Admin', perms: ['View Employees', 'View Payroll', 'Manage Attendance', 'Manage Users'] }
]

function roleColor(role: string): string {
  const map: Record<string, string> = { 'Super Admin': '#c62828', 'Sales Agent': '#2f80ed', Customer: '#2e7d32' }
  return map[role] ?? '#555'
}
</script>

<template>
  <div class="fade-in">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
      <span class="page-title">Permissions</span>
      <span class="page-subtitle">User roles · permission matrix</span>
    </div>

    <p v-if="loading" style="font-size: 11px; color: #888; padding: 16px">Loading users…</p>

    <template v-else>
      <!-- users -->
      <div class="card" style="margin-bottom: 10px">
        <div class="card-header"><h3>👥 Users & Roles</h3></div>
        <div class="card-body">
          <div v-for="u in users" :key="u.email" style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f5f5f5">
            <span style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #2f80ed, #56ccf2); color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700">{{ u.initials || u.name.slice(0, 2).toUpperCase() }}</span>
            <div style="flex: 1">
              <div style="font-size: 12px; font-weight: 600; color: #333">{{ u.name }}</div>
              <div style="font-size: 9px; color: #888">{{ u.email }} · {{ u.dept }}</div>
            </div>
            <span class="pill" :style="{ background: roleColor(u.role) + '22', color: roleColor(u.role) }">{{ u.role }}</span>
            <span class="pill" :style="{ background: u.status === 'Active' ? '#e8f5e9' : '#f5f5f5', color: u.status === 'Active' ? '#2e7d32' : '#888' }">{{ u.status }}</span>
          </div>
          <div v-if="!users.length" style="text-align: center; padding: 16px; color: #999; font-size: 11px">No users.</div>
        </div>
      </div>

      <!-- permission matrix -->
      <div class="card">
        <div class="card-header"><h3>🔐 Permission Groups</h3></div>
        <div class="card-body" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 8px">
          <div v-for="g in permGroups" :key="g.name" style="border: 1px solid #e8e8e8; border-radius: 8px; padding: 10px">
            <div style="font-size: 11px; font-weight: 700; color: #2f80ed; margin-bottom: 6px">{{ g.name }}</div>
            <div v-for="p in g.perms" :key="p" style="display: flex; align-items: center; gap: 6px; padding: 3px 0; font-size: 10px; color: #555">
              <span style="color: #2e7d32; font-size: 10px">✓</span>{{ p }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
