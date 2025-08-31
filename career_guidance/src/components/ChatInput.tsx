import React, { useState } from 'react';
import { Input, Button } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import '../styles/modal.css';

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
      gap: '12px',
      padding: '20px',
      background: 'rgba(255, 255, 255, 0.25)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.4)',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), 0 4px 16px rgba(0, 0, 0, 0.05)',
      borderRadius: '20px',
      margin: '0'
    }}>
      <Input.TextArea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="请描述你的职业发展需求..."
        autoSize={{ minRows: 1, maxRows: 4 }}
        className="modal-input"
        style={{ 
          flex: 1,
          borderRadius: '12px'
        }}
      />
      <Button 
        type="primary" 
        icon={<SendOutlined className="modal-icon" />} 
        onClick={handleSend}
        loading={isLoading}
        disabled={isLoading}
        className="modal-button"
        style={{
          height: '48px'
        }}
      >
        {isLoading ? 'AI思考中...' : '发送'}
      </Button>
    </div>
  );
};

export default ChatInput;
