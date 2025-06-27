#!/bin/bash

# 获取当前脚本所在目录
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# 启动 FastAPI 服务
gnome-terminal -- bash -c "cd $SCRIPT_DIR && uvicorn app.main:app --host 0.0.0.0 --port 8000; exec bash"

# 启动 Streamlit WebUI
gnome-terminal -- bash -c "cd $SCRIPT_DIR && streamlit run webui_api.py; exec bash"

echo "服务已启动，请检查窗口。"