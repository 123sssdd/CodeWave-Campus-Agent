import random
import json
from datetime import datetime, timedelta
from models import db, User, Question, LearningRecord, KnowledgePoint, UserKnowledgeStats

def generate_sample_data():
    """生成示例数据"""
    
    # 1. 创建知识点
    knowledge_points_data = [
        {"name": "数组与字符串", "category": "数据结构", "description": "数组和字符串的基本操作", "difficulty_level": 1},
        {"name": "链表", "category": "数据结构", "description": "单链表、双链表操作", "difficulty_level": 2},
        {"name": "栈与队列", "category": "数据结构", "description": "栈和队列的实现与应用", "difficulty_level": 2},
        {"name": "二叉树", "category": "数据结构", "description": "二叉树遍历、搜索", "difficulty_level": 3},
        {"name": "哈希表", "category": "数据结构", "description": "哈希表原理与应用", "difficulty_level": 2},
        {"name": "排序算法", "category": "算法", "description": "各种排序算法实现", "difficulty_level": 3},
        {"name": "搜索算法", "category": "算法", "description": "线性搜索、二分搜索", "difficulty_level": 2},
        {"name": "动态规划", "category": "算法", "description": "动态规划思想与实现", "difficulty_level": 4},
        {"name": "贪心算法", "category": "算法", "description": "贪心策略与应用", "difficulty_level": 3},
        {"name": "图算法", "category": "算法", "description": "图的遍历、最短路径", "difficulty_level": 4},
        {"name": "Python基础", "category": "编程语言", "description": "Python语法基础", "difficulty_level": 1},
        {"name": "Java基础", "category": "编程语言", "description": "Java语法基础", "difficulty_level": 1},
        {"name": "C++基础", "category": "编程语言", "description": "C++语法基础", "difficulty_level": 2},
        {"name": "面向对象编程", "category": "编程思想", "description": "OOP原理与实践", "difficulty_level": 2},
        {"name": "函数式编程", "category": "编程思想", "description": "函数式编程范式", "difficulty_level": 3}
    ]
    
    knowledge_points = []
    for kp_data in knowledge_points_data:
        kp = KnowledgePoint(**kp_data)
        db.session.add(kp)
        knowledge_points.append(kp)
    
    db.session.flush()  # 获取ID
    
    # 2. 创建用户
    users_data = [
        {"username": "alice_student", "email": "alice@example.com", "preferred_difficulty": "easy", 
         "preferred_question_types": '["theory", "multiple_choice"]', "preferred_interaction_type": "theory"},
        {"username": "bob_coder", "email": "bob@example.com", "preferred_difficulty": "medium", 
         "preferred_question_types": '["coding", "practical"]', "preferred_interaction_type": "practice"},
        {"username": "charlie_advanced", "email": "charlie@example.com", "preferred_difficulty": "hard", 
         "preferred_question_types": '["coding", "theory"]', "preferred_interaction_type": "mixed"},
        {"username": "diana_beginner", "email": "diana@example.com", "preferred_difficulty": "easy", 
         "preferred_question_types": '["multiple_choice", "theory"]', "preferred_interaction_type": "theory"},
        {"username": "evan_enthusiast", "email": "evan@example.com", "preferred_difficulty": "medium", 
         "preferred_question_types": '["coding", "practical", "theory"]', "preferred_interaction_type": "practice"}
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.session.add(user)
        users.append(user)
    
    db.session.flush()
    
    # 3. 创建题目
    questions_data = []
    
    # 理论题
    theory_questions = [
        {
            "title": "什么是数组？",
            "content": "请解释数组的定义、特点以及在内存中的存储方式。",
            "question_type": "theory",
            "difficulty": "easy",
            "estimated_time": 10,
            "knowledge_point_id": 1,
            "correct_answer": "数组是一种线性数据结构，存储相同类型的元素，在内存中连续存储，支持随机访问。",
            "explanation": "数组是最基本的数据结构之一，具有固定大小和连续内存布局的特点。"
        },
        {
            "title": "时间复杂度分析",
            "content": "分析冒泡排序算法的时间复杂度，并解释最好、最坏和平均情况。",
            "question_type": "theory",
            "difficulty": "medium",
            "estimated_time": 15,
            "knowledge_point_id": 6,
            "correct_answer": "冒泡排序的时间复杂度：最好O(n)，最坏O(n²)，平均O(n²)。",
            "explanation": "冒泡排序通过相邻元素比较交换来排序，嵌套循环导致平方级时间复杂度。"
        },
        {
            "title": "动态规划原理",
            "content": "什么是动态规划？请说明动态规划的基本思想和适用条件。",
            "question_type": "theory",
            "difficulty": "hard",
            "estimated_time": 20,
            "knowledge_point_id": 8,
            "correct_answer": "动态规划是通过把原问题分解为相对简单的子问题的方式求解复杂问题的方法，需要满足最优子结构和重叠子问题两个条件。",
            "explanation": "动态规划是一种重要的算法设计技巧，广泛应用于优化问题的求解。"
        }
    ]
    
    # 选择题
    choice_questions = [
        {
            "title": "Python列表操作",
            "content": "在Python中，以下哪个操作的时间复杂度是O(1)？",
            "question_type": "multiple_choice",
            "difficulty": "easy",
            "estimated_time": 5,
            "knowledge_point_id": 11,
            "options": '["A. append()", "B. insert(0, x)", "C. remove(x)", "D. index(x)"]',
            "correct_answer": "A",
            "explanation": "append()操作直接在列表末尾添加元素，时间复杂度为O(1)。"
        },
        {
            "title": "二叉树性质",
            "content": "一个有n个节点的完全二叉树的高度是？",
            "question_type": "multiple_choice",
            "difficulty": "medium",
            "estimated_time": 8,
            "knowledge_point_id": 4,
            "options": '["A. log₂n", "B. ⌊log₂n⌋", "C. ⌈log₂(n+1)⌉", "D. n-1"]',
            "correct_answer": "C",
            "explanation": "完全二叉树的高度为⌈log₂(n+1)⌉，这是由完全二叉树的性质决定的。"
        }
    ]
    
    # 编程题
    coding_questions = [
        {
            "title": "两数之和",
            "content": "给定一个整数数组nums和一个整数目标值target，请找出和为目标值target的两个整数，并返回它们的数组下标。",
            "question_type": "coding",
            "difficulty": "easy",
            "estimated_time": 20,
            "knowledge_point_id": 1,
            "programming_language": "python",
            "starter_code": "def twoSum(nums, target):\n    \"\"\"\n    :type nums: List[int]\n    :type target: int\n    :rtype: List[int]\n    \"\"\"\n    # 请在这里实现你的代码\n    pass",
            "correct_answer": "使用哈希表存储已遍历的数字及其索引，时间复杂度O(n)",
            "explanation": "通过哈希表可以在O(1)时间内查找complement，整体时间复杂度为O(n)。",
            "test_cases": '[{"input": "[2,7,11,15]\\n9", "expected_output": "[0,1]"}, {"input": "[3,2,4]\\n6", "expected_output": "[1,2]"}]',
            "external_platform": "leetcode",
            "external_id": "1"
        },
        {
            "title": "反转链表",
            "content": "给你单链表的头节点head，请你反转链表，并返回反转后的链表。",
            "question_type": "coding",
            "difficulty": "medium",
            "estimated_time": 25,
            "knowledge_point_id": 2,
            "programming_language": "python",
            "starter_code": "# Definition for singly-linked list.\nclass ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\nclass Solution:\n    def reverseList(self, head):\n        \"\"\"\n        :type head: ListNode\n        :rtype: ListNode\n        \"\"\"\n        # 请在这里实现你的代码\n        pass",
            "correct_answer": "使用迭代或递归方法反转链表指针",
            "explanation": "通过改变节点间的指针方向来反转链表，需要注意保存前一个节点的引用。",
            "test_cases": '[{"input": "[1,2,3,4,5]", "expected_output": "[5,4,3,2,1]"}]'
        },
        {
            "title": "最大子数组和",
            "content": "给你一个整数数组nums，请找出和最大的连续子数组（至少包含一个元素），返回其最大和。",
            "question_type": "coding",
            "difficulty": "medium",
            "estimated_time": 30,
            "knowledge_point_id": 8,
            "programming_language": "python",
            "starter_code": "def maxSubArray(nums):\n    \"\"\"\n    :type nums: List[int]\n    :rtype: int\n    \"\"\"\n    # 请使用动态规划实现\n    pass",
            "correct_answer": "使用Kadane算法（动态规划）",
            "explanation": "Kadane算法是解决最大子数组问题的经典动态规划方法。",
            "test_cases": '[{"input": "[-2,1,-3,4,-1,2,1,-5,4]", "expected_output": "6"}]'
        },
        {
            "title": "有效的括号",
            "content": "给定一个只包括'('，')'，'{'，'}'，'['，']'的字符串s，判断字符串是否有效。",
            "question_type": "coding",
            "difficulty": "easy",
            "estimated_time": 15,
            "knowledge_point_id": 3,
            "programming_language": "python",
            "starter_code": "def isValid(s):\n    \"\"\"\n    :type s: str\n    :rtype: bool\n    \"\"\"\n    # 使用栈来解决\n    pass",
            "correct_answer": "使用栈数据结构匹配括号",
            "explanation": "栈的LIFO特性完美符合括号匹配的需求。",
            "test_cases": '[{"input": "()", "expected_output": "true"}, {"input": "()[]", "expected_output": "true"}, {"input": "(]", "expected_output": "false"}]'
        }
    ]
    
    # 实践题
    practical_questions = [
        {
            "title": "设计一个栈",
            "content": "设计一个支持push、pop、top操作的栈，并能在常数时间内检索到最小元素。",
            "question_type": "practical",
            "difficulty": "medium",
            "estimated_time": 35,
            "knowledge_point_id": 3,
            "correct_answer": "使用辅助栈存储最小值",
            "explanation": "通过维护一个辅助栈来跟踪当前栈中的最小元素。"
        },
        {
            "title": "LRU缓存实现",
            "content": "设计一个LRU（最近最少使用）缓存结构，支持get和put操作。",
            "question_type": "practical",
            "difficulty": "hard",
            "estimated_time": 45,
            "knowledge_point_id": 5,
            "correct_answer": "使用哈希表+双向链表实现",
            "explanation": "哈希表提供O(1)访问，双向链表维护访问顺序。"
        }
    ]
    
    # 合并所有题目
    all_questions = theory_questions + choice_questions + coding_questions + practical_questions
    
    questions = []
    for q_data in all_questions:
        question = Question(**q_data)
        db.session.add(question)
        questions.append(question)
    
    db.session.flush()
    
    # 4. 生成学习记录
    interaction_types = ["theory_read", "practice_code", "quick_answer", "deep_think", "review"]
    
    for user in users:
        # 每个用户生成20-50条学习记录
        num_records = random.randint(20, 50)
        
        for _ in range(num_records):
            question = random.choice(questions)
            
            # 根据用户偏好和题目难度调整正确率
            base_accuracy = 0.7
            if user.preferred_difficulty == "easy":
                base_accuracy = 0.8
            elif user.preferred_difficulty == "hard":
                base_accuracy = 0.6
            
            # 难度调整
            if question.difficulty == "easy":
                accuracy = min(base_accuracy + 0.2, 0.95)
            elif question.difficulty == "hard":
                accuracy = max(base_accuracy - 0.2, 0.3)
            else:
                accuracy = base_accuracy
            
            is_correct = random.random() < accuracy
            
            # 生成答题时间（根据预估时间±50%）
            base_time = question.estimated_time * 60  # 转换为秒
            time_spent = random.randint(int(base_time * 0.5), int(base_time * 1.5))
            
            # 生成用户答案
            if question.question_type == "multiple_choice":
                if is_correct:
                    user_answer = question.correct_answer
                else:
                    options = ["A", "B", "C", "D"]
                    options.remove(question.correct_answer)
                    user_answer = random.choice(options)
            elif question.question_type == "coding":
                if is_correct:
                    user_answer = "# 正确的代码实现\ndef solution():\n    return 'correct'"
                else:
                    user_answer = "# 错误的代码实现\ndef solution():\n    return 'incorrect'"
            else:
                if is_correct:
                    user_answer = question.correct_answer
                else:
                    user_answer = "错误的理论回答"
            
            # 生成时间（过去30天内）
            days_ago = random.randint(1, 30)
            completed_time = datetime.utcnow() - timedelta(days=days_ago)
            started_time = completed_time - timedelta(seconds=time_spent)
            
            record = LearningRecord(
                user_id=user.id,
                question_id=question.id,
                is_correct=is_correct,
                time_spent=time_spent,
                user_answer=user_answer,
                interaction_type=random.choice(interaction_types),
                started_at=started_time,
                completed_at=completed_time
            )
            
            db.session.add(record)
    
    # 5. 生成用户知识点统计
    for user in users:
        for kp in knowledge_points:
            # 获取该用户在该知识点的所有记录
            records = LearningRecord.query.join(Question).filter(
                LearningRecord.user_id == user.id,
                Question.knowledge_point_id == kp.id
            ).all()
            
            if records:
                total_attempts = len(records)
                correct_attempts = sum(1 for r in records if r.is_correct)
                total_time = sum(r.time_spent for r in records)
                
                # 计算掌握程度
                accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0
                practice_frequency = min(total_attempts / 10.0, 1.0)
                mastery_level = accuracy * 0.7 + practice_frequency * 0.3
                
                stats = UserKnowledgeStats(
                    user_id=user.id,
                    knowledge_point_id=kp.id,
                    total_attempts=total_attempts,
                    correct_attempts=correct_attempts,
                    total_time_spent=total_time,
                    average_time=total_time / total_attempts,
                    mastery_level=mastery_level,
                    last_practice_time=max(r.completed_at for r in records)
                )
                
                db.session.add(stats)
    
    # 提交所有更改
    db.session.commit()
    
    print(f"成功生成数据：")
    print(f"- 用户: {len(users)} 个")
    print(f"- 知识点: {len(knowledge_points)} 个")
    print(f"- 题目: {len(questions)} 个")
    print(f"- 学习记录: {LearningRecord.query.count()} 条")
    print(f"- 知识点统计: {UserKnowledgeStats.query.count()} 条")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.create_all()
        generate_sample_data()
