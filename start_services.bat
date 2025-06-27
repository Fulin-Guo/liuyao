@echo off

:: 设置编码为 UTF-8
chcp 65001

:: 获取当前脚本所在目录
set SCRIPT_DIR=%~dp0

:: 启动 FastAPI 服务
start cmd /k "cd /d %SCRIPT_DIR% && uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: 启动 Streamlit WebUI
start cmd /k "cd /d %SCRIPT_DIR% && streamlit run webui_api.py"

echo 服务已启动，请检查窗口。
pause