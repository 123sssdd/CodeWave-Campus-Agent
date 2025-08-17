#!/usr/bin/env python3
"""
调试学术模式问题
"""

from app import app, db, Question, KnowledgePoint, User
from recommendation_engine import RecommendationEngine
import requests
import json

def debug_academic_mode():
    """调试学术模式"""
    
    print("=== 调试学术模式问题 ===")
    
    # 1. 检查数据库状态
    with app.app_context():
        print("\n1. 数据库状态检查:")
        academic_questions = Question.query.filter_by(question_bank_mode='academic').all()
        academic_kps = KnowledgePoint.query.filter_by(question_bank_mode='academic').all()
        users = User.query.all()
        
        print(f"   - 学术模式题目数: {len(academic_questions)}")
        print(f"   - 学术模式知识点数: {len(academic_kps)}")
        print(f"   - 用户数: {len(users)}")
        
        if academic_questions:
            print("   - 前5道学术题目:")
            for i, q in enumerate(academic_questions[:5]):
                print(f"     {i+1}. ID:{q.id} - {q.title} ({q.question_type}, {q.difficulty})")
        
        # 2. 测试推荐引擎
        print("\n2. 推荐引擎测试:")
        try:
            engine = RecommendationEngine()
            recommendations = engine.recommend_questions(1, 6, 'academic')
            print(f"   - 推荐成功，获得 {len(recommendations)} 道题目")
            for i, q in enumerate(recommendations):
                print(f"     {i+1}. {q.title} ({q.question_type}, {q.difficulty})")
        except Exception as e:
            print(f"   - 推荐失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 3. 测试API接口
    print("\n3. API接口测试:")
    
    # 测试推荐API
    try:
        with app.test_client() as client:
            response = client.get('/api/recommendations/1?count=6&mode=academic')
            print(f"   - 推荐API状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   - 返回题目数: {len(data.get('recommendations', []))}")
                print(f"   - 模式: {data.get('mode')}")
            else:
                print(f"   - 错误响应: {response.get_data(as_text=True)}")
    except Exception as e:
        print(f"   - API测试失败: {e}")
    
    # 测试按模式获取题目API
    try:
        with app.test_client() as client:
            response = client.get('/api/questions/by-mode/academic?per_page=10')
            print(f"   - 按模式获取题目API状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   - 题目总数: {data.get('total')}")
                print(f"   - 当前页题目数: {len(data.get('questions', []))}")
            else:
                print(f"   - 错误响应: {response.get_data(as_text=True)}")
    except Exception as e:
        print(f"   - API测试失败: {e}")
    
    # 4. 检查路由
    print("\n4. 路由检查:")
    with app.app_context():
        with app.test_client() as client:
            # 测试学术模式练习页面
            response = client.get('/practice/1?mode=academic')
            print(f"   - 学术模式练习页面状态码: {response.status_code}")
            
            # 测试学术模式专用路由
            response = client.get('/academic/practice')
            print(f"   - 学术模式专用路由状态码: {response.status_code}")
            
            # 测试默认练习页面
            response = client.get('/practice')
            print(f"   - 默认练习页面状态码: {response.status_code}")

def test_http_requests():
    """测试HTTP请求"""
    print("\n5. HTTP请求测试:")
    
    base_url = "http://localhost:5000"
    
    # 测试推荐API
    try:
        response = requests.get(f"{base_url}/api/recommendations/1?count=6&mode=academic", timeout=10)
        print(f"   - HTTP推荐API状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - 返回题目数: {len(data.get('recommendations', []))}")
        else:
            print(f"   - 错误响应: {response.text}")
    except requests.exceptions.ConnectionError:
        print("   - 连接失败: 应用可能没有运行在5000端口")
    except Exception as e:
        print(f"   - HTTP请求失败: {e}")

if __name__ == "__main__":
    debug_academic_mode()
    test_http_requests()
