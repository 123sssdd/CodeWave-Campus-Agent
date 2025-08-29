#!/usr/bin/env python3
"""
测试推荐功能的脚本
"""

import requests
import json
import time

def test_recommendation_api():
    """测试推荐API"""
    base_url = "http://localhost:5000"
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/api/users", timeout=5)
            if response.status_code == 200:
                print("✅ 服务器已启动")
                break
        except:
            time.sleep(2)
    else:
        print("❌ 服务器启动失败")
        return
    
    # 获取用户列表
    print("\n📋 获取用户列表...")
    response = requests.get(f"{base_url}/api/users")
    users = response.json()
    print(f"找到 {len(users)} 个用户:")
    for user in users:
        print(f"  - {user['username']} (ID: {user['id']}) - 偏好: {user['preferred_difficulty']}")
    
    # 测试每个用户的推荐
    for user in users:
        user_id = user['id']
        username = user['username']
        
        print(f"\n🎯 测试用户 {username} (ID: {user_id}) 的推荐...")
        
        # 获取推荐题目
        response = requests.get(f"{base_url}/api/recommendations/{user_id}?count=5")
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ 成功获取推荐，共 {recommendations['count']} 道题目:")
            
            for i, rec in enumerate(recommendations['recommendations'][:3], 1):
                print(f"  {i}. {rec['title']} ({rec['difficulty']}) - {rec['question_type']}")
        else:
            print(f"❌ 获取推荐失败: {response.status_code}")
            print(f"错误信息: {response.text}")
        
        time.sleep(1)  # 避免请求过快
    
    print("\n🎉 推荐功能测试完成！")

if __name__ == "__main__":
    test_recommendation_api()
