#!/usr/bin/env python3
"""
测试路由的脚本
"""

import requests
import time

def test_routes():
    """测试所有重要的路由"""
    base_url = "http://localhost:5000"
    
    routes_to_test = [
        ("/", "主页"),
        ("/interview", "面试主页"),
        ("/interview/mock", "模拟面试"),
        ("/interview/practice", "面试练习"),
        ("/wrong-questions", "错题本"),
        ("/practice/1", "练习页面"),
        ("/api/questions/count", "题目统计API"),
        ("/api/wrong-questions/1?mode=academic", "错题API")
    ]
    
    print("等待服务器启动...")
    time.sleep(3)
    
    print("\n=== 测试路由 ===")
    for route, name in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} ({route}) - 正常")
            elif response.status_code == 404:
                print(f"❌ {name} ({route}) - 404 未找到")
            else:
                print(f"⚠️  {name} ({route}) - 状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} ({route}) - 连接失败: {e}")
    
    print("\n=== 测试API功能 ===")
    
    # 测试错题本API
    try:
        response = requests.get(f"{base_url}/api/wrong-questions/1?mode=academic")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 错题本API正常 - 返回 {data.get('count', 0)} 道错题")
        else:
            print(f"❌ 错题本API异常 - 状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 错题本API测试失败: {e}")
    
    # 测试题目API
    try:
        response = requests.get(f"{base_url}/api/questions/by-mode/interview")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 面试题目API正常 - 返回 {data.get('total', 0)} 道题目")
        else:
            print(f"❌ 面试题目API异常 - 状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 面试题目API测试失败: {e}")

if __name__ == "__main__":
    test_routes()
