import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// ECharts imports
import { use } from 'echarts/core'
import { GaugeChart, PieChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'

// 注册 ECharts 组件（按需引入，减小打包体积）
use([GaugeChart, PieChart, CanvasRenderer])

import App from './App.vue'
import router from './router'
import './styles/tailwind.css'
import './styles/dashboard-dark.css'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 等待路由准备就绪后再挂载
router.isReady().then(() => {
  app.mount('#app')
})
