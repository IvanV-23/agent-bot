'use client';
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

type Message = { 
  role: 'user' | 'bot'; 
  content: string; 
  tool?: string; 
};

/**
 * A sub-component to render the weather data visually.
 * It parses the text response from the backend using regex.
 */
const WeatherWidget = ({ data }: { data: string }) => {
  // Extract values from the string format provided by your tool
  const temp = data.match(/Current: ([\d.]+)°C/)?.[1] || "--";
  const status = data.match(/Detailed status: ([\w\s]+)/)?.[1] || "unknown";
  const humidity = data.match(/Humidity: (\d+)%/)?.[1] || "--";
  const location = data.match(/In ([\w\s]+),/)?.[1] || "Location";
  const wind = data.match(/Wind speed: ([\d.]+)/)?.[1] || "0";

  // Simple icon mapper based on the "Detailed status"
  const getIcon = (status: string) => {
    const s = status.toLowerCase();
    if (s.includes('sun') || s.includes('clear')) return '☀️';
    if (s.includes('cloud')) return '☁️';
    if (s.includes('rain')) return '🌧️';
    if (s.includes('snow')) return '❄️';
    return '🌡️';
  };

  return (
    <div className="bg-gradient-to-br from-blue-500 to-blue-700 text-white p-5 rounded-2xl shadow-lg w-full max-w-[280px] my-2 border border-blue-400">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-xs opacity-80 uppercase font-bold tracking-widest mb-1">{location}</p>
          <h2 className="text-5xl font-extrabold">{Math.round(Number(temp))}°</h2>
        </div>
        <div className="text-5xl animate-bounce-slow">
           {getIcon(status)}
        </div>
      </div>
      <p className="capitalize font-medium text-lg mb-4">{status}</p>
      <div className="grid grid-cols-2 gap-2 text-xs bg-white/10 p-3 rounded-xl backdrop-blur-sm">
        <div className="flex flex-col">
          <span className="opacity-70">Humidity</span>
          <span className="font-bold text-sm">{humidity}%</span>
        </div>
        <div className="flex flex-col">
          <span className="opacity-70">Wind</span>
          <span className="font-bold text-sm">{wind} m/s</span>
        </div>
      </div>
    </div>
  );
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

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
      const { data } = await axios.post('/api/chat', {
        user_input: input,
        session_id: "nextjs-demo"
      });

      // KEY FIX: Make sure to capture the 'tool' field from your FastAPI response
      setMessages((prev) => [...prev, { 
        role: 'bot', 
        content: data.response,
        tool: data.tool // This matches the 'tool' key in your JSON snippet
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
    <main className="flex flex-col h-screen bg-gray-100 max-w-2xl mx-auto shadow-2xl border-x border-gray-200">
      <header className="p-4 bg-white border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <h1 className="font-bold text-gray-800 tracking-tight">AI Assistant</h1>
        </div>
        <span className="text-xs text-gray-400 font-mono">v1.0.4</span>
      </header>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-2 opacity-60">
            <span className="text-4xl">👋</span>
            <p className="text-sm font-medium">How can I help you today?</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-4 rounded-2xl transition-all ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-none shadow-blue-200 shadow-lg' 
                : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none shadow-sm'
            }`}>
              {/* Conditional Rendering: Check if the 'weather' tool was used */}
              {msg.tool === 'weather' ? (
                <div className="space-y-3">
                  <p className="text-sm border-b pb-2 mb-2 border-gray-100 font-medium">
                    I found the current weather for you:
                  </p>
                  <WeatherWidget data={msg.content} />
                </div>
              ) : (
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 p-4 rounded-2xl rounded-tl-none flex items-center gap-2 shadow-sm">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:-.3s]"></div>
                <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:-.5s]"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t">
        <div className="flex gap-2 items-center bg-gray-50 p-1 rounded-full border border-gray-200 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent transition-all">
          <input
            className="flex-1 bg-transparent px-4 py-2 focus:outline-none text-gray-700 placeholder-gray-400"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type a message..."
            disabled={isLoading}
          />
          <button 
            onClick={handleSend}
            className="bg-blue-600 text-white p-2 w-10 h-10 rounded-full hover:bg-blue-700 disabled:opacity-30 flex items-center justify-center transition-all shadow-md active:scale-95"
            disabled={isLoading || !input.trim()}
          >
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        </div>
      </div>
    </main>
  );
}