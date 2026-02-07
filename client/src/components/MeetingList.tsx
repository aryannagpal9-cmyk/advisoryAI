import { useState, useEffect } from 'react';
import { Video, Calendar, Clock, User, Plus, Search, Loader2, MapPin, MoreHorizontal, FileText } from 'lucide-react';
import { MeetingDetail } from './MeetingDetail';

interface Meeting {
    id: string;
    client_id: string;
    title: string;
    scheduled_at: string;
    type: string;
    status: string;
    location?: string;
    transcript?: string;
    clients?: { name: string };
}

export const MeetingList = ({ refreshTrigger }: { refreshTrigger?: number }) => {
    const [meetings, setMeetings] = useState<Meeting[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(null);

    useEffect(() => {
        const fetchMeetings = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/meetings');
                const data = await res.json();
                setMeetings(data);
            } catch (e) {
                console.error('Failed to fetch meetings:', e);
            } finally {
                setIsLoading(false);
            }
        };
        fetchMeetings();
    }, [refreshTrigger]);


    const filteredMeetings = meetings.filter(m =>
        (m.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (m.clients?.name || '').toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="space-y-6 animate-reveal">
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-center">
                <div className="relative w-full sm:w-96 group">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-primary-400 transition-colors" />
                    <input
                        type="text"
                        placeholder="SEARCH OPERATIONAL SESSIONS..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-white/5 border border-white/5 rounded-2xl pl-11 pr-4 py-3 text-white focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-xs font-bold tracking-wider uppercase placeholder:text-muted/50"
                    />
                </div>
                <button className="w-full sm:w-auto bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-2xl transition-all duration-300 shadow-glow hover:scale-105 active:scale-95 font-bold text-xs uppercase tracking-widest flex items-center justify-center gap-2">
                    <Plus className="w-4 h-4" /> Schedule Protocol
                </button>
            </div>

            {isLoading ? (
                <div className="flex justify-center py-20"><Loader2 className="animate-spin text-primary-500" size={40} /></div>
            ) : filteredMeetings.length === 0 ? (
                <div className="text-center py-24 glass rounded-[32px] border border-dashed border-white/10 relative overflow-hidden">
                    <div className="absolute inset-0 bg-primary-500/5 blur-[100px] pointer-events-none" />
                    <Video size={56} className="text-muted/30 mx-auto mb-6 relative z-10" />
                    <h3 className="text-xl font-black text-white mb-2 relative z-10 uppercase tracking-tight">No Active Protocols</h3>
                    <p className="text-muted font-bold text-xs uppercase tracking-widest relative z-10">Waiting for session initialization</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredMeetings.map(meeting => (
                        <div key={meeting.id} className="glass border border-white/5 rounded-[28px] p-6 hover:border-white/20 transition-all duration-500 group relative overflow-hidden hover:shadow-glow-sm">
                            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="flex justify-between items-start mb-5 relative z-10">
                                <div className={`p-4 rounded-2xl shadow-glow-sm border transition-all duration-500 ${meeting.status === 'COMPLETED' ? 'glass-glow-emerald border-emerald-500/20 text-emerald-400' : 'glass-glow-blue border-primary-500/20 text-primary-400'}`}>
                                    <Video size={24} />
                                </div>
                                <button className="p-2 text-muted hover:text-white hover:bg-white/5 rounded-xl transition-all">
                                    <MoreHorizontal size={20} />
                                </button>
                            </div>

                            <h4 className="text-lg font-black text-white mb-1.5 group-hover:text-primary-400 transition-colors uppercase tracking-tight truncate relative z-10">{meeting.title}</h4>

                            <div className="flex items-center gap-2 text-xs font-bold text-muted uppercase tracking-wider mb-6 relative z-10 opacity-70">
                                <User size={14} className="text-primary-500/50" />
                                <span>{meeting.clients?.name || 'External Entity'}</span>
                            </div>

                            <div className="space-y-3 mb-8 relative z-10">
                                <div className="flex items-center gap-3 text-[10px] font-bold text-muted uppercase tracking-widest group-hover:text-white/60 transition-colors">
                                    <div className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center border border-white/5">
                                        <Calendar size={12} className="text-primary-500/50" />
                                    </div>
                                    <span>{new Date(meeting.scheduled_at).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</span>
                                </div>
                                <div className="flex items-center gap-3 text-[10px] font-bold text-muted uppercase tracking-widest group-hover:text-white/60 transition-colors">
                                    <div className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center border border-white/5">
                                        <Clock size={12} className="text-primary-500/50" />
                                    </div>
                                    <span>{new Date(meeting.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                </div>
                                <div className="flex items-center gap-3 text-[10px] font-bold text-muted uppercase tracking-widest group-hover:text-white/60 transition-colors">
                                    <div className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center border border-white/5">
                                        <MapPin size={12} className="text-primary-500/50" />
                                    </div>
                                    <span className="truncate">{meeting.location || (meeting.type === 'VIDEO' ? 'Neural Link' : 'Operational Hub')}</span>
                                </div>
                            </div>

                            <div className="flex gap-3 relative z-10">
                                <button
                                    onClick={() => setSelectedMeetingId(meeting.id)}
                                    className="flex-1 px-4 py-3 glass hover:bg-white/10 text-white rounded-[18px] text-[10px] font-bold uppercase tracking-widest transition-all border border-white/5 hover:border-white/10"
                                >
                                    Protocol Log
                                </button>
                                {meeting.transcript && (
                                    <button className="px-4 py-3 glass-glow-blue text-primary-400 border border-primary-500/20 rounded-[18px] text-[10px] font-bold uppercase tracking-widest hover:bg-primary-500/10 transition-all flex items-center justify-center gap-2">
                                        <FileText size={14} /> Intelligence
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Meeting Detail Modal */}
            {selectedMeetingId && (
                <MeetingDetail
                    meetingId={selectedMeetingId}
                    onClose={() => setSelectedMeetingId(null)}
                />
            )}
        </div>
    );
};
