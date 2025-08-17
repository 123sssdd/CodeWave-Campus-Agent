#!/usr/bin/env python3
"""
理论题和简答题智能评分系统
支持关键词匹配、部分评分、详细反馈和鼓励性评语
"""

import re
import jieba
import difflib
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class GradingResult:
    """评分结果"""
    score: float  # 0-1之间的分数
    is_correct: bool  # 是否完全正确
    feedback: str  # 详细反馈
    correct_keywords: List[str]  # 答对的关键词
    missing_keywords: List[str]  # 遗漏的关键词
    incorrect_parts: List[str]  # 错误的部分
    encouragement: str  # 鼓励性评语

class TheoryQuestionGrader:
    """理论题评分器"""
    
    def __init__(self):
        # 同义词词典，用于关键词匹配
        self.synonyms = {
            # 数据结构相关
            "数组": ["列表", "array", "list"],
            "链表": ["linked list", "链式结构"],
            "栈": ["stack", "堆栈"],
            "队列": ["queue"],
            "树": ["tree", "二叉树"],
            "图": ["graph"],
            "哈希表": ["散列表", "hash table", "hash map", "映射"],
            
            # 算法相关
            "时间复杂度": ["时间开销", "运行时间"],
            "空间复杂度": ["空间开销", "内存开销"],
            "递归": ["递归调用", "recursion"],
            "迭代": ["循环", "iteration", "loop"],
            "排序": ["sort", "sorting"],
            "搜索": ["查找", "search"],
            
            # 编程概念
            "面向对象": ["oop", "object-oriented"],
            "封装": ["encapsulation"],
            "继承": ["inheritance"],
            "多态": ["polymorphism"],
            "函数": ["方法", "function", "method"],
            "变量": ["variable"],
            "常量": ["constant"],
            
            # 性能相关
            "优化": ["改进", "提升", "optimization"],
            "效率": ["性能", "performance"],
            "快速": ["高效", "fast", "efficient"],
            "慢": ["低效", "slow", "inefficient"]
        }
        
        # 鼓励性评语模板
        self.encouragements = {
            "excellent": [
                "回答非常精彩！你对这个概念的理解很深入。",
                "太棒了！你的分析很到位，展现了扎实的基础知识。",
                "完美的回答！继续保持这样的学习状态。"
            ],
            "good": [
                "很好的回答！你掌握了大部分要点。",
                "不错的理解！在此基础上继续深入会更好。",
                "回答得很好，继续努力完善细节部分。"
            ],
            "partial": [
                "你的理解方向是对的，但还需要补充一些要点。",
                "有一定的理解基础，继续学习会有很大提升。",
                "回答中有正确的部分，加油完善其他方面！"
            ],
            "poor": [
                "看起来需要加强这部分的学习，建议重新复习相关概念。",
                "别灰心！每个人都有学习的过程，多练习就会进步。",
                "这个概念确实有难度，建议先从基础开始逐步理解。"
            ]
        }
    
    def grade_theory_question(self, user_answer: str, correct_answer: str, 
                            question_content: str = "") -> GradingResult:
        """
        评分理论题
        
        Args:
            user_answer: 用户答案
            correct_answer: 标准答案
            question_content: 题目内容（用于上下文理解）
            
        Returns:
            GradingResult: 详细的评分结果
        """
        # 预处理答案
        user_clean = self._clean_text(user_answer)
        correct_clean = self._clean_text(correct_answer)
        
        if not user_clean:
            return GradingResult(
                score=0.0,
                is_correct=False,
                feedback="回答不能为空，请提供你的理解和想法。",
                correct_keywords=[],
                missing_keywords=self._extract_keywords(correct_clean),
                incorrect_parts=[],
                encouragement="别担心，开始思考和表达就是学习的第一步！"
            )
        
        # 提取关键词
        user_keywords = self._extract_keywords(user_clean)
        correct_keywords = self._extract_keywords(correct_clean)
        
        # 匹配关键词
        matched_keywords, missing_keywords = self._match_keywords(
            user_keywords, correct_keywords
        )
        
        # 计算基础分数
        base_score = len(matched_keywords) / len(correct_keywords) if correct_keywords else 0
        
        # 语义相似度加分
        similarity_score = self._calculate_similarity(user_clean, correct_clean)
        
        # 综合分数
        final_score = min(base_score * 0.7 + similarity_score * 0.3, 1.0)
        
        # 检查错误信息
        incorrect_parts = self._find_incorrect_parts(user_clean, correct_clean)
        
        # 生成反馈
        feedback = self._generate_feedback(
            matched_keywords, missing_keywords, incorrect_parts, final_score
        )
        
        # 生成鼓励性评语
        encouragement = self._generate_encouragement(final_score)
        
        return GradingResult(
            score=final_score,
            is_correct=final_score >= 0.8,
            feedback=feedback,
            correct_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            incorrect_parts=incorrect_parts,
            encouragement=encouragement
        )
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        # 移除标点符号（保留中文标点的语义）
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        return text.lower()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        # 使用jieba分词
        words = jieba.lcut(text)
        
        # 过滤停用词和短词
        stop_words = {'的', '是', '在', '有', '和', '与', '或', '但', '而', '因为', '所以', 
                     '可以', '能够', '就是', '这个', '那个', '一个', '一种', '这种', '那种',
                     'the', 'is', 'are', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                     'for', 'of', 'with', 'by', 'from', 'as', 'an', 'a'}
        
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) > 1 and word not in stop_words:
                keywords.append(word)
        
        return keywords
    
    def _match_keywords(self, user_keywords: List[str], 
                       correct_keywords: List[str]) -> Tuple[List[str], List[str]]:
        """匹配关键词，考虑同义词"""
        matched = []
        missing = []
        
        # 创建用户关键词的标准化版本
        user_normalized = set()
        for keyword in user_keywords:
            user_normalized.add(keyword)
            # 添加同义词
            for standard, synonyms in self.synonyms.items():
                if keyword in synonyms or keyword == standard:
                    user_normalized.add(standard)
                    user_normalized.update(synonyms)
        
        # 检查每个正确答案的关键词
        for correct_keyword in correct_keywords:
            found = False
            
            # 直接匹配
            if correct_keyword in user_normalized:
                matched.append(correct_keyword)
                found = True
            else:
                # 同义词匹配
                for standard, synonyms in self.synonyms.items():
                    if correct_keyword == standard or correct_keyword in synonyms:
                        if standard in user_normalized:
                            matched.append(correct_keyword)
                            found = True
                            break
                        for synonym in synonyms:
                            if synonym in user_normalized:
                                matched.append(correct_keyword)
                                found = True
                                break
                    if found:
                        break
                
                # 模糊匹配（编辑距离）
                if not found:
                    for user_keyword in user_keywords:
                        similarity = difflib.SequenceMatcher(None, correct_keyword, user_keyword).ratio()
                        if similarity > 0.8:  # 80%相似度
                            matched.append(correct_keyword)
                            found = True
                            break
            
            if not found:
                missing.append(correct_keyword)
        
        return matched, missing
    
    def _calculate_similarity(self, user_text: str, correct_text: str) -> float:
        """计算文本相似度"""
        if not user_text or not correct_text:
            return 0.0
        
        # 使用difflib计算序列相似度
        similarity = difflib.SequenceMatcher(None, user_text, correct_text).ratio()
        return similarity
    
    def _find_incorrect_parts(self, user_text: str, correct_text: str) -> List[str]:
        """找出可能错误的部分"""
        user_keywords = set(self._extract_keywords(user_text))
        correct_keywords = set(self._extract_keywords(correct_text))
        
        # 找出用户答案中可能错误的关键词
        incorrect = []
        
        # 一些明显错误的概念对
        contradictions = {
            "栈": ["先进先出", "fifo"],
            "队列": ["后进先出", "lifo"],
            "数组": ["不连续", "链式"],
            "链表": ["连续存储", "随机访问"],
            "递归": ["循环", "迭代"],
        }
        
        for keyword in user_keywords:
            for correct_concept, wrong_concepts in contradictions.items():
                if correct_concept in correct_keywords and keyword in wrong_concepts:
                    incorrect.append(f"'{keyword}'与'{correct_concept}'的特性不符")
        
        return incorrect
    
    def _generate_feedback(self, matched_keywords: List[str], missing_keywords: List[str],
                          incorrect_parts: List[str], score: float) -> str:
        """生成详细反馈"""
        feedback_parts = []
        
        # 正确部分的反馈
        if matched_keywords:
            feedback_parts.append(f"✅ 答对的要点：{', '.join(matched_keywords[:5])}")  # 只显示前5个
            if len(matched_keywords) > 5:
                feedback_parts.append(f"   （还有{len(matched_keywords)-5}个要点答对了）")
        
        # 遗漏部分的反馈
        if missing_keywords:
            feedback_parts.append(f"❓ 遗漏的要点：{', '.join(missing_keywords[:3])}")  # 只显示前3个
            if len(missing_keywords) > 3:
                feedback_parts.append(f"   （还需要补充{len(missing_keywords)-3}个要点）")
        
        # 错误部分的反馈
        if incorrect_parts:
            feedback_parts.append(f"❌ 需要修正：{'; '.join(incorrect_parts)}")
        
        # 总体评价
        if score >= 0.9:
            feedback_parts.append("🌟 总体评价：回答非常全面准确！")
        elif score >= 0.7:
            feedback_parts.append("👍 总体评价：回答基本准确，有小部分可以完善。")
        elif score >= 0.5:
            feedback_parts.append("📚 总体评价：理解了部分概念，建议补充关键要点。")
        else:
            feedback_parts.append("💪 总体评价：需要加强学习，建议复习相关基础知识。")
        
        return "\n".join(feedback_parts)
    
    def _generate_encouragement(self, score: float) -> str:
        """生成鼓励性评语"""
        import random
        
        if score >= 0.9:
            category = "excellent"
        elif score >= 0.7:
            category = "good"
        elif score >= 0.4:
            category = "partial"
        else:
            category = "poor"
        
        return random.choice(self.encouragements[category])

# 全局评分器实例
theory_grader = TheoryQuestionGrader()

def grade_theory_answer(user_answer: str, correct_answer: str, 
                       question_content: str = "") -> Dict:
    """
    评分理论题答案的便捷函数
    
    Returns:
        包含评分结果的字典
    """
    result = theory_grader.grade_theory_question(
        user_answer, correct_answer, question_content
    )
    
    return {
        'score': result.score,
        'is_correct': result.is_correct,
        'partial_score': result.score,  # 部分分数
        'feedback': result.feedback,
        'correct_keywords': result.correct_keywords,
        'missing_keywords': result.missing_keywords,
        'incorrect_parts': result.incorrect_parts,
        'encouragement': result.encouragement,
        'detailed_analysis': {
            'keyword_match_rate': len(result.correct_keywords) / (len(result.correct_keywords) + len(result.missing_keywords)) if (result.correct_keywords or result.missing_keywords) else 0,
            'total_keywords': len(result.correct_keywords) + len(result.missing_keywords),
            'matched_keywords_count': len(result.correct_keywords),
            'missing_keywords_count': len(result.missing_keywords)
        }
    }


def grade_fill_blank_answer(user_answer: str, correct_answer: str) -> Dict:
    """
    评分填空题答案
    
    填空题需要精确匹配，支持：
    - 多个答案用逗号、分号或空格分隔
    - 忽略大小写
    - 忽略前后空格
    - 同义词匹配（部分情况）
    
    Args:
        user_answer: 用户答案
        correct_answer: 标准答案
        
    Returns:
        包含评分结果的字典
    """
    if not user_answer or not user_answer.strip():
        return {
            'score': 0.0,
            'is_correct': False,
            'feedback': '请填写答案。',
            'encouragement': '填空题需要准确的答案，仔细思考一下！',
            'correct_keywords': [],
            'missing_keywords': [correct_answer],
            'incorrect_parts': [],
            'detailed_analysis': {'match_details': '答案为空'}
        }
    
    # 标准化答案 - 处理多种分隔符
    def normalize_answer(answer):
        # 替换各种分隔符为逗号
        answer = re.sub(r'[;；、\s]+', ',', answer.strip())
        # 分割并清理每部分
        parts = [part.strip().lower() for part in answer.split(',') if part.strip()]
        return parts
    
    user_parts = normalize_answer(user_answer)
    correct_parts = normalize_answer(correct_answer)
    
    print(f"填空题评分 - 用户答案: {user_parts}, 标准答案: {correct_parts}")
    
    # 精确匹配
    if user_parts == correct_parts:
        return {
            'score': 1.0,
            'is_correct': True,
            'feedback': '完全正确！答案完美匹配。',
            'encouragement': '太棒了！你的答案完全正确！',
            'correct_keywords': user_parts,
            'missing_keywords': [],
            'incorrect_parts': [],
            'detailed_analysis': {'match_details': '完全匹配'}
        }
    
    # 部分匹配计算
    if len(correct_parts) == 0:
        return {
            'score': 0.0,
            'is_correct': False,
            'feedback': '标准答案格式错误。',
            'encouragement': '请联系老师检查题目。',
            'correct_keywords': [],
            'missing_keywords': [],
            'incorrect_parts': user_parts,
            'detailed_analysis': {'match_details': '标准答案为空'}
        }
    
    # 计算匹配度
    matched_count = 0
    matched_parts = []
    missing_parts = []
    incorrect_parts = []
    
    # 检查每个标准答案部分
    for correct_part in correct_parts:
        if correct_part in user_parts:
            matched_count += 1
            matched_parts.append(correct_part)
        else:
            missing_parts.append(correct_part)
    
    # 检查用户多余的答案
    for user_part in user_parts:
        if user_part not in correct_parts:
            incorrect_parts.append(user_part)
    
    # 计算得分 - 基于匹配的比例，但有错误答案会扣分
    base_score = matched_count / len(correct_parts)
    # 错误答案扣分（每个错误答案扣除10%）
    penalty = len(incorrect_parts) * 0.1
    final_score = max(0.0, base_score - penalty)
    
    # 判断是否正确（90%以上且无错误答案）
    is_correct = final_score >= 0.9 and len(incorrect_parts) == 0 and len(missing_parts) == 0
    
    # 生成反馈
    if final_score >= 0.8:
        feedback = f"很接近正确答案！匹配了 {matched_count}/{len(correct_parts)} 个答案。"
    elif final_score >= 0.5:
        feedback = f"部分正确，匹配了 {matched_count}/{len(correct_parts)} 个答案。"
    else:
        feedback = f"答案需要改进，仅匹配了 {matched_count}/{len(correct_parts)} 个答案。"
    
    if missing_parts:
        feedback += f" 遗漏：{', '.join(missing_parts)}。"
    if incorrect_parts:
        feedback += f" 多余或错误：{', '.join(incorrect_parts)}。"
    
    # 鼓励性评语
    if final_score >= 0.8:
        encouragement = "很棒！继续保持这样的准确性！"
    elif final_score >= 0.5:
        encouragement = "不错的尝试！再仔细检查一下答案的完整性。"
    else:
        encouragement = "没关系，填空题需要精确记忆，多练习几遍就会熟悉了！"
    
    return {
        'score': final_score,
        'is_correct': is_correct,
        'feedback': feedback,
        'encouragement': encouragement,
        'correct_keywords': matched_parts,
        'missing_keywords': missing_parts,
        'incorrect_parts': incorrect_parts,
        'detailed_analysis': {
            'match_details': f'匹配 {matched_count}/{len(correct_parts)}，错误 {len(incorrect_parts)} 个',
            'user_parts': user_parts,
            'correct_parts': correct_parts
        }
    }