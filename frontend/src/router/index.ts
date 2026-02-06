import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    layout?: 'default' | 'auth'
    requiresAuth?: boolean
    guest?: boolean
    title?: string
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/opportunity-radar',
    name: 'OpportunityRadar',
    component: () => import('../views/OpportunityRadar.vue'),
    meta: { layout: 'default', title: '机会雷达', requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { layout: 'default', title: '个人信息', requiresAuth: true },
  },
  {
    path: '/pricing-benefits',
    name: 'PricingBenefits',
    component: () => import('../views/PricingBenefits.vue'),
    meta: { layout: 'default', title: '定价与权益', requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { layout: 'auth', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { layout: 'auth', guest: true }
  },
  {
    path: '/events/:id',
    name: 'EventDetail',
    component: () => import('../views/EventDetail.vue'),
    meta: { layout: 'default', title: '事件详情', requiresAuth: true },
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch {
      authStore.logout()
    }
  }

  const isAuthenticated = !!authStore.token && !!authStore.user

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  if (to.meta.guest && isAuthenticated) {
    next('/')
    return
  }

  next()
})

export default router
