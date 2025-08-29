#!/usr/bin/env python3
"""
测试API接口
"""

import requests
import json

def test_academic_mode():
    """测试学术模式推荐API"""
    try:
        response = requests.get('http://localhost:5000/api/recommendations/1?count=6&mode=academic')
        print(f'学术模式推荐API状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'推荐题目数量: {len(data.get("recommendations", []))}')
            print(f'模式: {data.get("mode")}')
            if data.get('recommendations'):
                print('前3道题目:')
                for i, q in enumerate(data['recommendations'][:3]):
                    print(f'  {i+1}. {q.get("title", "无标题")} ({q.get("question_type", "未知类型")})')
        else:
            print(f'错误响应: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

def test_interview_mode():
    """测试面试模式推荐API"""
    try:
        response = requests.get('http://localhost:5000/api/recommendations/1?count=6&mode=interview')
        print(f'面试模式推荐API状态码: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'推荐题目数量: {len(data.get("recommendations", []))}')
            print(f'模式: {data.get("mode")}')
            if data.get('recommendations'):
                print('前3道题目:')
                for i, q in enumerate(data['recommendations'][:3]):
                    print(f'  {i+1}. {q.get("title", "无标题")} ({q.get("question_type", "未知类型")})')
        else:
            print(f'错误响应: {response.text}')
    except Exception as e:
        print(f'请求失败: {e}')

def test_questions_by_mode():
    """测试按模式获取题目API"""
    for mode in ['academic', 'interview']:
        try:
            response = requests.get(f'http://localhost:5000/api/questions/by-mode/{mode}?per_page=5')
            print(f'{mode}模式题目API状态码: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print(f'题目总数: {data.get("total")}')
                print(f'当前页题目数: {len(data.get("questions", []))}')
                if data.get('questions'):
                    print('前3道题目:')
                    for i, q in enumerate(data['questions'][:3]):
                        print(f'  {i+1}. {q.get("title", "无标题")} ({q.get("question_type", "未知类型")})')
            else:
                print(f'错误响应: {response.text}')
        except Exception as e:
            print(f'请求失败: {e}')
        print()

if __name__ == "__main__":
    print("=== 测试学术模式 ===")
    test_academic_mode()
    print()
    
    print("=== 测试面试模式 ===")
    test_interview_mode()
    print()
    
    print("=== 测试按模式获取题目 ===")
    test_questions_by_mode()
