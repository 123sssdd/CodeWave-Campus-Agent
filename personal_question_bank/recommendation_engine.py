import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple
from collections import defaultdict

from models import db, User, Question, LearningRecord, KnowledgePoint, UserKnowledgeStats

class RecommendationEngine:
    """个性化推荐引擎"""
    
    def __init__(self):
        self.user_profiles = {}
        self.question_features = {}
        self.difficulty_weights = {'easy': 1, 'medium': 2, 'hard': 3}
        self.type_weights = {'theory': 1, 'multiple_choice': 1, 'practical': 2, 'coding': 3}
    
    def recommend_questions(self, user_id: int, count: int = 10) -> List[Question]:
        """为用户推荐个性化题目"""
        
        # 1. 构建用户画像
        user_profile = self._build_user_profile(user_id)
        
        # 2. 获取候选题目
        candidate_questions = self._get_candidate_questions(user_id, user_profile)
        
        # 3. 计算推荐分数
        scored_questions = self._score_questions(user_profile, candidate_questions)
        
        # 4. 多样性调整
        final_questions = self._diversify_recommendations(scored_questions, count)
        
        return final_questions
    
    def _build_user_profile(self, user_id: int) -> Dict:
        """构建用户画像"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"用户 {user_id} 不存在")
        
        # 基础偏好
        profile = {
            'user_id': user_id,
            'preferred_difficulty': user.preferred_difficulty,
            'preferred_types': json.loads(user.preferred_question_types) if user.preferred_question_types else [],
            'preferred_interaction': user.preferred_interaction_type
        }
        
        # 学习历史分析
        recent_records = LearningRecord.query.filter_by(user_id=user_id)\
                                           .filter(LearningRecord.completed_at >= datetime.utcnow() - timedelta(days=30))\
                                           .all()
        
        if recent_records:
            # 计算各知识点掌握情况
            kp_stats = defaultdict(lambda: {'total': 0, 'correct': 0, 'avg_time': 0})
            
            for record in recent_records:
                kp_id = record.question.knowledge_point_id
                kp_stats[kp_id]['total'] += 1
                if record.is_correct:
                    kp_stats[kp_id]['correct'] += 1
                kp_stats[kp_id]['avg_time'] += record.time_spent
            
            # 计算掌握程度和学习模式
            weak_knowledge_points = []
            strong_knowledge_points = []
            
            for kp_id, stats in kp_stats.items():
                accuracy = stats['correct'] / stats['total']
                avg_time = stats['avg_time'] / stats['total']
                
                if accuracy < 0.6:  # 掌握度较低
                    weak_knowledge_points.append(kp_id)
                elif accuracy > 0.8:  # 掌握度较高
                    strong_knowledge_points.append(kp_id)
            
            profile.update({
                'weak_knowledge_points': weak_knowledge_points,
                'strong_knowledge_points': strong_knowledge_points,
                'recent_activity': len(recent_records),
                'avg_accuracy': sum(r.is_correct for r in recent_records) / len(recent_records),
                'avg_time_per_question': sum(r.time_spent for r in recent_records) / len(recent_records)
            })
        else:
            # 新用户，基于偏好推荐
            profile.update({
                'weak_knowledge_points': [],
                'strong_knowledge_points': [],
                'recent_activity': 0,
                'avg_accuracy': 0.5,  # 假设中等水平
                'avg_time_per_question': 300  # 5分钟
            })
        
        # 学习节奏分析
        profile['learning_pattern'] = self._analyze_learning_pattern(user_id)
        
        return profile
    
    def _analyze_learning_pattern(self, user_id: int) -> Dict:
        """分析用户学习模式"""
        records = LearningRecord.query.filter_by(user_id=user_id)\
                                    .order_by(LearningRecord.completed_at.desc())\
                                    .limit(50).all()
        
        if not records:
            return {'type': 'new_learner', 'intensity': 'medium'}
        
        # 分析学习频率
        dates = [r.completed_at.date() for r in records]
        unique_dates = set(dates)
        days_span = (max(dates) - min(dates)).days + 1
        
        # 分析学习强度
        daily_counts = defaultdict(int)
        for date in dates:
            daily_counts[date] += 1
        
        avg_questions_per_day = len(records) / days_span
        
        # 分析偏好题型
        type_counts = defaultdict(int)
        for record in records:
            type_counts[record.question.question_type] += 1
        
        most_preferred_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else 'theory'
        
        return {
            'type': self._classify_learner_type(avg_questions_per_day, len(unique_dates), days_span),
            'intensity': self._classify_intensity(avg_questions_per_day),
            'preferred_type': most_preferred_type,
            'consistency': len(unique_dates) / days_span  # 学习的连续性
        }
    
    def _classify_learner_type(self, avg_per_day: float, active_days: int, total_days: int) -> str:
        """分类学习者类型"""
        consistency = active_days / total_days
        
        if avg_per_day >= 5 and consistency >= 0.7:
            return 'intensive_learner'
        elif avg_per_day >= 2 and consistency >= 0.5:
            return 'regular_learner'
        elif consistency >= 0.3:
            return 'casual_learner'
        else:
            return 'sporadic_learner'
    
    def _classify_intensity(self, avg_per_day: float) -> str:
        """分类学习强度"""
        if avg_per_day >= 10:
            return 'high'
        elif avg_per_day >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _get_candidate_questions(self, user_id: int, user_profile: Dict) -> List[Question]:
        """获取候选题目"""
        # 排除已经做过的题目（最近做过的）
        recent_question_ids = db.session.query(LearningRecord.question_id)\
                                      .filter_by(user_id=user_id)\
                                      .filter(LearningRecord.completed_at >= datetime.utcnow() - timedelta(days=7))\
                                      .subquery()
        
        query = Question.query.filter(~Question.id.in_(recent_question_ids))
        
        # 基于用户偏好过滤
        preferred_types = user_profile.get('preferred_types', [])
        if preferred_types:
            query = query.filter(Question.question_type.in_(preferred_types))
        
        candidates = query.all()
        
        # 如果候选题目太少，放宽限制
        if len(candidates) < 20:
            candidates = Question.query.filter(~Question.id.in_(recent_question_ids)).all()
        
        return candidates
    
    def _score_questions(self, user_profile: Dict, questions: List[Question]) -> List[Tuple[Question, float]]:
        """为题目打分"""
        scored_questions = []
        
        for question in questions:
            score = self._calculate_question_score(user_profile, question)
            scored_questions.append((question, score))
        
        # 按分数排序
        scored_questions.sort(key=lambda x: x[1], reverse=True)
        return scored_questions
    
    def _calculate_question_score(self, user_profile: Dict, question: Question) -> float:
        """计算单个题目的推荐分数"""
        score = 0.0
        
        # 1. 难度匹配度 (权重: 30%)
        difficulty_score = self._calculate_difficulty_score(user_profile, question)
        score += difficulty_score * 0.3
        
        # 2. 题型偏好度 (权重: 25%)
        type_score = self._calculate_type_score(user_profile, question)
        score += type_score * 0.25
        
        # 3. 知识点需求度 (权重: 35%)
        knowledge_score = self._calculate_knowledge_score(user_profile, question)
        score += knowledge_score * 0.35
        
        # 4. 时间匹配度 (权重: 10%)
        time_score = self._calculate_time_score(user_profile, question)
        score += time_score * 0.1
        
        return score
    
    def _calculate_difficulty_score(self, user_profile: Dict, question: Question) -> float:
        """计算难度匹配分数"""
        user_difficulty = user_profile['preferred_difficulty']
        question_difficulty = question.difficulty
        user_accuracy = user_profile.get('avg_accuracy', 0.5)
        
        # 基础匹配分数
        if user_difficulty == question_difficulty:
            base_score = 1.0
        elif (user_difficulty == 'easy' and question_difficulty == 'medium') or \
             (user_difficulty == 'medium' and question_difficulty == 'easy') or \
             (user_difficulty == 'medium' and question_difficulty == 'hard') or \
             (user_difficulty == 'hard' and question_difficulty == 'medium'):
            base_score = 0.7
        else:
            base_score = 0.3
        
        # 根据用户表现调整
        if user_accuracy > 0.8:  # 表现很好，可以提高难度
            if question_difficulty == 'hard':
                base_score += 0.2
            elif question_difficulty == 'medium':
                base_score += 0.1
        elif user_accuracy < 0.5:  # 表现较差，降低难度
            if question_difficulty == 'easy':
                base_score += 0.2
            elif question_difficulty == 'medium':
                base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _calculate_type_score(self, user_profile: Dict, question: Question) -> float:
        """计算题型偏好分数"""
        preferred_types = user_profile.get('preferred_types', [])
        learning_pattern = user_profile.get('learning_pattern', {})
        
        if not preferred_types:
            return 0.5  # 中性分数
        
        if question.question_type in preferred_types:
            base_score = 1.0
        else:
            base_score = 0.3
        
        # 根据学习模式调整
        pattern_preferred_type = learning_pattern.get('preferred_type', '')
        if pattern_preferred_type == question.question_type:
            base_score += 0.2
        
        # 实践类题目优先级提升
        if question.question_type in ['coding', 'practical']:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _calculate_knowledge_score(self, user_profile: Dict, question: Question) -> float:
        """计算知识点需求分数"""
        weak_kps = user_profile.get('weak_knowledge_points', [])
        strong_kps = user_profile.get('strong_knowledge_points', [])
        
        question_kp = question.knowledge_point_id
        
        # 优先推荐薄弱知识点
        if question_kp in weak_kps:
            return 1.0
        
        # 避免过多重复强项知识点
        if question_kp in strong_kps:
            return 0.3
        
        # 新知识点给中等分数
        return 0.6
    
    def _calculate_time_score(self, user_profile: Dict, question: Question) -> float:
        """计算时间匹配分数"""
        user_avg_time = user_profile.get('avg_time_per_question', 300)
        question_estimated_time = (question.estimated_time or 10) * 60  # 转换为秒
        
        # 计算时间比例
        time_ratio = question_estimated_time / user_avg_time
        
        # 最佳匹配是在用户平均时间的0.5-1.5倍之间
        if 0.5 <= time_ratio <= 1.5:
            return 1.0
        elif 0.3 <= time_ratio < 0.5 or 1.5 < time_ratio <= 2.0:
            return 0.7
        else:
            return 0.3
    
    def _diversify_recommendations(self, scored_questions: List[Tuple[Question, float]], count: int) -> List[Question]:
        """多样化推荐结果"""
        if len(scored_questions) <= count:
            return [q for q, _ in scored_questions]
        
        selected_questions = []
        used_knowledge_points = set()
        used_types = set()
        
        # 第一轮：选择高分且多样化的题目
        for question, score in scored_questions:
            if len(selected_questions) >= count:
                break
                
            kp_id = question.knowledge_point_id
            q_type = question.question_type
            
            # 多样性检查
            kp_diversity = kp_id not in used_knowledge_points
            type_diversity = len([q for q in selected_questions if q.question_type == q_type]) < count // 3
            
            if kp_diversity or type_diversity or len(selected_questions) < count // 2:
                selected_questions.append(question)
                used_knowledge_points.add(kp_id)
                used_types.add(q_type)
        
        # 第二轮：如果还没够数，按分数补充
        if len(selected_questions) < count:
            remaining_count = count - len(selected_questions)
            selected_ids = {q.id for q in selected_questions}
            
            for question, score in scored_questions:
                if question.id not in selected_ids:
                    selected_questions.append(question)
                    remaining_count -= 1
                    if remaining_count == 0:
                        break
        
        return selected_questions[:count]
    
    def update_user_model(self, user_id: int, question_id: int, is_correct: bool, time_spent: int):
        """更新用户模型（实时学习）"""
        # 这里可以实现在线学习算法，根据用户的实时反馈调整推荐模型
        # 例如：更新用户偏好权重、调整难度预测等
        pass
    
    def get_learning_path(self, user_id: int) -> List[Dict]:
        """生成学习路径推荐"""
        user_profile = self._build_user_profile(user_id)
        weak_kps = user_profile.get('weak_knowledge_points', [])
        
        if not weak_kps:
            return []
        
        # 为每个薄弱知识点推荐学习路径
        learning_path = []
        
        for kp_id in weak_kps[:3]:  # 最多3个薄弱知识点
            kp = KnowledgePoint.query.get(kp_id)
            if not kp:
                continue
                
            # 获取该知识点的题目，按难度排序
            kp_questions = Question.query.filter_by(knowledge_point_id=kp_id)\
                                       .order_by(Question.difficulty).all()
            
            path_item = {
                'knowledge_point': kp.to_dict(),
                'recommended_sequence': [q.to_dict() for q in kp_questions[:5]],  # 推荐5道题
                'estimated_time': sum(q.estimated_time or 10 for q in kp_questions[:5]),
                'priority': 'high' if kp_id in weak_kps else 'medium'
            }
            
            learning_path.append(path_item)
        
        return learning_path