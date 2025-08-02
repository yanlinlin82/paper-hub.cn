#!/bin/bash

# 完整配置验证脚本
# 用于验证整个端口配置系统是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 完整配置验证${NC}"
echo "=================================="
echo ""

# 获取脚本所在目录的上级目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

echo -e "${YELLOW}📁 项目根目录: $PROJECT_ROOT${NC}"
echo ""

# 1. 检查 .env 文件
echo -e "${BLUE}1. 检查 .env 文件${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}✅ .env 文件存在${NC}"
else
    echo -e "${RED}❌ .env 文件不存在${NC}"
    exit 1
fi

# 2. 加载环境变量
echo -e "${BLUE}2. 加载环境变量${NC}"
source ./scripts/load-env.sh

# 3. 验证关键环境变量
echo -e "${BLUE}3. 验证关键环境变量${NC}"
FRONTEND_PORT=${FRONTEND_DEV_PORT:-5173}
BACKEND_PORT=${BACKEND_DEV_PORT:-8000}

echo -e "${YELLOW}   前端端口: $FRONTEND_PORT${NC}"
echo -e "${YELLOW}   后端端口: $BACKEND_PORT${NC}"
echo -e "${YELLOW}   API URL: http://localhost:$BACKEND_PORT/api${NC}"

# 4. 检查端口占用
echo -e "${BLUE}4. 检查端口占用${NC}"
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}   ❌ $service 端口 $port 已被占用${NC}"
        return 1
    else
        echo -e "${GREEN}   ✅ $service 端口 $port 可用${NC}"
        return 0
    fi
}

check_port $FRONTEND_PORT "前端"
check_port $BACKEND_PORT "后端"

# 5. 验证 Vite 配置
echo -e "${BLUE}5. 验证 Vite 配置${NC}"
if [ -f frontend/vite.config.ts ]; then
    echo -e "${GREEN}   ✅ vite.config.ts 文件存在${NC}"
    
    if grep -q "loadEnv" frontend/vite.config.ts; then
        echo -e "${GREEN}   ✅ 包含 loadEnv 函数${NC}"
    else
        echo -e "${RED}   ❌ 缺少 loadEnv 函数${NC}"
    fi
    
    if grep -q "path.resolve(__dirname, '..')" frontend/vite.config.ts; then
        echo -e "${GREEN}   ✅ 正确配置项目根目录路径${NC}"
    else
        echo -e "${RED}   ❌ 项目根目录路径配置有问题${NC}"
    fi
else
    echo -e "${RED}   ❌ vite.config.ts 文件不存在${NC}"
fi

# 6. 验证 package.json 脚本
echo -e "${BLUE}6. 验证 package.json 脚本${NC}"
if [ -f package.json ]; then
    echo -e "${GREEN}   ✅ package.json 文件存在${NC}"
    
    if grep -q "load-env.sh" package.json; then
        echo -e "${GREEN}   ✅ 包含环境变量加载脚本${NC}"
    else
        echo -e "${RED}   ❌ 缺少环境变量加载脚本${NC}"
    fi
    
    if grep -q "dev:frontend" package.json; then
        echo -e "${GREEN}   ✅ 包含前端开发脚本${NC}"
    else
        echo -e "${RED}   ❌ 缺少前端开发脚本${NC}"
    fi
    
    if grep -q "dev:backend" package.json; then
        echo -e "${GREEN}   ✅ 包含后端开发脚本${NC}"
    else
        echo -e "${RED}   ❌ 缺少后端开发脚本${NC}"
    fi
else
    echo -e "${RED}   ❌ package.json 文件不存在${NC}"
fi

# 7. 验证 Docker 配置
echo -e "${BLUE}7. 验证 Docker 配置${NC}"
if [ -f docker-compose.yml ]; then
    echo -e "${GREEN}   ✅ docker-compose.yml 文件存在${NC}"
    
    if grep -q "\${FRONTEND_CONTAINER_PORT" docker-compose.yml; then
        echo -e "${GREEN}   ✅ 支持前端容器端口环境变量${NC}"
    else
        echo -e "${RED}   ❌ 不支持前端容器端口环境变量${NC}"
    fi
    
    if grep -q "\${BACKEND_CONTAINER_PORT" docker-compose.yml; then
        echo -e "${GREEN}   ✅ 支持后端容器端口环境变量${NC}"
    else
        echo -e "${RED}   ❌ 不支持后端容器端口环境变量${NC}"
    fi
else
    echo -e "${RED}   ❌ docker-compose.yml 文件不存在${NC}"
fi

# 8. 验证脚本文件
echo -e "${BLUE}8. 验证脚本文件${NC}"
scripts=("load-env.sh" "port-config.sh" "test-config.sh" "test-env.sh" "test-vite-config.js")

for script in "${scripts[@]}"; do
    if [ -f "scripts/$script" ]; then
        echo -e "${GREEN}   ✅ scripts/$script 存在${NC}"
    else
        echo -e "${RED}   ❌ scripts/$script 不存在${NC}"
    fi
done

echo ""
echo -e "${BLUE}🎯 验证完成！${NC}"
echo ""
echo -e "${YELLOW}📋 使用说明:${NC}"
echo "1. 启动开发服务器: npm run dev"
echo "2. 启动前端: npm run dev:frontend"
echo "3. 启动后端: npm run dev:backend"
echo "4. 检查端口: npm run config:check"
echo "5. 测试配置: npm run config:test"
echo "6. 测试环境变量: npm run env:test"
echo "7. 测试Vite配置: npm run vite:test"
echo ""
echo -e "${GREEN}✅ 如果所有检查都通过，说明配置系统正常工作！${NC}" 