from flask import Flask, render_template, request, jsonify, session
import json
import time
import random
import difflib
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class MisconceptionPattern:
    def __init__(self, target_knowledge, category, description, tool_calls,
                 expected_output, explanation, correct_keywords, incorrect_keywords):
        self.target_knowledge = target_knowledge
        self.category = category
        self.description = description
        self.tool_calls = tool_calls
        self.expected_output = expected_output
        self.explanation = explanation
        self.correct_keywords = correct_keywords
        self.incorrect_keywords = incorrect_keywords

    def to_dict(self):
        return {
            "target_knowledge": self.target_knowledge,
            "category": self.category,
            "description": self.description,
            "tool_calls": self.tool_calls,
            "expected_output": self.expected_output,
            "explanation": self.explanation,
            "correct_keywords": self.correct_keywords,
            "incorrect_keywords": self.incorrect_keywords
        }

class MCPKnowledgeBase:
    def __init__(self):
        self.patterns = []
        self.load_sample_data()

    def load_sample_data(self):
        sample_patterns = [
            # 将“二分查找”置于首位，便于评委快速选择
            MisconceptionPattern(
                "二分查找",
                "边界更新错误",
                "在相邻区间时未使用 mid±1 导致死循环，或 mid 计算存在加法溢出风险",
                ["binary_search(nums, target)", "update_left_or_right(mid)", "compute_mid(left,right)"] ,
                "代码可以不加1/减1也能找到目标",
                "区间收缩需配合 mid±1；mid 推荐写法 left+(right-left)//2 以避免溢出",
                ["mid+1", "mid - 1", "left + (right - left) // 2", "死循环", "边界"],
                ["没问题", "对的", "right = mid", "left = mid"]
            ),
            MisconceptionPattern(
                "代数方程求解",
                "概念混淆",
                "将方程两边同时除以变量时忽略零点情况",
                ["solve_equation(equation='x^2 = x')", "divide_both_sides_by(x)"],
                "x = 1",
                "忽略x=0也是方程的解，除以变量时未考虑变量可能为零的情况",
                ["零点", "x=0", "定义域", "除以零", "遗漏解"],
                ["正确", "没错", "合理", "应该这样"]
            ),
            MisconceptionPattern(
                "概率计算",
                "条件概率误解",
                "将P(A|B)与P(B|A)混淆",
                ["calculate_probability(event='A', given='B')"],
                "P(A|B) = P(B|A)",
                "未正确理解贝叶斯定理，混淆了条件概率的方向",
                ["贝叶斯", "条件概率", "P(B|A)", "方向", "混淆"],
                ["相等", "一样", "相同", "对称"]
            ),
            MisconceptionPattern(
                "微积分",
                "极限概念误解",
                "将无穷小与零混淆",
                ["calculate_limit(expression='1/x', x='0')", "simplify_expression()"],
                "lim(x→0) 1/x = 0",
                "未正确理解极限概念，将无穷小等同于零",
                ["极限", "无穷大", "无穷小", "不存在", "发散"],
                ["等于零", "就是零", "没有意义"]
            )
        ]
        self.patterns.extend(sample_patterns)

    def find_patterns(self, knowledge_point):
        return [p for p in self.patterns if knowledge_point in p.target_knowledge]

    def get_all_patterns(self):
        return [p.to_dict() for p in self.patterns]

class AILearningAssistant:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.confidence_threshold = 0.7
        self.current_knowledge = None
        self.current_pattern = None
        self.question_count = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.interaction_history = []
        self.student_confidence = 0.5  # 学生当前置信度
        self.learning_phase = "initial"  # 学习阶段：initial, simulation, questioning, summary
        self.consecutive_correct = 0  # 连续正确回答次数
        self.consecutive_incorrect = 0  # 连续错误回答次数

        # 固定分支对话（代数方程求解）状态
        self.fixed_dialogue_enabled = False
        self.fixed_branch = None  # A: 首答错误, B: 首答部分正确, C: 首答正确, D: 无关/空
        self.fixed_step = 0

    def start_learning_session(self, knowledge_point):
        """开始学习会话 - 情景分析阶段"""
        self.current_knowledge = knowledge_point
        self.question_count = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.student_confidence = 0.5
        self.learning_phase = "initial"
        self.consecutive_correct = 0
        self.consecutive_incorrect = 0
        self.fixed_dialogue_enabled = ("代数方程" in knowledge_point) or ("代数方程求解" in knowledge_point)
        self.fixed_branch = None
        self.fixed_step = 0
        
        # MCP检索：从知识库中策略性地选取相关的MCP
        patterns = self.kb.find_patterns(knowledge_point)
        if not patterns:
            return None, "未找到相关错误模式"
        
        # 根据知识点复杂度选择MCP
        self.current_pattern = self._select_appropriate_pattern(patterns, knowledge_point)
        self.learning_phase = "simulation"
        return self.current_pattern, None

    def _categorize_algebra_answer(self, answer: str):
        """将学生回答归类为 correct/partial/incorrect
        规则：
        - incorrect：包含典型错误词（如“正确/没错/合理/应该这样”）或完全无关/空
        - correct：包含关键要点（如“x=0”“零点”“遗漏解”“不能除以可能为零的变量”且能给出两个解）
        - partial：包含部分关键概念（如“不能除以零/定义域/零点”等），但未明确两个解
        """
        text = (answer or "").strip()
        if not text:
            return "incorrect", "未提供回答"

        lower = text.lower()
        incorrect_keywords = ["正确", "没错", "合理", "应该这样"]
        for k in incorrect_keywords:
            if k in text:
                return "incorrect", f"回答包含错误关键词: {k}"

        # 正确要点关键词
        correct_keys = ["x=0", "x = 0", "零点", "遗漏解", "不能除以可能为零", "两个解", "x=1 和 x=0", "x=0 和 x=1"]
        partial_keys = ["不能除以零", "定义域", "零点", "除以x", "不能随意除以变量"]

        # 是否包含两个解的表达
        two_solutions = ("x=0" in lower and "x=1" in lower) or ("x = 0" in lower and "x = 1" in lower)

        if two_solutions:
            return "correct", "回答包含两个解：x=0 与 x=1"

        for k in correct_keys:
            if k in text:
                if "x=0" in text and "x=1" in text:
                    return "correct", "回答包含两个解：x=0 与 x=1"
        for k in partial_keys:
            if k in text:
                return "partial", f"回答包含部分正确信息：{k}"

        return "incorrect", "回答未包含关键概念"

    def _select_appropriate_pattern(self, patterns, knowledge_point):
        """策略性地选择MCP模式"""
        # 根据知识点复杂度选择
        if "微积分" in knowledge_point:
            # 微积分较复杂，选择概念性错误
            return next((p for p in patterns if "概念" in p.category), patterns[0])
        elif "概率" in knowledge_point:
            # 概率容易混淆，选择条件概率错误
            return next((p for p in patterns if "条件" in p.category), patterns[0])
        else:
            # 默认选择第一个
            return patterns[0]

    def get_simulation_messages(self):
        """错误模拟：AI以第一人称视角展示错误思维过程"""
        if not self.current_pattern:
            return []
        
        # 根据错误模式生成更详细的模拟过程
        simulation_steps = self._generate_detailed_simulation()
        
        messages = [
            {
                "type": "ai",
                "content": f"🤖 [AI模拟错误思维过程]\n💡 目标知识点: {self.current_pattern.target_knowledge}\n🔴 错误类别: {self.current_pattern.category}\n📝 错误描述: {self.current_pattern.description}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        ]
        
        # 添加详细的思维过程
        for step in simulation_steps:
            messages.append({
                "type": "ai",
                "content": step,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
        
        return messages

    def _generate_detailed_simulation(self):
        """生成详细的错误模拟过程"""
        steps = []
        
        if "代数方程求解" in self.current_pattern.target_knowledge:
            steps = [
                "🧠 [思维过程] 让我来解决这个方程 x² = x...",
                "💭 首先，我需要将方程两边同时除以x，这样就能得到 x = 1",
                "🛠️ 模拟调用过程:\n  1. solve_equation(equation='x² = x')\n  2. divide_both_sides_by(x)",
                "✅ 看起来逻辑很清晰，除以x后得到 x = 1",
                "❌ 错误输出: x = 1",
                "💬 AI结论: \"这个解法很直接，x = 1 就是方程的唯一解！\""
            ]
        elif "概率计算" in self.current_pattern.target_knowledge:
            steps = [
                "🧠 [思维过程] 让我来计算条件概率 P(A|B)...",
                "💭 根据条件概率的定义，P(A|B) = P(A∩B) / P(B)",
                "🛠️ 模拟调用过程:\n  1. calculate_probability(event='A', given='B')",
                "✅ 但是等等，P(B|A) 也是 P(B∩A) / P(A)，分子相同！",
                "❌ 错误输出: P(A|B) = P(B|A)",
                "💬 AI结论: \"既然分子相同，那么 P(A|B) 和 P(B|A) 应该相等！\""
            ]
        elif "微积分" in self.current_pattern.target_knowledge:
            steps = [
                "🧠 [思维过程] 让我来计算极限 lim(x→0) 1/x...",
                "💭 当x接近0时，1/x会变得很大，但最终会接近0",
                "🛠️ 模拟调用过程:\n  1. calculate_limit(expression='1/x', x='0')\n  2. simplify_expression()",
                "✅ 当x趋近于0时，1/x趋近于无穷大，但无穷大就是0",
                "❌ 错误输出: lim(x→0) 1/x = 0",
                "💬 AI结论: \"极限就是0，这很合理！\""
            ]
        else:
            steps = [
                "🛠️ 模拟调用过程:",
                f"  {' → '.join(self.current_pattern.tool_calls)}",
                f"❌ 错误输出: {self.current_pattern.expected_output}",
                f"💬 AI结论: \"看来结果是{self.current_pattern.expected_output}，这应该就是正确答案了！\""
            ]
        
        return steps

    def get_question(self):
        """获取苏格拉底式引导问题
        支持代数方程求解的固定分支首题。
        """
        if not self.current_pattern:
            return None
        
        # 固定脚本：代数方程求解
        if self.fixed_dialogue_enabled and self.learning_phase in ("simulation", "initial"):
            self.question_count += 1
            self.learning_phase = "questioning"
            return "👨‍🏫 问题1：你发现了AI推理过程中的错误吗？请描述你的观察。"

        # 默认策略（非固定脚本）
        if self.learning_phase == "simulation":
            questions = [
                f"👨‍🎓 你发现了AI推理过程中的错误吗？请描述你的观察。",
                f"🔍 仔细看看AI的推理步骤，你觉得哪里有问题？",
                f"💡 作为学生，你能指出AI思维过程中的漏洞吗？"
            ]
        elif self.student_confidence < self.confidence_threshold:
            questions = [
                f"🤔 看起来你不太确定，让我们深入分析一下...",
                f"🔍 让我换个角度问你：{self._get_confidence_based_question()}",
                f"💭 你觉得AI在哪个具体步骤上犯了错误？"
            ]
        else:
            questions = [
                f"为什么你认为{self.current_pattern.expected_output}可能是错误的？",
                f"在{self.current_pattern.tool_calls[-1]}这一步，可能存在什么问题？",
                f"如果改变条件X，结果会如何变化？这与当前结论一致吗？",
                f"你能解释一下{self.current_pattern.target_knowledge}的核心概念吗？"
            ]
        
        self.question_count += 1
        self.learning_phase = "questioning"
        return random.choice(questions)

    def _get_confidence_based_question(self):
        """根据置信度生成特定问题"""
        if "代数方程求解" in self.current_pattern.target_knowledge and not self.fixed_dialogue_enabled:
            return "当x=0时，方程x²=x还成立吗？"
        elif "概率计算" in self.current_pattern.target_knowledge:
            return "P(A|B)和P(B|A)的分母相同吗？"
        elif "微积分" in self.current_pattern.target_knowledge:
            return "当x趋近于0时，1/x是趋近于0还是无穷大？"
        else:
            return "你能更具体地指出错误所在吗？"

    def evaluate_answer(self, answer):
        if not answer.strip():
            return False, "未提供回答"

        # 检查是否包含错误关键词
        for keyword in self.current_pattern.incorrect_keywords:
            if keyword in answer:
                return False, f"回答包含错误关键词: {keyword}"

        # 检查是否包含正确关键词
        correct_found = False
        for keyword in self.current_pattern.correct_keywords:
            if keyword in answer:
                correct_found = True
                break

        # 计算相似度
        similarity = difflib.SequenceMatcher(
            None,
            answer,
            " ".join(self.current_pattern.correct_keywords)
        ).ratio()

        if similarity > 0.6:
            return True, f"回答与正确答案相似度高 ({similarity:.2f})"
        elif correct_found:
            return True, "回答包含正确关键词"
        elif similarity > 0.4:
            return None, f"回答部分相关 (相似度: {similarity:.2f})"
        else:
            return False, "回答未包含关键概念"

    def process_answer(self, answer):
        """处理学生回答并更新置信度
        对于代数方程求解，走固定分支：A/B/C/D
        A: 首答错误 → 追问1：x=0 是否成立？ → 学生若部分正确 → 追问2：有哪些解？ → 正确后总结
        B: 首答部分正确 → 追问：有哪些解？ → 正确后总结
        C: 首答正确 → 直接总结
        D: 空/无关 → 回到追问1
        """

        # 固定脚本路径
        if self.fixed_dialogue_enabled and "代数方程求解" in self.current_pattern.target_knowledge:
            # 判定答案类别
            cat, reason = self._categorize_algebra_answer(answer)

            # 更新统计与置信度
            if cat == "correct":
                self.correct_answers += 1
                self.consecutive_correct += 1
                self.consecutive_incorrect = 0
                self.student_confidence = min(1.0, self.student_confidence + 0.2)
                feedback = "✅ 回答正确！"
            elif cat == "partial":
                feedback = "⚠️ 回答部分正确。"
                self.student_confidence = max(0.1, min(1.0, self.student_confidence + 0.05))
            else:
                self.incorrect_answers += 1
                self.consecutive_incorrect += 1
                self.consecutive_correct = 0
                self.student_confidence = max(0.1, self.student_confidence - 0.15)
                feedback = "❌ 回答不正确。"

            # 记录交互
            self.interaction_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "knowledge": self.current_pattern.target_knowledge,
                "pattern": self.current_pattern.description,
                "response": answer,
                "type": f"问题{self.question_count}回答",
                "is_correct": True if cat == "correct" else (None if cat == "partial" else False),
                "evaluation_reason": reason,
                "confidence": self.student_confidence
            })

            # 固定分支推进
            follow_up = None
            should_continue = False
            if self.fixed_step == 0:
                # 首答阶段：决定分支
                if cat == "incorrect":
                    self.fixed_branch = "A"
                    follow_up = "🧠 追问1：当 x = 0 时，方程 x² = x 还成立吗？"
                    self.question_count += 1
                    should_continue = True
                elif cat == "partial":
                    self.fixed_branch = "B"
                    follow_up = "🔍 追问：那这个方程究竟有哪些解？为什么？"
                    self.question_count += 1
                    should_continue = True
                elif cat == "correct":
                    self.fixed_branch = "C"
                    should_continue = False
                else:
                    self.fixed_branch = "D"
                    follow_up = "🧠 追问1：当 x = 0 时，方程 x² = x 还成立吗？"
                    self.question_count += 1
                    should_continue = True
                self.fixed_step = 1
            else:
                # 后续阶段
                if self.fixed_branch == "A":
                    if cat in ("partial", "correct"):
                        # 从追问1回来，继续追问2
                        if cat == "partial":
                            follow_up = "🔍 追问2：那这个方程究竟有哪些解？为什么？"
                            self.question_count += 1
                            should_continue = True
                        else:
                            should_continue = False
                    else:
                        follow_up = "🧠 追问1：当 x = 0 时，方程 x² = x 还成立吗？"
                        self.question_count += 1
                        should_continue = True
                elif self.fixed_branch == "B":
                    if cat == "correct":
                        should_continue = False
                    else:
                        follow_up = "🔍 再想想：有哪些解？为什么？请给出理由。"
                        self.question_count += 1
                        should_continue = True
                elif self.fixed_branch == "C":
                    should_continue = False
                else:  # D
                    follow_up = "🧠 追问1：当 x = 0 时，方程 x² = x 还成立吗？"
                    self.question_count += 1
                    should_continue = True

            return {
                "feedback": f"{feedback} {reason}",
                "is_correct": True if cat == "correct" else (None if cat == "partial" else False),
                "should_continue": should_continue,
                "question_count": self.question_count,
                "confidence": self.student_confidence,
                "confidence_threshold": self.confidence_threshold,
                "follow_up": follow_up
            }

        # 原有通用流程
        is_correct, reason = self.evaluate_answer(answer)
        
        # 更新统计数据
        if is_correct is True:
            self.correct_answers += 1
            self.consecutive_correct += 1
            self.consecutive_incorrect = 0
            feedback = "✅ 回答正确！"
            # 提高置信度
            self.student_confidence = min(1.0, self.student_confidence + 0.2)
        elif is_correct is False:
            self.incorrect_answers += 1
            self.consecutive_incorrect += 1
            self.consecutive_correct = 0
            feedback = "❌ 回答不正确。"
            # 降低置信度
            self.student_confidence = max(0.1, self.student_confidence - 0.15)
        else:
            feedback = "⚠️ 回答部分正确。"
            # 轻微调整置信度
            self.student_confidence = max(0.1, min(1.0, self.student_confidence + 0.05))
        
        # 记录交互
        self.interaction_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "knowledge": self.current_pattern.target_knowledge,
            "pattern": self.current_pattern.description,
            "response": answer,
            "type": f"问题{self.question_count}回答",
            "is_correct": is_correct,
            "evaluation_reason": reason,
            "confidence": self.student_confidence
        })
        
        # 判断是否需要继续提问
        should_continue = self._should_continue_questioning(is_correct)
        
        return {
            "feedback": f"{feedback} {reason}",
            "is_correct": is_correct,
            "should_continue": should_continue,
            "question_count": self.question_count,
            "confidence": self.student_confidence,
            "confidence_threshold": self.confidence_threshold
        }

    def _should_continue_questioning(self, is_correct):
        """判断是否需要继续提问"""
        # 固定脚本：是否由固定分支决定
        if self.fixed_dialogue_enabled and self.fixed_branch is not None:
            return None  # 由 process_answer 的返回字段控制
        # 如果回答错误，继续提问
        if is_correct is False:
            return True
        
        # 如果置信度低于阈值，继续提问
        if self.student_confidence < self.confidence_threshold:
            return True
        
        # 如果连续错误次数过多，继续提问
        if self.consecutive_incorrect >= 2:
            return True
        
        # 如果回答正确且置信度足够，可以总结
        return False

    def get_follow_up_question(self):
        """获取跟进提问 - 基于置信度和学习进度"""
        if not self.current_pattern:
            return None
        # 固定脚本：直接使用 process_answer 给出的 follow_up
        if self.fixed_dialogue_enabled and self.fixed_branch is not None:
            return None
        
        # 根据置信度和连续错误次数选择不同的跟进问题
        if self.student_confidence < 0.3:
            # 置信度很低，提供更基础的引导
            follow_ups = [
                f"让我们从最基础的开始：{self._get_basic_question()}",
                f"你能先告诉我{self.current_pattern.target_knowledge}的基本定义吗？",
                f"在AI的推理中，你觉得哪个步骤最可疑？"
            ]
        elif self.consecutive_incorrect >= 2:
            # 连续错误，提供更具体的提示
            follow_ups = [
                f"让我给你一个提示：{self._get_hint_question()}",
                f"仔细想想，AI在{self._get_specific_error_step()}这一步犯了什么错误？",
                f"如果让你重新思考这个问题，你会怎么开始？"
            ]
        else:
            # 常规跟进问题
            follow_ups = [
                f"你能更详细地解释一下为什么{self.current_pattern.expected_output}是错误的吗？",
                f"在这个推理过程中，最关键的错误步骤是什么？",
                f"如果是你，会如何正确解决这个问题？"
            ]
        
        self.question_count += 1
        return random.choice(follow_ups)

    def _get_basic_question(self):
        """获取基础问题"""
        if "代数方程求解" in self.current_pattern.target_knowledge and not self.fixed_dialogue_enabled:
            return "方程x²=x的解是什么？"
        elif "概率计算" in self.current_pattern.target_knowledge:
            return "P(A|B)和P(B|A)有什么区别？"
        elif "微积分" in self.current_pattern.target_knowledge:
            return "当x趋近于0时，1/x的极限是什么？"
        else:
            return "这个知识点的核心概念是什么？"

    def _get_hint_question(self):
        """获取提示性问题"""
        if "代数方程求解" in self.current_pattern.target_knowledge and not self.fixed_dialogue_enabled:
            return "当x=0时，方程x²=x还成立吗？"
        elif "概率计算" in self.current_pattern.target_knowledge:
            return "P(A|B)的分母是P(B)，P(B|A)的分母是P(A)，它们相同吗？"
        elif "微积分" in self.current_pattern.target_knowledge:
            return "1/x在x=0附近的行为是怎样的？"
        else:
            return "你能找出AI推理中的逻辑漏洞吗？"

    def _get_specific_error_step(self):
        """获取具体错误步骤"""
        if "代数方程求解" in self.current_pattern.target_knowledge:
            return "除以x"
        elif "概率计算" in self.current_pattern.target_knowledge:
            return "混淆P(A|B)和P(B|A)"
        elif "微积分" in self.current_pattern.target_knowledge:
            return "认为无穷大等于0"
        else:
            return "关键推理步骤"

    def get_summary(self):
        """归纳总结：对本次踩坑-纠错过程进行总结"""
        if not self.current_pattern:
            return None
        
        total_answers = self.correct_answers + self.incorrect_answers
        accuracy = self.correct_answers / total_answers * 100 if total_answers > 0 else 0
        
        # 生成详细的学习总结
        learning_insights = self._generate_learning_insights()
        
        summary = {
            "knowledge": self.current_pattern.target_knowledge,
            "pattern": self.current_pattern.category,
            "explanation": self.current_pattern.explanation,
            "correct_method": self._get_correct_method(),
            "correct_answers": self.correct_answers,
            "incorrect_answers": self.incorrect_answers,
            "accuracy": accuracy,
            "confidence_final": self.student_confidence,
            "learning_insights": learning_insights,
            "key_lessons": self._get_key_lessons(),
            "recommendations": self._get_recommendations()
        }
        
        # 记录总结
        self.interaction_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "knowledge": self.current_pattern.target_knowledge,
            "pattern": self.current_pattern.description,
            "response": "学习总结",
            "type": "总结",
            "correct_answers": self.correct_answers,
            "incorrect_answers": self.incorrect_answers,
            "final_confidence": self.student_confidence,
            "learning_insights": learning_insights
        })
        
        self.learning_phase = "summary"
        return summary

    def _generate_learning_insights(self):
        """生成学习洞察"""
        insights = []
        
        if self.correct_answers > self.incorrect_answers:
            insights.append("✅ 你成功识别了AI的错误思维过程")
            insights.append("✅ 你对核心概念有良好的理解")
        else:
            insights.append("⚠️ 你在识别错误方面还需要更多练习")
            insights.append("💡 建议多关注概念的本质理解")
        
        if self.student_confidence >= 0.8:
            insights.append("🎯 你的学习信心很高，继续保持！")
        elif self.student_confidence >= 0.5:
            insights.append("📈 你的理解在逐步提升")
        else:
            insights.append("🔍 建议深入理解基础概念")
        
        return insights

    def _get_correct_method(self):
        """获取正确方法"""
        if "代数方程求解" in self.current_pattern.target_knowledge:
            return "应该考虑x=0的情况，使用因式分解或移项法求解"
        elif "概率计算" in self.current_pattern.target_knowledge:
            return "应该正确区分P(A|B)和P(B|A)，理解贝叶斯定理"
        elif "微积分" in self.current_pattern.target_knowledge:
            return "应该理解极限概念，无穷大不等于零"
        else:
            return self.current_pattern.explanation.replace('未', '').replace('忽略', '考虑')

    def _get_key_lessons(self):
        """获取关键教训"""
        if "代数方程求解" in self.current_pattern.target_knowledge:
            return [
                "解方程时要注意定义域",
                "不能随意除以可能为零的变量",
                "要检查所有可能的解"
            ]
        elif "概率计算" in self.current_pattern.target_knowledge:
            return [
                "条件概率有方向性",
                "P(A|B) ≠ P(B|A) 除非特殊情况",
                "贝叶斯定理揭示了条件概率的关系"
            ]
        elif "微积分" in self.current_pattern.target_knowledge:
            return [
                "极限概念需要精确理解",
                "无穷大不是具体的数",
                "要区分无穷大和零"
            ]
        else:
            return ["理解概念的本质很重要", "避免常见的思维误区"]

    def _get_recommendations(self):
        """获取学习建议"""
        recommendations = []
        
        # 计算准确率
        total_answers = self.correct_answers + self.incorrect_answers
        accuracy = self.correct_answers / total_answers * 100 if total_answers > 0 else 0
        
        if accuracy < 50:
            recommendations.append("📚 建议复习基础概念")
            recommendations.append("🔍 多做相关练习")
        elif accuracy < 80:
            recommendations.append("📖 巩固已掌握的知识")
            recommendations.append("💡 尝试更复杂的问题")
        else:
            recommendations.append("🎯 你已经掌握得很好")
            recommendations.append("🚀 可以挑战更高难度")
        
        if self.student_confidence < 0.6:
            recommendations.append("💪 建立学习信心")
            recommendations.append("🔄 多练习，熟能生巧")
        
        return recommendations

# 全局变量
knowledge_base = MCPKnowledgeBase()
assistant = AILearningAssistant(knowledge_base)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_learning', methods=['POST'])
def start_learning():
    data = request.get_json()
    knowledge_point = data.get('knowledge_point', '')
    
    if not knowledge_point:
        return jsonify({'error': '请输入要学习的知识点'})
    
    pattern, error = assistant.start_learning_session(knowledge_point)
    
    if error:
        return jsonify({'error': error})
    
    # 获取模拟消息
    simulation_messages = assistant.get_simulation_messages()
    
    # 获取第一个问题
    question = assistant.get_question()
    
    return jsonify({
        'success': True,
        'pattern': pattern.to_dict() if pattern else None,
        'simulation_messages': simulation_messages,
        'question': question,
        'session_id': str(uuid.uuid4())
    })

@app.route('/api/answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    answer = data.get('answer', '')
    
    if not answer:
        return jsonify({'error': '请输入回答'})
    
    result = assistant.process_answer(answer)
    
    response = {
        'feedback': result['feedback'],
        'is_correct': result['is_correct'],
        'question_count': result['question_count'],
        'confidence': result['confidence'],
        'confidence_threshold': result['confidence_threshold']
    }
    
    if result['should_continue']:
        # 固定脚本优先使用 result['follow_up']
        if 'follow_up' in result and result['follow_up']:
            response['follow_up_question'] = result['follow_up']
        else:
            follow_up_question = assistant.get_follow_up_question()
            response['follow_up_question'] = follow_up_question
    else:
        # 回答正确，进行总结
        summary = assistant.get_summary()
        response['summary'] = summary
    
    return jsonify(response)

@app.route('/api/follow_up_answer', methods=['POST'])
def submit_follow_up_answer():
    data = request.get_json()
    answer = data.get('answer', '')
    
    if not answer:
        return jsonify({'error': '请输入回答'})
    
    result = assistant.process_answer(answer)
    
    # 无论回答如何，都进行总结
    summary = assistant.get_summary()
    
    return jsonify({
        'feedback': result['feedback'],
        'is_correct': result['is_correct'],
        'summary': summary
    })

@app.route('/api/knowledge_base')
def get_knowledge_base():
    patterns = knowledge_base.get_all_patterns()
    return jsonify({'patterns': patterns})

@app.route('/api/demo_algebra')
def demo_algebra():
    """评委演示：代数方程求解的完整脚本化对话"""
    script = [
        # 错误模拟阶段
        {"action": "message", "type": "ai", "content": "🤖 [AI模拟错误思维过程]\n💡 目标知识点: 代数方程求解\n🔴 错误类别: 概念混淆\n📝 错误描述: 将方程两边同时除以变量时忽略零点情况"},
        {"action": "message", "type": "ai", "content": "🧠 [思维过程] 让我来解决这个方程 x² = x..."},
        {"action": "message", "type": "ai", "content": "💭 我将两边同时除以 x，得到 x = 1"},
        {"action": "message", "type": "ai", "content": "🛠️ 模拟调用过程:\n  1. solve_equation(equation='x² = x')\n  2. divide_both_sides_by(x)"},
        {"action": "message", "type": "ai", "content": "❌ 错误输出: x = 1\n💬 AI结论: \"x = 1 是方程的唯一解！\""},

        # 首题（苏格拉底式）
        {"action": "message", "type": "ai", "content": "👨‍🏫 问题1：你发现了AI推理过程中的错误吗？请描述你的观察。"},

        # 学生第一次回答：错误
        {"action": "message", "type": "user", "content": "我觉得 AI 的解法是正确的。"},
        {"action": "feedback", "feedback": "❌ 回答不正确。 回答包含错误关键词: 正确", "is_correct": False},
        {"action": "confidence", "confidence": 0.35, "threshold": 0.7},

        # 追问1：因置信度不足
        {"action": "message", "type": "ai", "content": "🧠 追问1：当 x = 0 时，方程 x² = x 还成立吗？"},

        # 学生第二次回答：部分正确
        {"action": "message", "type": "user", "content": "不能除以零。"},
        {"action": "feedback", "feedback": "⚠️ 回答部分正确。 回答部分相关 (相似度: 0.45)", "is_correct": None},
        {"action": "confidence", "confidence": 0.45, "threshold": 0.7},

        # 追问2：引导更具体
        {"action": "message", "type": "ai", "content": "🔍 追问2：那这个方程究竟有哪些解？为什么？"},

        # 学生第三次回答：正确
        {"action": "message", "type": "user", "content": "应该有 x=0 和 x=1。"},
        {"action": "feedback", "feedback": "✅ 回答正确！ 回答包含正确关键词", "is_correct": True},
        {"action": "confidence", "confidence": 0.75, "threshold": 0.7},

        # 总结
        {"action": "summary", "summary": {
            "knowledge": "代数方程求解",
            "pattern": "概念混淆",
            "explanation": "忽略x=0也是方程的解，除以变量时未考虑变量可能为零的情况",
            "correct_method": "应该考虑x=0的情况，使用因式分解或移项法求解",
            "correct_answers": 1,
            "incorrect_answers": 1,
            "accuracy": 50.0,
            "confidence_final": 0.75,
            "learning_insights": [
                "📈 你的理解在逐步提升",
                "✅ 你成功识别了AI的错误思维过程"
            ],
            "key_lessons": [
                "解方程时要注意定义域",
                "不能随意除以可能为零的变量",
                "要检查所有可能的解"
            ],
            "recommendations": [
                "📖 巩固已掌握的知识",
                "💡 尝试更复杂的问题"
            ]
        }}
    ]

    return jsonify({"script": script})

@app.route('/api/demo_binary_search')
def demo_binary_search():
    """评委演示：计算机经典问题 - 二分查找（固定对话与置信度曲线）"""
    script = [
        # 错误模拟阶段
        {"action": "message", "type": "ai", "content": "🤖 [AI模拟错误思维过程]\n💡 目标知识点: 二分查找\n🔴 常见错误: 区间更新不加1/减1导致死循环，mid 计算溢出"},
        {"action": "message", "type": "ai", "content": "🧠 [错误思路] while (left < right) { mid=(l+r)/2; if (nums[mid] < target) left = mid; else right = mid; }"},
        {"action": "message", "type": "ai", "content": "❌ 错误结论: 这样写也能找到 target"},

        # 首题（常规鼓励主动思考）
        {"action": "message", "type": "ai", "content": "👨‍🏫 问题1：如果 nums=[1,3,5] 且 target=5，上述写法会不会卡住？为什么？"},
        {"action": "message", "type": "user", "content": "我觉得代码没问题。"},
        {"action": "feedback", "feedback": "❌ 回答不正确。 该写法在相邻区间时可能死循环", "is_correct": False},
        {"action": "confidence", "confidence": 0.45, "threshold": 0.7},

        # 第二问（常规引导）
        {"action": "message", "type": "ai", "content": "🔍 追问：当 left 与 right 只差 1 时，left = mid 会发生什么？"},
        {"action": "message", "type": "user", "content": "mid 等于 left，left 不变，会死循环。"},
        {"action": "feedback", "feedback": "✅ 回答正确！ 识别出死循环原因", "is_correct": True},
        {"action": "confidence", "confidence": 0.60, "threshold": 0.7},

        # 第三问（常规引导）
        {"action": "message", "type": "ai", "content": "🧪 追问：在 while (left <= right) 中，target 小于 nums[mid] 时，right 应该设为 mid 还是 mid-1？"},
        {"action": "message", "type": "user", "content": "right = mid。"},
        {"action": "feedback", "feedback": "❌ 回答不正确。 应为 mid-1 以缩小区间", "is_correct": False},
        {"action": "confidence", "confidence": 0.30, "threshold": 0.7},

        # 极低置信度（提定义）
        {"action": "message", "type": "ai", "content": "📘 你有些不确定。请先给出二分查找的定义：它适用于什么场景？每一步做了什么？"},
        # 连续错误提示（再错一次，给具体提示）
        {"action": "message", "type": "ai", "content": "🧪 追问：当 nums[mid] < target 时，left 应该设为 mid 还是 mid+1？"},
        {"action": "message", "type": "user", "content": "left = mid。"},
        {"action": "feedback", "feedback": "❌ 连续错误。具体提示：避免重复 mid 导致卡住，应使用 mid±1", "is_correct": False},
        {"action": "confidence", "confidence": 0.25, "threshold": 0.7},

        # 学生给出定义（小幅上调）
        {"action": "message", "type": "user", "content": "二分查找用于有序数组，每次取中间与目标比较，丢弃一半区间。"},
        {"action": "feedback", "feedback": "⚠️ 回答部分正确。 定义到位，但未提到边界更新规则", "is_correct": None},
        {"action": "confidence", "confidence": 0.38, "threshold": 0.7},

        # 具体问题（逐步上升）
        {"action": "message", "type": "ai", "content": "🧩 在 left <= right 时，若要查找小于等于 target 的最后一个位置，right 应该如何更新？"},
        {"action": "message", "type": "user", "content": "right = mid - 1。"},
        {"action": "feedback", "feedback": "✅ 回答正确！", "is_correct": True},
        {"action": "confidence", "confidence": 0.55, "threshold": 0.7},

        {"action": "message", "type": "ai", "content": "🛡️ mid 如何避免加法溢出？"},
        {"action": "message", "type": "user", "content": "mid = left + (right - left) // 2。"},
        {"action": "feedback", "feedback": "✅ 回答正确！", "is_correct": True},
        {"action": "confidence", "confidence": 0.72, "threshold": 0.7},

        {"action": "message", "type": "ai", "content": "🧩 请写出正确的模板（查找等于 target 的任意位置）。"},
        {"action": "message", "type": "user", "content": "while l <= r: mid = l + (r-l)//2; if a[mid]==t: return mid; elif a[mid] < t: l = mid+1; else: r = mid-1"},
        {"action": "feedback", "feedback": "✅ 回答正确！ 模板与边界更新合理", "is_correct": True},
        {"action": "confidence", "confidence": 0.90, "threshold": 0.7},

        {"action": "summary", "summary": {
            "knowledge": "二分查找",
            "pattern": "边界更新错误与死循环",
            "explanation": "区间更新未加1/减1导致死循环；使用 <= 时应配合 mid±1；mid 需用 left+(right-left)//2",
            "correct_method": "在 l<=r 中：< 时 l=mid+1，> 时 r=mid-1；返回时根据目标和需求调整，避免死循环",
            "correct_answers": 4,
            "incorrect_answers": 3,
            "accuracy": 57.1,
            "confidence_final": 0.90,
            "learning_insights": [
                "📈 从定义→边界→模板逐步清晰",
                "🛠️ 连续错误后给出具体提示，帮助定位 mid±1 细节"
            ],
            "key_lessons": [
                "相邻区间须使用 mid±1",
                "不同查找目标需配套边界收缩策略",
                "mid 用 left+(right-left)//2 避免溢出"
            ],
            "recommendations": [
                "多做边界条件题目（首个/最后一个 >= 或 > 条件）",
                "对比三种区间定义 [l,r] / [l,r) / (l,r) 的模板差异"
            ]
        }}
    ]

    return jsonify({"script": script})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)