"""
外部平台接口模块

注意：此模块中的代码执行功能已废弃！
现在使用CodePen在线编辑器替代本地代码执行。

保留此文件仅用于：
1. LeetCode题目获取功能
2. 其他外部平台集成
3. 向后兼容性
"""

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import base64

@dataclass
class CodeExecutionResult:
    """代码执行结果"""
    success: bool
    output: str
    error: str = ""
    execution_time: float = 0.0
    memory_usage: int = 0
    test_cases_passed: int = 0
    total_test_cases: int = 0

class OnlineJudgeInterface:
    """在线评判系统接口基类"""
    
    def submit_code(self, code: str, language: str, problem_id: str) -> CodeExecutionResult:
        raise NotImplementedError
    
    def get_problem_details(self, problem_id: str) -> Dict:
        raise NotImplementedError
    
    def run_code(self, code: str, language: str, test_cases: List[Dict]) -> CodeExecutionResult:
        raise NotImplementedError

class JudgeZeroAPI(OnlineJudgeInterface):
    """Judge0 API集成 - 免费的在线代码执行平台"""
    
    def __init__(self, api_url: str = "https://judge0-ce.p.rapidapi.com"):
        self.api_url = api_url
        self.language_map = {
            'python': 71,    # Python 3.8.1
            'java': 62,      # Java (OpenJDK 13.0.1)
            'cpp': 54,       # C++ (GCC 9.2.0)
            'c': 50,         # C (GCC 9.2.0)
            'javascript': 63, # JavaScript (Node.js 12.14.0)
            'go': 60,        # Go (1.13.5)
            'rust': 73,      # Rust (1.40.0)
            'csharp': 51     # C# (Mono 6.6.0.161)
        }
    
    def submit_code(self, code: str, language: str, problem_id: str = None) -> CodeExecutionResult:
        """提交代码执行"""
        if language not in self.language_map:
            return CodeExecutionResult(
                success=False,
                output="",
                error=f"不支持的编程语言: {language}"
            )
        
        # 准备提交数据
        submission_data = {
            "source_code": base64.b64encode(code.encode()).decode(),
            "language_id": self.language_map[language],
            "stdin": base64.b64encode("".encode()).decode()
        }
        
        try:
            # 提交代码
            response = requests.post(
                f"{self.api_url}/submissions",
                json=submission_data,
                headers={"Content-Type": "application/json"},
                params={"base64_encoded": "true", "wait": "true"}
            )
            
            if response.status_code == 201:
                result = response.json()
                return self._parse_execution_result(result)
            else:
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error=f"提交失败: {response.status_code}"
                )
                
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                output="",
                error=f"网络错误: {str(e)}"
            )
    
    def run_code(self, code: str, language: str, test_cases: List[Dict]) -> CodeExecutionResult:
        """运行代码并测试用例"""
        if not test_cases:
            return self.submit_code(code, language)
        
        passed_tests = 0
        total_tests = len(test_cases)
        all_outputs = []
        total_time = 0.0
        
        for i, test_case in enumerate(test_cases):
            # 为每个测试用例准备输入
            test_input = test_case.get('input', '')
            expected_output = test_case.get('expected_output', '')
            
            submission_data = {
                "source_code": base64.b64encode(code.encode()).decode(),
                "language_id": self.language_map.get(language, 71),
                "stdin": base64.b64encode(test_input.encode()).decode()
            }
            
            try:
                response = requests.post(
                    f"{self.api_url}/submissions",
                    json=submission_data,
                    headers={"Content-Type": "application/json"},
                    params={"base64_encoded": "true", "wait": "true"}
                )
                
                if response.status_code == 201:
                    result = response.json()
                    execution_result = self._parse_execution_result(result)
                    
                    if execution_result.success:
                        actual_output = execution_result.output.strip()
                        expected_output = expected_output.strip()
                        
                        if actual_output == expected_output:
                            passed_tests += 1
                        
                        all_outputs.append(f"测试用例 {i+1}: {'PASS' if actual_output == expected_output else 'FAIL'}")
                        all_outputs.append(f"输入: {test_input}")
                        all_outputs.append(f"期望输出: {expected_output}")
                        all_outputs.append(f"实际输出: {actual_output}")
                        all_outputs.append("---")
                        
                        total_time += execution_result.execution_time
                    else:
                        all_outputs.append(f"测试用例 {i+1}: ERROR - {execution_result.error}")
                        break
                        
            except Exception as e:
                all_outputs.append(f"测试用例 {i+1}: 网络错误 - {str(e)}")
                break
        
        return CodeExecutionResult(
            success=True,
            output="\n".join(all_outputs),
            execution_time=total_time,
            test_cases_passed=passed_tests,
            total_test_cases=total_tests
        )
    
    def _parse_execution_result(self, result: Dict) -> CodeExecutionResult:
        """解析执行结果"""
        stdout = ""
        stderr = ""
        
        if result.get('stdout'):
            stdout = base64.b64decode(result['stdout']).decode()
        if result.get('stderr'):
            stderr = base64.b64decode(result['stderr']).decode()
        
        # 检查状态
        status = result.get('status', {})
        status_id = status.get('id', 0)
        
        # 状态码含义: 1-排队中, 2-处理中, 3-接受, 4-错误答案, 5-时间限制超出, 6-编译错误, etc.
        success = status_id == 3  # 3表示Accepted
        
        return CodeExecutionResult(
            success=success,
            output=stdout,
            error=stderr if stderr else status.get('description', ''),
            execution_time=float(result.get('time', 0)),
            memory_usage=int(result.get('memory', 0))
        )

class LeetCodeAPI:
    """LeetCode题库接口模拟"""
    
    def __init__(self):
        # 模拟一些LeetCode题目
        self.problems = {
            "two-sum": {
                "id": 1,
                "title": "Two Sum",
                "difficulty": "Easy",
                "description": "给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。",
                "examples": [
                    {
                        "input": "nums = [2,7,11,15], target = 9",
                        "output": "[0,1]",
                        "explanation": "因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。"
                    }
                ],
                "starter_code": {
                    "python": "def twoSum(nums, target):\n    # 在这里写你的代码\n    pass",
                    "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // 在这里写你的代码\n    }\n}",
                    "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // 在这里写你的代码\n    }\n};"
                },
                "test_cases": [
                    {"input": "[2,7,11,15]\n9", "expected_output": "[0,1]"},
                    {"input": "[3,2,4]\n6", "expected_output": "[1,2]"},
                    {"input": "[3,3]\n6", "expected_output": "[0,1]"}
                ]
            },
            "palindrome-number": {
                "id": 9,
                "title": "Palindrome Number",
                "difficulty": "Easy",
                "description": "给你一个整数 x ，如果 x 是一个回文整数，返回 true ；否则，返回 false 。",
                "starter_code": {
                    "python": "def isPalindrome(x):\n    # 在这里写你的代码\n    pass"
                },
                "test_cases": [
                    {"input": "121", "expected_output": "true"},
                    {"input": "-121", "expected_output": "false"},
                    {"input": "10", "expected_output": "false"}
                ]
            }
        }
    
    def get_problem(self, problem_slug: str) -> Optional[Dict]:
        """获取题目详情"""
        return self.problems.get(problem_slug)
    
    def list_problems(self, difficulty: str = None, topic: str = None) -> List[Dict]:
        """列出题目"""
        problems = []
        for slug, problem in self.problems.items():
            if difficulty and problem['difficulty'].lower() != difficulty.lower():
                continue
            problems.append({
                'slug': slug,
                'title': problem['title'],
                'difficulty': problem['difficulty']
            })
        return problems

class ExternalPlatformManager:
    """外部平台管理器"""
    
    def __init__(self):
        self.judge_zero = JudgeZeroAPI()
        self.leetcode = LeetCodeAPI()
    
    def execute_code(self, code: str, language: str, test_cases: List[Dict] = None) -> CodeExecutionResult:
        """执行代码"""
        if test_cases:
            return self.judge_zero.run_code(code, language, test_cases)
        else:
            return self.judge_zero.submit_code(code, language)
    
    def get_leetcode_problem(self, problem_slug: str) -> Optional[Dict]:
        """获取LeetCode题目"""
        return self.leetcode.get_problem(problem_slug)
    
    def search_leetcode_problems(self, difficulty: str = None, topic: str = None) -> List[Dict]:
        """搜索LeetCode题目"""
        return self.leetcode.list_problems(difficulty, topic)

# 全局平台管理器实例
platform_manager = ExternalPlatformManager()
