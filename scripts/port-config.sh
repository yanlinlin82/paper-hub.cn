#!/bin/bash

# 端口配置脚本
# 用于快速设置和验证前后端端口配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
DEFAULT_FRONTEND_PORT=5173
DEFAULT_BACKEND_PORT=8000
DEFAULT_NGINX_PORT=80
DEFAULT_DB_PORT=5432

# 显示帮助信息
show_help() {
    echo -e "${BLUE}端口配置脚本${NC}"
    echo ""
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -f, --frontend PORT    设置前端端口 (默认: $DEFAULT_FRONTEND_PORT)"
    echo "  -b, --backend PORT     设置后端端口 (默认: $DEFAULT_BACKEND_PORT)"
    echo "  -n, --nginx PORT       设置Nginx端口 (默认: $DEFAULT_NGINX_PORT)"
    echo "  -d, --db PORT          设置数据库端口 (默认: $DEFAULT_DB_PORT)"
    echo "  -c, --check            检查端口占用情况"
    echo "  -g, --generate         生成.env文件"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -f 3000 -b 8001     # 设置前端端口3000，后端端口8001"
    echo "  $0 --check              # 检查端口占用"
    echo "  $0 --generate           # 生成.env文件"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ 端口 $port 已被占用${NC}"
        lsof -Pi :$port -sTCP:LISTEN
        return 1
    else
        echo -e "${GREEN}✅ 端口 $port 可用${NC}"
        return 0
    fi
}

# 检查所有端口
check_all_ports() {
    echo -e "${BLUE}检查端口占用情况...${NC}"
    echo ""
    
    local frontend_port=${FRONTEND_DEV_PORT:-$DEFAULT_FRONTEND_PORT}
    local backend_port=${BACKEND_DEV_PORT:-$DEFAULT_BACKEND_PORT}
    local nginx_port=${NGINX_PORT:-$DEFAULT_NGINX_PORT}
    local db_port=${DB_PORT:-$DEFAULT_DB_PORT}
    
    echo -e "${YELLOW}前端端口 ($frontend_port):${NC}"
    check_port $frontend_port "前端"
    
    echo -e "${YELLOW}后端端口 ($backend_port):${NC}"
    check_port $backend_port "后端"
    
    echo -e "${YELLOW}Nginx端口 ($nginx_port):${NC}"
    check_port $nginx_port "Nginx"
    
    echo -e "${YELLOW}数据库端口 ($db_port):${NC}"
    check_port $db_port "数据库"
}

# 生成.env文件
generate_env_file() {
    local frontend_port=${FRONTEND_DEV_PORT:-$DEFAULT_FRONTEND_PORT}
    local backend_port=${BACKEND_DEV_PORT:-$DEFAULT_BACKEND_PORT}
    local nginx_port=${NGINX_PORT:-$DEFAULT_NGINX_PORT}
    local db_port=${DB_PORT:-$DEFAULT_DB_PORT}
    
    echo -e "${BLUE}生成 .env 文件...${NC}"
    
    cat > .env << EOF
# 环境配置文件
# 生成时间: $(date)

# ===== 开发环境配置 =====
FRONTEND_DEV_PORT=$frontend_port
BACKEND_DEV_PORT=$backend_port
VITE_API_BASE_URL=http://localhost:$backend_port/api

# ===== 生产环境配置 =====
FRONTEND_CONTAINER_PORT=$frontend_port
BACKEND_CONTAINER_PORT=$backend_port
NGINX_PORT=$nginx_port
PRODUCTION_API_BASE_URL=http://localhost:$backend_port/api

# ===== 数据库配置 =====
DB_PORT=$db_port
DB_NAME=paperhub
DB_USER=paperhub
DB_PASSWORD=password

# ===== Django配置 =====
DJANGO_ENV=production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here

# ===== 域名配置 =====
DOMAIN=localhost
EOF

    echo -e "${GREEN}✅ .env 文件已生成${NC}"
}

# 验证端口配置
validate_config() {
    local frontend_port=${FRONTEND_DEV_PORT:-$DEFAULT_FRONTEND_PORT}
    local backend_port=${BACKEND_DEV_PORT:-$DEFAULT_BACKEND_PORT}
    
    echo -e "${BLUE}验证端口配置...${NC}"
    echo ""
    
    # 检查端口范围
    if [ $frontend_port -lt 1024 ] || [ $frontend_port -gt 65535 ]; then
        echo -e "${RED}❌ 前端端口 $frontend_port 超出有效范围 (1024-65535)${NC}"
        return 1
    fi
    
    if [ $backend_port -lt 1024 ] || [ $backend_port -gt 65535 ]; then
        echo -e "${RED}❌ 后端端口 $backend_port 超出有效范围 (1024-65535)${NC}"
        return 1
    fi
    
    # 检查端口冲突
    if [ $frontend_port -eq $backend_port ]; then
        echo -e "${RED}❌ 前端和后端端口不能相同${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ 端口配置验证通过${NC}"
    echo -e "${YELLOW}前端端口: $frontend_port${NC}"
    echo -e "${YELLOW}后端端口: $backend_port${NC}"
    echo -e "${YELLOW}API URL: http://localhost:$backend_port/api${NC}"
}

# 主函数
main() {
    local check_only=false
    local generate_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--frontend)
                export FRONTEND_DEV_PORT="$2"
                shift 2
                ;;
            -b|--backend)
                export BACKEND_DEV_PORT="$2"
                shift 2
                ;;
            -n|--nginx)
                export NGINX_PORT="$2"
                shift 2
                ;;
            -d|--db)
                export DB_PORT="$2"
                shift 2
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            -g|--generate)
                generate_only=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}未知选项: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 执行相应操作
    if [ "$check_only" = true ]; then
        check_all_ports
    elif [ "$generate_only" = true ]; then
        generate_env_file
    else
        validate_config
        echo ""
        check_all_ports
        echo ""
        echo -e "${BLUE}启动开发服务器:${NC}"
        echo -e "${YELLOW}npm run dev:custom${NC}"
        echo ""
        echo -e "${BLUE}启动Docker服务:${NC}"
        echo -e "${YELLOW}npm run docker:custom${NC}"
    fi
}

# 运行主函数
main "$@" 