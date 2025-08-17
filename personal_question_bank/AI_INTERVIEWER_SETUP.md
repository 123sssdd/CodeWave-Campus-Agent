# AI面试官功能设置指南

## 🤖 功能概述

新的AI面试官系统提供以下智能功能：

1. **智能反馈**：根据用户回答进行专业评价和建议
2. **语音转文字**：实时语音识别，支持语音输入答案
3. **上下文理解**：基于对话历史进行连贯的面试对话
4. **个性化回应**：识别答非所问、开玩笑等情况并做出合适反应

## 🔧 API配置

系统支持多种大语言模型，会自动选择可用的模型：

### 1. 通义千问API配置（推荐，免费额度大）

```env
# 通义千问API配置
QWEN_API_KEY=your-qwen-api-key-here
```

**获取API密钥**：
1. 访问 [阿里云DashScope](https://dashscope.aliyuncs.com/)
2. 注册/登录阿里云账户
3. 开通DashScope服务
4. 在API密钥管理页面生成密钥

### 2. 百度文心一言API配置（免费）

```env
# 百度文心一言API配置
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key
```

**获取API密钥**：
1. 访问 [百度智能云千帆大模型平台](https://cloud.baidu.com/product/wenxinworkshop)
2. 注册/登录百度账户
3. 创建应用获取API Key和Secret Key

### 3. 智谱AI配置（免费额度）

```env
# 智谱AI配置
ZHIPU_API_KEY=your-zhipu-api-key
```

**获取API密钥**：
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册/登录账户
3. 创建API密钥

### 4. OpenAI API配置（需付费）

```env
# OpenAI API配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**获取API密钥**：
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账户
3. 在 API Keys 页面生成新的密钥

### 2. 百度语音识别API配置（可选）

```env
# 百度语音识别API
BAIDU_APP_ID=your-app-id
BAIDU_API_KEY=your-api-key
BAIDU_SECRET_KEY=your-secret-key
```

**获取API密钥**：
1. 访问 [百度AI开放平台](https://ai.baidu.com/)
2. 创建语音识别应用
3. 获取 AppID、API Key、Secret Key

### 3. 其他兼容的大语言模型

系统支持任何与OpenAI API兼容的服务，如：

- **Azure OpenAI**：
  ```env
  OPENAI_API_KEY=your-azure-key
  OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment/
  ```

- **本地部署的模型**（如Ollama）：
  ```env
  OPENAI_API_KEY=ollama
  OPENAI_BASE_URL=http://localhost:11434/v1
  ```

## 🎯 使用方法

### 1. 启动AI面试官功能

1. 配置好API密钥后重启应用
2. 进入模拟面试页面
3. AI面试官功能会自动启用

### 2. 语音转文字功能

1. 点击 **语音转文字** 按钮（💬图标）
2. 允许浏览器访问麦克风
3. 开始说话，系统会实时转录到文本框
4. 再次点击按钮停止语音识别

### 3. AI面试官交互

1. 提交答案后，AI面试官会：
   - 分析你的回答质量
   - 给出专业反馈
   - 提供改进建议
   - 决定是否需要追问

2. AI面试官能够识别：
   - 专业的技术回答
   - 答非所问的情况
   - 回避问题的行为
   - 不严肃的态度

## 🔧 故障排除

### API不可用时的降级处理

如果没有配置API或API不可用，系统会：
1. 使用内置的模拟面试官回应
2. 保持基本的面试流程功能
3. 在控制台显示相关错误信息

### 语音识别问题

1. **浏览器不支持**：
   - 使用Chrome、Edge等现代浏览器
   - 确保浏览器版本较新

2. **麦克风权限**：
   - 点击地址栏的麦克风图标
   - 选择"始终允许"

3. **识别准确性**：
   - 在安静环境中使用
   - 说话清晰，语速适中
   - 使用普通话

## 📊 面试表现分析

AI面试官会对整场面试进行分析，包括：

- **总体评分**：基于回答质量计算
- **优势分析**：识别表现突出的方面
- **改进建议**：针对性的学习建议
- **详细反馈**：每个问题的具体评价

## 🚀 高级功能

### 自定义面试官角色

可以在 `ai_interviewer_service.py` 中修改面试官的角色设定：

```python
self.interviewer_persona = {
    'role': 'system',
    'content': '''你是一位资深的技术面试官，具有以下特点：
    1. 专业性：精通各种技术栈
    2. 互动性：根据候选人回答进行追问
    3. 适应性：识别各种回答情况
    ...'''
}
```

### 扩展语音识别

系统支持多种语音识别方案：
1. **浏览器内置**：Web Speech API（免费）
2. **百度API**：更准确的中文识别
3. **其他服务**：可扩展集成更多API

## 💡 使用建议

1. **首次使用**：建议先配置OpenAI API获得最佳体验
2. **网络环境**：确保网络稳定，避免API调用失败
3. **浏览器选择**：推荐使用Chrome或Edge浏览器
4. **面试准备**：在安静环境中进行模拟面试
5. **反馈利用**：认真阅读AI面试官的反馈和建议

## 📞 技术支持

如果在使用过程中遇到问题：

1. 检查 `.env` 文件配置是否正确
2. 查看浏览器控制台的错误信息
3. 确认API密钥是否有效且有足够额度
4. 检查网络连接是否稳定

---

**注意**：AI面试官功能需要网络连接和相应的API配置。如果暂时无法配置，系统仍会提供基础的面试功能。
