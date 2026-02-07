import { useEffect, useState } from 'react';
import { AlertCircle, Clock, CheckCircle, MoreHorizontal, Send, Eye } from 'lucide-react';
import clsx from 'clsx';
import { API_BASE_URL } from '../config';

interface Request {
    id: string;
    case_id: string;
    title: string;
    status: string;
    priority: string;
    owner_type: string;
    retry_count: number;
    created_at: string;
    next_action_at: string;
    case_title?: string;
}

export function ExceptionFeed({ onViewCase, refreshTrigger }: { onViewCase: (caseId: string) => void, refreshTrigger?: number }) {
    const [items, setItems] = useState<Request[]>([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<string | null>(null);

    const fetchExceptions = () => {
        setLoading(true);
        fetch(`${API_BASE_URL}/api/feed/exceptions`)
            .then(res => res.json())
            .then(data => setItems(data))
            .catch(err => console.error("Failed to fetch feed", err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchExceptions();
    }, [refreshTrigger]);

    const handleResolve = async (requestId: string) => {
        setActionLoading(requestId);
        try {
            await fetch(`${API_BASE_URL}/api/requests/${requestId}/resolve`, { method: 'POST' });
            fetchExceptions(); // Refresh
        } catch (e) {
            console.error('Resolve failed:', e);
        } finally {
            setActionLoading(null);
        }
    };

    const handleChase = async (requestId: string) => {
        setActionLoading(requestId);
        try {
            await fetch(`${API_BASE_URL}/api/requests/${requestId}/chase`, { method: 'POST' });
            fetchExceptions();
        } catch (e) {
            console.error('Chase failed:', e);
        } finally {
            setActionLoading(null);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
        </div>
    );

    if (items.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-center text-gray-400">
                <CheckCircle className="w-12 h-12 mb-4 text-emerald-500" />
                <h3 className="text-xl font-medium text-white">All Clear</h3>
                <p>No actionable exceptions found.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold text-white/90 px-1">
                    Exception Feed <span className="text-gray-500 font-normal">({items.length} Actionable)</span>
                </h2>
                <button
                    onClick={fetchExceptions}
                    className="text-xs text-gray-400 hover:text-white"
                >
                    Refresh
                </button>
            </div>

            {items.map((item: any) => (
                <div
                    key={item.id}
                    className={clsx(
                        "glass-card hover:bg-surface/50 transition-all group relative border-l-4 animate-slide-up",
                        item.status === 'ESCALATED' ? 'border-l-rose-500' : 'border-l-amber-500'
                    )}
                >
                    <div className="flex justify-between items-start">
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <h3 className="text-lg font-medium text-white">{item.title}</h3>
                                {item.priority === 'HIGH' && (
                                    <span className="text-xs bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded">High Priority</span>
                                )}
                            </div>

                            <div className="flex items-center gap-4 text-sm text-gray-400">
                                <span className={clsx(
                                    "flex items-center gap-1.5 font-medium",
                                    item.status === 'ESCALATED' ? "text-rose-400" : "text-amber-400"
                                )}>
                                    <AlertCircle className="w-4 h-4" />
                                    {item.status}
                                </span>

                                <span className="flex items-center gap-1.5">
                                    <Clock className="w-4 h-4" />
                                    Retry #{item.retry_count}
                                </span>

                                <span>Owner: {item.owner_type}</span>
                                {item.case_title && (
                                    <span className="text-xs text-gray-500">• {item.case_title}</span>
                                )}
                            </div>
                        </div>

                        <button className="p-2 hover:bg-white/10 rounded-lg text-gray-400 transition-colors">
                            <MoreHorizontal className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="mt-4 flex gap-3">
                        <button
                            onClick={() => onViewCase(item.case_id)}
                            className="flex items-center gap-1.5 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-white transition-colors"
                        >
                            <Eye className="w-4 h-4" />
                            View Timeline
                        </button>
                        <button
                            onClick={() => handleChase(item.id)}
                            disabled={actionLoading === item.id}
                            className="flex items-center gap-1.5 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors disabled:opacity-50 border border-white/10"
                        >
                            <Send className="w-4 h-4" />
                            {actionLoading === item.id ? 'Sending...' : 'Send Chase'}
                        </button>
                        {item.status === 'ESCALATED' && (
                            <button
                                onClick={() => handleResolve(item.id)}
                                disabled={actionLoading === item.id}
                                className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm transition-colors shadow-lg shadow-emerald-900/20 disabled:opacity-50"
                            >
                                <CheckCircle className="w-4 h-4" />
                                Mark Resolved
                            </button>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}
