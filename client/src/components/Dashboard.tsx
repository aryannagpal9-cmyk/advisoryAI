import { useEffect, useState } from 'react';
import { API_BASE_URL } from '../config';
import {
    Users,
    FileText,
    Trophy,
    AlertTriangle,
    Zap,
    Activity,
    Plus,
    ArrowUpRight,
    TrendingUp,
    PieChart as PieChartIcon,
    Mail,
    CheckSquare,
    FileCheck,
    Send,
    ChevronRight
} from 'lucide-react';
import clsx from 'clsx';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts';

interface DashboardProps {
    onViewCase: (id: string) => void;
    onNavigate: (tab: string) => void;
    refreshTrigger?: number;
}

export function Dashboard({ onViewCase, onNavigate, refreshTrigger }: DashboardProps) {
    const [stats, setStats] = useState<any>({
        active_cases: 0,
        completed_cases: 0,
        pending_requests: 0,
        blocked_items: 0,
        time_saved_hours: 0,
        system_health: { automation_rate: 0 }
    });
    const [trend, setTrend] = useState<any[]>([]);
    const [distribution, setDistribution] = useState<any[]>([]);
    const [priorityCases, setPriorityCases] = useState<any[]>([]);
    const [recentActivity, setRecentActivity] = useState<any[]>([]);

    const fetchData = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/dashboard/overview`);
            const data = await res.json();

            setStats(data.stats);
            setTrend(data.trend);
            setDistribution(data.distribution);
            setPriorityCases(data.priority);
            setRecentActivity(data.activity);
        } catch (e) {
            console.error("Dashboard fetch error:", e);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 60000); // 60 seconds
        return () => clearInterval(interval);
    }, [refreshTrigger]);

    const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'];

    const getActionIcon = (action: string) => {
        switch (action) {
            case 'CASE_CREATED': return <Plus className="w-3.5 h-3.5 text-white" />;
            case 'EMAIL_SENT': return <Send className="w-3.5 h-3.5 text-blue-400" />;
            case 'EMAIL_RECEIVED': return <Mail className="w-3.5 h-3.5 text-purple-400" />;
            case 'DOCUMENT_RECEIVED': return <FileCheck className="w-3.5 h-3.5 text-emerald-400" />;
            case 'TASK_CREATED': return <CheckSquare className="w-3.5 h-3.5 text-white" />;
            case 'REQUEST_FULFILLED': return <Trophy className="w-3.5 h-3.5 text-emerald-400" />;
            case 'CHASE_SENT': return <Zap className="w-3.5 h-3.5 text-amber-400" />;
            case 'MANUAL_CHASE': return <Zap className="w-3.5 h-3.5 text-amber-400" />;
            default: return <Activity className="w-3.5 h-3.5 text-white" />;
        }
    };

    return (
        <div className="space-y-8 animate-fade-in relative">
            {/* Ambient Background Glows */}
            <div className="absolute -top-24 -left-24 w-96 h-96 bg-blue-600/10 blur-[100px] pointer-events-none rounded-full animate-glow-pulse" />
            <div className="absolute top-1/2 -right-24 w-96 h-96 bg-purple-600/10 blur-[100px] pointer-events-none rounded-full animate-glow-pulse" style={{ animationDelay: '-1.5s' }} />

            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 relative z-10">
                <div>
                    <h2 className="text-4xl font-extrabold text-white tracking-tight mb-2">
                        System <span className="text-gradient-blue italic">Intelligence</span>
                    </h2>
                    <p className="text-gray-400 text-base max-w-lg">Autonomous case management and strategic operational analytics.</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={fetchData}
                        className="glass px-4 py-2 rounded-xl text-sm font-medium text-gray-300 hover:text-white hover:bg-white/10 transition-all border border-white/5 active:scale-95"
                    >
                        Force Refresh
                    </button>
                    <div className="flex items-center gap-3 text-sm font-medium text-emerald-400 bg-emerald-500/10 px-4 py-2 rounded-xl border border-emerald-500/20 backdrop-blur-md">
                        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                        Live Intelligence
                    </div>
                </div>
            </div>

            {/* Stats Cards Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
                <StatCard
                    icon={<Users className="w-6 h-6 text-blue-400" />}
                    label="Active Folders"
                    value={stats.active_cases}
                    subtext="Total currently in progress"
                    variant="blue"
                    onClick={() => onNavigate('cases')}
                />
                <StatCard
                    icon={<FileText className="w-6 h-6 text-amber-400" />}
                    label="Active Exceptions"
                    value={stats.blocked_items}
                    subtext="Action required items"
                    variant="amber"
                    onClick={() => onNavigate('exceptions')}
                />
                <StatCard
                    icon={<Zap className="w-6 h-6 text-purple-400" />}
                    label="Automation Rate"
                    value={`${stats.system_health?.automation_rate}%`}
                    subtext="AI efficiency benchmark"
                    variant="white"
                    onClick={() => onNavigate('dashboard')}
                />
                <StatCard
                    icon={<Trophy className="w-6 h-6 text-emerald-400" />}
                    label="Time Reclaimed"
                    value={`${stats.time_saved_hours}h`}
                    subtext="Total manual hours saved"
                    variant="emerald"
                    onClick={() => onNavigate('dashboard')}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative z-10">
                {/* Historical Trend Chart */}
                <div className="lg:col-span-2 glass border border-white/5 rounded-3xl p-8 h-[450px] flex flex-col hover:border-white/10 transition-all shadow-2xl overflow-hidden group">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 blur-3xl rounded-full -mr-32 -mt-32 group-hover:bg-white/10 transition-all" />
                    <div className="flex justify-between items-center mb-8 relative z-10">
                        <div className="flex items-center gap-3">
                            <div className="p-3 bg-white/5 rounded-2xl border border-white/10">
                                <TrendingUp className="w-5 h-5 text-blue-400" />
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-white">Acquisition Velocity</h3>
                                <p className="text-sm text-gray-500">Case volume vs agent reachouts</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 bg-white/5 rounded-full px-4 py-1.5 border border-white/10">
                            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                            <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Weekly Performance</span>
                        </div>
                    </div>
                    <div className="flex-1 min-h-0 relative z-10">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trend}>
                                <defs>
                                    <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorReachouts" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    stroke="#4b5563"
                                    fontSize={12}
                                    tickLine={false}
                                    axisLine={false}
                                    dy={10}
                                    tickFormatter={(val) => val.split('-').slice(1).join('/')}
                                />
                                <YAxis
                                    stroke="#4b5563"
                                    fontSize={12}
                                    tickLine={false}
                                    axisLine={false}
                                    dx={-10}
                                    allowDecimals={false}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: '16px',
                                        backdropFilter: 'blur(12px)',
                                        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)'
                                    }}
                                    itemStyle={{ color: '#fff', fontSize: '12px' }}
                                    labelStyle={{ color: '#94a3b8', marginBottom: '8px' }}
                                />
                                <Area
                                    name="New Cases"
                                    type="monotone"
                                    dataKey="cases"
                                    stroke="#3b82f6"
                                    strokeWidth={4}
                                    fillOpacity={1}
                                    fill="url(#colorCases)"
                                />
                                <Area
                                    name="Agent Reachouts"
                                    type="monotone"
                                    dataKey="reachouts"
                                    stroke="#8b5cf6"
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    fillOpacity={1}
                                    fill="url(#colorReachouts)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Status Distribution */}
                <div className="glass border border-white/5 rounded-3xl p-8 h-[450px] flex flex-col hover:border-white/10 transition-all shadow-2xl relative overflow-hidden">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-3 bg-white/5 rounded-2xl border border-white/10">
                            <PieChartIcon className="w-5 h-5 text-purple-400" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-white">Status Engine</h3>
                            <p className="text-sm text-gray-500">Inventory distribution</p>
                        </div>
                    </div>
                    <div className="flex-1 flex flex-col items-center justify-center relative">
                        <div className="w-full h-56 relative">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={distribution}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={70}
                                        outerRadius={95}
                                        paddingAngle={8}
                                        dataKey="value"
                                        stroke="none"
                                    >
                                        {distribution.map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                                            border: '1px solid rgba(255,255,255,0.1)',
                                            borderRadius: '12px',
                                            backdropFilter: 'blur(12px)'
                                        }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                                <span className="text-3xl font-black text-white">{stats.active_cases + stats.completed_cases}</span>
                                <span className="text-[10px] uppercase font-bold text-gray-500 tracking-widest">Total Assets</span>
                            </div>
                        </div>
                        <div className="mt-8 grid grid-cols-2 gap-x-8 gap-y-3 w-full">
                            {distribution.map((item, i) => (
                                <div key={item.name} className="flex items-center justify-between group cursor-default">
                                    <div className="flex items-center gap-2.5">
                                        <div className="w-2.5 h-2.5 rounded-full shadow-[0_0_8px_currentColor]" style={{ color: COLORS[i], backgroundColor: COLORS[i] }} />
                                        <span className="text-xs font-semibold text-gray-400 group-hover:text-white transition-colors uppercase tracking-wider">{item.name}</span>
                                    </div>
                                    <span className="text-sm font-bold text-white">{item.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative z-10">
                {/* Priority Focus */}
                <div className="glass border border-white/5 rounded-3xl p-8 hover:border-white/10 transition-all shadow-2xl">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-white flex items-center gap-3">
                            <AlertTriangle className="w-5 h-5 text-amber-400 animate-pulse" />
                            Strategic Oversight
                        </h3>
                        <span className="text-xs font-bold text-rose-400 bg-rose-400/10 px-3 py-1 rounded-full border border-rose-400/20 uppercase tracking-tighter">High Impact</span>
                    </div>
                    <div className="space-y-4">
                        {priorityCases.length > 0 ? (
                            priorityCases.map((c: any) => (
                                <div key={c.id}
                                    onClick={() => onViewCase(c.id)}
                                    className="flex items-center justify-between p-4 rounded-2xl bg-white/5 hover:bg-white/10 transition-all border border-white/5 group cursor-pointer active:scale-[0.98]"
                                >
                                    <div className="flex items-center gap-5">
                                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center text-white font-bold text-xl border border-white/10 group-hover:border-white/30 transition-all shadow-inner">
                                            {c.client_name?.charAt(0)}
                                        </div>
                                        <div>
                                            <div className="font-bold text-white text-base group-hover:text-blue-400 transition-colors">
                                                {c.client_name}
                                            </div>
                                            <div className="text-sm text-gray-500 truncate max-w-[200px]">{c.title}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="hidden sm:flex flex-col items-end">
                                            <span className="text-[10px] font-black text-gray-600 uppercase tracking-widest leading-none mb-1">Status</span>
                                            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider leading-none">Healthy</span>
                                        </div>
                                        <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-blue-500/20 transition-all">
                                            <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-white transition-all transform group-hover:translate-x-0.5" />
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="flex flex-col items-center justify-center py-12 text-gray-600 bg-white/5 rounded-2xl border border-dashed border-white/10">
                                <FileText className="w-8 h-8 mb-3 opacity-20" />
                                <p className="italic text-sm">Clear operational horizon. No priority items.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Automation Log */}
                <div className="glass border border-white/5 rounded-3xl p-8 hover:border-white/10 transition-all shadow-2xl flex flex-col">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-white flex items-center gap-3">
                            <Activity className="w-5 h-5 text-emerald-400" />
                            Intelligence Stream
                        </h3>
                        <div className="flex items-center gap-2">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Real-time</span>
                        </div>
                    </div>
                    <div className="space-y-6 max-h-[280px] overflow-y-auto pr-4 scrollbar-thin flex-1">
                        {recentActivity.length > 0 && recentActivity.map((item, idx) => (
                            <div key={idx} className="flex gap-4 items-start relative group">
                                <div className="absolute left-[19px] top-10 bottom-0 w-0.5 bg-white/5 last:hidden group-hover:bg-blue-500/20 transition-colors" />
                                <div className="p-2.5 bg-white/5 rounded-xl border border-white/10 group-hover:border-blue-500/30 transition-all z-10 bg-surface shadow-xl">
                                    {getActionIcon(item.action)}
                                </div>
                                <div className="flex-1 min-w-0 pt-1">
                                    <div className="flex justify-between items-start mb-1">
                                        <p className="text-xs font-black text-white uppercase tracking-[0.15em]">{item.action?.replace(/_/g, ' ')}</p>
                                        <span className="text-[10px] font-bold text-gray-600 bg-white/5 px-2 py-0.5 rounded-full">{new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                    <p className="text-sm text-gray-400 leading-relaxed font-medium group-hover:text-gray-300 transition-colors">{item.reason || item.details}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ icon, label, value, subtext, variant, onClick }: any) {
    const glowClass = {
        blue: "glass-glow-blue",
        amber: "glass-glow-amber",
        emerald: "glass-glow-emerald",
        white: "glass-glow-white"
    }[variant as string] || "glass-glow-white";

    return (
        <button
            onClick={onClick}
            className={clsx(
                "rounded-3xl p-7 text-left transition-all hover:-translate-y-2 cursor-pointer group active:scale-95 animate-slide-up h-full flex flex-col relative overflow-hidden",
                glowClass
            )}
        >
            <div className="absolute top-0 right-0 w-24 h-24 bg-white/5 blur-2xl rounded-full -mr-12 -mt-12 group-hover:bg-white/10 transition-all" />
            <div className="flex items-center justify-between mb-6">
                <div className="p-3 bg-white/10 rounded-2xl border border-white/10 backdrop-blur-md shadow-inner group-hover:scale-110 transition-transform">
                    {icon}
                </div>
                <div className="w-8 h-8 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all bg-white/10 translate-x-4 group-hover:translate-x-0">
                    <ArrowUpRight className="w-4 h-4 text-white" />
                </div>
            </div>
            <div className="mt-auto">
                <div className="text-4xl font-black text-white tracking-tighter mb-1 tabular-nums animate-fade-in">{value}</div>
                <div className="text-sm font-bold text-gray-300 uppercase tracking-widest leading-none mb-2">{label}</div>
                <div className="text-[11px] font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                    {subtext}
                </div>
            </div>
        </button>
    );
}
