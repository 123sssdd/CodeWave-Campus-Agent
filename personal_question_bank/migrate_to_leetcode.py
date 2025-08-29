#!/usr/bin/env python3
"""
数据库迁移脚本：从模拟数据迁移到LeetCode真实数据
"""

from app import app, db
from leetcode_integration import LeetCodeIntegration, clear_existing_data

def migrate_database():
    """执行数据库迁移"""
    print("=== 数据库迁移：集成LeetCode题库 ===\n")
    
    with app.app_context():
        # 1. 创建新的数据库字段
        print("1. 更新数据库结构...")
        try:
            # 检查是否需要添加新字段
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('questions')]
            
            if 'external_source' not in columns:
                print("   添加新字段...")
                db.engine.execute("""
                    ALTER TABLE questions 
                    ADD COLUMN external_source VARCHAR(50),
                    ADD COLUMN tags TEXT,
                    ADD COLUMN acceptance_rate FLOAT,
                    ADD COLUMN likes_count INTEGER DEFAULT 0,
                    ADD COLUMN dislikes_count INTEGER DEFAULT 0
                """)
                print("   ✅ 数据库结构更新完成")
            else:
                print("   ✅ 数据库结构已是最新")
        except Exception as e:
            print(f"   ⚠️  数据库结构更新失败: {e}")
            print("   继续使用现有结构...")
        
        # 2. 询问是否清除现有数据
        print("\n2. 数据迁移选项:")
        print("   a) 清除所有现有数据，导入LeetCode题目")
        print("   b) 保留现有数据，追加LeetCode题目")
        print("   c) 仅更新数据库结构，不导入题目")
        
        choice = input("\n请选择 (a/b/c): ").lower()
        
        if choice == 'a':
            print("\n正在清除现有数据...")
            clear_existing_data()
            print("✅ 现有数据已清除")
            
            print("\n正在导入LeetCode题目...")
            leetcode = LeetCodeIntegration()
            leetcode.import_problems(limit=30)  # 导入30道经典题目
            
        elif choice == 'b':
            print("\n正在追加LeetCode题目...")
            leetcode = LeetCodeIntegration()
            leetcode.import_problems(limit=20)  # 导入20道题目作为补充
            
        elif choice == 'c':
            print("\n仅更新数据库结构，跳过数据导入")
            
        else:
            print("无效选择，退出迁移")
            return
        
        print("\n=== 迁移完成 ===")
        print("现在您可以重启应用，享受真实的LeetCode题目！")

if __name__ == "__main__":
    migrate_database()
