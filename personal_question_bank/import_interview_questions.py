#!/usr/bin/env python3
"""
面试题库导入工具
将interview_question_bank.JSON导入到面试就业模式
"""

import json
import sys
from app import app, db
from models import Question, KnowledgePoint

def import_interview_questions():
    """导入面试题库"""
    
    print("🚀 开始导入面试题库...")
    
    try:
        # 读取JSON文件
        with open('interview_question_bank.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    with app.app_context():
        db.create_all()
        
        imported_kp = 0
        imported_questions = 0
        
        # 1. 导入知识点
        print("\n📚 导入知识点...")
        for kp_data in data.get('knowledge_points', []):
            # 检查是否已存在
            existing_kp = KnowledgePoint.query.filter_by(
                name=kp_data['name'], 
                category=kp_data['category']
            ).first()
            
            if not existing_kp:
                kp = KnowledgePoint(
                    name=kp_data['name'],
                    category=kp_data['category'],
                    description=kp_data['description'],
                    difficulty_level=kp_data['difficulty_level'],
                    question_bank_mode='interview'  # 标记为面试模式
                )
                db.session.add(kp)
                imported_kp += 1
                print(f"  ✅ {kp_data['name']} ({kp_data['category']})")
            else:
                print(f"  ⚠️  已存在: {kp_data['name']}")
        
        db.session.flush()
        
        # 获取所有面试相关的知识点（用于后续题目关联）
        interview_kps = KnowledgePoint.query.filter_by(question_bank_mode='interview').all()
        kp_mapping = {i+1: kp.id for i, kp in enumerate(interview_kps)}
        
        # 2. 导入理论题
        print("\n📝 导入理论题...")
        for q_data in data.get('theory_questions', []):
            if Question.query.filter_by(title=q_data['title']).first():
                print(f"  ⚠️  重复题目: {q_data['title']}")
                continue
            
            # 找到对应的知识点
            kp_index = q_data['knowledge_point_id']
            if kp_index in kp_mapping:
                kp_id = kp_mapping[kp_index]
                
                question = Question(
                    title=q_data['title'],
                    content=q_data['content'],
                    question_type=q_data['question_type'],
                    difficulty=q_data['difficulty'],
                    estimated_time=q_data['estimated_time'],
                    knowledge_point_id=kp_id,
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation'],
                    question_bank_mode='interview'  # 标记为面试模式
                )
                
                db.session.add(question)
                imported_questions += 1
                print(f"  ✅ {q_data['title']}")
            else:
                print(f"  ❌ 找不到知识点ID {kp_index}")
        
        # 3. 导入编程题
        print("\n💻 导入编程题...")
        for q_data in data.get('coding_questions', []):
            if Question.query.filter_by(title=q_data['title']).first():
                print(f"  ⚠️  重复题目: {q_data['title']}")
                continue
            
            kp_index = q_data['knowledge_point_id']
            if kp_index in kp_mapping:
                kp_id = kp_mapping[kp_index]
                
                # 处理测试用例
                test_cases = None
                if 'test_cases' in q_data:
                    test_cases = json.dumps(q_data['test_cases'], ensure_ascii=False)
                
                question = Question(
                    title=q_data['title'],
                    content=q_data['content'],
                    question_type=q_data['question_type'],
                    difficulty=q_data['difficulty'],
                    estimated_time=q_data['estimated_time'],
                    knowledge_point_id=kp_id,
                    correct_answer=q_data.get('correct_answer'),
                    explanation=q_data.get('explanation'),
                    programming_language=q_data.get('programming_language', 'javascript'),
                    starter_code=q_data.get('starter_code'),
                    test_cases=test_cases,
                    question_bank_mode='interview'  # 标记为面试模式
                )
                
                db.session.add(question)
                imported_questions += 1
                print(f"  ✅ {q_data['title']}")
            else:
                print(f"  ❌ 找不到知识点ID {kp_index}")
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"""
🎉 导入成功！
📊 统计信息:
   - 新增知识点: {imported_kp} 个
   - 新增题目: {imported_questions} 道
   - 数据库总题目数: {Question.query.count()} 道
   - 数据库总知识点数: {KnowledgePoint.query.count()} 个
   - 面试题目数: {Question.query.filter_by(question_bank_mode='interview').count()} 道
""")
        except Exception as e:
            print(f"❌ 提交失败: {e}")
            db.session.rollback()

if __name__ == "__main__":
    import_interview_questions()
