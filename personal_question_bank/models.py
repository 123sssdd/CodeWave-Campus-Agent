from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 学习偏好
    preferred_difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    preferred_question_types = db.Column(db.Text)  # JSON字符串存储多个类型
    preferred_interaction_type = db.Column(db.String(50), default='mixed')  # theory, practice, mixed
    
    # 关联
    learning_records = db.relationship('LearningRecord', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'preferred_difficulty': self.preferred_difficulty,
            'preferred_question_types': json.loads(self.preferred_question_types) if self.preferred_question_types else [],
            'preferred_interaction_type': self.preferred_interaction_type
        }

class KnowledgePoint(db.Model):
    """知识点模型"""
    __tablename__ = 'knowledge_points'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 算法、数据结构、编程语言等
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.Integer, default=1)  # 1-5级难度
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'difficulty_level': self.difficulty_level
        }

class Question(db.Model):
    """题目模型"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # theory, coding, multiple_choice, practical
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    estimated_time = db.Column(db.Integer)  # 预估完成时间(分钟)
    
    # 知识点关联
    knowledge_point_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id'), nullable=False)
    knowledge_point = db.relationship('KnowledgePoint', backref='questions')
    
    # 题目具体配置
    options = db.Column(db.Text)  # JSON字符串，存储选择题选项
    correct_answer = db.Column(db.Text)  # 正确答案
    explanation = db.Column(db.Text)  # 答案解释
    
    # 编程题专用字段
    programming_language = db.Column(db.String(50))  # 编程语言
    starter_code = db.Column(db.Text)  # 初始代码
    test_cases = db.Column(db.Text)  # JSON字符串，存储测试用例
    external_platform = db.Column(db.String(100))  # 外部平台 (leetcode, hackerrank等)
    external_id = db.Column(db.String(100))  # 外部平台题目ID
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'estimated_time': self.estimated_time,
            'knowledge_point': self.knowledge_point.to_dict() if self.knowledge_point else None,
            'options': json.loads(self.options) if self.options else None,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'programming_language': self.programming_language,
            'starter_code': self.starter_code,
            'test_cases': json.loads(self.test_cases) if self.test_cases else None,
            'external_platform': self.external_platform,
            'external_id': self.external_id
        }

class LearningRecord(db.Model):
    """学习记录模型"""
    __tablename__ = 'learning_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    
    # 答题结果
    is_correct = db.Column(db.Boolean, nullable=False)
    time_spent = db.Column(db.Integer, nullable=False)  # 耗时(秒)
    attempt_count = db.Column(db.Integer, default=1)  # 尝试次数
    
    # 用户答案
    user_answer = db.Column(db.Text)
    
    # 交互类型记录
    interaction_type = db.Column(db.String(50))  # theory_read, practice_code, quick_answer等
    
    # 时间记录
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    question = db.relationship('Question', backref='learning_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'is_correct': self.is_correct,
            'time_spent': self.time_spent,
            'attempt_count': self.attempt_count,
            'user_answer': self.user_answer,
            'interaction_type': self.interaction_type,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat(),
            'question': self.question.to_dict() if self.question else None
        }

class UserKnowledgeStats(db.Model):
    """用户知识点统计模型"""
    __tablename__ = 'user_knowledge_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    knowledge_point_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id'), nullable=False)
    
    # 统计数据
    total_attempts = db.Column(db.Integer, default=0)
    correct_attempts = db.Column(db.Integer, default=0)
    total_time_spent = db.Column(db.Integer, default=0)  # 总耗时(秒)
    average_time = db.Column(db.Float, default=0.0)  # 平均耗时
    
    # 掌握程度评估
    mastery_level = db.Column(db.Float, default=0.0)  # 0-1之间，掌握程度
    last_practice_time = db.Column(db.DateTime)
    
    # 关联
    user = db.relationship('User', backref='knowledge_stats')
    knowledge_point = db.relationship('KnowledgePoint', backref='user_stats')
    
    @property
    def accuracy_rate(self):
        if self.total_attempts == 0:
            return 0.0
        return self.correct_attempts / self.total_attempts
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'knowledge_point': self.knowledge_point.to_dict() if self.knowledge_point else None,
            'total_attempts': self.total_attempts,
            'correct_attempts': self.correct_attempts,
            'accuracy_rate': self.accuracy_rate,
            'total_time_spent': self.total_time_spent,
            'average_time': self.average_time,
            'mastery_level': self.mastery_level,
            'last_practice_time': self.last_practice_time.isoformat() if self.last_practice_time else None
        }
