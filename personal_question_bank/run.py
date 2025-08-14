#!/usr/bin/env python3
"""
个性化题库系统启动脚本
运行此脚本以启动Web应用程序
"""

import os
import sys
from app import app, db, create_tables
from data_generator import generate_sample_data
from models import User

def check_dependencies():
    """检查必要的依赖"""
    try:
        import flask
        import flask_sqlalchemy
        import pandas
        import numpy
        import sklearn
        print("✅ 所有依赖已正确安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def init_database():
    """初始化数据库"""
    try:
        # 调用应用的数据库初始化函数
        create_tables()
        print("✅ 数据库表创建成功")
        
        with app.app_context():
            # 显示示例用户信息
            users = User.query.all()
            if users:
                print("\n📋 可用的示例用户:")
                for user in users:
                    print(f"   - {user.username} ({user.email}) - {user.preferred_difficulty}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_welcome():
    """打印欢迎信息"""
    print("""
🎓 ================================
   个性化题库系统
   Personalized Question Bank
🎓 ================================

🌟 主要特色:
   • 智能题目推荐
   • 多语言在线编程
   • 学习进度分析
   • 个性化学习路径

🚀 系统启动中...
""")

def print_startup_info():
    """打印启动信息"""
    print("""
🎉 系统启动成功！

📱 访问地址:
   • 本地访问: http://localhost:5000
   • 网络访问: http://0.0.0.0:5000

🔧 系统功能:
   • 首页: 用户选择和系统介绍
   • 练习模式: 个性化题目推荐和在线答题
   • 学习统计: 详细的学习数据分析

💡 使用提示:
   1. 选择一个预设用户开始体验
   2. 在练习模式中答题获得个性化推荐
   3. 查看学习统计了解你的进步情况

⌨️  按 Ctrl+C 停止服务器
""")

def main():
    """主启动函数"""
    print_welcome()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 初始化数据库
    if not init_database():
        sys.exit(1)
    
    # 设置Flask配置
    app.config['DEBUG'] = True
    app.config['HOST'] = '0.0.0.0'
    app.config['PORT'] = 5000
    
    # 打印启动信息
    print_startup_info()
    
    try:
        # 启动应用
        app.run(
            debug=True,
            host=app.config['HOST'],
            port=app.config['PORT'],
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 感谢使用个性化题库系统！")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
