import React from 'react';
import './Chatbot.css';
import TypingIndicator from './TypingIndicator';


const Message = ({ message, isBot, isTyping }) => {
  return (
    <div className={`message-container ${isBot ? 'bot-message' : 'user-message'}`}>
      {isBot && isTyping ? (
        <div className="typing-message-container">
          <div className="typing-message">
            {isTyping && (
              <div className="typing-wrapper">
                <TypingIndicator />
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className={`message-bubble ${isBot ? 'bot-bubble' : 'user-bubble'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default Message;