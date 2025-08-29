#!/usr/bin/env python3
"""
导入增强的学术题库
包含更丰富的计算机科学基础知识题目
"""

import json
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import KnowledgePoint, Question

def import_enhanced_academic_questions():
    """导入增强的学术题库"""
    
    # 读取JSON文件
    json_file = 'enhanced_academic_questions.json'
    if not os.path.exists(json_file):
        print(f"❌ 找不到文件: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🚀 开始导入增强的学术题库...")
    
    with app.app_context():
        # 不清空现有题库，而是添加新的题目
        print("📝 检查现有学术题库...")
        existing_academic_questions = Question.query.filter_by(question_bank_mode='academic').count()
        existing_academic_kps = KnowledgePoint.query.filter_by(question_bank_mode='academic').count()
        
        print(f"📊 当前学术题库: {existing_academic_kps} 个知识点, {existing_academic_questions} 道题目")
        print("➕ 开始添加新的增强题库内容...")
        
        # 导入新的知识点和题目
        total_kp_count = 0
        total_question_count = 0
        
        for kp_data in data['knowledge_points']:
            # 创建知识点
            knowledge_point = KnowledgePoint(
                name=kp_data['name'],
                category=kp_data['category'],
                description=kp_data['description'],
                question_bank_mode='academic'  # 标记为学术模式
            )
            
            db.session.add(knowledge_point)
            db.session.flush()  # 获取ID
            
            print(f"📚 创建知识点: {kp_data['name']} (分类: {kp_data['category']})")
            total_kp_count += 1
            
            # 导入该知识点下的题目
            for q_data in kp_data['questions']:
                question = Question(
                    title=q_data['title'],
                    content=q_data['content'],
                    question_type=q_data['type'],  # 注意字段名是question_type
                    difficulty=q_data['difficulty'],
                    estimated_time=q_data['estimated_time'],
                    knowledge_point_id=knowledge_point.id,
                    question_bank_mode='academic'  # 标记为学术模式
                )
                
                # 设置参考答案
                if 'reference_answer' in q_data:
                    question.correct_answer = q_data['reference_answer']  # 设置正确答案
                    question.explanation = q_data['reference_answer']  # 同时设置解释
                
                # 标签信息暂时不存储（模型中没有tags字段）
                
                db.session.add(question)
                total_question_count += 1
                
                print(f"  ➕ 题目: {q_data['title']} ({q_data['difficulty']}, {q_data['points']}分)")
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"\n🎉 导入完成!")
            print(f"📊 统计信息:")
            print(f"   - 知识点数量: {total_kp_count}")
            print(f"   - 题目数量: {total_question_count}")
            print(f"   - 涵盖分类: {len(set(kp['category'] for kp in data['knowledge_points']))}")
            
            # 显示分类统计
            categories = {}
            for kp_data in data['knowledge_points']:
                category = kp_data['category']
                if category not in categories:
                    categories[category] = {'kp_count': 0, 'q_count': 0}
                categories[category]['kp_count'] += 1
                categories[category]['q_count'] += len(kp_data['questions'])
            
            print(f"\n📋 分类详情:")
            for category, stats in categories.items():
                print(f"   - {category}: {stats['kp_count']}个知识点, {stats['q_count']}道题目")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ 导入失败: {str(e)}")
            raise

def verify_import():
    """验证导入结果"""
    with app.app_context():
        # 统计学术模式的题库
        academic_kps = KnowledgePoint.query.filter_by(question_bank_mode='academic').all()
        academic_questions = Question.query.filter_by(question_bank_mode='academic').all()
        
        print(f"\n🔍 验证结果:")
        print(f"   - 学术模式知识点: {len(academic_kps)}")
        print(f"   - 学术模式题目: {len(academic_questions)}")
        
        # 按难度统计
        difficulty_stats = {}
        for q in academic_questions:
            diff = q.difficulty
            if diff not in difficulty_stats:
                difficulty_stats[diff] = 0
            difficulty_stats[diff] += 1
        
        print(f"   - 难度分布: {difficulty_stats}")
        
        # 按类型统计
        type_stats = {}
        for q in academic_questions:
            qtype = q.question_type  # 字段名是question_type
            if qtype not in type_stats:
                type_stats[qtype] = 0
            type_stats[qtype] += 1
        
        print(f"   - 类型分布: {type_stats}")

if __name__ == '__main__':
    print("=" * 50)
    print("📖 增强学术题库导入工具")
    print("=" * 50)
    
    try:
        import_enhanced_academic_questions()
        verify_import()
        
        print(f"\n✅ 全部完成! 现在你有了一个更丰富的学术题库!")
        print(f"💡 提示: 重启应用后即可在学术模式中体验新题库")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
