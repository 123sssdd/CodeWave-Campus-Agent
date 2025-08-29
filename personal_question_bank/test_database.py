#!/usr/bin/env python3
"""
测试数据库状态
"""

from app import app, db, Question, KnowledgePoint

def test_database():
    with app.app_context():
        print('=== 数据库状态检查 ===')
        print(f'总题目数: {Question.query.count()}')
        print(f'学术模式题目数: {Question.query.filter_by(question_bank_mode="academic").count()}')
        print(f'面试模式题目数: {Question.query.filter_by(question_bank_mode="interview").count()}')
        print(f'总知识点数: {KnowledgePoint.query.count()}')
        print(f'学术模式知识点数: {KnowledgePoint.query.filter_by(question_bank_mode="academic").count()}')
        print(f'面试模式知识点数: {KnowledgePoint.query.filter_by(question_bank_mode="interview").count()}')
        
        print('\n=== 学术模式题目示例 ===')
        academic_questions = Question.query.filter_by(question_bank_mode='academic').limit(5).all()
        for q in academic_questions:
            print(f'ID: {q.id}, 标题: {q.title}, 类型: {q.question_type}, 难度: {q.difficulty}')
        
        print('\n=== 面试模式题目示例 ===')
        interview_questions = Question.query.filter_by(question_bank_mode='interview').limit(5).all()
        for q in interview_questions:
            print(f'ID: {q.id}, 标题: {q.title}, 类型: {q.question_type}, 难度: {q.difficulty}')

if __name__ == "__main__":
    test_database()
