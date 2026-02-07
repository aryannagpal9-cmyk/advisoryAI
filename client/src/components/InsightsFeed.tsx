/**
 * InsightsFeed Component
 * Displays proactive AI-generated insights and recommendations.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
    Lightbulb,
    AlertTriangle,
    TrendingUp,
    Shield,
    Calendar,
    CheckCircle,
    XCircle,
    RefreshCw,
    Filter,
    Eye,
    EyeOff,
    ChevronRight,
    Loader2,
    Sparkles
} from 'lucide-react';

interface Insight {
    id: string;
    category: 'INVESTMENT' | 'PROACTIVE' | 'COMPLIANCE' | 'BUSINESS' | 'FOLLOWUP';
    title: string;
    description: string;
    recommendation?: string;
    priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
    client_id?: string;
    client_name?: string;
    metrics?: Record<string, any>;
    affected_value?: number;
    is_read: boolean;
    is_actioned: boolean;
    created_at: string;
}

interface InsightsFeedProps {
    className?: string;
    compact?: boolean;
    refreshTrigger?: number;
}

import { API_BASE_URL } from '../config';
const API_BASE = `${API_BASE_URL}/api`;

const CATEGORY_CONFIG: Record<string, { icon: React.ComponentType<any>; color: string; label: string }> = {
    INVESTMENT: { icon: TrendingUp, color: 'text-green-400 bg-green-400/10', label: 'Investment' },
    PROACTIVE: { icon: Lightbulb, color: 'text-yellow-400 bg-yellow-400/10', label: 'Opportunity' },
    COMPLIANCE: { icon: Shield, color: 'text-red-400 bg-red-400/10', label: 'Compliance' },
    BUSINESS: { icon: TrendingUp, color: 'text-blue-400 bg-blue-400/10', label: 'Business' },
    FOLLOWUP: { icon: Calendar, color: 'text-purple-400 bg-purple-400/10', label: 'Follow-up' },
};

const PRIORITY_STYLES: Record<string, string> = {
    CRITICAL: 'glass-glow-white border-l-2 border-l-red-500/50',
    HIGH: 'glass-glow-white border-l-2 border-l-orange-500/50',
    MEDIUM: 'glass-glow-white border-l-2 border-l-yellow-500/50',
    LOW: 'glass-glow-white border-l-2 border-l-gray-500/50',
};

export default function InsightsFeed({ className = '', compact = false, refreshTrigger }: InsightsFeedProps) {
    const [insights, setInsights] = useState<Insight[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);
    const [filter, setFilter] = useState<string | null>(null);
    const [showRead, setShowRead] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchInsights = useCallback(async () => {
        try {
            setIsLoading(true);
            const params = new URLSearchParams();
            if (filter) params.append('category', filter);
            if (!showRead) params.append('unread_only', 'true');

            const response = await fetch(`${API_BASE}/insights?${params}`);
            const data = await response.json();
            setInsights(data.insights || []);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch insights:', err);
            setError('Failed to load insights');
            setInsights([]);
        } finally {
            setIsLoading(false);
        }
    }, [filter, showRead]);

    useEffect(() => {
        fetchInsights();
    }, [fetchInsights, refreshTrigger]);

    const generateInsights = async () => {
        try {
            setIsGenerating(true);
            const response = await fetch(`${API_BASE}/insights/generate`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                await fetchInsights();
            }
        } catch (err) {
            console.error('Failed to generate insights:', err);
        } finally {
            setIsGenerating(false);
        }
    };

    const updateInsight = async (id: string, updates: { is_read?: boolean; is_dismissed?: boolean; is_actioned?: boolean }) => {
        try {
            const params = new URLSearchParams();
            Object.entries(updates).forEach(([key, value]) => {
                if (value !== undefined) params.append(key, String(value));
            });

            await fetch(`${API_BASE}/insights/${id}?${params}`, { method: 'PATCH' });

            // Update local state
            if (updates.is_dismissed) {
                setInsights(prev => prev.filter(i => i.id !== id));
            } else {
                setInsights(prev => prev.map(i => i.id === id ? { ...i, ...updates } : i));
            }
        } catch (err) {
            console.error('Failed to update insight:', err);
        }
    };

    const markAsRead = (id: string) => updateInsight(id, { is_read: true });
    const dismiss = (id: string) => updateInsight(id, { is_dismissed: true });
    const markActioned = (id: string) => updateInsight(id, { is_actioned: true });

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);

        if (diffHours < 1) return 'Just now';
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    };

    const unreadCount = insights.filter(i => !i.is_read).length;

    if (compact) {
        // Compact view for dashboard sidebar
        return (
            <div className={`glass-glow-blue rounded-xl p-4 overflow-hidden relative ${className}`}>
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/5 blur-3xl -mr-16 -mt-16 animate-glow-pulse" />
                <div className="flex items-center justify-between mb-4 relative z-10">
                    <div className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-yellow-400 animate-float" />
                        <h3 className="font-semibold text-white">AI Insights</h3>
                        {unreadCount > 0 && (
                            <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded-full border border-red-500/30">
                                {unreadCount}
                            </span>
                        )}
                    </div>
                </div>

                {isLoading ? (
                    <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-6 h-6 text-primary-400 animate-spin" />
                    </div>
                ) : insights.length === 0 ? (
                    <p className="text-muted text-sm text-center py-4">No new insights</p>
                ) : (
                    <div className="space-y-3 relative z-10">
                        {insights.slice(0, 3).map((insight, idx) => {
                            const config = CATEGORY_CONFIG[insight.category] || CATEGORY_CONFIG.PROACTIVE;
                            const Icon = config.icon;

                            return (
                                <div
                                    key={insight.id}
                                    onClick={() => markAsRead(insight.id)}
                                    className={`p-3 rounded-lg cursor-pointer transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]
                            ${insight.is_read ? 'opacity-50' : ''} ${PRIORITY_STYLES[insight.priority]}`}
                                    style={{ animationDelay: `${idx * 150}ms` }}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className={`p-1.5 rounded-lg glass ${config.color.split(' ')[0]}`}>
                                            <Icon className="w-3.5 h-3.5" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-white truncate">{insight.title}</p>
                                            {insight.client_name && (
                                                <p className="text-xs text-muted">{insight.client_name}</p>
                                            )}
                                        </div>
                                        {!insight.is_read && (
                                            <div className="w-2 h-2 bg-primary-500 rounded-full flex-shrink-0 animate-pulse" />
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        );
    }

    // Full view
    return (
        <div className={`glass rounded-xl overflow-hidden relative ${className}`}>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary-500/50 to-transparent" />
            <div className="absolute -top-24 -left-24 w-96 h-96 bg-primary-500/5 blur-[100px] rounded-full" />

            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/5 relative z-10">
                <div>
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Sparkles className="w-6 h-6 text-yellow-400 animate-float" />
                        <span className="text-gradient-blue font-extrabold tracking-tight">AI Intelligence</span>
                        {unreadCount > 0 && (
                            <span className="ml-2 px-2.5 py-1 bg-red-500/20 text-red-400 text-sm rounded-full border border-red-500/20">
                                {unreadCount} new
                            </span>
                        )}
                    </h2>
                    <p className="text-muted text-sm mt-1">
                        Proactive recommendations and operational alerts
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={generateInsights}
                        disabled={isGenerating}
                        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg
                     hover:bg-primary-500 disabled:opacity-50 transition-all duration-300 shadow-lg shadow-primary-500/20 active:scale-95"
                    >
                        {isGenerating ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <RefreshCw className="w-4 h-4" />
                        )}
                        <span>Sync Insights</span>
                    </button>

                    <button
                        onClick={() => setShowRead(!showRead)}
                        className={`p-2 rounded-lg transition-all duration-300 ${showRead ? 'bg-white/10 text-white' : 'text-muted hover:text-white hover:bg-white/5'
                            }`}
                        title={showRead ? 'Hide read' : 'Show read'}
                    >
                        {showRead ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2 px-6 py-4 border-b border-white/5 overflow-x-auto relative z-10 scrollbar-none">
                <Filter className="w-4 h-4 text-muted flex-shrink-0" />
                <button
                    onClick={() => setFilter(null)}
                    className={`px-4 py-1.5 rounded-full text-sm transition-all duration-300 hover:scale-105 ${filter === null ? 'bg-primary-600 shadow-glow-sm text-white' : 'text-muted hover:bg-white/5'
                        }`}
                >
                    All Streams
                </button>
                {Object.entries(CATEGORY_CONFIG).map(([key, config]) => (
                    <button
                        key={key}
                        onClick={() => setFilter(key)}
                        className={`px-4 py-1.5 rounded-full text-sm whitespace-nowrap transition-all duration-300 hover:scale-105 ${filter === key ? 'bg-primary-600 shadow-glow-sm text-white' : 'text-muted hover:bg-white/5'
                            }`}
                    >
                        {config.label}
                    </button>
                ))}
            </div>

            {/* Insights List */}
            <div className="p-6 relative z-10">
                {isLoading ? (
                    <div className="flex items-center justify-center py-24">
                        <Loader2 className="w-10 h-10 text-primary-400 animate-spin" />
                    </div>
                ) : error ? (
                    <div className="text-center py-12 glass rounded-2xl p-8 max-w-md mx-auto">
                        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                        <p className="text-muted">{error}</p>
                        <button
                            onClick={fetchInsights}
                            className="mt-6 px-6 py-2 glass-glow-white rounded-lg hover:scale-105 transition-all"
                        >
                            Retry Loading
                        </button>
                    </div>
                ) : insights.length === 0 ? (
                    <div className="text-center py-24 glass rounded-2xl border-dashed border-white/5">
                        <div className="relative inline-block">
                            <Lightbulb className="w-16 h-16 text-muted/30 mx-auto mb-4 animate-float" />
                            <Sparkles className="w-6 h-6 text-yellow-400/50 absolute -top-2 -right-2 animate-pulse" />
                        </div>
                        <p className="text-white font-medium">No active intelligence</p>
                        <p className="text-muted text-sm mt-1 max-w-xs mx-auto">
                            Sync insights to uncover hidden opportunities across your client portfolio
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {insights.map((insight, idx) => {
                            const config = CATEGORY_CONFIG[insight.category] || CATEGORY_CONFIG.PROACTIVE;
                            const Icon = config.icon;

                            return (
                                <div
                                    key={insight.id}
                                    className={`group rounded-2xl p-6 transition-all duration-500 hover:shadow-glow-sm relative overflow-hidden
                            ${PRIORITY_STYLES[insight.priority]}
                            ${insight.is_read ? 'opacity-50' : ''}`}
                                    style={{ animation: `reveal 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both ${idx * 0.1}s` }}
                                >
                                    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                                    <div className="flex items-start gap-5 relative z-10">
                                        <div className={`p-3 rounded-xl glass ${config.color.split(' ')[0]} shadow-inner group-hover:scale-110 transition-transform duration-300`}>
                                            <Icon className="w-6 h-6" />
                                        </div>

                                        <div className="flex-1">
                                            <div className="flex items-start justify-between gap-4">
                                                <div>
                                                    <div className="flex items-center gap-3">
                                                        <h3 className="text-white text-lg font-bold group-hover:text-primary-400 transition-colors uppercase tracking-tight">{insight.title}</h3>
                                                        {!insight.is_read && (
                                                            <div className="w-2.5 h-2.5 bg-primary-500 rounded-full shadow-[0_0_12px_rgba(59,130,246,0.5)] animate-pulse" />
                                                        )}
                                                    </div>
                                                    {insight.client_name && (
                                                        <div className="flex items-center gap-2 mt-1">
                                                            <div className="w-1 h-1 rounded-full bg-muted/40" />
                                                            <p className="text-muted text-sm font-medium">
                                                                {insight.client_name}
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                                <span className="text-muted text-xs font-mono uppercase tracking-widest bg-white/5 px-2 py-1 rounded">
                                                    {formatDate(insight.created_at)}
                                                </span>
                                            </div>

                                            <p className="text-gray-300 mt-3 text-base leading-relaxed font-light">
                                                {insight.description}
                                            </p>

                                            {insight.recommendation && (
                                                <div className="mt-4 p-4 glass-glow-blue border-none rounded-xl relative overflow-hidden">
                                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary-500/50" />
                                                    <p className="text-sm text-primary-300 relative z-10">
                                                        <strong className="text-white mr-1 opacity-50 uppercase text-[10px] tracking-widest">Protocol:</strong> {insight.recommendation}
                                                    </p>
                                                </div>
                                            )}

                                            {insight.affected_value && (
                                                <div className="flex items-center gap-2 mt-4">
                                                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                                                    <p className="text-sm text-muted">
                                                        Projected Impact: <span className="text-emerald-400 font-bold ml-1">
                                                            £{insight.affected_value.toLocaleString()}
                                                        </span>
                                                    </p>
                                                </div>
                                            )}

                                            {/* Actions */}
                                            <div className="flex items-center gap-4 mt-6">
                                                {!insight.is_actioned && (
                                                    <button
                                                        onClick={() => markActioned(insight.id)}
                                                        className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 text-emerald-400 
                                     border border-emerald-500/20 rounded-xl text-sm font-semibold hover:bg-emerald-500/20 active:scale-95 transition-all"
                                                    >
                                                        <CheckCircle className="w-4 h-4" />
                                                        Mark Actioned
                                                    </button>
                                                )}
                                                <button
                                                    onClick={() => dismiss(insight.id)}
                                                    className="flex items-center gap-2 px-4 py-2 glass-glow-white 
                                   rounded-xl text-sm font-semibold text-white/70 hover:text-white active:scale-95 transition-all"
                                                >
                                                    <XCircle className="w-4 h-4" />
                                                    Archive
                                                </button>
                                                {insight.client_id && (
                                                    <button
                                                        className="flex items-center gap-1.5 px-4 py-2 text-primary-400 font-bold
                                     rounded-xl text-sm hover:bg-primary-500/10 transition-all ml-auto group/btn"
                                                    >
                                                        Open Intel
                                                        <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
