import React from 'react';
import Chatbot from './components/Chatbot';
import './App.css';

function App() {
  return (
    <div className="App">
      {/* Your website content would go here */}
      <div className="website-content">
        <h1 className="website-title">Company Website</h1>
        <p className="website-description">This is where your main website content would appear.</p>
      </div>
      
      {/* Chatbot component */}
      <Chatbot />
    </div>
  );
}

export default App;