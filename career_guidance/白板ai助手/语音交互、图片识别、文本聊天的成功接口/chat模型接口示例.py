import requests
import json

# 基础URL
BASE_URL = "http://localhost:5000"


def start_new_chat(user_id="user_123"):
    """开始新的对话"""
    url = f"{BASE_URL}/new_chat"
    payload = {"user_id": user_id}
    response = requests.post(url, json=payload)
    return response.json()


def send_message(user_id="user_123", message=""):
    """发送消息并获取回复"""
    url = f"{BASE_URL}/chat"
    payload = {
        "user_id": user_id,
        "message": message
    }
    response = requests.post(url, json=payload)
    return response.json()


# 使用示例
if __name__ == "__main__":
    # 开始新的对话
    print("开始新的对话:")
    print(start_new_chat())

    # 第一次对话
    print("\n第一次对话:")
    response = send_message(message="你好，你现在是简历大师，这是我的个人情况：前端，react/vue，css 基础一般，js 基础扎实，了解网络请求、浏览器渲染原理、计网和 xss 脚本攻击等基础知识。熟悉 webpack 等打包工具的原理和配置，了解 Vite 的构建过程和底层源码， 参与过组件库开发和低代码平台开发，计划学习 vue 和 react 源码，算法是薄弱项，没有参与过大型项目的开发，了解微前端的概念和大致现状、方案。 理想职位 web 前端工程师，月薪 20k，城市北上广深杭。")
    print("AI回复:", response["reply"])

    # 连续对话（会记住上下文）
    print("\n第二次对话:")
    response = send_message(message="你能做什么？")
    print("AI回复:", response["reply"])

    # 开始新的对话（清除历史）
    print("\n开始新的对话:")
    print(start_new_chat())

    # 新对话中的问题（没有之前的上下文）
    print("\n新对话中的问题:")
    response = send_message(message="我们刚才聊了什么？")
    print("AI回复:", response["reply"])