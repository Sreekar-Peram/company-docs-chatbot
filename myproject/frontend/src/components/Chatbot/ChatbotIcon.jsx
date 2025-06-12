import React from 'react';
import { Player } from '@lottiefiles/react-lottie-player';
import animationData from '../../animations/chatbot-icon.json';
import './Chatbot.css';

const ChatbotIcon = ({ onClick, visible }) => {
  if (!visible) return null;
  
  return (
    <div 
      className="chatbot-icon"
      onClick={onClick}
    >
      <Player
        autoplay
        loop
        src={animationData}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default ChatbotIcon;