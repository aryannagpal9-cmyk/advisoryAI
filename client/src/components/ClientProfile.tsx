import { useState, useEffect } from 'react';
import { User, Mail, Phone, Briefcase, Shield, Calendar, CheckSquare, TrendingUp, Loader2, ArrowLeft } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface ClientProfileProps {
    clientId: string;
    onBack: () => void;
}

interface ClientData {
    client: {
        id: string;
        name: string;
        email: string;
        phone?: string;
        created_at: string;
    };
    profile?: {
        date_of_birth?: string;
        occupation?: string;
        marital_status?: string;
        dependents?: number;
        risk_profile?: string;
        annual_income?: number;
        notes?: string;
    };
    investments: {
        items: Array<{
            id: string;
            type: string;
            provider: string;
            current_value: number;
            annual_contribution?: number;
        }>;
        total_value: number;
    };
    protection: Array<{
        id: string;
        type: string;
        provider: string;
        sum_assured: number;
        premium_monthly?: number;
    }>;
    recent_meetings: Array<{
        id: string;
        title: string;
        scheduled_at: string;
        status: string;
    }>;
    open_actions: Array<{
        id: string;
        title: string;
        status: string;
        due_date?: string;
    }>;
    cases?: Array<{
        id: string;
        title: string;
        status: string;
        created_at: string;
    }>;
}

export const ClientProfile = ({ clientId, onBack }: ClientProfileProps) => {
    const [data, setData] = useState<ClientData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/clients/${clientId}/profile`);
                if (!res.ok) throw new Error('Client not found');
                const profile = await res.json();

                // Also fetch cases
                const casesRes = await fetch(`${API_BASE_URL}/api/cases?client_id=${clientId}`);
                const cases = casesRes.ok ? await casesRes.json() : [];

                setData({ ...profile, cases });
            } catch (e: any) {
                setError(e.message);
            } finally {
                setIsLoading(false);
            }
        };
        fetchProfile();
    }, [clientId]);

    if (isLoading) {
        return (
            <div className="flex justify-center items-center h-96">
                <Loader2 className="animate-spin text-blue-500" size={48} />
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="text-center py-20">
                <p className="text-red-400 mb-4">{error || 'Client not found'}</p>
                <button onClick={onBack} className="px-4 py-2 bg-gray-700 rounded-lg text-white">Back</button>
            </div>
        );
    }

    const { client, profile, investments, protection, recent_meetings, open_actions, cases } = data;

    const formatCurrency = (val: number) => new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(val);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4 mb-6">
                <button onClick={onBack} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
                    <ArrowLeft size={20} className="text-gray-400" />
                </button>
                <div className="flex items-center gap-4 flex-1">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center text-white font-bold text-2xl shadow-lg">
                        {client.name.charAt(0)}
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white">{client.name}</h1>
                        <div className="flex items-center gap-4 text-gray-400 mt-1">
                            <span className="flex items-center gap-1"><Mail size={14} /> {client.email}</span>
                            {client.phone && <span className="flex items-center gap-1"><Phone size={14} /> {client.phone}</span>}
                        </div>
                    </div>
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border border-blue-500/20 rounded-2xl p-5">
                    <p className="text-xs text-gray-400 uppercase font-bold mb-1">Total Investments</p>
                    <p className="text-2xl font-bold text-white">{formatCurrency(investments.total_value)}</p>
                </div>
                <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20 rounded-2xl p-5">
                    <p className="text-xs text-gray-400 uppercase font-bold mb-1">Protection Policies</p>
                    <p className="text-2xl font-bold text-white">{protection.length}</p>
                </div>
                <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-2xl p-5">
                    <p className="text-xs text-gray-400 uppercase font-bold mb-1">Active Cases</p>
                    <p className="text-2xl font-bold text-white">{cases?.filter(c => c.status === 'ACTIVE').length || 0}</p>
                </div>
                <div className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20 rounded-2xl p-5">
                    <p className="text-xs text-gray-400 uppercase font-bold mb-1">Open Actions</p>
                    <p className="text-2xl font-bold text-white">{open_actions.length}</p>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Profile & Investments */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Profile Info */}
                    {profile && (
                        <div className="bg-gray-800/40 border border-gray-700/50 rounded-2xl p-6">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <User size={20} className="text-blue-400" /> Personal Information
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                {profile.date_of_birth && (
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase">Date of Birth</p>
                                        <p className="text-white">{new Date(profile.date_of_birth).toLocaleDateString()}</p>
                                    </div>
                                )}
                                {profile.occupation && (
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase">Occupation</p>
                                        <p className="text-white">{profile.occupation}</p>
                                    </div>
                                )}
                                {profile.marital_status && (
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase">Marital Status</p>
                                        <p className="text-white">{profile.marital_status}</p>
                                    </div>
                                )}
                                {profile.dependents !== undefined && (
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase">Dependents</p>
                                        <p className="text-white">{profile.dependents}</p>
                                    </div>
                                )}
                                {profile.risk_profile && (
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase">Risk Profile</p>
                                        <p className="text-white">{profile.risk_profile}</p>
                                    </div>
                                )}
                                {profile.annual_income && (
                                    <div>
                                        <p className="text-xs text-gray-500 uppercase">Annual Income</p>
                                        <p className="text-white">{formatCurrency(profile.annual_income)}</p>
                                    </div>
                                )}
                            </div>
                            {profile.notes && (
                                <div className="mt-4 pt-4 border-t border-gray-700/50">
                                    <p className="text-xs text-gray-500 uppercase mb-1">Advisor Notes</p>
                                    <p className="text-gray-300 text-sm">{profile.notes}</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Investments */}
                    <div className="bg-gray-800/40 border border-gray-700/50 rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <TrendingUp size={20} className="text-green-400" /> Investment Portfolio
                        </h3>
                        {investments.items.length > 0 ? (
                            <div className="space-y-3">
                                {investments.items.map(inv => (
                                    <div key={inv.id} className="flex justify-between items-center p-4 bg-gray-900/50 rounded-xl">
                                        <div>
                                            <p className="text-white font-semibold">{inv.type}</p>
                                            <p className="text-gray-500 text-sm">{inv.provider}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-white font-bold">{formatCurrency(inv.current_value)}</p>
                                            {inv.annual_contribution && (
                                                <p className="text-gray-500 text-xs">+{formatCurrency(inv.annual_contribution)}/yr</p>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-center py-8">No investments on record.</p>
                        )}
                    </div>

                    {/* Protection */}
                    <div className="bg-gray-800/40 border border-gray-700/50 rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Shield size={20} className="text-purple-400" /> Protection Policies
                        </h3>
                        {protection.length > 0 ? (
                            <div className="space-y-3">
                                {protection.map(pol => (
                                    <div key={pol.id} className="flex justify-between items-center p-4 bg-gray-900/50 rounded-xl">
                                        <div>
                                            <p className="text-white font-semibold">{pol.type}</p>
                                            <p className="text-gray-500 text-sm">{pol.provider}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-white font-bold">{formatCurrency(pol.sum_assured)}</p>
                                            {pol.premium_monthly && (
                                                <p className="text-gray-500 text-xs">{formatCurrency(pol.premium_monthly)}/mo</p>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-center py-8">No protection policies on record.</p>
                        )}
                    </div>
                </div>

                {/* Right Column: Activity */}
                <div className="space-y-6">
                    {/* Cases */}
                    <div className="bg-gray-800/40 border border-gray-700/50 rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Briefcase size={20} className="text-blue-400" /> Cases
                        </h3>
                        {cases && cases.length > 0 ? (
                            <div className="space-y-2">
                                {cases.slice(0, 5).map(c => (
                                    <div key={c.id} className="flex justify-between items-center p-3 bg-gray-900/50 rounded-lg">
                                        <span className="text-white text-sm truncate flex-1">{c.title}</span>
                                        <span className={`text-xs px-2 py-1 rounded-full ml-2 ${c.status === 'COMPLETED' ? 'bg-green-500/10 text-green-400' :
                                            c.status === 'ACTIVE' ? 'bg-blue-500/10 text-blue-400' :
                                                'bg-gray-500/10 text-gray-400'
                                            }`}>{c.status}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-sm">No cases.</p>
                        )}
                    </div>

                    {/* Recent Meetings */}
                    <div className="bg-gray-800/40 border border-gray-700/50 rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Calendar size={20} className="text-amber-400" /> Recent Meetings
                        </h3>
                        {recent_meetings.length > 0 ? (
                            <div className="space-y-2">
                                {recent_meetings.map(m => (
                                    <div key={m.id} className="p-3 bg-gray-900/50 rounded-lg">
                                        <p className="text-white text-sm font-medium truncate">{m.title}</p>
                                        <p className="text-gray-500 text-xs">{new Date(m.scheduled_at).toLocaleDateString()}</p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-sm">No recent meetings.</p>
                        )}
                    </div>

                    {/* Open Actions */}
                    <div className="bg-gray-800/40 border border-gray-700/50 rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <CheckSquare size={20} className="text-red-400" /> Open Actions
                        </h3>
                        {open_actions.length > 0 ? (
                            <div className="space-y-2">
                                {open_actions.map(a => (
                                    <div key={a.id} className="flex justify-between items-center p-3 bg-gray-900/50 rounded-lg">
                                        <span className="text-white text-sm truncate flex-1">{a.title}</span>
                                        <span className={`text-xs px-2 py-1 rounded-full ml-2 ${a.status === 'OVERDUE' ? 'bg-red-500/10 text-red-400' :
                                            'bg-yellow-500/10 text-yellow-400'
                                            }`}>{a.status}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-sm">No open actions.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
