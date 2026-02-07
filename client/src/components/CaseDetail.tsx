import { useEffect, useState } from 'react';
import { ArrowLeft, Clock, FileText, Send, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-react';

interface CaseDetailProps {
    caseId: string;
    onBack: () => void;
}

export function CaseDetail({ caseId, onBack }: CaseDetailProps) {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<string | null>(null);

    const fetchCase = () => {
        setLoading(true);
        fetch(`http://localhost:8000/api/cases/${caseId}`)
            .then(res => res.json())
            .then(setData)
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchCase();
    }, [caseId]);

    const handleChase = async (requestId: string) => {
        setActionLoading(requestId);
        try {
            await fetch(`http://localhost:8000/api/requests/${requestId}/chase`, { method: 'POST' });
            fetchCase(); // Refresh data
        } catch (e) {
            console.error('Chase failed:', e);
        } finally {
            setActionLoading(null);
        }
    };

    const handleResolve = async (requestId: string) => {
        setActionLoading(requestId);
        try {
            await fetch(`http://localhost:8000/api/requests/${requestId}/resolve`, { method: 'POST' });
            fetchCase();
        } catch (e) {
            console.error('Resolve failed:', e);
        } finally {
            setActionLoading(null);
        }
    };

    const handleEscalate = async (requestId: string) => {
        setActionLoading(requestId);
        try {
            await fetch(`http://localhost:8000/api/requests/${requestId}/escalate`, { method: 'POST' });
            fetchCase();
        } catch (e) {
            console.error('Escalate failed:', e);
        } finally {
            setActionLoading(null);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center py-32 animate-reveal">
            <div className="w-12 h-12 border-2 border-primary-500/20 border-t-primary-500 rounded-full animate-spin shadow-glow"></div>
        </div>
    );

    if (!data) return <div className="p-8 text-center text-gray-500">Case not found</div>;

    return (
        <div className="space-y-8 animate-reveal">
            <button onClick={onBack} className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.3em] text-muted hover:text-primary-400 transition-all group">
                <div className="p-2 glass border border-white/5 rounded-xl group-hover:border-primary-500/30">
                    <ArrowLeft className="w-4 h-4" />
                </div>
                Return to Registry
            </button>

            <div className="flex justify-between items-end pb-8 border-b border-white/5 relative overflow-hidden">
                <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
                <div className="relative z-10">
                    <p className="text-[10px] font-black text-muted uppercase tracking-[0.5em] mb-4">Operational Intelligence Link</p>
                    <h1 className="text-4xl font-black text-white mb-2 leading-none uppercase tracking-tighter">{data.client_name}</h1>
                    <p className="text-xl font-bold text-primary-500/60 uppercase tracking-widest">{data.title}</p>
                </div>
                <div className="text-right relative z-10">
                    <span className="text-[10px] font-black text-muted uppercase tracking-[0.3em] block mb-3 opacity-40">Link Status</span>
                    <span className="px-6 py-2 glass-glow-blue text-white rounded-2xl border border-primary-500/30 text-[10px] font-black uppercase tracking-widest shadow-glow-sm">
                        {data.status}
                    </span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-8">
                    <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center gap-3">
                            <div className="w-1.5 h-6 bg-primary-500 rounded-full shadow-glow" />
                            <h3 className="text-lg font-black text-white uppercase tracking-tight">Active Strategic Directives</h3>
                        </div>
                        <button
                            onClick={fetchCase}
                            className="p-2 glass border border-white/5 rounded-xl text-muted hover:text-primary-400 hover:border-primary-500/30 transition-all flex items-center gap-2"
                        >
                            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                            <span className="text-[9px] font-black uppercase tracking-widest">Re-Sync</span>
                        </button>
                    </div>
                    <div className="space-y-4">
                        {data.requests && data.requests.map((req: any) => (
                            <div key={req.id} className="glass border border-white/5 p-6 rounded-[32px] group relative overflow-hidden hover:border-white/20 transition-all duration-500">
                                <div className="absolute inset-0 bg-primary-500/[0.01] pointer-events-none" />
                                <div className="flex justify-between items-start relative z-10">
                                    <div className="flex items-center gap-6">
                                        <div className={`p-4 rounded-[20px] shadow-glow-sm border transition-all duration-500 ${req.status === 'FULFILLED' ? 'glass-glow-emerald border-emerald-500/20 text-emerald-400' :
                                            req.status === 'ESCALATED' ? 'glass-glow-amber border-amber-500/20 text-amber-400' :
                                                'glass border-white/10 text-white'
                                            }`}>
                                            <FileText className="w-6 h-6" />
                                        </div>
                                        <div>
                                            <h4 className="font-black text-base text-white uppercase tracking-tight group-hover:text-primary-400 transition-colors mb-2">{req.title}</h4>
                                            <div className="flex items-center gap-4">
                                                <span className="text-[9px] font-black text-muted uppercase tracking-widest px-2 py-0.5 glass rounded-md border border-white/5">
                                                    ENTITY: {req.owner_type}
                                                </span>
                                                <span className="text-[9px] font-black text-muted uppercase tracking-widest">
                                                    SEQ LOG: {req.retry_count}/{req.max_retries || 3}
                                                </span>
                                                {req.priority === 'HIGH' && (
                                                    <span className="text-[9px] font-black bg-primary-500/20 text-primary-400 px-2.5 py-1 rounded-[10px] tracking-widest shadow-glow-sm">PRIORITY RED</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className={`text-[9px] font-black uppercase tracking-[0.2em] px-4 py-1.5 rounded-xl border ${req.status === 'ESCALATED' ? 'glass-glow-amber border-amber-500/30 text-amber-400' :
                                            req.status === 'FULFILLED' ? 'glass-glow-emerald border-emerald-500/30 text-emerald-400' :
                                                req.status === 'PENDING' ? 'glass-glow-blue border-primary-500/30 text-white' :
                                                    'glass border-white/10 text-muted'
                                            }`}>
                                            {req.status}
                                        </span>
                                    </div>
                                </div>

                                {/* Action Buttons - Only show for non-fulfilled requests */}
                                {req.status !== 'FULFILLED' && (
                                    <div className="flex gap-4 mt-6 pt-6 border-t border-white/5 relative z-10">
                                        <button
                                            onClick={() => handleChase(req.id)}
                                            disabled={actionLoading === req.id}
                                            className="flex-1 flex items-center justify-center gap-2.5 px-4 py-3 glass hover:bg-white/10 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all disabled:opacity-30 border border-white/5 group/btn shadow-glow-sm hover:shadow-primary-500/20"
                                        >
                                            <Send className="w-3.5 h-3.5 group-hover/btn:translate-x-1 transition-transform" />
                                            {actionLoading === req.id ? 'TRANSMITTING...' : 'INITIATE CHASE'}
                                        </button>
                                        <button
                                            onClick={() => handleResolve(req.id)}
                                            disabled={actionLoading === req.id}
                                            className="flex-1 flex items-center justify-center gap-2.5 px-4 py-3 glass-glow-emerald hover:bg-emerald-500/20 text-emerald-400 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all disabled:opacity-30 border border-emerald-500/20"
                                        >
                                            <CheckCircle className="w-3.5 h-3.5" />
                                            RESOLVE PROTOCOL
                                        </button>
                                        {req.status !== 'ESCALATED' && (
                                            <button
                                                onClick={() => handleEscalate(req.id)}
                                                disabled={actionLoading === req.id}
                                                className="flex-1 flex items-center justify-center gap-2.5 px-4 py-3 glass-glow-amber hover:bg-amber-500/20 text-amber-400 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all disabled:opacity-30 border border-amber-500/20"
                                            >
                                                <AlertTriangle className="w-3.5 h-3.5" />
                                                ESCALATE LINK
                                            </button>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))}
                        {(!data.requests || data.requests.length === 0) && (
                            <div className="text-center py-8 text-gray-500">
                                <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p>No requests tracked</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="glass p-8 rounded-[40px] border border-white/5 h-fit relative overflow-hidden">
                    <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
                    <h3 className="text-[10px] font-black text-white uppercase tracking-[0.4em] mb-8 flex items-center gap-3 relative z-10">
                        <Clock className="w-4 h-4 text-primary-500" />
                        Operational Audit Trail
                    </h3>
                    <div className="relative pl-6 space-y-8 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-[1px] before:bg-white/5 relative z-10">
                        {data.audit_logs && data.audit_logs.map((log: any) => (
                            <div key={log.id} className="relative group">
                                <div className={`absolute -left-6 top-1.5 w-2 h-2 rounded-full ring-4 ring-black/40 shadow-glow-sm transition-transform duration-500 group-hover:scale-150 ${log.action === 'CASE_CREATED' ? 'bg-primary-400' :
                                    log.action === 'EMAIL_SENT' ? 'bg-purple-500' :
                                        log.action === 'ESCALATED' || log.action === 'MANUAL_ESCALATION' ? 'bg-amber-500' :
                                            log.action === 'REQUEST_FULFILLED' ? 'bg-emerald-500' :
                                                log.action === 'CHASE_SENT' || log.action === 'MANUAL_CHASE' ? 'bg-primary-500' :
                                                    'bg-muted'
                                    }`} />
                                <p className="text-xs font-bold text-white uppercase tracking-tight mb-1 opacity-80 group-hover:opacity-100 transition-opacity">{log.details}</p>
                                <span className="text-[9px] font-black text-muted uppercase tracking-widest">{new Date(log.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                        ))}
                        {(!data.audit_logs || data.audit_logs.length === 0) && (
                            <p className="text-[10px] font-black text-muted uppercase tracking-widest italic pl-2 opacity-50">Operational Log Clear.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
