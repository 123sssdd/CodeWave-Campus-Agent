@echo off
chcp 65001 >nul
echo 启动职业发展AI服务...

echo.
echo 检查环境...
where python >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到npm，请先安装Node.js
    pause
    exit /b 1
)

echo Python和Node.js环境检查通过

echo.
echo 1. 启动后端AI服务 (端口5001)...
cd /d "%~dp0"
if not exist "backend" (
    echo 错误: 找不到backend文件夹
    pause
    exit /b 1
)

start "AI后端服务" cmd /k "cd /d \"%~dp0backend\" && python career_ai_service.py"

echo.
echo 2. 等待5秒后启动前端服务...
timeout /t 5 /nobreak > nul

echo.
echo 3. 启动前端React应用 (端口3000)...
if not exist "package.json" (
    echo 错误: 找不到package.json文件
    pause
    exit /b 1
)

start "前端应用" cmd /k "cd /d \"%~dp0\" && npm start"

echo.
echo 服务启动完成！
echo - 后端AI服务: http://localhost:5001
echo - 前端应用: http://localhost:3000
echo.
echo 请等待服务完全启动后使用应用
echo 如果浏览器没有自动打开，请手动访问: http://localhost:3000
pause
