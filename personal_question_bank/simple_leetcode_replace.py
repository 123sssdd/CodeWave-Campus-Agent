#!/usr/bin/env python3
"""
简化版LeetCode题目替换脚本
只使用现有数据库字段，不添加新字段
"""

from app import app, db
from models import Question, KnowledgePoint, LearningRecord, UserKnowledgeStats, WrongQuestion, SimilarQuestion
from datetime import datetime

def clear_and_replace():
    """清除并替换为LeetCode题目"""
    print("=== 快速替换为LeetCode题目 ===\n")
    
    with app.app_context():
        # 1. 清除所有相关数据
        print("正在清除现有数据...")
        db.session.query(SimilarQuestion).delete()
        db.session.query(WrongQuestion).delete()
        db.session.query(LearningRecord).delete()
        db.session.query(UserKnowledgeStats).delete()
        db.session.query(Question).delete()
        db.session.query(KnowledgePoint).delete()
        db.session.commit()
        print("✅ 现有数据已清除")
        
        # 2. 创建LeetCode知识点
        print("\n正在创建LeetCode知识点...")
        knowledge_points_data = [
            {"name": "数组", "category": "数据结构", "description": "数组操作、双指针技巧", "difficulty_level": 1, "question_bank_mode": "academic"},
            {"name": "链表", "category": "数据结构", "description": "链表操作、快慢指针", "difficulty_level": 2, "question_bank_mode": "academic"},
            {"name": "字符串", "category": "数据结构", "description": "字符串处理、模式匹配", "difficulty_level": 2, "question_bank_mode": "academic"},
            {"name": "哈希表", "category": "数据结构", "description": "哈希表应用、查找优化", "difficulty_level": 2, "question_bank_mode": "academic"},
            {"name": "滑动窗口", "category": "算法", "description": "窗口技巧、子串问题", "difficulty_level": 3, "question_bank_mode": "academic"},
            {"name": "二分查找", "category": "算法", "description": "有序查找、分治思想", "difficulty_level": 3, "question_bank_mode": "academic"},
        ]
        
        knowledge_points = {}
        for kp_data in knowledge_points_data:
            kp = KnowledgePoint(**kp_data)
            db.session.add(kp)
            knowledge_points[kp_data["name"]] = kp
        
        db.session.flush()
        print("✅ 知识点创建完成")
        
        # 3. 创建LeetCode题目（只使用现有字段）
        print("\n正在导入LeetCode经典题目...")
        
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
- 只会存在一个有效答案

进阶：你可以想出一个时间复杂度小于 O(n²) 的算法吗？""",
                "difficulty": "easy",
                "knowledge_point": "哈希表",
                "correct_answer": """def twoSum(nums, target):
    \"\"\"
    :type nums: List[int]
    :type target: int
    :rtype: List[int]
    \"\"\"
    hashmap = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hashmap:
            return [hashmap[complement], i]
        hashmap[num] = i
    return []

# 时间复杂度：O(n)
# 空间复杂度：O(n)""",
                "explanation": """**解题思路：哈希表**

1. **暴力解法**：两层循环遍历所有组合，时间复杂度O(n²)

2. **哈希表优化**：
   - 遍历数组，对于每个元素num，计算其补数complement = target - num
   - 检查complement是否已在哈希表中
   - 如果在，返回两个元素的索引
   - 如果不在，将当前元素和索引存入哈希表

**关键优化**：用空间换时间，将查找时间从O(n)降到O(1)

**注意事项**：
- 题目保证有且仅有一个答案
- 同一个元素不能使用两次
- 可以按任意顺序返回答案""",
                "estimated_time": 15,
                "test_cases": '[{"input": {"nums": [2,7,11,15], "target": 9}, "expected": [0,1]}, {"input": {"nums": [3,2,4], "target": 6}, "expected": [1,2]}, {"input": {"nums": [3,3], "target": 6}, "expected": [0,1]}]',
                "external_platform": "leetcode",
                "external_id": "1"
            },
            {
                "title": "两数相加",
                "content": """给你两个非空的链表，表示两个非负的整数。它们每位数字都是按照逆序的方式存储的，并且每个节点只能存储一位数字。

请你将两个数相加，并以相同形式返回一个表示和的链表。

你可以假设除了数字 0 之外，这两个数都不会以 0 开头。

示例 1：
输入：l1 = [2,4,3], l2 = [5,6,4]
输出：[7,0,8]
解释：342 + 465 = 807.

示例 2：
输入：l1 = [0], l2 = [0]
输出：[0]

示例 3：
输入：l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
输出：[8,9,9,9,0,0,0,1]

提示：
- 每个链表中的节点数在范围 [1, 100] 内
- 0 <= Node.val <= 9""",
                "difficulty": "medium",
                "knowledge_point": "链表",
                "correct_answer": """# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def addTwoNumbers(l1, l2):
    \"\"\"
    :type l1: ListNode
    :type l2: ListNode
    :rtype: ListNode
    \"\"\"
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
    
    return dummy.next

# 时间复杂度：O(max(m,n))
# 空间复杂度：O(max(m,n))""",
                "explanation": """**解题思路：链表加法模拟**

1. **问题分析**：
   - 链表按逆序存储，正好符合加法运算从低位到高位的顺序
   - 需要处理进位carry
   - 两个链表长度可能不同

2. **算法步骤**：
   - 使用dummy节点简化链表操作
   - 同时遍历两个链表，逐位相加
   - 当前位 = (数字1 + 数字2 + 进位) % 10
   - 新进位 = (数字1 + 数字2 + 进位) // 10
   - 继续直到两个链表都遍历完且无进位

3. **边界情况**：
   - 链表长度不同
   - 最后仍有进位
   - 其中一个链表为空

**技巧**：使用dummy节点可以避免特殊处理头节点""",
                "estimated_time": 25,
                "test_cases": '[{"input": {"l1": [2,4,3], "l2": [5,6,4]}, "expected": [7,0,8]}, {"input": {"l1": [0], "l2": [0]}, "expected": [0]}, {"input": {"l1": [9,9,9,9,9,9,9], "l2": [9,9,9,9]}, "expected": [8,9,9,9,0,0,0,1]}]',
                "external_platform": "leetcode",
                "external_id": "2"
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
请注意，你的答案必须是子串的长度，"pwke" 是一个子序列，不是子串。

提示：
- 0 <= s.length <= 5 * 10^4
- s 由英文字母、数字、符号和空格组成""",
                "difficulty": "medium",
                "knowledge_point": "滑动窗口",
                "correct_answer": """def lengthOfLongestSubstring(s):
    \"\"\"
    :type s: str
    :rtype: int
    \"\"\"
    char_map = {}
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        
        char_map[s[right]] = right
        max_length = max(max_length, right - left + 1)
    
    return max_length

# 时间复杂度：O(n)
# 空间复杂度：O(min(m,n))，m是字符集大小""",
                "explanation": """**解题思路：滑动窗口 + 哈希表**

1. **暴力解法**：检查所有子串，时间复杂度O(n³)

2. **滑动窗口优化**：
   - 使用两个指针left和right构成滑动窗口
   - right指针向右扩展窗口
   - 当遇到重复字符时，移动left指针到重复字符的下一个位置
   - 用哈希表记录每个字符最后出现的位置

3. **算法流程**：
   - 初始化left=0, max_length=0, char_map={}
   - 遍历字符串，right从0到n-1
   - 如果s[right]在窗口内重复，更新left
   - 更新字符位置和最大长度

**关键点**：
- 窗口内无重复字符
- 哈希表优化字符查找
- 动态调整窗口大小""",
                "estimated_time": 30,
                "test_cases": '[{"input": {"s": "abcabcbb"}, "expected": 3}, {"input": {"s": "bbbbb"}, "expected": 1}, {"input": {"s": "pwwkew"}, "expected": 3}, {"input": {"s": ""}, "expected": 0}]',
                "external_platform": "leetcode",
                "external_id": "3"
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
- 1 <= m + n <= 2000
- -10^6 <= nums1[i], nums2[i] <= 10^6""",
                "difficulty": "hard",
                "knowledge_point": "二分查找",
                "correct_answer": """def findMedianSortedArrays(nums1, nums2):
    \"\"\"
    :type nums1: List[int]
    :type nums2: List[int]
    :rtype: float
    \"\"\"
    # 确保nums1是较短的数组
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
    
    return -1

# 时间复杂度：O(log(min(m,n)))
# 空间复杂度：O(1)""",
                "explanation": """**解题思路：二分查找分割点**

1. **暴力解法**：合并两个数组再找中位数，时间复杂度O(m+n)

2. **二分查找优化**：
   - 不需要真正合并数组，只需找到正确的分割点
   - 在较短数组上进行二分查找，减少搜索空间
   - 分割后左边元素个数 = (m+n+1)//2

3. **算法原理**：
   - 将两个数组分割成左右两部分
   - 左边最大值 <= 右边最小值
   - 左边元素个数 = 右边元素个数（或相差1）

4. **检查条件**：
   - left1 <= right2 且 left2 <= right1
   - 满足条件时找到答案
   - 不满足时调整二分边界

**难点**：
- 边界处理（数组为空的情况）
- 奇偶长度的中位数计算
- 二分查找的边界调整""",
                "estimated_time": 45,
                "test_cases": '[{"input": {"nums1": [1,3], "nums2": [2]}, "expected": 2.0}, {"input": {"nums1": [1,2], "nums2": [3,4]}, "expected": 2.5}, {"input": {"nums1": [0,0], "nums2": [0,0]}, "expected": 0.0}]',
                "external_platform": "leetcode",
                "external_id": "4"
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
    \"\"\"
    :type s: str
    :rtype: str
    \"\"\"
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
        # 奇数长度的回文
        len1 = expand_around_center(i, i)
        # 偶数长度的回文
        len2 = expand_around_center(i, i + 1)
        
        current_max = max(len1, len2)
        if current_max > max_len:
            max_len = current_max
            start = i - (current_max - 1) // 2
    
    return s[start:start + max_len]

# 时间复杂度：O(n²)
# 空间复杂度：O(1)""",
                "explanation": """**解题思路：中心扩展法**

1. **暴力解法**：检查所有子串是否为回文，时间复杂度O(n³)

2. **动态规划**：dp[i][j]表示s[i:j+1]是否为回文，时间O(n²)，空间O(n²)

3. **中心扩展法**（推荐）：
   - 遍历每个可能的回文中心
   - 从中心向两边扩展，检查是否构成回文
   - 需要考虑奇数和偶数长度的回文

4. **算法流程**：
   - 对每个位置i，分别以i为中心和以i,i+1为中心扩展
   - 记录最长回文的起始位置和长度
   - 返回对应的子串

**优化点**：
- 只需O(1)的额外空间
- 每个中心最多扩展n次
- 比动态规划更省空间

**注意**：回文有奇数长度（如"aba"）和偶数长度（如"abba"）两种情况""",
                "estimated_time": 35,
                "test_cases": '[{"input": {"s": "babad"}, "expected": "bab"}, {"input": {"s": "cbbd"}, "expected": "bb"}, {"input": {"s": "a"}, "expected": "a"}, {"input": {"s": "ac"}, "expected": "a"}]',
                "external_platform": "leetcode",
                "external_id": "5"
            },
            {
                "title": "整数反转",
                "content": """给你一个 32 位的有符号整数 x ，返回将 x 中的数字部分反转后的结果。

如果反转后整数超过 32 位的有符号整数的范围 [−2³¹,  2³¹ − 1] ，就返回 0。

假设环境不允许存储 64 位整数（有符号或无符号）。

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
-2³¹ <= x <= 2³¹ - 1""",
                "difficulty": "easy",
                "knowledge_point": "数组",
                "correct_answer": """def reverse(x):
    \"\"\"
    :type x: int
    :rtype: int
    \"\"\"
    INT_MAX = 2**31 - 1
    INT_MIN = -2**31
    
    result = 0
    while x != 0:
        # 提取最后一位数字
        if x > 0:
            digit = x % 10
            x //= 10
        else:
            digit = -((-x) % 10)
            x = -((-x) // 10)
        
        # 检查溢出
        if result > INT_MAX // 10 or (result == INT_MAX // 10 and digit > 7):
            return 0
        if result < INT_MIN // 10 or (result == INT_MIN // 10 and digit < -8):
            return 0
        
        result = result * 10 + digit
    
    return result

# 时间复杂度：O(log x)
# 空间复杂度：O(1)""",
                "explanation": """**解题思路：数字反转与溢出检查**

1. **基本思路**：
   - 逐位提取数字：digit = x % 10
   - 重新组合：result = result * 10 + digit
   - 更新x：x //= 10

2. **处理负数**：
   - Python的取模和整除对负数处理特殊
   - 需要特别处理负数的情况

3. **溢出检查**：
   - 32位整数范围：[-2³¹, 2³¹-1]
   - 在每次操作前检查是否会溢出
   - 如果result * 10 + digit会溢出，提前返回0

4. **边界情况**：
   - x = 0：直接返回0
   - 反转后超出范围：返回0
   - 负数：保持符号不变

**关键点**：
- 不能使用64位整数存储中间结果
- 每次操作前都要检查溢出
- 正确处理正负数的取模和整除""",
                "estimated_time": 20,
                "test_cases": '[{"input": {"x": 123}, "expected": 321}, {"input": {"x": -123}, "expected": -321}, {"input": {"x": 120}, "expected": 21}, {"input": {"x": 0}, "expected": 0}]',
                "external_platform": "leetcode",
                "external_id": "7"
            }
        ]
        
        imported_count = 0
        for problem_data in leetcode_problems:
            knowledge_point = knowledge_points.get(problem_data["knowledge_point"])
            
            # 只使用现有数据库字段创建Question对象
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
                external_platform=problem_data["external_platform"],
                external_id=problem_data["external_id"],
                question_bank_mode='academic',
                created_at=datetime.utcnow()
            )
            
            db.session.add(question)
            imported_count += 1
            print(f"  ✅ 导入: {problem_data['title']} ({problem_data['difficulty']})")
        
        db.session.commit()
        print(f"\n✅ 成功导入 {imported_count} 道LeetCode经典题目！")
        
        print("\n=== 🎉 LeetCode题库集成完成 ===")
        print("现在系统包含以下LeetCode经典题目：")
        print("📚 **简单题目**：")
        print("  • 两数之和 - 哈希表基础应用")
        print("  • 整数反转 - 数字操作与溢出处理")
        print("\n📚 **中等题目**：")
        print("  • 两数相加 - 链表操作")
        print("  • 无重复字符的最长子串 - 滑动窗口")
        print("  • 最长回文子串 - 中心扩展法")
        print("\n📚 **困难题目**：")
        print("  • 寻找两个正序数组的中位数 - 二分查找")
        print("\n🔧 **改进内容**：")
        print("  ✅ 真实LeetCode题目和解答")
        print("  ✅ 详细的解题思路和复杂度分析")
        print("  ✅ 完整的测试用例")
        print("  ✅ 知识点分类和难度标记")
        print("  ✅ 支持举一反三功能")
        
        print(f"\n🚀 请重启Flask应用来体验新的LeetCode题库！")

if __name__ == "__main__":
    clear_and_replace()
