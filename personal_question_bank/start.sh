#!/bin/bash

echo "======================================="
echo "  个性化题库系统启动脚本 (Linux/macOS)"
echo "======================================="
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 显示Python版本
echo "🐍 Python版本: $(python3 --version)"

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "💡 建议: 使用虚拟环境运行项目"
    echo "   创建虚拟环境: python3 -m venv venv"
    echo "   激活虚拟环境: source venv/bin/activate"
    echo
fi

# 检查依赖是否安装
echo "🔍 检查依赖包..."
if ! python3 -c "import flask, flask_sqlalchemy, pandas, numpy, sklearn" 2>/dev/null; then
    echo "📦 正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 错误: 依赖安装失败"
        exit 1
    fi
fi

# 创建logs目录（如果不存在）
mkdir -p logs

# 检查端口是否被占用
if command -v lsof &> /dev/null; then
    if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  警告: 端口5000已被占用"
        echo "   你可以修改run.py中的端口配置"
    fi
fi

# 启动应用
echo "🚀 启动个性化题库系统..."
python3 run.py
