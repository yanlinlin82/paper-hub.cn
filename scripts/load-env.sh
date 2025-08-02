#!/bin/bash

# 加载环境变量脚本
# 用于在运行其他脚本前加载 .env 文件中的环境变量

# 获取脚本所在目录的上级目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 加载 .env 文件
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    # 使用 export 导出所有非注释的环境变量
    while IFS= read -r line; do
        # 跳过空行和注释行
        if [[ ! -z "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
            # 导出环境变量
            export "$line"
        fi
    done < .env
    echo "Environment variables loaded successfully."
else
    echo "Warning: .env file not found, using default values."
fi

# 执行传入的命令
exec "$@"
