<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <i class="fas fa-microscope"></i>
          响马读paper
        </h1>
        <p class="hero-subtitle">科研论文分享社群，与志同道合的研究者共同探讨前沿科技</p>
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalPapers }}</div>
            <div class="stat-label">论文总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalUsers }}</div>
            <div class="stat-label">社群成员</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.thisMonthPapers }}</div>
            <div class="stat-label">本月分享</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.topContributor }}</div>
            <div class="stat-label">分享达人</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 最新分享 -->
    <section class="recent-papers-section">
      <div class="section-header">
        <h2 class="section-title">
          <i class="fas fa-clock"></i>
          最新分享
        </h2>
        <router-link to="/all-shares" class="view-all-link">
          查看全部
          <i class="fas fa-arrow-right"></i>
        </router-link>
      </div>

      <div class="papers-grid">
        <div
          v-for="paper in recentPapers"
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

      <div v-if="recentPapers.length === 0" class="empty-state">
        <i class="fas fa-file-alt empty-icon"></i>
        <h3>暂无最新分享</h3>
        <p>成为第一个分享论文的成员吧！</p>
      </div>
    </section>

    <!-- 快速导航 -->
    <section class="quick-nav-section">
      <h2 class="section-title">
        <i class="fas fa-compass"></i>
        快速导航
      </h2>
      <div class="quick-nav-grid">
        <router-link to="/all-shares" class="quick-nav-item">
          <i class="fas fa-list-alt"></i>
          <span>所有分享</span>
        </router-link>
        <router-link to="/this-month" class="quick-nav-item">
          <i class="fas fa-calendar-check"></i>
          <span>本月分享</span>
        </router-link>
        <router-link to="/last-month" class="quick-nav-item">
          <i class="fas fa-history"></i>
          <span>上月分享</span>
        </router-link>
        <router-link to="/rankings" class="quick-nav-item">
          <i class="fas fa-medal"></i>
          <span>社群榜单</span>
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api, type Stats, type Paper } from '@/services/api'
import { formatDate } from '@/services/api'

// 响应式数据
const stats = ref<Stats>({
  totalPapers: 0,
  totalUsers: 0,
  thisMonthPapers: 0,
  topContributor: 0
})

const recentPapers = ref<Paper[]>([])
const loading = ref(true)

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    const [statsData, papersData] = await Promise.all([
      api.getStats(),
      api.getRecentPapers()
    ])
    
    stats.value = statsData
    recentPapers.value = papersData
  } catch (error) {
    console.error('Error fetching home data:', error)
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home-page {
  width: 100%;
  margin: 0;
  max-width: none;
  padding: 0;
}

/* 欢迎横幅 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 3rem 2rem;
  margin-bottom: 3rem;
  text-align: center;
  color: white;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.hero-title i {
  font-size: 2rem;
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 2rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* 最新分享 */
.recent-papers-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
}

.section-title i {
  color: #3498db;
}

.view-all-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.view-all-link:hover {
  color: #2980b9;
  transform: translateX(5px);
}

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  width: 100%;
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

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* 快速导航 */
.quick-nav-section {
  margin-bottom: 2rem;
}

.quick-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  width: 100%;
}

.quick-nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  padding: 1.5rem;
  border-radius: 15px;
  text-decoration: none;
  color: #2c3e50;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.quick-nav-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  color: #3498db;
}

.quick-nav-item i {
  font-size: 1.5rem;
  color: #3498db;
  width: 30px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-section {
    padding: 2rem 1rem;
    margin-bottom: 2rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .papers-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

/* 深色主题 */
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

[data-theme="dark"] .quick-nav-item {
  background: rgba(44, 62, 80, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
  color: #ecf0f1;
}

[data-theme="dark"] .section-title {
  color: #ecf0f1;
}
</style>
