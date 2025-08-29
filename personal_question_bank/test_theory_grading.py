#!/usr/bin/env python3
"""
测试理论题智能评分系统
"""

from theory_grader import grade_theory_answer

def test_theory_grading():
    """测试不同情况下的理论题评分"""
    
    # 测试用例
    test_cases = [
        {
            "name": "完全正确的答案",
            "question": "什么是数组？",
            "correct_answer": "数组是一种线性数据结构，存储相同类型的元素，在内存中连续存储，支持随机访问。",
            "user_answer": "数组是线性数据结构，元素类型相同，连续存储在内存中，可以随机访问任意元素。",
            "expected_score_range": (0.8, 1.0)
        },
        {
            "name": "部分正确的答案",
            "question": "什么是栈？",
            "correct_answer": "栈是后进先出的数据结构，主要操作是push和pop，常用于函数调用管理。",
            "user_answer": "栈是一种数据结构，主要有push操作。",
            "expected_score_range": (0.3, 0.7)
        },
        {
            "name": "有错误概念的答案",
            "question": "什么是栈？",
            "correct_answer": "栈是后进先出的数据结构，主要操作是push和pop。",
            "user_answer": "栈是先进先出的数据结构，可以从两端操作。",
            "expected_score_range": (0.0, 0.4)
        },
        {
            "name": "空答案",
            "question": "什么是队列？",
            "correct_answer": "队列是先进先出的数据结构，主要操作是enqueue和dequeue。",
            "user_answer": "",
            "expected_score_range": (0.0, 0.0)
        },
        {
            "name": "使用同义词的答案",
            "question": "什么是哈希表？",
            "correct_answer": "哈希表是通过哈希函数将键映射到数组索引的数据结构，提供快速查找。",
            "user_answer": "散列表使用hash函数把key映射到索引，可以快速搜索。",
            "expected_score_range": (0.7, 1.0)
        }
    ]
    
    print("🧪 开始测试理论题智能评分系统...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_case['name']}")
        print(f"题目: {test_case['question']}")
        print(f"标准答案: {test_case['correct_answer']}")
        print(f"用户答案: {test_case['user_answer'] or '(空答案)'}")
        
        result = grade_theory_answer(
            test_case['user_answer'], 
            test_case['correct_answer'],
            test_case['question']
        )
        
        score = result['score']
        expected_min, expected_max = test_case['expected_score_range']
        
        print(f"得分: {score:.2f} ({score*100:.1f}%)")
        print(f"是否正确: {'✅' if result['is_correct'] else '❌'}")
        print(f"反馈: {result['feedback']}")
        print(f"鼓励评语: {result['encouragement']}")
        
        if result['correct_keywords']:
            print(f"答对的要点: {', '.join(result['correct_keywords'])}")
        if result['missing_keywords']:
            print(f"遗漏的要点: {', '.join(result['missing_keywords'])}")
        if result['incorrect_parts']:
            print(f"错误部分: {', '.join(result['incorrect_parts'])}")
        
        # 验证分数是否在预期范围内
        if expected_min <= score <= expected_max:
            print("✅ 分数在预期范围内")
        else:
            print(f"❌ 分数不在预期范围内 (期望: {expected_min}-{expected_max})")
        
        print("-" * 80)
        print()

def test_api_integration():
    """测试API集成"""
    import requests
    import time
    
    print("🔗 测试API集成...")
    
    base_url = "http://localhost:5000"
    
    # 等待服务器启动
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/", timeout=3)
            if response.status_code == 200:
                print("✅ 服务器已启动")
                break
        except:
            time.sleep(1)
    else:
        print("❌ 服务器未启动，跳过API测试")
        return
    
    # 测试提交理论题答案
    test_data = {
        "user_id": 1,
        "question_id": 1,  # 假设ID为1的是理论题
        "user_answer": "数组是一种线性的数据结构，可以存储多个相同类型的元素，支持通过索引快速访问。",
        "time_spent": 60,
        "interaction_type": "theory_read"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/learning-records",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功")
            print(f"得分: {result.get('score_percentage', 0)}%")
            
            if 'grading_result' in result:
                grading = result['grading_result']
                print(f"反馈: {grading.get('feedback', '')}")
                print(f"鼓励: {grading.get('encouragement', '')}")
            
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ API测试异常: {e}")

if __name__ == "__main__":
    # 测试评分算法
    test_theory_grading()
    
    # 测试API集成
    test_api_integration()
    
    print("🎉 测试完成！")
