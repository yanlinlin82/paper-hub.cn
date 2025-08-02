<template>
  <div class="rankings-page">
    <div class="page-header">
      <h1 class="page-title">
        <i class="fas fa-medal"></i>
        社群榜单
      </h1>
      <p class="page-subtitle">查看社群成员的分享排行榜</p>
    </div>

    <!-- 榜单类型选择器 -->
    <div class="rankings-tabs">
      <button 
        v-for="tab in rankingTabs" 
        :key="tab.key"
        @click="selectRankingTab(tab.key)"
        class="tab-button"
        :class="{ active: selectedTab === tab.key }"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- 年月选择器（用于月度榜单和年度榜单） -->
    <div v-if="showDateSelector" class="date-selector">
      <div class="date-controls">
        <!-- 月度榜单导航 -->
        <div v-if="selectedTab === 'monthly'" class="monthly-navigation">
          <button 
            class="nav-button prev-button" 
            @click="previousMonth"
            :disabled="!canGoPreviousMonth"
          >
            <i class="fas fa-chevron-left"></i>
            上一月
          </button>
          
          <div class="date-display">
            <span class="current-date">{{ selectedYear }}年{{ selectedMonth }}月</span>
          </div>
          
          <button 
            class="nav-button next-button" 
            @click="nextMonth"
            :disabled="!canGoNextMonth"
          >
            下一月
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        
        <!-- 年度榜单导航 -->
        <div v-if="selectedTab === 'yearly'" class="yearly-navigation">
          <button 
            class="nav-button prev-button" 
            @click="previousYear"
            :disabled="!canGoPreviousYear"
          >
            <i class="fas fa-chevron-left"></i>
            上一年
          </button>
          
          <div class="date-display">
            <span class="current-date">{{ selectedYear }}年</span>
          </div>
          
          <button 
            class="nav-button next-button" 
            @click="nextYear"
            :disabled="!canGoNextYear"
          >
            下一年
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="rankings-container">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>加载中...</p>
      </div>

      <div v-else-if="currentRankingData.length === 0" class="empty-state">
        <i class="fas fa-trophy"></i>
        <h3>暂无排行榜数据</h3>
        <p>开始分享论文，登上排行榜吧！</p>
      </div>

      <div v-else class="rankings-grid">
        <div
          v-for="ranking in currentRankingData"
          :key="ranking.name"
          class="ranking-card"
        >
          <div class="ranking-header">
            <h3 class="ranking-title">{{ ranking.title }}</h3>
            <div class="ranking-count">共 {{ ranking.total_count }} 人</div>
          </div>
          
          <div class="ranking-list">
            <div
              v-for="(item, index) in ranking.content"
              :key="item.id || item.name"
              class="ranking-item"
              :class="{ 'top-three': index < 3 }"
            >
              <div class="rank-number" :class="getRankClass(index + 1)">
                {{ index + 1 }}
              </div>
              <div class="user-info">
                <div class="user-name">
                  <a v-if="item.link" :href="item.link" class="journal-link">{{ item.name }}</a>
                  <span v-else>{{ item.name }}</span>
                </div>
                <div class="user-count">
                  {{ item.count }} {{ ranking.name === 'journal' ? '篇论文' : '篇论文' }}
                </div>
              </div>
              <div class="rank-badge" :class="getRankBadgeClass(index + 1)">
                <i :class="getRankIcon(index + 1)"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'

interface RankingItem {
  id?: number
  name: string
  count: number
  link?: string
}

interface RankingData {
  name: string
  title: string
  total_count: number
  columns: string[]
  content: RankingItem[]
}

const rankings = ref<RankingData[]>([])
const loading = ref(true)
const selectedTab = ref('this-month')
const selectedYear = ref(new Date().getFullYear())
const selectedMonth = ref(new Date().getMonth() + 1)

// 榜单类型配置
const rankingTabs = [
  { key: 'this-month', label: '本月榜单', icon: 'fas fa-calendar-alt' },
  { key: 'last-month', label: '上月榜单', icon: 'fas fa-calendar-minus' },
  { key: 'monthly', label: '月度榜单', icon: 'fas fa-calendar-week' },
  { key: 'yearly', label: '年度榜单', icon: 'fas fa-calendar' },
  { key: 'all', label: '总榜单', icon: 'fas fa-trophy' },
  { key: 'journal', label: '杂志榜单', icon: 'fas fa-book' }
]

// 计算属性
const showDateSelector = computed(() => {
  return selectedTab.value === 'monthly' || selectedTab.value === 'yearly'
})

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: currentYear - 2021 + 1 }, (_, i) => currentYear - i)
})

// 导航按钮状态计算
const canGoPreviousMonth = computed(() => {
  if (selectedTab.value !== 'monthly') return false
  return selectedYear.value > 2022 || (selectedYear.value === 2022 && selectedMonth.value > 1)
})

const canGoNextMonth = computed(() => {
  if (selectedTab.value !== 'monthly') return false
  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth() + 1
  return selectedYear.value < currentYear || (selectedYear.value === currentYear && selectedMonth.value < currentMonth)
})

const canGoPreviousYear = computed(() => {
  if (selectedTab.value !== 'yearly') return false
  return selectedYear.value > 2022
})

const canGoNextYear = computed(() => {
  if (selectedTab.value !== 'yearly') return false
  const currentYear = new Date().getFullYear()
  return selectedYear.value < currentYear
})

const currentRankingData = computed(() => {
  // 对于所有榜单类型，都只返回对应的榜单数据
  return rankings.value.filter(r => r.name === selectedTab.value)
})

const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-gold'
  if (rank === 2) return 'rank-silver'
  if (rank === 3) return 'rank-bronze'
  return 'rank-normal'
}

const getRankBadgeClass = (rank: number) => {
  if (rank === 1) return 'badge-gold'
  if (rank === 2) return 'badge-silver'
  if (rank === 3) return 'badge-bronze'
  return 'badge-normal'
}

const getRankIcon = (rank: number) => {
  if (rank === 1) return 'fas fa-crown'
  if (rank === 2) return 'fas fa-medal'
  if (rank === 3) return 'fas fa-award'
  return 'fas fa-star'
}

const selectRankingTab = (tabKey: string) => {
  selectedTab.value = tabKey
  fetchRankingData()
}

// 月度导航方法
const previousMonth = () => {
  if (selectedMonth.value > 1) {
    selectedMonth.value--
  } else {
    selectedMonth.value = 12
    selectedYear.value--
  }
  fetchRankingData()
}

const nextMonth = () => {
  if (selectedMonth.value < 12) {
    selectedMonth.value++
  } else {
    selectedMonth.value = 1
    selectedYear.value++
  }
  fetchRankingData()
}

// 年度导航方法
const previousYear = () => {
  selectedYear.value--
  fetchRankingData()
}

const nextYear = () => {
  selectedYear.value++
  fetchRankingData()
}

const fetchRankingData = async () => {
  try {
    loading.value = true
    
    if (selectedTab.value === 'monthly' || selectedTab.value === 'yearly') {
      // 获取特定类型的榜单
      const data = await api.getRankingByType(selectedTab.value, selectedYear.value, selectedTab.value === 'monthly' ? selectedMonth.value : undefined)
      if (data) {
        rankings.value = [data]
      } else {
        rankings.value = []
      }
    } else {
      // 获取所有榜单
      const data = await api.getRankings()
      rankings.value = data
    }
  } catch (error) {
    console.error('Error fetching ranking data:', error)
    rankings.value = []
  } finally {
    loading.value = false
  }
}

const fetchRankings = async () => {
  try {
    loading.value = true
    const data = await api.getRankings()
    rankings.value = data
  } catch (error) {
    console.error('Error fetching rankings:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRankings()
})
</script>

<style scoped>
.rankings-page {
  width: 100%;
  margin: 0;
  max-width: none;
  padding: 0;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.page-title i {
  color: #f39c12;
}

.page-subtitle {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

.rankings-tabs {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  background: white;
  color: #6c757d;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-button:hover {
  border-color: #007bff;
  color: #007bff;
  transform: translateY(-2px);
}

.tab-button.active {
  border-color: #007bff;
  background: #007bff;
  color: white;
}

.tab-button i {
  font-size: 1rem;
}

.date-selector {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 10px;
}

.date-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-controls label {
  font-weight: 500;
  color: #495057;
}

.date-controls select {
  padding: 0.5rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 5px;
  background: white;
  color: #495057;
  font-size: 0.9rem;
}

.monthly-navigation,
.yearly-navigation {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid #007bff;
  border-radius: 25px;
  background: white;
  color: #007bff;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-button:hover:not(:disabled) {
  background: #007bff;
  color: white;
  transform: translateY(-2px);
}

.nav-button:disabled {
  border-color: #6c757d;
  color: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.date-display {
  padding: 0.75rem 1.5rem;
  background: #f8f9fa;
  border-radius: 25px;
  border: 2px solid #e9ecef;
}

.current-date {
  font-weight: 600;
  color: #495057;
  font-size: 1.1rem;
}

.rankings-container {
  min-height: 400px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.loading-state i,
.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.rankings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  width: 100%;
}

.ranking-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.ranking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.ranking-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.ranking-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 10px;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.ranking-item:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.ranking-item.top-three {
  background: linear-gradient(135deg, #fff9c4 0%, #fff59d 100%);
  border: 1px solid #ffd54f;
}

.rank-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  color: white;
}

.rank-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
}

.rank-silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a0a0a0 100%);
}

.rank-bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #b8860b 100%);
}

.rank-normal {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.user-count {
  font-size: 0.85rem;
  color: #6c757d;
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
}

.badge-gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
}

.badge-silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a0a0a0 100%);
}

.badge-bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #b8860b 100%);
}

.badge-normal {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .rankings-tabs {
    gap: 0.5rem;
  }
  
  .tab-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
  
  .date-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .rankings-grid {
    grid-template-columns: 1fr;
  }
  
  .ranking-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

/* 深色主题 */
[data-theme="dark"] .page-title {
  color: #ecf0f1;
}

[data-theme="dark"] .tab-button {
  background: rgba(44, 62, 80, 0.9);
  border-color: rgba(255, 255, 255, 0.2);
  color: #bdc3c7;
}

[data-theme="dark"] .tab-button:hover {
  border-color: #007bff;
  color: #007bff;
}

[data-theme="dark"] .tab-button.active {
  border-color: #007bff;
  background: #007bff;
  color: white;
}

[data-theme="dark"] .date-selector {
  background: rgba(52, 73, 94, 0.5);
}

[data-theme="dark"] .date-controls label {
  color: #ecf0f1;
}

[data-theme="dark"] .date-controls select {
  background: rgba(44, 62, 80, 0.9);
  border-color: rgba(255, 255, 255, 0.2);
  color: #ecf0f1;
}

[data-theme="dark"] .nav-button {
  background: rgba(44, 62, 80, 0.9);
  border-color: #007bff;
  color: #007bff;
}

[data-theme="dark"] .nav-button:hover:not(:disabled) {
  background: #007bff;
  color: white;
}

[data-theme="dark"] .nav-button:disabled {
  border-color: #6c757d;
  color: #6c757d;
}

[data-theme="dark"] .date-display {
  background: rgba(52, 73, 94, 0.5);
  border-color: rgba(255, 255, 255, 0.2);
}

[data-theme="dark"] .current-date {
  color: #ecf0f1;
}

[data-theme="dark"] .ranking-card {
  background: rgba(44, 62, 80, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .ranking-title {
  color: #ecf0f1;
}

[data-theme="dark"] .ranking-item {
  background: rgba(52, 73, 94, 0.5);
}

[data-theme="dark"] .ranking-item.top-three {
  background: linear-gradient(135deg, rgba(255, 249, 196, 0.2) 0%, rgba(255, 245, 157, 0.2) 100%);
  border-color: #ffd54f;
}

[data-theme="dark"] .user-name {
  color: #ecf0f1;
}

[data-theme="dark"] .user-count {
  color: #bdc3c7;
}
</style>
