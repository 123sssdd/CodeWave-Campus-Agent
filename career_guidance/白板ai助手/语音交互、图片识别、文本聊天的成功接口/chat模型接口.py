# # encoding:UTF-8
# import json
# import requests
# from flask import Flask, request, jsonify
# from flask_cors import CORS
#
# app = Flask(__name__)
# CORS(app)  # 允许跨域请求
#
# api_key = "Bearer IZCYjZldtFfctRDljtZJ:yGDOYHzOXQRmoKXQIRAw"
# url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
#
# # 全局变量存储对话历史（实际应用中应该使用数据库）
# chat_histories = {}
#
#
# # 请求模型，并将结果输出
# def get_answer(message):
#     headers = {
#         'Authorization': api_key,
#         'content-type': "application/json"
#     }
#     body = {
#         "model": "4.0Ultra",
#         "user": "user_id",
#         "messages": message,
#         "stream": True,
#         "tools": [
#             {
#                 "type": "web_search",
#                 "web_search": {
#                     "enable": True,
#                     "search_mode": "deep"
#                 }
#             }
#         ]
#     }
#     full_response = ""
#     isFirstContent = True
#
#     response = requests.post(url=url, json=body, headers=headers, stream=True)
#     for chunks in response.iter_lines():
#         if (chunks and '[DONE]' not in str(chunks)):
#             data_org = chunks[6:]
#             chunk = json.loads(data_org)
#             text = chunk['choices'][0]['delta']
#
#             if ('content' in text and '' != text['content']):
#                 content = text["content"]
#                 if (True == isFirstContent):
#                     isFirstContent = False
#                 print(content, end="")
#                 full_response += content
#     return full_response
#
#
# def getText(text, role, content):
#     jsoncon = {}
#     jsoncon["role"] = role
#     jsoncon["content"] = content
#     text.append(jsoncon)
#     return text
#
#
# def getlength(text):
#     length = 0
#     for content in text:
#         temp = content["content"]
#         leng = len(temp)
#         length += leng
#     return length
#
#
# def checklen(text):
#     while (getlength(text) > 11000):
#         del text[0]
#     return text
#
#
# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     user_id = data.get('user_id', 'default_user')  # 获取用户ID，默认为'default_user'
#     message = data.get('message', '')
#
#     # 初始化或获取该用户的聊天历史
#     if user_id not in chat_histories:
#         chat_histories[user_id] = []
#
#     # 添加用户消息到历史
#     chat_history = checklen(getText(chat_histories[user_id], "user", message))
#
#     # 获取模型回复
#     print(f"用户 {user_id}: {message}")
#     print("星火:", end="")
#     assistant_reply = get_answer(chat_history)
#
#     # 添加助手回复到历史
#     getText(chat_histories[user_id], "assistant", assistant_reply)
#
#     return jsonify({
#         'status': 'success',
#         'reply': assistant_reply
#     })
#
#
# @app.route('/new_chat', methods=['POST'])
# def new_chat():
#     data = request.get_json()
#     user_id = data.get('user_id', 'default_user')
#
#     # 清空该用户的聊天历史
#     if user_id in chat_histories:
#         chat_histories[user_id] = []
#
#     return jsonify({
#         'status': 'success',
#         'message': f'Chat history cleared for user {user_id}'
#     })
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)


# encoding:UTF-8
import json
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # 允许跨域请求

api_key = "Bearer IZCYjZldtFfctRDljtZJ:yGDOYHzOXQRmoKXQIRAw"
url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

# 全局变量存储对话历史（实际应用中应该使用数据库）
chat_histories = {}


def get_answer_stream(messages):
    headers = {
        'Authorization': api_key,
        'content-type': "application/json"
    }
    body = {
        "model": "4.0Ultra",
        "user": "user_id",
        "messages": messages,
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

    response = requests.post(url=url, json=body, headers=headers, stream=True)

    for chunk in response.iter_lines():
        if chunk:
            # 解码字节数据
            decoded_chunk = chunk.decode('utf-8')

            # 跳过SSE格式的注释和空行
            if decoded_chunk.startswith(':') or decoded_chunk == '':
                continue

            # 检查是否为结束标记
            if decoded_chunk == 'data: [DONE]':
                yield f"data: {json.dumps({'finished': True})}\n\n"
                break

            # 提取JSON数据
            if decoded_chunk.startswith('data:'):
                json_str = decoded_chunk[5:].strip()
                try:
                    data = json.loads(json_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        if 'content' in delta and delta['content']:
                            # 发送内容给客户端
                            yield f"data: {json.dumps({'content': delta['content'], 'finished': False})}\n\n"
                except json.JSONDecodeError:
                    continue


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

    # 创建流式响应
    def generate():
        full_response = ""
        for chunk in get_answer_stream(chat_history):
            # 将数据发送给客户端
            yield chunk

            # 提取内容并构建完整响应
            try:
                chunk_data = json.loads(chunk[5:].strip())  # 去掉 "data: " 前缀
                if 'content' in chunk_data:
                    full_response += chunk_data['content']
            except:
                pass

        # 流结束后，将完整回复添加到历史记录
        if full_response:
            getText(chat_histories[user_id], "assistant", full_response)

    return Response(generate(), mimetype='text/event-stream')


@app.route('/chat_non_stream', methods=['POST'])
def chat_non_stream():
    """保留原来的非流式接口作为备选"""
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    message = data.get('message', '')

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_history = checklen(getText(chat_histories[user_id], "user", message))

    full_response = ""
    headers = {
        'Authorization': api_key,
        'content-type': "application/json"
    }
    body = {
        "model": "4.0Ultra",
        "user": "user_id",
        "messages": chat_history,
        "stream": False,  # 非流式
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

    response = requests.post(url=url, json=body, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            full_response = result['choices'][0]['message']['content']
            getText(chat_histories[user_id], "assistant", full_response)

    return jsonify({
        'status': 'success',
        'reply': full_response
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)