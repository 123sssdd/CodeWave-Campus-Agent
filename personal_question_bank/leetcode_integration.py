#!/usr/bin/env python3
"""
LeetCode题库集成工具
集成真实的LeetCode题目数据到系统中
"""

import json
import requests
from datetime import datetime
from models import db, Question, KnowledgePoint

class LeetCodeIntegration:
    def __init__(self):
        self.base_url = "https://leetcode.com/api/problems/all/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_problems_list(self):
        """获取LeetCode题目列表"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                data = response.json()
                return data.get('stat_status_pairs', [])
            else:
                print(f"获取题目列表失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"网络请求失败: {e}")
            return self.get_offline_problems()
    
    def get_offline_problems(self):
        """获取离线的LeetCode题目数据"""
        # 这里提供一些经典的LeetCode题目作为示例
        return [
            {
                "stat": {
                    "question_id": 1,
                    "question__title": "Two Sum",
                    "question__title_slug": "two-sum",
                    "question__article": "",
                    "question__hide": False,
                    "total_acs": 3000000,
                    "total_submitted": 7000000,
                    "frontend_question_id": 1,
                    "is_new_question": False
                },
                "status": None,
                "difficulty": {
                    "level": 1
                },
                "paid_only": False,
                "is_favor": False,
                "frequency": 0,
                "progress": 0
            },
            {
                "stat": {
                    "question_id": 2,
                    "question__title": "Add Two Numbers",
                    "question__title_slug": "add-two-numbers",
                    "question__article": "",
                    "question__hide": False,
                    "total_acs": 1500000,
                    "total_submitted": 4000000,
                    "frontend_question_id": 2,
                    "is_new_question": False
                },
                "status": None,
                "difficulty": {
                    "level": 2
                },
                "paid_only": False,
                "is_favor": False,
                "frequency": 0,
                "progress": 0
            },
            {
                "stat": {
                    "question_id": 3,
                    "question__title": "Longest Substring Without Repeating Characters",
                    "question__title_slug": "longest-substring-without-repeating-characters",
                    "question__article": "",
                    "question__hide": False,
                    "total_acs": 2000000,
                    "total_submitted": 6000000,
                    "frontend_question_id": 3,
                    "is_new_question": False
                },
                "status": None,
                "difficulty": {
                    "level": 2
                },
                "paid_only": False,
                "is_favor": False,
                "frequency": 0,
                "progress": 0
            },
            {
                "stat": {
                    "question_id": 4,
                    "question__title": "Median of Two Sorted Arrays",
                    "question__title_slug": "median-of-two-sorted-arrays",
                    "question__article": "",
                    "question__hide": False,
                    "total_acs": 800000,
                    "total_submitted": 3000000,
                    "frontend_question_id": 4,
                    "is_new_question": False
                },
                "status": None,
                "difficulty": {
                    "level": 3
                },
                "paid_only": False,
                "is_favor": False,
                "frequency": 0,
                "progress": 0
            },
            {
                "stat": {
                    "question_id": 5,
                    "question__title": "Longest Palindromic Substring",
                    "question__title_slug": "longest-palindromic-substring",
                    "question__article": "",
                    "question__hide": False,
                    "total_acs": 1200000,
                    "total_submitted": 3500000,
                    "frontend_question_id": 5,
                    "is_new_question": False
                },
                "status": None,
                "difficulty": {
                    "level": 2
                },
                "paid_only": False,
                "is_favor": False,
                "frequency": 0,
                "progress": 0
            }
        ]
    
    def get_problem_details(self):
        """获取题目详情"""
        # 由于LeetCode API限制，这里提供详细的题目内容
        problem_details = {
            "two-sum": {
                "content": """给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

你可以按任意顺序返回答案。

示例 1：
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。

示例 2：
输入：nums = [3,2,4], target = 6
输出：[1,2]

示例 3：
输入：nums = [3,3], target = 6
输出：[0,1]

提示：
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- 只会存在一个有效答案""",
                "correct_answer": """# 解法一：哈希表
def twoSum(nums, target):
    hashmap = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hashmap:
            return [hashmap[complement], i]
        hashmap[num] = i
    return []

# 时间复杂度：O(n)
# 空间复杂度：O(n)""",
                "explanation": """这道题可以使用哈希表来解决：

1. 遍历数组，对于每个元素，计算其补数（target - 当前元素）
2. 检查补数是否已经在哈希表中
3. 如果在，返回两个元素的索引
4. 如果不在，将当前元素和索引存入哈希表

关键思路：用空间换时间，将查找时间从O(n)降到O(1)"""
            },
            "add-two-numbers": {
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
- 0 <= Node.val <= 9
- 题目数据保证列表表示的数字不含前导零""",
                "correct_answer": """# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def addTwoNumbers(l1, l2):
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
                "explanation": """链表加法的核心思路：

1. 同时遍历两个链表，模拟数字相加过程
2. 处理进位：当前位 = (数字1 + 数字2 + 进位) % 10
3. 新的进位 = (数字1 + 数字2 + 进位) // 10
4. 注意边界情况：链表长度不同、最后的进位

技巧：使用dummy节点简化链表操作"""
            },
            "longest-substring-without-repeating-characters": {
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
                "explanation": """滑动窗口 + 哈希表解法：

1. 使用两个指针left和right构成滑动窗口
2. right指针向右扩展窗口，left指针收缩窗口
3. 当遇到重复字符时，移动left到重复字符的下一个位置
4. 用哈希表记录每个字符最后出现的位置

时间复杂度：O(n)，空间复杂度：O(min(m,n))"""
            },
            "median-of-two-sorted-arrays": {
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
                "explanation": """二分查找解法：

1. 确保nums1是较短的数组，减少搜索空间
2. 在nums1上进行二分查找分割点
3. 根据分割点计算nums2的分割点，使得左右两部分元素个数相等
4. 检查分割是否正确：左边最大值 <= 右边最小值
5. 根据总长度奇偶性计算中位数

关键思路：不需要真正合并数组，只需要找到正确的分割点"""
            },
            "longest-palindromic-substring": {
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
        # 奇数长度的回文
        len1 = expand_around_center(i, i)
        # 偶数长度的回文
        len2 = expand_around_center(i, i + 1)
        
        current_max = max(len1, len2)
        if current_max > max_len:
            max_len = current_max
            start = i - (current_max - 1) // 2
    
    return s[start:start + max_len]""",
                "explanation": """中心扩展法：

1. 遍历每个可能的回文中心
2. 对于每个中心，向两边扩展，检查是否构成回文
3. 需要考虑奇数和偶数长度的回文
4. 记录最长回文的起始位置和长度

时间复杂度：O(n²)，空间复杂度：O(1)
比动态规划方法更省空间，是最常用的解法"""
            }
        }
        return problem_details
    
    def difficulty_map(self, level):
        """映射难度级别"""
        mapping = {1: "easy", 2: "medium", 3: "hard"}
        return mapping.get(level, "medium")
    
    def create_knowledge_points(self):
        """创建LeetCode相关的知识点"""
        leetcode_knowledge_points = [
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
        
        knowledge_points = []
        for kp_data in leetcode_knowledge_points:
            # 检查是否已存在
            existing = KnowledgePoint.query.filter_by(name=kp_data["name"], question_bank_mode="academic").first()
            if not existing:
                kp = KnowledgePoint(**kp_data)
                db.session.add(kp)
                knowledge_points.append(kp)
            else:
                knowledge_points.append(existing)
        
        db.session.flush()
        return knowledge_points
    
    def get_knowledge_point_by_problem(self, problem_slug):
        """根据题目类型获取知识点"""
        knowledge_map = {
            "two-sum": "哈希表",
            "add-two-numbers": "链表", 
            "longest-substring-without-repeating-characters": "滑动窗口",
            "median-of-two-sorted-arrays": "二分查找",
            "longest-palindromic-substring": "字符串"
        }
        
        kp_name = knowledge_map.get(problem_slug, "数组")
        return KnowledgePoint.query.filter_by(name=kp_name, question_bank_mode="academic").first()
    
    def import_problems(self, limit=50):
        """导入LeetCode题目"""
        print("正在创建LeetCode知识点...")
        knowledge_points = self.create_knowledge_points()
        
        print("正在获取LeetCode题目列表...")
        problems = self.fetch_problems_list()
        
        if not problems:
            print("无法获取题目列表，请检查网络连接")
            return
        
        problem_details = self.get_problem_details()
        imported_count = 0
        
        print(f"开始导入题目，限制数量: {limit}")
        
        for problem_data in problems[:limit]:
            if imported_count >= limit:
                break
                
            stat = problem_data.get('stat', {})
            difficulty = problem_data.get('difficulty', {})
            
            title = stat.get('question__title', '')
            title_slug = stat.get('question__title_slug', '')
            question_id = stat.get('frontend_question_id', 0)
            
            # 跳过付费题目
            if problem_data.get('paid_only', False):
                continue
            
            # 检查题目是否已存在
            existing = Question.query.filter_by(
                external_source='leetcode',
                external_id=str(question_id)
            ).first()
            
            if existing:
                print(f"题目 {title} 已存在，跳过")
                continue
            
            # 获取题目详情
            detail = problem_details.get(title_slug, {})
            content = detail.get('content', f'LeetCode第{question_id}题：{title}')
            correct_answer = detail.get('correct_answer', '请参考LeetCode官方解答')
            explanation = detail.get('explanation', '请查看详细解题思路')
            
            # 获取对应的知识点
            knowledge_point = self.get_knowledge_point_by_problem(title_slug)
            if not knowledge_point and knowledge_points:
                knowledge_point = knowledge_points[0]  # 默认使用第一个知识点
            
            # 创建题目
            question = Question(
                title=title,
                content=content,
                question_type='coding',
                difficulty=self.difficulty_map(difficulty.get('level', 2)),
                estimated_time=self.estimate_time(difficulty.get('level', 2)),
                knowledge_point_id=knowledge_point.id if knowledge_point else None,
                correct_answer=correct_answer,
                explanation=explanation,
                programming_language='python',
                test_cases=self.generate_test_cases(title_slug),
                external_source='leetcode',
                external_id=str(question_id),
                question_bank_mode='academic',
                created_at=datetime.utcnow()
            )
            
            db.session.add(question)
            imported_count += 1
            print(f"导入题目: {title} (难度: {question.difficulty})")
        
        try:
            db.session.commit()
            print(f"成功导入 {imported_count} 道LeetCode题目！")
        except Exception as e:
            db.session.rollback()
            print(f"导入失败: {e}")
    
    def estimate_time(self, difficulty_level):
        """估算题目完成时间"""
        time_map = {1: 15, 2: 25, 3: 45}
        return time_map.get(difficulty_level, 25)
    
    def generate_test_cases(self, problem_slug):
        """生成测试用例"""
        test_cases_map = {
            "two-sum": '[{"input": {"nums": [2,7,11,15], "target": 9}, "expected": [0,1]}, {"input": {"nums": [3,2,4], "target": 6}, "expected": [1,2]}]',
            "add-two-numbers": '[{"input": {"l1": [2,4,3], "l2": [5,6,4]}, "expected": [7,0,8]}]',
            "longest-substring-without-repeating-characters": '[{"input": {"s": "abcabcbb"}, "expected": 3}, {"input": {"s": "bbbbb"}, "expected": 1}]',
            "median-of-two-sorted-arrays": '[{"input": {"nums1": [1,3], "nums2": [2]}, "expected": 2.0}]',
            "longest-palindromic-substring": '[{"input": {"s": "babad"}, "expected": "bab"}]'
        }
        return test_cases_map.get(problem_slug, '[]')

def clear_existing_data():
    """清除现有的模拟数据"""
    print("正在清除现有数据...")
    
    # 删除学习记录
    from models import LearningRecord, UserKnowledgeStats, WrongQuestion, SimilarQuestion
    
    db.session.query(SimilarQuestion).delete()
    db.session.query(WrongQuestion).delete() 
    db.session.query(LearningRecord).delete()
    db.session.query(UserKnowledgeStats).delete()
    
    # 删除现有题目（但保留用户数据）
    Question.query.filter_by(question_bank_mode='academic').delete()
    
    # 删除现有知识点
    KnowledgePoint.query.filter_by(question_bank_mode='academic').delete()
    
    db.session.commit()
    print("数据清除完成")

def main():
    """主函数"""
    print("=== LeetCode题库集成工具 ===")
    
    # 询问是否清除现有数据
    response = input("是否清除现有的模拟数据？(y/n): ").lower()
    if response == 'y':
        clear_existing_data()
    
    # 导入LeetCode题目
    leetcode = LeetCodeIntegration()
    
    # 询问导入数量
    try:
        limit = int(input("请输入要导入的题目数量 (建议50以内): ") or "20")
    except ValueError:
        limit = 20
    
    leetcode.import_problems(limit)
    
    print("\n=== 集成完成 ===")
    print("现在您可以重启应用，体验真实的LeetCode题目！")

if __name__ == "__main__":
    # 需要在Flask应用上下文中运行
    from app import app
    with app.app_context():
        main()
