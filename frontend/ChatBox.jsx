// src/components/ChatBox.jsx
import React, { useState } from "react";
import axios from "axios";

function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  async function sendMessage() {
    if (!input.trim()) return;
    
    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
    try {
      const res = await axios.post("http://localhost:8000/ask", {
        question: input,
      });
      setMessages((prev) => [...prev, { role: "bot", content: res.data.answer }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", content: "❌ Error fetching response" }]);
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="p-4 max-w-lg mx-auto">
      <div className="space-y-2 h-80 overflow-y-auto border p-2">
        {messages.map((m, i) => (
          <div key={i} className={`text-${m.role === "user" ? "right" : "left"}`}>
            <span className="block bg-gray-200 rounded p-1">{m.content}</span>
          </div>
        ))}
      </div>
      <div className="flex mt-2">
        <input
          className="flex-1 border rounded p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask something about films..."
        />
        <button className="ml-2 bg-blue-500 text-white p-2 rounded" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatBox;
