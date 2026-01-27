# 🎨 设计规范 - 基于 SITUATION MONITOR 和 GLOBE 截图

## 📊 设计分析总结

基于参考截图的分析，本设计采用**暗色企业科幻风格**（Dark Corporate Sci-Fi），结合专业的数据可视化和清晰的层级结构。

## 🎨 核心设计特征

### 1. 布局结构

#### SITUATION MONITOR 布局
```
┌─────────────────────────────────────────────────────────┐
│  Header: Logo | Statistics | Navigation                  │
├──────────┬──────────────────────────────────────────────┤
│          │  Main Content Area (75%)                     │
│  Left    │  ┌────────────────────────────────────────┐  │
│  Sidebar │  │ Article Card 1                         │  │
│  (25%)   │  │ - Category Tag (colored)               │  │
│          │  │ - Source & Location                    │  │
│ - Map    │  │ - Title                                │  │
│ - Filter │  │ - Excerpt                              │  │
│ - Stats  │  └────────────────────────────────────────┘  │
│          │  ┌────────────────────────────────────────┐  │
│          │  │ Article Card 2                         │  │
│          │  └────────────────────────────────────────┘  │
└──────────┴──────────────────────────────────────────────┘
```

#### GLOBE 布局
```
┌─────────────────────────────────────────────────────────┐
│  Header: GLOBAL EVENT MONITOR | Dashboard | Globe       │
├──────────┬──────────────────────────────┬───────────────┤
│  Left    │     Central Globe            │   Right       │
│  Sidebar │     Visualization            │   Sidebar     │
│          │                              │               │
│ - Panel  │      [3D GLOBE]              │ - Spin        │
│ - Panel  │      with Data Bars          │ - Wars        │
│ - Legend │                              │ - Trade       │
│          │                              │ - Time        │
└──────────┴──────────────────────────────┴───────────────┘
```

### 2. 配色方案

#### 背景色系
- **主背景**: `#1a1a2e` (深海军蓝)
- **次背景**: `#0f0f1a` (更深的黑蓝)
- **卡片背景**: `#2a2a3e` (稍浅的深灰)
- **面板背景**: `rgba(26, 26, 46, 0.95)` (半透明面板)

#### 强调色
- **主强调色**: `#ff4d4d` (亮红/橙)
- **成功色**: `#4ade80` (绿色 - 用于 LIVE 指示器)
- **高亮数据**: `#f59e0b` (橙黄)
- **常规数据**: `#10b981` (绿色)
- **低数据**: `#3b82f6` (蓝色)

#### 文字色
- **主文字**: `#ffffff` (纯白)
- **次文字**: `#a0a0a0` (浅灰)
- **弱化文字**: `#6b7280` (中灰)

### 3. 组件设计

#### Header (顶部栏)
```css
- 高度: 60px
- 背景: #0f0f1a
- 边框底部: 1px solid #2a2a3e
- 布局: Flexbox (Logo | Statistics | Navigation)
```

**元素**:
- Logo: "金融事件分析" (白色粗体)
- LIVE 指示器: 绿点 + "LIVE" 文字
- 统计数据: "2,026 篇文章 | 42 来源 | 38 板块"
- 导航按钮: 圆角, 红色主按钮

#### 统计卡片 (Stat Cards)
```css
- 背景: #2a2a3e
- 圆角: 12px
- 内边距: 20px
- 悬停效果: 轻微上浮 + 边框发光
```

#### 文章卡片 (Article Cards)
```css
- 背景: #2a2a3e
- 圆角: 8px
- 内边距: 16px
- 下边距: 16px
```

**卡片结构**:
```
┌────────────────────────────────────┐
│ [CATEGORY TAG]     [SOURCE] [TIME] │
│ 📍 Location                          │
│                                     │
│ Article Title (bold, white)         │
│                                     │
│ Article excerpt (lighter gray)      │
│                                     │
│ [Impact Score: 7.5] [Read More]     │
└────────────────────────────────────┘
```

#### 分类标签 (Category Tags)
- GEOPOLITICS: 橙色背景 `#f59e0b`
- MARKETS: 红色背景 `#ef4444`
- ECONOMY: 绿色背景 `#10b981`
- TECHNOLOGY: 蓝色背景 `#3b82f6`
- OTHERS: 灰色背景 `#6b7280`

#### 左侧边栏 (Left Sidebar)
```css
- 宽度: 320px (约25%)
- 背景: #1a1a2e
- 右边框: 1px solid #2a2a3e
```

**面板样式**:
```css
- 背景: rgba(42, 42, 62, 0.8)
- 圆角: 12px
- 内边距: 16px
- 底部边距: 16px
- 标题: 大写, 粗体, 白色
```

#### 筛选按钮 (Filter Buttons)
```css
- 背景: #2a2a3e
- 文字: 白色
- 圆角: 20px (pill shape)
- 内边距: 8px 16px
- 悬停: 背景变亮 #3a3a4e
- 激活: 红色背景 #ff4d4d
```

### 4. 视觉效果

#### 阴影系统
```css
card-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
panel-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
hover-glow: 0 0 16px rgba(255, 77, 77, 0.3);
```

#### 边框
```css
default-border: 1px solid #2a2a3e;
accent-border: 1px solid #ff4d4d;
active-border: 1px solid #4ade80;
```

#### 过渡动画
```css
transition: all 0.2s ease;
hover-transform: translateY(-2px);
```

### 5. 数据可视化配色

基于 GLOBE 截图的颜色系统:

| 数据强度 | 颜色 | RGB | 用途 |
|---------|------|-----|------|
| High (高) | Red | #ef4444 | 7-10 分, >20 事件 |
| Medium (中) | Yellow/Orange | #f59e0b | 5-6 分, 5-19 事件 |
| Low (低) | Green | #10b981 | 1-4 分, 1-4 事件 |
| Normal | Blue | #3b82f6 | 默认状态 |
| Shipping/Air | Cyan | #06b6d4 | 特殊类型 |

### 6. 字体系统

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* 标题 */
h1: 28px, bold, 700
h2: 24px, semibold, 600
h3: 20px, semibold, 600

/* 正文 */
body: 14px, regular, 400
small: 12px, regular, 400

/* 标签/按钮 */
tags: 12px, semibold, 600, uppercase
buttons: 14px, semibold, 600, uppercase
```

### 7. 关键 UI 模式

#### LIVE 指示器
```html
<div class="live-indicator">
  <span class="live-dot"></span>
  <span class="live-text">LIVE</span>
</div>

<style>
.live-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #4ade80;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  box-shadow: 0 0 8px #4ade80;
}

.live-text {
  color: #4ade80;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
}
</style>
```

#### 统计数字显示
```html
<div class="stats-display">
  <div class="stat-item">
    <span class="stat-value">2,026</span>
    <span class="stat-label">Events</span>
  </div>
  <div class="stat-divider"></div>
  <div class="stat-item">
    <span class="stat-value">42</span>
    <span class="stat-label">Sources</span>
  </div>
  <!-- ... -->
</div>
```

#### 文章卡片示例
```html
<div class="article-card">
  <div class="card-header">
    <span class="category-tag" style="background: #f59e0b;">GEOPOLITICS</span>
    <div class="card-meta">
      <span class="source">📰 Bloomberg</span>
      <span class="location">📍 Washington</span>
      <span class="time">8h ago</span>
    </div>
  </div>

  <h3 class="card-title">Fed signals potential rate cuts in 2025</h3>

  <p class="card-excerpt">
    Federal Reserve officials indicated that interest rate cuts could begin
    in the coming months as inflation continues to moderate...
  </p>

  <div class="card-footer">
    <div class="impact-score" style="color: #ef4444;">
      Impact: 8.5/10
    </div>
    <button class="read-more-btn">View Analysis</button>
  </div>
</div>
```

## 📐 CSS 变量系统

```css
:root {
  /* 背景色 */
  --bg-primary: #1a1a2e;
  --bg-secondary: #0f0f1a;
  --bg-card: #2a2a3e;
  --bg-panel: rgba(42, 42, 62, 0.8);

  /* 强调色 */
  --accent-red: #ff4d4d;
  --accent-orange: #f59e0b;
  --accent-green: #4ade80;
  --accent-blue: #3b82f6;
  --accent-cyan: #06b6d4;

  /* 文字色 */
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --text-muted: #6b7280;

  /* 边框 */
  --border-primary: #2a2a3e;
  --border-accent: #ff4d4d;

  /* 阴影 */
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-panel: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 16px rgba(255, 77, 77, 0.3);

  /* 圆角 */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 20px;

  /* 过渡 */
  --transition-fast: 0.15s ease;
  --transition-base: 0.2s ease;
  --transition-slow: 0.3s ease;
}
```

## 🎯 实现优先级

1. ✅ **立即实现**:
   - 更新配色系统
   - 更新布局结构 (三栏布局)
   - Header 统计显示
   - 文章卡片样式

2. ⏳ **次要优先级**:
   - LIVE 指示器动画
   - 筛选按钮样式
   - 面板组件

3. 🎨 **增强功能** (未来):
   - 3D Globe 可视化
   - 地图标记
   - 数据柱状图
   - 更多动画效果

## 📋 与现有设计的差异

| 特征 | 现有 Cyberpunk 主题 | 参考截图设计 |
|------|-------------------|-------------|
| 主色调 | 霓虹蓝 #0080FF | 红色/橙 #ff4d4d |
| 风格 | Cyberpunk (霓虹发光) | 企业科幻 (专业暗色) |
| 扫描线 | 有 (CRT 效果) | 无 |
| 发光效果 | 强烈发光效果 | 轻微发光 |
| 背景 | 纯黑 #0D0D0D | 深海军蓝 #1a1a2e |
| 玻璃态 | 强烈 | 微妙 |
| 布局 | 两栏 | 三栏 (Header + Sidebar + Content) |

## 🚀 下一步行动

1. 更新 `cyberpunk-dark.css` 为 `dashboard-dark.css`
2. 修改配色方案匹配截图
3. 更新 App.vue 布局结构
4. 更新 Dashboard.vue 组件
5. 更新 EventCard.vue 样式
