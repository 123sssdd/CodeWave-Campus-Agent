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
    
    # 双模式支持
    preferred_mode = db.Column(db.String(20), default='academic')  # academic, interview
    current_preparation_goal = db.Column(db.String(100))  # 当前备考目标
    
    # 关联
    learning_records = db.relationship('LearningRecord', backref='user', lazy=True)
    
    def to_dict(self):
        # 安全的JSON解析函数
        def safe_json_loads(json_str):
            if not json_str:
                return None
            try:
                return json.loads(json_str)
            except (json.JSONDecodeError, TypeError):
                return None
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'preferred_difficulty': self.preferred_difficulty,
            'preferred_question_types': safe_json_loads(self.preferred_question_types) or [],
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
    
    # 双模式支持
    question_bank_mode = db.Column(db.String(20), default='academic')  # academic, interview
    
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
    
    # 新增字段支持外部题库（暂时注释，等数据库迁移完成后启用）
    # external_source = db.Column(db.String(50))  # 题目来源 (leetcode, codeforces等)
    # tags = db.Column(db.Text)  # JSON字符串，存储题目标签
    # acceptance_rate = db.Column(db.Float)  # 通过率
    # likes_count = db.Column(db.Integer, default=0)  # 点赞数
    # dislikes_count = db.Column(db.Integer, default=0)  # 点踩数
    
    # 双模式支持 
    question_bank_mode = db.Column(db.String(20), default='academic')  # academic, interview
    interview_company_type = db.Column(db.String(50))  # 面试公司类型（大厂、中小企业、创业公司）
    interview_position = db.Column(db.String(100))     # 面试岗位（前端、后端、全栈等）
    interview_experience_level = db.Column(db.String(20))  # 经验要求（初级、中级、高级）
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # 安全的JSON解析函数
        def safe_json_loads(json_str):
            if not json_str:
                return None
            try:
                return json.loads(json_str)
            except (json.JSONDecodeError, TypeError):
                # 如果JSON解析失败，返回None而不是抛出异常
                return None
        
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'estimated_time': self.estimated_time,
            'knowledge_point': self.knowledge_point.to_dict() if self.knowledge_point else None,
            'options': safe_json_loads(self.options),
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'programming_language': self.programming_language,
            'starter_code': self.starter_code,
            'test_cases': safe_json_loads(self.test_cases),
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
    partial_score = db.Column(db.Float, default=0.0)  # 部分分数 (0.0-1.0)
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
            'partial_score': self.partial_score,
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

class InterviewPreparationPlan(db.Model):
    """面试准备计划"""
    __tablename__ = 'interview_preparation_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 面试目标
    target_position = db.Column(db.String(100), nullable=False)  # 目标岗位
    target_company_type = db.Column(db.String(50))  # 目标公司类型
    target_experience_level = db.Column(db.String(20))  # 目标经验级别
    
    # 计划时间
    preparation_start_date = db.Column(db.Date, nullable=False)
    target_interview_date = db.Column(db.Date)
    
    # 学习进度
    total_questions_planned = db.Column(db.Integer, default=0)
    questions_completed = db.Column(db.Integer, default=0)
    
    # 重点技术栈
    focus_technologies = db.Column(db.Text)  # JSON字符串存储技术栈列表
    
    # 状态
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    user = db.relationship('User', backref='interview_plans')
    
    def to_dict(self):
        # 安全的JSON解析函数
        def safe_json_loads(json_str):
            if not json_str:
                return None
            try:
                return json.loads(json_str)
            except (json.JSONDecodeError, TypeError):
                return None
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_position': self.target_position,
            'target_company_type': self.target_company_type,
            'target_experience_level': self.target_experience_level,
            'preparation_start_date': self.preparation_start_date.isoformat() if self.preparation_start_date else None,
            'target_interview_date': self.target_interview_date.isoformat() if self.target_interview_date else None,
            'total_questions_planned': self.total_questions_planned,
            'questions_completed': self.questions_completed,
            'focus_technologies': safe_json_loads(self.focus_technologies) or [],
            'status': self.status,
            'progress_percentage': round((self.questions_completed / self.total_questions_planned * 100) if self.total_questions_planned > 0 else 0, 1)
        }

class WrongQuestion(db.Model):
    """错题本模型"""
    __tablename__ = 'wrong_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    learning_record_id = db.Column(db.Integer, db.ForeignKey('learning_records.id'))
    
    # 错误信息
    wrong_answer = db.Column(db.Text)  # 用户的错误答案
    correct_answer = db.Column(db.Text)  # 正确答案
    mistake_reason = db.Column(db.Text)  # 错误原因分析
    
    # 复习状态
    review_count = db.Column(db.Integer, default=0)  # 复习次数
    mastery_level = db.Column(db.Integer, default=0)  # 掌握程度 0-5
    last_review_date = db.Column(db.DateTime)  # 上次复习时间
    next_review_date = db.Column(db.DateTime)  # 下次复习时间
    
    # 模式标识
    question_bank_mode = db.Column(db.String(20), default='academic')  # academic, interview
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user = db.relationship('User', backref='wrong_questions')
    question = db.relationship('Question', backref='wrong_records')
    learning_record = db.relationship('LearningRecord', backref='wrong_question_record')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'question': self.question.to_dict() if self.question else None,
            'wrong_answer': self.wrong_answer,
            'correct_answer': self.correct_answer,
            'mistake_reason': self.mistake_reason,
            'review_count': self.review_count,
            'mastery_level': self.mastery_level,
            'last_review_date': self.last_review_date.isoformat() if self.last_review_date else None,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None,
            'question_bank_mode': self.question_bank_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SimilarQuestion(db.Model):
    """举一反三题目模型"""
    __tablename__ = 'similar_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    original_question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    wrong_question_id = db.Column(db.Integer, db.ForeignKey('wrong_questions.id'))
    
    # 生成的相似题目
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    estimated_time = db.Column(db.Integer)
    
    # 相似性信息
    similarity_type = db.Column(db.String(50))  # 相似类型：knowledge_point, algorithm, pattern等
    similarity_score = db.Column(db.Float)  # 相似度评分
    
    # AI生成信息
    generated_by = db.Column(db.String(50))  # 生成方式：ai_model, template等
    generation_prompt = db.Column(db.Text)  # 生成时使用的提示词
    
    # 答案和解析
    correct_answer = db.Column(db.Text)
    explanation = db.Column(db.Text)
    
    # 模式标识
    question_bank_mode = db.Column(db.String(20), default='academic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    original_question = db.relationship('Question', backref='similar_questions')
    wrong_question = db.relationship('WrongQuestion', backref='similar_questions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'original_question_id': self.original_question_id,
            'title': self.title,
            'content': self.content,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'estimated_time': self.estimated_time,
            'similarity_type': self.similarity_type,
            'similarity_score': self.similarity_score,
            'generated_by': self.generated_by,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'question_bank_mode': self.question_bank_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Company(db.Model):
    """公司模型"""
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    company_type = db.Column(db.String(50), default='startup')  # big_tech, unicorn, startup, foreign, traditional
    difficulty = db.Column(db.Float, default=4.0)
    description = db.Column(db.Text)
    tech_stack = db.Column(db.Text)  # JSON字符串存储技术栈数组
    question_count = db.Column(db.Integer, default=0)
    pass_rate = db.Column(db.Integer, default=70)
    is_default = db.Column(db.Boolean, default=False)  # 是否为系统默认公司
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        import json
        tech_stack = []
        if self.tech_stack:
            try:
                tech_stack = json.loads(self.tech_stack)
            except:
                tech_stack = []

        return {
            'id': self.id,
            'name': self.name,
            'type': self.company_type,
            'difficulty': self.difficulty,
            'description': self.description,
            'techStack': tech_stack,
            'questionCount': self.question_count,
            'passRate': self.pass_rate,
            'isDefault': self.is_default,
            'categories': tech_stack,  # 兼容前端
            'question_count': self.question_count,  # 兼容前端
            'difficulty_avg': self.difficulty,  # 兼容前端
            'pass_rate': self.pass_rate,  # 兼容前端
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
