import { useState } from 'react';
import { X, Briefcase, User, Plus, Trash2, Building } from 'lucide-react';

export function NewCase({ onClose, onSubmit }: { onClose: () => void, onSubmit: (data: any) => void }) {
    const [formData, setFormData] = useState({
        clientName: '',
        clientEmail: '',
        caseType: 'Pension Consolidation',
        description: '',
        providerName: '',
        providerEmail: '',
        isPriority: false,
        items: [] as { title: string, type: 'CLIENT' | 'PROVIDER' }[]
    });

    const [newItem, setNewItem] = useState('');
    const [newItemType, setNewItemType] = useState<'CLIENT' | 'PROVIDER'>('CLIENT');

    const handleAddItem = () => {
        if (!newItem) return;
        setFormData({
            ...formData,
            items: [...formData.items, { title: newItem, type: newItemType }]
        });
        setNewItem('');
    };

    const handleRemoveItem = (idx: number) => {
        setFormData({
            ...formData,
            items: formData.items.filter((_, i) => i !== idx)
        });
    };

    const handleSubmit = () => {
        // Transform to backend expected format
        const payload = {
            client_name: formData.clientName,
            client_email: formData.clientEmail,
            provider_name: formData.providerName,
            provider_email: formData.providerEmail,
            title: formData.caseType,
            description: formData.description || `New ${formData.caseType} case`,
            is_priority: formData.isPriority,
            items: formData.items
        };
        onSubmit(payload);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-reveal">
            <div className="absolute inset-0 bg-black/80 backdrop-blur-md" onClick={onClose} />

            <div className="glass w-full max-w-2xl relative border border-white/5 shadow-glow rounded-[40px] max-h-[90vh] overflow-hidden flex flex-col">
                <div className="absolute inset-0 bg-primary-500/[0.02] pointer-events-none" />

                <div className="p-8 glass border-b border-white/5 flex justify-between items-center relative z-10">
                    <div>
                        <p className="text-[10px] font-black text-muted uppercase tracking-[0.4em] mb-2">Protocol Initialization</p>
                        <h2 className="text-2xl font-black text-white flex items-center gap-4 uppercase tracking-tighter">
                            <Briefcase className="w-6 h-6 text-primary-500" />
                            Launch New Case
                        </h2>
                    </div>
                    <button onClick={onClose} className="p-3 hover:bg-white/10 rounded-2xl transition-all group">
                        <X size={24} className="text-muted group-hover:text-white" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-10 space-y-10 relative z-10 custom-scrollbar">
                    {/* Case Info */}
                    <section className="space-y-6">
                        <div className="flex items-center gap-3">
                            <div className="w-1.5 h-5 bg-primary-500 rounded-full shadow-glow" />
                            <h3 className="text-[10px] font-black text-muted uppercase tracking-[0.3em]">Core Parameters</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-muted uppercase tracking-widest ml-1">Case Type</label>
                                <div className="relative group">
                                    <select
                                        className="w-full bg-white/5 border border-white/5 rounded-[18px] px-5 py-4 text-sm font-bold text-white focus:outline-none focus:border-primary-500/30 transition-all appearance-none cursor-pointer"
                                        value={formData.caseType}
                                        onChange={e => setFormData({ ...formData, caseType: e.target.value })}
                                    >
                                        <option>Pension Consolidation</option>
                                        <option>Mortgage Application</option>
                                        <option>Investment Transfer</option>
                                        <option>Protection Application</option>
                                    </select>
                                    <div className="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none opacity-40">
                                        ▼
                                    </div>
                                </div>
                            </div>
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-muted uppercase tracking-widest ml-1">Objective</label>
                                <input
                                    type="text"
                                    className="w-full bg-white/5 border border-white/5 rounded-[18px] px-5 py-4 text-sm font-bold text-white placeholder:text-muted/30 focus:outline-none focus:border-primary-500/30 transition-all"
                                    placeholder="Brief designation..."
                                    value={formData.description}
                                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="mt-4 glass bg-primary-500/[0.03] p-6 rounded-[24px] border border-primary-500/10">
                            <label className="flex items-center gap-6 cursor-pointer group">
                                <div className="relative">
                                    <input
                                        type="checkbox"
                                        className="sr-only peer"
                                        checked={formData.isPriority}
                                        onChange={e => setFormData({ ...formData, isPriority: e.target.checked })}
                                    />
                                    <div className="w-14 h-7 bg-white/5 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600 shadow-inner"></div>
                                </div>
                                <div>
                                    <span className="text-[10px] font-black text-white uppercase tracking-widest block mb-1">Redline Priority</span>
                                    <p className="text-[9px] font-bold text-muted uppercase tracking-widest opacity-60 leading-relaxed">Engage maximum acceleration protocols for immediate resolution</p>
                                </div>
                            </label>
                        </div>
                    </section>


                    {/* Client Info */}
                    <section className="space-y-6">
                        <div className="flex items-center gap-3">
                            <div className="w-1.5 h-5 bg-emerald-500 rounded-full shadow-glow" />
                            <h3 className="text-[10px] font-black text-muted uppercase tracking-[0.3em]">Client Interface</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 glass bg-emerald-500/[0.02] border border-emerald-500/10 rounded-[32px]">
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-muted uppercase tracking-widest ml-1">Entity Name</label>
                                <div className="relative group/input">
                                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within/input:text-emerald-400 transition-colors" />
                                    <input
                                        type="text"
                                        className="w-full bg-white/5 border border-white/5 rounded-[18px] pl-12 pr-4 py-4 text-sm font-bold text-white focus:outline-none focus:border-emerald-500/30 transition-all"
                                        placeholder="Identification handle..."
                                        value={formData.clientName}
                                        onChange={e => setFormData({ ...formData, clientName: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-muted uppercase tracking-widest ml-1">Transmission Address</label>
                                <input
                                    type="email"
                                    className="w-full bg-white/5 border border-white/5 rounded-[18px] px-5 py-4 text-sm font-bold text-white focus:outline-none focus:border-emerald-500/30 transition-all"
                                    placeholder="client@terminal.hub"
                                    value={formData.clientEmail}
                                    onChange={e => setFormData({ ...formData, clientEmail: e.target.value })}
                                />
                            </div>
                        </div>
                    </section>

                    {/* Provider Info */}
                    <section className="space-y-6">
                        <div className="flex items-center gap-3">
                            <div className="w-1.5 h-5 bg-primary-500 rounded-full shadow-glow" />
                            <h3 className="text-[10px] font-black text-muted uppercase tracking-[0.3em]">Provider Gateway</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 glass bg-primary-500/[0.02] border border-primary-500/10 rounded-[32px]">
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-muted uppercase tracking-widest ml-1">Network Entity</label>
                                <div className="relative group/input">
                                    <Building className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted group-focus-within/input:text-primary-400 transition-colors" />
                                    <input
                                        type="text"
                                        className="w-full bg-white/5 border border-white/5 rounded-[18px] pl-12 pr-4 py-4 text-sm font-bold text-white focus:outline-none focus:border-primary-500/30 transition-all"
                                        placeholder="Operational node..."
                                        value={formData.providerName}
                                        onChange={e => setFormData({ ...formData, providerName: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-muted uppercase tracking-widest ml-1">Data Uplink</label>
                                <input
                                    type="email"
                                    className="w-full bg-white/5 border border-white/5 rounded-[18px] px-5 py-4 text-sm font-bold text-white focus:outline-none focus:border-primary-500/30 transition-all"
                                    placeholder="uplink@node.net"
                                    value={formData.providerEmail}
                                    onChange={e => setFormData({ ...formData, providerEmail: e.target.value })}
                                />
                            </div>
                        </div>
                    </section>

                    {/* Requirements */}
                    <section className="space-y-4 pt-4 border-t border-white/5">
                        <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider">Required Actions / Documents</h3>

                        <div className="flex gap-2">
                            <select
                                className="bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-white/40 focus:outline-none text-sm"
                                value={newItemType}
                                onChange={e => setNewItemType(e.target.value as any)}
                            >
                                <option value="CLIENT">Client Must Provide</option>
                                <option value="PROVIDER">Provider Must Provide</option>
                            </select>
                            <input
                                type="text"
                                className="flex-1 bg-black/20 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-white/40 focus:outline-none text-sm"
                                placeholder="e.g. Passport Copy or Letter of Authority"
                                value={newItem}
                                onChange={e => setNewItem(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && handleAddItem()}
                            />
                            <button
                                onClick={handleAddItem}
                                className="p-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors border border-white/10"
                            >
                                <Plus size={20} />
                            </button>
                        </div>

                        <div className="space-y-2 max-h-40 overflow-y-auto">
                            {formData.items.map((item, idx) => (
                                <div key={idx} className="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/5 group">
                                    <div className="flex items-center gap-3">
                                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${item.type === 'CLIENT' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-purple-500/20 text-purple-400'
                                            }`}>
                                            {item.type}
                                        </span>
                                        <span className="text-sm text-gray-200">{item.title}</span>
                                    </div>
                                    <button
                                        onClick={() => handleRemoveItem(idx)}
                                        className="text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </div>
                            ))}
                            {formData.items.length === 0 && (
                                <p className="text-xs text-center text-gray-600 py-2">No requirements added yet.</p>
                            )}
                        </div>
                    </section>

                    <div className="pt-6 flex justify-end gap-3 border-t border-white/10">
                        <button onClick={onClose} className="px-4 py-2 text-gray-400 hover:text-white transition-colors">
                            Cancel
                        </button>
                        <button
                            onClick={handleSubmit}
                            disabled={!formData.clientName || !formData.providerName}
                            className="bg-white hover:bg-gray-200 text-black px-6 py-2 rounded-lg font-bold shadow-lg transition-all active:scale-95 disabled:bg-white/20 disabled:text-white/40"
                        >
                            Create Case
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
