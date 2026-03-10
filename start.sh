#!/bin/bash

echo "启动 OpenClaw 多实例管理系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，请先安装 Docker 和 Docker Compose"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 进入docker目录
cd docker

# 启动服务
docker-compose up -d

echo "服务启动中，请稍候..."
sleep 10

echo "服务启动完成！"
echo "管理后台地址：http://localhost"
echo "API接口地址：http://localhost:8000"
echo "管理员初始化：请在启动前设置 DEFAULT_ADMIN_PASSWORD 环境变量"
echo ""
echo "查看日志：docker-compose logs -f"
echo "停止服务：docker-compose down"
