"""
AI面试官服务模块
集成语音转文字、大语言模型API，实现智能面试官功能
"""

import openai
import requests
import json
import base64
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIInterviewerService:
    """AI面试官服务类"""
    
    def __init__(self):
        """初始化AI面试官服务"""
        # 多种大模型API配置
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
        # 通义千问API配置
        self.qwen_api_key = os.getenv('QWEN_API_KEY', '')
        self.qwen_api_url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        
        # 百度文心一言API配置
        self.baidu_api_key = os.getenv('BAIDU_API_KEY', '')
        self.baidu_secret_key = os.getenv('BAIDU_SECRET_KEY', '')
        self.baidu_app_id = os.getenv('BAIDU_APP_ID', '')
        
        # 智谱AI配置
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY', '')
        
        # 确定使用哪个模型
        self.selected_model = self._select_available_model()
        
        # 面试官角色设定
        self.interviewer_persona = {
            'role': 'system',
            'content': '''你是一位来自阿里巴巴/腾讯/字节跳动的资深技术面试官，姓名叫张总监。你有15年的技术和管理经验，面试过上千名候选人。你的特点：

**性格特征**：
- 🎯 犀利直接：一针见血，不绕弯子
- 😏 适度幽默：会用幽默缓解紧张，但不失专业
- 🔍 眼光毒辣：能快速识破候选人的真实水平
- 💡 实用主义：关注实际工作能力，不只是理论知识

**面试风格**：
- 对优秀回答：「不错，看来你确实有两把刷子。那我问个更深入的...」
- 对一般回答：「嗯，基础还行，但在我们公司这个水平可能还不够。你能说说...」
- 对错误回答：「哎，这个理解有问题啊。在阿里我们经常遇到这种情况，正确的做法是...」
- 对答非所问：「等等，你这是在回避我的问题吧？我问的是A，你答的是B。再来一次？」
- 对开玩笑：「哈哈，幽默感不错，但面试还是严肃点。刚才那个问题你再认真回答一下。」

**公司场景问题**（会随机提出）：
1. **阿里场景**：「假设你在淘宝工作，双11当天系统QPS突然飙升10倍，你会怎么处理？」
2. **腾讯场景**：「微信有10亿用户，如果让你设计朋友圈的推荐算法，你会考虑哪些因素？」
3. **字节场景**：「抖音的推荐系统每天要处理几亿个视频，如何保证推荐的实时性和准确性？」
4. **产品理解**：「你觉得我们公司的核心产品有什么可以改进的地方？给个具体建议。」
5. **技术挑战**：「在你看来，我们公司面临的最大技术挑战是什么？你会怎么解决？」

**评价标准**：
- 技术深度（40%）：不只要知道是什么，更要知道为什么
- 实际经验（30%）：有没有真正做过项目，踩过坑
- 思维逻辑（20%）：分析问题的思路是否清晰
- 学习能力（10%）：遇到不会的问题，学习态度如何

**回应格式**（必须严格遵循JSON格式）：
{
    "evaluation": "优秀/良好/一般/需要改进",
    "feedback": "犀利而幽默的具体反馈，体现面试官个性",
    "follow_up": "追问问题或下一个问题（可选）",
    "suggestions": "实用的改进建议（可选）",
    "tone": "鼓励/中性/严肃/幽默",
    "company_scenario": "如果合适，提出公司场景问题（可选）"
}

记住：你是张总监，要体现出资深面试官的犀利和幽默，让候选人感受到真实的大厂面试氛围！'''
        }
    
    def _select_available_model(self):
        """选择可用的大模型"""
        if self.qwen_api_key:
            logger.info("使用通义千问模型")
            return 'qwen'
        elif self.baidu_api_key and self.baidu_secret_key:
            logger.info("使用百度文心一言模型")
            return 'baidu'
        elif self.zhipu_api_key:
            logger.info("使用智谱AI模型")
            return 'zhipu'
        elif self.openai_api_key:
            logger.info("使用OpenAI模型")
            return 'openai'
        else:
            logger.info("没有配置API密钥，使用本地模拟模型")
            return 'mock'
    
    def speech_to_text_web_api(self, audio_blob_url: str) -> str:
        """
        使用Web Speech API进行语音转文字（前端实现）
        这里提供后端接口支持
        """
        # 这个方法主要是为了提供接口，实际转换在前端完成
        return ""
    
    def speech_to_text_baidu(self, audio_data: bytes, audio_format: str = 'wav') -> str:
        """
        使用百度语音识别API进行语音转文字
        """
        if not all([self.baidu_app_id, self.baidu_api_key, self.baidu_secret_key]):
            logger.warning("百度语音识别API配置不完整")
            return ""
        
        try:
            # 获取access_token
            token_url = "https://aip.baidubce.com/oauth/2.0/token"
            token_params = {
                'grant_type': 'client_credentials',
                'client_id': self.baidu_api_key,
                'client_secret': self.baidu_secret_key
            }
            
            token_response = requests.post(token_url, params=token_params)
            access_token = token_response.json().get('access_token')
            
            if not access_token:
                logger.error("获取百度API access_token失败")
                return ""
            
            # 语音识别请求
            asr_url = f"https://vop.baidu.com/server_api?access_token={access_token}"
            
            # 音频数据base64编码
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            asr_data = {
                'format': audio_format,
                'rate': 16000,
                'channel': 1,
                'cuid': 'python_client',
                'token': access_token,
                'speech': audio_base64,
                'len': len(audio_data)
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(asr_url, data=json.dumps(asr_data), headers=headers)
            result = response.json()
            
            if result.get('err_no') == 0:
                return result.get('result', [''])[0]
            else:
                logger.error(f"百度语音识别错误: {result.get('err_msg')}")
                return ""
                
        except Exception as e:
            logger.error(f"百度语音识别异常: {str(e)}")
            return ""
    
    def get_ai_response(self, question: str, user_answer: str, context: List[Dict] = None) -> Dict:
        """
        使用大语言模型获取AI面试官回应
        
        Args:
            question: 面试问题
            user_answer: 用户回答
            context: 对话上下文
            
        Returns:
            AI面试官的回应
        """
        try:
            # 构建提示词
            current_prompt = f"""
面试问题：{question}

候选人回答：{user_answer}

请作为张总监（资深技术面试官）对这个回答进行评价和反馈。要求：
1. 犀利直接，一针见血
2. 适度幽默，但不失专业
3. 根据回答质量决定是否追问
4. 可以提出公司场景问题

请严格按照JSON格式返回：
{{
    "evaluation": "优秀/良好/一般/需要改进",
    "feedback": "犀利而幽默的具体反馈",
    "follow_up": "追问问题（可选）",
    "suggestions": "改进建议（可选）",
    "tone": "鼓励/中性/严肃/幽默",
    "company_scenario": "公司场景问题（可选）"
}}
"""
            
            # 根据选择的模型调用相应API
            if self.selected_model == 'qwen':
                return self._call_qwen_api(current_prompt)
            elif self.selected_model == 'baidu':
                return self._call_baidu_api(current_prompt)
            elif self.selected_model == 'zhipu':
                return self._call_zhipu_api(current_prompt)
            elif self.selected_model == 'openai':
                return self._call_openai_api(current_prompt, context)
            else:
                return self._get_mock_response(question, user_answer)
                
        except Exception as e:
            logger.error(f"AI面试官回应生成失败: {str(e)}")
            return self._get_mock_response(question, user_answer)
    
    def _call_qwen_api(self, prompt: str) -> Dict:
        """调用通义千问API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.qwen_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 800
                }
            }
            
            response = requests.post(self.qwen_api_url, headers=headers, json=data)
            result = response.json()
            
            if response.status_code == 200 and 'output' in result:
                ai_response = result['output']['text']
                return self._parse_json_response(ai_response)
            else:
                logger.error(f"通义千问API调用失败: {result}")
                return self._get_mock_response("", "")
                
        except Exception as e:
            logger.error(f"通义千问API异常: {str(e)}")
            return self._get_mock_response("", "")
    
    def _call_baidu_api(self, prompt: str) -> Dict:
        """调用百度文心一言API"""
        try:
            # 获取access_token
            token_url = "https://aip.baidubce.com/oauth/2.0/token"
            token_params = {
                'grant_type': 'client_credentials',
                'client_id': self.baidu_api_key,
                'client_secret': self.baidu_secret_key
            }
            
            token_response = requests.post(token_url, params=token_params)
            access_token = token_response.json().get('access_token')
            
            if not access_token:
                logger.error("获取百度API access_token失败")
                return self._get_mock_response("", "")
            
            # 调用文心一言API
            api_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
            
            headers = {'Content-Type': 'application/json'}
            data = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_output_tokens": 800
            }
            
            response = requests.post(api_url, headers=headers, json=data)
            result = response.json()
            
            if response.status_code == 200 and 'result' in result:
                ai_response = result['result']
                return self._parse_json_response(ai_response)
            else:
                logger.error(f"百度文心一言API调用失败: {result}")
                return self._get_mock_response("", "")
                
        except Exception as e:
            logger.error(f"百度文心一言API异常: {str(e)}")
            return self._get_mock_response("", "")
    
    def _call_zhipu_api(self, prompt: str) -> Dict:
        """调用智谱AI API"""
        try:
            import jwt
            import time
            
            # 生成JWT token
            def generate_token(apikey: str, exp_seconds: int = 3600):
                try:
                    id, secret = apikey.split(".")
                except Exception:
                    raise Exception("invalid apikey")
                
                payload = {
                    "iss": id,
                    "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
                    "timestamp": int(round(time.time() * 1000)),
                }
                
                return jwt.encode(payload, secret, algorithm="HS256", headers={"alg": "HS256", "sign_type": "SIGN"})
            
            token = generate_token(self.zhipu_api_key)
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "glm-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            response = requests.post("https://open.bigmodel.cn/api/paas/v4/chat/completions", headers=headers, json=data)
            result = response.json()
            
            if response.status_code == 200 and 'choices' in result:
                ai_response = result['choices'][0]['message']['content']
                return self._parse_json_response(ai_response)
            else:
                logger.error(f"智谱AI API调用失败: {result}")
                return self._get_mock_response("", "")
                
        except Exception as e:
            logger.error(f"智谱AI API异常: {str(e)}")
            return self._get_mock_response("", "")
    
    def _call_openai_api(self, prompt: str, context: List[Dict] = None) -> Dict:
        """调用OpenAI API"""
        try:
            messages = [self.interviewer_persona]
            if context:
                messages.extend(context)
            messages.append({'role': 'user', 'content': prompt})
            
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                base_url=self.openai_base_url
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_json_response(ai_response)
            
        except Exception as e:
            logger.error(f"OpenAI API异常: {str(e)}")
            return self._get_mock_response("", "")
    
    def _parse_json_response(self, ai_response: str) -> Dict:
        """解析AI模型返回的JSON响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(ai_response)
        except json.JSONDecodeError:
            # 如果不是标准JSON，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # 如果还是失败，包装成标准格式
            return {
                'evaluation': '一般',
                'feedback': ai_response,
                'follow_up': '',
                'suggestions': '',
                'tone': '中性'
            }
    
    def _get_mock_response(self, question: str, user_answer: str) -> Dict:
        """
        生成模拟的AI面试官回应（当API不可用时使用）
        张总监的犀利风格模拟版本
        """
        import random
        
        answer_lower = user_answer.lower()
        
        # 公司场景问题库
        company_scenarios = [
            "假设你在阿里工作，双11当天系统突然崩了，你第一时间会做什么？",
            "如果让你优化微信朋友圈的加载速度，你会从哪几个方面入手？",
            "抖音每天新增几千万个视频，如何保证推荐算法不会推重复内容？",
            "你觉得淘宝的搜索结果排序有什么问题？给个改进方案。",
            "假设你是腾讯云的架构师，如何设计一个能承载春晚红包的系统？"
        ]
        
        if not user_answer.strip():
            responses = [
                "张总监皱了皱眉：小伙子，这是面试不是冥想，说点什么吧？",
                "哦豁，这是准备用沉默来征服我吗？我们阿里不需要哑巴工程师哦。",
                "emmm...你这是在思考人生吗？我问的是技术问题，不是哲学问题。"
            ]
            return {
                'evaluation': '需要改进',
                'feedback': random.choice(responses),
                'follow_up': '来来来，随便说点什么，哪怕是错的也比不说强。',
                'suggestions': '面试官最怕的就是候选人不说话，有想法就大胆说出来。',
                'tone': '幽默'
            }
        
        if any(word in answer_lower for word in ['不知道', '不会', '没有经验', '没做过']):
            responses = [
                "诚实是好事，但'不知道'可不是万能答案。在我们公司，遇到不会的问题要学会分析。",
                "嗯，至少你诚实。但在字节跳动，我们更喜欢'虽然没做过，但我觉得可以这样...'的态度。",
                "哈哈，如果什么都会那还要培训干嘛？说说你的思路，错了也没关系。"
            ]
            return {
                'evaluation': '需要改进',
                'feedback': random.choice(responses),
                'follow_up': random.choice(company_scenarios),
                'suggestions': '遇到不会的问题，可以说说你会怎么去学习和解决。',
                'tone': '鼓励'
            }
        
        if any(word in answer_lower for word in ['哈哈', '开玩笑', '搞笑', '呵呵']):
            responses = [
                "哈哈，幽默感不错！但咱们还是聊聊技术吧，我可是技术出身的。",
                "段子手啊？我们公司确实需要活跃气氛的人，但技术也得过关才行。",
                "笑容很灿烂，那技术水平是不是也这么亮眼呢？"
            ]
            return {
                'evaluation': '一般',
                'feedback': random.choice(responses),
                'follow_up': '来个正经回答，让我看看你的真本事。',
                'suggestions': '适度幽默可以，但要把握好度，面试官更关注你的专业能力。',
                'tone': '幽默'
            }
        
        if len(user_answer) < 20:
            responses = [
                "这回答有点简单啊，在阿里我们喜欢有深度的思考。能详细说说吗？",
                "emmm...这个回答让我想起了小学生的作文，能再丰富一点吗？",
                "看来你是个惜字如金的人，但面试时还是多说点比较好。"
            ]
            return {
                'evaluation': '一般',
                'feedback': random.choice(responses),
                'follow_up': '能举个具体的例子吗？或者说说你的实际经验？',
                'suggestions': '回答问题时，尽量结合具体例子，这样更有说服力。',
                'tone': '中性'
            }
        
        if any(word in answer_lower for word in ['项目', '经验', '实际', '遇到过']):
            responses = [
                "不错，看来你确实有实战经验。那我问个更深入的问题...",
                "嗯，有项目经验是好事。但在我们公司，光有经验还不够，还要有深度思考。",
                "项目经验很重要，但我更想知道你从中学到了什么。"
            ]
            return {
                'evaluation': '良好',
                'feedback': random.choice(responses),
                'follow_up': random.choice(company_scenarios),
                'suggestions': '继续保持，结合实际项目经验回答问题是很好的习惯。',
                'tone': '鼓励'
            }
        
        # 默认回应 - 更加犀利
        responses = [
            "回答还算中规中矩，但在大厂面试中，中规中矩往往意味着平庸。",
            "基础理论掌握得不错，但我更想听听你的独特见解。",
            "嗯，教科书式的回答。那实际工作中你会怎么处理呢？"
        ]
        
        return {
            'evaluation': '一般',
            'feedback': random.choice(responses),
            'follow_up': random.choice(company_scenarios),
            'suggestions': '尝试从实际应用场景的角度来思考问题，这样更有价值。',
            'tone': '中性',
            'company_scenario': random.choice(company_scenarios)
        }
    
    def analyze_interview_performance(self, qa_history: List[Dict]) -> Dict:
        """
        分析整场面试的表现
        
        Args:
            qa_history: 问答历史记录
            
        Returns:
            面试表现分析报告
        """
        if not qa_history:
            return {
                'overall_score': 0,
                'strengths': [],
                'weaknesses': ['未完成任何问答'],
                'recommendations': ['建议重新进行面试']
            }
        
        # 统计各种评价
        evaluations = [qa.get('ai_response', {}).get('evaluation', '一般') for qa in qa_history]
        
        excellent_count = evaluations.count('优秀')
        good_count = evaluations.count('良好')
        average_count = evaluations.count('一般')
        poor_count = evaluations.count('需要改进')
        
        total_questions = len(evaluations)
        
        # 计算总分
        score = (excellent_count * 4 + good_count * 3 + average_count * 2 + poor_count * 1) / total_questions
        overall_score = min(100, int(score * 25))
        
        # 分析优势和不足
        strengths = []
        weaknesses = []
        recommendations = []
        
        if excellent_count > total_questions * 0.3:
            strengths.append('技术理解深入，回答质量高')
        if good_count > total_questions * 0.4:
            strengths.append('基础知识扎实')
        if poor_count < total_questions * 0.2:
            strengths.append('整体表现稳定')
        
        if poor_count > total_questions * 0.3:
            weaknesses.append('部分问题回答不够准确')
            recommendations.append('建议加强基础知识学习')
        if average_count > total_questions * 0.5:
            weaknesses.append('回答深度有待提升')
            recommendations.append('建议多进行实践项目经验积累')
        
        if not strengths:
            strengths.append('参与了完整的面试流程')
        if not recommendations:
            recommendations.append('继续保持学习热情，多做练习')
        
        return {
            'overall_score': overall_score,
            'question_count': total_questions,
            'excellent_count': excellent_count,
            'good_count': good_count,
            'average_count': average_count,
            'poor_count': poor_count,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations
        }

# 全局AI面试官服务实例
ai_interviewer = AIInterviewerService()
