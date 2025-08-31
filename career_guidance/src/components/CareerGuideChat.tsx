import React, { useState, useEffect, useRef } from 'react';
import { Layout, Card, Typography, Avatar, Button, Dropdown, Space, Select, message } from 'antd';
import { UserOutlined, RobotOutlined, SendOutlined, ExportOutlined, DownloadOutlined, FileTextOutlined, FileOutlined, FilePdfOutlined, ReloadOutlined } from '@ant-design/icons';
import ChatInput from './ChatInput';
import AIService, { Role } from '../services/aiService';
import '../styles/modal.css';

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
  currentRole: string;
  availableRoles: Role[];
  isLoading: boolean;
}

const CareerGuideChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: '🎯 **欢迎使用AI职业发展顾问！**\n\n我是您的智能职业助手，可以为您提供：\n\n🎓 **个性化学习路线** - 根据现有技能制定进阶计划\n💻 **大模型编程实践** - AI辅助开发的最佳工作流\n📈 **技术栈分析** - 从现状到理想职位的技能差距\n🚀 **实战项目推荐** - 提升技能的最佳实践路径\n📝 **简历优化服务** - 专业简历制作与优化指导\n🎯 **面试指导** - 技术面试和行为面试准备\n\n**AI角色切换：**\n您可以在右上角选择不同的AI专家角色，获得更专业的建议！\n\n**快速开始：**\n选择您的情况或直接描述：\n\n👨‍🎓 应届毕业生 | 🔄 想要转行 | 📊 技能提升 | 💼 求职准备 | 📝 简历优化',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  
  const [userProfile, setUserProfile] = useState<UserProfile>({});
  const [conversationContext, setConversationContext] = useState<string[]>([]);
  const [appState, setAppState] = useState<AppState>({
    isRedirecting: false,
    awaitingUserConfirmation: false,
    showResumeDownload: false,
    currentRole: 'career_advisor',
    availableRoles: [],
    isLoading: false
  });
  
  const [aiService] = useState(() => new AIService());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // 初始化加载角色列表
  useEffect(() => {
    loadRoles();
  }, []);

  // 自动滚动到最新消息
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end'
      });
    }
  };

  const loadRoles = async () => {
    try {
      const response = await aiService.getRoles();
      if (response.status === 'success') {
        setAppState(prev => ({ ...prev, availableRoles: response.roles }));
      }
    } catch (error) {
      console.error('加载角色列表失败:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setConversationContext(prev => [...prev, content]);
    setAppState(prev => ({ ...prev, isLoading: true }));

    // 分析用户输入并更新用户档案
    updateUserProfile(content);

    try {
      // 创建临时消息用于显示流式响应
      const tempBotMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '',
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, tempBotMessage]);
      
      // 调用流式AI服务获取回复
      const response = await aiService.sendMessageStream(content, appState.currentRole, (chunk: string) => {
        // 实时更新消息内容
        setMessages(prev => 
          prev.map(msg => 
            msg.id === tempBotMessage.id 
              ? { ...msg, content: msg.content + chunk }
              : msg
          )
        );
      });
      
      // 检查是否生成了简历
      const isResumeGenerated = response.reply.includes('📝 **专业简历已生成完成！**');
      
      // 更新最终消息
      setMessages(prev => 
        prev.map(msg => 
          msg.id === tempBotMessage.id 
            ? { ...msg, content: response.reply, hasResumeDownload: isResumeGenerated }
            : msg
        )
      );
      
      // 如果生成了简历，保存到状态中
      if (isResumeGenerated) {
        const resumeContent = extractResumeContent(response.reply);
        setAppState(prev => ({ 
          ...prev, 
          generatedResume: resumeContent, 
          showResumeDownload: true 
        }));
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '抱歉，AI服务暂时不可用，请稍后再试。',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setAppState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const extractResumeContent = (reply: string): string => {
    // 从AI回复中提取简历内容
    const resumeStart = reply.indexOf('# **');
    if (resumeStart !== -1) {
      return reply.substring(resumeStart);
    }
    return reply;
  };

  const handleRoleChange = async (newRole: string) => {
    setAppState(prev => ({ ...prev, currentRole: newRole }));
    
    const roleInfo = appState.availableRoles.find(role => role.key === newRole);
    if (roleInfo) {
      message.success(`已切换到：${roleInfo.name}`);
      
      // 添加角色切换提示消息
      const switchMessage: Message = {
        id: Date.now().toString(),
        content: `🔄 **角色已切换为：${roleInfo.name}**\n\n${roleInfo.description}\n\n现在我将以${roleInfo.name}的身份为您提供专业建议！`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, switchMessage]);
    }
  };

  const handleNewChat = async () => {
    try {
      await aiService.startNewChat();
      setMessages([
        {
          id: '1',
          content: '🎯 **新的对话已开始！**\n\n我是您的智能职业助手，请告诉我您需要什么帮助？',
          sender: 'bot',
          timestamp: new Date()
        }
      ]);
      setUserProfile({});
      setConversationContext([]);
      setAppState(prev => ({ 
        ...prev, 
        generatedResume: undefined, 
        showResumeDownload: false,
        awaitingUserConfirmation: false,
        isRedirecting: false
      }));
      message.success('已开始新的对话');
    } catch (error) {
      message.error('重置对话失败');
    }
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
    <Layout style={{ height: '100vh', backgroundColor: 'transparent' }}>
      <Content style={{ padding: '20px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ width: '100%', maxWidth: '900px', height: '100%', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div 
            style={{ 
              borderRadius: '20px',
              background: 'rgba(255, 255, 255, 0.25)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.4)',
              padding: '20px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={4} className="modal-title" style={{ color: '#1e293b', margin: 0, fontWeight: '600', textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)' }}>
                🤖 AI 职业发展顾问
              </Title>
              <Space>
                <Select
                  value={appState.currentRole}
                  onChange={handleRoleChange}
                  style={{ width: 150 }}
                  size="small"
                  options={appState.availableRoles.map(role => ({
                    value: role.key,
                    label: role.name
                  }))}
                  placeholder="选择AI角色"
                />
                <Button 
                  icon={<ReloadOutlined className="modal-icon" />} 
                  size="small"
                  onClick={handleNewChat}
                  title="开始新对话"
                  className="modal-button-secondary"
                >
                  新对话
                </Button>
                {appState.showResumeDownload && (
                  <Dropdown menu={{ items: resumeDownloadItems }} placement="bottomRight">
                    <Button type="primary" icon={<DownloadOutlined className="modal-icon" />} size="small" className="modal-button">
                      下载简历
                    </Button>
                  </Dropdown>
                )}
                {messages.length > 1 && (
                  <Dropdown menu={{ items: exportMenuItems }} placement="bottomRight">
                    <Button icon={<DownloadOutlined className="modal-icon" />} size="small" className="modal-button-secondary">
                      导出对话
                    </Button>
                  </Dropdown>
                )}
              </Space>
            </div>
          </div>

          <div 
            style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              borderRadius: '20px',
              background: 'rgba(255, 255, 255, 0.35)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.05)',
              padding: '20px'
            }}
          >
            <div ref={chatContainerRef} style={{ height: '100%', overflowY: 'auto' }}>
            {messages.map((message) => (
              <Card
                key={message.id}
                style={{
                  marginBottom: '15px',
                  borderRadius: '16px',
                  background: 'rgba(255, 255, 255, 0.25)',
                  backdropFilter: 'blur(15px)',
                  WebkitBackdropFilter: 'blur(15px)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)'
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
                      background: message.sender === 'user' 
                        ? 'rgba(0, 255, 255, 0.08)' 
                        : 'rgba(255, 0, 255, 0.06)',
                      border: `1px solid ${message.sender === 'user' ? 'rgba(0, 255, 255, 0.2)' : 'rgba(255, 0, 255, 0.15)'}`,
                      borderRadius: '16px',
                      padding: '16px',
                      position: 'relative',
                      backdropFilter: 'blur(10px)',
                      WebkitBackdropFilter: 'blur(10px)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.3)'
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
                        color: message.sender === 'user' ? '#0891b2' : '#7c3aed',
                        fontSize: '14px',
                        marginBottom: '8px',
                        display: 'block',
                        textShadow: '0 1px 2px rgba(255, 255, 255, 0.5)'
                      }}>
                        {message.sender === 'user' ? '您' : '🤖 AI顾问'}
                      </Text>
                      
                      <div style={{ 
                        whiteSpace: 'pre-line',
                        lineHeight: '1.6',
                        fontSize: '14px',
                        color: '#1e293b',
                        textShadow: '0 1px 1px rgba(255, 255, 255, 0.3)'
                      }}>
                        <Text style={{ color: '#1e293b' }}>{message.content}</Text>
                      </div>
                      
                      {/* Loading indicator for bot messages */}
                      {message.sender === 'bot' && appState.isLoading && messages[messages.length - 1].id === message.id && (
                        <div style={{ marginTop: '8px', color: '#1890ff' }}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>AI正在思考中...</Text>
                        </div>
                      )}
                      
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
                              icon={<DownloadOutlined className="modal-icon" />}
                              className="modal-button"
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
                        <Text type="secondary" style={{ fontSize: '11px', color: 'rgba(30, 41, 59, 0.6)', textShadow: '0 1px 1px rgba(255, 255, 255, 0.3)' }}>
                          {message.timestamp.toLocaleTimeString()}
                        </Text>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
              {/* 用于自动滚动的锚点 */}
              <div ref={messagesEndRef} style={{ height: '1px' }} />
            </div>
          </div>
          <ChatInput onSend={handleSendMessage} isLoading={appState.isLoading} />
        </div>
      </Content>
    </Layout>
  );
};

export default CareerGuideChat;