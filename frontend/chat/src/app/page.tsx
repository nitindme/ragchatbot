'use client';

import { useState, useEffect, useRef } from 'react';
import { startSession, sendMessage, getChatHistory, submitFeedback } from '@/lib/api';

interface Message {
  id: string;
  role: string;
  message: string;
  created_at: string;
  message_id?: number;
  sources?: string[];
  retrieved_chunks?: any[];
  feedback?: number; // 1 = thumbs up, -1 = thumbs down, null = no feedback
  userQuestion?: string; // Store the user's original question for feedback
}

export default function ChatPage() {
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const parseMessageWithCitations = (message: string) => {
    // Split message by citation separator
    const parts = message.split('\n---\n');
    if (parts.length === 1) {
      return { content: message, citations: [] };
    }
    
    const content = parts[0];
    const citationSection = parts[1] || '';
    
    // Extract citations
    const citations: string[] = [];
    const lines = citationSection.split('\n');
    for (const line of lines) {
      if (line.startsWith('• ')) {
        citations.push(line.substring(2));
      }
    }
    
    return { content, citations };
  };

  const initSession = async () => {
    try {
      const sid = await startSession();
      setSessionId(sid);
    } catch (error) {
      console.error('Failed to start session:', error);
    } finally {
      setInitializing(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !sessionId || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message immediately
    const tempUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      message: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendMessage(sessionId, userMessage);
      
      // Add assistant message with metadata for feedback
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        message: response.message,
        created_at: new Date().toISOString(),
        message_id: response.message_id,
        sources: response.sources,
        retrieved_chunks: response.retrieved_chunks,
        userQuestion: userMessage, // Store the question for feedback
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (messageId: string, rating: number) => {
    const message = messages.find(m => m.id === messageId);
    if (!message || !message.message_id || !message.userQuestion) return;

    try {
      await submitFeedback({
        session_id: sessionId,
        message_id: message.message_id,
        question: message.userQuestion,
        response: message.message,
        rating,
        sources: message.sources,
        retrieved_chunks: message.retrieved_chunks,
      });

      // Update message with feedback
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { ...m, feedback: rating } : m
      ));

      console.log(`Feedback ${rating > 0 ? 'positive' : 'negative'} submitted successfully`);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const handleNewChat = async () => {
    setMessages([]);
    setInput('');
    setLoading(false);
    try {
      const sid = await startSession();
      setSessionId(sid);
    } catch (error) {
      console.error('Failed to start new session:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (initializing) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Initializing chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-[#343541]">
      {/* Header - ChatGPT style */}
      <div className="bg-[#343541] border-b border-gray-700/50 px-4 py-3">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">Delhi Police Assistant</h1>
              <p className="text-xs text-gray-400">AI-powered document Q&A</p>
            </div>
          </div>
          <button
            onClick={handleNewChat}
            className="px-4 py-2 text-sm text-gray-300 hover:text-white border border-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
          >
            New Chat
          </button>
        </div>
      </div>

      {/* Messages - ChatGPT style */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">How can I help you today?</h2>
              <p className="text-gray-400">Ask me anything about Delhi Police documents and regulations</p>
              
              {/* Example prompts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-8 max-w-2xl mx-auto">
                <button
                  onClick={() => setInput("What is the dress code for training?")}
                  className="p-4 bg-[#444654] hover:bg-[#505060] rounded-xl text-left transition-colors"
                >
                  <p className="text-sm text-white font-medium mb-1">Dress Code</p>
                  <p className="text-xs text-gray-400">What is the dress code for training?</p>
                </button>
                <button
                  onClick={() => setInput("What are the training requirements?")}
                  className="p-4 bg-[#444654] hover:bg-[#505060] rounded-xl text-left transition-colors"
                >
                  <p className="text-sm text-white font-medium mb-1">Training Info</p>
                  <p className="text-xs text-gray-400">What are the training requirements?</p>
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={msg.id}
              className={`py-6 ${msg.role === 'assistant' ? 'bg-[#444654]' : ''}`}
            >
              <div className="max-w-3xl mx-auto px-4">
                <div className="flex gap-4">
                  {/* Avatar */}
                  <div className="flex-shrink-0">
                    {msg.role === 'user' ? (
                      <div className="w-8 h-8 bg-blue-600 rounded-sm flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                    ) : (
                      <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-cyan-400 rounded-sm flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                    )}
                  </div>
                  
                  {/* Message content */}
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-white">
                        {msg.role === 'user' ? 'You' : 'Delhi Police Assistant'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-gray-100 leading-relaxed whitespace-pre-wrap">
                      {(() => {
                        const { content, citations } = parseMessageWithCitations(msg.message);
                        return (
                          <>
                            <div>{content}</div>
                            {citations.length > 0 && (
                              <div className="mt-4 pt-3 border-t border-gray-600">
                                <div className="flex items-start gap-2">
                                  <svg className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                  </svg>
                                  <div className="flex-1">
                                    <p className="text-xs font-semibold text-gray-400 mb-1">Sources</p>
                                    <div className="space-y-1">
                                      {citations.map((citation, idx) => (
                                        <div key={idx} className="text-xs text-gray-300 bg-gray-700/30 px-2 py-1 rounded">
                                          📄 {citation}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                    
                    {/* Feedback buttons for assistant messages */}
                    {msg.role === 'assistant' && msg.message_id && (
                      <div className="flex items-center gap-2 mt-3">
                        <span className="text-xs text-gray-500">Was this helpful?</span>
                        <button
                          onClick={() => handleFeedback(msg.id, 1)}
                          disabled={msg.feedback !== undefined}
                          className={`p-1.5 rounded transition-colors ${
                            msg.feedback === 1
                              ? 'bg-green-600 text-white'
                              : 'text-gray-400 hover:text-green-400 hover:bg-gray-700'
                          } disabled:cursor-not-allowed`}
                          title="Thumbs up"
                        >
                          <svg className="w-4 h-4" fill={msg.feedback === 1 ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, -1)}
                          disabled={msg.feedback !== undefined}
                          className={`p-1.5 rounded transition-colors ${
                            msg.feedback === -1
                              ? 'bg-red-600 text-white'
                              : 'text-gray-400 hover:text-red-400 hover:bg-gray-700'
                          } disabled:cursor-not-allowed`}
                          title="Thumbs down"
                        >
                          <svg className="w-4 h-4" fill={msg.feedback === -1 ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                          </svg>
                        </button>
                        {msg.feedback && (
                          <span className="text-xs text-gray-500 ml-1">
                            Thank you for your feedback!
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="py-6 bg-[#444654]">
              <div className="max-w-3xl mx-auto px-4">
                <div className="flex gap-4">
                  <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-cyan-400 rounded-sm flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input - ChatGPT style */}
      <div className="border-t border-gray-700/50 bg-[#343541] pb-6 pt-4">
        <div className="max-w-3xl mx-auto px-4">
          <div className="relative bg-[#40414f] rounded-xl shadow-lg border border-gray-700/50">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Send a message..."
              disabled={loading}
              rows={1}
              className="w-full px-4 py-4 pr-12 bg-transparent text-white placeholder-gray-400 resize-none focus:outline-none max-h-40"
              style={{ minHeight: '52px' }}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="absolute right-2 bottom-2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <p className="text-xs text-gray-500 text-center mt-3">
            This assistant provides information based on uploaded documents. Always verify critical information with official sources.
          </p>
        </div>
      </div>
    </div>
  );
}
