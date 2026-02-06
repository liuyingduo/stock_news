<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 移除 username，添加 phone
// 用户名将在后端自动生成
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const phone = ref('')
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const handleRegister = async () => {
  if (!email.value || !password.value) {
    ElMessage.warning('请填写完整的注册信息')
    return
  }

  if (password.value !== confirmPassword.value) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  if (password.value.length < 6) {
    ElMessage.warning('密码长度至少为6位')
    return
  }

  loading.value = true
  try {
    await register({
      // username: 不传，由后端自动从邮箱生成
      email: email.value,
      password: password.value,
      phone: phone.value || undefined // 如果为空则不传或传undefined
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-surface-dark/40 backdrop-blur-xl rounded-2xl border border-white/5 p-8 shadow-2xl ring-1 ring-white/5">
    <div class="mb-8">
      <h3 class="text-2xl font-bold font-sans tracking-tight text-white">创建账号</h3>
    </div>
    
    <form @submit.prevent="handleRegister" class="space-y-5">
      <div class="group">
        <label for="email" class="block text-xs font-medium uppercase tracking-wider text-gray-400 mb-2 font-mono">电子邮箱</label>
        <div class="relative">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <span class="material-symbols-outlined text-gray-500 text-[20px]">alternate_email</span>
          </div>
          <input id="email" v-model="email" name="email" type="email" autocomplete="email" required 
            class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-3 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all font-mono" 
            placeholder="name@company.com">
        </div>
      </div>
      
      <div>
        <div class="flex items-center justify-between mb-2">
          <label for="password" class="block text-xs font-medium uppercase tracking-wider text-gray-400 font-mono">设置密码</label>
        </div>
        <div class="relative">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <span class="material-symbols-outlined text-gray-500 text-[20px]">lock</span>
          </div>
          <input id="password" v-model="password" name="password" :type="showPassword ? 'text' : 'password'" autocomplete="new-password" required 
            class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-10 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all font-mono" 
            placeholder="••••••••">
          <button type="button" @click="showPassword = !showPassword" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-300 focus:outline-none">
            <span class="material-symbols-outlined text-[20px]">{{ showPassword ? 'visibility' : 'visibility_off' }}</span>
          </button>
        </div>
      </div>

      <div>
        <div class="flex items-center justify-between mb-2">
          <label for="confirmPassword" class="block text-xs font-medium uppercase tracking-wider text-gray-400 font-mono">确认密码</label>
        </div>
        <div class="relative">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <span class="material-symbols-outlined text-gray-500 text-[20px]">lock_reset</span>
          </div>
          <input id="confirmPassword" v-model="confirmPassword" name="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" autocomplete="new-password" required 
            class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-10 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all font-mono" 
            placeholder="••••••••">
          <button type="button" @click="showConfirmPassword = !showConfirmPassword" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-300 focus:outline-none">
            <span class="material-symbols-outlined text-[20px]">{{ showConfirmPassword ? 'visibility' : 'visibility_off' }}</span>
          </button>
        </div>
      </div>

      <div class="group">
        <label for="phone" class="block text-xs font-medium uppercase tracking-wider text-gray-400 mb-2 font-mono">手机号码</label>
        <div class="relative">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <span class="material-symbols-outlined text-gray-500 text-[20px]">smartphone</span>
          </div>
          <input id="phone" v-model="phone" name="phone" type="tel" autocomplete="tel" 
            class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-3 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all font-mono" 
            placeholder="138 0000 0000">
        </div>
      </div>
      
      <div class="pt-4">
        <button type="submit" :disabled="loading" 
          class="group flex w-full justify-center items-center gap-2 rounded-lg bg-gradient-to-b from-[#F2D06B] to-[#D4AF37] px-3 py-3.5 text-sm font-bold font-sans text-[#151921] shadow-lg shadow-logic-gold/20 hover:brightness-110 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-logic-gold transition-all duration-200 transform hover:scale-[1.01] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed">
          <span v-if="loading" class="animate-spin h-4 w-4 border-2 border-[#151921] border-t-transparent rounded-full mr-2"></span>
          {{ loading ? '注册中...' : '立即注册' }}
          <span v-if="!loading" class="material-symbols-outlined text-[18px] group-hover:translate-x-0.5 transition-transform text-[#151921]">arrow_forward</span>
        </button>
      </div>
    </form>
    
    <div class="text-center pt-8 border-t border-gray-700/50 mt-6">
      <p class="text-sm text-gray-400">
        已有账号？
        <RouterLink to="/login" class="font-bold text-logic-gold hover:text-[#F2D06B] hover:underline ml-1 transition-colors">立即登录</RouterLink>
      </p>
      <div class="mt-8 flex justify-center gap-3 opacity-40 hover:opacity-80 transition-opacity duration-300">
        <div class="flex items-center gap-1.5 px-2 py-1 border border-gray-600 rounded text-[10px] font-bold text-gray-400 font-mono">
          <span class="material-symbols-outlined text-[14px]">security</span>
          SOC2 TYPE II
        </div>
        <div class="flex items-center gap-1.5 px-2 py-1 border border-gray-600 rounded text-[10px] font-bold text-gray-400 font-mono">
          <span class="material-symbols-outlined text-[14px]">lock</span>
          ISO 27001
        </div>
      </div>
    </div>
  </div>
</template>
