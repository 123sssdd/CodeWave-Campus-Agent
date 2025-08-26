# AI 回答分析机制详解

## 🧠 AI 回答分析的核心流程

### 📋 1. 回答评估机制 (`evaluate_answer`)

AI 使用**三层评估体系**来分析用户回答：

#### 🔍 第一层：空回答检查

```python
if not answer.strip():
    return False, "未提供回答"
```

#### 🚫 第二层：错误关键词检测

```python
# 检查是否包含错误关键词
for keyword in self.current_pattern.incorrect_keywords:
    if keyword in answer:
        return False, f"回答包含错误关键词: {keyword}"
```

**代数方程求解的错误关键词**：`["正确", "没错", "合理", "应该这样"]`

#### ✅ 第三层：正确性评估

```python
# 检查是否包含正确关键词
correct_found = False
for keyword in self.current_pattern.correct_keywords:
    if keyword in answer:
        correct_found = True
        break

# 计算相似度
similarity = difflib.SequenceMatcher(
    None,
    answer,
    " ".join(self.current_pattern.correct_keywords)
).ratio()
```

**代数方程求解的正确关键词**：`["零点", "x=0", "定义域", "除以零", "遗漏解"]`

#### 📊 评估结果分类

| 条件           | 返回结果 | 置信度变化 | 反馈类型               |
| -------------- | -------- | ---------- | ---------------------- |
| 相似度 > 0.6   | `True`   | +0.2       | 回答与正确答案相似度高 |
| 包含正确关键词 | `True`   | +0.2       | 回答包含正确关键词     |
| 相似度 0.4-0.6 | `None`   | +0.05      | 回答部分相关           |
| 相似度 < 0.4   | `False`  | -0.15      | 回答未包含关键概念     |

---

### 🎯 2. 置信度管理机制

#### 📈 置信度变化规则

```python
if is_correct is True:
    self.student_confidence = min(1.0, self.student_confidence + 0.2)
elif is_correct is False:
    self.student_confidence = max(0.1, self.student_confidence - 0.15)
else:
    self.student_confidence = max(0.1, min(1.0, self.student_confidence + 0.05))
```

#### 🔄 连续回答跟踪

```python
if is_correct is True:
    self.consecutive_correct += 1
    self.consecutive_incorrect = 0
elif is_correct is False:
    self.consecutive_incorrect += 1
    self.consecutive_correct = 0
```

---

### 🤔 3. 继续提问决策机制 (`_should_continue_questioning`)

AI 根据**三个条件**决定是否继续提问：

```python
def _should_continue_questioning(self, is_correct):
    # 条件1：回答错误
    if is_correct is False:
        return True

    # 条件2：置信度低于阈值
    if self.student_confidence < self.confidence_threshold:  # 0.7
        return True

    # 条件3：连续错误次数过多
    if self.consecutive_incorrect >= 2:
        return True

    # 满足条件：回答正确且置信度足够
    return False
```

---

### 🎨 4. 智能追问策略 (`get_follow_up_question`)

AI 根据**学生状态**选择不同的追问策略：

#### 📊 追问策略选择逻辑

```python
if self.student_confidence < 0.3:
    # 策略1：基础引导（置信度极低）
    follow_ups = [
        f"让我们从最基础的开始：{self._get_basic_question()}",
        f"你能先告诉我{self.current_pattern.target_knowledge}的基本定义吗？",
        f"在AI的推理中，你觉得哪个步骤最可疑？"
    ]
elif self.consecutive_incorrect >= 2:
    # 策略2：具体提示（连续错误）
    follow_ups = [
        f"让我给你一个提示：{self._get_hint_question()}",
        f"仔细想想，AI在{self._get_specific_error_step()}这一步犯了什么错误？",
        f"如果让你重新思考这个问题，你会怎么开始？"
    ]
else:
    # 策略3：常规跟进（其他情况）
    follow_ups = [
        f"你能更详细地解释一下为什么{self.current_pattern.expected_output}是错误的吗？",
        f"在这个推理过程中，最关键的错误步骤是什么？",
        f"如果是你，会如何正确解决这个问题？"
    ]
```

#### 🎯 知识点特定问题生成

**代数方程求解的基础问题**：

```python
def _get_basic_question(self):
    return "方程x²=x的解是什么？"
```

**代数方程求解的提示问题**：

```python
def _get_hint_question(self):
    return "当x=0时，方程x²=x还成立吗？"
```

**代数方程求解的具体错误步骤**：

```python
def _get_specific_error_step(self):
    return "除以x"
```

---

## 🔄 完整分析流程示例

### 📝 示例：用户回答"我觉得 AI 的解法是正确的"

#### 1️⃣ 回答评估阶段

```python
# 检查错误关键词
if "正确" in answer:  # 找到错误关键词
    return False, "回答包含错误关键词: 正确"
```

#### 2️⃣ 置信度更新

```python
# 置信度变化
self.student_confidence = 0.5 - 0.15 = 0.35

# 连续错误计数
self.consecutive_incorrect = 1
```

#### 3️⃣ 继续提问决策

```python
# 检查条件
is_correct = False  # 条件1：满足
confidence = 0.35 < 0.7  # 条件2：满足
consecutive_incorrect = 1 < 2  # 条件3：不满足

# 结果：继续提问
should_continue = True
```

#### 4️⃣ 追问策略选择

```python
# 置信度检查
confidence = 0.35 >= 0.3  # 不满足极低置信度条件
consecutive_incorrect = 1 < 2  # 不满足连续错误条件

# 选择常规跟进策略
follow_ups = [
    "你能更详细地解释一下为什么x=1是错误的吗？",
    "在这个推理过程中，最关键的错误步骤是什么？",
    "如果是你，会如何正确解决这个问题？"
]

# 随机选择一个追问
question = "如果是你，会如何正确解决这个问题？"
```

---

## 🎯 智能适应性特征

### 📊 1. 动态难度调整

- **高置信度**：直接进入总结
- **中等置信度**：常规追问
- **低置信度**：基础引导
- **极低置信度**：最基础问题

### 🔄 2. 错误模式识别

- **连续错误**：提供具体提示
- **单次错误**：常规追问
- **部分正确**：轻微引导

### 🎨 3. 问题类型多样化

- **基础问题**：概念理解
- **提示问题**：具体引导
- **解决方案问题**：主动思考
- **错误步骤问题**：针对性分析

### 📈 4. 学习进度跟踪

- **置信度变化**：实时调整策略
- **连续回答**：识别学习模式
- **交互历史**：记录学习轨迹

---

## 💡 核心优势

1. **精确评估**：三层评估体系确保准确性
2. **智能适应**：根据学生状态动态调整
3. **个性化引导**：多种追问策略满足不同需求
4. **渐进式教学**：从基础到深入的引导过程
5. **实时反馈**：即时调整教学策略

这种机制确保了 AI 能够像真正的老师一样，根据学生的回答质量和学习状态，提供最适合的引导和帮助。
