#!/usr/bin/env python3
"""
重新生成数据库数据脚本
用于添加更多题目并重置学习记录
"""

import os
import sys
from app import app, db
from models import User, Question, LearningRecord, KnowledgePoint, UserKnowledgeStats
from data_generator import generate_sample_data

def regenerate_database():
    """重新生成数据库"""
    print("🔄 开始重新生成数据库...")
    
    with app.app_context():
        # 删除现有数据
        print("📝 清空现有数据...")
        LearningRecord.query.delete()
        UserKnowledgeStats.query.delete()
        Question.query.delete()
        User.query.delete()
        KnowledgePoint.query.delete()
        db.session.commit()
        
        # 重新生成数据
        print("🔄 生成新的示例数据...")
        generate_sample_data()
        
        # 显示统计信息
        users_count = User.query.count()
        questions_count = Question.query.count()
        kp_count = KnowledgePoint.query.count()
        records_count = LearningRecord.query.count()
        
        print(f"""
✅ 数据库重新生成完成！
📊 统计信息:
   - 用户: {users_count} 个
   - 知识点: {kp_count} 个  
   - 题目: {questions_count} 个
   - 学习记录: {records_count} 条
   
🎯 现在系统有更多题目可供推荐了！
""")

if __name__ == "__main__":
    regenerate_database()
