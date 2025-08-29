#!/usr/bin/env python3
"""
调试面试错题本API
"""

from app import app
import json

def debug_interview_api():
    """调试面试错题本API"""
    
    with app.test_client() as client:
        print("=== 调试面试错题本API ===")
        
        # 测试面试模式错题API
        response = client.get('/api/wrong-questions/1?mode=interview')
        print(f'API状态码: {response.status_code}')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f'API响应结构:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success') and data.get('wrong_questions'):
                print(f'\n错题数量: {len(data["wrong_questions"])}')
                
                # 检查第一道错题的详细结构
                if data['wrong_questions']:
                    first_wq = data['wrong_questions'][0]
                    print(f'\n第一道错题的结构:')
                    print(json.dumps(first_wq, indent=2, ensure_ascii=False))
                    
                    # 检查question字段
                    if 'question' in first_wq and first_wq['question']:
                        question = first_wq['question']
                        print(f'\n题目字段:')
                        print(f'- title: {question.get("title")}')
                        print(f'- content: {question.get("content", "")[:100]}...')
                        print(f'- question_type: {question.get("question_type")}')
                        print(f'- difficulty: {question.get("difficulty")}')
                        print(f'- knowledge_point: {question.get("knowledge_point")}')
                        
                        # 检查knowledge_point字段
                        if question.get('knowledge_point'):
                            kp = question['knowledge_point']
                            print(f'\n知识点字段:')
                            print(f'- name: {kp.get("name")}')
                            print(f'- category: {kp.get("category")}')
                            print(f'- difficulty_level: {kp.get("difficulty_level")}')
        else:
            print(f'API错误: {response.get_data(as_text=True)}')

if __name__ == "__main__":
    debug_interview_api()
