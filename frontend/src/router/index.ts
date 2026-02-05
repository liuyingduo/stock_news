import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/events/:id',
    name: 'EventDetail',
    component: () => import('../views/EventDetail.vue'),
    meta: { title: '事件详情', requiresAuth: true },
  },
  {
    path: '/sectors',
    name: 'Sectors',
    component: () => import('../views/Sectors.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ecosignal',
    name: 'EcoSignal',
    component: () => import('../views/EcoSignal.vue'),
    meta: { title: '智金通 EcoSignal', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 初始化认证状态
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      // Token无效或过期
    }
  }

  // 需要登录的页面
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
    return
  }

  // 已登录状态下访问游客页面（登录/注册），重定向到首页
  if (to.meta.guest && authStore.isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
