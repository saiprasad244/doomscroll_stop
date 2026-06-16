import React, { useState, useEffect, useRef } from 'react';
import { Send, User, BrainCircuit, Sparkles } from 'lucide-react';

export function HabitCoach() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'coach',
      text: "Hello! I am your AI Habit Coach. Reclaiming your attention takes deliberate practice. What habit would you like to discuss today?\n\nTry asking me: \n• *'How can I stop doomscrolling?'*\n• *'Give me a productivity plan.'*\n• *'How can I reduce screen time?'*"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatBottomRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    // Add user message
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:5000/api/coach', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: query })
      });
      const data = await response.json();
      
      if (response.ok) {
        const coachMsg = {
          id: Date.now() + 1,
          sender: 'coach',
          text: data.reply
        };
        setMessages(prev => [...prev, coachMsg]);
      } else {
        throw new Error(data.message || 'Failed to contact coach.');
      }
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'coach',
        text: "I'm having trouble connecting to the network right now. Make sure the backend Flask server is running and try again."
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const handleQuickQuestion = (q) => {
    handleSend(q);
  };

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col justify-between">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 dark:from-white dark:via-brand-200 dark:to-accent-200 bg-clip-text text-transparent flex items-center gap-2">
          AI Habit Coach
          <Sparkles className="w-5 h-5 text-brand-400 animate-pulse" />
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
          Chat with our AI Coach to build personalized schedules, configure routines, and stop screen addiction.
        </p>
      </div>

      {/* Chat Conversation Thread */}
      <div className="flex-1 glass-card p-6 border-brand-500/10 overflow-y-auto mb-4 flex flex-col gap-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 max-w-[80%] ${
              msg.sender === 'user' ? 'self-end flex-row-reverse' : 'self-start'
            }`}
          >
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${
              msg.sender === 'user' 
                ? 'bg-brand-500 text-white border-brand-600' 
                : 'bg-slate-200 dark:bg-slate-900 border-slate-350 dark:border-slate-800 text-slate-600 dark:text-slate-400'
            }`}>
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <BrainCircuit className="w-4 h-4" />}
            </div>

            {/* Text Bubble */}
            <div className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
              msg.sender === 'user'
                ? 'bg-brand-600 text-white rounded-tr-none'
                : 'bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200/50 dark:border-slate-850 rounded-tl-none'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-start gap-3 self-start">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-slate-200 dark:bg-slate-900 border border-slate-350 dark:border-slate-800 text-slate-650 dark:text-slate-450">
              <BrainCircuit className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-900 text-slate-500 dark:text-slate-400 border border-slate-200/50 dark:border-slate-850 rounded-tl-none flex items-center gap-2 text-xs font-semibold">
              Coach is mapping triggers
              <span className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-slate-455 rounded-full animate-bounce"></span>
                <span className="w-1.5 h-1.5 bg-slate-455 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                <span className="w-1.5 h-1.5 bg-slate-455 rounded-full animate-bounce [animation-delay:0.4s]"></span>
              </span>
            </div>
          </div>
        )}
        <div ref={chatBottomRef} />
      </div>

      {/* Input panel with suggestions */}
      <div className="space-y-4">
        {messages.length === 1 && !loading && (
          <div className="flex flex-wrap gap-2">
            {[
              "How can I stop doomscrolling?",
              "Give me a productivity plan.",
              "How can I reduce screen time?"
            ].map((q) => (
              <button
                key={q}
                onClick={() => handleQuickQuestion(q)}
                className="px-3.5 py-1.5 rounded-full bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-xs font-semibold transition-colors duration-200"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask your Coach about reducing screen time or building deep focus..."
            className="flex-1 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-sm focus:outline-none focus:border-brand-500 text-slate-800 dark:text-white"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="px-5 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white flex items-center justify-center shadow-lg shadow-brand-600/10 transition-colors disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
export default HabitCoach;
