'use client';
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

type Message = { role: 'user' | 'bot'; content: string };

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // SUCCESS: Now calling the local Next.js API Route Proxy
      const { data } = await axios.post('/api/chat', {
        user_input: input,
        session_id: "nextjs-demo"
      });

      // Update messages with the response from the proxy
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        content: data.response // Matches the FastAPI response key
      }]);
    } catch (error) {
      console.error("Chat Error:", error);
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        content: "Sorry, I'm having trouble connecting to the service." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex flex-col h-screen bg-gray-50 max-w-2xl mx-auto shadow-xl">
      <header className="p-4 bg-blue-600 text-white font-bold text-center border-b shadow-sm">
        AI Chat Assistant
      </header>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white/50">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-10">
            Start a conversation with the AI!
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-2xl shadow-sm ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-none' 
                : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
             <div className="bg-gray-200 text-gray-500 p-3 rounded-2xl rounded-tl-none animate-pulse text-sm">
               Bot is thinking...
             </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t bg-white flex gap-2 items-center">
        <input
          className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-700"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything..."
          disabled={isLoading}
        />
        <button 
          onClick={handleSend}
          className="bg-blue-600 text-white p-2 w-10 h-10 rounded-full hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center transition-colors"
          disabled={isLoading || !input.trim()}
        >
          {/* Simple Send Arrow Icon */}
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
    </main>
  );
}