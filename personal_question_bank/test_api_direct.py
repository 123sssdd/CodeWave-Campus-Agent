#!/usr/bin/env python3
"""
直接测试API接口（不通过HTTP）
"""

from app import app, db
from flask import Flask
import json

def test_api_direct():
    with app.app_context():
        with app.test_client() as client:
            print('=== 测试学术模式推荐API ===')
            response = client.get('/api/recommendations/1?count=6&mode=academic')
            print(f'状态码: {response.status_code}')
            if response.status_code == 200:
                data = response.get_json()
                print(f'推荐题目数量: {len(data.get("recommendations", []))}')
                print(f'模式: {data.get("mode")}')
                if data.get('recommendations'):
                    print('前3道题目:')
                    for i, q in enumerate(data['recommendations'][:3]):
                        print(f'  {i+1}. {q.get("title", "无标题")} ({q.get("question_type", "未知类型")})')
            else:
                print(f'错误响应: {response.get_data(as_text=True)}')
            
            print('\n=== 测试面试模式推荐API ===')
            response = client.get('/api/recommendations/1?count=6&mode=interview')
            print(f'状态码: {response.status_code}')
            if response.status_code == 200:
                data = response.get_json()
                print(f'推荐题目数量: {len(data.get("recommendations", []))}')
                print(f'模式: {data.get("mode")}')
                if data.get('recommendations'):
                    print('前3道题目:')
                    for i, q in enumerate(data['recommendations'][:3]):
                        print(f'  {i+1}. {q.get("title", "无标题")} ({q.get("question_type", "未知类型")})')
            else:
                print(f'错误响应: {response.get_data(as_text=True)}')
            
            print('\n=== 测试按模式获取题目API ===')
            for mode in ['academic', 'interview']:
                response = client.get(f'/api/questions/by-mode/{mode}?per_page=5')
                print(f'{mode}模式题目API状态码: {response.status_code}')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f'题目总数: {data.get("total")}')
                    print(f'当前页题目数: {len(data.get("questions", []))}')
                    if data.get('questions'):
                        print('前3道题目:')
                        for i, q in enumerate(data['questions'][:3]):
                            print(f'  {i+1}. {q.get("title", "无标题")} ({q.get("question_type", "未知类型")})')
                else:
                    print(f'错误响应: {response.get_data(as_text=True)}')
                print()

if __name__ == "__main__":
    test_api_direct()
