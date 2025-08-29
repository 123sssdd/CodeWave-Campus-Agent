import React, { useState } from 'react';
import { Modal, Button, Input, Form, Space } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, CloseOutlined } from '@ant-design/icons';
import '../styles/modal.css';

interface ExampleModalProps {
  visible: boolean;
  onClose: () => void;
}

const ExampleModal: React.FC<ExampleModalProps> = ({ visible, onClose }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields();
      console.log('Form values:', values);
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      onClose();
    } catch (error) {
      console.error('Form validation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      open={visible}
      onCancel={onClose}
      footer={null}
      width={600}
      centered
      destroyOnClose
      maskStyle={{
        background: 'rgba(15, 23, 42, 0.8)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)'
      }}
      modalRender={(modal) => (
        <div className="modal-overlay">
          <div className="modal-card breathing">
            <Button
              className="modal-close"
              icon={<CloseOutlined />}
              onClick={onClose}
              aria-label="关闭"
            />
            
            <h2 className="modal-title">
              ✨ 个人信息设置
            </h2>
            
            <div className="modal-content">
              <Form
                form={form}
                layout="vertical"
                requiredMark={false}
                style={{ marginTop: '24px' }}
              >
                <Form.Item
                  name="name"
                  label={
                    <span style={{ color: '#e2e8f0', textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)' }}>
                      姓名
                    </span>
                  }
                  rules={[{ required: true, message: '请输入您的姓名' }]}
                >
                  <Input
                    className="modal-input"
                    prefix={<UserOutlined className="modal-icon" style={{ color: '#00ffff' }} />}
                    placeholder="请输入您的姓名"
                    size="large"
                  />
                </Form.Item>

                <Form.Item
                  name="email"
                  label={
                    <span style={{ color: '#e2e8f0', textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)' }}>
                      邮箱
                    </span>
                  }
                  rules={[
                    { required: true, message: '请输入您的邮箱' },
                    { type: 'email', message: '请输入有效的邮箱地址' }
                  ]}
                >
                  <Input
                    className="modal-input"
                    prefix={<MailOutlined className="modal-icon" style={{ color: '#ff00ff' }} />}
                    placeholder="请输入您的邮箱"
                    size="large"
                  />
                </Form.Item>

                <Form.Item
                  name="phone"
                  label={
                    <span style={{ color: '#e2e8f0', textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)' }}>
                      电话
                    </span>
                  }
                  rules={[{ required: true, message: '请输入您的电话号码' }]}
                >
                  <Input
                    className="modal-input"
                    prefix={<PhoneOutlined className="modal-icon" style={{ color: '#667eea' }} />}
                    placeholder="请输入您的电话号码"
                    size="large"
                  />
                </Form.Item>

                <Form.Item
                  name="description"
                  label={
                    <span style={{ color: '#e2e8f0', textShadow: '0 1px 2px rgba(0, 0, 0, 0.8)' }}>
                      个人简介
                    </span>
                  }
                >
                  <Input.TextArea
                    className="modal-input"
                    placeholder="请简单介绍一下自己..."
                    rows={4}
                    showCount
                    maxLength={200}
                  />
                </Form.Item>
              </Form>

              <Space style={{ width: '100%', justifyContent: 'center', marginTop: '32px' }} size="large">
                <Button
                  className="modal-button-secondary"
                  size="large"
                  onClick={onClose}
                >
                  取消
                </Button>
                <Button
                  className="modal-button"
                  size="large"
                  loading={loading}
                  onClick={handleSubmit}
                >
                  {loading ? '保存中...' : '保存设置'}
                </Button>
              </Space>
            </div>
          </div>
        </div>
      )}
    />
  );
};

export default ExampleModal;
