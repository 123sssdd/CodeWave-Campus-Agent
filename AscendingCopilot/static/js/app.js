// 全局变量
let currentSession = null;
let isWaitingForResponse = false;

// DOM元素
const chatArea = document.getElementById("chatArea");
const summaryArea = document.getElementById("summaryArea");
const messagesContainer = document.getElementById("messagesContainer");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const restartBtn = document.getElementById("restartBtn");
const newSessionBtn = document.getElementById("newSessionBtn");
const loadingOverlay = document.getElementById("loadingOverlay");
const knowledgeList = document.getElementById("knowledgeList");

// 初始化
document.addEventListener("DOMContentLoaded", function () {
  loadKnowledgeBase();
  setupEventListeners();
  setupDemoButton();
});

// 设置事件监听器
function setupEventListeners() {
  if (sendBtn) sendBtn.addEventListener("click", sendMessage);
  if (restartBtn) restartBtn.addEventListener("click", restartSession);
  if (newSessionBtn) newSessionBtn.addEventListener("click", showStartLearning);

  if (messageInput) {
    messageInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }
}

// 设置演示按钮
function setupDemoButton() {
  const demoBtn = document.getElementById("demoBtn");
  const demoBinarySearchBtn = document.getElementById("demoBinarySearchBtn");
  
  if (demoBtn) {
    demoBtn.addEventListener("click", playDemoAlgebra);
  }
  
  if (demoBinarySearchBtn) {
    demoBinarySearchBtn.addEventListener("click", playDemoBinarySearch);
  }
}

// 播放代数方程求解演示
async function playDemoAlgebra() {
  clearMessages();
  try {
    const res = await fetch("/api/demo_algebra");
    const data = await res.json();
    const script = data.script || [];
    for (let step of script) {
      if (step.action === "message") {
        await new Promise((r) => setTimeout(r, 1500));
        addMessage(step.content, step.type);
      } else if (step.action === "feedback") {
        await new Promise((r) => setTimeout(r, 1200));
        addFeedbackMessage(step.feedback, step.is_correct);
      } else if (step.action === "confidence") {
        await new Promise((r) => setTimeout(r, 800));
        addConfidenceMessage(step.confidence, step.threshold);
      } else if (step.action === "summary") {
        await new Promise((r) => setTimeout(r, 1800));
        showSummary(step.summary);
      }
    }
  } catch (e) {
    console.error("加载演示失败", e);
    showError("加载演示失败");
  }
}

// 播放二分查找演示
async function playDemoBinarySearch() {
  clearMessages();
  try {
    const res = await fetch("/api/demo_binary_search");
    const data = await res.json();
    const script = data.script || [];
    for (let step of script) {
      if (step.action === "message") {
        await new Promise((r) => setTimeout(r, 1500));
        addMessage(step.content, step.type);
      } else if (step.action === "feedback") {
        await new Promise((r) => setTimeout(r, 1200));
        addFeedbackMessage(step.feedback, step.is_correct);
      } else if (step.action === "confidence") {
        await new Promise((r) => setTimeout(r, 800));
        addConfidenceMessage(step.confidence, step.threshold);
      } else if (step.action === "summary") {
        await new Promise((r) => setTimeout(r, 1800));
        showSummary(step.summary);
      }
    }
  } catch (e) {
    console.error("加载二分查找演示失败", e);
    showError("加载二分查找演示失败");
  }
}

// 加载知识库
async function loadKnowledgeBase() {
  try {
    const response = await fetch("/api/knowledge_base");
    const data = await response.json();
    displayKnowledgeBase(data.patterns);
  } catch (error) {
    console.error("加载知识库失败:", error);
  }
}

// 显示知识库
function displayKnowledgeBase(patterns) {
  knowledgeList.innerHTML = "";

  patterns.forEach((pattern) => {
    const item = document.createElement("div");
    item.className = "knowledge-item";
    item.innerHTML = `
            <h4>${pattern.target_knowledge}</h4>
            <div class="category">${pattern.category}</div>
            <div class="description">${pattern.description}</div>
        `;

    item.addEventListener("click", () => {
      knowledgePointInput.value = pattern.target_knowledge;
    });

    knowledgeList.appendChild(item);
  });
}

// 开始学习会话
async function startLearningSession() {
  const knowledgePoint = knowledgePointInput.value.trim();

  if (!knowledgePoint) {
    showError("请输入要学习的知识点");
    return;
  }

  showLoading(true);

  try {
    const response = await fetch("/api/start_learning", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ knowledge_point: knowledgePoint }),
    });

    const data = await response.json();

    if (data.error) {
      showError(data.error);
      return;
    }

    currentSession = data.session_id;
    showChatArea();

    // 显示模拟消息
    if (data.simulation_messages) {
      for (let i = 0; i < data.simulation_messages.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 800));
        addMessage(
          data.simulation_messages[i].content,
          "ai",
          data.simulation_messages[i].timestamp
        );
      }
    }

    // 显示问题
    if (data.question) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      addMessage(data.question, "ai");
    }

    showInputArea();
  } catch (error) {
    console.error("开始学习失败:", error);
    showError("网络错误，请重试");
  } finally {
    showLoading(false);
  }
}

// 发送消息
async function sendMessage() {
  if (isWaitingForResponse) return;

  const message = messageInput.value.trim();
  if (!message) return;

  addMessage(message, "user");
  messageInput.value = "";

  isWaitingForResponse = true;
  sendBtn.disabled = true;

  try {
    const response = await fetch("/api/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ answer: message }),
    });

    const data = await response.json();

    if (data.error) {
      showError(data.error);
      return;
    }

    // 显示反馈
    addFeedbackMessage(data.feedback, data.is_correct);

    // 显示置信度信息
    if (data.confidence !== undefined) {
      addConfidenceMessage(data.confidence, data.confidence_threshold);
    }

    if (data.follow_up_question) {
      // 需要跟进提问
      await new Promise((resolve) => setTimeout(resolve, 1000));
      addMessage(data.follow_up_question, "ai");
    } else if (data.summary) {
      // 显示总结
      await new Promise((resolve) => setTimeout(resolve, 1000));
      showSummary(data.summary);
    }
  } catch (error) {
    console.error("发送消息失败:", error);
    showError("网络错误，请重试");
  } finally {
    isWaitingForResponse = false;
    sendBtn.disabled = false;
  }
}

// 发送跟进回答
async function sendFollowUpAnswer(message) {
  if (isWaitingForResponse) return;

  addMessage(message, "user");

  isWaitingForResponse = true;
  sendBtn.disabled = true;

  try {
    const response = await fetch("/api/follow_up_answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ answer: message }),
    });

    const data = await response.json();

    if (data.error) {
      showError(data.error);
      return;
    }

    // 显示反馈
    addFeedbackMessage(data.feedback, data.is_correct);

    // 显示总结
    await new Promise((resolve) => setTimeout(resolve, 1000));
    showSummary(data.summary);
  } catch (error) {
    console.error("发送跟进回答失败:", error);
    showError("网络错误，请重试");
  } finally {
    isWaitingForResponse = false;
    sendBtn.disabled = false;
  }
}

// 添加消息到对话区域
function addMessage(content, type, timestamp = null) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${type}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.innerHTML =
    type === "ai"
      ? '<i class="fas fa-robot"></i>'
      : '<i class="fas fa-user"></i>';

  const messageContent = document.createElement("div");
  messageContent.className = "message-content";
  messageContent.textContent = content;

  const messageTime = document.createElement("div");
  messageTime.className = "message-time";
  messageTime.textContent =
    timestamp ||
    new Date().toLocaleTimeString("zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(messageContent);
  messageDiv.appendChild(messageTime);

  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 添加反馈消息
function addFeedbackMessage(feedback, isCorrect) {
  const feedbackDiv = document.createElement("div");
  feedbackDiv.className = `feedback-message ${
    isCorrect ? "correct" : "incorrect"
  }`;
  feedbackDiv.textContent = feedback;

  messagesContainer.appendChild(feedbackDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 添加置信度消息
function addConfidenceMessage(confidence, threshold) {
  const confidenceDiv = document.createElement("div");
  confidenceDiv.className = "confidence-message";

  const confidencePercent = Math.round(confidence * 100);
  const thresholdPercent = Math.round(threshold * 100);

  let status = "";
  if (confidence >= threshold) {
    status = "✅ 置信度充足";
  } else {
    status = "⚠️ 置信度不足，触发追问";
  }

  confidenceDiv.innerHTML = `
    <div class="confidence-bar">
      <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
      <div class="confidence-threshold" style="left: ${thresholdPercent}%"></div>
    </div>
    <div class="confidence-text">
      <span>当前置信度: ${confidencePercent}%</span>
      <span>阈值: ${thresholdPercent}%</span>
      <span class="confidence-status">${status}</span>
    </div>
  `;

  messagesContainer.appendChild(confidenceDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 清空消息
function clearMessages() {
  messagesContainer.innerHTML = "";
  chatArea.style.display = "flex";
  summaryArea.style.display = "none";
}

// 显示聊天区域
function showChatArea() {
  chatArea.style.display = "flex";
  summaryArea.style.display = "none";

  // 清空消息容器
  messagesContainer.innerHTML = "";

  // 隐藏输入区域，等待模拟消息完成
  hideInputArea();
}

// 显示输入区域
function showInputArea() {
  const inputArea = document.getElementById("inputArea");
  inputArea.style.display = "block";
}

// 隐藏输入区域
function hideInputArea() {
  const inputArea = document.getElementById("inputArea");
  inputArea.style.display = "none";
}

// 显示总结
function showSummary(summary) {
  const summaryContent = document.getElementById("summaryContent");

  let insightsHtml = "";
  if (summary.learning_insights) {
    insightsHtml = `
      <div class="summary-section">
        <h4>📊 学习洞察</h4>
        ${summary.learning_insights
          .map((insight) => `<div class="insight-item">${insight}</div>`)
          .join("")}
      </div>
    `;
  }

  let lessonsHtml = "";
  if (summary.key_lessons) {
    lessonsHtml = `
      <div class="summary-section">
        <h4>🎯 关键教训</h4>
        ${summary.key_lessons
          .map((lesson) => `<div class="lesson-item">• ${lesson}</div>`)
          .join("")}
      </div>
    `;
  }

  let recommendationsHtml = "";
  if (summary.recommendations) {
    recommendationsHtml = `
      <div class="summary-section">
        <h4>💡 学习建议</h4>
        ${summary.recommendations
          .map((rec) => `<div class="recommendation-item">${rec}</div>`)
          .join("")}
      </div>
    `;
  }

  summaryContent.innerHTML = `
        <div class="summary-item">
            <span class="summary-label">知识点:</span>
            <span class="summary-value">${summary.knowledge}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">错误模式:</span>
            <span class="summary-value">${summary.pattern}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">关键教训:</span>
            <span class="summary-value">${summary.explanation}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">正确方法:</span>
            <span class="summary-value">${summary.correct_method}</span>
        </div>
        
        <div class="accuracy-display">
            <div class="accuracy-number">${summary.accuracy.toFixed(1)}%</div>
            <div class="accuracy-label">准确率</div>
            <div class="confidence-final">最终置信度: ${Math.round(
              summary.confidence_final * 100
            )}%</div>
        </div>
        
        <div class="summary-item">
            <span class="summary-label">正确回答:</span>
            <span class="summary-value">${summary.correct_answers} 次</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">错误回答:</span>
            <span class="summary-value">${summary.incorrect_answers} 次</span>
        </div>

        ${insightsHtml}
        ${lessonsHtml}
        ${recommendationsHtml}
    `;

  chatArea.style.display = "none";
  summaryArea.style.display = "flex";
}

// 显示开始学习界面
function showStartLearning() {
  // 由于移除了欢迎界面，直接清空消息并显示对话区域
  clearMessages();
  currentSession = null;
}

// 重新开始会话
function restartSession() {
  if (currentSession) {
    showStartLearning();
  }
}

// 显示加载动画
function showLoading(show) {
  loadingOverlay.style.display = show ? "flex" : "none";
}

// 显示错误消息
function showError(message) {
  // 创建错误提示
  const errorDiv = document.createElement("div");
  errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #fed7d7;
        border: 1px solid #feb2b2;
        color: #c53030;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1001;
        max-width: 300px;
        animation: slideInRight 0.3s ease;
    `;
  errorDiv.textContent = message;

  document.body.appendChild(errorDiv);

  // 3秒后自动移除
  setTimeout(() => {
    errorDiv.style.animation = "slideOutRight 0.3s ease";
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.parentNode.removeChild(errorDiv);
      }
    }, 300);
  }, 3000);
}

// 添加CSS动画
const style = document.createElement("style");
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
