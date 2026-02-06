import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 扩展路由 Meta 类型
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
  },
  {
    path: '/sectors',
    name: 'Sectors',
    component: () => import('../views/Sectors.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/ecosignal',
    name: 'EcoSignal',
    component: () => import('../views/EcoSignal.vue'),
    meta: { layout: 'default', title: '智金通 EcoSignal', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // 初始化认证状态：有 token 但没有 user 时尝试获取用户信息
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch {
      // Token 无效或过期，清理状态
      authStore.logout()
    }
  }

  // 重新评估登录状态（fetchUser 完成后）
  const isAuthenticated = !!authStore.token && !!authStore.user

  // 需要登录的页面
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  // 已登录状态下访问游客页面（登录/注册），重定向到首页
  if (to.meta.guest && isAuthenticated) {
    next('/')
    return
  }

  next()
})

export default router
