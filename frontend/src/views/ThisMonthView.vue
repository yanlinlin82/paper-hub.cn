<template>
  <div class="this-month-page">
    <div class="page-header">
      <h1 class="page-title">
        <i class="fas fa-calendar-check"></i>
        本月分享
      </h1>
      <p class="page-subtitle">{{ currentMonth }} 的论文分享统计</p>
    </div>

    <div class="papers-container">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>加载中...</p>
      </div>

      <div v-else-if="papers.length === 0" class="empty-state">
        <i class="fas fa-calendar-times"></i>
        <h3>本月暂无分享</h3>
        <p>成为第一个分享论文的成员吧！</p>
      </div>

      <div v-else class="papers-grid">
        <div
          v-for="paper in papers"
          :key="paper.id"
          class="paper-card"
        >
          <div class="paper-header">
            <div class="paper-category">{{ paper.category }}</div>
            <div class="paper-date">{{ formatDate(paper.created_at) }}</div>
          </div>
          <h3 class="paper-title">{{ paper.title }}</h3>
          <p class="paper-journal">{{ paper.journal }}</p>
          <p class="paper-abstract">{{ paper.abstract }}</p>
          <div class="paper-footer">
            <div class="paper-author">
              <i class="fas fa-user"></i>
              {{ paper.authors }}
            </div>
            <div class="paper-metrics">
              <span class="metric">
                <i class="fas fa-eye"></i>
                {{ paper.views }}
              </span>
              <span class="metric">
                <i class="fas fa-heart"></i>
                {{ paper.likes }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api, type Paper } from '@/services/api'
import { formatDate } from '@/services/api'

const papers = ref<Paper[]>([])
const loading = ref(true)

const currentMonth = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月`
})

const fetchPapers = async () => {
  try {
    loading.value = true
    const data = await api.getPapers('this-month')
    papers.value = data
  } catch (error) {
    console.error('Error fetching this month papers:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPapers()
})
</script>

<style scoped>
.this-month-page {
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
  color: #3498db;
}

.page-subtitle {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

.papers-container {
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

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.paper-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.paper-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.paper-category {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
}

.paper-date {
  color: #6c757d;
  font-size: 0.85rem;
}

.paper-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.paper-journal {
  color: #3498db;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.paper-abstract {
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.paper-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.paper-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6c757d;
  font-size: 0.85rem;
}

.paper-metrics {
  display: flex;
  gap: 1rem;
}

.metric {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6c757d;
  font-size: 0.85rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .papers-grid {
    grid-template-columns: 1fr;
  }
}

/* 深色主题 */
[data-theme="dark"] .page-title {
  color: #ecf0f1;
}

[data-theme="dark"] .paper-card {
  background: rgba(44, 62, 80, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .paper-title {
  color: #ecf0f1;
}

[data-theme="dark"] .paper-abstract {
  color: #bdc3c7;
}

[data-theme="dark"] .paper-author {
  color: #bdc3c7;
}

[data-theme="dark"] .metric {
  color: #bdc3c7;
}
</style>
