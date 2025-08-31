# encoding:UTF-8
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

api_key = "Bearer IZCYjZldtFfctRDljtZJ:yGDOYHzOXQRmoKXQIRAw"
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

# 全局变量存储对话历史（实际应用中应该使用数据库）
chat_histories = {}


# 请求模型，并将结果输出
def get_answer(message):
    headers = {
        'Authorization': api_key,
        'content-type': "application/json"
    }
    body = {
        "model": "4.0Ultra",
        "user": "user_id",
        "messages": message,
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
    return full_response


def getText(text, role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while (getlength(text) > 11000):
        del text[0]
    return text


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')  # 获取用户ID，默认为'default_user'
    message = data.get('message', '')

    # 初始化或获取该用户的聊天历史
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    # 添加用户消息到历史
    chat_history = checklen(getText(chat_histories[user_id], "user", message))

    # 获取模型回复
    print(f"用户 {user_id}: {message}")
    print("星火:", end="")
    assistant_reply = get_answer(chat_history)

    # 添加助手回复到历史
    getText(chat_histories[user_id], "assistant", assistant_reply)

    return jsonify({
        'status': 'success',
        'reply': assistant_reply
    })


@app.route('/new_chat', methods=['POST'])
def new_chat():
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')

    # 清空该用户的聊天历史
    if user_id in chat_histories:
        chat_histories[user_id] = []

    return jsonify({
        'status': 'success',
        'message': f'Chat history cleared for user {user_id}'
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "chat"})

if __name__ == '__main__':
    print("正在启动聊天API服务器...")
    print("服务器将运行在 http://0.0.0.0:5002")
    try:
        app.run(host='0.0.0.0', port=5002, debug=True)
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        import traceback
        traceback.print_exc()
    # app.run(host='0.0.0.0', port=5001, debug=True)