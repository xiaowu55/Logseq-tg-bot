#!/bin/bash

# 检查配置文件
if [ ! -f "config/config.ini" ]; then
    echo "错误: 未找到配置文件 config/config.ini"
    echo "请复制 config.sample.ini 到 config/config.ini 并修改配置"
    exit 1
fi

# 创建必要的目录
mkdir -p logs

# 启动容器
docker-compose up -d

echo "Lupin Bot 已启动！"
echo "查看日志: docker-compose logs -f" 