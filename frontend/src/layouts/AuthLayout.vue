<template>
  <div class="bg-background-dark font-sans text-gray-200 h-screen w-full overflow-hidden flex flex-col lg:flex-row antialiased selection:bg-logic-gold selection:text-white">
    <!-- Left Banner (共享，不会因路由切换而重新渲染) -->
    <div class="relative hidden w-full lg:flex lg:w-5/12 xl:w-1/2 flex-col justify-between p-12 bg-black overflow-hidden group border-r border-white/5">
      <div class="absolute inset-0 z-0 opacity-40 transition-transform duration-[40s] ease-linear group-hover:scale-105" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuB05i95VsA062FksCvGBuQjSCxem40pr1U6I5abihPl0iz_Xg8i2grj8dTZbKgZnPc-GxWdGTcD8u9vXLhoGu31LfQOvMhu-U-BOY5FGIXzmzOBiAenFOnO8UB5eb4wXD138KvY3IPNbbvHk6asT6y99KyvEUn-DQRcpvDoZA35qzpwhOPMOdX2F6Cp6D910elKQiYSIFczLEvV_PfFvdJABUw9HlqFFPmZKLOyU0CZdo5H9YYgi7K4HVoHhHxCm9mbN4LkVhhWWiII'); background-size: cover; background-position: center;">
      </div>
      <div class="absolute inset-0 z-10 bg-gradient-to-b from-black/60 via-black/20 to-black/90"></div>
      <div class="absolute inset-0 z-10 bg-gradient-to-r from-black/80 via-transparent to-transparent"></div>
      
      <div class="relative z-20 flex flex-col h-full justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-full bg-logic-gold/10 backdrop-blur-md border border-logic-gold/40 shadow-glow-gold">
            <span class="material-symbols-outlined text-logic-gold text-2xl" style="font-variation-settings: 'FILL' 1, 'wght' 400;">travel_explore</span>
          </div>
          <h1 class="text-2xl font-bold tracking-tight text-white">万古经纬</h1>
        </div>
        
        <div class="flex flex-col gap-8 max-w-xl">
          <div class="inline-flex w-fit items-center gap-2 rounded-full border border-logic-gold/20 bg-logic-gold/5 px-3 py-1 text-xs font-medium text-logic-gold backdrop-blur-sm tracking-wide">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-logic-gold opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-logic-gold"></span>
            </span>
            AI金融情绪监测系统在线
          </div>
          
          <h2 class="text-4xl font-black leading-[1.2] tracking-wide text-white xl:text-5xl drop-shadow-xl">
            经古往今来 <br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-white via-logic-gold to-white text-glow-gold">纬南北东西</span>
          </h2>
          
          <p class="text-lg text-gray-400 font-normal leading-relaxed border-l-2 border-logic-gold/60 pl-5 tracking-wide">
            让每一条资讯都有逻辑经纬
          </p>
          
          <div class="mt-4 grid grid-cols-3 gap-8 pt-8 border-t border-white/10">
            <div>
              <p class="text-2xl font-bold text-white tracking-tight tabular-nums">2.4M+</p>
              <p class="text-[11px] font-medium uppercase tracking-wider text-gray-500 mt-1">每日信号处理</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-white tracking-tight tabular-nums">150<span class="text-sm align-top text-gray-400 font-semibold ml-0.5">ms</span></p>
              <p class="text-[11px] font-medium uppercase tracking-wider text-gray-500 mt-1">NLP解析延迟</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-white tracking-tight tabular-nums">99.9%</p>
              <p class="text-[11px] font-medium uppercase tracking-wider text-gray-500 mt-1">系统在线率</p>
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

    <!-- Right Content (登录/注册表单，通过 slot 传入) -->
    <div class="flex flex-1 flex-col justify-center items-center overflow-y-auto bg-background-dark p-6 sm:p-12 lg:p-24 relative">
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px] pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-logic-gold/5 rounded-full blur-[100px] pointer-events-none"></div>
      
      <div class="w-full max-w-sm lg:max-w-md space-y-8 relative z-10">
        <!-- Mobile Logo -->
        <div class="flex lg:hidden items-center gap-2 mb-8">
          <div class="flex h-8 w-8 items-center justify-center rounded bg-logic-gold/10 border border-logic-gold/30">
            <span class="material-symbols-outlined text-logic-gold text-xl" style="font-variation-settings: 'FILL' 1, 'wght' 400;">travel_explore</span>
          </div>
          <span class="text-lg font-bold tracking-tight text-white">万古经纬</span>
        </div>

        <!-- 表单内容通过 slot 传入，切换时只有这部分会变化 -->
        <slot />
        
        <div class="absolute bottom-6 text-[10px] text-gray-600 font-semibold tracking-widest uppercase">
          Secure Connection :: Encrypted
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Auth Layout - 用于登录/注册等全屏认证页面
// 左侧 Banner 在此布局中共享，切换路由时不会重新渲染
</script>

<style scoped>
/* 自定义样式已通过 Tailwind 类实现 */
</style>
