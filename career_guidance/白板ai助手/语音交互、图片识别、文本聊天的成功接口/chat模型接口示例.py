# import requests
# import json
#
# # 基础URL
# BASE_URL = "http://localhost:5000"
#
#
# def start_new_chat(user_id="user_123"):
#     """开始新的对话"""
#     url = f"{BASE_URL}/new_chat"
#     payload = {"user_id": user_id}
#     response = requests.post(url, json=payload)
#     return response.json()
#
#
# def send_message(user_id="user_123", message=""):
#     """发送消息并获取回复"""
#     url = f"{BASE_URL}/chat"
#     payload = {
#         "user_id": user_id,
#         "message": message
#     }
#     response = requests.post(url, json=payload)
#     return response.json()
#
#
# # 使用示例
# if __name__ == "__main__":
#     # 开始新的对话
#     print("开始新的对话:")
#     print(start_new_chat())
#
#     # 第一次对话
#     print("\n第一次对话:")
#     response = send_message(message="你好，你现在是简历大师，这是我的个人情况：前端，react/vue，css 基础一般，js 基础扎实，了解网络请求、浏览器渲染原理、计网和 xss 脚本攻击等基础知识。熟悉 webpack 等打包工具的原理和配置，了解 Vite 的构建过程和底层源码， 参与过组件库开发和低代码平台开发，计划学习 vue 和 react 源码，算法是薄弱项，没有参与过大型项目的开发，了解微前端的概念和大致现状、方案。 理想职位 web 前端工程师，月薪 20k，城市北上广深杭。")
#     print("AI回复:", response["reply"])
#
#     # 连续对话（会记住上下文）
#     print("\n第二次对话:")
#     response = send_message(message="你能做什么？")
#     print("AI回复:", response["reply"])
#
#     # 开始新的对话（清除历史）
#     print("\n开始新的对话:")
#     print(start_new_chat())
#
#     # 新对话中的问题（没有之前的上下文）
#     print("\n新对话中的问题:")
#     response = send_message(message="我们刚才聊了什么？")
#     print("AI回复:", response["reply"])

import requests
import json
import sys
import time


class SparkChatClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.user_id = "default_user"
        self.conversation_history = []

    def set_user_id(self, user_id):
        self.user_id = user_id

    def new_chat(self):
        """清空当前对话历史"""
        try:
            response = requests.post(
                f"{self.base_url}/new_chat",
                json={"user_id": self.user_id}
            )
            if response.status_code == 200:
                print("对话历史已清空")
                self.conversation_history = []
            else:
                print(f"清空对话历史失败: {response.text}")
        except Exception as e:
            print(f"请求出错: {e}")

    def chat(self, message):
        """发送消息并接收流式响应"""
        print(f"\n用户: {message}")
        print("星火: ", end="", flush=True)

        try:
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "message": message,
                    "user_id": self.user_id
                },
                stream=True
            )

            if response.status_code != 200:
                print(f"请求失败: {response.text}")
                return

            # 处理流式响应
            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # 解析SSE格式的数据
                    if line.startswith('data: '):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        try:
                            data = json.loads(data_str)
                            if 'content' in data:
                                content = data['content']
                                print(content, end="", flush=True)
                                full_response += content
                            if data.get('finished', False):
                                break
                        except json.JSONDecodeError:
                            print(f"解析JSON出错: {data_str}")
                            continue

            # 将完整的响应添加到对话历史
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            print()  # 换行

        except Exception as e:
            print(f"请求出错: {e}")

    def print_history(self):
        """打印对话历史"""
        print("\n=== 对话历史 ===")
        for msg in self.conversation_history:
            role = "用户" if msg["role"] == "user" else "星火"
            print(f"{role}: {msg['content']}")
        print("===============\n")

    def run_interactive(self):
        """运行交互式聊天界面"""
        print("星火认知大模型聊天客户端")
        print(f"用户ID: {self.user_id}")
        print("输入 'quit' 退出, 'clear' 清空对话历史, 'history' 查看历史")
        print("-" * 50)

        while True:
            try:
                user_input = input("你: ").strip()

                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'clear':
                    self.new_chat()
                elif user_input.lower() == 'history':
                    self.print_history()
                elif user_input:
                    self.chat(user_input)

            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"出错: {e}")


if __name__ == "__main__":
    # 创建客户端实例
    client = SparkChatClient()

    # 如果需要更改用户ID
    # client.set_user_id("your_user_id")

    # 运行交互式界面
    client.run_interactive()