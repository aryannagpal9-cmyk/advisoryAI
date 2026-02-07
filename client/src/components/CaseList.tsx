import { useEffect, useState } from 'react';
import { Search, ChevronRight, User, RefreshCw } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface Case {
    id: string;
    client_name: string;
    title: string;
    status: string;
    updated_at: string;
}

export function CaseList({ onSelectCase, refreshTrigger }: { onSelectCase: (id: string) => void, refreshTrigger?: number }) {
    const [cases, setCases] = useState<Case[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [activeTab, setActiveTab] = useState<'ACTIVE' | 'COMPLETED'>('ACTIVE');

    const fetchCases = () => {
        setLoading(true);
        fetch(`${API_BASE_URL}/api/cases`)
            .then(res => res.json())
            .then(data => setCases(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchCases();
    }, [refreshTrigger]);

    // Filter cases based on search query and active tab
    const filteredCases = cases.filter(c => {
        const matchesSearch = c.client_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            c.title?.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesTab = c.status === activeTab;
        return matchesSearch && matchesTab;
    });

    return (
        <div className="space-y-6 animate-reveal">
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
                <div className="flex glass p-1.5 rounded-2xl border border-white/5 relative overflow-hidden">
                    <div className="absolute inset-0 bg-primary-500/5 pointer-events-none" />
                    <button
                        onClick={() => setActiveTab('ACTIVE')}
                        className={`px-8 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-500 relative z-10 ${activeTab === 'ACTIVE'
                            ? 'glass-glow-blue text-white shadow-glow-sm'
                            : 'text-muted hover:text-white hover:bg-white/5'
                            }`}
                    >
                        Active Operations
                    </button>
                    <button
                        onClick={() => setActiveTab('COMPLETED')}
                        className={`px-8 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-500 relative z-10 ${activeTab === 'COMPLETED'
                            ? 'glass-glow-blue text-white shadow-glow-sm'
                            : 'text-muted hover:text-white hover:bg-white/5'
                            }`}
                    >
                        Success Logs
                    </button>
                </div>

                <div className="flex items-center gap-4 w-full sm:w-auto relative z-10">
                    <button
                        onClick={fetchCases}
                        className="text-muted hover:text-white p-3 rounded-xl hover:bg-white/5 transition border border-white/5 glass shadow-glow-sm hover:shadow-primary-500/20"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                    <div className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em] whitespace-nowrap">
                        {filteredCases.length} <span className="text-primary-500/60 font-black">Registry Instances</span>
                    </div>
                </div>
            </div>

            <div className="flex justify-between items-center glass p-3 rounded-2xl border border-white/5 relative overflow-hidden group">
                <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
                <div className="relative flex-1 max-w-md relative z-10">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-primary-400 transition-colors" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder={`FILTER ${activeTab} REGISTRY...`}
                        className="w-full bg-white/5 border border-white/5 rounded-xl pl-12 pr-4 py-3 text-xs font-bold text-white tracking-widest uppercase placeholder:text-muted/40 focus:outline-none focus:border-primary-500/30 transition-all"
                    />
                </div>
            </div>

            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="w-10 h-10 border-2 border-primary-500/20 border-t-primary-500 rounded-full animate-spin shadow-glow-sm"></div>
                </div>
            ) : filteredCases.length === 0 ? (
                <div className="glass p-24 text-center rounded-[40px] border border-white/5 relative overflow-hidden">
                    <div className="absolute inset-0 bg-primary-500/5 blur-[100px] pointer-events-none" />
                    <User className="w-16 h-16 mx-auto mb-6 text-muted/30 relative z-10" />
                    <h3 className="text-xl font-black text-white mb-2 relative z-10 uppercase tracking-tight">
                        {searchQuery ? 'Zero Intelligence Matches' : `Empty Registry Sink`}
                    </h3>
                    <p className="text-muted font-bold text-[10px] uppercase tracking-[0.3em] relative z-10 opacity-50">
                        {searchQuery ? 'Adjust filtration parameters' : 'Waiting for system data flow...'}
                    </p>
                </div>
            ) : (
                <div className="glass overflow-hidden rounded-[32px] border border-white/5 shadow-2xl relative">
                    <div className="absolute inset-0 bg-primary-500/[0.01] pointer-events-none" />
                    <table className="w-full text-left relative z-10">
                        <thead className="bg-white/[0.03] text-muted text-[10px] font-black uppercase tracking-[0.2em]">
                            <tr>
                                <th className="px-8 py-6">Operational Entity</th>
                                <th className="px-8 py-6">Objective Designation</th>
                                <th className="px-8 py-6">Protocol Status</th>
                                <th className="px-8 py-6">Last Link</th>
                                <th className="px-8 py-6"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {filteredCases.map(c => (
                                <tr
                                    key={c.id}
                                    className="hover:bg-white/[0.03] transition-all duration-300 cursor-pointer group"
                                    onClick={() => onSelectCase(c.id)}
                                >
                                    <td className="px-8 py-6">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-2xl glass border border-white/5 flex items-center justify-center text-primary-500 shadow-glow-sm group-hover:scale-110 transition-transform">
                                                <User className="w-5 h-5" />
                                            </div>
                                            <span className="font-black text-sm text-white tracking-tight uppercase group-hover:text-primary-400 transition-colors">{c.client_name}</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6 text-white/70 text-xs font-bold uppercase tracking-wider">{c.title}</td>
                                    <td className="px-8 py-6">
                                        <StatusBadge status={c.status} />
                                    </td>
                                    <td className="px-8 py-6 text-muted text-[10px] font-black tracking-widest uppercase">
                                        {new Date(c.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-primary-500 transition-all duration-300">
                                            <ChevronRight className="w-5 h-5 text-muted group-hover:text-white transition-colors" />
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    const colors: any = {
        ACTIVE: 'glass-glow-emerald border-emerald-500/30 text-emerald-400 shadow-glow-sm',
        BLOCKED: 'glass-glow-amber border-amber-500/30 text-amber-400 shadow-glow-sm',
        COMPLETED: 'glass border-white/10 text-muted'
    };

    return (
        <span className={`px-4 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-[0.2em] border ${colors[status] || colors.ACTIVE}`}>
            {status}
        </span>
    );
}
