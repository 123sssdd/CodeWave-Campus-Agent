#!/usr/bin/env python3
"""
测试修复后的功能
"""
import requests
import time

def test_wrong_questions_routes():
    """测试错题本路由"""
    base_url = "http://localhost:5000"
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    routes_to_test = [
        ("学术模式错题本", "/academic/wrong-questions"),
        ("面试模式错题本", "/interview/wrong-questions"), 
        ("API - 获取题目", "/api/questions/by-mode/academic"),
        ("API - 获取面试题目", "/api/questions/by-mode/interview")
    ]
    
    print("🔍 测试错题本路由修复...")
    success_count = 0
    
    for name, url in routes_to_test:
        try:
            response = requests.get(f"{base_url}{url}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} - 正常 (200)")
                success_count += 1
            elif response.status_code == 500:
                print(f"❌ {name} - 服务器错误 (500)")
            else:
                print(f"⚠️  {name} - 状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} - 连接失败: {str(e)[:50]}...")
    
    print(f"\n📊 修复结果: {success_count}/{len(routes_to_test)} 路由正常")
    
    if success_count == len(routes_to_test):
        print("🎉 所有问题已修复！")
        print("💡 现在您可以:")
        print("   • 正常访问学术模式错题本")
        print("   • 正常访问面试模式错题本") 
        print("   • 题目应该能正常加载")
    else:
        print("⚠️  仍有部分问题，可能需要进一步调试")

if __name__ == "__main__":
    test_wrong_questions_routes()
