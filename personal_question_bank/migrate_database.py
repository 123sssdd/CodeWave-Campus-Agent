#!/usr/bin/env python3
"""
数据库迁移脚本
用于添加双模式支持的新字段
"""

import sqlite3
import os
from app import app

def migrate_database():
    """迁移数据库添加新字段"""
    
    db_path = 'instance/question_bank.db'
    
    print("🔄 开始数据库迁移...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查并添加新字段到users表
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN preferred_mode VARCHAR(20) DEFAULT 'academic'")
            print("✅ 已添加 users.preferred_mode 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️  users.preferred_mode 字段已存在")
            else:
                print(f"❌ 添加 users.preferred_mode 失败: {e}")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN current_preparation_goal VARCHAR(100)")
            print("✅ 已添加 users.current_preparation_goal 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️  users.current_preparation_goal 字段已存在")
            else:
                print(f"❌ 添加 users.current_preparation_goal 失败: {e}")
        
        # 检查并添加新字段到knowledge_points表
        try:
            cursor.execute("ALTER TABLE knowledge_points ADD COLUMN question_bank_mode VARCHAR(20) DEFAULT 'academic'")
            print("✅ 已添加 knowledge_points.question_bank_mode 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️  knowledge_points.question_bank_mode 字段已存在")
            else:
                print(f"❌ 添加 knowledge_points.question_bank_mode 失败: {e}")
        
        # 检查并添加新字段到questions表
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN question_bank_mode VARCHAR(20) DEFAULT 'academic'")
            print("✅ 已添加 questions.question_bank_mode 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️  questions.question_bank_mode 字段已存在")
            else:
                print(f"❌ 添加 questions.question_bank_mode 失败: {e}")
                
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN interview_company_type VARCHAR(50)")
            print("✅ 已添加 questions.interview_company_type 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️  questions.interview_company_type 字段已存在")
            else:
                print(f"❌ 添加 questions.interview_company_type 失败: {e}")
                
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN interview_position VARCHAR(100)")
            print("✅ 已添加 questions.interview_position 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️  questions.interview_position 字段已存在")
            else:
                print(f"❌ 添加 questions.interview_position 失败: {e}")
                
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN interview_experience_level VARCHAR(20)")
            print("✅ 已添加 questions.interview_experience_level 字段")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("⚠️  questions.interview_experience_level 字段已存在")
            else:
                print(f"❌ 添加 questions.interview_experience_level 失败: {e}")
        
        # 创建面试准备计划表
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interview_preparation_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    target_position VARCHAR(100) NOT NULL,
                    target_company_type VARCHAR(50),
                    target_experience_level VARCHAR(20),
                    preparation_start_date DATE NOT NULL,
                    target_interview_date DATE,
                    total_questions_planned INTEGER DEFAULT 0,
                    questions_completed INTEGER DEFAULT 0,
                    focus_technologies TEXT,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            print("✅ 已创建 interview_preparation_plans 表")
        except sqlite3.OperationalError as e:
            print(f"❌ 创建 interview_preparation_plans 表失败: {e}")
        
        conn.commit()
        conn.close()
        
        print("🎉 数据库迁移完成！")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_database()
