# encoding:UTF-8
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 星火API配置
api_key = "Bearer IZCYjZldtFfctRDljtZJ:yGDOYHzOXQRmoKXQIRAw"
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

# 存储对话历史
chat_histories = {}

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
    try:
        response = requests.post(url=url, json=body, headers=headers, stream=True)
        for chunks in response.iter_lines():
            if chunks and '[DONE]' not in str(chunks):
                data_org = chunks[6:]
                chunk = json.loads(data_org)
                text = chunk['choices'][0]['delta']
                
                if 'content' in text and text['content'] != '':
                    content = text["content"]
                    print(content, end="")
                    full_response += content
    except Exception as e:
        print(f"API请求错误: {e}")
        return f"错误: {e}"
    
    return full_response

def getText(text, role, content):
    jsoncon = {"role": role, "content": content}
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
    while getlength(text) > 11000:
        del text[0]
    return text

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        message = data.get('message', '')

        if user_id not in chat_histories:
            chat_histories[user_id] = []

        chat_history = checklen(getText(chat_histories[user_id], "user", message))

        print(f"用户 {user_id}: {message}")
        print("星火:", end="")
        assistant_reply = get_answer(chat_history)

        getText(chat_histories[user_id], "assistant", assistant_reply)

        return jsonify({
            'status': 'success',
            'reply': assistant_reply
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/new_chat', methods=['POST'])
def new_chat():
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    
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
    print("服务器将运行在 http://0.0.0.0:5001")
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        import traceback
        traceback.print_exc()