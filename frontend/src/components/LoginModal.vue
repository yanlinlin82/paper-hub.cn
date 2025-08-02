<template>
  <div v-if="show" class="login-modal-overlay" @click="closeModal">
    <div class="login-modal" @click.stop>
      <div class="modal-header">
        <h3>登录</h3>
        <button class="close-button" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="login-tabs">
          <button 
            class="tab-button"
            :class="{ active: activeTab === 'password' }"
            @click="activeTab = 'password'"
          >
            密码登录
          </button>
          <button 
            class="tab-button"
            :class="{ active: activeTab === 'wechat' }"
            @click="activeTab = 'wechat'"
          >
            微信登录
          </button>
        </div>
        
        <!-- 密码登录 -->
        <div v-if="activeTab === 'password'" class="login-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input 
              id="username"
              v-model="loginForm.username"
              type="text"
              placeholder="请输入用户名"
              @keyup.enter="handlePasswordLogin"
            />
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <input 
              id="password"
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              @keyup.enter="handlePasswordLogin"
            />
          </div>
          
          <button 
            class="login-button"
            @click="handlePasswordLogin"
            :disabled="loading"
          >
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>
        
        <!-- 微信登录 -->
        <div v-if="activeTab === 'wechat'" class="wechat-login">
          <div class="wechat-qr">
            <i class="fab fa-weixin"></i>
            <p>请使用微信扫码登录</p>
          </div>
          <button class="wechat-button" @click="handleWechatLogin">
            获取微信登录二维码
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { api } from '@/services/api'

interface Props {
  show: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'login-success', data: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const activeTab = ref('password')
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const closeModal = () => {
  emit('close')
}

const handlePasswordLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    alert('请输入用户名和密码')
    return
  }
  
  try {
    loading.value = true
    const response = await api.login(loginForm.username, loginForm.password)
    
    if (response.success) {
      // 存储token到cookie
      document.cookie = `token=${response.token}; path=/; max-age=86400`
      emit('login-success', response)
      closeModal()
    } else {
      alert(response.error || '登录失败')
    }
  } catch (error) {
    console.error('Login error:', error)
    alert('登录失败，请重试')
  } finally {
    loading.value = false
  }
}

const handleWechatLogin = async () => {
  try {
    // 这里应该调用微信登录API
    alert('微信登录功能开发中...')
  } catch (error) {
    console.error('WeChat login error:', error)
    alert('微信登录失败，请重试')
  }
}
</script>

<style scoped>
.login-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.login-modal {
  background: white;
  border-radius: 15px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-button:hover {
  background: #f8f9fa;
  color: #495057;
}

.modal-body {
  padding: 1.5rem;
}

.login-tabs {
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.tab-button {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  color: #6c757d;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.tab-button.active {
  color: #007bff;
  border-bottom-color: #007bff;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #495057;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.login-button {
  padding: 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.login-button:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.login-button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.wechat-login {
  text-align: center;
  padding: 2rem 0;
}

.wechat-qr {
  margin-bottom: 1.5rem;
}

.wechat-qr i {
  font-size: 4rem;
  color: #07c160;
  margin-bottom: 1rem;
}

.wechat-qr p {
  color: #6c757d;
  margin: 0;
}

.wechat-button {
  padding: 0.75rem 1.5rem;
  background: #07c160;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.wechat-button:hover {
  background: #06ad56;
  transform: translateY(-1px);
}

/* 深色主题 */
[data-theme="dark"] .login-modal {
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

[data-theme="dark"] .modal-header h3 {
  color: #ecf0f1;
}

[data-theme="dark"] .close-button {
  color: #bdc3c7;
}

[data-theme="dark"] .close-button:hover {
  background: rgba(52, 73, 94, 0.5);
  color: #ecf0f1;
}

[data-theme="dark"] .tab-button {
  color: #bdc3c7;
}

[data-theme="dark"] .tab-button.active {
  color: #007bff;
}

[data-theme="dark"] .form-group label {
  color: #ecf0f1;
}

[data-theme="dark"] .form-group input {
  background: rgba(52, 73, 94, 0.5);
  border-color: rgba(255, 255, 255, 0.2);
  color: #ecf0f1;
}

[data-theme="dark"] .form-group input:focus {
  border-color: #007bff;
}

[data-theme="dark"] .wechat-qr p {
  color: #bdc3c7;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .modal-body {
    padding: 1rem;
  }
  
  .login-tabs {
    flex-direction: column;
  }
  
  .tab-button {
    border-bottom: none;
    border-right: 2px solid transparent;
  }
  
  .tab-button.active {
    border-bottom: none;
    border-right-color: #007bff;
  }
}
</style> 