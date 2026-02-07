/**
 * ChatInterface Component
 * A persistent chat sidebar for conversational AI interactions with the advisory system.
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
    MessageSquare,
    Send,
    X,
    Minimize2,
    Maximize2,
    Sparkles,
    User,
    Bot,
    Loader2,
    ChevronDown,
    RefreshCw
} from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    data?: any;
    followUpSuggestions?: string[];
    isLoading?: boolean;
}

interface ChatInterfaceProps {
    isOpen: boolean;
    onToggle: () => void;
    className?: string;
}

const API_BASE = 'http://localhost:8000/api';

export default function ChatInterface({ isOpen, onToggle, className = '' }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'welcome',
            role: 'assistant',
            content: "👋 Hello! I'm your Advisory Assistant. I can help you with:\n\n• **Investment Analysis** - Equity allocations, ISA allowances, protection gaps\n• **Client Insights** - Overdue reviews, business opportunities, estate planning\n• **Compliance** - Recommendation history, risk discussions, promised items\n• **Follow-ups** - Email drafting, open actions, overdue tasks\n\nHow can I help you today?",
            timestamp: new Date(),
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [isMinimized, setIsMinimized] = useState(false);
    const [showScrollButton, setShowScrollButton] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const messagesContainerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, []);

    useEffect(() => {
        if (!isLoading) {
            scrollToBottom();
        }
    }, [messages, isLoading, scrollToBottom]);

    useEffect(() => {
        if (isOpen && !isMinimized) {
            inputRef.current?.focus();
        }
    }, [isOpen, isMinimized]);

    const handleScroll = useCallback(() => {
        if (messagesContainerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
            setShowScrollButton(scrollHeight - scrollTop - clientHeight > 100);
        }
    }, []);

    const sendMessage = async (messageContent: string) => {
        if (!messageContent.trim() || isLoading) return;

        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: messageContent.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        // Add a loading message
        const loadingId = `loading-${Date.now()}`;
        setMessages(prev => [...prev, {
            id: loadingId,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            isLoading: true,
        }]);

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageContent.trim(),
                    session_id: sessionId,
                }),
            });

            const data = await response.json();

            // Remove loading message and add actual response
            setMessages(prev => {
                const filtered = prev.filter(m => m.id !== loadingId);
                return [...filtered, {
                    id: `assistant-${Date.now()}`,
                    role: 'assistant',
                    content: data.message || 'I apologize, but I encountered an issue processing your request.',
                    timestamp: new Date(),
                    data: data.data,
                    followUpSuggestions: data.follow_up_suggestions,
                }];
            });

            if (data.session_id) {
                setSessionId(data.session_id);
            }
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => {
                const filtered = prev.filter(m => m.id !== loadingId);
                return [...filtered, {
                    id: `error-${Date.now()}`,
                    role: 'assistant',
                    content: '❌ I apologize, but I encountered an error connecting to the server. Please check that the backend is running and try again.',
                    timestamp: new Date(),
                }];
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendMessage(input);
    };

    const handleFollowUp = (suggestion: string) => {
        sendMessage(suggestion);
    };

    const handleNewChat = () => {
        setSessionId(null);
        setMessages([{
            id: 'welcome-new',
            role: 'assistant',
            content: "✨ Starting a fresh conversation. How can I help you?",
            timestamp: new Date(),
        }]);
    };

    const formatContent = (content: string) => {
        // Simple markdown-like formatting
        return content
            .split('\n')
            .map((line, i) => {
                // Bold text
                line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                // Italic text
                line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
                // Code
                line = line.replace(/`(.*?)`/g, '<code class="bg-white/5 border border-white/10 px-1 rounded text-xs font-mono">$1</code>');

                return (
                    <span key={i} dangerouslySetInnerHTML={{ __html: line || '&nbsp;' }} />
                );
            })
            .reduce((acc: React.ReactNode[], curr, i) => {
                if (i > 0) acc.push(<br key={`br-${i}`} />);
                acc.push(curr);
                return acc;
            }, []);
    };

    if (!isOpen) {
        return (
            <button
                onClick={onToggle}
                className={`fixed bottom-8 right-8 w-14 h-14 bg-primary-600 rounded-full shadow-glow flex items-center justify-center text-white 
                   hover:bg-primary-500 transition-all duration-500 hover:scale-110 z-50 group ${className}`}
                aria-label="Open chat"
            >
                <div className="absolute inset-0 bg-primary-400 rounded-full animate-ping opacity-20 group-hover:opacity-40" />
                <MessageSquare className="w-6 h-6 relative z-10" />
                <span className="absolute top-0 right-0 w-3.5 h-3.5 bg-primary-500 rounded-full border-2 border-background z-20 flex items-center justify-center">
                    <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                </span>
            </button>
        );
    }

    return (
        <div
            className={`fixed right-8 bottom-8 w-[400px] glass rounded-3xl shadow-2xl 
                 border border-white/5 flex flex-col z-50 transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]
                 ${isMinimized ? 'h-16' : 'h-[650px]'} ${className}`}
        >
            <div className="absolute inset-0 bg-primary-500/5 blur-[100px] rounded-full pointer-events-none" />

            {/* Header */}
            <div
                className="flex items-center justify-between px-5 py-4 glass-glow-blue 
                   rounded-t-[22px] border-b border-white/5 cursor-pointer relative z-10"
                onClick={() => isMinimized && setIsMinimized(false)}
            >
                <div className="flex items-center gap-4">
                    <div className="w-9 h-9 bg-primary-600/20 border border-primary-500/30 rounded-xl flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-primary-400" />
                    </div>
                    <div>
                        <h3 className="text-white font-bold text-sm tracking-tight text-gradient-blue uppercase">Neural Link</h3>
                        <p className="text-muted text-[10px] font-bold uppercase tracking-widest mt-0.5">Tactical Interface</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => { e.stopPropagation(); handleNewChat(); }}
                        className="p-2 text-muted hover:text-white hover:bg-white/5 rounded-lg transition-all"
                        title="Reset Protocol"
                    >
                        <RefreshCw className="w-4 h-4" />
                    </button>
                    <button
                        onClick={(e) => { e.stopPropagation(); setIsMinimized(!isMinimized); }}
                        className="p-2 text-muted hover:text-white hover:bg-white/5 rounded-lg transition-all"
                    >
                        {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
                    </button>
                    <button
                        onClick={onToggle}
                        className="p-2 text-muted hover:text-white hover:bg-white/5 rounded-lg transition-all"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {!isMinimized && (
                <>
                    {/* Messages */}
                    <div
                        ref={messagesContainerRef}
                        onScroll={handleScroll}
                        className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin relative z-10"
                    >
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex gap-4 animate-reveal ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center border
                              ${message.role === 'user'
                                        ? 'bg-primary-600 border-primary-500 shadow-glow-sm'
                                        : 'bg-white/5 border-white/10'}`}
                                >
                                    {message.role === 'user'
                                        ? <User className="w-4 h-4 text-white" />
                                        : <Bot className="w-4 h-4 text-primary-400" />
                                    }
                                </div>
                                <div className={`max-w-[85%] ${message.role === 'user' ? 'text-right' : ''}`}>
                                    <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
                                ${message.role === 'user'
                                            ? 'glass-glow-blue text-white rounded-tr-none'
                                            : 'glass border-white/5 text-white/90 rounded-tl-none'}`}
                                    >
                                        {message.isLoading ? (
                                            <div className="flex items-center gap-3">
                                                <div className="flex gap-1.5">
                                                    <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                                    <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                                    <span className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-bounce" />
                                                </div>
                                                <span className="text-muted text-xs font-bold uppercase tracking-wider">Syncing...</span>
                                            </div>
                                        ) : (
                                            <div className="whitespace-pre-wrap">{formatContent(message.content)}</div>
                                        )}
                                    </div>

                                    {/* Follow-up suggestions */}
                                    {message.followUpSuggestions && message.followUpSuggestions.length > 0 && (
                                        <div className="mt-3 flex flex-wrap gap-2 justify-start">
                                            {message.followUpSuggestions.map((suggestion, i) => (
                                                <button
                                                    key={i}
                                                    onClick={() => handleFollowUp(suggestion)}
                                                    disabled={isLoading}
                                                    className="text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 glass-glow-blue text-primary-400 rounded-lg 
                                   hover:bg-primary-500/20 hover:text-white transition-all 
                                   border border-primary-500/20 disabled:opacity-50"
                                                >
                                                    {suggestion}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                    <p className="text-[10px] font-bold text-muted uppercase tracking-widest mt-2 px-1">
                                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </p>
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Scroll to bottom button */}
                    {showScrollButton && (
                        <button
                            onClick={scrollToBottom}
                            className="absolute bottom-20 left-1/2 -translate-x-1/2 p-2 bg-gray-700 
                       rounded-full shadow-lg hover:bg-gray-600 transition-colors"
                        >
                            <ChevronDown className="w-4 h-4 text-white" />
                        </button>
                    )}

                    {/* Input */}
                    <form onSubmit={handleSubmit} className="p-5 border-t border-white/5 relative z-10 bg-black/20">
                        <div className="flex items-center gap-3">
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Command AI assistant..."
                                disabled={isLoading}
                                className="flex-1 glass text-white rounded-xl px-5 py-3.5 text-sm
                         placeholder-muted border border-white/5 
                         focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm
                         disabled:opacity-50 transition-all"
                            />
                            <button
                                type="submit"
                                disabled={!input.trim() || isLoading}
                                className="p-3.5 bg-primary-600 text-white rounded-xl hover:bg-primary-500 
                         disabled:opacity-50 disabled:cursor-not-allowed transition-all
                         shadow-glow active:scale-95"
                            >
                                {isLoading ? (
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                ) : (
                                    <Send className="w-5 h-5" />
                                )}
                            </button>
                        </div>
                    </form>
                </>
            )}
        </div>
    );
}
