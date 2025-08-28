import React, { useState } from 'react';
import { Input, Button } from 'antd';
import { SendOutlined } from '@ant-design/icons';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading = false }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ 
      display: 'flex',
      gap: '10px',
      position: 'fixed',
      bottom: '20px',
      left: '50%',
      transform: 'translateX(-50%)',
      width: '780px',
      padding: '20px',
      backgroundColor: '#fff',
      boxShadow: '0 -2px 10px rgba(0,0,0,0.1)',
      borderRadius: '15px',
      zIndex: 1000
    }}>
      <Input.TextArea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="请描述你的职业发展需求..."
        autoSize={{ minRows: 1, maxRows: 4 }}
        style={{ 
          flex: 1,
          borderRadius: '8px'
        }}
      />
      <Button 
        type="primary" 
        icon={<SendOutlined />} 
        onClick={handleSend}
        loading={isLoading}
        disabled={isLoading}
        style={{
          height: '40px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
        }}
      >
        {isLoading ? 'AI思考中...' : '发送'}
      </Button>
    </div>
  );
};

export default ChatInput;
