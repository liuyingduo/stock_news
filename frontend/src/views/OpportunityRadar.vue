<template>
  <div class="bg-background-dark text-gray-300 font-sans h-screen w-full overflow-hidden flex antialiased selection:bg-logic-gold selection:text-black">
    <aside class="w-16 lg:w-64 border-r border-white/5 bg-[#0b0e12] flex flex-col shrink-0 z-50">
      <div class="h-16 flex items-center justify-center lg:justify-start lg:px-6 border-b border-white/5 shrink-0">
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-logic-gold/10 border border-logic-gold/30 shadow-glow-gold shrink-0">
            <span class="material-symbols-outlined text-logic-gold text-xl">language</span>
          </div>
          <span class="hidden lg:block text-base font-bold tracking-tight text-white font-sans">万古经纬</span>
        </div>
      </div>
      <div class="flex-1 overflow-y-auto py-6 px-2 lg:px-4 space-y-8">
        <div>
          <button class="w-full flex items-center gap-3 px-3 py-3 rounded-lg bg-surface-lighter text-logic-gold border border-logic-gold/30 shadow-[0_0_15px_rgba(212,175,55,0.1)] transition-all group relative overflow-hidden hover:bg-surface-lighter/80">
            <div class="absolute left-0 top-0 bottom-0 w-1 bg-logic-gold"></div>
            <span class="material-symbols-outlined shrink-0">restart_alt</span>
            <span class="hidden lg:block text-sm font-bold">默认 (全部事件)</span>
          </button>
        </div>
        <div class="space-y-3">
          <div class="hidden lg:flex px-3 items-center justify-between">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider font-mono">指数倾向</h3>
            <span class="text-[10px] text-gray-600 bg-white/5 px-1.5 py-0.5 rounded">单选互斥</span>
          </div>
          <div class="space-y-1">
            <button class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors group">
              <span class="material-symbols-outlined text-[20px] shrink-0">all_inclusive</span>
              <span class="hidden lg:block text-sm">全部信号</span>
            </button>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0" type="checkbox" />
              <span class="hidden lg:flex items-center text-sm group-hover:text-logic-gold transition-colors">
                捕捉机会
                <span class="text-xs text-market-up ml-2 font-mono font-bold bg-market-up/10 px-1 rounded">&gt;70</span>
              </span>
            </label>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0" type="checkbox" />
              <span class="hidden lg:flex items-center text-sm group-hover:text-logic-gold transition-colors">
                规避风险
                <span class="text-xs text-market-down ml-2 font-mono font-bold bg-market-down/10 px-1 rounded">&lt;70</span>
              </span>
            </label>
          </div>
        </div>
        <div class="space-y-3 pt-6 border-t border-white/5">
          <div class="hidden lg:flex px-3 items-center justify-between">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider font-mono">情报鲜度</h3>
          </div>
          <div class="space-y-1">
            <button class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors group">
              <span class="material-symbols-outlined text-[20px] shrink-0">all_inclusive</span>
              <span class="hidden lg:block text-sm">全部信号</span>
            </button>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0" type="checkbox" />
              <span class="hidden lg:block text-sm group-hover:text-logic-gold transition-colors">首发新闻</span>
            </label>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0" type="checkbox" />
              <span class="hidden lg:block text-sm group-hover:text-logic-gold transition-colors">逻辑接力</span>
            </label>
          </div>
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col min-w-0 bg-background-dark relative">
      <div class="absolute inset-0 grid-pattern opacity-[0.03] pointer-events-none"></div>
      <AppHeader />

      <div class="flex-1 overflow-y-auto p-4 lg:p-8 space-y-6 scroll-smooth">
        <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
          <div class="xl:col-span-8 bg-surface-dark border border-white/5 rounded-2xl p-1 relative overflow-hidden group shadow-lg h-full">
            <div class="absolute top-0 right-0 p-4 opacity-50">
              <span class="material-symbols-outlined text-[120px] text-white/[0.02]">speed</span>
            </div>
            <div class="bg-surface-lighter/30 rounded-xl p-6 h-full border border-white/5 backdrop-blur-sm relative z-10 flex flex-col">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <h2 class="text-base font-bold text-white flex items-center gap-2">
                    <span class="material-symbols-outlined text-logic-gold text-sm">network_node</span>
                    市场先生指数
                  </h2>
                  <p class="text-xs text-gray-500 mt-1 font-mono uppercase">Mr. Market Index</p>
                </div>
                <div class="flex gap-2">
                  <button class="px-3 py-1 bg-white/5 hover:bg-white/10 text-xs text-gray-400 rounded border border-white/5 transition-colors">1H</button>
                  <button class="px-3 py-1 bg-logic-gold/20 text-xs text-logic-gold rounded border border-logic-gold/30 transition-colors font-bold">4H</button>
                  <button class="px-3 py-1 bg-white/5 hover:bg-white/10 text-xs text-gray-400 rounded border border-white/5 transition-colors">1D</button>
                </div>
              </div>
              <div class="flex-1 flex flex-col lg:flex-row items-center justify-center gap-8 py-6">
                <div class="relative w-64 h-32 lg:w-80 lg:h-40 shrink-0 flex justify-center">
                  <div class="absolute top-[90%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-logic-gold/5 rounded-full blur-3xl pointer-events-none animate-[pulse_4s_infinite]"></div>
                  <div class="absolute top-[90%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-logic-gold/10 rounded-full blur-2xl pointer-events-none"></div>
                  <svg class="w-full h-full overflow-visible z-10" viewBox="0 0 200 110">
                    <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="#1f2937" stroke-linecap="round" stroke-width="8"></path>
                    <path class="drop-shadow-[0_0_10px_rgba(255,77,77,0.5)]" d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="url(#spectrumGradient)" stroke-dasharray="283" stroke-dashoffset="0" stroke-linecap="round" stroke-width="8">
                      <animate attributeName="stroke-dashoffset" dur="1.5s" fill="freeze" from="283" to="31"></animate>
                    </path>
                    <g class="text-gray-500 font-mono text-[8px] font-bold select-none opacity-50">
                      <text text-anchor="middle" x="10" y="115">-100</text>
                      <text text-anchor="middle" x="100" y="5">0</text>
                      <text text-anchor="middle" x="190" y="115">100</text>
                    </g>
                    <defs>
                      <linearGradient id="spectrumGradient" x1="0%" x2="100%" y1="0%" y2="0%">
                        <stop offset="0%" stop-color="#00e676"></stop>
                        <stop offset="30%" stop-color="#115e59"></stop>
                        <stop offset="50%" stop-color="#64748b"></stop>
                        <stop offset="70%" stop-color="#f87171"></stop>
                        <stop offset="100%" stop-color="#ff4d4d"></stop>
                      </linearGradient>
                    </defs>
                  </svg>
                  <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-6 text-center z-20 pointer-events-none flex flex-col items-center">
                    <div class="relative">
                      <span class="text-5xl font-bold font-mono text-white text-glow leading-none tracking-tighter drop-shadow-lg">78.4</span>
                      <span class="absolute -top-3 -right-14 text-sm font-bold font-mono text-market-up bg-market-up/10 px-1.5 py-0.5 rounded border border-market-up/20">+3.5%</span>
                    </div>
                    <div class="mt-2 px-3 py-1 rounded-full border border-market-up/30 bg-market-up/5 shadow-glow-red backdrop-blur-sm">
                      <span class="text-xs font-bold text-market-up uppercase tracking-wider text-glow-red">理性乐观</span>
                    </div>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-x-12 gap-y-8 w-full lg:w-auto mt-10 lg:mt-0">
                  <div class="flex flex-col items-center lg:items-start">
                    <p class="text-xs text-gray-500 mb-1">叙事规模</p>
                    <div class="flex flex-col items-center lg:items-start">
                      <span class="text-2xl font-mono text-white font-bold">1,284</span>
                      <span class="text-xs text-market-up font-mono flex items-center gap-1 mt-1">
                        <span class="material-symbols-outlined text-[14px]">arrow_upward</span>
                        +4.2%
                      </span>
                    </div>
                  </div>
                  <div class="flex flex-col items-center lg:items-start">
                    <p class="text-xs text-gray-500 mb-1">置信度</p>
                    <div class="flex flex-col items-center lg:items-start">
                      <span class="text-2xl font-mono text-white font-bold">85%</span>
                      <span class="text-xs text-market-up font-mono flex items-center gap-1 mt-1">
                        <span class="material-symbols-outlined text-[14px]">arrow_upward</span>
                        +1.5%
                      </span>
                    </div>
                  </div>
                  <div class="flex flex-col items-center lg:items-start">
                    <p class="text-xs text-gray-500 mb-1">多空信号</p>
                    <div class="flex flex-col items-center lg:items-start">
                      <span class="text-2xl font-mono text-market-up font-bold">0.8</span>
                      <span class="text-xs text-market-up font-mono flex items-center gap-1 mt-1">
                        <span class="material-symbols-outlined text-[14px]">arrow_upward</span>
                        +12.8%
                      </span>
                    </div>
                  </div>
                  <div class="flex flex-col items-center lg:items-start">
                    <p class="text-xs text-gray-500 mb-1">影响力</p>
                    <div class="flex flex-col items-center lg:items-start">
                      <span class="text-2xl font-mono text-white font-bold">92</span>
                      <span class="text-xs text-market-down font-mono flex items-center gap-1 mt-1">
                        <span class="material-symbols-outlined text-[14px]">arrow_downward</span>
                        -0.5%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="xl:col-span-4 flex flex-col gap-6 h-full">
            <div class="bg-surface-dark border border-market-up/30 rounded-xl p-6 relative overflow-hidden shadow-glow-red flex-1 flex flex-col">
              <div class="absolute -right-4 -top-4 w-24 h-24 bg-market-up/5 rounded-full blur-2xl"></div>
              <div class="flex justify-between items-center mb-4 relative z-10">
                <h3 class="text-sm font-bold text-market-up flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-market-up animate-[pulse_3s_infinite]"></span>
                  机会提示
                </h3>
                <span class="text-xs text-gray-500 font-mono">共 12 条事件</span>
              </div>
              <div class="flex-1 flex flex-col justify-center relative z-10">
                <div class="bg-market-up/5 border border-market-up/10 rounded-lg p-3 group hover:bg-market-up/10 transition-colors cursor-pointer">
                  <div class="flex justify-between items-start mb-1.5">
                    <span class="text-xs font-bold text-market-up group-hover:text-white transition-colors">低空经济政策利好</span>
                    <span class="text-[10px] font-mono text-gray-500">14:15</span>
                  </div>
                  <p class="text-[10px] text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">深圳发布低空基础设施建设三年行动计划，eVTOL板块预期强化</p>
                </div>
              </div>
            </div>

            <div class="bg-surface-dark border border-market-down/30 rounded-xl p-6 relative overflow-hidden shadow-glow-green flex-1 flex flex-col">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-sm font-bold text-market-down flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-market-down animate-pulse"></span>
                  风险预警
                </h3>
                <span class="text-xs text-gray-500 font-mono">共 8 条事件</span>
              </div>
              <div class="flex-1 flex flex-col justify-center">
                <div class="bg-market-down/5 border border-market-down/10 rounded-lg p-3 hover:bg-market-down/10 transition-colors cursor-pointer group">
                  <div class="flex justify-between items-start mb-1.5">
                    <span class="text-xs font-bold text-market-down group-hover:text-white transition-colors">地产债违约预期</span>
                    <span class="text-[10px] font-mono text-gray-500">10:42</span>
                  </div>
                  <p class="text-[10px] text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">信用利差快速走阔，机构情绪转弱，抛压加剧</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-surface-dark border border-white/5 rounded-2xl overflow-hidden flex flex-col shadow-lg">
          <div class="p-5 border-b border-white/5 bg-surface-lighter/20 flex justify-between items-center">
            <div class="flex items-center gap-3">
              <div class="p-1.5 rounded bg-logic-gold/10 border border-logic-gold/20">
                <span class="material-symbols-outlined text-logic-gold text-sm">view_list</span>
              </div>
              <h2 class="text-base font-bold text-white">博弈极点 TOP 20</h2>
              <span class="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded-full border border-white/10">筛选: 逻辑相关性 &gt; 80%</span>
            </div>
            <div class="flex gap-4 text-xs text-gray-500 font-mono">
              <span class="flex items-center gap-1"><span class="w-2 h-2 bg-market-up rounded-full"></span>多头信号</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 bg-market-down rounded-full"></span>空头信号</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 bg-logic-gold rounded-full"></span>关键转折</span>
            </div>
          </div>
          <div class="grid grid-cols-12 px-6 py-3 border-b border-white/5 bg-black/20 text-xs font-medium text-gray-500 uppercase tracking-wider">
            <div class="col-span-1"></div>
            <div class="col-span-4 text-left">事件</div>
            <div class="col-span-2 text-center">事件类型</div>
            <div class="col-span-2 text-right">指数</div>
            <div class="col-span-3 text-right pr-20">影响标的</div>
          </div>
          <div class="divide-y divide-white/5">
            <div class="bg-white/[0.02]">
              <div class="grid grid-cols-12 px-6 py-4 items-center hover:bg-white/5 transition-colors cursor-pointer group">
                <div class="col-span-1 font-mono font-bold text-logic-gold text-lg">01</div>
                <div class="col-span-4">
                  <h3 class="text-sm font-bold text-white group-hover:text-logic-gold transition-colors">美联储降息预期升温</h3>
                  <p class="text-xs text-gray-500 mt-0.5 font-light">CPI数据低于预期，通胀压力缓解，市场押注9月降息</p>
                </div>
                <div class="col-span-2">
                  <span class="inline-flex items-center rounded-full bg-blue-400/10 px-2 py-1 text-xs font-medium text-blue-400 ring-1 ring-inset ring-blue-400/20">宏观政策</span>
                </div>
                <div class="col-span-2 text-right">
                  <span class="text-sm font-mono font-bold text-market-up">+92.4</span>
                </div>
                <div class="col-span-3 flex justify-end gap-2">
                  <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">XAU/USD</span>
                  <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">TLT</span>
                  <span class="material-symbols-outlined text-gray-600 text-sm rotate-180">expand_less</span>
                </div>
              </div>
              <div class="px-6 pb-6 pt-2 border-l-2 border-logic-gold ml-6 mb-2 bg-black/20 rounded-r-lg">
                <div class="grid grid-cols-3 gap-6">
                  <div class="col-span-2">
                    <h4 class="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">新闻聚合 (News Aggregation)</h4>
                    <ul class="space-y-2">
                      <li class="flex gap-3 text-xs text-gray-300">
                        <span class="text-gray-600 font-mono shrink-0">14:02</span>
                        <span class="line-clamp-1 hover:text-white cursor-pointer">WSJ: Inflation Cools Again, Likely Sealing Deal for Fed Rate Cut</span>
                      </li>
                      <li class="flex gap-3 text-xs text-gray-300">
                        <span class="text-gray-600 font-mono shrink-0">13:45</span>
                        <span class="line-clamp-1 hover:text-white cursor-pointer">Bloomberg: Traders Boost Bets on 50bps Cut After PPI Miss</span>
                      </li>
                      <li class="flex gap-3 text-xs text-gray-300">
                        <span class="text-gray-600 font-mono shrink-0">12:30</span>
                        <span class="line-clamp-1 hover:text-white cursor-pointer">Reuters: Dollar Slides as Yields Tumble on Dovish Signals</span>
                      </li>
                    </ul>
                  </div>
                  <div class="col-span-1 border-l border-white/5 pl-6">
                    <h4 class="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">AI 逻辑推演</h4>
                    <p class="text-xs text-gray-400 leading-relaxed">
                      通胀下行确立 -&gt; 实际利率预期下降 -&gt; <span class="text-logic-gold">黄金 (Gold)</span> 估值修复动力增强 同时，美元指数承压，利好 <span class="text-white">新兴市场 (EM)</span> 资产 建议关注对利率敏感的生物医药板块
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-12 px-6 py-4 items-center hover:bg-white/5 transition-colors cursor-pointer group">
              <div class="col-span-1 font-mono font-bold text-gray-500 text-lg">02</div>
              <div class="col-span-4">
                <h3 class="text-sm font-bold text-gray-300 group-hover:text-white transition-colors">OpenAI 发布新一代推理模型</h3>
                <p class="text-xs text-gray-600 mt-0.5 font-light">算力需求预期再次上修，光模块产业链受益</p>
              </div>
              <div class="col-span-2 flex flex-wrap gap-2">
                <span class="inline-flex items-center rounded-full bg-purple-400/10 px-2 py-1 text-xs font-medium text-purple-400 ring-1 ring-inset ring-purple-400/20">产业趋势</span>
                <span class="inline-flex items-center rounded-full bg-cyan-400/10 px-2 py-1 text-xs font-medium text-cyan-400 ring-1 ring-inset ring-cyan-400/20">技术创新</span>
              </div>
              <div class="col-span-2 text-right">
                <span class="text-sm font-mono font-bold text-market-up">+88.1</span>
              </div>
              <div class="col-span-3 flex justify-end gap-2">
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">NVDA</span>
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">CPO</span>
                <span class="material-symbols-outlined text-gray-600 text-sm">expand_more</span>
              </div>
            </div>

            <div class="grid grid-cols-12 px-6 py-4 items-center hover:bg-white/5 transition-colors cursor-pointer group">
              <div class="col-span-1 font-mono font-bold text-gray-500 text-lg">03</div>
              <div class="col-span-4">
                <h3 class="text-sm font-bold text-gray-300 group-hover:text-white transition-colors">中东地缘局势升级</h3>
                <p class="text-xs text-gray-600 mt-0.5 font-light">原油供给担忧加剧，航运价格波动</p>
              </div>
              <div class="col-span-2">
                <span class="inline-flex items-center rounded-full bg-red-400/10 px-2 py-1 text-xs font-medium text-red-400 ring-1 ring-inset ring-red-400/20">地缘政治</span>
              </div>
              <div class="col-span-2 text-right">
                <span class="text-sm font-mono font-bold text-market-down">-76.5</span>
              </div>
              <div class="col-span-3 flex justify-end gap-2">
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">BRENT</span>
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">SHIP</span>
                <span class="material-symbols-outlined text-gray-600 text-sm">expand_more</span>
              </div>
            </div>

            <div class="grid grid-cols-12 px-6 py-4 items-center hover:bg-white/5 transition-colors cursor-pointer group">
              <div class="col-span-1 font-mono font-bold text-gray-500 text-lg">04</div>
              <div class="col-span-4">
                <h3 class="text-sm font-bold text-gray-300 group-hover:text-white transition-colors">欧盟针对中国电动车关税落地</h3>
                <p class="text-xs text-gray-600 mt-0.5 font-light">出口链短期承压，关注欧洲本土产能布局企业</p>
              </div>
              <div class="col-span-2">
                <span class="inline-flex items-center rounded-full bg-orange-400/10 px-2 py-1 text-xs font-medium text-orange-400 ring-1 ring-inset ring-orange-400/20">贸易摩擦</span>
              </div>
              <div class="col-span-2 text-right">
                <span class="text-sm font-mono font-bold text-market-down">-64.2</span>
              </div>
              <div class="col-span-3 flex justify-end gap-2">
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">BYD</span>
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">AUTO</span>
                <span class="material-symbols-outlined text-gray-600 text-sm">expand_more</span>
              </div>
            </div>

            <div class="grid grid-cols-12 px-6 py-4 items-center hover:bg-white/5 transition-colors cursor-pointer group">
              <div class="col-span-1 font-mono font-bold text-gray-500 text-lg">05</div>
              <div class="col-span-4">
                <h3 class="text-sm font-bold text-gray-300 group-hover:text-white transition-colors">固态电池技术突破</h3>
                <p class="text-xs text-gray-600 mt-0.5 font-light">某头部大厂宣布量产时间表提前，产业链情绪提振</p>
              </div>
              <div class="col-span-2">
                <span class="inline-flex items-center rounded-full bg-green-400/10 px-2 py-1 text-xs font-medium text-green-400 ring-1 ring-inset ring-green-400/20">技术革新</span>
              </div>
              <div class="col-span-2 text-right">
                <span class="text-sm font-mono font-bold text-market-up">+55.8</span>
              </div>
              <div class="col-span-3 flex justify-end gap-2">
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">CATL</span>
                <span class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">LIT</span>
                <span class="material-symbols-outlined text-gray-600 text-sm">expand_more</span>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 border-t border-white/5 bg-black/10 flex justify-center">
            <button class="text-xs text-gray-500 hover:text-logic-gold transition-colors flex items-center gap-1">
              查看全部 15 条剩余事件
              <span class="material-symbols-outlined text-sm">arrow_downward</span>
            </button>
          </div>
        </div>

        <footer class="flex justify-between items-center text-[10px] text-gray-600 font-mono pt-4 pb-8 px-6 lg:px-0">
          <div class="flex items-center gap-4">
            <span>万古终端 User_01</span>
            <span class="px-1.5 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] text-logic-gold">PRO</span>
          </div>
          <div class="flex gap-4">
            <span>DATA SOURCE: REUTERS / BLOOMBERG / INTERNAL NLP</span>
            <span>SERVER: HK-01</span>
          </div>
        </footer>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/common/AppHeader.vue'
// 静态展示页面，交互逻辑后续接入
</script>
