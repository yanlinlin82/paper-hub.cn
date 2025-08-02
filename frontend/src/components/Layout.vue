<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="container-fluid">
        <div class="header-container">
        <!-- Logo -->
        <div class="logo">
          <router-link to="/" class="logo-link">
            <i class="fas fa-microscope"></i>
            <span class="logo-text">Paper Hub</span>
          </router-link>
        </div>

        <!-- 搜索栏 -->
        <div class="search-container">
          <div class="search-box">
            <i class="fas fa-search search-icon"></i>
            <input
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              class="search-input"
              type="text"
              placeholder="搜索论文..."
            />
            <button @click="handleSearch" class="search-button">
              搜索
            </button>
          </div>
        </div>

        <!-- 右侧菜单 -->
        <div class="header-menu">
          <button class="menu-button" @click="toggleTheme">
            <i :class="theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon'"></i>
          </button>
          <div class="user-menu">
            <button v-if="!isLoggedIn" class="user-button" @click="showLoginModal = true">
              <i class="fas fa-user-circle"></i>
              <span>登录</span>
            </button>
            <button v-if="!isLoggedIn && isDev" class="dev-login-button" @click="devLogin">
              <i class="fas fa-bug"></i>
              <span>开发登录</span>
            </button>
            <div v-else class="user-info">
              <span class="username">{{ userInfo.nickname || '用户' }}</span>
              <button class="logout-button" @click="handleLogout">
                <i class="fas fa-sign-out-alt"></i>
                退出
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <div class="container-fluid">
        <div class="content-container">
        <!-- 侧边栏 -->
        <aside class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
          <div class="sidebar-header">
            <h3 class="sidebar-title">
              <i class="fas fa-users"></i>
              响马读paper
            </h3>
            <button class="sidebar-toggle" @click="toggleSidebar">
              <i :class="sidebarCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
            </button>
          </div>

          <nav class="sidebar-nav">
            <router-link to="/" class="nav-item" active-class="active">
              <i class="fas fa-home"></i>
              <span>社群首页</span>
            </router-link>
            <router-link to="/all-shares" class="nav-item" active-class="active">
              <i class="fas fa-list-alt"></i>
              <span>所有分享</span>
            </router-link>
            <router-link to="/this-month" class="nav-item" active-class="active">
              <i class="fas fa-calendar-check"></i>
              <span>本月分享</span>
            </router-link>
            <router-link to="/last-month" class="nav-item" active-class="active">
              <i class="fas fa-history"></i>
              <span>上月分享</span>
            </router-link>
            <router-link to="/rankings" class="nav-item" active-class="active">
              <i class="fas fa-medal"></i>
              <span>社群榜单</span>
            </router-link>
          </nav>
        </aside>

        <!-- 主内容区 -->
        <div class="main-area">
          <router-view />
        </div>
        </div>
      </div>
    </main>

    <!-- 登录模态框 -->
    <LoginModal 
      :show="showLoginModal"
      @close="showLoginModal = false"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCookie } from '@/services/api'
import LoginModal from './LoginModal.vue'

const router = useRouter()
const searchQuery = ref('')
const sidebarCollapsed = ref(false)
const theme = ref('light')
const showLoginModal = ref(false)
const isLoggedIn = ref(false)
const userInfo = ref<any>({})
const isDev = ref(import.meta.env.DEV)

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 实现搜索功能
    console.log('搜索:', searchQuery.value)
  }
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme.value)
}

const checkLoginStatus = () => {
  const token = getCookie('token')
  isLoggedIn.value = !!token
  if (token) {
    // 这里可以从token中解析用户信息，或者调用API获取
    userInfo.value = { nickname: '用户' }
  }
}

const handleLoginSuccess = (data: any) => {
  isLoggedIn.value = true
  userInfo.value = data
  showLoginModal.value = false
}

const handleLogout = () => {
  // 清除cookie
  document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT'
  isLoggedIn.value = false
  userInfo.value = {}
}

const devLogin = () => {
  // 开发模式自动登录
  const testToken = '24641876-dee6-402c-af9d-5c1ac6c59221'
  document.cookie = `token=${testToken}; path=/; max-age=86400`
  isLoggedIn.value = true
  userInfo.value = { nickname: '开发用户' }
}

onMounted(() => {
  checkLoginStatus()
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  width: 100vw !important;
  max-width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  left: 0;
  right: 0;
}

/* 顶部导航栏 */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.header-container {
  max-width: none !important;
  margin: 0 !important;
  padding: 0;
  display: flex;
  align-items: center;
  height: 70px;
  gap: 2rem;
  width: 100% !important;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: #2c3e50;
  font-weight: 700;
  font-size: 1.5rem;
}

.logo-link i {
  color: #3498db;
  font-size: 1.75rem;
}

.search-container {
  flex: 1;
  max-width: 700px;
  min-width: 300px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: #f8f9fa;
  border-radius: 25px;
  padding: 0.5rem;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.search-box:focus-within {
  border-color: #3498db;
  background: white;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-icon {
  color: #6c757d;
  margin-left: 0.75rem;
  font-size: 0.9rem;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.5rem 1rem;
  font-size: 0.95rem;
  outline: none;
}

.search-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-button:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

.header-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu-button {
  background: transparent;
  border: none;
  color: #6c757d;
  font-size: 1.1rem;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-button:hover {
  background: #f8f9fa;
  color: #3498db;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: 2px solid #e9ecef;
  color: #6c757d;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.user-button:hover {
  border-color: #3498db;
  color: #3498db;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: #495057;
  font-weight: 500;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #dc3545;
  border: none;
  border-radius: 20px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.logout-button:hover {
  background: #c82333;
  transform: translateY(-1px);
}

.dev-login-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #28a745;
  border: none;
  border-radius: 20px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  margin-left: 0.5rem;
}

.dev-login-button:hover {
  background: #218838;
  transform: translateY(-1px);
}

/* 主要内容区域 */
.main-content {
  flex: 1;
  padding: 2rem 0;
  margin-top: 70px; /* 为顶部导航栏留出空间 */
  width: 100% !important;
  max-width: none !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

.content-container {
  max-width: none !important;
  margin: 0 !important;
  padding: 0;
  display: flex;
  gap: 1.5rem;
  width: 100% !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

/* 侧边栏 */
.sidebar {
  width: 220px;
  min-width: 220px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.25rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  height: fit-content;
  position: sticky;
  top: 100px;
}

.sidebar-collapsed {
  width: 80px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.sidebar-title i {
  color: #3498db;
}

.sidebar-toggle {
  background: transparent;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.sidebar-toggle:hover {
  background: #f8f9fa;
  color: #3498db;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #6c757d;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-item:hover {
  background: #f8f9fa;
  color: #3498db;
  transform: translateX(5px);
}

.nav-item.active {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
}

.nav-item i {
  width: 20px;
  text-align: center;
}

/* 主内容区 */
.main-area {
  flex: 1;
  min-height: calc(100vh - 70px);
  padding: 1rem 0;
  width: 100% !important;
  max-width: none !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-container {
    flex-direction: column;
    padding: 0;
  }
  
  .sidebar {
    width: 100%;
    position: static;
  }
  
  .sidebar-collapsed {
    width: 100%;
  }
}

@media (min-width: 1400px) {
  .papers-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (min-width: 1600px) {
  .papers-grid {
    grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-container {
    padding: 0;
    gap: 1rem;
  }
  
  .content-container {
    padding: 0;
  }
  
  .search-container {
    display: none;
  }
  
  .logo-text {
    display: none;
  }
}

/* 深色主题 */
[data-theme="dark"] .app-layout {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

[data-theme="dark"] .header {
  background: rgba(44, 62, 80, 0.95);
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .sidebar {
  background: rgba(44, 62, 80, 0.9);
}

[data-theme="dark"] .logo-link {
  color: #ecf0f1;
}

[data-theme="dark"] .search-box {
  background: #34495e;
}

[data-theme="dark"] .search-input {
  color: #ecf0f1;
}

[data-theme="dark"] .search-input::placeholder {
  color: #bdc3c7;
}
</style>
