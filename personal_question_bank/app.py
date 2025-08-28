from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

from models import db, User, Question, LearningRecord, KnowledgePoint, UserKnowledgeStats, InterviewPreparationPlan, WrongQuestion, SimilarQuestion
from recommendation_engine import RecommendationEngine
from external_platforms import platform_manager
from data_generator import generate_sample_data
from theory_grader import grade_theory_answer, grade_fill_blank_answer


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
    
    # 最近学习记录 (获取更多记录用于统计，前端会自行筛选本周数据)
    recent_records = LearningRecord.query.filter_by(user_id=user_id)\
                                        .order_by(LearningRecord.completed_at.desc())\
                                        .limit(100).all()  # 增加到100条，覆盖更长时间段
    
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
    mode = request.args.get('mode', 'academic')  # 新增：题库模式过滤
    
    query = Question.query
    
    # 过滤条件
    if question_type:
        query = query.filter(Question.question_type == question_type)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    if mode:
        query = query.filter(Question.question_bank_mode == mode)
    
    questions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'questions': [q.to_dict() for q in questions.items],
        'total': questions.total,
        'pages': questions.pages,
        'current_page': page,
        'mode': mode
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
    mode = request.args.get('mode', 'academic') # 获取模式参数，默认为'academic'
    
    try:
        recommended_questions = recommendation_engine.recommend_questions(user_id, count, question_bank_mode=mode)
        return jsonify({
            'user_id': user_id,
            'recommendations': [q.to_dict() for q in recommended_questions],
            'count': len(recommended_questions),
            'mode': mode
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
    grading_result = None
    partial_score = 0.0
    
    if question.question_type == 'coding':
        # 编程题现在使用CodePen，不再服务器端执行代码
        # 简单的代码长度和语法检查
        if user_answer and user_answer.strip():
            # 基本的代码质量检查
            code_lines = user_answer.strip().split('\n')
            non_empty_lines = [line for line in code_lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('#')]
            
            # 简单的评分逻辑
            if len(non_empty_lines) >= 3:  # 至少3行有效代码
                if any(keyword in user_answer.lower() for keyword in ['function', 'def', 'class', 'if', 'for', 'while']):
                    is_correct = True
                    partial_score = 0.8  # 基础分数
                    
                    # 如果代码包含常见的算法关键词，给予更高分数
                    if any(keyword in user_answer.lower() for keyword in ['return', 'console.log', 'print']):
                        partial_score = 1.0
                else:
                    is_correct = False
                    partial_score = 0.5  # 有代码但质量不高
            else:
                is_correct = False
                partial_score = 0.2  # 代码太少
        else:
            is_correct = False
            partial_score = 0.0
        
        # 创建一个简单的执行结果对象
        class SimpleExecutionResult:
            def __init__(self, success, score):
                self.success = success
                self.output = "代码已提交，使用CodePen进行测试和调试"
                self.error = "" if success else "代码格式需要改进"
                self.execution_time = 0
                self.test_cases_passed = int(score * 3) if score > 0 else 0  # 模拟测试用例通过数
                self.total_test_cases = 3  # 假设有3个测试用例
        
        execution_result = SimpleExecutionResult(is_correct, partial_score)
    elif question.question_type == 'theory':
        # 理论题使用智能评分系统
        grading_result = grade_theory_answer(user_answer, question.correct_answer, question.content)
        is_correct = grading_result['is_correct']
        partial_score = grading_result['score']
    elif question.question_type == 'multiple_choice':
        # 选择题直接比较答案
        is_correct = user_answer.strip().upper() == question.correct_answer.strip().upper()
        partial_score = 1.0 if is_correct else 0.0
    elif question.question_type == 'fill_blank':
        # 填空题使用智能填空匹配
        fill_blank_result = grade_fill_blank_answer(user_answer, question.correct_answer)
        is_correct = fill_blank_result['is_correct']
        partial_score = fill_blank_result['score']
        grading_result = fill_blank_result  # 保持反馈格式一致
    else:
        # 其他类型题目使用智能评分（如实践题等）
        grading_result = grade_theory_answer(user_answer, question.correct_answer, question.content)
        is_correct = grading_result['is_correct']
        partial_score = grading_result['score']
    
    # 创建学习记录
    learning_record = LearningRecord(
        user_id=user_id,
        question_id=question_id,
        is_correct=is_correct,
        partial_score=partial_score,
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
    
    # 更新统计数据（确保默认值）
    if user_stats.total_attempts is None:
        user_stats.total_attempts = 0
    if user_stats.correct_attempts is None:
        user_stats.correct_attempts = 0
    if user_stats.total_time_spent is None:
        user_stats.total_time_spent = 0
    
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
    
    # 如果答错了，自动添加到错题本
    if not is_correct and partial_score < 0.6:  # 低于60%就认为是错题
        existing_wrong = WrongQuestion.query.filter_by(
            user_id=user_id,
            question_id=question_id,
            question_bank_mode=question.question_bank_mode or 'academic'
        ).first()
        
        if not existing_wrong:
            wrong_question = WrongQuestion(
                user_id=user_id,
                question_id=question_id,
                learning_record_id=learning_record.id,
                wrong_answer=user_answer,
                correct_answer=question.correct_answer,
                question_bank_mode=question.question_bank_mode or 'academic'
            )
            db.session.add(wrong_question)
            db.session.commit()
    
    # 准备响应
    response_data = {
        'is_correct': is_correct,
        'partial_score': partial_score,
        'score_percentage': round(partial_score * 100, 1),
        'correct_answer': question.correct_answer,
        'explanation': question.explanation,
        'learning_record_id': learning_record.id,
        'updated_stats': user_stats.to_dict(),
        'added_to_wrong_questions': not is_correct and partial_score < 0.6
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
    
    # 如果是理论题或实践题，包含详细的评分反馈
    if grading_result:
        response_data['grading_result'] = {
            'feedback': grading_result['feedback'],
            'encouragement': grading_result['encouragement'],
            'correct_keywords': grading_result['correct_keywords'],
            'missing_keywords': grading_result['missing_keywords'],
            'incorrect_parts': grading_result['incorrect_parts'],
            'detailed_analysis': grading_result['detailed_analysis']
        }
    
    return jsonify(response_data)

# ==================== 编程题执行API (已废弃，使用CodePen) ====================

@app.route('/api/code/run', methods=['POST'])
def run_code():
    """运行代码（已废弃，现在使用CodePen在线编辑器）"""
    return jsonify({
        'success': False,
        'error': '代码执行功能已迁移到CodePen在线编辑器，请使用CodePen进行代码编写和测试',
        'message': '请使用页面上的CodePen编辑器来编写和运行您的代码'
    }), 410  # 410 Gone - 资源已不再可用

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

# ==================== 学习路径API ====================

@app.route('/api/learning-path/<int:user_id>', methods=['GET'])
def get_learning_path(user_id):
    """获取用户学习路径"""
    try:
        learning_path = recommendation_engine.get_learning_path(user_id)
        return jsonify({
            'user_id': user_id,
            'learning_path': learning_path,
            'total_paths': len(learning_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/progress', methods=['GET'])
def get_user_progress(user_id):
    """获取用户总体学习进度"""
    user = User.query.get_or_404(user_id)
    
    # 计算总体进度
    total_knowledge_points = KnowledgePoint.query.count()
    user_stats = UserKnowledgeStats.query.filter_by(user_id=user_id).all()
    
    progress_data = {
        'user': user.to_dict(),
        'total_knowledge_points': total_knowledge_points,
        'mastered_knowledge_points': len([s for s in user_stats if s.mastery_level > 0.7]),
        'learning_knowledge_points': len([s for s in user_stats if 0.3 <= s.mastery_level <= 0.7]),
        'weak_knowledge_points': len([s for s in user_stats if s.mastery_level < 0.3]),
        'overall_progress': sum(s.mastery_level for s in user_stats) / total_knowledge_points if total_knowledge_points > 0 else 0,
        'knowledge_point_details': [s.to_dict() for s in user_stats]
    }
    
    return jsonify(progress_data)

# ==================== 前端页面 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/practice/<int:user_id>')
def practice_page(user_id):
    """练习页面"""
    mode = request.args.get('mode', 'academic')
    question_id = request.args.get('question', type=int)
    return render_template('practice.html', user_id=user_id, mode=mode, question_id=question_id)

@app.route('/dashboard/<int:user_id>')
def dashboard_page(user_id):
    """用户仪表板"""
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        # 如果用户不存在，创建一个默认用户
        user = User(
            username="演示用户",
            email="demo@example.com",
            preferred_difficulty="medium",
            preferred_interaction_type="对话式"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    return render_template('dashboard.html', user_id=user_id)

@app.route('/knowledge-points/<int:user_id>')
def knowledge_points_page(user_id):
    """知识点页面"""
    return render_template('knowledge_points.html', user_id=user_id)

@app.route('/learning-path/<int:user_id>')
def learning_path_page(user_id):
    """学习路径页面"""
    return render_template('learning_path.html', user_id=user_id)

# ==================== 面试模式API ====================

@app.route('/api/interview/hot-questions', methods=['GET'])
def get_hot_interview_questions():
    """获取热门面试题"""
    category = request.args.get('category', 'all')
    limit = int(request.args.get('limit', 10))
    
    query = Question.query.filter_by(question_bank_mode='interview')
    
    if category != 'all':
        # 根据知识点类别筛选
        query = query.join(KnowledgePoint).filter(
            KnowledgePoint.category.ilike(f'%{category}%')
        )
    
    # 可以添加热度排序逻辑，这里暂时按创建时间倒序
    questions = query.order_by(Question.created_at.desc()).limit(limit).all()
    
    return jsonify([q.to_dict() for q in questions])

@app.route('/api/interview/plan', methods=['POST'])
def create_interview_plan():
    """创建面试准备计划"""
    data = request.json
    
    try:
        # 获取重点技术栈
        focus_technologies = get_focus_technologies(data.get('target_position', ''))
        
        # 这里可以添加更复杂的计划生成逻辑
        plan = InterviewPreparationPlan(
            user_id=data.get('user_id', 1),  # 暂时硬编码，实际应该从session获取
            target_position=data['target_position'],
            target_company_type=data['target_company_type'],
            target_experience_level=data['target_experience_level'],
            preparation_start_date=datetime.now().date(),
            focus_technologies=json.dumps(focus_technologies, ensure_ascii=False)
        )
        
        # 计算计划的题目数量
        total_questions = Question.query.filter_by(question_bank_mode='interview').count()
        plan.total_questions_planned = min(total_questions, 50)  # 默认计划50道题
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({'success': True, 'plan_id': plan.id, 'plan': plan.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/interview/plans/<int:user_id>', methods=['GET'])
def get_user_interview_plans(user_id):
    """获取用户的面试计划"""
    plans = InterviewPreparationPlan.query.filter_by(user_id=user_id).all()
    return jsonify([plan.to_dict() for plan in plans])

@app.route('/api/questions/by-mode/<mode>', methods=['GET'])
def get_questions_by_mode(mode):
    """根据模式获取题目"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    query = Question.query.filter_by(question_bank_mode=mode)
    questions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'questions': [q.to_dict() for q in questions.items],
        'total': questions.total,
        'pages': questions.pages,
        'current_page': page,
        'mode': mode
    })

@app.route('/api/knowledge-points/by-mode/<mode>', methods=['GET'])
def get_knowledge_points_by_mode(mode):
    """根据模式获取知识点"""
    knowledge_points = KnowledgePoint.query.filter_by(question_bank_mode=mode).all()
    return jsonify([kp.to_dict() for kp in knowledge_points])

def get_focus_technologies(position):
    """根据岗位获取重点技术栈"""
    tech_map = {
        'frontend': ['Vue', 'React', 'JavaScript', '前端工程化'],
        'backend': ['Golang', 'Node.js', '数据库', '微服务'],
        'fullstack': ['Vue', 'React', 'Node.js', 'Golang'],
        'go_developer': ['Golang', '微服务', '高并发', '分布式']
    }
    return tech_map.get(position, ['通用'])

# 添加学术模式的路由
@app.route('/academic')
def academic_dashboard():
    """学术模式主页"""
    # 暂时使用默认用户ID 1，实际应用中应该从session中获取
    return render_template('dashboard.html', mode='academic', user_id=1)

@app.route('/academic/practice')
def academic_practice():
    """学术模式练习页面"""
    return render_template('practice.html', mode='academic')

@app.route('/interview/ai-intro')
def interview_ai_intro():
    """AI模拟面试介绍页面"""
    return render_template('interview_ai_intro.html')

# 添加面试模式的路由
@app.route('/interview')
def interview_dashboard():
    """面试模式主页"""
    return render_template('interview_dashboard.html')

@app.route('/interview/practice')
def interview_practice():
    """面试练习页面"""
    return render_template('interview_practice_enhanced.html')

@app.route('/interview/plans')
def interview_plans():
    """面试计划页面"""
    return render_template('interview_plans.html')

@app.route('/interview/companies')
def interview_companies():
    """我的题库页面"""
    return render_template('interview_companies.html')

@app.route('/interview/tech-stack')
def interview_tech_stack():
    """技术栈分类页面"""
    return render_template('interview_tech_stack_new.html')

@app.route('/interview/tech-stack/detail')
def tech_stack_detail():
    """技术栈详情页面"""
    tech_name = request.args.get('tech', 'Vue.js')
    return render_template('tech_stack_detail.html', tech_name=tech_name)

@app.route('/interview/tech-stack/<category>/practice')
def tech_stack_practice(category):
    """技术栈专练页面"""
    return render_template('tech_stack_practice.html', category=category)

@app.route('/api/tech-stack/<category>/questions')
def get_tech_stack_questions(category):
    """获取指定技术栈的题目列表"""
    try:
        # 获取该技术栈分类下的所有题目
        questions = db.session.query(Question).join(KnowledgePoint).filter(
            KnowledgePoint.category == category,
            KnowledgePoint.question_bank_mode == 'interview'
        ).all()
        
        result = []
        for question in questions:
            result.append({
                'id': question.id,
                'title': question.title,
                'content': question.content,
                'difficulty': question.difficulty,
                'question_type': question.question_type,
                'knowledge_point': question.knowledge_point.name,
                'estimated_time': question.estimated_time or 15
            })
        
        return jsonify({
            'category': category,
            'questions': result,
            'total_count': len(result)
        })
        
    except Exception as e:
        print(f"获取技术栈题目失败: {e}")
        return jsonify({'error': '获取题目失败'}), 500




@app.route('/practice')
def practice_page_default():
    """默认练习页面（重定向到学术模式）"""
    return render_template('practice.html', mode='academic')

@app.route('/test_frontend.html')
def test_frontend():
    """前端测试页面"""
    with open('test_frontend.html', 'r', encoding='utf-8') as f:
        return f.read()



# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    # 如果是API请求，返回JSON
    if request.path.startswith('/api/'):
        return jsonify({'error': '资源未找到'}), 404
    # 否则返回HTML页面
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': '服务器内部错误'}), 500

# 公司题库相关API
@app.route('/api/companies', methods=['GET', 'POST'])
def companies_api():
    """获取公司列表和添加新公司"""
    from models import Company
    import json

    if request.method == 'GET':
        try:
            # 从数据库获取所有公司
            companies = Company.query.order_by(Company.is_default.desc(), Company.created_at.asc()).all()
            companies_data = [company.to_dict() for company in companies]
            return jsonify(companies_data)
        except Exception as e:
            print(f"获取公司列表失败: {e}")
            # 如果数据库查询失败，返回空列表
            return jsonify([])

    elif request.method == 'POST':
        # 添加新公司
        try:
            data = request.get_json()

            # 验证必填字段
            if not data.get('name'):
                return jsonify({'success': False, 'message': '公司名称不能为空'}), 400

            # 检查公司名称是否已存在
            existing_company = Company.query.filter_by(name=data['name']).first()
            if existing_company:
                return jsonify({'success': False, 'message': '公司名称已存在'}), 400

            # 创建新公司对象
            new_company = Company(
                name=data['name'],
                company_type=data.get('type', 'startup'),
                difficulty=float(data.get('difficulty', 4.0)),
                description=data.get('description', ''),
                tech_stack=json.dumps(data.get('techStack', [])),
                question_count=0,  # 新公司初始题目数为0
                pass_rate=70,  # 默认通过率
                is_default=False  # 用户添加的公司不是默认公司
            )

            # 保存到数据库
            db.session.add(new_company)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '公司添加成功',
                'company': new_company.to_dict()
            })

        except Exception as e:
            db.session.rollback()
            print(f"添加公司失败: {e}")
            return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@app.route('/api/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    """删除公司"""
    from models import Company

    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'message': '公司不存在'}), 404

        # 检查是否为默认公司
        if company.is_default:
            return jsonify({'success': False, 'message': '不能删除系统默认公司'}), 400

        # 删除公司
        company_name = company.name
        db.session.delete(company)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'公司 "{company_name}" 删除成功'
        })

    except Exception as e:
        db.session.rollback()
        print(f"删除公司失败: {e}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/companies/<company_id>/questions')
def get_company_questions(company_id):
    """获取特定公司的面试题目"""
    questions = Question.query.filter_by(question_bank_mode='interview').limit(10).all()
    
    return jsonify([{
        'id': q.id,
        'title': q.title,
        'content': q.content,
        'question_type': q.question_type,
        'difficulty': q.difficulty,
        'estimated_time': q.estimated_time,
        'knowledge_point': {
            'id': q.knowledge_point.id,
            'name': q.knowledge_point.name
        } if q.knowledge_point else None
    } for q in questions])

# 技术栈相关API
@app.route('/api/tech-stacks')
def get_tech_stacks():
    """获取技术栈列表和统计"""
    try:
        from sqlalchemy import func
        
        # 获取面试模式下的技术栈统计
        tech_stats = db.session.query(
            KnowledgePoint.category,
            func.count(Question.id).label('question_count')
        ).outerjoin(Question).filter(
            KnowledgePoint.question_bank_mode == 'interview'
        ).group_by(KnowledgePoint.category).all()
        
        # 计算每个技术栈的难度分布
        result = []
        for stat in tech_stats:
            # 获取该技术栈的所有题目
            questions = db.session.query(Question).join(KnowledgePoint).filter(
                KnowledgePoint.category == stat.category,
                KnowledgePoint.question_bank_mode == 'interview'
            ).all()
            
            # 计算难度分布
            total = len(questions)
            if total > 0:
                easy_count = len([q for q in questions if q.difficulty == 'easy'])
                medium_count = len([q for q in questions if q.difficulty == 'medium'])
                hard_count = len([q for q in questions if q.difficulty == 'hard'])
                
                difficulty_distribution = {
                    'easy': round((easy_count / total) * 100),
                    'medium': round((medium_count / total) * 100),
                    'hard': round((hard_count / total) * 100)
                }
            else:
                difficulty_distribution = {'easy': 30, 'medium': 50, 'hard': 20}
            
            # 获取该分类下的知识点作为topics
            knowledge_points = db.session.query(KnowledgePoint.name).filter(
                KnowledgePoint.category == stat.category,
                KnowledgePoint.question_bank_mode == 'interview'
            ).limit(3).all()
            
            topics = [kp.name[:25] + "..." if len(kp.name) > 25 else kp.name for kp in knowledge_points]
            
            result.append({
                'category': stat.category,
                'question_count': stat.question_count,
                'difficulty_distribution': difficulty_distribution,
                'topics': topics,
                'practice_url': f'/interview/tech-stack/{stat.category}/practice'
            })
        
        # 如果没有数据，返回默认的技术栈
        if not result:
            default_tech_stacks = [
                {
                    'category': 'Vue.js',
                    'question_count': 8,
                    'difficulty_distribution': {'easy': 25, 'medium': 50, 'hard': 25}
                },
                {
                    'category': 'React',
                    'question_count': 6,
                    'difficulty_distribution': {'easy': 30, 'medium': 45, 'hard': 25}
                },
                {
                    'category': 'JavaScript',
                    'question_count': 10,
                    'difficulty_distribution': {'easy': 35, 'medium': 40, 'hard': 25}
                },
                {
                    'category': 'Golang',
                    'question_count': 7,
                    'difficulty_distribution': {'easy': 20, 'medium': 50, 'hard': 30}
                },
                {
                    'category': '前端工程化',
                    'question_count': 5,
                    'difficulty_distribution': {'easy': 40, 'medium': 40, 'hard': 20}
                },
                {
                    'category': '算法与数据结构',
                    'question_count': 12,
                    'difficulty_distribution': {'easy': 20, 'medium': 40, 'hard': 40}
                }
            ]
            return jsonify(default_tech_stacks)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"获取技术栈统计失败: {e}")
        # 返回默认数据作为备用方案
        default_tech_stacks = [
            {
                'category': 'Vue.js',
                'question_count': 8,
                'difficulty_distribution': {'easy': 25, 'medium': 50, 'hard': 25}
            },
            {
                'category': 'React',
                'question_count': 6,
                'difficulty_distribution': {'easy': 30, 'medium': 45, 'hard': 25}
            },
            {
                'category': 'JavaScript',
                'question_count': 10,
                'difficulty_distribution': {'easy': 35, 'medium': 40, 'hard': 25}
            },
            {
                'category': 'Golang',
                'question_count': 7,
                'difficulty_distribution': {'easy': 20, 'medium': 50, 'hard': 30}
            },
            {
                'category': '前端工程化',
                'question_count': 5,
                'difficulty_distribution': {'easy': 40, 'medium': 40, 'hard': 20}
            },
            {
                'category': '算法与数据结构',
                'question_count': 12,
                'difficulty_distribution': {'easy': 20, 'medium': 40, 'hard': 40}
            }
        ]
        return jsonify(default_tech_stacks)












# ===== 错题本相关API =====

@app.route('/api/wrong-questions/<int:user_id>')
def get_wrong_questions(user_id):
    """获取用户的错题本"""
    try:
        mode = request.args.get('mode', 'academic')  # academic 或 interview
        
        # 1. 验证用户是否存在
        user = User.query.get(user_id)
        if not user:
            # 如果用户不存在，创建默认用户
            user = User(
                id=user_id,
                username="演示用户",
                email="demo@example.com",
                preferred_difficulty="medium",
                preferred_interaction_type="对话式"
            )
            db.session.add(user)
            db.session.commit()
        
        # 2. 获取错题
        wrong_questions = WrongQuestion.query.filter_by(
            user_id=user_id,
            question_bank_mode=mode
        ).order_by(WrongQuestion.created_at.desc()).all()
        
        # 3. 确保所有相关的数据都被加载
        result_list = []
        for wq in wrong_questions:
            try:
                question_dict = wq.question.to_dict() if wq.question else None
                if question_dict and wq.question.knowledge_point:
                    question_dict['knowledge_point'] = wq.question.knowledge_point.to_dict()
                
                wq_dict = {
                    'id': wq.id,
                    'user_id': wq.user_id,
                    'question_id': wq.question_id,
                    'learning_record_id': wq.learning_record_id,
                    'wrong_answer': wq.wrong_answer,
                    'correct_answer': wq.correct_answer,
                    'review_count': wq.review_count,
                    'mastery_level': wq.mastery_level,
                    'next_review_date': wq.next_review_date.isoformat() if wq.next_review_date else None,
                    'created_at': wq.created_at.isoformat() if wq.created_at else None,
                    'updated_at': wq.updated_at.isoformat() if wq.updated_at else None,
                    'question': question_dict
                }
                result_list.append(wq_dict)
            except Exception as e:
                print(f"Error processing wrong question {wq.id}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'wrong_questions': result_list,
            'count': len(result_list)
        })
        
    except Exception as e:
        print(f"Error in get_wrong_questions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'wrong_questions': [],
            'count': 0
        }), 500

@app.route('/api/wrong-questions', methods=['POST'])
def add_wrong_question():
    """添加错题到错题本"""
    try:
        data = request.json
        user_id = data.get('user_id')
        question_id = data.get('question_id')
        wrong_answer = data.get('wrong_answer')
        learning_record_id = data.get('learning_record_id')
        mode = data.get('mode', 'academic')
        
        # 检查是否已存在
        existing = WrongQuestion.query.filter_by(
            user_id=user_id,
            question_id=question_id,
            question_bank_mode=mode
        ).first()
        
        if existing:
            # 更新错误答案
            existing.wrong_answer = wrong_answer
            existing.updated_at = datetime.now()
        else:
            # 创建新的错题记录
            question = Question.query.get(question_id)
            wrong_question = WrongQuestion(
                user_id=user_id,
                question_id=question_id,
                learning_record_id=learning_record_id,
                wrong_answer=wrong_answer,
                correct_answer=question.correct_answer if question else '',
                question_bank_mode=mode
            )
            db.session.add(wrong_question)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '错题已添加到错题本'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/wrong-questions/<int:wrong_question_id>/review', methods=['POST'])
def review_wrong_question(wrong_question_id):
    """复习错题"""
    try:
        data = request.json
        mastery_level = data.get('mastery_level', 1)  # 1-5级掌握程度
        
        wrong_question = WrongQuestion.query.get(wrong_question_id)
        if not wrong_question:
            return jsonify({'error': '错题不存在'}), 404
        
        # 更新复习信息
        wrong_question.review_count += 1
        wrong_question.mastery_level = mastery_level
        wrong_question.last_review_date = datetime.now()
        
        # 计算下次复习时间（基于遗忘曲线）
        if mastery_level >= 4:
            # 掌握较好，延长复习间隔
            next_days = [7, 15, 30, 60, 120][min(wrong_question.review_count, 4)]
        else:
            # 掌握不好，缩短复习间隔
            next_days = [1, 3, 7, 15, 30][min(wrong_question.review_count, 4)]
        
        wrong_question.next_review_date = datetime.now() + timedelta(days=next_days)
        wrong_question.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '复习记录已更新',
            'next_review_date': wrong_question.next_review_date.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/wrong-questions/<int:wrong_question_id>/similar', methods=['POST'])
def generate_similar_questions(wrong_question_id):
    """为错题生成举一反三题目"""
    try:
        wrong_question = WrongQuestion.query.get(wrong_question_id)
        if not wrong_question:
            return jsonify({'error': '错题不存在'}), 404
        
        original_question = wrong_question.question
        
        # 构建生成提示词
        prompt = f"""
基于以下错题，生成3道相似的题目用于举一反三练习：

原题标题：{original_question.title}
原题内容：{original_question.content}
题目类型：{original_question.question_type}
难度：{original_question.difficulty}
知识点：{original_question.knowledge_point.name if original_question.knowledge_point else ''}

要求：
1. 保持相同的知识点和难度
2. 变换题目的具体场景和参数
3. 题目要有一定的区分度
4. 提供标准答案和解析

请按照以下JSON格式返回：
[
    {{
        "title": "题目标题",
        "content": "题目内容",
        "correct_answer": "正确答案",
        "explanation": "答案解析",
        "similarity_type": "相似类型"
    }},
    ...
]
"""
        
        # 使用AI服务生成相似题目的建议
        ai_response = "基于错题分析，建议加强以下知识点的练习：" + original_question.knowledge_point.name if original_question.knowledge_point else "相关基础概念"
        
        # 解析AI响应并保存相似题目
        similar_questions = []
        
        # 从数据库中查找相似的题目
        # 1. 相同知识点的其他题目
        similar_from_db = Question.query.filter(
            Question.knowledge_point_id == original_question.knowledge_point_id,
            Question.id != original_question.id,
            Question.question_bank_mode == wrong_question.question_bank_mode
        ).limit(3).all()
        
        # 2. 如果不够，从相同难度和类型的题目中找
        if len(similar_from_db) < 3:
            additional = Question.query.filter(
                Question.difficulty == original_question.difficulty,
                Question.question_type == original_question.question_type,
                Question.id != original_question.id,
                Question.question_bank_mode == wrong_question.question_bank_mode,
                Question.knowledge_point_id != original_question.knowledge_point_id
            ).limit(3 - len(similar_from_db)).all()
            similar_from_db.extend(additional)
        
        # 3. 如果还是不够，使用模板题目
        if len(similar_from_db) == 0:
            templates = [
                {
                    "title": f"{original_question.title} - 变式练习",
                    "content": f"基于 {original_question.knowledge_point.name if original_question.knowledge_point else '相关知识点'} 的类似问题练习",
                    "similarity_type": "knowledge_point_similar"
                },
                {
                    "title": f"相关练习题 - {original_question.question_type}",
                    "content": f"针对 {original_question.difficulty} 难度的 {original_question.question_type} 题目练习",
                    "similarity_type": "type_similar"
                }
            ]
            
            for template in templates:
                similar_question = SimilarQuestion(
                    original_question_id=original_question.id,
                    wrong_question_id=wrong_question_id,
                    title=template['title'],
                    content=template['content'],
                    question_type=original_question.question_type,
                    difficulty=original_question.difficulty,
                    estimated_time=original_question.estimated_time,
                    similarity_type=template['similarity_type'],
                    similarity_score=0.6,
                    generated_by='template',
                    generation_prompt=prompt,
                    correct_answer=f"参考原题答案：{original_question.correct_answer}",
                    explanation=f"参考原题解析：{original_question.explanation}",
                    question_bank_mode=wrong_question.question_bank_mode
                )
                
                db.session.add(similar_question)
                similar_questions.append(similar_question)
        else:
            # 将数据库中的真实题目转换为相似题目记录
            for i, db_question in enumerate(similar_from_db):
                similarity_types = ["knowledge_point_match", "difficulty_match", "type_match"]
                
                similar_question = SimilarQuestion(
                    original_question_id=original_question.id,
                    wrong_question_id=wrong_question_id,
                    title=db_question.title,
                    content=db_question.content,
                    question_type=db_question.question_type,
                    difficulty=db_question.difficulty,
                    estimated_time=db_question.estimated_time,
                    similarity_type=similarity_types[i % len(similarity_types)],
                    similarity_score=0.9 if db_question.knowledge_point_id == original_question.knowledge_point_id else 0.7,
                    generated_by='database_match',
                    generation_prompt=prompt,
                    correct_answer=db_question.correct_answer,
                    explanation=db_question.explanation,
                    question_bank_mode=wrong_question.question_bank_mode
                )
                
                db.session.add(similar_question)
                similar_questions.append(similar_question)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功生成{len(similar_questions)}道相似题目',
            'similar_questions': [sq.to_dict() for sq in similar_questions]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/similar-questions/<int:question_id>')
def get_similar_questions(question_id):
    """获取指定题目的相似题目"""
    try:
        similar_questions = SimilarQuestion.query.filter_by(
            original_question_id=question_id
        ).all()
        
        return jsonify({
            'success': True,
            'similar_questions': [sq.to_dict() for sq in similar_questions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wrong-questions/<int:wrong_question_id>', methods=['DELETE'])
def delete_wrong_question(wrong_question_id):
    """删除错题"""
    try:
        wrong_question = WrongQuestion.query.get(wrong_question_id)
        if not wrong_question:
            return jsonify({'error': '错题不存在'}), 404
        
        db.session.delete(wrong_question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '错题已删除'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ===== 错题本页面路由 =====

@app.route('/wrong-questions')
def wrong_questions_page():
    """错题本页面"""
    return render_template('wrong_questions.html')

@app.route('/academic/wrong-questions')
def academic_wrong_questions_page():
    """学术模式错题本页面"""
    return render_template('wrong_questions.html')

@app.route('/interview/wrong-questions')
def interview_wrong_questions_page():
    """面试模式错题本页面"""
    return render_template('interview_wrong_questions.html')

@app.route('/interview/wrong-questions-simple')
def interview_wrong_questions_simple():
    """面试模式错题本页面（简化版）"""
    return render_template('interview_wrong_questions_simple.html')

@app.route('/test-communication')
def test_communication():
    """跨页面通信测试页面"""
    from flask import send_from_directory
    return send_from_directory('.', 'test_cross_page_communication.html')

# ===== 统计数据API =====

@app.route('/api/questions/count')
def get_questions_count():
    """获取题目总数"""
    try:
        count = Question.query.count()
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/count')
def get_users_count():
    """获取用户总数"""
    try:
        count = User.query.count()
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/learning-records/count')
def get_learning_records_count():
    """获取学习记录总数"""
    try:
        count = LearningRecord.query.count()
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
