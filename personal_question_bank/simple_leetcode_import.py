#!/usr/bin/env python3
"""
简单的LeetCode题目导入脚本
直接替换现有的模拟数据为真实的LeetCode题目
"""

from app import app, db
from models import Question, KnowledgePoint, LearningRecord, UserKnowledgeStats, WrongQuestion, SimilarQuestion
from datetime import datetime
import json

def clear_all_questions():
    """清除所有题目相关数据"""
    print("正在清除现有题目数据...")
    
    with app.app_context():
        # 删除相关数据（保持外键约束）
        db.session.query(SimilarQuestion).delete()
        db.session.query(WrongQuestion).delete()
        db.session.query(LearningRecord).delete() 
        db.session.query(UserKnowledgeStats).delete()
        db.session.query(Question).delete()
        db.session.query(KnowledgePoint).delete()
        
        db.session.commit()
        print("✅ 现有数据已清除")

def create_leetcode_knowledge_points():
    """创建LeetCode相关知识点"""
    print("正在创建LeetCode知识点...")
    
    knowledge_points_data = [
        {"name": "数组", "category": "数据结构", "description": "数组操作、双指针技巧", "difficulty_level": 1, "question_bank_mode": "academic"},
        {"name": "链表", "category": "数据结构", "description": "链表操作、快慢指针", "difficulty_level": 2, "question_bank_mode": "academic"},
        {"name": "字符串", "category": "数据结构", "description": "字符串处理、模式匹配", "difficulty_level": 2, "question_bank_mode": "academic"},
        {"name": "哈希表", "category": "数据结构", "description": "哈希表应用、查找优化", "difficulty_level": 2, "question_bank_mode": "academic"},
        {"name": "栈", "category": "数据结构", "description": "栈的应用、表达式求值", "difficulty_level": 2, "question_bank_mode": "academic"},
        {"name": "队列", "category": "数据结构", "description": "队列操作、BFS应用", "difficulty_level": 2, "question_bank_mode": "academic"},
        {"name": "二叉树", "category": "数据结构", "description": "树的遍历、递归思想", "difficulty_level": 3, "question_bank_mode": "academic"},
        {"name": "动态规划", "category": "算法", "description": "状态转移、最优子结构", "difficulty_level": 4, "question_bank_mode": "academic"},
        {"name": "贪心算法", "category": "算法", "description": "贪心策略、局部最优", "difficulty_level": 3, "question_bank_mode": "academic"},
        {"name": "二分查找", "category": "算法", "description": "有序查找、分治思想", "difficulty_level": 3, "question_bank_mode": "academic"},
        {"name": "滑动窗口", "category": "算法", "description": "窗口技巧、子串问题", "difficulty_level": 3, "question_bank_mode": "academic"},
        {"name": "双指针", "category": "算法", "description": "指针技巧、空间优化", "difficulty_level": 2, "question_bank_mode": "academic"}
    ]
    
    knowledge_points = {}
    for kp_data in knowledge_points_data:
        kp = KnowledgePoint(**kp_data)
        db.session.add(kp)
        knowledge_points[kp_data["name"]] = kp
    
    db.session.flush()
    return knowledge_points

def import_leetcode_problems(knowledge_points):
    """导入经典LeetCode题目"""
    print("正在导入LeetCode题目...")
    
    leetcode_problems = [
        {
            "title": "两数之和",
            "content": """给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

示例 1：
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。

示例 2：
输入：nums = [3,2,4], target = 6
输出：[1,2]

提示：
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- 只会存在一个有效答案""",
            "difficulty": "easy",
            "knowledge_point": "哈希表",
            "correct_answer": """def twoSum(nums, target):
    hashmap = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hashmap:
            return [hashmap[complement], i]
        hashmap[num] = i
    return []""",
            "explanation": """使用哈希表优化查找过程：
1. 遍历数组，对于每个元素，计算其补数
2. 检查补数是否已在哈希表中
3. 如果在，返回两个索引；如果不在，将当前元素存入哈希表
时间复杂度：O(n)，空间复杂度：O(n)""",
            "estimated_time": 15,
            "test_cases": '[{"input": {"nums": [2,7,11,15], "target": 9}, "expected": [0,1]}, {"input": {"nums": [3,2,4], "target": 6}, "expected": [1,2]}]'
        },
        {
            "title": "两数相加",
            "content": """给你两个非空的链表，表示两个非负的整数。它们每位数字都是按照逆序的方式存储的，并且每个节点只能存储一位数字。

请你将两个数相加，并以相同形式返回一个表示和的链表。

示例 1：
输入：l1 = [2,4,3], l2 = [5,6,4]
输出：[7,0,8]
解释：342 + 465 = 807.

示例 2：
输入：l1 = [0], l2 = [0]
输出：[0]

提示：
- 每个链表中的节点数在范围 [1, 100] 内
- 0 <= Node.val <= 9""",
            "difficulty": "medium",
            "knowledge_point": "链表",
            "correct_answer": """def addTwoNumbers(l1, l2):
    dummy = ListNode(0)
    current = dummy
    carry = 0
    
    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        total = val1 + val2 + carry
        carry = total // 10
        digit = total % 10
        
        current.next = ListNode(digit)
        current = current.next
        
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    
    return dummy.next""",
            "explanation": """链表加法模拟：
1. 同时遍历两个链表，处理进位
2. 当前位 = (数字1 + 数字2 + 进位) % 10
3. 新进位 = (数字1 + 数字2 + 进位) // 10
4. 使用dummy节点简化操作""",
            "estimated_time": 25,
            "test_cases": '[{"input": {"l1": [2,4,3], "l2": [5,6,4]}, "expected": [7,0,8]}]'
        },
        {
            "title": "无重复字符的最长子串",
            "content": """给定一个字符串 s ，请你找出其中不含有重复字符的最长子串的长度。

示例 1:
输入: s = "abcabcbb"
输出: 3 
解释: 因为无重复字符的最长子串是 "abc"，所以其长度为 3。

示例 2:
输入: s = "bbbbb"
输出: 1
解释: 因为无重复字符的最长子串是 "b"，所以其长度为 1。

示例 3:
输入: s = "pwwkew"
输出: 3
解释: 因为无重复字符的最长子串是 "wke"，所以其长度为 3。

提示：
- 0 <= s.length <= 5 * 10^4
- s 由英文字母、数字、符号和空格组成""",
            "difficulty": "medium",
            "knowledge_point": "滑动窗口",
            "correct_answer": """def lengthOfLongestSubstring(s):
    char_map = {}
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        
        char_map[s[right]] = right
        max_length = max(max_length, right - left + 1)
    
    return max_length""",
            "explanation": """滑动窗口 + 哈希表：
1. 使用left和right指针维护窗口
2. 遇到重复字符时，移动left到重复字符的下一位
3. 用哈希表记录字符最后出现位置
时间复杂度：O(n)""",
            "estimated_time": 30,
            "test_cases": '[{"input": {"s": "abcabcbb"}, "expected": 3}, {"input": {"s": "bbbbb"}, "expected": 1}]'
        },
        {
            "title": "寻找两个正序数组的中位数",
            "content": """给定两个大小分别为 m 和 n 的正序（从小到大）数组 nums1 和 nums2。请你找出并返回这两个正序数组的中位数。

算法的时间复杂度应该为 O(log (m+n)) 。

示例 1：
输入：nums1 = [1,3], nums2 = [2]
输出：2.00000
解释：合并数组 = [1,2,3] ，中位数 2

示例 2：
输入：nums1 = [1,2], nums2 = [3,4]
输出：2.50000
解释：合并数组 = [1,2,3,4] ，中位数 (2 + 3) / 2 = 2.5

提示：
- nums1.length == m
- nums2.length == n
- 0 <= m <= 1000
- 0 <= n <= 1000
- 1 <= m + n <= 2000""",
            "difficulty": "hard",
            "knowledge_point": "二分查找",
            "correct_answer": """def findMedianSortedArrays(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    
    m, n = len(nums1), len(nums2)
    low, high = 0, m
    
    while low <= high:
        cut1 = (low + high) // 2
        cut2 = (m + n + 1) // 2 - cut1
        
        left1 = float('-inf') if cut1 == 0 else nums1[cut1 - 1]
        left2 = float('-inf') if cut2 == 0 else nums2[cut2 - 1]
        right1 = float('inf') if cut1 == m else nums1[cut1]
        right2 = float('inf') if cut2 == n else nums2[cut2]
        
        if left1 <= right2 and left2 <= right1:
            if (m + n) % 2 == 0:
                return (max(left1, left2) + min(right1, right2)) / 2
            else:
                return max(left1, left2)
        elif left1 > right2:
            high = cut1 - 1
        else:
            low = cut1 + 1
    
    return -1""",
            "explanation": """二分查找分割点：
1. 在较短数组上进行二分查找
2. 计算分割点使左右元素个数相等
3. 检查分割是否正确
4. 根据总长度奇偶性计算中位数
时间复杂度：O(log(min(m,n)))""",
            "estimated_time": 45,
            "test_cases": '[{"input": {"nums1": [1,3], "nums2": [2]}, "expected": 2.0}]'
        },
        {
            "title": "最长回文子串",
            "content": """给你一个字符串 s，找到 s 中最长的回文子串。

示例 1：
输入：s = "babad"
输出："bab"
解释："aba" 同样是符合题意的答案。

示例 2：
输入：s = "cbbd"
输出："bb"

提示：
- 1 <= s.length <= 1000
- s 仅由数字和英文字母组成""",
            "difficulty": "medium",
            "knowledge_point": "字符串",
            "correct_answer": """def longestPalindrome(s):
    if not s:
        return ""
    
    start = 0
    max_len = 1
    
    def expand_around_center(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1
    
    for i in range(len(s)):
        len1 = expand_around_center(i, i)  # 奇数长度
        len2 = expand_around_center(i, i + 1)  # 偶数长度
        
        current_max = max(len1, len2)
        if current_max > max_len:
            max_len = current_max
            start = i - (current_max - 1) // 2
    
    return s[start:start + max_len]""",
            "explanation": """中心扩展法：
1. 遍历每个可能的回文中心
2. 从中心向两边扩展检查回文
3. 考虑奇数和偶数长度的回文
4. 记录最长回文的位置和长度
时间复杂度：O(n²)""",
            "estimated_time": 35,
            "test_cases": '[{"input": {"s": "babad"}, "expected": "bab"}]'
        },
        {
            "title": "整数反转",
            "content": """给你一个 32 位的有符号整数 x ，返回将 x 中的数字部分反转后的结果。

如果反转后整数超过 32 位的有符号整数的范围 [−2^31,  2^31 − 1] ，就返回 0。

示例 1：
输入：x = 123
输出：321

示例 2：
输入：x = -123
输出：-321

示例 3：
输入：x = 120
输出：21

提示：
-2^31 <= x <= 2^31 - 1""",
            "difficulty": "easy",
            "knowledge_point": "数组",
            "correct_answer": """def reverse(x):
    INT_MAX = 2**31 - 1
    INT_MIN = -2**31
    
    result = 0
    while x != 0:
        digit = x % 10 if x > 0 else -((-x) % 10)
        x = x // 10 if x > 0 else -((-x) // 10)
        
        # 检查溢出
        if result > INT_MAX // 10 or (result == INT_MAX // 10 and digit > 7):
            return 0
        if result < INT_MIN // 10 or (result == INT_MIN // 10 and digit < -8):
            return 0
        
        result = result * 10 + digit
    
    return result""",
            "explanation": """数字反转与溢出检查：
1. 逐位提取数字并重新组合
2. 每次操作前检查是否会溢出
3. 处理正负数的边界情况
时间复杂度：O(log x)""",
            "estimated_time": 20,
            "test_cases": '[{"input": {"x": 123}, "expected": 321}, {"input": {"x": -123}, "expected": -321}]'
        },
        {
            "title": "回文数",
            "content": """给你一个整数 x ，如果 x 是一个回文整数，返回 true ；否则，返回 false 。

回文数是指正序（从左向右）和倒序（从右向左）读都是一样的整数。

例如，121 是回文，而 123 不是。

示例 1：
输入：x = 121
输出：true

示例 2：
输入：x = -121
输出：false
解释：从左向右读, 为 -121 。 从右向左读, 为 121- 。因此它不是一个回文数。

示例 3：
输入：x = 10
输出：false
解释：从右向左读, 为 01 。因此它不是一个回文数。

提示：
-2^31 <= x <= 2^31 - 1""",
            "difficulty": "easy",
            "knowledge_point": "数组",
            "correct_answer": """def isPalindrome(x):
    # 负数和以0结尾的正数（除了0本身）不是回文数
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    
    reversed_half = 0
    while x > reversed_half:
        reversed_half = reversed_half * 10 + x % 10
        x //= 10
    
    # 奇数位数：x == reversed_half // 10
    # 偶数位数：x == reversed_half
    return x == reversed_half or x == reversed_half // 10""",
            "explanation": """只反转一半数字的优化方法：
1. 排除负数和末尾为0的数（除了0）
2. 反转后半部分数字
3. 比较前半部分和反转的后半部分
时间复杂度：O(log x)，空间复杂度：O(1)""",
            "estimated_time": 15,
            "test_cases": '[{"input": {"x": 121}, "expected": true}, {"input": {"x": -121}, "expected": false}]'
        },
        {
            "title": "罗马数字转整数",
            "content": """罗马数字包含以下七种字符: I， V， X， L，C，D 和 M。

字符          数值
I             1
V             5
X             10
L             50
C             100
D             500
M             1000

例如， 罗马数字 2 写做 II ，即为两个并列的 1 。12 写做 XII ，即为 X + II 。 27 写做  XXVII, 即为 XX + V + II 。

通常情况下，罗马数字中小的数字在大的数字的右边。但也存在特例，例如 4 不写做 IIII，而是 IV。数字 1 在数字 5 的左边，所表示的数等于大数 5 减小数 1 得到的数值 4 。同样地，数字 9 表示为 IX。这个特殊的规则只适用于以下六种情况：

I 可以放在 V (5) 和 X (10) 的左边，来表示 4 和 9。
X 可以放在 L (50) 和 C (100) 的左边，来表示 40 和 90。 
C 可以放在 D (500) 和 M (1000) 的左边，来表示 400 和 900。

给定一个罗马数字，将其转换成整数。

示例 1:
输入: s = "III"
输出: 3

示例 2:
输入: s = "IV"
输出: 4

示例 3:
输入: s = "IX"
输出: 9

示例 4:
输入: s = "LVIII"
输出: 58
解释: L = 50, V= 5, III = 3.

示例 5:
输入: s = "MCMXC"
输出: 1994
解释: M = 1000, CM = 900, XC = 90.""",
            "difficulty": "easy",
            "knowledge_point": "哈希表",
            "correct_answer": """def romanToInt(s):
    roman_values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    
    total = 0
    prev_value = 0
    
    for char in reversed(s):
        value = roman_values[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value
    
    return total""",
            "explanation": """从右到左遍历的巧妙方法：
1. 如果当前字符的值小于前一个字符的值，就减去当前值（减法情况）
2. 否则就加上当前值（正常情况）
3. 使用哈希表存储字符对应的数值
时间复杂度：O(n)""",
            "estimated_time": 20,
            "test_cases": '[{"input": {"s": "III"}, "expected": 3}, {"input": {"s": "IV"}, "expected": 4}]'
        }
    ]
    
    imported_count = 0
    for problem_data in leetcode_problems:
        knowledge_point = knowledge_points.get(problem_data["knowledge_point"])
        
        question = Question(
            title=problem_data["title"],
            content=problem_data["content"],
            question_type='coding',
            difficulty=problem_data["difficulty"],
            estimated_time=problem_data["estimated_time"],
            knowledge_point_id=knowledge_point.id if knowledge_point else None,
            correct_answer=problem_data["correct_answer"],
            explanation=problem_data["explanation"],
            programming_language='python',
            test_cases=problem_data["test_cases"],
            question_bank_mode='academic',
            created_at=datetime.utcnow()
        )
        
        db.session.add(question)
        imported_count += 1
        print(f"  ✅ 导入: {problem_data['title']} ({problem_data['difficulty']})")
    
    db.session.commit()
    print(f"✅ 成功导入 {imported_count} 道LeetCode经典题目！")

def main():
    """主函数"""
    print("=== LeetCode题库替换工具 ===\n")
    
    response = input("确定要用LeetCode题目替换现有的模拟数据吗？(y/n): ").lower()
    if response != 'y':
        print("操作已取消")
        return
    
    with app.app_context():
        # 1. 清除现有数据
        clear_all_questions()
        
        # 2. 创建LeetCode知识点
        knowledge_points = create_leetcode_knowledge_points()
        
        # 3. 导入LeetCode题目
        import_leetcode_problems(knowledge_points)
        
        print("\n=== 🎉 替换完成 ===")
        print("现在系统中包含了8道LeetCode经典题目：")
        print("- 两数之和 (简单)")
        print("- 两数相加 (中等)")  
        print("- 无重复字符的最长子串 (中等)")
        print("- 寻找两个正序数组的中位数 (困难)")
        print("- 最长回文子串 (中等)")
        print("- 整数反转 (简单)")
        print("- 回文数 (简单)")
        print("- 罗马数字转整数 (简单)")
        print("\n请重启应用体验真实的LeetCode题目！")

if __name__ == "__main__":
    main()
