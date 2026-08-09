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
