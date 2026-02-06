<template>
  <div class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-white antialiased overflow-hidden min-h-screen flex flex-col font-body text-rendering-optimize">
    <AppHeader />

    <main class="flex-1 bg-background-dark p-6">
      <div class="max-w-3xl mx-auto">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h1 class="text-white text-2xl font-bold font-display tracking-tight">个人信息</h1>
            <p class="text-gray-500 text-sm mt-1">在这里更新你的账号资料</p>
          </div>
          <button
            class="px-4 py-2 rounded-lg border border-border-dark text-gray-300 hover:text-white hover:border-white/20 transition-colors"
            @click="handleLogout"
          >
            退出登录
          </button>
        </div>

        <div class="bg-[#151a23] border border-border-dark rounded-xl p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <label class="flex flex-col gap-2">
              <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">用户名</span>
              <input
                v-model="form.username"
                class="h-10 rounded-lg bg-[#0f1115] border border-border-dark px-3 text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="请输入用户名"
              />
            </label>

            <label class="flex flex-col gap-2">
              <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">邮箱</span>
              <input
                v-model="form.email"
                class="h-10 rounded-lg bg-[#0f1115] border border-border-dark px-3 text-gray-500 text-sm"
                disabled
              />
            </label>

            <label class="flex flex-col gap-2">
              <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">手机号</span>
              <input
                v-model="form.phone"
                class="h-10 rounded-lg bg-[#0f1115] border border-border-dark px-3 text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="选填"
              />
            </label>

            <div class="flex flex-col gap-2">
              <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">注册时间</span>
              <div class="h-10 flex items-center rounded-lg bg-[#0f1115] border border-border-dark px-3 text-gray-400 text-sm">
                {{ createdAtLabel }}
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 mt-8">
            <button
              class="px-4 py-2 rounded-lg border border-border-dark text-gray-300 hover:text-white hover:border-white/20 transition-colors"
              :disabled="saving"
              @click="resetForm"
            >
              取消
            </button>
            <button
              class="px-4 py-2 rounded-lg bg-primary text-white hover:opacity-90 transition-colors"
              :disabled="saving"
              @click="handleSave"
            >
              {{ saving ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const saving = ref(false)

const form = ref({
  username: '',
  email: '',
  phone: '',
})

const createdAtLabel = computed(() => {
  const createdAt = authStore.user?.created_at
  if (!createdAt) return '--'
  const date = new Date(createdAt)
  if (Number.isNaN(date.getTime())) return createdAt
  return date.toLocaleString()
})

const syncForm = () => {
  const user = authStore.user
  if (!user) return
  form.value.username = user.username || ''
  form.value.email = user.email || ''
  form.value.phone = user.phone || ''
}

const handleSave = async () => {
  saving.value = true
  try {
    await authStore.updateProfile({
      username: form.value.username || undefined,
      phone: form.value.phone || undefined,
    })
    syncForm()
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  syncForm()
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

watch(
  () => authStore.user,
  () => syncForm(),
  { immediate: true }
)

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchUser()
  }
})
</script>
