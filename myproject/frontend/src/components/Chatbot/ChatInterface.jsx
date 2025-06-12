import React, { useState, useEffect, useRef } from 'react';
import { Player } from '@lottiefiles/react-lottie-player';
import Send from '@mui/icons-material/Send';
import Close from '@mui/icons-material/Close';
import Message from './Message';
import TypingIndicator from './TypingIndicator';
import animationData from '../../animations/chatbot-waving.json';
import './Chatbot.css';

const ChatInterface = ({ onClose, hideWidget }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    hideWidget();
  }, [hideWidget]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;

    const userMessage = {
      text: inputValue,
      isBot: false,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    //  backend URL
     fetch('http://127.0.0.1:8000/query_with_retrieval/',{
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ question: userMessage.text }),
    })
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then(data => {
        setMessages(prev => [
          ...prev,
          {
            text: data.answer || "Sorry, I couldn't find an answer.",
            isBot: true,
          },
        ]);
      })
      .catch(error => {
        setMessages(prev => [
          ...prev,
          {
            text: "Oops! Something went wrong. Please try again later.",
            isBot: true,
          },
        ]);
        console.error('Error:', error);
      })
      .finally(() => {
        setIsTyping(false);
      });
  };

  const handleGetStarted = () => {
    setShowWelcome(false);
    setIsTyping(true);

    setTimeout(() => {
      setMessages([{
        text: "Hello! I'm your company assistant. You can ask me anything about our products, services, or company information. How can I help you today?",
        isBot: true,
      }]);
      setIsTyping(false);
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chat-interface-overlay">
      <div className="chat-interface">
        {/* Header */}
        <div className="chat-header">
          <h2 className="chat-title">Company Assistant</h2>
          <button onClick={onClose} className="close-button">
            <Close />
          </button>
        </div>

        {/* Chat Area */}
        <div className="chat-messages scrollable-chat">
          {showWelcome ? (
            <div className="welcome-screen">
              <Player
                autoplay
                loop
                src={animationData}
                style={{ width: '200px', height: '200px' }}
              />
              <h3 className="welcome-title">Hello! I'm your Company ChatBot</h3>
              <p className="welcome-text">
                I can help answer any questions you have about our company, products, or services. 
                Whether you need information about our team, pricing, or features, I'm here to assist!
              </p>
              <button
                onClick={handleGetStarted}
                className="get-started-button"
              >
                Get Started
              </button>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <Message
                  key={index}
                  message={message.text}
                  isBot={message.isBot}
                />
              ))}
              {isTyping && (
                <TypingIndicator />
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        {!showWelcome && (
          <div className="chat-input-container">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask something about our company..."
              className="chat-input"
            />
            <button
              onClick={handleSendMessage}
              disabled={inputValue.trim() === ''}
              className={`send-button ${inputValue.trim() === '' ? 'disabled' : ''}`}
            >
              <Send />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
