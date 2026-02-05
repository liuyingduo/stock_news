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
      // username: 不传，由后端生成
      username: '', 
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
  <div class="bg-background-dark font-mono text-gray-200 h-screen w-full overflow-hidden flex flex-col lg:flex-row antialiased selection:bg-logic-gold selection:text-white">
    <!-- Left Banner -->
    <div class="relative hidden w-full lg:flex lg:w-5/12 xl:w-1/2 flex-col justify-between p-12 bg-black overflow-hidden group border-r border-white/5">
      <div class="absolute inset-0 z-0 opacity-40 transition-transform duration-[40s] ease-linear group-hover:scale-105" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuB05i95VsA062FksCvGBuQjSCxem40pr1U6I5abihPl0iz_Xg8i2grj8dTZbKgZnPc-GxWdGTcD8u9vXLhoGu31LfQOvMhu-U-BOY5FGIXzmzOBiAenFOnO8UB5eb4wXD138KvY3IPNbbvHk6asT6y99KyvEUn-DQRcpvDoZA35qzpwhOPMOdX2F6Cp6D910elKQiYSIFczLEvV_PfFvdJABUw9HlqFFPmZKLOyU0CZdo5H9YYgi7K4HVoHhHxCm9mbN4LkVhhWWiII'); background-size: cover; background-position: center;">
      </div>
      <div class="absolute inset-0 z-10 bg-gradient-to-b from-black/60 via-black/20 to-black/90"></div>
      <div class="absolute inset-0 z-10 bg-gradient-to-r from-black/80 via-transparent to-transparent"></div>
      
      <div class="relative z-20 flex flex-col h-full justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-full bg-logic-gold/10 backdrop-blur-md border border-logic-gold/40 shadow-glow-gold">
            <span class="material-symbols-outlined text-logic-gold text-2xl">public</span>
          </div>
          <h1 class="text-2xl font-bold font-sans tracking-tight text-white">万古经纬</h1>
        </div>
        
        <div class="flex flex-col gap-8 max-w-xl">
          <div class="inline-flex w-fit items-center gap-2 rounded-full border border-logic-gold/20 bg-logic-gold/5 px-3 py-1 text-xs font-medium text-logic-gold backdrop-blur-sm tracking-wide">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-logic-gold opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-logic-gold"></span>
            </span>
            AI金融情绪监测系统在线
          </div>
          
          <h2 class="text-4xl font-black font-sans leading-[1.2] tracking-wide text-white xl:text-5xl drop-shadow-xl">
            经古往今来 <br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-white via-logic-gold to-white text-glow-gold">纬南北东西</span>
          </h2>
          
          <p class="text-lg text-gray-400 font-light leading-relaxed border-l-2 border-logic-gold/60 pl-5">
            让每一条资讯都有逻辑经纬
          </p>
          
          <div class="mt-4 grid grid-cols-3 gap-8 pt-8 border-t border-white/10">
            <div>
              <p class="text-2xl font-bold text-white tracking-tight font-mono">2.4M+</p>
              <p class="text-[10px] font-medium uppercase tracking-wider text-gray-500 mt-1">每日信号处理</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-white tracking-tight font-mono">150<span class="text-sm align-top text-gray-400">ms</span></p>
              <p class="text-[10px] font-medium uppercase tracking-wider text-gray-500 mt-1">NLP解析延迟</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-white tracking-tight font-mono">99.9%</p>
              <p class="text-[10px] font-medium uppercase tracking-wider text-gray-500 mt-1">系统在线率</p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-between items-end text-xs text-gray-500 font-medium">
          <p>© 2024 万古经纬</p>
          <div class="flex gap-6">
            <a class="hover:text-logic-gold transition-colors" href="#">隐私政策</a>
            <a class="hover:text-logic-gold transition-colors" href="#">服务条款</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Register Form -->
    <div class="flex flex-1 flex-col justify-center items-center overflow-y-auto bg-background-dark p-6 sm:p-12 lg:p-24 relative">
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px] pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-logic-gold/5 rounded-full blur-[100px] pointer-events-none"></div>
      
      <div class="w-full max-w-sm lg:max-w-md space-y-8 relative z-10">
        <!-- Mobile Logo -->
        <div class="flex lg:hidden items-center gap-2 mb-8">
          <div class="flex h-8 w-8 items-center justify-center rounded bg-logic-gold/10 border border-logic-gold/30">
            <span class="material-symbols-outlined text-logic-gold text-xl">public</span>
          </div>
          <span class="text-lg font-bold font-sans tracking-tight text-white">万古经纬</span>
        </div>

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
                <input id="password" v-model="password" name="password" type="password" autocomplete="new-password" required 
                  class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-10 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all font-mono" 
                  placeholder="••••••••">
                <button type="button" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-300 focus:outline-none">
                  <span class="material-symbols-outlined text-[20px]">visibility_off</span>
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
                <input id="confirmPassword" v-model="confirmPassword" name="confirmPassword" type="password" autocomplete="new-password" required 
                  class="block w-full rounded-lg border border-gray-700/50 bg-[#0e1217] py-3 pl-10 pr-10 text-white shadow-sm placeholder:text-gray-600 focus:border-logic-gold/50 focus:ring-1 focus:ring-logic-gold/50 sm:text-sm transition-all font-mono" 
                  placeholder="••••••••">
                <button type="button" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-300 focus:outline-none">
                  <span class="material-symbols-outlined text-[20px]">visibility_off</span>
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
        
        <div class="absolute bottom-6 text-[10px] text-gray-600 font-mono">
          SECURE CONNECTION :: ENCRYPTED
        </div>
      </div>
    </div>
  </div>
</template>
