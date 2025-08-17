#!/usr/bin/env python3
"""
测试新功能的脚本
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_wrong_questions_api():
    """测试错题本API"""
    print("=== 测试错题本API ===")
    
    # 1. 获取用户错题
    try:
        response = requests.get(f"{BASE_URL}/api/wrong-questions/1?mode=academic")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取错题成功: {data.get('count', 0)} 道错题")
        else:
            print(f"✗ 获取错题失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取错题失败: {e}")
    
    # 2. 添加错题 (模拟)
    try:
        wrong_data = {
            "user_id": 1,
            "question_id": 1,
            "wrong_answer": "错误的测试答案",
            "mode": "academic"
        }
        response = requests.post(f"{BASE_URL}/api/wrong-questions", json=wrong_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 添加错题成功: {data.get('message')}")
        else:
            print(f"✗ 添加错题失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 添加错题失败: {e}")

def test_interview_questions():
    """测试面试题目获取"""
    print("\n=== 测试面试题目API ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/questions/by-mode/interview")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取面试题目成功: {data.get('total', 0)} 道题目")
        else:
            print(f"✗ 获取面试题目失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取面试题目失败: {e}")

def test_hot_questions():
    """测试热门题目获取"""
    print("\n=== 测试热门题目API ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/interview/hot-questions?category=vue&limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 获取Vue热门题目成功: {len(data)} 道题目")
        else:
            print(f"✗ 获取热门题目失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取热门题目失败: {e}")

def test_routes():
    """测试页面路由"""
    print("\n=== 测试页面路由 ===")
    
    routes_to_test = [
        "/",
        "/interview",
        "/interview/practice",
        "/wrong-questions",
        "/practice/1",
        "/practice/1?mode=interview&question=1"
    ]
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{BASE_URL}{route}")
            if response.status_code == 200:
                print(f"✓ 路由 {route} 正常")
            else:
                print(f"✗ 路由 {route} 返回 {response.status_code}")
        except Exception as e:
            print(f"✗ 路由 {route} 错误: {e}")

if __name__ == "__main__":
    print("开始测试个人题库系统功能...")
    print("确保应用已在 http://localhost:5000 运行")
    
    test_routes()
    test_wrong_questions_api()
    test_interview_questions()
    test_hot_questions()
    
    print("\n测试完成！")
