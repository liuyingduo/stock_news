<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginType = ref<'email' | 'phone' | 'wechat'>('email')
const email = ref('')
const password = ref('')
const formPhone = ref('')
const verificationCode = ref('')
const countdown = ref(0)
const loading = ref(false)

const handleLogin = async () => {
  if (!email.value || !password.value) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login({
      email: email.value,
      password: password.value
    })
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查邮箱和密码')
  } finally {
    loading.value = false
  }
}

const getVerificationCode = () => {
  if (!formPhone.value) {
    ElMessage.warning('请输入手机号')
    return
  }
  // 模拟发送由于后端暂无SMS服务
  ElMessage.success('验证码已发送 (演示模式: 123456)')
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const handlePhoneLogin = async () => {
  if (!formPhone.value || !verificationCode.value) {
    ElMessage.warning('请输入手机号和验证码')
    return
  }
  
  loading.value = true
  // 模拟手机登录延迟
  setTimeout(() => {
    loading.value = false
    if (verificationCode.value === '123456') {
      ElMessage.success('登录成功 (演示)')
      router.push('/')
    } else {
      ElMessage.error('验证码错误')
    }
  }, 1000)
}
</script>

<template>
  <div class="bg-surface-dark/40 backdrop-blur-xl rounded-2xl border border-white/5 p-8 shadow-2xl ring-1 ring-white/5">
    <div class="space-y-2 mb-8">
      <h3 class="text-2xl font-bold tracking-tight text-white">欢迎登录</h3>
    </div>
    
    <div class="border-b border-gray-700/50 mb-6">
      <nav aria-label="Tabs" class="-mb-px flex gap-6">
        <button @click="loginType = 'email'" 
          :class="[
            loginType === 'email' 
              ? 'border-logic-gold text-logic-gold font-bold' 
              : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600 font-medium',
            'whitespace-nowrap border-b-2 py-3 px-1 text-sm flex items-center gap-2 transition-colors tracking-wide'
          ]">
          <span class="material-symbols-outlined text-[18px]">mail</span>
          邮箱登录
        </button>
        <button @click="loginType = 'phone'" 
          :class="[
            loginType === 'phone' 
              ? 'border-logic-gold text-logic-gold font-bold' 
              : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600 font-medium',
            'whitespace-nowrap border-b-2 py-3 px-1 text-sm flex items-center gap-2 transition-colors tracking-wide'
          ]">
          <span class="material-symbols-outlined text-[18px]">smartphone</span>
          手机登录
        </button>
        <button @click="loginType = 'wechat'" 
          :class="[
            loginType === 'wechat' 
              ? 'border-logic-gold text-logic-gold font-bold' 
              : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600 font-medium',
            'whitespace-nowrap border-b-2 py-3 px-1 text-sm flex items-center gap-2 transition-colors tracking-wide'
          ]">
          <span class="material-symbols-outlined text-[18px]">qr_code_2</span>
          微信扫码
        </button>
      </nav>
    </div>
    
    <!-- Email Login Form -->
    <form v-if="loginType === 'email'" @submit.prevent="handleLogin" class="space-y-6">
      <div class="space-y-5">
        <div class="group">
          <label for="email" class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">账户邮箱</label>
          <div class="relative">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <span class="material-symbols-outlined text-gray-500 text-[20px]">alternate_email</span>
            </div>
            <input id="email" v-model="email" name="email" type="email" autocomplete="email" required 
              class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-3 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all tracking-wide font-medium" 
              placeholder="name@company.com">
          </div>
        </div>
        
        <div>
          <div class="flex items-center justify-between mb-2">
            <label for="password" class="block text-xs font-semibold uppercase tracking-wider text-gray-400">密码</label>
            <div class="text-xs">
              <a href="#" class="font-medium text-logic-gold hover:text-white transition-colors">忘记密码？</a>
            </div>
          </div>
          <div class="relative">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <span class="material-symbols-outlined text-gray-500 text-[20px]">lock</span>
            </div>
            <input id="password" v-model="password" name="password" type="password" autocomplete="current-password" required 
              class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-10 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all tracking-wide font-medium" 
              placeholder="••••••••">
            <button type="button" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-300 focus:outline-none">
              <span class="material-symbols-outlined text-[20px]">visibility_off</span>
            </button>
          </div>
        </div>
      </div>
      
      <div class="pt-2">
        <button type="submit" :disabled="loading" 
          class="group flex w-full justify-center items-center gap-2 rounded-lg bg-logic-gold px-3 py-3.5 text-sm font-bold text-gray-900 shadow-lg shadow-logic-gold/20 hover:bg-[#c4a030] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-logic-gold transition-all duration-200 transform hover:scale-[1.01] active:scale-[0.98] tracking-wide disabled:opacity-70 disabled:cursor-not-allowed">
          <span v-if="loading" class="animate-spin h-4 w-4 border-2 border-gray-900 border-t-transparent rounded-full mr-2"></span>
          {{ loading ? '登录中...' : '立即登录' }}
          <span v-if="!loading" class="material-symbols-outlined text-[18px] group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
        </button>
      </div>
    </form>

    <!-- Phone Login Form -->
    <form v-if="loginType === 'phone'" @submit.prevent="handlePhoneLogin" class="space-y-6">
      <div class="space-y-5">
        <div class="group">
          <label for="phone" class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">手机号码</label>
          <div class="relative flex w-full rounded-lg border border-gray-700/50 bg-[#0e1217] shadow-sm transition-all focus-within:border-logic-gold/50 focus-within:ring-1 focus-within:ring-logic-gold/50">
            <div class="relative flex items-center border-r border-gray-700/50">
              <select class="h-full bg-transparent border-none text-gray-300 text-sm focus:ring-0 py-3 pl-3 pr-7 cursor-pointer appearance-none outline-none rounded-l-lg hover:bg-white/5 transition-colors">
                <option class="bg-[#0e1217]" value="86">+86</option>
                <option class="bg-[#0e1217]" value="1">+1</option>
                <option class="bg-[#0e1217]" value="852">+852</option>
              </select>
              <div class="pointer-events-none absolute right-1 flex items-center">
                <span class="material-symbols-outlined text-gray-500 text-[16px]">expand_more</span>
              </div>
            </div>
            <input id="phone" v-model="formPhone" name="phone" type="tel" autocomplete="tel" required
              class="block w-full border-none bg-transparent py-3 px-4 text-white placeholder:text-gray-600 focus:ring-0 sm:text-sm rounded-r-lg" 
              placeholder="请输入手机号">
          </div>
        </div>

        <div class="group">
          <label for="code" class="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">验证码</label>
          <div class="relative">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <span class="material-symbols-outlined text-gray-500 text-[20px]">lock_clock</span>
            </div>
            <input id="code" v-model="verificationCode" name="code" type="text" autocomplete="one-time-code" required
              class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-32 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all" 
              placeholder="6位数字">
            <div class="absolute inset-y-0 right-0 flex items-center pr-2">
              <button type="button" @click="getVerificationCode" :disabled="countdown > 0"
                class="rounded px-3 py-1.5 text-xs font-bold text-logic-gold hover:text-white hover:bg-logic-gold/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                {{ countdown > 0 ? `${countdown}s 后重新获取` : '获取验证码' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="pt-2">
        <button type="submit" :disabled="loading" 
          class="group flex w-full justify-center items-center gap-2 rounded-lg bg-gradient-to-r from-logic-gold to-[#B38F1D] px-3 py-3.5 text-sm font-bold font-sans text-white shadow-lg shadow-logic-gold/20 hover:brightness-110 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-logic-gold transition-all duration-200 transform hover:scale-[1.01] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed">
          <span v-if="loading" class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></span>
          {{ loading ? '登录中...' : '立即登录' }}
          <span v-if="!loading" class="material-symbols-outlined text-[18px] group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
        </button>
      </div>
    </form>

    <!-- WeChat QR Code Login -->
    <div v-if="loginType === 'wechat'" class="flex flex-col items-center justify-center py-6 min-h-[300px]">
      <div class="relative p-1 rounded-xl bg-gradient-to-br from-white/10 to-white/0 border border-logic-gold/30 shadow-2xl backdrop-blur-sm">
        <div class="bg-white p-3 rounded-lg overflow-hidden relative group cursor-pointer">
          <img alt="Scan QR Code" class="w-48 h-48 opacity-95 block" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCo5KZghz7xv6yPyGHzZNZbC38m7QpLTlC7M5z7dolE828T7orIeyMUAgbmL-N5GLHGvZ7JSBahxLnFLddYi4DPyhoLGUjZsl65BLg4FExaiWay4Afz3FQPro5enes0UkgqFgmJ6MGkxBT_PeYa9lU5_ZaJ5TduQZbwD2wLiE9b0WRmiy7FTZWg1avGqvIj09HrTiT6V2pcDMZX7wJ2si3GxOW99ssun9N4eyrFyEQn4qtl-DblbSQ_CC-GoLIc0aLeuZy3TCf-ASoI" />
          <!-- Scanning Line Animation -->
          <div class="absolute left-0 right-0 top-1/2 h-[2px] bg-logic-gold shadow-[0_0_15px_2px_rgba(212,175,55,0.8)] z-10 opacity-90 animate-pulse"></div>
          <div class="absolute inset-0 bg-gradient-to-b from-transparent via-logic-gold/10 to-transparent pointer-events-none"></div>
        </div>
        <!-- Corner Decorations -->
        <div class="absolute -top-px -left-px w-5 h-5 border-t-2 border-l-2 border-logic-gold rounded-tl-sm shadow-glow-gold"></div>
        <div class="absolute -top-px -right-px w-5 h-5 border-t-2 border-r-2 border-logic-gold rounded-tr-sm shadow-glow-gold"></div>
        <div class="absolute -bottom-px -left-px w-5 h-5 border-b-2 border-l-2 border-logic-gold rounded-bl-sm shadow-glow-gold"></div>
        <div class="absolute -bottom-px -right-px w-5 h-5 border-b-2 border-r-2 border-logic-gold rounded-br-sm shadow-glow-gold"></div>
      </div>
      <p class="text-xs text-gray-400 mt-6 font-mono tracking-wide">
        请使用微信扫描二维码安全登录
      </p>
    </div>
    
    <div class="text-center pt-8 border-t border-gray-700/50 mt-6">
      <p class="text-sm text-gray-400">
        还没有账号？
        <RouterLink to="/register" class="font-bold text-logic-gold hover:text-white hover:underline ml-1 transition-colors">立即注册</RouterLink>
      </p>
      <div class="mt-8 flex justify-center gap-3 opacity-40 hover:opacity-80 transition-opacity duration-300">
        <div class="flex items-center gap-1.5 px-2 py-1 border border-gray-600 rounded text-[10px] font-bold text-gray-400 tracking-wider">
          <span class="material-symbols-outlined text-[14px]">security</span>
          SOC2 TYPE II
        </div>
        <div class="flex items-center gap-1.5 px-2 py-1 border border-gray-600 rounded text-[10px] font-bold text-gray-400 tracking-wider">
          <span class="material-symbols-outlined text-[14px]">lock</span>
          ISO 27001
        </div>
      </div>
    </div>
  </div>
</template>
