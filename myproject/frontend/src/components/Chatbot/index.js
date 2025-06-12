import React, { useState } from 'react';
import ChatbotIcon from './ChatbotIcon';
import ChatInterface from './ChatInterface';
import './Chatbot.css';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [iconVisible, setIconVisible] = useState(true);

  const handleOpen = () => {
    setIsOpen(true);
    setIconVisible(false); // Hide the widget immediately when clicked
  };

  const handleClose = () => {
    setIsOpen(false);
    setIconVisible(true); // Show widget again when chat is closed
  };

  return (
    <>
      <ChatbotIcon onClick={handleOpen} visible={iconVisible} />
      {isOpen && <ChatInterface onClose={handleClose} hideWidget={() => setIconVisible(false)} />}
    </>
  );
};

export default Chatbot;