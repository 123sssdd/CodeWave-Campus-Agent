@echo off
echo.
echo =======================================
echo   个性化题库系统启动脚本 (Windows)
echo =======================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

:: 检查是否在虚拟环境中
python -c "import sys; exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo 建议: 使用虚拟环境运行项目
    echo 创建虚拟环境: python -m venv venv
    echo 激活虚拟环境: venv\Scripts\activate
    echo.
)

:: 检查依赖是否安装
echo 检查依赖包...
python -c "import flask, flask_sqlalchemy, pandas, numpy, sklearn" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

:: 启动应用
echo 启动个性化题库系统...
python run.py

pause
