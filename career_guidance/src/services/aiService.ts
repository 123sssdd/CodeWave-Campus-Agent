// AI服务接口
const API_BASE_URL = 'http://localhost:5001';

export interface ChatResponse {
  status: string;
  reply: string;
  role?: string;
}

export interface Role {
  key: string;
  name: string;
  description: string;
}

export class AIService {
  private userId: string;

  constructor(userId: string = 'default_user') {
    this.userId = userId;
  }

  /**
   * 发送消息给AI
   */
  async sendMessage(message: string, role?: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          message: message,
          role: role
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('AI服务调用失败:', error);
      return {
        status: 'error',
        reply: '抱歉，AI服务暂时不可用，请检查网络连接或稍后再试。',
        role: role || 'career_advisor'
      };
    }
  }

  /**
   * 开始新的对话
   */
  async startNewChat(): Promise<{ status: string; message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/new_chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
        }),
      });

      return await response.json();
    } catch (error) {
      console.error('重置对话失败:', error);
      return {
        status: 'error',
        message: '重置对话失败'
      };
    }
  }

  /**
   * 设置AI角色
   */
  async setRole(role: string): Promise<{ status: string; message: string; role: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/set_role`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          role: role
        }),
      });

      return await response.json();
    } catch (error) {
      console.error('设置角色失败:', error);
      return {
        status: 'error',
        message: '设置角色失败',
        role: role
      };
    }
  }

  /**
   * 获取可用角色列表
   */
  async getRoles(): Promise<{ status: string; roles: Role[] }> {
    try {
      const response = await fetch(`${API_BASE_URL}/get_roles`);
      return await response.json();
    } catch (error) {
      console.error('获取角色列表失败:', error);
      return {
        status: 'error',
        roles: [
          {
            key: 'career_advisor',
            name: '职业发展顾问',
            description: '提供全面的职业规划和发展建议'
          }
        ]
      };
    }
  }
}

export default AIService;
