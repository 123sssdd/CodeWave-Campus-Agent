#!/usr/bin/env python3
"""
AI面试服务 - 基于通义千问API
提供智能面试官功能
"""

import openai
import json
import random
from datetime import datetime
from typing import List, Dict, Any
import os
import logging

class AIInterviewService:
    """AI面试服务类"""
    
    def __init__(self):
        # 设置API配置 - 使用通义千问兼容的OpenAI API格式
        self.api_key = os.getenv('TONGYI_API_KEY', 'your-api-key-here')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-turbo"  # 通义千问免费模型
        
        # 如果没有配置API密钥，使用本地模拟
        self.use_mock = self.api_key == 'your-api-key-here'
        
        if not self.use_mock:
            # 配置OpenAI客户端使用通义千问API
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        
        # 面试官人设
        self.interviewer_persona = {
            "name": "李老师",
            "role": "资深技术面试官",
            "personality": "专业、友善、严谨",
            "background": "10年以上软件开发和面试经验"
        }
        
        # 面试场景模板
        self.interview_scenarios = {
            "technical": "技术岗位面试",
            "general": "综合能力面试", 
            "behavioral": "行为面试",
            "project": "项目经验面试"
        }
        
        logging.info(f"AI面试服务初始化 - 模式: {'本地模拟' if self.use_mock else '通义千问API'}")
    
    def generate_opening_question(self, position: str, tech_stack: List[str] = None) -> Dict[str, Any]:
        """生成开场问题"""
        try:
            if self.use_mock:
                return self._mock_opening_question(position, tech_stack)
            
            # 构建系统提示
            tech_info = f"技术栈: {', '.join(tech_stack)}" if tech_stack else ""
            system_prompt = f"""你是{self.interviewer_persona['name']}，一位{self.interviewer_persona['background']}的{self.interviewer_persona['role']}。
你正在面试一位应聘{position}职位的候选人。{tech_info}

请生成一个开场问题，要求：
1. 语气友善、专业
2. 问题针对该职位特点
3. 能够让候选人放松并展示基本能力
4. 返回JSON格式：{{"question": "问题内容", "type": "问题类型", "tips": "回答建议"}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请为{position}职位生成一个合适的开场面试问题"}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "question": result.get("question", "请简单介绍一下自己和您的技术背景。"),
                "type": result.get("type", "自我介绍"),
                "tips": result.get("tips", "简洁明了地介绍背景，突出与职位相关的经验"),
                "interviewer": self.interviewer_persona['name']
            }
            
        except Exception as e:
            logging.error(f"生成开场问题失败: {e}")
            return self._mock_opening_question(position, tech_stack)
    
    def generate_followup_question(self, 
                                 conversation_history: List[Dict], 
                                 position: str,
                                 difficulty: str = "medium") -> Dict[str, Any]:
        """基于对话历史生成追问"""
        try:
            if self.use_mock:
                return self._mock_followup_question(conversation_history, position, difficulty)
            
            # 构建对话上下文
            conversation_text = "\n".join([
                f"{'面试官' if msg['role'] == 'interviewer' else '候选人'}: {msg['content']}"
                for msg in conversation_history[-6:]  # 只保留最近3轮对话
            ])
            
            system_prompt = f"""你是{self.interviewer_persona['name']}，正在面试{position}职位的候选人。
面试难度: {difficulty}

基于以下对话历史，生成一个合适的追问或新问题：
{conversation_text}

要求：
1. 根据候选人的回答进行有针对性的追问
2. 难度适中，既要有挑战性又不能过于困难
3. 问题应该能够深入了解候选人的能力
4. 返回JSON格式：{{"question": "问题内容", "type": "问题类型", "focus": "考察重点", "tips": "回答建议"}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请生成下一个面试问题"}
                ],
                temperature=0.8,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "question": result.get("question", "能详细说说您在项目中遇到的最大挑战是什么吗？"),
                "type": result.get("type", "项目经验"),
                "focus": result.get("focus", "问题解决能力"),
                "tips": result.get("tips", "结合具体例子说明解决过程和学到的经验"),
                "interviewer": self.interviewer_persona['name']
            }
            
        except Exception as e:
            logging.error(f"生成追问失败: {e}")
            return self._mock_followup_question(conversation_history, position, difficulty)
    
    def evaluate_answer(self, question: str, answer: str, position: str) -> Dict[str, Any]:
        """评估候选人回答"""
        try:
            if self.use_mock:
                return self._mock_evaluate_answer(question, answer, position)
            
            system_prompt = f"""你是{self.interviewer_persona['name']}，正在评估{position}职位候选人的面试回答。

面试问题：{question}
候选人回答：{answer}

请从以下维度评估回答质量（1-10分）：
1. 内容完整性
2. 技术准确性  
3. 表达清晰度
4. 逻辑性
5. 实用性

返回JSON格式：
{{
    "overall_score": 总分(1-10),
    "detailed_scores": {{
        "completeness": 完整性分数,
        "accuracy": 准确性分数,
        "clarity": 清晰度分数,
        "logic": 逻辑性分数,
        "practicality": 实用性分数
    }},
    "feedback": "具体评价",
    "suggestions": "改进建议",
    "highlights": "亮点"
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请评估这个回答"}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logging.error(f"评估回答失败: {e}")
            return self._mock_evaluate_answer(question, answer, position)
    
    def generate_interview_summary(self, conversation_history: List[Dict], position: str) -> Dict[str, Any]:
        """生成面试总结报告"""
        try:
            if self.use_mock:
                return self._mock_interview_summary(conversation_history, position)
            
            # 整理对话历史
            conversation_text = "\n".join([
                f"Q: {msg['content']}" if msg['role'] == 'interviewer' else f"A: {msg['content']}"
                for msg in conversation_history
            ])
            
            system_prompt = f"""你是{self.interviewer_persona['name']}，请为这次{position}职位的面试生成总结报告。

面试完整记录：
{conversation_text}

请生成综合评估报告，包括：
1. 总体表现评分 (1-10)
2. 各项能力评估
3. 优势与亮点
4. 需要改进的地方
5. 录用建议

返回JSON格式：
{{
    "overall_rating": 总评分,
    "skill_assessment": {{
        "technical_skills": 技术能力分数,
        "communication": 沟通能力分数,
        "problem_solving": 解决问题能力分数,
        "experience": 经验匹配度分数
    }},
    "strengths": ["优势1", "优势2"],
    "areas_for_improvement": ["改进点1", "改进点2"],
    "recommendation": "录用建议",
    "detailed_feedback": "详细反馈"
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "请生成面试总结报告"}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logging.error(f"生成面试总结失败: {e}")
            return self._mock_interview_summary(conversation_history, position)
    
    # ===== 本地模拟方法 =====
    
    def _mock_opening_question(self, position: str, tech_stack: List[str] = None) -> Dict[str, Any]:
        """本地模拟开场问题"""
        questions = {
            "前端工程师": "请简单介绍一下自己，以及您在前端开发方面的经验和擅长的技术栈。",
            "后端工程师": "能否介绍一下您的技术背景，特别是在后端开发和数据库设计方面的经验？",
            "全栈工程师": "请介绍一下您的全栈开发经验，以及您认为全栈开发最重要的能力是什么？",
            "算法工程师": "请分享一下您在算法和数据结构方面的学习经历和项目经验。"
        }
        
        question = questions.get(position, "请简单介绍一下自己和您的技术背景。")
        tech_info = f" 我看到您熟悉{', '.join(tech_stack[:2])}等技术" if tech_stack else ""
        
        return {
            "question": question + tech_info + "，请详细说说。",
            "type": "自我介绍",
            "tips": "简洁明了地介绍背景，突出与职位相关的经验",
            "interviewer": self.interviewer_persona['name']
        }
    
    def _mock_followup_question(self, conversation_history: List[Dict], position: str, difficulty: str) -> Dict[str, Any]:
        """本地模拟追问"""
        questions_by_difficulty = {
            "easy": [
                "能详细说说您最近做过的一个项目吗？",
                "您在团队协作中通常扮演什么角色？",
                "遇到技术难题时，您通常如何解决？"
            ],
            "medium": [
                "在您的项目中，您是如何保证代码质量的？",
                "能说说您对性能优化的理解和实践吗？",
                "如果要设计一个高并发系统，您会考虑哪些因素？"
            ],
            "hard": [
                "请设计一个分布式系统来处理每秒10万次请求。",
                "如何在微服务架构中处理数据一致性问题？",
                "能详细解释一下您对系统架构设计的理解吗？"
            ]
        }
        
        questions = questions_by_difficulty.get(difficulty, questions_by_difficulty["medium"])
        question = random.choice(questions)
        
        return {
            "question": question,
            "type": "技术深入",
            "focus": "技术能力",
            "tips": "结合具体例子详细说明，展示您的思考过程",
            "interviewer": self.interviewer_persona['name']
        }
    
    def _mock_evaluate_answer(self, question: str, answer: str, position: str) -> Dict[str, Any]:
        """本地模拟回答评估"""
        # 简单的评分逻辑
        answer_length = len(answer)
        base_score = min(8, max(4, answer_length // 50))  # 基于回答长度的基础分
        
        # 关键词加分
        keywords = ["项目", "经验", "技术", "团队", "挑战", "解决", "学习", "优化"]
        keyword_bonus = sum(1 for keyword in keywords if keyword in answer) * 0.2
        
        overall_score = min(10, base_score + keyword_bonus)
        
        return {
            "overall_score": round(overall_score, 1),
            "detailed_scores": {
                "completeness": round(min(10, overall_score + 0.5), 1),
                "accuracy": round(overall_score, 1),
                "clarity": round(max(6, overall_score - 0.5), 1),
                "logic": round(overall_score, 1),
                "practicality": round(min(9, overall_score + 0.3), 1)
            },
            "feedback": "回答比较全面，展现了一定的技术理解和实践经验。",
            "suggestions": "可以加入更多具体的技术细节和解决方案。",
            "highlights": "逻辑清晰，表达流畅"
        }
    
    def _mock_interview_summary(self, conversation_history: List[Dict], position: str) -> Dict[str, Any]:
        """本地模拟面试总结"""
        return {
            "overall_rating": 7.5,
            "skill_assessment": {
                "technical_skills": 7.8,
                "communication": 8.0,
                "problem_solving": 7.2,
                "experience": 7.5
            },
            "strengths": ["技术基础扎实", "沟通能力较强", "学习能力好"],
            "areas_for_improvement": ["项目经验可以更丰富", "系统设计能力有待提升"],
            "recommendation": "建议录用，具有良好的发展潜力",
            "detailed_feedback": "候选人整体表现良好，技术基础扎实，沟通清晰。在实际项目经验和系统设计方面还有提升空间，但学习能力强，值得培养。"
        }

# 全局服务实例
interview_service = AIInterviewService()
