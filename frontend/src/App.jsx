import { useState, useRef, useEffect } from 'react';
import { Send, Shield, Bot, AlertTriangle } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'agent',
      content: 'Hello! I am the SupportProof AI Agent. How can I assist you today?',
      escalate: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Mock service to simulate the Python backend agent
  const mockAgentResponse = async (userMessage) => {
    // Determine mock behavior based on keywords
    let reply = 'Could you please provide more details?';
    let escalate = false;
    let escalateReason = '';

    const lowerMsg = userMessage.toLowerCase();
    
    if (lowerMsg.includes('refund') || lowerMsg.includes('damaged') || lowerMsg.includes('missing')) {
      reply = "I'm sorry you're experiencing issues. Please provide your order number so I can investigate and arrange a refund.";
      escalate = true;
      escalateReason = "Requires human investigation and refund processing.";
    } else if (lowerMsg.includes('http') || lowerMsg.includes('link')) {
      reply = "Please wait while I connect you to a human agent to resolve this securely.";
      escalate = true;
      escalateReason = "Grounding Validation Failure: URLs are prohibited in AI responses.";
    } else if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
      reply = "Hi there! How can I help you with your Amazon order today?";
    }

    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ reply, escalate, escalateReason });
      }, 1500 + Math.random() * 1000); // Simulate network/LLM delay (1.5s - 2.5s)
    });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMsg = inputValue.trim();
    setInputValue('');
    
    // Add user message
    const newUserMsg = { id: Date.now(), role: 'user', content: userMsg };
    setMessages(prev => [...prev, newUserMsg]);
    setIsTyping(true);

    // Call mock backend (Replace this with actual fetch to Python API later)
    const agentData = await mockAgentResponse(userMsg);
    
    setIsTyping(false);
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'agent',
      content: agentData.reply,
      escalate: agentData.escalate,
      escalateReason: agentData.escalateReason
    }]);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-icon">
          <Shield color="white" size={24} />
        </div>
        <div>
          <h1>SupportProof</h1>
          <p>AI Customer Service Agent</p>
        </div>
      </header>

      {/* Chat Area */}
      <div className="chat-window">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.role}`}>
            <div className={`message ${msg.role}`}>
              {/* Escalation Badge for Agent */}
              {msg.role === 'agent' && msg.escalate && (
                <div className="escalate-badge">
                  <AlertTriangle size={16} />
                  <span>Escalated to Human: {msg.escalateReason}</span>
                </div>
              )}
              
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                {msg.role === 'agent' && (
                  <div style={{ marginTop: '2px', color: 'var(--accent)' }}>
                    <Bot size={20} />
                  </div>
                )}
                <div style={{ wordBreak: 'break-word' }}>{msg.content}</div>
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="message-wrapper agent">
            <div className="message agent">
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <div style={{ color: 'var(--accent)' }}>
                  <Bot size={20} />
                </div>
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-area">
        <form className="input-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            disabled={isTyping}
            autoFocus
          />
          <button type="submit" className="send-btn" disabled={!inputValue.trim() || isTyping}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}
