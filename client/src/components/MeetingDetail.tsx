import { useState, useEffect } from 'react';
import { X, Video, Calendar, Clock, User, MapPin, FileText, CheckSquare, Loader2 } from 'lucide-react';

interface MeetingDetailProps {
    meetingId: string;
    onClose: () => void;
}

interface Meeting {
    id: string;
    title: string;
    scheduled_at: string;
    status: string;
    meeting_type?: string;
    location?: string;
    notes?: string;
    transcript?: string;
    agenda?: string;
    clients?: {
        id: string;
        name: string;
        email: string;
    };
    action_items?: Array<{
        id: string;
        title: string;
        status: string;
        priority: string;
    }>;
}

export const MeetingDetail = ({ meetingId, onClose }: MeetingDetailProps) => {
    const [meeting, setMeeting] = useState<Meeting | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchMeeting = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/meetings/${meetingId}`);
                if (!res.ok) throw new Error('Meeting not found');
                const data = await res.json();
                setMeeting(data);
            } catch (e: any) {
                setError(e.message);
            } finally {
                setIsLoading(false);
            }
        };
        fetchMeeting();
    }, [meetingId]);

    if (isLoading) {
        return (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 animate-reveal">
                <div className="glass rounded-[40px] p-16 shadow-glow flex flex-col items-center">
                    <Loader2 className="animate-spin text-primary-500 mb-4" size={48} />
                    <p className="text-[10px] font-black uppercase tracking-[0.4em] text-primary-500/60">Decrypting Session...</p>
                </div>
            </div>
        );
    }

    if (error || !meeting) {
        return (
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="bg-gray-900 rounded-2xl p-10 text-center">
                    <p className="text-red-400 mb-4">{error || 'Meeting not found'}</p>
                    <button onClick={onClose} className="px-4 py-2 bg-gray-700 rounded-lg text-white">Close</button>
                </div>
            </div>
        );
    }

    const statusColors: Record<string, string> = {
        SCHEDULED: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        COMPLETED: 'bg-green-500/10 text-green-400 border-green-500/20',
        CANCELLED: 'bg-red-500/10 text-red-400 border-red-500/20',
    };

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4 animate-reveal">
            <div className="glass border border-white/5 rounded-[40px] w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col shadow-glow relative">
                <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
                {/* Header */}
                <div className="p-8 border-b border-white/5 flex justify-between items-start relative z-10 glass">
                    <div className="flex items-start gap-6">
                        <div className={`p-5 rounded-[20px] shadow-glow-sm border transition-all duration-500 ${meeting.status === 'COMPLETED' ? 'glass-glow-emerald border-emerald-500/20 text-emerald-400' : 'glass-glow-blue border-primary-500/20 text-primary-400'}`}>
                            <Video size={32} />
                        </div>
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-muted mb-2">Protocol Session Registry</p>
                            <h2 className="text-3xl font-black text-white mb-2 leading-tight uppercase tracking-tight">{meeting.title}</h2>
                            <div className="flex items-center gap-4 text-[10px] font-black uppercase tracking-widest">
                                <span className="flex items-center gap-2 text-primary-400 group">
                                    <User size={14} className="text-primary-500/50" />
                                    {meeting.clients?.name || 'External Entity'}
                                </span>
                                <span className="text-white/10">|</span>
                                <span className={`px-3 py-1 rounded-xl border ${statusColors[meeting.status] || statusColors.SCHEDULED}`}>
                                    {meeting.status}
                                </span>
                            </div>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-3 hover:bg-white/10 rounded-2xl transition-all group">
                        <X size={24} className="text-muted group-hover:text-white" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8 relative z-10 custom-scrollbar">
                    {/* Details Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="glass bg-white/[0.03] p-5 rounded-[24px] border border-white/5 group hover:border-white/10 transition-all">
                            <p className="text-[9px] text-muted uppercase font-black tracking-[0.3em] mb-3 opacity-50 text-center">Protocol Date</p>
                            <div className="flex items-center justify-center gap-3 text-white">
                                <Calendar size={18} className="text-primary-400 shadow-glow-sm" />
                                <span className="font-bold text-sm tracking-widest uppercase">{new Date(meeting.scheduled_at).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' })}</span>
                            </div>
                        </div>
                        <div className="glass bg-white/[0.03] p-5 rounded-[24px] border border-white/5 group hover:border-white/10 transition-all">
                            <p className="text-[9px] text-muted uppercase font-black tracking-[0.3em] mb-3 opacity-50 text-center">Session Clock</p>
                            <div className="flex items-center justify-center gap-3 text-white">
                                <Clock size={18} className="text-primary-400 shadow-glow-sm" />
                                <span className="font-bold text-sm tracking-widest uppercase">{new Date(meeting.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                        </div>
                        <div className="glass bg-white/[0.03] p-5 rounded-[24px] border border-white/5 group hover:border-white/10 transition-all">
                            <p className="text-[9px] text-muted uppercase font-black tracking-[0.3em] mb-3 opacity-50 text-center">Interface Location</p>
                            <div className="flex items-center justify-center gap-3 text-white">
                                <MapPin size={18} className="text-primary-400 shadow-glow-sm" />
                                <span className="font-bold text-sm tracking-widest uppercase truncate max-w-[150px]">{meeting.location || (meeting.meeting_type === 'VIDEO_CALL' ? 'Neural Link' : 'Operational Hub')}</span>
                            </div>
                        </div>
                    </div>

                    {/* Client Info */}
                    {meeting.clients && (
                        <div className="glass bg-white/[0.02] p-6 rounded-[28px] border border-white/5 relative overflow-hidden group">
                            <div className="absolute inset-0 bg-primary-500/[0.01] pointer-events-none" />
                            <h3 className="text-[10px] font-black text-muted uppercase tracking-[0.4em] mb-5 opacity-40">Primary Target Profile</h3>
                            <div className="flex items-center gap-6 relative z-10">
                                <div className="w-16 h-16 glass-glow-blue border border-primary-500/20 rounded-[22px] flex items-center justify-center text-primary-400 font-black text-2xl shadow-glow-sm group-hover:scale-105 transition-transform duration-500">
                                    {meeting.clients.name.charAt(0)}
                                </div>
                                <div className="space-y-1">
                                    <p className="text-white font-black text-xl uppercase tracking-tighter">{meeting.clients.name}</p>
                                    <p className="text-primary-500/60 font-bold text-xs uppercase tracking-widest">{meeting.clients.email}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Notes */}
                    {meeting.notes && (
                        <div className="bg-gray-800/30 p-5 rounded-xl border border-gray-700/50">
                            <h3 className="text-sm font-bold text-gray-400 uppercase mb-3">Notes</h3>
                            <p className="text-gray-300 whitespace-pre-wrap">{meeting.notes}</p>
                        </div>
                    )}

                    {/* Transcript */}
                    {meeting.transcript && (
                        <div className="glass bg-white/[0.02] p-8 rounded-[32px] border border-white/5 group relative overflow-hidden">
                            <div className="absolute inset-0 bg-primary-500/[0.01] pointer-events-none" />
                            <h3 className="text-[10px] font-black text-muted uppercase tracking-[0.4em] mb-6 flex items-center gap-3 relative z-10 opacity-40">
                                <FileText size={18} className="text-primary-500" />
                                Intelligence Transcript Decode
                            </h3>
                            <div className="text-white/80 text-sm leading-relaxed max-h-64 overflow-y-auto custom-scrollbar pr-4 relative z-10 font-medium italic">
                                "{meeting.transcript}"
                            </div>
                        </div>
                    )}

                    {/* Action Items */}
                    {meeting.action_items && meeting.action_items.length > 0 && (
                        <div className="glass bg-white/[0.02] p-8 rounded-[32px] border border-white/5 relative overflow-hidden">
                            <h3 className="text-[10px] font-black text-muted uppercase tracking-[0.4em] mb-6 flex items-center gap-3 opacity-40">
                                <CheckSquare size={18} className="text-primary-500" />
                                Operational Directives ({meeting.action_items.length})
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {meeting.action_items.map(item => (
                                    <div key={item.id} className="flex items-center justify-between p-5 glass bg-white/[0.03] border border-white/5 rounded-[22px] group hover:border-white/10 transition-all duration-300">
                                        <span className="text-xs font-bold text-white uppercase tracking-tight group-hover:text-primary-400 transition-colors">{item.title}</span>
                                        <span className={`text-[8px] px-3 py-1 rounded-lg font-black uppercase tracking-widest ${item.status === 'COMPLETED' ? 'glass-glow-emerald text-emerald-400' : 'glass bg-white/5 text-muted'}`}>
                                            {item.status}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-white/5 bg-white/[0.02] flex justify-end gap-5 relative z-10">
                    <button onClick={onClose} className="px-8 py-3 text-muted hover:text-white font-black text-[10px] uppercase tracking-[0.3em] transition-all">Abbreviate Session</button>
                    {meeting.status === 'SCHEDULED' && (
                        <button className="px-10 py-3 bg-primary-600 hover:bg-primary-500 text-white rounded-[20px] font-black text-[10px] uppercase tracking-[0.3em] transition-all shadow-glow hover:shadow-primary-500/40">
                            Commit Complete
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};
