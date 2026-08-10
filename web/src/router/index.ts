import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/DashboardView.vue'),
      meta: { module: 'dashboard', title: 'Dashboard' }
    },
    {
      path: '/leads',
      name: 'leads',
      component: () => import('../views/LeadsView.vue'),
      meta: { module: 'crm', title: 'CRM & Leads' }
    },
    {
      path: '/bookings',
      name: 'bookings',
      component: () => import('../views/BookingsView.vue'),
      meta: { module: 'bookings', title: 'Bookings' }
    },
    {
      path: '/dues',
      name: 'dues',
      component: () => import('../views/DuesView.vue'),
      meta: { module: 'dues', title: 'Dues & Collections' }
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('../views/ProjectsView.vue'),
      meta: { module: 'projects', title: 'Projects' }
    },
    {
      path: '/hr',
      name: 'hr',
      component: () => import('../views/EmployeesView.vue'),
      meta: { module: 'hr', title: 'HR & Employees' }
    },
    {
      path: '/stock',
      name: 'stock',
      component: () => import('../views/StockView.vue'),
      meta: { module: 'stock', title: 'Stock & Procurement' }
    },
    {
      path: '/finance',
      name: 'finance',
      component: () => import('../views/FinanceView.vue'),
      meta: { module: 'finance', title: 'Finance' }
    },
    {
      path: '/contractors',
      name: 'contractors',
      component: () => import('../views/ContractorsView.vue'),
      meta: { module: 'contractors', title: 'Contractors' }
    },
    {
      path: '/plots',
      name: 'plots',
      component: () => import('../views/PlotsView.vue'),
      meta: { module: 'plots', title: 'Plots' }
    },
    {
      path: '/approvals',
      name: 'approvals',
      component: () => import('../views/ApprovalsView.vue'),
      meta: { module: 'approvals', title: 'Financial Approvals' }
    },
    {
      path: '/tickets',
      name: 'tickets',
      component: () => import('../views/TicketsView.vue'),
      meta: { module: 'tickets', title: 'Ticketing & Issue' }
    },
    {
      path: '/handover',
      name: 'handover',
      component: () => import('../views/HandoverView.vue'),
      meta: { module: 'handover', title: 'Handover & Post-Sales' }
    },
    {
      path: '/work-orders',
      name: 'workorders',
      component: () => import('../views/WorkOrdersView.vue'),
      meta: { module: 'work-orders', title: 'Work Orders' }
    },
    {
      path: '/labor',
      name: 'labor',
      component: () => import('../views/LaborView.vue'),
      meta: { module: 'labor', title: 'Labor & Workforce' }
    },
    {
      path: '/equipment',
      name: 'equipment',
      component: () => import('../views/EquipmentView.vue'),
      meta: { module: 'equipment', title: 'Equipment & Machinery' }
    },
    {
      path: '/variations',
      name: 'variations',
      component: () => import('../views/VariationOrdersView.vue'),
      meta: { module: 'variations', title: 'Variation Orders' }
    },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

// Auth guard: everything except /login requires a session.
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (auth.authenticated && to.name === 'login') return { path: '/' }
    return true
  }
  if (!auth.authenticated) return { path: '/login', query: { redirect: to.fullPath } }
  // Role-based module guard
  const moduleId = to.meta.module as string | undefined
  if (moduleId && !auth.canAccess(moduleId)) return { path: '/' }
  return true
})

export default router
