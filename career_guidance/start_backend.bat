@echo off
echo 启动后端AI服务...
cd /d "%~dp0backend"
python career_ai_service.py
pause
