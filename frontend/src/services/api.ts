import axios from 'axios'

// 配置axios基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加时间戳防止缓存
    if (config.method === 'get') {
      config.params = { ...config.params, _t: Date.now() }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  },
)

// 类型定义
export interface Paper {
  id: number
  title: string
  authors: string
  journal: string
  abstract: string
  category: string
  created_at: string
  views: number
  likes: number
}

export interface Stats {
  totalPapers: number
  totalUsers: number
  thisMonthPapers: number
  topContributor: number
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

// API函数
export const api = {
  // 用户登录
  async login(username: string, password: string): Promise<any> {
    try {
      const response = await apiClient.post('/login', {
        username: username,
        password: password
      })
      return response.data
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  },

  // 获取统计数据
  async getStats(): Promise<Stats> {
    try {
      const response = await apiClient.get('/data')
      if (response.data.success) {
        return response.data.stats
      } else {
        throw new Error(response.data.error || '获取统计数据失败')
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
      // 返回默认数据
      return {
        totalPapers: 0,
        totalUsers: 0,
        thisMonthPapers: 0,
        topContributor: 0
      }
    }
  },

  // 获取最新论文
  async getRecentPapers(): Promise<Paper[]> {
    try {
      const response = await apiClient.get('/data')
      if (response.data.success) {
        return response.data.recentPapers
      } else {
        throw new Error(response.data.error || '获取最新论文失败')
      }
    } catch (error) {
      console.error('Error fetching recent papers:', error)
      return []
    }
  },

  // 获取论文列表
  async getPapers(mode: 'all' | 'this-month' | 'last-month' = 'all'): Promise<Paper[]> {
    try {
      // 使用真实数据API
      const response = await apiClient.get('/data')
      if (response.data.success) {
        return response.data.recentPapers
      } else {
        throw new Error(response.data.error || '获取论文列表失败')
      }
    } catch (error) {
      console.error('Error fetching papers:', error)
      return []
    }
  },

  // 获取排行榜
  async getRankings(): Promise<any[]> {
    try {
      // 榜单数据是公开的，不需要token
      const groupName = 'xiangma'
      
      const response = await apiClient.post('/fetch_rank_list', {
        group_name: groupName
      })

      if (response.data.success) {
        return response.data.results || []
      } else {
        console.error('Failed to fetch rankings:', response.data.error)
        return []
      }
    } catch (error) {
      console.error('Error fetching rankings:', error)
      // 返回空数组，不使用模拟数据
      return []
    }
  },

  // 获取特定类型的榜单
  async getRankingByType(rankType: string, year?: number, month?: number): Promise<any> {
    try {
      const groupName = 'xiangma'
      
      const requestData: any = {
        group_name: groupName,
        rank_type: rankType
      }
      
      if (year) requestData.year = year
      if (month) requestData.month = month

      const response = await apiClient.post('/fetch_rank_by_type', requestData)
      
      if (response.data.success) {
        return response.data.result
      } else {
        console.error('Failed to fetch ranking by type:', response.data.error)
        return null
      }
    } catch (error) {
      console.error('Error fetching ranking by type:', error)
      return null
    }
  },

  // 根据期刊获取分类
  getCategoryFromJournal(journal: string): string {
    if (!journal) return '其他'
    
    const journalLower = journal.toLowerCase()
    if (journalLower.includes('nature') || journalLower.includes('science')) {
      return '顶级期刊'
    } else if (journalLower.includes('machine learning') || journalLower.includes('ai')) {
      return 'AI/ML'
    } else if (journalLower.includes('quantum')) {
      return 'Quantum'
    } else if (journalLower.includes('energy') || journalLower.includes('environmental')) {
      return 'Energy'
    } else if (journalLower.includes('biomedical') || journalLower.includes('medical')) {
      return 'Biomedical'
    } else {
      return '其他'
    }
  }
}

// 工具函数
export const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export const formatNumber = (num: number) => {
  return num.toLocaleString()
}

// Cookie工具函数
export const getCookie = (name: string): string | null => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null
  return null
}

export default api
