import React from 'react';
import ChatBox from './ChatBox';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Film RAG Chat
        </h1>
        <ChatBox />
      </div>
    </div>
  );
}

export default App; 