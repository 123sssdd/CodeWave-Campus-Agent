# 🎯 个性化题库系统

一个基于AI的智能化编程学习平台，支持**学术应试**和**就业面试**双模式，能够根据用户的学习记录、知识掌握情况和学习偏好，智能推荐最适合的题目，提供个性化的学习体验。

## 🌟 项目亮点

- **🎓 双模式设计**：学术模式 + 面试模式，满足不同学习场景
- **🤖 智能推荐**：基于机器学习的个性化题目推荐算法
- **🎤 模拟面试**：完整的面试流程体验，支持录音功能和多平台接入
- **📊 数据驱动**：基于真实数据的技术栈分类和统计分析
- **💻 在线编程**：集成多种在线编程环境和判题系统
- **📈 学习分析**：详细的学习数据统计和可视化图表

## 🎯 双模式设计

### 📚 学术模式 (Academic Mode)
专为学生考试、毕业设计等学术场景设计
- 系统性知识点覆盖
- 理论与实践相结合
- 循序渐进的学习路径

### 💼 就业模式 (Interview Mode) 
专为求职面试、技能提升等就业场景设计
- 真实面试题目库
- 按公司和技术栈分类
- 模拟面试体验
- 面试计划管理

## 🌟 主要特色

### 💡 智能推荐系统
- **个性化算法**：基于用户学习历史、知识点掌握度、答题时间等多维度数据
- **难度自适应**：根据用户表现动态调整题目难度
- **学习路径规划**：为薄弱知识点制定专门的学习计划

### 🎯 多样化题型
- **理论题**：概念理解和原理掌握
- **编程题**：实际代码实现能力训练
- **选择题**：快速知识点检验
- **实践题**：综合应用能力考查
- **面试题**：真实面试场景模拟

### 🚀 面试模式特色功能
- **🎯 智能技术栈分类**：基于真实题库数据动态生成技术栈（Golang、JavaScript、React、Vue、前端工程化）
- **⚡ 技术栈专练系统**：每个技术栈独立练习入口，支持难度筛选和随机练习
- **📊 数据驱动展示**：实时统计题目数量、难度分布，完全基于数据库真实数据
- **🏢 公司题库**：阿里巴巴、腾讯、字节跳动等知名企业真题
- **🎤 多平台模拟面试**：接入Pramp、Interviewing.io、LeetCode Mock等专业面试平台
- **🎙️ 录音答题集成**：录音可作为有效答案提交，支持文字+录音混合回答模式
- **📋 面试计划**：个性化面试准备计划制定和进度跟踪
- **❌ 错题本系统**：智能收集错题，支持相似题推荐和复习提醒

### 💻 在线编程环境
- **🌐 多语言支持**：Python、Java、C++、JavaScript等主流编程语言
- **⚡ 实时代码执行**：集成Judge0 API，支持在线运行和测试
- **🤖 智能评判**：自动检查代码正确性和性能
- **🔗 外部平台集成**：可接入LeetCode、HackerRank等平台
- **📝 代码编辑器**：支持语法高亮、自动补全、代码格式化

### 📊 详细学习分析
- **学习统计**：答题数量、正确率、学习时长等
- **知识点掌握度**：每个知识点的详细掌握情况分析
- **学习趋势**：可视化学习进度和趋势图表
- **个性化建议**：基于数据分析的学习建议

## 🏗️ 系统架构

### 后端技术栈
- **Flask**：轻量级Web框架
- **SQLAlchemy**：ORM数据库操作
- **scikit-learn**：机器学习算法支持
- **pandas/numpy**：数据处理和分析

### 前端技术栈
- **Bootstrap 5**：响应式UI框架
- **Chart.js**：数据可视化图表
- **Prism.js**：代码语法高亮
- **原生JavaScript**：交互逻辑实现

### 外部服务
- **Judge0 API**：在线代码执行服务
- **SQLite**：轻量级数据库（可切换到PostgreSQL/MySQL）

## 📁 项目结构

```
personal_question_bank/
├── 📄 核心应用文件
│   ├── app.py                         # Flask主应用，包含所有API路由
│   ├── models.py                      # SQLAlchemy数据模型定义
│   ├── config.py                      # 应用配置管理
│   └── requirements.txt               # Python依赖包列表
│
├── 🧠 智能算法模块
│   ├── recommendation_engine.py       # 个性化推荐算法引擎
│   ├── theory_grader.py              # 理论题智能评分系统
│   └── ai_interview_service.py       # AI面试服务（预留）
│
├── 🎨 前端模板
│   └── templates/
│       ├── base.html                 # 基础模板（双模式切换支持）
│       ├── index.html                # 系统首页
│       ├── dashboard.html            # 学术模式统计面板
│       ├── practice.html             # 学术模式练习页面
│       ├── knowledge_points.html     # 知识点管理
│       ├── learning_path.html        # 学习路径规划
│       ├── wrong_questions.html      # 错题本系统
│       ├── interview_dashboard.html  # 面试模式主页
│       ├── interview_companies.html  # 公司题库
│       ├── interview_tech_stack.html # 技术栈分类
│       ├── tech_stack_detail.html    # 技术栈专练页面
│       ├── tech_stack_practice.html  # 技术栈练习界面
│       ├── interview_plans.html      # 面试计划管理
│       ├── interview_mock.html       # 多平台模拟面试
│       └── interview_wrong_questions.html # 面试错题本
│
├── 💾 数据存储
│   └── instance/
│       └── question_bank.db          # SQLite数据库文件
│
└── 📚 文档说明
    ├── README.md                      # 项目说明文档
    └── how_to_use.md                 # 详细使用指南
```

## 🚀 快速开始

### 1. 环境准备

确保你的系统已安装Python 3.7+

```bash
# 克隆项目（如果从git仓库）
cd personal_question_bank

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

### 4. 访问系统

1. **打开浏览器访问** `http://localhost:5000`
2. **选择学习模式**：
   - 🎓 **学术模式**：适合在校学生、考试备考
   - 💼 **面试模式**：适合求职者、面试准备
3. **选择预设用户**开始体验个性化推荐
4. **开始学习**：
   - 点击"开始练习"进入练习模式
   - 访问"学习统计"查看详细数据分析
   - 使用"模拟面试"体验完整面试流程

## 🎮 使用指南

> 💡 **详细使用说明**：请参考 [how_to_use.md](how_to_use.md) 获取完整的使用指南和操作步骤

### 🔄 双模式切换
系统支持两种模式，可在左侧导航栏随时切换：

#### 🎓 学术模式（默认）
- **目标用户**：在校学生、考试备考者
- **主要功能**：知识点练习、考试模拟、学习统计
- **访问路径**：`http://localhost:5000/`

#### 💼 面试模式
- **目标用户**：求职者、面试准备者
- **主要功能**：
  - 🎯 面试题练习和技术栈专练
  - 🏢 公司题库（阿里、腾讯、字节等）
  - 🎤 多平台模拟面试（Pramp、Interviewing.io、LeetCode）
  - 📋 个性化面试计划制定
  - ❌ 面试错题本和复习系统
- **访问路径**：`http://localhost:5000/interview`

### 🏠 首页功能
- **用户选择**：选择不同学习背景的用户体验个性化推荐
- **系统介绍**：了解平台主要功能和特色
- **快速开始**：一键进入学习模式

### 📚 练习模式
- **智能推荐**：系统自动推荐10道个性化题目
- **实时计时**：记录答题时间，优化学习节奏
- **即时反馈**：提交后立即查看正确答案和详细解释
- **代码执行**：编程题支持在线运行和测试
- **进度跟踪**：实时显示答题进度

### 📊 学习统计
- **个人概况**：基本信息和整体学习表现
- **详细统计**：各项学习数据的深度分析
- **知识图谱**：每个知识点的掌握程度可视化
- **学习建议**：基于数据的个性化改进建议
- **趋势图表**：学习进度和正确率变化趋势

## 🤖 推荐算法详解

### 用户画像构建
- **学习偏好**：题型偏好、难度偏好、交互方式偏好
- **能力评估**：基于历史答题表现的能力建模
- **学习模式**：学习频率、学习强度、学习一致性分析
- **知识结构**：各知识点掌握程度的多维度评估

### 推荐策略
1. **难度匹配**（30%权重）：根据用户当前能力推荐合适难度
2. **题型偏好**（25%权重）：优先推荐用户喜欢的题型
3. **知识补强**（35%权重）：重点推荐薄弱知识点相关题目
4. **时间适配**（10%权重）：考虑用户平均答题时间

### 多样性保证
- **知识点分散**：避免连续推荐同一知识点
- **题型平衡**：保持不同题型的合理比例
- **难度梯度**：适当的难度变化曲线

## 📈 数据模型

### 核心实体
- **User**：用户基本信息和学习偏好
- **Question**：题目内容、类型、难度等属性
- **KnowledgePoint**：知识点分类和层级结构
- **LearningRecord**：详细的学习行为记录

### 统计分析
- **UserKnowledgeStats**：用户知识点掌握统计
- **实时计算**：正确率、平均用时、掌握程度等指标

## 🔌 扩展功能

### 外部平台集成
- **LeetCode题库**：可同步LeetCode热门题目
- **在线判题**：支持多种在线判题平台
- **题目导入**：支持批量导入外部题库

### 可定制化
- **评分策略**：可调整推荐算法权重
- **题目标签**：支持自定义题目分类
- **学习目标**：可设置个性化学习计划

## 🛠️ 开发说明

### 环境变量配置
创建 `.env` 文件：
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///question_bank.db
JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com
RAPIDAPI_KEY=your-rapidapi-key
```

### 数据库初始化
```python
# 自动创建表结构
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 生成示例数据
python data_generator.py
```

### API接口说明

#### 用户相关
- `GET /api/users` - 获取用户列表
- `GET /api/users/{id}` - 获取用户详情
- `GET /api/users/{id}/stats` - 获取用户学习统计

#### 题目相关
- `GET /api/questions` - 获取题目列表（支持筛选）
- `GET /api/questions/{id}` - 获取题目详情
- `GET /api/recommendations/{user_id}` - 获取个性化推荐

#### 学习记录
- `POST /api/learning-records` - 提交答题记录
- `POST /api/code/run` - ~~在线执行代码~~ (已废弃，现使用CodePen在线编辑器)

#### 面试模式API
- `GET /api/tech-stacks` - 获取基于真实数据的技术栈统计
- `GET /api/tech-stack/{category}/questions` - 获取指定技术栈的题目列表
- `GET /api/companies` - 获取公司题库列表
- `POST /api/mock-interview/questions` - 生成模拟面试题目
- `POST /api/mock-interview/result` - 保存模拟面试结果

#### 错题本API
- `GET /api/wrong-questions/{user_id}` - 获取用户错题列表
- `POST /api/wrong-questions` - 添加错题记录
- `GET /api/similar-questions/{question_id}` - 获取相似题目推荐
- `DELETE /api/wrong-questions/{id}` - 删除错题记录

#### 外部平台集成
- `GET /api/external/leetcode/problems` - 获取LeetCode题目
- `GET /api/external/leetcode/problems/{slug}` - 获取LeetCode题目详情

## 🎯 未来规划

### 功能增强
- [x] ✅ **模拟面试多平台接入**（Pramp、Interviewing.io、LeetCode Mock）
- [x] ✅ **模拟面试录音功能**（录音答题、混合回答模式）
- [x] ✅ **技术栈模块重构**（基于真实数据的动态技术栈）
- [x] ✅ **技术栈专练系统**（独立练习入口、题目筛选、随机练习）
- [x] ✅ **数据驱动的统计展示**（实时题目数量、难度分布）
- [x] ✅ **错题本系统**（智能收集、相似题推荐、复习提醒）
- [ ] 多人竞赛模式
- [ ] 学习小组功能
- [ ] 智能题目生成
- [ ] 语音识别输入
- [ ] 实时面试官角色扮演
- [ ] 跨技术栈关联推荐
- [ ] 录音转文字功能
- [ ] 语音质量分析

### 技术优化
- [ ] 微服务架构重构
- [ ] Redis缓存优化
- [ ] 机器学习模型优化
- [ ] 移动端适配

### 平台扩展
- [ ] 更多编程语言支持
- [ ] 企业级权限管理
- [ ] 课程体系集成
- [ ] AI助教功能

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

1. Fork本项目
2. 创建新的功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下开源项目的支持：
- Flask Web框架
- Bootstrap UI框架
- Chart.js数据可视化
- Judge0在线执行服务
- scikit-learn机器学习库

---

**开始你的个性化学习之旅吧！** 🚀
