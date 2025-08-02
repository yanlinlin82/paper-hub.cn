# 部署指南

## 部署方案对比

### 1. 开发环境（推荐）
```bash
# 启动开发服务器
npm run dev
```
- 前端：http://localhost:5173
- 后端：http://localhost:8000
- 适合：本地开发和调试

### 2. Docker容器化部署（推荐）
```bash
# 构建并启动所有服务
npm run docker:build
npm run docker:up

# 查看日志
npm run docker:logs

# 停止服务
npm run docker:down
```
- 访问：http://localhost
- 适合：生产环境、CI/CD

### 3. 传统部署（不推荐）
```bash
# 将前端构建产物复制到Django
npm run deploy:legacy
```
- 访问：http://localhost:8000/vue-app
- 适合：简单的单服务器部署

## 现代化部署架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Frontend      │    │   Backend       │
│   (Port 80)     │◄──►│   (Vue.js)      │    │   (Django)      │
│                 │    │   (Port 3000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │   (PostgreSQL)  │
                    └─────────────────┘
```

## 环境变量配置

### 前端环境变量
```bash
# frontend/.env.production
VITE_API_BASE_URL=https://api.example.com/api
```

### 后端环境变量
```bash
# backend/.env
DJANGO_ENV=production
DJANGO_DEBUG=False
DATABASE_URL=postgresql://user:pass@db:5432/paperhub
SECRET_KEY=your-secret-key
```

## 生产环境部署

### 使用Docker Compose
```bash
# 1. 设置环境变量
cp .env.example .env
# 编辑.env文件

# 2. 构建和启动
docker-compose -f docker-compose.prod.yml up -d

# 3. 运行数据库迁移
docker-compose exec backend python manage.py migrate

# 4. 创建超级用户
docker-compose exec backend python manage.py createsuperuser
```

### 使用云服务

#### 前端部署到Vercel
```bash
# 1. 安装Vercel CLI
npm i -g vercel

# 2. 部署前端
cd frontend
vercel --prod
```

#### 后端部署到Railway/Heroku
```bash
# 1. 安装CLI工具
# 2. 部署后端
railway up
# 或
heroku create
git push heroku main
```

## 监控和日志

### 查看应用状态
```bash
# Docker环境
docker-compose ps
docker-compose logs -f

# 系统资源
docker stats
```

### 性能监控
- 前端：使用Vue DevTools和浏览器开发者工具
- 后端：使用Django Debug Toolbar
- 数据库：使用pgAdmin或DBeaver

## 安全配置

### HTTPS配置
```nginx
# nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... 其他配置
}
```

### 安全头设置
```nginx
# 在nginx配置中添加
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

## 备份和恢复

### 数据库备份
```bash
# 备份
docker-compose exec db pg_dump -U paperhub paperhub > backup.sql

# 恢复
docker-compose exec -T db psql -U paperhub paperhub < backup.sql
```

### 文件备份
```bash
# 备份静态文件
tar -czf static_backup.tar.gz backend/static_root/

# 恢复静态文件
tar -xzf static_backup.tar.gz
``` 