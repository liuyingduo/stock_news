import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/sectors',
    name: 'Sectors',
    component: () => import('../views/Sectors.vue'),
  },
  {
    path: '/ecosignal',
    name: 'EcoSignal',
    component: () => import('../views/EcoSignal.vue'),
    meta: { title: '智金通 EcoSignal' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
