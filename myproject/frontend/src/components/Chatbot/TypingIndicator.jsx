import React from 'react';
import { motion } from 'framer-motion';
import './Chatbot.css';

const TypingIndicator = () => {
  return (
    <div className="typing-container">
     
      {/* Typing dots */}
      <div className="typing-dots">
        <motion.div
          className="typing-dot"
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, delay: 0 }}
        />
        <motion.div
          className="typing-dot"
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }}
        />
        <motion.div
          className="typing-dot"
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, delay: 0.4 }}
        />
      </div>
    </div>
  );
};

export default TypingIndicator;