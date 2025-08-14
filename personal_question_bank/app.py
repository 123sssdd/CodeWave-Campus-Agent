from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

from models import db, User, Question, LearningRecord, KnowledgePoint, UserKnowledgeStats
from recommendation_engine import RecommendationEngine
from external_platforms import platform_manager
from data_generator import generate_sample_data

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///question_bank.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db.init_app(app)
CORS(app)

# 初始化推荐引擎
recommendation_engine = RecommendationEngine()

def create_tables():
    """创建数据库表"""
    with app.app_context():
        db.create_all()
        
        # 检查是否需要生成示例数据
        if User.query.count() == 0:
            print("生成示例数据...")
            generate_sample_data()
            print("示例数据生成完成！")

# ==================== 用户相关API ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/api/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """获取用户学习统计"""
    user = User.query.get_or_404(user_id)
    
    # 基础统计
    total_questions = LearningRecord.query.filter_by(user_id=user_id).count()
    correct_answers = LearningRecord.query.filter_by(user_id=user_id, is_correct=True).count()
    
    # 知识点统计
    knowledge_stats = UserKnowledgeStats.query.filter_by(user_id=user_id).all()
    
    # 最近学习记录
    recent_records = LearningRecord.query.filter_by(user_id=user_id)\
                                        .order_by(LearningRecord.completed_at.desc())\
                                        .limit(10).all()
    
    stats = {
        'user': user.to_dict(),
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'accuracy_rate': correct_answers / total_questions if total_questions > 0 else 0,
        'knowledge_stats': [stat.to_dict() for stat in knowledge_stats],
        'recent_records': [record.to_dict() for record in recent_records]
    }
    
    return jsonify(stats)

# ==================== 题目相关API ====================

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """获取题目列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    question_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    knowledge_point_id = request.args.get('knowledge_point_id', type=int)
    
    query = Question.query
    
    # 过滤条件
    if question_type:
        query = query.filter(Question.question_type == question_type)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    
    questions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'questions': [q.to_dict() for q in questions.items],
        'total': questions.total,
        'pages': questions.pages,
        'current_page': page
    })

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """获取题目详情"""
    question = Question.query.get_or_404(question_id)
    return jsonify(question.to_dict())

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """获取个性化推荐题目"""
    user = User.query.get_or_404(user_id)
    count = request.args.get('count', 10, type=int)
    
    try:
        recommended_questions = recommendation_engine.recommend_questions(user_id, count)
        return jsonify({
            'user_id': user_id,
            'recommendations': [q.to_dict() for q in recommended_questions],
            'count': len(recommended_questions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 学习记录API ====================

@app.route('/api/learning-records', methods=['POST'])
def submit_answer():
    """提交答案并记录学习过程"""
    data = request.get_json()
    
    required_fields = ['user_id', 'question_id', 'user_answer', 'time_spent', 'interaction_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': '缺少必要字段'}), 400
    
    user_id = data['user_id']
    question_id = data['question_id']
    user_answer = data['user_answer']
    time_spent = data['time_spent']
    interaction_type = data['interaction_type']
    
    # 获取题目和用户
    question = Question.query.get_or_404(question_id)
    user = User.query.get_or_404(user_id)
    
    # 判断答案正确性
    is_correct = False
    execution_result = None
    
    if question.question_type == 'coding':
        # 编程题需要运行代码测试
        if question.test_cases:
            test_cases = json.loads(question.test_cases)
            execution_result = platform_manager.execute_code(
                user_answer, 
                question.programming_language or 'python',
                test_cases
            )
            is_correct = execution_result.test_cases_passed == execution_result.total_test_cases
        else:
            # 没有测试用例，只检查语法
            execution_result = platform_manager.execute_code(
                user_answer,
                question.programming_language or 'python'
            )
            is_correct = execution_result.success
    else:
        # 其他类型题目直接比较答案
        is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
    
    # 创建学习记录
    learning_record = LearningRecord(
        user_id=user_id,
        question_id=question_id,
        is_correct=is_correct,
        time_spent=time_spent,
        user_answer=user_answer,
        interaction_type=interaction_type,
        started_at=datetime.utcnow() - timedelta(seconds=time_spent),
        completed_at=datetime.utcnow()
    )
    
    db.session.add(learning_record)
    
    # 更新用户知识点统计
    knowledge_point_id = question.knowledge_point_id
    user_stats = UserKnowledgeStats.query.filter_by(
        user_id=user_id, 
        knowledge_point_id=knowledge_point_id
    ).first()
    
    if not user_stats:
        user_stats = UserKnowledgeStats(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id
        )
        db.session.add(user_stats)
    
    # 更新统计数据
    user_stats.total_attempts += 1
    if is_correct:
        user_stats.correct_attempts += 1
    
    user_stats.total_time_spent += time_spent
    user_stats.average_time = user_stats.total_time_spent / user_stats.total_attempts
    user_stats.last_practice_time = datetime.utcnow()
    
    # 计算掌握程度 (简单算法: 正确率 * 0.7 + 练习频率 * 0.3)
    accuracy = user_stats.correct_attempts / user_stats.total_attempts
    practice_frequency = min(user_stats.total_attempts / 10.0, 1.0)  # 最多10次达到满分
    user_stats.mastery_level = accuracy * 0.7 + practice_frequency * 0.3
    
    db.session.commit()
    
    # 准备响应
    response_data = {
        'is_correct': is_correct,
        'correct_answer': question.correct_answer,
        'explanation': question.explanation,
        'learning_record_id': learning_record.id,
        'updated_stats': user_stats.to_dict()
    }
    
    # 如果是编程题，包含执行结果
    if execution_result:
        response_data['execution_result'] = {
            'success': execution_result.success,
            'output': execution_result.output,
            'error': execution_result.error,
            'execution_time': execution_result.execution_time,
            'test_cases_passed': execution_result.test_cases_passed,
            'total_test_cases': execution_result.total_test_cases
        }
    
    return jsonify(response_data)

# ==================== 编程题执行API ====================

@app.route('/api/code/run', methods=['POST'])
def run_code():
    """运行代码（不保存记录）"""
    data = request.get_json()
    
    if not all(field in data for field in ['code', 'language']):
        return jsonify({'error': '缺少必要字段: code, language'}), 400
    
    code = data['code']
    language = data['language']
    test_cases = data.get('test_cases', [])
    
    try:
        if test_cases:
            result = platform_manager.execute_code(code, language, test_cases)
        else:
            result = platform_manager.execute_code(code, language)
        
        return jsonify({
            'success': result.success,
            'output': result.output,
            'error': result.error,
            'execution_time': result.execution_time,
            'memory_usage': result.memory_usage,
            'test_cases_passed': result.test_cases_passed,
            'total_test_cases': result.total_test_cases
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 外部平台API ====================

@app.route('/api/external/leetcode/problems', methods=['GET'])
def get_leetcode_problems():
    """获取LeetCode题目列表"""
    difficulty = request.args.get('difficulty')
    topic = request.args.get('topic')
    
    problems = platform_manager.search_leetcode_problems(difficulty, topic)
    return jsonify(problems)

@app.route('/api/external/leetcode/problems/<problem_slug>', methods=['GET'])
def get_leetcode_problem(problem_slug):
    """获取LeetCode题目详情"""
    problem = platform_manager.get_leetcode_problem(problem_slug)
    if problem:
        return jsonify(problem)
    else:
        return jsonify({'error': '题目未找到'}), 404

# ==================== 知识点API ====================

@app.route('/api/knowledge-points', methods=['GET'])
def get_knowledge_points():
    """获取知识点列表"""
    knowledge_points = KnowledgePoint.query.all()
    return jsonify([kp.to_dict() for kp in knowledge_points])

@app.route('/api/knowledge-points/<int:kp_id>/questions', methods=['GET'])
def get_knowledge_point_questions(kp_id):
    """获取知识点相关题目"""
    knowledge_point = KnowledgePoint.query.get_or_404(kp_id)
    questions = Question.query.filter_by(knowledge_point_id=kp_id).all()
    
    return jsonify({
        'knowledge_point': knowledge_point.to_dict(),
        'questions': [q.to_dict() for q in questions]
    })

# ==================== 前端页面 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/practice/<int:user_id>')
def practice_page(user_id):
    """练习页面"""
    return render_template('practice.html', user_id=user_id)

@app.route('/dashboard/<int:user_id>')
def dashboard_page(user_id):
    """用户仪表板"""
    return render_template('dashboard.html', user_id=user_id)

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源未找到'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 生成示例数据（如果数据库为空）
        if User.query.count() == 0:
            print("生成示例数据...")
            from data_generator import generate_sample_data
            generate_sample_data()
            print("示例数据生成完成！")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
