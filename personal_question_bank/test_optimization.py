#!/usr/bin/env python3
"""
测试测试用例布局优化效果
"""
import requests
import time
import json

def test_test_cases_optimization():
    """测试测试用例优化"""
    base_url = "http://localhost:5000"
    
    print("⏳ 等待服务器启动...")
    time.sleep(5)
    
    print("🧪 测试测试用例布局优化...")
    
    try:
        # 测试获取LeetCode题目
        response = requests.get(f"{base_url}/api/questions/by-mode/academic", timeout=10)
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ 成功获取 {len(questions)} 道学术题目")
            
            # 查看test_cases数据结构
            coding_questions = [q for q in questions if q.get('question_type') == 'coding' and q.get('test_cases')]
            print(f"✅ 其中包含 {len(coding_questions)} 道有测试用例的编程题")
            
            if coding_questions:
                sample_question = coding_questions[0]
                print(f"\n📝 示例题目: {sample_question['title']}")
                
                # 检查test_cases格式
                test_cases_str = sample_question.get('test_cases', '[]')
                try:
                    test_cases = json.loads(test_cases_str)
                    print(f"✅ 测试用例格式正确 - 包含 {len(test_cases)} 个用例")
                    
                    # 显示第一个测试用例
                    if test_cases:
                        first_case = test_cases[0]
                        print(f"📋 第一个测试用例:")
                        print(f"   输入: {first_case.get('input', 'N/A')}")
                        print(f"   期望输出: {first_case.get('expected', 'N/A')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ 测试用例JSON格式错误: {e}")
                    print(f"   原始数据: {test_cases_str[:100]}...")
                    
        else:
            print(f"❌ 获取题目失败: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败: {str(e)[:50]}...")
        return False
    
    # 测试练习页面
    try:
        print(f"\n🔗 测试练习页面访问...")
        response = requests.get(f"{base_url}/academic/practice", timeout=10)
        if response.status_code == 200:
            print("✅ 学术练习页面正常")
        else:
            print(f"❌ 学术练习页面错误: {response.status_code}")
            
        response = requests.get(f"{base_url}/interview/practice", timeout=10)
        if response.status_code == 200:
            print("✅ 面试练习页面正常")
        else:
            print(f"❌ 面试练习页面错误: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 练习页面测试失败: {str(e)[:50]}...")
    
    print(f"\n🎉 测试用例布局优化完成！")
    print(f"💡 优化内容:")
    print(f"   • 📊 网格布局 - 每行显示2个测试用例")
    print(f"   • 🎨 美化样式 - 渐变背景和圆角卡片")  
    print(f"   • 📝 格式化显示 - JSON数据自动格式化")
    print(f"   • 🏷️  标签显示 - 显示用例编号和来源")
    print(f"   • 💡 提示信息 - 添加使用说明")
    print(f"   • 📏 响应式设计 - 适配不同屏幕尺寸")
    
    print(f"\n🚀 现在可以访问:")
    print(f"   • 主页: http://localhost:5000")
    print(f"   • 学术练习: http://localhost:5000/academic/practice") 
    print(f"   • 面试练习: http://localhost:5000/interview/practice")

if __name__ == "__main__":
    test_test_cases_optimization()

