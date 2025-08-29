#!/usr/bin/env python3
"""
测试新页面功能的脚本
"""

import requests
import time

def test_new_pages():
    """测试新页面的API接口"""
    base_url = "http://localhost:5000"
    user_id = 1
    
    print("🧪 开始测试新页面功能...")
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ 服务器已启动")
                break
        except:
            time.sleep(2)
    else:
        print("❌ 服务器启动失败")
        return
    
    # 测试API接口
    test_cases = [
        ("用户进度API", f"/api/users/{user_id}/progress"),
        ("学习路径API", f"/api/learning-path/{user_id}"),
        ("知识点列表API", "/api/knowledge-points"),
        ("知识点详情API", "/api/knowledge-points/1/questions"),
    ]
    
    for name, endpoint in test_cases:
        try:
            print(f"\n🧪 测试 {name}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name} 成功")
                
                # 简单的数据验证
                if "learning_path" in endpoint:
                    print(f"   - 学习路径数量: {len(data.get('learning_path', []))}")
                elif "progress" in endpoint:
                    print(f"   - 总体进度: {data.get('overall_progress', 0)*100:.1f}%")
                elif "questions" in endpoint:
                    print(f"   - 相关题目数量: {len(data.get('questions', []))}")
                elif "knowledge-points" in endpoint and isinstance(data, list):
                    print(f"   - 知识点总数: {len(data)}")
                    
            else:
                print(f"❌ {name} 失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name} 异常: {e}")
    
    # 测试页面访问
    print("\n🌐 测试页面访问...")
    page_tests = [
        ("首页", "/"),
        ("知识点页面", f"/knowledge-points/{user_id}"),
        ("学习路径页面", f"/learning-path/{user_id}"),
        ("练习页面", f"/practice/{user_id}"),
        ("统计页面", f"/dashboard/{user_id}"),
    ]
    
    for name, url in page_tests:
        try:
            response = requests.get(f"{base_url}{url}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} 页面访问正常")
            else:
                print(f"❌ {name} 页面访问失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name} 页面访问异常: {e}")
    
    print("\n🎉 测试完成！")
    print("\n📋 访问地址:")
    print(f"   • 首页: {base_url}/")
    print(f"   • 知识点: {base_url}/knowledge-points/{user_id}")
    print(f"   • 学习路径: {base_url}/learning-path/{user_id}")
    print(f"   • 练习模式: {base_url}/practice/{user_id}")
    print(f"   • 学习统计: {base_url}/dashboard/{user_id}")

if __name__ == "__main__":
    test_new_pages()
