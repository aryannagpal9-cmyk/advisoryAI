import React, { useState, useEffect } from 'react';
import { Users, Building, Plus, Search, Edit2, Check, X, Phone, Mail, Globe, Clock } from 'lucide-react';
import { ClientProfile } from './ClientProfile';

interface Client {
    id: string;
    name: string;
    email: string;
    phone?: string;
    created_at: string;
}

interface Provider {
    id: string;
    name: string;
    email: string;
    portal_url?: string;
    standard_response_days: number;
}

export function DataManagement() {
    const [activeTab, setActiveTab] = useState<'clients' | 'providers'>('clients');
    const [clients, setClients] = useState<Client[]>([]);
    const [providers, setProviders] = useState<Provider[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingItem, setEditingItem] = useState<Client | Provider | null>(null);
    const [selectedClientId, setSelectedClientId] = useState<string | null>(null);

    // Form State
    const [formData, setFormData] = useState<any>({});

    useEffect(() => {
        fetchData();
    }, [activeTab]);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const endpoint = activeTab === 'clients' ? '/api/clients' : '/api/providers';
            const response = await fetch(`http://localhost:8000${endpoint}`);
            const data = await response.json();

            if (activeTab === 'clients') {
                setClients(data);
            } else {
                setProviders(data);
            }
        } catch (error) {
            console.error('Failed to fetch data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleOpenModal = (item?: Client | Provider) => {
        setEditingItem(item || null);
        if (item) {
            setFormData(item);
        } else {
            // Default empty form
            setFormData(
                activeTab === 'clients'
                    ? { name: '', email: '', phone: '' }
                    : { name: '', email: '', portal_url: '', standard_response_days: 10 }
            );
        }
        setIsModalOpen(true);
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const endpoint = activeTab === 'clients' ? '/api/clients' : '/api/providers';
            const method = editingItem ? 'PATCH' : 'POST';
            const url = editingItem
                ? `http://localhost:8000${endpoint}/${editingItem.id}`
                : `http://localhost:8000${endpoint}`;

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            if (!response.ok) throw new Error('Failed to save');

            setIsModalOpen(false);
            fetchData(); // Refresh list
        } catch (error) {
            console.error('Save failed:', error);
            alert('Failed to save data');
        }
    };

    const filteredData = (activeTab === 'clients' ? clients : providers).filter((item: any) =>
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.email.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="h-full flex flex-col space-y-6 p-6 overflow-y-auto">
            {/* Header */}
            <div className="flex justify-between items-end mb-4">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight uppercase flex items-center gap-3">
                        <span className="text-gradient-blue">Data</span> Management
                    </h1>
                    <p className="text-muted font-bold uppercase tracking-widest text-[10px] mt-1.5 opacity-70">
                        Operational Registry & Network Command
                    </p>
                </div>

                <button
                    onClick={() => handleOpenModal()}
                    className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-5 py-2.5 rounded-xl transition-all duration-300 shadow-glow hover:scale-105 active:scale-95 font-bold text-xs uppercase tracking-wider"
                >
                    <Plus className="w-4 h-4" />
                    <span>Add {activeTab === 'clients' ? 'Client' : 'Provider'}</span>
                </button>
            </div>

            {/* Tabs & Search */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-center glass p-2 rounded-2xl border border-white/5 relative overflow-hidden">
                <div className="absolute inset-0 bg-primary-500/5 pointer-events-none" />
                <div className="flex gap-2 relative z-10">
                    <button
                        onClick={() => setActiveTab('clients')}
                        className={`flex items-center gap-2 px-6 py-2 rounded-xl transition-all duration-500 font-bold text-xs uppercase tracking-wider ${activeTab === 'clients'
                            ? 'glass-glow-blue text-white shadow-glow-sm border-primary-500/20'
                            : 'text-muted hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <Users className="w-4 h-4" />
                        <span>Clients</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('providers')}
                        className={`flex items-center gap-2 px-6 py-2 rounded-xl transition-all duration-500 font-bold text-xs uppercase tracking-wider ${activeTab === 'providers'
                            ? 'glass-glow-blue text-white shadow-glow-sm border-primary-500/20'
                            : 'text-muted hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <Building className="w-4 h-4" />
                        <span>Providers</span>
                    </button>
                </div>

                <div className="relative w-full sm:w-72 relative z-10">
                    <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted" />
                    <input
                        type="text"
                        placeholder={`SEARCH ${activeTab.toUpperCase()}...`}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-white/5 border border-white/5 text-white pl-11 pr-4 py-2.5 rounded-xl focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-xs font-bold tracking-wider uppercase placeholder:text-muted/50"
                    />
                </div>
            </div>

            {/* List Content */}
            {selectedClientId ? (
                <ClientProfile
                    clientId={selectedClientId}
                    onBack={() => setSelectedClientId(null)}
                />
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {isLoading ? (
                        <div className="col-span-full text-center py-20 text-gray-500">Loading data...</div>
                    ) : filteredData.length === 0 ? (
                        <div className="col-span-full text-center py-20 text-gray-500">
                            No {activeTab} found matching your search.
                        </div>
                    ) : (
                        filteredData.map((item: any) => (
                            <div
                                key={item.id}
                                onClick={() => activeTab === 'clients' && setSelectedClientId(item.id)}
                                className={`glass border border-white/5 rounded-2xl p-6 hover:border-white/20 transition-all duration-500 group relative overflow-hidden animate-reveal cursor-pointer hover:shadow-glow-sm`}
                            >
                                <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                                <div className="flex justify-between items-start mb-5 relative z-10">
                                    <div className="p-3 rounded-xl glass-glow-blue border border-primary-500/20 shadow-glow-sm">
                                        {activeTab === 'clients' ? (
                                            <Users className="w-5 h-5 text-primary-400" />
                                        ) : (
                                            <Building className="w-5 h-5 text-primary-400" />
                                        )}
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleOpenModal(item);
                                        }}
                                        className="p-2 text-muted hover:text-white rounded-lg hover:bg-white/5 transition-all opacity-0 group-hover:opacity-100"
                                    >
                                        <Edit2 className="w-4 h-4" />
                                    </button>
                                </div>

                                <h3 className="text-lg font-bold text-white mb-2 relative z-10 tracking-tight">{item.name}</h3>
                                <div className="space-y-3 text-sm text-white/60 relative z-10">
                                    <div className="flex items-center gap-3">
                                        <div className="w-6 h-6 rounded-md bg-white/5 flex items-center justify-center border border-white/5">
                                            <Mail className="w-3.5 h-3.5 text-muted" />
                                        </div>
                                        <span className="truncate text-xs font-medium">{item.email}</span>
                                    </div>

                                    {activeTab === 'clients' && item.phone && (
                                        <div className="flex items-center gap-3">
                                            <div className="w-6 h-6 rounded-md bg-white/5 flex items-center justify-center border border-white/5">
                                                <Phone className="w-3.5 h-3.5 text-muted" />
                                            </div>
                                            <span className="text-xs font-medium">{item.phone}</span>
                                        </div>
                                    )}

                                    {activeTab === 'providers' && (
                                        <>
                                            {item.portal_url && (
                                                <div className="flex items-center gap-3">
                                                    <div className="w-6 h-6 rounded-md bg-white/5 flex items-center justify-center border border-white/5">
                                                        <Globe className="w-3.5 h-3.5 text-muted" />
                                                    </div>
                                                    <a href={item.portal_url} target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:text-primary-300 hover:underline truncate text-xs font-medium">
                                                        Access Portal
                                                    </a>
                                                </div>
                                            )}
                                            <div className="flex items-center gap-3">
                                                <div className="w-6 h-6 rounded-md bg-white/5 flex items-center justify-center border border-white/5">
                                                    <Clock className="w-3.5 h-3.5 text-muted" />
                                                </div>
                                                <span className="text-xs font-medium">{item.standard_response_days}d response standard</span>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Edit/Create Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-xl flex items-center justify-center z-[100] p-4 animate-reveal">
                    <div className="bg-background/95 w-full max-w-md rounded-[32px] border border-white/5 shadow-2xl overflow-hidden relative">
                        <div className="absolute inset-0 bg-primary-500/5 blur-[100px] pointer-events-none" />

                        <div className="flex justify-between items-center p-8 border-b border-white/5 relative z-10">
                            <div>
                                <h2 className="text-2xl font-black text-white tracking-tight uppercase">
                                    <span className="text-gradient-blue">{editingItem ? 'Update' : 'Register'}</span> {activeTab === 'clients' ? 'Client' : 'Provider'}
                                </h2>
                                <p className="text-[10px] font-bold text-muted uppercase tracking-[0.2em] mt-1">Registry Entry Protocol</p>
                            </div>
                            <button
                                onClick={() => setIsModalOpen(false)}
                                className="p-2 text-muted hover:text-white hover:bg-white/5 rounded-xl transition-all"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <form onSubmit={handleSave} className="p-8 space-y-6 relative z-10">
                            <div className="space-y-1.5">
                                <label className="block text-[10px] font-bold text-muted uppercase tracking-widest ml-1">Identity Designation</label>
                                <input
                                    required
                                    type="text"
                                    value={formData.name || ''}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-3.5 text-white focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-sm font-medium"
                                    placeholder={activeTab === 'clients' ? "Sarah Williams" : "Aviva Operational"}
                                />
                            </div>

                            <div className="space-y-1.5">
                                <label className="block text-[10px] font-bold text-muted uppercase tracking-widest ml-1">Communication Link (Email)</label>
                                <input
                                    required
                                    type="email"
                                    value={formData.email || ''}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-3.5 text-white focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-sm font-medium"
                                    placeholder="contact@entity.com"
                                />
                            </div>

                            {activeTab === 'clients' ? (
                                <div className="space-y-1.5">
                                    <label className="block text-[10px] font-bold text-muted uppercase tracking-widest ml-1">Secure Line (Optional)</label>
                                    <input
                                        type="tel"
                                        value={formData.phone || ''}
                                        onChange={e => setFormData({ ...formData, phone: e.target.value })}
                                        className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-3.5 text-white focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-sm font-medium"
                                        placeholder="+44 7700 900000"
                                    />
                                </div>
                            ) : (
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1.5">
                                        <label className="block text-[10px] font-bold text-muted uppercase tracking-widest ml-1">Portal Access</label>
                                        <input
                                            type="url"
                                            value={formData.portal_url || ''}
                                            onChange={e => setFormData({ ...formData, portal_url: e.target.value })}
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-3.5 text-white focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-sm font-medium"
                                            placeholder="https://..."
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="block text-[10px] font-bold text-muted uppercase tracking-widest ml-1">Response Standard</label>
                                        <input
                                            type="number"
                                            min="1"
                                            value={formData.standard_response_days || 10}
                                            onChange={e => setFormData({ ...formData, standard_response_days: parseInt(e.target.value) })}
                                            className="w-full bg-white/5 border border-white/5 rounded-2xl px-5 py-3.5 text-white focus:outline-none focus:border-primary-500/50 focus:shadow-glow-sm transition-all text-sm font-medium"
                                        />
                                    </div>
                                </div>
                            )}

                            <div className="flex justify-end pt-6 gap-4">
                                <button
                                    type="button"
                                    onClick={() => setIsModalOpen(false)}
                                    className="px-6 py-3 text-muted hover:text-white font-bold text-xs uppercase tracking-widest transition-all"
                                >
                                    Abort
                                </button>
                                <button
                                    type="submit"
                                    className="px-8 py-3 bg-primary-600 hover:bg-primary-500 text-white rounded-2xl transition-all duration-300 shadow-glow font-bold text-xs uppercase tracking-widest flex items-center gap-2"
                                >
                                    <Check className="w-4 h-4" />
                                    <span>Commit Changes</span>
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
