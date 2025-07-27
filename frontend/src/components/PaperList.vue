<template>
  <div class="paper-list">
    <div class="header">
      <h2>论文列表</h2>
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          @input="handleSearch"
          placeholder="搜索论文..."
          class="search-input"
        />
      </div>
      <button @click="showAddForm = true" class="add-btn">添加论文</button>
    </div>

    <!-- 添加论文表单 -->
    <div v-if="showAddForm" class="add-form">
      <input 
        v-model="newPaperIdentifier" 
        placeholder="输入DOI或PMID"
        class="form-input"
      />
      <button @click="addPaper" :disabled="loading" class="form-btn">
        {{ loading ? '添加中...' : '添加' }}
      </button>
      <button @click="showAddForm = false" class="form-btn cancel">取消</button>
    </div>

    <!-- 论文列表 -->
    <div class="papers">
      <div v-for="paper in papers" :key="paper.id" class="paper-item">
        <h3>{{ paper.title }}</h3>
        <p class="authors">{{ paper.authors }}</p>
        <p class="journal">{{ paper.journal }}</p>
        <p class="abstract">{{ paper.abstract }}</p>
        <div class="meta">
          <span v-if="paper.doi">DOI: {{ paper.doi }}</span>
          <span v-if="paper.pmid">PMID: {{ paper.pmid }}</span>
          <span class="date">{{ formatDate(paper.created_at) }}</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { paperAPI } from '@/services/api'

interface Paper {
  id: number
  title: string
  authors: string
  journal: string
  abstract: string
  doi: string
  pmid: string
  created_at: string
}

const papers = ref<Paper[]>([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const showAddForm = ref(false)
const newPaperIdentifier = ref('')

const loadPapers = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await paperAPI.getPapers()
    papers.value = response.data.papers || []
  } catch (err) {
    error.value = '加载论文列表失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    await loadPapers()
    return
  }
  
  loading.value = true
  error.value = ''
  try {
    const response = await paperAPI.searchPapers(searchQuery.value)
    papers.value = response.data.papers || []
  } catch (err) {
    error.value = '搜索失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const addPaper = async () => {
  if (!newPaperIdentifier.value.trim()) {
    error.value = '请输入论文标识符'
    return
  }
  
  loading.value = true
  error.value = ''
  try {
    await paperAPI.addPaper(newPaperIdentifier.value)
    newPaperIdentifier.value = ''
    showAddForm.value = false
    await loadPapers()
  } catch (err) {
    error.value = '添加论文失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadPapers()
})
</script>

<style scoped>
.paper-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.add-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.add-btn:hover {
  background-color: #0056b3;
}

.add-form {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.form-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.form-btn:not(.cancel) {
  background-color: #28a745;
  color: white;
}

.form-btn.cancel {
  background-color: #6c757d;
  color: white;
}

.papers {
  display: grid;
  gap: 20px;
}

.paper-item {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.paper-item h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.authors {
  color: #666;
  font-size: 14px;
  margin: 5px 0;
}

.journal {
  color: #007bff;
  font-size: 14px;
  margin: 5px 0;
  font-weight: 500;
}

.abstract {
  color: #555;
  font-size: 14px;
  line-height: 1.5;
  margin: 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #888;
  margin-top: 10px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}
</style> 