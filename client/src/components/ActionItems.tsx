/**
 * ActionItems Component
 * Dashboard view for managing action items and follow-ups.
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
    CheckCircle2,
    Clock,
    AlertTriangle,
    Plus,
    Filter,
    Search,
    Calendar,
    User,
    Loader2,
    CheckCircle,
    Circle,
    Trash2,
    Edit2,
    Activity,
    Zap,
    Send,
    Briefcase,
    CheckSquare,
    Bot,
    ChevronRight,
} from 'lucide-react';

interface ActionItem {
    id: string;
    title: string;
    description?: string;
    client_id?: string;
    client_name?: string;
    case_id?: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'OVERDUE' | 'COMPLETED';
    priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    owner: 'ADVISOR' | 'CLIENT' | 'SYSTEM';
    due_date?: string;
    category?: string;
    created_at: string;
    completed_at?: string;
}

interface StatusCounts {
    pending: number;
    in_progress: number;
    overdue: number;
    completed: number;
}

interface ActionItemsProps {
    className?: string;
    refreshTrigger?: number;
}

import { API_BASE_URL } from '../config';
const API_BASE = `${API_BASE_URL}/api`;

const STATUS_CONFIG: Record<string, { icon: React.ComponentType<any>; color: string; bgColor: string }> = {
    PENDING: { icon: Circle, color: 'text-gray-400', bgColor: 'bg-gray-400/10' },
    IN_PROGRESS: { icon: Clock, color: 'text-blue-400', bgColor: 'bg-blue-400/10' },
    OVERDUE: { icon: AlertTriangle, color: 'text-red-400', bgColor: 'bg-red-400/10' },
    COMPLETED: { icon: CheckCircle2, color: 'text-green-400', bgColor: 'bg-green-400/10' },
};

const PRIORITY_COLORS: Record<string, string> = {
    LOW: 'bg-gray-500 shadow-[0_0_10px_rgba(107,114,128,0.3)]',
    MEDIUM: 'bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.3)]',
    HIGH: 'bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.3)]',
    CRITICAL: 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)] animate-pulse',
};

export default function ActionItems({ className = '', refreshTrigger }: ActionItemsProps) {
    const [items, setItems] = useState<ActionItem[]>([]);
    const [counts, setCounts] = useState<StatusCounts>({ pending: 0, in_progress: 0, overdue: 0, completed: 0 });
    const [isLoading, setIsLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState<string>('OPEN');
    const [searchQuery, setSearchQuery] = useState('');
    const [showNewModal, setShowNewModal] = useState(false);
    const [editingItem, setEditingItem] = useState<ActionItem | null>(null);
    const [viewMode, setViewMode] = useState<'TASKS' | 'TIMELINE'>('TASKS');
    const [auditLogs, setAuditLogs] = useState<any[]>([]);

    const fetchItems = useCallback(async () => {
        try {
            setIsLoading(true);
            const params = new URLSearchParams();
            if (statusFilter !== 'ALL') {
                params.append('status', statusFilter);
            }

            const response = await fetch(`${API_BASE}/action-items?${params}`);
            const data = await response.json();
            setItems(data.items || []);
            setCounts(data.counts || { pending: 0, in_progress: 0, overdue: 0, completed: 0 });
        } catch (err) {
            console.error('Failed to fetch action items:', err);
            setItems([]);
        } finally {
            setIsLoading(false);
        }
    }, [statusFilter]);

    const fetchLogs = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`${API_BASE}/recent-activity`);
            const data = await response.json();
            setAuditLogs(data || []);
        } catch (err) {
            console.error('Failed to fetch activity logs:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (viewMode === 'TASKS') {
            fetchItems();
        } else {
            fetchLogs();
        }
    }, [fetchItems, viewMode, refreshTrigger]);

    const updateItem = async (id: string, updates: Partial<ActionItem>) => {
        try {
            await fetch(`${API_BASE}/action-items/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates),
            });
            await fetchItems();
        } catch (err) {
            console.error('Failed to update item:', err);
        }
    };

    const deleteItem = async (id: string) => {
        if (!confirm('Are you sure you want to delete this action item?')) return;
        try {
            await fetch(`${API_BASE}/action-items/${id}`, { method: 'DELETE' });
            await fetchItems();
        } catch (err) {
            console.error('Failed to delete item:', err);
        }
    };

    const filteredItems = items.filter(item => {
        if (!searchQuery) return true;
        const query = searchQuery.toLowerCase();
        return (
            item.title.toLowerCase().includes(query) ||
            item.description?.toLowerCase().includes(query) ||
            item.client_name?.toLowerCase().includes(query)
        );
    });

    const groupedItems = filteredItems.reduce((acc, item) => {
        const group = item.status === 'OVERDUE' ? 'Overdue' :
            item.status === 'IN_PROGRESS' ? 'In Progress' :
                item.status === 'COMPLETED' ? 'Completed' : 'Pending';
        if (!acc[group]) acc[group] = [];
        acc[group].push(item);
        return acc;
    }, {} as Record<string, ActionItem[]>);

    return (
        <div className={`glass min-h-screen relative overflow-hidden ${className}`}>
            <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent" />
            <div className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-primary-500/5 blur-[120px] rounded-full pointer-events-none" />

            {/* Header */}
            <div className="relative z-10 border-b border-white/5 backdrop-blur-md px-8 py-6">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="flex items-center gap-6 mb-2">
                            <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
                                <Zap className="w-8 h-8 text-yellow-400 animate-float" />
                                <span className="text-gradient-blue">Action Center</span>
                            </h1>
                            <div className="flex bg-white/5 p-1 rounded-xl border border-white/10 backdrop-blur-sm">
                                <button
                                    onClick={() => setViewMode('TASKS')}
                                    className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest transition-all duration-300 ${viewMode === 'TASKS' ? 'bg-primary-600 text-white shadow-glow-sm' : 'text-muted hover:text-white'}`}
                                >
                                    Operational
                                </button>
                                <button
                                    onClick={() => setViewMode('TIMELINE')}
                                    className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest transition-all duration-300 ${viewMode === 'TIMELINE' ? 'bg-primary-600 text-white shadow-glow-sm' : 'text-muted hover:text-white'}`}
                                >
                                    Log
                                </button>
                            </div>
                        </div>
                        <p className="text-muted text-sm font-medium">
                            {viewMode === 'TASKS' ? 'Strategic task management and operational follow-ups' : 'Real-time trace of autonomous intelligence actions'}
                        </p>
                    </div>
                    <button
                        onClick={() => setShowNewModal(true)}
                        className="flex items-center gap-2 px-6 py-2.5 bg-primary-600 text-white rounded-xl font-bold hover:bg-primary-500 transition-all duration-300 shadow-glow active:scale-95"
                    >
                        <Plus className="w-5 h-5" />
                        Initiate Action
                    </button>
                </div>

                {viewMode === 'TASKS' && (
                    <div className="grid grid-cols-4 gap-6 mt-8">
                        {[
                            { key: 'overdue', label: 'Critical Ops', value: counts.overdue, color: 'glass-glow-red border-red-500/30 text-red-400' },
                            { key: 'pending', label: 'Pending', value: counts.pending, color: 'glass-glow-white border-white/10 text-white' },
                            { key: 'in_progress', label: 'Active', value: counts.in_progress, color: 'glass-glow-blue border-primary-500/30 text-primary-400' },
                            { key: 'completed', label: 'Resolved', value: counts.completed, color: 'glass-glow-emerald border-emerald-500/30 text-emerald-400' },
                        ].map((stat, idx) => (
                            <div
                                key={stat.key}
                                className={`p-5 rounded-2xl border ${stat.color} cursor-pointer hover:scale-105 transition-all duration-500 group relative overflow-hidden`}
                                onClick={() => setStatusFilter(stat.key.toUpperCase())}
                                style={{ animation: `reveal 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both ${idx * 0.1}s` }}
                            >
                                <div className="absolute inset-0 bg-gradient-to-br from-white/[0.05] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                <p className="text-4xl font-extrabold mb-1">{stat.value}</p>
                                <p className="text-xs font-mono uppercase tracking-widest opacity-70">{stat.label}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Content Area */}
            <div className="p-8 relative z-10">
                {isLoading ? (
                    <div className="flex items-center justify-center py-24">
                        <Loader2 className="w-12 h-12 text-primary-400 animate-spin" />
                    </div>
                ) : viewMode === 'TASKS' ? (
                    <>
                        <div className="mb-8 flex items-center gap-6">
                            <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 flex-1 max-w-md focus-within:border-primary-500/50 transition-all">
                                <Search className="w-5 h-5 text-muted" />
                                <input
                                    type="text"
                                    placeholder="Search command center..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="bg-transparent border-none outline-none text-white text-sm flex-1 placeholder-muted"
                                />
                            </div>
                            <div className="flex items-center gap-3">
                                <Filter className="w-5 h-5 text-muted" />
                                {['OPEN', 'ALL', 'COMPLETED'].map((status) => (
                                    <button
                                        key={status}
                                        onClick={() => setStatusFilter(status)}
                                        className={`px-5 py-2 rounded-xl text-sm font-bold uppercase tracking-wide transition-all duration-300 ${statusFilter === status ? 'bg-primary-600 shadow-glow-sm text-white' : 'glass-glow-white text-muted hover:text-white'}`}
                                    >
                                        {status}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {filteredItems.length === 0 ? (
                            <div className="text-center py-24 glass rounded-3xl border-dashed border-white/10 max-w-lg mx-auto">
                                <CheckCircle className="w-16 h-16 text-muted/30 mx-auto mb-4 animate-float" />
                                <p className="text-white font-bold text-xl">Inbox Zero Achieved</p>
                                <p className="text-muted mt-2">All critical operations are currently up to date.</p>
                            </div>
                        ) : (
                            <div className="space-y-10">
                                {Object.entries(groupedItems).map(([group, groupItems]) => (
                                    <div key={group} className="animate-reveal">
                                        <div className="flex items-center gap-4 mb-4">
                                            <h3 className="text-xs font-black text-muted uppercase tracking-[0.2em]">
                                                {group}
                                            </h3>
                                            <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent" />
                                            <span className="text-[10px] font-mono text-muted bg-white/5 px-2 py-0.5 rounded-full border border-white/5">
                                                {groupItems.length} ITEMS
                                            </span>
                                        </div>
                                        <div className="space-y-3">
                                            {groupItems.map((item, idx) => {
                                                const StatusIcon = STATUS_CONFIG[item.status].icon;
                                                return (
                                                    <div key={item.id}
                                                        className="glass-glow-white border-white/5 rounded-2xl p-5 flex items-center gap-5 hover:scale-[1.01] hover:border-white/10 transition-all duration-300 group relative overflow-hidden"
                                                        style={{ animationDelay: `${idx * 100}ms` }}>
                                                        <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none" />

                                                        <button
                                                            onClick={() => updateItem(item.id, { status: item.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED' })}
                                                            className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-500 scale-in ${item.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/20' : 'glass hover:bg-white/10 text-muted hover:text-white border border-white/5'}`}
                                                        >
                                                            <StatusIcon size={20} className={item.status === 'COMPLETED' ? 'animate-glow-pulse' : ''} />
                                                        </button>

                                                        <div className="flex-1 min-w-0 pointer-cursor" onClick={() => setEditingItem(item)}>
                                                            <div className="flex items-center gap-3 mb-1.5">
                                                                <h4 className={`font-bold text-lg tracking-tight ${item.status === 'COMPLETED' ? 'text-muted line-through opacity-50' : 'text-white'}`}>
                                                                    {item.title}
                                                                </h4>
                                                                <span className={`px-2 py-0.5 rounded text-[10px] font-black text-white uppercase tracking-tighter shadow-lg ${PRIORITY_COLORS[item.priority]}`}>
                                                                    {item.priority}
                                                                </span>
                                                            </div>
                                                            <div className="flex items-center gap-6 text-xs text-muted font-medium">
                                                                <span className="flex items-center gap-1.5"><User size={14} className="opacity-50" /> {item.client_name || 'Protocol'}</span>
                                                                {item.due_date && <span className="flex items-center gap-1.5"><Calendar size={14} className="opacity-50" /> {new Date(item.due_date).toLocaleDateString()}</span>}
                                                                <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-white/5 border border-white/5 text-[10px] uppercase font-bold tracking-widest">{item.owner}</span>
                                                            </div>
                                                        </div>

                                                        <div className="opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center gap-2 translate-x-4 group-hover:translate-x-0">
                                                            <button onClick={() => setEditingItem(item)} className="p-2.5 text-muted hover:text-white glass rounded-xl transition-all"><Edit2 size={18} /></button>
                                                            <button onClick={() => deleteItem(item.id)} className="p-2.5 text-muted hover:text-red-400 glass rounded-xl transition-all"><Trash2 size={18} /></button>
                                                            <button className="p-2.5 text-primary-400 hover:text-primary-300 glass rounded-xl transition-all"><ChevronRight size={18} /></button>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <div className="max-w-4xl mx-auto py-8">
                        {auditLogs.length === 0 ? (
                            <div className="text-center py-32 glass rounded-3xl border-dashed border-white/10">
                                <Activity className="w-16 h-16 text-muted/30 mx-auto mb-4 animate-float" />
                                <p className="text-white font-bold text-xl">Operational Silence</p>
                                <p className="text-muted mt-2">No autonomous system actions recorded in the current cycle.</p>
                            </div>
                        ) : (
                            <div className="space-y-0 relative">
                                <div className="absolute left-[21px] top-6 bottom-6 w-px bg-gradient-to-b from-primary-500/50 via-white/5 to-transparent" />

                                {auditLogs.map((log, idx) => {
                                    const date = new Date(log.created_at);
                                    let Icon = Activity;
                                    let color = 'text-primary-400';
                                    let bg = 'bg-primary-500/10';
                                    let border = 'border-primary-500/20 shadow-glow-sm';

                                    if (log.action === 'CHASE_SENT') { Icon = Zap; color = 'text-amber-400'; bg = 'bg-amber-400/10'; border = 'border-amber-500/20'; }
                                    else if (log.action === 'EMAIL_SENT') { Icon = Send; color = 'text-primary-400'; bg = 'bg-primary-500/10'; border = 'border-primary-500/20'; }
                                    else if (log.action === 'TASK_CREATED') { Icon = CheckSquare; color = 'text-purple-400'; bg = 'bg-purple-400/10'; border = 'border-purple-500/20'; }
                                    else if (log.action === 'CASE_CREATED') { Icon = Briefcase; color = 'text-emerald-400'; bg = 'bg-emerald-500/10'; border = 'border-emerald-500/20'; }

                                    return (
                                        <div key={log.id}
                                            className="flex gap-8 group pb-10 last:pb-0"
                                            style={{ animation: `reveal 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both ${idx * 0.05}s` }}>
                                            <div className="flex flex-col items-center relative z-10 pt-1">
                                                <div className={`w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 glass ${bg} ${color} border ${border} transition-all duration-500 group-hover:scale-110`}>
                                                    <Icon size={20} className="group-hover:animate-glow-pulse" />
                                                </div>
                                            </div>
                                            <div className="flex-1 glass-glow-white border-white/5 rounded-2xl p-6 hover:border-white/10 transition-all duration-300 group-hover:bg-white/[0.03] animate-reveal">
                                                <div className="flex items-center justify-between mb-3">
                                                    <span className={`text-[10px] font-black uppercase tracking-[0.2em] px-3 py-1 rounded-full ${bg} ${color} border ${border}`}>
                                                        {log.action.replace('_', ' ')}
                                                    </span>
                                                    <span className="text-[10px] font-mono text-muted uppercase tracking-widest bg-white/5 px-2 py-1 rounded">
                                                        {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                                    </span>
                                                </div>
                                                <p className="text-white text-base font-medium leading-relaxed mb-4">{log.reason || log.description}</p>
                                                {log.actor && (
                                                    <div className="flex items-center gap-2 text-[10px] text-muted font-bold uppercase tracking-widest">
                                                        <Bot size={14} className="opacity-50" />
                                                        <span>Source: {log.actor}</span>
                                                        <div className="w-1 h-1 rounded-full bg-muted/30 ml-auto" />
                                                        <span>{date.toLocaleDateString()}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Modal */}
            {(showNewModal || editingItem) && (
                <NewActionModal
                    item={editingItem}
                    onClose={() => { setShowNewModal(false); setEditingItem(null); }}
                    onSave={async () => { await fetchItems(); setShowNewModal(false); setEditingItem(null); }}
                />
            )}
        </div>
    );
}

function NewActionModal({ item, onClose, onSave }: { item: ActionItem | null; onClose: () => void; onSave: () => void; }) {
    const [title, setTitle] = useState(item?.title || '');
    const [description, setDescription] = useState(item?.description || '');
    const [priority, setPriority] = useState(item?.priority || 'MEDIUM');
    const [dueDate, setDueDate] = useState(item?.due_date?.split('T')[0] || '');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!title.trim()) return;
        setIsSubmitting(true);
        try {
            const body = { title: title.trim(), description: description.trim() || undefined, priority, due_date: dueDate || undefined };
            if (item) {
                await fetch(`${API_BASE}/action-items/${item.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
            } else {
                await fetch(`${API_BASE}/action-items`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
            }
            onSave();
        } catch (err) { console.error('Failed to save:', err); }
        finally { setIsSubmitting(false); }
    };

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-xl flex items-center justify-center z-50 p-4">
            <div className="glass-glow-white border-white/5 rounded-3xl max-w-lg w-full shadow-2xl overflow-hidden scale-in relative">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary-500/50 to-transparent" />
                <form onSubmit={handleSubmit}>
                    <div className="p-8 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                        <h2 className="text-2xl font-black text-white tracking-tight">{item ? 'EDIT PROTOCOL' : 'INITIATE ACTION'}</h2>
                        <button type="button" onClick={onClose} className="p-2 text-muted hover:text-white transition-colors">
                            <Plus className="w-6 h-6 rotate-45" />
                        </button>
                    </div>
                    <div className="p-8 space-y-6">
                        <div>
                            <label className="block text-[10px] font-black text-muted uppercase tracking-[0.2em] mb-2 ml-1">Directive Title</label>
                            <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white font-bold focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/50 transition-all placeholder:text-muted/30" placeholder="Operational target..." required />
                        </div>
                        <div>
                            <label className="block text-[10px] font-black text-muted uppercase tracking-[0.2em] mb-2 ml-1">Contextual Description</label>
                            <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/50 transition-all resize-none placeholder:text-muted/30" placeholder="Provide detailed intelligence..." rows={4} />
                        </div>
                        <div className="grid grid-cols-2 gap-6">
                            <div>
                                <label className="block text-[10px] font-black text-muted uppercase tracking-[0.2em] mb-2 ml-1">Priority Level</label>
                                <select value={priority} onChange={(e) => setPriority(e.target.value as any)} className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white font-bold focus:outline-none focus:border-primary-500/50 transition-all appearance-none cursor-pointer" >
                                    <option value="LOW">Routine (Low)</option>
                                    <option value="MEDIUM">Standard (Med)</option>
                                    <option value="HIGH">Strategic (High)</option>
                                    <option value="CRITICAL">Critical (Now)</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-[10px] font-black text-muted uppercase tracking-[0.2em] mb-2 ml-1">Deadline</label>
                                <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4 text-white font-bold focus:outline-none focus:border-primary-500/50 transition-all cursor-pointer" />
                            </div>
                        </div>
                    </div>
                    <div className="p-8 bg-white/[0.02] border-t border-white/5 flex justify-end gap-4">
                        <button type="button" onClick={onClose} className="px-6 py-3 text-muted font-bold hover:text-white hover:bg-white/5 rounded-2xl transition-all">ABORT</button>
                        <button type="submit" disabled={!title.trim() || isSubmitting} className="px-8 py-3 bg-primary-600 text-white rounded-2xl font-black uppercase tracking-widest hover:bg-primary-500 disabled:opacity-50 transition-all shadow-glow flex items-center gap-3 active:scale-95">
                            {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                            {item ? 'UPDATE PROTOCOL' : 'DEPLOY'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

