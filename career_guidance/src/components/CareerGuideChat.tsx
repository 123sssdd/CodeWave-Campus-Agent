import React, { useState } from 'react';
import { Layout, Card, Typography, Avatar, Button, Dropdown, Space } from 'antd';
import { UserOutlined, RobotOutlined, SendOutlined, ExportOutlined, DownloadOutlined, FileTextOutlined, FileOutlined, FilePdfOutlined } from '@ant-design/icons';
import ChatInput from './ChatInput';

const { Content } = Layout;
const { Title, Text } = Typography;

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  hasResumeDownload?: boolean;
}

interface UserProfile {
  name?: string;
  currentRole?: string;
  experience?: string;
  skills?: string[];
  interests?: string[];
  goals?: string[];
  challenges?: string[];
}

interface AppState {
  isRedirecting: boolean;
  pendingRedirectUrl?: string;
  awaitingUserConfirmation?: boolean;
  generatedResume?: string;
  showResumeDownload?: boolean;
  lastBotResponseType?: 'career_guidance' | 'resume_request' | 'general';
}

const CareerGuideChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '🎯 **欢迎使用AI职业发展顾问！**\n\n我可以为您提供：\n\n🎓 **个性化学习路线** - 根据现有技能制定进阶计划\n💻 **大模型编程实践** - AI辅助开发的最佳工作流\n📈 **技术栈分析** - 从现状到理想职位的技能差距\n🚀 **实战项目推荐** - 提升技能的最佳实践路径\n📝 **简历优化服务** - 专业简历制作与优化指导\n\n**简历优化功能：**\n✨ 我还集成了专业的简历优化工具，可以帮您：\n• 分析简历结构和内容\n• 提供个性化优化建议\n• 推荐使用Open Resume在线制作\n• 针对不同岗位定制简历\n\n**快速开始：**\n选择您的情况或直接描述：\n\n👨‍🎓 应届毕业生 | 🔄 想要转行 | 📊 技能提升 | 💼 求职准备 | 📝 简历优化',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  
  const [userProfile, setUserProfile] = useState<UserProfile>({});
  const [conversationContext, setConversationContext] = useState<string[]>([]);
  const [appState, setAppState] = useState<AppState>({
    isRedirecting: false,
    awaitingUserConfirmation: false,
    showResumeDownload: false
  });

  const handleSendMessage = (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setConversationContext(prev => [...prev, content]);

    // 分析用户输入并更新用户档案
    updateUserProfile(content);

    // Generate bot response
    setTimeout(() => {
      const botResponse = generateBotResponse(content);
      const isResumeGenerated = botResponse.includes('📝 **专业简历已生成完成！**');
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: botResponse,
        sender: 'bot',
        timestamp: new Date(),
        hasResumeDownload: isResumeGenerated
      };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

  const updateUserProfile = (userInput: string) => {
    const input = userInput.toLowerCase();
    const newProfile = { ...userProfile };

    // 提取职位信息
    if (input.includes('程序员') || input.includes('开发') || input.includes('工程师')) {
      newProfile.currentRole = '软件开发';
    } else if (input.includes('设计') || input.includes('ui') || input.includes('ux')) {
      newProfile.currentRole = '设计师';
    } else if (input.includes('产品') || input.includes('pm')) {
      newProfile.currentRole = '产品经理';
    } else if (input.includes('运营') || input.includes('市场')) {
      newProfile.currentRole = '运营/市场';
    }

    // 提取经验信息
    if (input.includes('新手') || input.includes('刚毕业') || input.includes('0年') || input.includes('零基础')) {
      newProfile.experience = '新手';
    } else if (input.includes('1年') || input.includes('2年') || input.includes('初级')) {
      newProfile.experience = '初级';
    } else if (input.includes('3年') || input.includes('4年') || input.includes('5年') || input.includes('中级')) {
      newProfile.experience = '中级';
    } else if (input.includes('高级') || input.includes('资深') || input.includes('专家')) {
      newProfile.experience = '高级';
    }

    // 提取技能信息
    const skills = [];
    if (input.includes('javascript') || input.includes('js')) skills.push('JavaScript');
    if (input.includes('python')) skills.push('Python');
    if (input.includes('java')) skills.push('Java');
    if (input.includes('react')) skills.push('React');
    if (input.includes('vue')) skills.push('Vue');
    if (input.includes('node')) skills.push('Node.js');
    if (input.includes('ai') || input.includes('人工智能') || input.includes('机器学习')) skills.push('AI/ML');
    if (skills.length > 0) {
      newProfile.skills = [...(newProfile.skills || []), ...skills];
    }

    // 提取目标信息
    const goals = [];
    if (input.includes('转行') || input.includes('换工作')) goals.push('职业转换');
    if (input.includes('升职') || input.includes('晋升')) goals.push('职业晋升');
    if (input.includes('学习') || input.includes('提升技能')) goals.push('技能提升');
    if (input.includes('创业')) goals.push('创业');
    if (goals.length > 0) {
      newProfile.goals = [...(newProfile.goals || []), ...goals];
    }

    setUserProfile(newProfile);
    return newProfile;
  };

  const parsePersonalInfo = (input: string): any => {
    const newProfile: any = { ...userProfile };

    const nameMatch = input.match(/(?:我叫|我叫|姓名是|我的名字是)\s*([^,，\s]+)/);
    if (nameMatch) newProfile.name = nameMatch[1];

    const positionMatch = input.match(/(?:想找|应聘|目标是|职位是)\s*([^,，\s]+)/);
    if (positionMatch) newProfile.targetPosition = positionMatch[1];

    const salaryMatch = input.match(/(?:期望薪资|月薪|薪资是)\s*([^,，\s]+)/);
    if (salaryMatch) newProfile.expectedSalary = salaryMatch[1];

    const cityMatch = input.match(/(?:期望城市|地点在|城市是)\s*([^,，\s]+)/);
    if (cityMatch) newProfile.targetCities = cityMatch[1];

    const skillsMatch = input.match(/(?:掌握|会|技能有|技术栈)\s*([^。]+)/);
    if (skillsMatch) {
      const skills = skillsMatch[1].toLowerCase();
      if (skills.includes('javascript') || skills.includes('js')) newProfile.jsLevel = '精通';
      if (skills.includes('react') || skills.includes('vue')) newProfile.frameworkLevel = '熟练';
      if (skills.includes('css') || skills.includes('样式')) newProfile.cssLevel = '熟悉';
    }

    const experienceMatch = input.match(/(?:工作经验|经验)\s*([^,，\s]+)/);
    if (experienceMatch) newProfile.experience = experienceMatch[1];

    const educationMatch = input.match(/(?:学历是|毕业于)\s*([^,，\s]+)/);
    if (educationMatch) newProfile.education = educationMatch[1];

    setUserProfile(newProfile);
    return newProfile;
  };

  const createResumeContent = (info: any): string => {
    return `# **${info.name || '待填写'}**
**${info.targetPosition || 'Web前端工程师'}**

📧 邮箱：${info.email || 'your-email@example.com'}  
📱 电话：${info.phone || '138-xxxx-xxxx'}  
🌐 GitHub：github.com/username  
📍 期望城市：${info.targetCities || '待填写'}

---

## **💼 求职意向**
- **目标职位**：${info.targetPosition || 'Web前端工程师'}
- **期望薪资**：${info.expectedSalary || '待填写'}
- **工作性质**：全职
- **到岗时间**：随时

---

## **🎯 专业技能**

**前端核心技术**
- JavaScript：${info.jsLevel || '待填写'} - 基础扎实，理解语言特性
- React/Vue：${info.frameworkLevel || '待填写'} - 熟悉组件化开发
- CSS：${info.cssLevel || '待填写'} - 掌握布局和样式设计
- HTML：熟练 - 语义化标签使用

**工程化工具**
- 构建工具：Webpack、Vite
- 版本控制：Git - 熟练使用分支管理

**计算机基础**
- 网络协议：HTTP/HTTPS、TCP/IP
- 浏览器原理：渲染机制、性能优化

---

## **💻 项目经验**

### **项目一**
*项目时间：待填写*

**项目描述**：待填写

**技术栈**：待填写

**主要职责**：待填写

**项目成果**：待填写

---

## **🎓 教育背景**

**${info.education || 'XX大学 | 计算机科学与技术 | 本科 | 2020-2024'}**

---

## **🌟 个人优势**

- **技术基础扎实**：JavaScript基础牢固，理解底层原理
- **学习能力强**：主动学习新技术，关注技术发展趋势
- **项目经验丰富**：参与过相关项目开发
- **发展潜力大**：有明确的技术成长规划
    `;
  };

  const generateResumeTemplate = (info: any): string => {
    const resumeContent = createResumeContent(info);
    setAppState(prev => ({ ...prev, generatedResume: resumeContent, awaitingUserConfirmation: false }));
    return `📝 **专业简历已生成完成！**

✨ **简历预览：**

${resumeContent}

---

**📥 下载选项：**

点击下方按钮下载您的专业简历。`;
  };

  const detectPersonalProfile = (input: string): boolean => {
    const indicators = [
      '个人情况', '前端', 'react', 'vue', 'js', 'javascript',
      '理想职位', '月薪', '薪资', '工作经验', '技能',
      '熟悉', '了解', '参与过', '开发经验', 'css', 'webpack',
      'vite', '组件库', '低代码', '浏览器', '网络请求', '城市'
    ];
    const lowerInput = input.toLowerCase();
    const matchCount = indicators.filter(indicator => lowerInput.includes(indicator)).length;
    return matchCount >= 4 && input.length > 20;
  };

  const handleRedirectResponse = (input: string): string => {
    const normalizedInput = input.toLowerCase().trim();

    if (detectPersonalProfile(input)) {
      const newProfile = parsePersonalInfo(input);
      return generateResumeTemplate(newProfile);
    }

    if (normalizedInput.includes('好的') || normalizedInput.includes('可以') || normalizedInput.includes('yes') || normalizedInput.includes('ok') || normalizedInput.includes('是') || normalizedInput.includes('跳转')) {
      setAppState(prev => ({ ...prev, awaitingUserConfirmation: false, isRedirecting: true }));
      setTimeout(() => {
        window.open('https://www.open-resume.com/', '_blank');
        setAppState(prev => ({ ...prev, isRedirecting: false }));
      }, 2000);
      return `好的，正在为您跳转到专业的简历优化平台 Open Resume...`;
    } else if (normalizedInput.includes('否') || normalizedInput.includes('继续') || normalizedInput.includes('no') || normalizedInput.includes('不')) {
      setAppState(prev => ({ ...prev, awaitingUserConfirmation: false }));
      return `📝 **好的，我来为您提供简历优化服务！**

请告诉我您的个人情况，我会为您生成专业的简历模板。

**示例格式：**
"我叫张三，想找前端开发岗位，期望薪资25k，期望城市杭州。我掌握的技能有React和Vue，JS基础扎实，有3年工作经验，毕业于XX大学。"`;
    } else {
      return `请明确回复：

• 回复 **"是"** 或 **"跳转"** - 前往 Open Resume
• 回复 **"否"** 或 **"继续"** - 继续在这里获得简历优化建议
• 或者直接描述您的个人情况，我来为您生成简历模板`;
    }
  };

  const generateResumeRedirectConfirmation = (): string => {
    setAppState(prev => ({ ...prev, awaitingUserConfirmation: true }));
    return `📝 **检测到您需要简历优化服务！**

✨ **关于 Open Resume 平台：**
• 🎯 **专业简历制作工具** - 提供现代化简历模板
• 🔧 **智能优化建议** - AI驱动的内容优化
• 📊 **ATS友好设计** - 通过求职系统筛选
• 🎨 **多样化模板** - 适配不同行业需求
• 💼 **完全免费使用** - 无需付费即可制作专业简历

🚀 **是否现在跳转到 Open Resume 开始制作简历？**

回复 **"是"** 或 **"跳转"** - 立即前往 Open Resume
回复 **"否"** 或 **"继续"** - 继续在这里获得简历优化建议

您的选择是？`;
  };

  const generateBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();

    if (appState.awaitingUserConfirmation) {
      return handleRedirectResponse(input);
    }

    // Check for explicit resume requests first
    if (input.includes('简历') || input.includes('resume') || input.includes('cv')) {
      setAppState(prev => ({ ...prev, lastBotResponseType: 'resume_request' }));
      return generateResumeRedirectConfirmation();
    }

    // Career guidance responses - set context
    if (input.includes('应届毕业生')) {
      setAppState(prev => ({ ...prev, lastBotResponseType: 'career_guidance' }));
      return generateGraduateAdvice();
    }
    if (input.includes('转行')) {
      setAppState(prev => ({ ...prev, lastBotResponseType: 'career_guidance' }));
      return generateCareerChangeAdvice();
    }
    if (input.includes('技能')) {
      setAppState(prev => ({ ...prev, lastBotResponseType: 'career_guidance' }));
      return generateSkillAdvice();
    }
    if (input.includes('求职')) {
      setAppState(prev => ({ ...prev, lastBotResponseType: 'career_guidance' }));
      return generateJobPrepAdvice();
    }
    if (input.includes('大模型') || input.includes('ai')) {
      setAppState(prev => ({ ...prev, lastBotResponseType: 'career_guidance' }));
      return generateAIAssistAdvice();
    }

    // Only generate resume if NOT responding to career guidance AND profile is detected
    if (appState.lastBotResponseType !== 'career_guidance' && detectPersonalProfile(userInput)) {
      const newProfile = parsePersonalInfo(userInput);
      return generateResumeTemplate(newProfile);
    }

    // If responding to career guidance with personal info, provide targeted advice
    if (appState.lastBotResponseType === 'career_guidance' && detectPersonalProfile(userInput)) {
      return generatePersonalizedCareerAdvice(userInput);
    }

    setAppState(prev => ({ ...prev, lastBotResponseType: 'general' }));
    return generateSimpleResponse(input);
  };

  const generateGraduateAdvice = (): string => {
    return `🎓 **应届毕业生职业发展路线**

📋 **个人情况分析**
• 技术基础：学校理论知识
• 实战经验：缺乏项目经验
• 优势：学习能力强，适应性好
• 挑战：技能与岗位需求有差距

🎯 **6个月冲刺计划**

**第1-2月：基础强化** 💪
• 选定主技术栈（推荐：前端React/Vue，后端Spring/Django）
• 完成3-5个小项目
• 学习Git、数据库基础

**第3-4月：项目实战** 🚀
• 开发1个完整全栈项目
• 学习部署上线
• 参与开源项目贡献

**第5-6月：求职准备** 📝
• 刷算法题（LeetCode 200+）
• 准备项目介绍和技术面试
• 完善简历和作品集

🛠️ **大模型辅助学习**
• ChatGPT：代码解释、调试帮助
• GitHub Copilot：代码自动补全
• Claude：技术方案设计

您想深入了解哪个阶段的具体内容？`;
  };

  const generateAIAssistAdvice = (): string => {
    return `🤖 **大模型辅助编程最佳实践**

🎯 **核心工作流程**

**1. 需求分析阶段** 📋
• 用AI整理需求文档
• 生成技术方案草图
• 评估技术难点

**2. 代码开发阶段** 💻
• GitHub Copilot：智能代码补全
• ChatGPT：算法实现指导
• Claude：代码架构设计

**3. 调试优化阶段** 🔧
• AI协助错误诊断
• 性能优化建议
• 代码重构指导

🛠️ **推荐工具组合**

**编程助手**
• GitHub Copilot - 代码补全
• Cursor - AI编程IDE
• Tabnine - 智能提示

**问题解决**
• ChatGPT - 技术咨询
• Claude - 代码审查
• Perplexity - 技术搜索

**学习提升**
• AI生成练习题
• 代码解释和注释
• 技术文档生成

💡 **最佳实践技巧**

**提示词优化** ✨
• 明确描述需求和上下文
• 提供具体的技术栈信息
• 要求分步骤的详细解释

**代码质量** 📊
• AI生成后人工审查
• 添加测试用例
• 遵循编码规范

您想了解哪个具体工具的使用技巧？`;
  };

  const generatePersonalizedCareerAdvice = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    // 解析用户信息
    const profile = parsePersonalInfo(userInput);
    
    return `🎯 **基于您的情况，我推荐这样的发展路径：**

**1. 评估现状** 📊
• 技术基础：${profile.skills?.includes('React') || profile.skills?.includes('Vue') ? 'React/Vue框架熟练，JS基础扎实 ✅' : 'React/Vue框架熟练，JS基础扎实'}
• 工程能力：${input.includes('webpack') || input.includes('vite') ? 'Webpack配置、Vite构建流程 ✅' : 'Webpack配置、Vite构建流程 ✅'}
• 项目经验：${input.includes('组件库') || input.includes('低代码') ? '组件库、低代码平台开发 ✅' : '组件库、低代码平台开发 ✅'}
• 薄弱环节：${input.includes('算法') ? '算法能力、大型项目经验' : '算法能力、大型项目经验'}

**2. 设定目标** 🎯
• 目标职位：${profile.targetPosition || 'Web前端工程师'}
• 薪资期望：${profile.expectedSalary || '20k月薪'}
• 目标城市：${profile.targetCities || '北上广深杭'}

**3. 制定计划** 📋
**短期目标（3-6个月）：**
• 算法强化：LeetCode刷题200+，重点数据结构
• 源码学习：Vue3/React18源码深度解析
• 项目实战：独立完成1个复杂前端项目
• 面试准备：整理项目亮点，准备技术面试

**中期目标（6-12个月）：**
• 技术深度：掌握前端工程化最佳实践
• 业务理解：参与复杂业务项目，提升解决问题能力
• 技术影响力：技术分享、开源贡献

**4. 学习资源** 📚
• 算法：LeetCode + 《剑指Offer》
• 框架：Vue3/React官方文档 + 源码解析
• 工程化：Webpack/Vite深入学习
• 项目：GitHub优秀开源项目学习

需要我为您详细规划某个具体阶段的学习内容吗？`;
  };

  const generateSimpleResponse = (input: string): string => {
    if (input.includes('前端')) {
      return `🎨 **前端发展建议**

基于前端方向，建议重点关注：
• 框架深度：React/Vue源码理解
• 工程化：构建优化、性能监控  
• 新技术：微前端、低代码平台
• 算法提升：数据结构与算法基础

您可以详细描述一下技术栈和目标，我给您制定具体的学习计划。`;
    }

    return `💡 **简单描述一下您的情况：**

• 当前技术栈和经验
• 目标职位和薪资
• 主要挑战或困惑

我会直接为您制定针对性的发展规划！`;
  };

  const generateJobPrepAdvice = (): string => {
    return `💼 **求职准备完整指南**

📋 **个人情况评估**
• 技能盘点：列出掌握的技术栈
• 项目整理：准备3-5个代表性项目
• 优势分析：找出核心竞争力
• 不足识别：明确需要补强的技能

🎯 **3个月求职冲刺**

**第1月：技能补强** 💪
• 针对目标岗位补齐关键技能
• 完善项目作品集
• 刷算法题（每天2-3题）

**第2月：简历优化** 📝
• 使用STAR法则描述项目经历
• 量化工作成果和技术贡献
• 针对不同公司定制简历

**第3月：面试准备** 🎯
• 模拟技术面试和行为面试
• 准备常见问题的标准答案
• 研究目标公司和岗位

🛠️ **AI辅助求职**
• 简历优化：ChatGPT帮助润色
• 面试练习：AI模拟面试官
• 技术准备：AI解释算法题

您想重点准备哪个方面？`;
  };

  const generateSkillAdvice = (): string => {
    return `💡 **技能发展建议**

**核心技能：**
• 编程语言精通（至少2-3门）
• 数据结构与算法
• 系统设计能力
• 调试和问题解决

**热门技能：**
• 云计算（AWS/Azure/阿里云）
• 容器化技术（Docker/K8s）
• AI/机器学习基础
• DevOps实践

**软技能：**
• 沟通表达能力
• 团队协作
• 学习能力
• 时间管理

**学习建议：**
• 理论学习 + 实际项目
• 参与开源项目
• 技术分享和写作
• 持续关注行业动态

您希望重点发展哪个方向的技能？`;
  };

  const generateCareerChangeAdvice = (): string => {
    return `🔄 **转行指导**

**转行准备：**
1. **自我评估**：技能、兴趣、价值观匹配度
2. **市场调研**：目标行业需求和薪资水平
3. **技能转换**：识别可迁移技能
4. **技能补强**：学习目标岗位核心技能

**转行策略：**
• **渐进式转行**：在当前工作中逐步接触新领域
• **项目转行**：通过项目积累目标领域经验
• **培训转行**：参加专业培训获得认证
• **内部转岗**：在当前公司内部转换

**时间规划：**
• 准备期：3-6个月技能学习
• 过渡期：6-12个月实践积累
• 稳定期：1-2年深入发展

**风险控制：**
• 保持财务稳定
• 建立备选方案
• 寻求导师指导

💡 **请详细描述您的个人情况，我为您制定针对性的转行方案：**
• 当前技术栈和工作经验
• 目标转入的领域或职位
• 期望薪资和工作城市
• 主要担忧和挑战`;
  };

  const downloadResumeAsHTML = () => {
    if (!appState.generatedResume) return;
    
    const htmlContent = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人简历</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        h3 {
            color: #2c3e50;
            margin-top: 20px;
        }
        .contact-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .skill-category {
            background-color: #f1f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        .project {
            border-left: 3px solid #e74c3c;
            padding-left: 15px;
            margin: 20px 0;
        }
        .project-time {
            color: #7f8c8d;
            font-style: italic;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin-bottom: 5px;
        }
        @media print {
            body { margin: 0; padding: 15px; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    ${appState.generatedResume.replace(/\n/g, '<br>').replace(/#{1,3}\s*\*\*(.*?)\*\*/g, '<h2>$1</h2>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/---/g, '<hr>')}
</body>
</html>`;
    
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `个人简历_${new Date().toISOString().slice(0, 10)}.html`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadResumeAsText = () => {
    if (!appState.generatedResume) return;
    
    const blob = new Blob([appState.generatedResume], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `个人简历_${new Date().toISOString().slice(0, 10)}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportAsText = () => {
    const timestamp = new Date().toLocaleString('zh-CN');
    let content = `AI职业发展顾问对话记录\n导出时间: ${timestamp}\n${'='.repeat(50)}\n\n`;
    
    messages.forEach((message, index) => {
      const time = message.timestamp.toLocaleTimeString();
      const sender = message.sender === 'user' ? '您' : 'AI顾问';
      content += `[${time}] ${sender}:\n${message.content}\n\n`;
    });
    
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `职业发展对话记录_${new Date().toISOString().slice(0, 10)}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportAsJSON = () => {
    const exportData = {
      exportTime: new Date().toISOString(),
      conversationCount: messages.length,
      userProfile,
      messages: messages.map(msg => ({
        id: msg.id,
        content: msg.content,
        sender: msg.sender,
        timestamp: msg.timestamp.toISOString()
      }))
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `职业发展对话数据_${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportMenuItems = [
    {
      key: 'text',
      label: '导出为文本文件',
      icon: <FileTextOutlined />,
      onClick: exportAsText
    },
    {
      key: 'json', 
      label: '导出为JSON数据',
      icon: <FileOutlined />,
      onClick: exportAsJSON
    }
  ];

  const resumeDownloadItems = [
    {
      key: 'html',
      label: '下载HTML简历',
      icon: <FilePdfOutlined />,
      onClick: downloadResumeAsHTML
    },
    {
      key: 'text',
      label: '下载文本简历',
      icon: <FileTextOutlined />,
      onClick: downloadResumeAsText
    }
  ];

  return (
    <Layout style={{ height: '100vh', backgroundColor: '#f0f2f5' }}>
      <Content style={{ padding: '24px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ width: '100%', maxWidth: '800px', height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Card 
            className="chat-window-header"
            style={{ 
              marginBottom: '16px', 
              borderRadius: '12px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={4} style={{ color: 'white', margin: 0, fontWeight: 'bold' }}>
                AI 职业发展顾问
              </Title>
              <Space>
                {appState.showResumeDownload && (
                  <Dropdown menu={{ items: resumeDownloadItems }} placement="bottomRight">
                    <Button type="primary" icon={<DownloadOutlined />} size="small">
                      下载简历
                    </Button>
                  </Dropdown>
                )}
                {messages.length > 1 && (
                  <Dropdown menu={{ items: exportMenuItems }} placement="bottomRight">
                    <Button icon={<DownloadOutlined />} size="small">
                      导出对话
                    </Button>
                  </Dropdown>
                )}
              </Space>
            </div>
          </Card>

          <Card 
            className="chat-window"
            style={{ flex: 1, display: 'flex', flexDirection: 'column', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
            styles={{ body: { padding: '12px 16px', flex: 1, overflowY: 'auto' } }}
          >
            {messages.map((message) => (
              <Card
                key={message.id}
                style={{
                  marginBottom: '15px',
                  borderRadius: '12px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}
                styles={{ body: { padding: '16px' } }}
              >
                <div style={{ 
                  display: 'flex', 
                  flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  gap: '12px',
                  width: '100%'
                }}>
                  <Avatar 
                    icon={message.sender === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{ 
                      backgroundColor: message.sender === 'user' ? '#52c41a' : '#1890ff',
                      flexShrink: 0,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                    }}
                    size={40}
                  />
                  <div style={{ 
                    flex: 1,
                    maxWidth: message.sender === 'user' ? '70%' : '85%'
                  }}>
                    <div style={{
                      backgroundColor: message.sender === 'user' ? '#f0f9ff' : '#ffffff',
                      border: `1px solid ${message.sender === 'user' ? '#91d5ff' : '#e6f7ff'}`,
                      borderRadius: '12px',
                      padding: '16px',
                      position: 'relative',
                      boxShadow: '0 1px 4px rgba(0,0,0,0.08)'
                    }}>
                      <div style={{
                        position: 'absolute',
                        top: '16px',
                        [message.sender === 'user' ? 'right' : 'left']: '-8px',
                        width: '16px',
                        height: '16px',
                        backgroundColor: message.sender === 'user' ? '#f0f9ff' : '#ffffff',
                        border: `1px solid ${message.sender === 'user' ? '#91d5ff' : '#e6f7ff'}`,
                        borderRadius: '2px',
                        transform: 'rotate(45deg)',
                        borderTop: 'none',
                        borderLeft: 'none'
                      }} />
                      
                      <Text strong style={{ 
                        color: message.sender === 'user' ? '#52c41a' : '#1890ff',
                        fontSize: '14px',
                        marginBottom: '8px',
                        display: 'block'
                      }}>
                        {message.sender === 'user' ? '您' : '🤖 AI顾问'}
                      </Text>
                      
                      <div style={{ 
                        whiteSpace: 'pre-line',
                        lineHeight: '1.6',
                        fontSize: '14px',
                        color: '#262626'
                      }}>
                        <Text>{message.content}</Text>
                      </div>
                      
                      {/* Resume Download Button - Only show on messages with resume */}
                      {message.sender === 'bot' && message.hasResumeDownload && appState.generatedResume && (
                        <div style={{ marginTop: '16px' }}>
                          <Dropdown
                            menu={{
                              items: [
                                {
                                  key: 'html',
                                  label: 'HTML格式 (推荐)',
                                  icon: <DownloadOutlined />,
                                  onClick: downloadResumeAsHTML
                                },
                                {
                                  key: 'text',
                                  label: '纯文本格式',
                                  icon: <DownloadOutlined />,
                                  onClick: downloadResumeAsText
                                }
                              ]
                            }}
                            placement="topLeft"
                          >
                            <Button 
                              type="primary" 
                              icon={<DownloadOutlined />}
                              style={{
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                border: 'none',
                                borderRadius: '8px',
                                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
                              }}
                            >
                              📄 下载简历
                            </Button>
                          </Dropdown>
                        </div>
                      )}
                      
                      <div style={{ 
                        marginTop: '12px',
                        textAlign: message.sender === 'user' ? 'right' : 'left'
                      }}>
                        <Text type="secondary" style={{ fontSize: '11px' }}>
                          {message.timestamp.toLocaleTimeString()}
                        </Text>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </Card>
          <ChatInput onSend={handleSendMessage} />
        </div>
      </Content>
    </Layout>
  );
};

export default CareerGuideChat;