# encoding:UTF-8
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 星火API配置
api_key = "Bearer IZCYjZldtFfctRDljtZJ:yGDOYHzOXQRmoKXQIRAw"
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

# 全局变量存储对话历史
chat_histories = {}

# 不同角色的系统提示词模板
ROLE_PROMPTS = {
    "career_advisor": """你是一位专业的AI职业发展顾问，具有丰富的职业规划经验。你的职责是：

1. **个性化分析**：根据用户的技能、经验、目标提供针对性建议
2. **学习路线规划**：制定具体可行的技能提升计划
3. **求职指导**：提供面试技巧、简历优化、职场发展建议
4. **技术发展**：关注最新技术趋势，提供技术栈选择建议
5. **AI辅助开发**：指导如何使用AI工具提升工作效率

回答风格：
- 专业而友好，使用适当的emoji增强表达
- 提供具体可操作的建议，避免空泛的理论
- 结构化回答，使用标题、列表等格式
- 根据用户情况给出个性化的时间规划和学习路径

请始终保持专业、耐心、鼓励的态度，帮助用户实现职业发展目标。""",

    "resume_expert": """你是一位专业的简历优化专家，专门帮助用户制作和优化简历。你的专长包括：

1. **简历结构优化**：设计清晰、专业的简历布局
2. **内容提炼**：将用户经历转化为有吸引力的简历内容
3. **关键词优化**：确保简历能通过ATS系统筛选
4. **行业适配**：针对不同行业和职位定制简历
5. **量化成果**：帮助用户量化工作成果和技术贡献

回答特点：
- 专注于简历制作的具体细节
- 提供模板和示例
- 给出具体的修改建议
- 关注简历的视觉效果和可读性

当用户需要简历相关服务时，你会主动询问详细信息并生成专业的简历内容。""",

    "skill_mentor": """你是一位技能发展导师，专注于帮助用户提升专业技能。你的核心能力：

1. **技能评估**：准确评估用户当前技能水平
2. **学习路径设计**：制定系统性的技能学习计划
3. **实践项目推荐**：推荐适合的实战项目来巩固技能
4. **技术趋势分析**：分享最新的技术发展趋势
5. **学习资源推荐**：提供优质的学习资源和工具

教学风格：
- 循序渐进，从基础到进阶
- 理论结合实践，重视动手能力
- 提供具体的学习时间安排
- 鼓励持续学习和技能迭代

你会根据用户的技术背景和目标，制定个性化的技能提升方案。""",

    "interview_coach": """你是一位面试指导专家，专门帮助用户准备技术面试和职场面试。你的专业领域：

1. **面试准备**：制定全面的面试准备计划
2. **技术面试**：算法题解析、系统设计、技术深度问题
3. **行为面试**：STAR方法、软技能展示、职场情景应对
4. **模拟面试**：提供真实的面试场景练习
5. **心理建设**：帮助缓解面试焦虑，建立自信

指导特色：
- 提供具体的面试题目和标准答案
- 分析不同公司的面试风格
- 给出实用的面试技巧和注意事项
- 帮助用户准备项目介绍和技术展示

你会根据用户的目标职位和公司，提供针对性的面试准备建议。"""
}

def get_answer(messages, role="career_advisor"):
    """调用星火API获取回答"""
    headers = {
        'Authorization': api_key,
        'content-type': "application/json"
    }
    
    # 添加角色提示词到消息开头
    system_message = {"role": "system", "content": ROLE_PROMPTS.get(role, ROLE_PROMPTS["career_advisor"])}
    full_messages = [system_message] + messages
    
    body = {
        "model": "4.0Ultra",
        "user": "career_guidance_user",
        "messages": full_messages,
        "stream": True,
        "tools": [
            {
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_mode": "deep"
                }
            }
        ]
    }
    
    full_response = ""
    isFirstContent = True

    try:
        response = requests.post(url=url, json=body, headers=headers, stream=True)
        for chunks in response.iter_lines():
            if (chunks and '[DONE]' not in str(chunks)):
                data_org = chunks[6:]
                chunk = json.loads(data_org)
                text = chunk['choices'][0]['delta']

                if ('content' in text and '' != text['content']):
                    content = text["content"]
                    if (True == isFirstContent):
                        isFirstContent = False
                    print(content, end="")
                    full_response += content
    except Exception as e:
        print(f"API调用错误: {e}")
        full_response = "抱歉，AI服务暂时不可用，请稍后再试。"
    
    return full_response

def getText(text, role, content):
    """添加消息到对话历史"""
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def getlength(text):
    """计算对话历史长度"""
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def checklen(text):
    """检查并限制对话历史长度"""
    while (getlength(text) > 11000):
        del text[0]
    return text

def detect_user_intent(message):
    """检测用户意图，返回对应的角色"""
    message_lower = message.lower()
    
    # 简历相关关键词
    resume_keywords = ['简历', 'resume', 'cv', '个人情况', '求职', '应聘']
    if any(keyword in message_lower for keyword in resume_keywords):
        return "resume_expert"
    
    # 面试相关关键词
    interview_keywords = ['面试', 'interview', '算法题', '技术面试', '行为面试']
    if any(keyword in message_lower for keyword in interview_keywords):
        return "interview_coach"
    
    # 技能学习相关关键词
    skill_keywords = ['学习', '技能', '提升', '教程', '课程', '项目']
    if any(keyword in message_lower for keyword in skill_keywords):
        return "skill_mentor"
    
    # 默认返回职业顾问
    return "career_advisor"

@app.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    message = data.get('message', '')
    role = data.get('role', None)  # 允许前端指定角色

    # 初始化或获取该用户的聊天历史
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # 如果没有指定角色，自动检测
    if not role:
        role = detect_user_intent(message)

    # 添加用户消息到历史
    chat_history = checklen(getText(chat_histories[user_id], "user", message))

    # 获取模型回复
    print(f"用户 {user_id} ({role}): {message}")
    print("AI回复:", end="")
    assistant_reply = get_answer(chat_history, role)

    # 添加助手回复到历史
    getText(chat_histories[user_id], "assistant", assistant_reply)

    return jsonify({
        'status': 'success',
        'reply': assistant_reply,
        'role': role
    })

@app.route('/new_chat', methods=['POST'])
def new_chat():
    """开始新的对话"""
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')

    # 清空该用户的聊天历史
    if user_id in chat_histories:
        chat_histories[user_id] = []

    return jsonify({
        'status': 'success',
        'message': f'Chat history cleared for user {user_id}'
    })

@app.route('/set_role', methods=['POST'])
def set_role():
    """设置AI角色"""
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    role = data.get('role', 'career_advisor')
    
    # 验证角色是否有效
    if role not in ROLE_PROMPTS:
        return jsonify({
            'status': 'error',
            'message': 'Invalid role'
        }), 400
    
    return jsonify({
        'status': 'success',
        'message': f'Role set to {role} for user {user_id}',
        'role': role
    })

@app.route('/get_roles', methods=['GET'])
def get_roles():
    """获取可用的AI角色列表"""
    roles = [
        {
            'key': 'career_advisor',
            'name': '职业发展顾问',
            'description': '提供全面的职业规划和发展建议'
        },
        {
            'key': 'resume_expert', 
            'name': '简历优化专家',
            'description': '专业的简历制作和优化服务'
        },
        {
            'key': 'skill_mentor',
            'name': '技能发展导师', 
            'description': '制定个性化的技能学习计划'
        },
        {
            'key': 'interview_coach',
            'name': '面试指导专家',
            'description': '提供面试准备和技巧指导'
        }
    ]
    
    return jsonify({
        'status': 'success',
        'roles': roles
    })

if __name__ == '__main__':
    print("职业发展AI服务启动中...")
    print("支持的角色:")
    for key, name in [('career_advisor', '职业发展顾问'), ('resume_expert', '简历优化专家'), 
                      ('skill_mentor', '技能发展导师'), ('interview_coach', '面试指导专家')]:
        print(f"  - {name} ({key})")
    app.run(host='0.0.0.0', port=5001, debug=True)
