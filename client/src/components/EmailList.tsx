import { useState, useEffect } from 'react';
import { Mail, Search, Send, Loader2, User } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface Email {
    id: string;
    subject: string;
    body: string;
    status: string;
    client_name?: string;
    to_email: string;
    created_at: string;
    context_type?: string;
    clients?: { name: string };
}

export const EmailList = ({ refreshTrigger }: { refreshTrigger?: number }) => {
    const [emails, setEmails] = useState<Email[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);

    useEffect(() => {
        const fetchEmails = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/emails`);
                const data = await res.json();
                setEmails(data);
            } catch (e) {
                console.error('Failed to fetch emails:', e);
            } finally {
                setIsLoading(false);
            }
        };
        fetchEmails();
    }, [refreshTrigger]);

    const filteredEmails = emails.filter(e =>
        e.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (e.clients?.name || '').toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="flex gap-6 h-[calc(100vh-220px)] animate-reveal">
            {/* List */}
            <div className="w-1/3 flex flex-col gap-6">
                <div className="relative group">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within:text-primary-400 transition-colors" />
                    <input
                        type="text"
                        placeholder="SEARCH INTEL..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-white/5 border border-white/5 rounded-2xl pl-11 pr-4 py-3 text-white focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-xs font-bold tracking-wider uppercase placeholder:text-muted/50"
                    />
                </div>

                <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                    {isLoading ? (
                        <div className="flex justify-center py-10"><Loader2 className="animate-spin text-primary-500" /></div>
                    ) : filteredEmails.length === 0 ? (
                        <div className="text-center py-10 text-muted font-bold text-xs uppercase tracking-widest">No Intelligence Found</div>
                    ) : (
                        filteredEmails.map(email => {
                            const isInbound = email.context_type === 'INBOUND';
                            return (
                                <button
                                    key={email.id}
                                    onClick={() => setSelectedEmail(email)}
                                    className={`w-full text-left p-5 rounded-2xl border transition-all duration-500 group relative overflow-hidden ${selectedEmail?.id === email.id
                                        ? 'glass-glow-blue border-primary-500/30 shadow-glow-sm'
                                        : 'glass border-white/5 hover:border-white/20'
                                        }`}
                                >
                                    <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                    <div className="flex justify-between items-start mb-2 relative z-10">
                                        <div className="flex items-center gap-2">
                                            <span className={`text-[9px] font-black uppercase tracking-[0.2em] px-2 py-0.5 rounded-md ${isInbound ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                                                {isInbound ? 'INBOUND' : email.status}
                                            </span>
                                            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-muted-foreground/40">{isInbound ? '←' : '→'}</span>
                                        </div>
                                        <span className="text-[9px] font-bold text-muted uppercase tracking-widest">{new Date(email.created_at).toLocaleDateString()}</span>
                                    </div>
                                    <h4 className={`font-black text-sm truncate mb-1.5 tracking-tight relative z-10 transition-colors ${selectedEmail?.id === email.id ? 'text-white' : 'text-white/80 group-hover:text-white'}`}>{email.subject}</h4>
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-muted uppercase tracking-widest relative z-10">
                                        <User size={12} className="text-primary-500/30" />
                                        <span>{email.clients?.name || 'External Sink'}</span>
                                    </div>
                                </button>
                            );
                        })
                    )}
                </div>
            </div>

            {/* Detail */}
            <div className="flex-1 glass border border-white/5 rounded-[32px] overflow-hidden flex flex-col relative">
                <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />
                {selectedEmail ? (
                    <>
                        <div className="p-8 border-b border-white/5 glass relative z-10">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <h2 className="text-2xl font-black text-white tracking-tight leading-tight uppercase mb-2">{selectedEmail.subject}</h2>
                                    <p className="text-[10px] font-bold text-muted uppercase tracking-[0.3em]">Operational Transmission Log</p>
                                </div>
                                <div className="px-4 py-1.5 glass-glow-emerald border border-emerald-500/20 rounded-xl text-emerald-400 text-[10px] font-black uppercase tracking-widest shadow-glow-sm">
                                    Status: {selectedEmail.context_type === 'INBOUND' ? 'RECEIVED' : selectedEmail.status}
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-6">
                                <div className="glass bg-white/[0.03] p-4 rounded-2xl border border-white/5 group hover:border-white/10 transition-colors">
                                    <p className="text-[9px] text-muted uppercase font-black tracking-widest mb-1.5 opacity-50">Origin Point</p>
                                    <p className="text-xs text-white font-bold tracking-tight uppercase group-hover:text-primary-400 transition-colors">
                                        {selectedEmail.context_type === 'INBOUND' ? selectedEmail.clients?.name : 'Strategic AI Hub'}
                                        {selectedEmail.context_type === 'INBOUND' ? '' : <span className="text-muted font-medium normal-case ml-1">{"<core@advisors.ai>"}</span>}
                                    </p>
                                </div>
                                <div className="glass bg-white/[0.03] p-4 rounded-2xl border border-white/5 group hover:border-white/10 transition-colors">
                                    <p className="text-[9px] text-muted uppercase font-black tracking-widest mb-1.5 opacity-50">Target Destination</p>
                                    <p className="text-xs text-white font-bold tracking-tight uppercase group-hover:text-primary-400 transition-colors">
                                        {selectedEmail.context_type === 'INBOUND' ? 'Strategic AI Hub' : selectedEmail.clients?.name}
                                        <span className="text-muted font-medium normal-case ml-1">{" <" + selectedEmail.to_email + ">"}</span>
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div className="p-10 flex-1 overflow-y-auto bg-transparent relative z-10 custom-scrollbar">
                            <div className="max-w-none">
                                {selectedEmail.body.split('\n').map((line: string, i: number) => (
                                    <p key={i} className="text-white/80 text-sm leading-relaxed mb-6 font-medium whitespace-pre-wrap">{line}</p>
                                ))}
                            </div>
                        </div>
                        <div className="p-6 border-t border-white/5 bg-white/[0.02] flex justify-end gap-4 relative z-10">
                            <button className="px-6 py-3 text-muted hover:text-white font-bold text-xs uppercase tracking-widest transition-all">Archive Thread</button>
                            <button className="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white rounded-2xl font-black text-xs uppercase tracking-widest transition-all shadow-glow hover:shadow-primary-500/40 flex items-center gap-2">
                                <Send size={16} /> Re-Transmit
                            </button>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-muted p-12 text-center relative z-10">
                        <div className="w-24 h-24 glass rounded-full flex items-center justify-center mb-8 border border-white/5 shadow-glow-sm">
                            <Mail size={40} className="text-primary-500/40" />
                        </div>
                        <h3 className="text-2xl font-black text-white mb-3 uppercase tracking-tight">Intelligence Sink</h3>
                        <p className="max-w-xs text-xs font-bold uppercase tracking-[0.2em] opacity-40 leading-loose">Select a transmission vector from the left console to initialize data decryption.</p>
                    </div>
                )}
            </div>
        </div>
    );
};
