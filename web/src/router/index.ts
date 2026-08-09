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
      meta: { module: 'dashboard' }
    },
    {
      path: '/leads',
      name: 'leads',
      component: () => import('../views/LeadsView.vue'),
      meta: { module: 'crm' }
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
