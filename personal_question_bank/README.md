# 个性化题库系统

一个基于AI的个性化编程学习平台，能够根据用户的学习记录、知识掌握情况和学习偏好，智能推荐最适合的题目，提供个性化的学习体验。

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

### 💻 在线编程环境
- **多语言支持**：Python、Java、C++、JavaScript等
- **实时代码执行**：集成Judge0 API，支持在线运行和测试
- **智能评判**：自动检查代码正确性和性能
- **外部平台集成**：可接入LeetCode、HackerRank等平台

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
├── app.py                    # Flask主应用
├── models.py                 # 数据模型定义
├── recommendation_engine.py  # 推荐算法引擎
├── external_platforms.py     # 外部平台集成
├── data_generator.py         # 示例数据生成器
├── requirements.txt          # Python依赖包
├── templates/               # HTML模板文件
│   ├── base.html           # 基础模板
│   ├── index.html          # 首页
│   ├── practice.html       # 练习页面
│   └── dashboard.html      # 统计面板
└── README.md               # 项目说明文档
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

1. 打开浏览器访问 `http://localhost:5000`
2. 选择一个预设用户开始体验
3. 点击"开始练习"进入练习模式
4. 或访问"学习统计"查看详细数据分析

## 🎮 使用指南

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
- `POST /api/code/run` - 在线执行代码

#### 外部平台
- `GET /api/external/leetcode/problems` - 获取LeetCode题目
- `GET /api/external/leetcode/problems/{slug}` - 获取LeetCode题目详情

## 🎯 未来规划

### 功能增强
- [ ] 多人竞赛模式
- [ ] 学习小组功能
- [ ] 智能题目生成
- [ ] 语音识别输入

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
