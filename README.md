# Paper Hub

A modern web application for managing and exploring academic papers.

## Quick Start

1. **Initial Setup**
   ```bash
   npm run setup
   ```

2. **Start Development**
   ```bash
   npm run dev
   ```

3. **Make Changes**
   - Frontend: Edit files in `frontend/src/`
   - Backend: Edit files in `backend/`

4. **Code Quality**
   ```bash
   npm run format  # Format code
   npm run lint    # Check code quality
   ```

5. **Testing**
   ```bash
   npm run test    # Run all tests
   ```

## 端口配置指南

### 快速配置

使用端口配置脚本快速设置和验证端口：

```bash
# 检查当前端口占用情况
npm run config:check

# 设置自定义端口并生成配置文件
./scripts/port-config.sh -f 3000 -b 8001 --generate

# 查看帮助信息
./scripts/port-config.sh --help
```

### 环境变量配置

#### 开发环境

创建 `.env` 文件（参考 `env.example`）：

```bash
# 前端开发服务器端口
FRONTEND_DEV_PORT=5173

# 后端开发服务器端口
BACKEND_DEV_PORT=8000

# 前端API基础URL
VITE_API_BASE_URL=http://localhost:8000/api
```

#### 生产环境

```bash
# Docker容器端口映射
FRONTEND_CONTAINER_PORT=3000
BACKEND_CONTAINER_PORT=8000
NGINX_PORT=80

# 生产环境API基础URL
PRODUCTION_API_BASE_URL=http://localhost:8000/api
```

### 启动方式

#### 1. 默认端口启动
```bash
npm run dev
```

#### 2. 自定义端口启动
```bash
# 设置环境变量
export FRONTEND_DEV_PORT=3000
export BACKEND_DEV_PORT=8001

# 启动开发服务器
npm run dev:custom
```

#### 3. Docker启动
```bash
# 使用默认配置
npm run docker:up

# 使用自定义配置
npm run docker:custom
```

### 环境变量加载

项目使用自动环境变量加载系统，确保 `.env` 文件中的配置能够正确传递给前后端服务：

#### 自动加载机制

1. **前端环境变量**：Vite 自动从项目根目录的 `.env` 文件加载环境变量
2. **后端环境变量**：通过 `load-env.sh` 脚本在启动前加载环境变量
3. **Docker环境变量**：通过 `--env-file .env` 参数加载环境变量

#### 测试环境变量

```bash
# 测试环境变量加载
npm run env:test

# 测试Vite配置
npm run vite:test

# 测试端口配置
npm run config:test
```

#### 环境变量优先级

1. 命令行环境变量（最高优先级）
2. `.env` 文件中的变量
3. 默认值（最低优先级）

### 端口配置说明

| 服务 | 默认端口 | 环境变量 | 说明 |
|------|----------|----------|------|
| 前端开发服务器 | 5173 | `FRONTEND_DEV_PORT` | Vite开发服务器 |
| 后端开发服务器 | 8000 | `BACKEND_DEV_PORT` | Django开发服务器 |
| 前端容器 | 3000 | `FRONTEND_CONTAINER_PORT` | Docker容器端口 |
| 后端容器 | 8000 | `BACKEND_CONTAINER_PORT` | Docker容器端口 |
| Nginx | 80 | `NGINX_PORT` | 反向代理端口 |
| 数据库 | 5432 | `DB_PORT` | PostgreSQL端口 |

### 端口冲突解决

1. **检查端口占用**
   ```bash
   npm run config:check
   ```

2. **修改端口配置**
   ```bash
   # 修改前端端口
   export FRONTEND_DEV_PORT=3001
   
   # 修改后端端口
   export BACKEND_DEV_PORT=8001
   ```

3. **重新启动服务**
   ```bash
   npm run dev:custom
   ```

### API对接配置

前端会自动根据后端端口配置API基础URL：

- **开发环境**：通过Vite代理自动转发 `/api` 请求
- **生产环境**：通过Nginx反向代理转发请求
- **自定义配置**：通过 `VITE_API_BASE_URL` 环境变量指定

## Environment Variables

### Backend (.env file in backend/ directory)

```txt
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

### Frontend (.env file in frontend/ directory)

```txt
VITE_API_BASE_URL=http://localhost:8000/api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
