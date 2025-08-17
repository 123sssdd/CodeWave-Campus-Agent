#!/usr/bin/env python3
"""
测试LeetCode题库集成功能
"""
import requests
import json

def test_routes():
    """测试主要路由"""
    base_url = "http://localhost:5000"
    
    tests = [
        ("主页", "/"),
        ("学术模式首页", "/academic/"),
        ("学术练习页面", "/academic/practice"),
        ("面试模式首页", "/interview/"),
        ("面试练习页面", "/interview/practice"),
        ("错题本（学术）", "/academic/wrong-questions"),
        ("错题本（面试）", "/interview/wrong-questions"),
        ("知识点列表", "/api/knowledge-points"),
        ("题目列表", "/api/questions"),
        ("学术模式题目", "/api/questions/by-mode/academic"),
        ("面试模式题目", "/api/questions/by-mode/interview"),
    ]
    
    print("🔍 开始测试路由...")
    success_count = 0
    total_count = len(tests)
    
    for name, url in tests:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} ({url}) - 正常")
                success_count += 1
            else:
                print(f"❌ {name} ({url}) - 状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} ({url}) - 连接失败: {e}")
    
    print(f"\n📊 测试结果: {success_count}/{total_count} 通过")
    return success_count == total_count

def test_leetcode_questions():
    """测试LeetCode题目"""
    print("\n🧮 测试LeetCode题目...")
    try:
        response = requests.get("http://localhost:5000/api/questions", timeout=5)
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ 成功获取 {len(questions)} 道题目")
            
            leetcode_questions = [q for q in questions if q.get('external_platform') == 'leetcode']
            print(f"✅ 其中包含 {len(leetcode_questions)} 道LeetCode题目")
            
            # 显示一些题目信息
            for i, q in enumerate(leetcode_questions[:3], 1):
                print(f"  {i}. {q['title']} ({q['difficulty']}) - {q.get('external_id', 'N/A')}")
            
            return True
        else:
            print(f"❌ 获取题目失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_knowledge_points():
    """测试知识点"""
    print("\n📚 测试知识点...")
    try:
        response = requests.get("http://localhost:5000/api/knowledge-points", timeout=5)
        if response.status_code == 200:
            knowledge_points = response.json()
            print(f"✅ 成功获取 {len(knowledge_points)} 个知识点")
            
            for kp in knowledge_points:
                print(f"  • {kp['name']} ({kp['category']}) - 难度: {kp['difficulty_level']}")
            
            return True
        else:
            print(f"❌ 获取知识点失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("=== 🧪 LeetCode题库集成测试 ===\n")
    
    # 测试路由
    routes_ok = test_routes()
    
    # 测试LeetCode题目
    questions_ok = test_leetcode_questions()
    
    # 测试知识点
    knowledge_ok = test_knowledge_points()
    
    print("\n" + "="*50)
    if routes_ok and questions_ok and knowledge_ok:
        print("🎉 所有测试通过！LeetCode题库集成成功！")
        print("\n🚀 您现在可以:")
        print("  1. 访问 http://localhost:5000 体验新的LeetCode题库")
        print("  2. 在学术模式下练习经典算法题")
        print("  3. 使用错题本功能管理错题")
        print("  4. 体验改进的相似题目推荐")
    else:
        print("❌ 部分测试失败，请检查服务器状态")
    print("="*50)

if __name__ == "__main__":
    main()
