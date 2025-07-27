import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 使用现有的API端点
export const paperAPI = {
  // 获取论文列表
  getPapers: () => api.get('/papers/'),
  
  // 获取论文详情
  getPaperDetail: (id: number) => api.get(`/papers/${id}/`),
  
  // 添加论文
  addPaper: (identifier: string) => api.post('/papers/add/', { identifier }),
  
  // 搜索论文
  searchPapers: (query: string) => api.get('/papers/search/', { params: { q: query } }),
  
  // 添加评论
  addReview: (paperId: number, content: string, rating = 0) => 
    api.post(`/papers/${paperId}/reviews/`, { content, rating }),
  
  // 获取评论列表
  getReviews: (paperId: number) => api.get(`/papers/${paperId}/reviews/`)
}

export const authAPI = {
  // 登录
  login: (username: string, password: string) => 
    api.post('/auth/login/', { username, password }),
  
  // 登出
  logout: () => api.post('/auth/logout/'),
  
  // 获取用户信息
  getUserInfo: () => api.get('/auth/user/')
}

export default api 