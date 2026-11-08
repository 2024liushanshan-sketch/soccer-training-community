#!/bin/bash
# 后端服务启动脚本

cd "$(dirname "$0")"
echo "正在启动后端服务..."
echo "服务地址: http://127.0.0.1:8000"
echo "API文档: http://127.0.0.1:8000/docs"
echo "按 Ctrl+C 停止服务"
echo "================================"
python3 run.py

