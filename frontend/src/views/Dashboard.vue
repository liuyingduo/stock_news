<template>
  <div class="dashboard">
    <!-- 顶部筛选器 -->
    <div class="filter-section">
      <el-input
        v-model="queryParams.search"
        placeholder="搜索事件标题或内容..."
        :prefix-icon="Search"
        clearable
        class="search-input"
        @change="handleSearch"
      />
      <el-select
        v-model="queryParams.category"
        placeholder="事件类别"
        clearable
        class="filter-select"
        @change="handleSearch"
      >
        <el-option label="核心驱动板块" value="core_driver" />
        <el-option label="特殊机遇板块" value="special_situation" />
        <el-option label="产业链驱动" value="industrial_chain" />
        <el-option label="市场情绪" value="sentiment_flows" />
        <el-option label="宏观地缘" value="macro_geopolitics" />
      </el-select>
      <el-select
        v-model="queryParams.event_type"
        placeholder="事件类型"
        clearable
        filterable
        class="filter-select"
        @change="handleSearch"
      >
        <el-option label="监管政策" value="regulatory_policy" />
        <el-option label="产业政策" value="industry_policy" />
        <el-option label="监管处罚" value="regulatory_penalty" />
        <el-option label="业绩预告" value="earnings_preview" />
        <el-option label="并购重组" value="ma" />
        <el-option label="年报" value="annual_report" />
        <el-option label="其他" value="other" />
      </el-select>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        class="filter-date"
        @change="handleDateChange"
      />
      <el-button type="primary" @click="loadEvents" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 事件列表 -->
    <div v-loading="loading" class="events-container">
      <div v-if="events.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无事件数据" />
      </div>
      <div v-else class="events-grid">
        <EventCard
          v-for="event in events"
          :key="event.id"
          :event="event"
          @analyze="handleAnalyze"
        />
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getEvents, analyzeEvent } from '../api/events'
import type { Event } from '../api/types'
import EventCard from '../components/EventCard.vue'

const loading = ref(false)
const events = ref<Event[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const dateRange = ref<[string, string] | null>(null)

const queryParams = reactive({
  skip: 0,
  limit: 20,
  category: '',
  event_type: '',
  search: '',
  start_date: '',
  end_date: '',
})

const loadEvents = async () => {
  loading.value = true
  try {
    const response = await getEvents(queryParams)
    events.value = response || []
    // 注意：这里假设后端返回总数的方式，可能需要调整
    // total.value = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载事件失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  queryParams.skip = 0
  loadEvents()
}

const handleDateChange = (dates: [string, string] | null) => {
  if (dates) {
    queryParams.start_date = dates[0]
    queryParams.end_date = dates[1]
  } else {
    queryParams.start_date = ''
    queryParams.end_date = ''
  }
  handleSearch()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  queryParams.skip = (page - 1) * pageSize.value
  loadEvents()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  queryParams.limit = size
  queryParams.skip = 0
  currentPage.value = 1
  loadEvents()
}

const handleAnalyze = async (eventId: string) => {
  try {
    await analyzeEvent(eventId)
    ElMessage.success('AI 分析完成')
    loadEvents()
  } catch (error: any) {
    ElMessage.error(error.message || 'AI 分析失败')
  }
}

onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding: 16px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-primary);
}

.search-input {
  flex: 1;
  min-width: 250px;
}

.filter-select {
  width: 180px;
}

.filter-date {
  width: 280px;
}

.events-container {
  min-height: 400px;
}

.empty-state {
  padding: 60px 20px;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

@media (max-width: 1200px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input,
  .filter-select,
  .filter-date {
    width: 100%;
  }
}
</style>
