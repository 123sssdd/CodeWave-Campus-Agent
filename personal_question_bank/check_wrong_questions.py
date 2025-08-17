#!/usr/bin/env python3
"""
检查错题本数据
"""

from app import app, db, WrongQuestion, Question, User, LearningRecord

def check_wrong_questions():
    with app.app_context():
        print('=== 错题本数据检查 ===')
        
        # 检查面试模式错题数据
        interview_wrong_questions = WrongQuestion.query.filter_by(question_bank_mode='interview').all()
        print(f'面试模式错题数量: {len(interview_wrong_questions)}')
        
        # 检查学术模式错题数据
        academic_wrong_questions = WrongQuestion.query.filter_by(question_bank_mode='academic').all()
        print(f'学术模式错题数量: {len(academic_wrong_questions)}')
        
        # 检查所有错题数据
        all_wrong_questions = WrongQuestion.query.all()
        print(f'总错题数量: {len(all_wrong_questions)}')
        
        # 显示一些错题示例
        if all_wrong_questions:
            print('\n错题示例:')
            for wq in all_wrong_questions[:3]:
                question_title = wq.question.title if wq.question else "无题目"
                print(f'ID: {wq.id}, 模式: {wq.question_bank_mode}, 题目: {question_title}')
        
        # 检查学习记录
        print('\n=== 学习记录检查 ===')
        total_records = LearningRecord.query.count()
        print(f'总学习记录数: {total_records}')
        
        # 检查错误的学习记录（可能生成错题）
        wrong_records = LearningRecord.query.filter_by(is_correct=False).all()
        print(f'错误的学习记录数: {len(wrong_records)}')
        
        if wrong_records:
            print('\n最近的错误记录:')
            for record in wrong_records[-3:]:
                question_title = record.question.title if record.question else "无题目"
                question_mode = record.question.question_bank_mode if record.question else "未知"
                print(f'用户: {record.user_id}, 题目: {question_title}, 模式: {question_mode}')

def create_sample_wrong_questions():
    """创建一些示例错题数据"""
    with app.app_context():
        print('\n=== 创建示例错题数据 ===')
        
        # 获取面试模式的题目
        interview_questions = Question.query.filter_by(question_bank_mode='interview').limit(3).all()
        
        if not interview_questions:
            print('没有面试模式题目，无法创建示例错题')
            return
        
        user_id = 1  # 使用默认用户
        
        for i, question in enumerate(interview_questions):
            # 检查是否已存在错题
            existing = WrongQuestion.query.filter_by(
                user_id=user_id,
                question_id=question.id,
                question_bank_mode='interview'
            ).first()
            
            if not existing:
                wrong_question = WrongQuestion(
                    user_id=user_id,
                    question_id=question.id,
                    wrong_answer=f"这是用户对题目'{question.title}'的错误回答示例",
                    correct_answer=question.correct_answer,
                    question_bank_mode='interview',
                    mastery_level=i,  # 不同的掌握程度
                    review_count=i
                )
                
                db.session.add(wrong_question)
                print(f'创建错题: {question.title}')
        
        try:
            db.session.commit()
            print('示例错题数据创建成功！')
        except Exception as e:
            db.session.rollback()
            print(f'创建失败: {e}')

if __name__ == "__main__":
    check_wrong_questions()
    
    # 如果没有面试错题，创建一些示例数据
    with app.app_context():
        interview_wrong_count = WrongQuestion.query.filter_by(question_bank_mode='interview').count()
        if interview_wrong_count == 0:
            print('\n没有面试错题数据，创建示例数据...')
            create_sample_wrong_questions()
            print('\n重新检查数据:')
            check_wrong_questions()
