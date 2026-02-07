import { Mail, Shield, UserCog, Sliders } from 'lucide-react';

export function Settings() {
    return (
        <div className="space-y-6">
            <h2 className="text-xl font-semibold text-white mb-6">System Settings</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <SettingSection title="Email Configuration" icon={<Mail className="w-5 h-5" />}>
                    <div className="space-y-4">
                        <Toggle label="Auto-Send Reminders" checked />
                        <Toggle label="Include 'No Action Needed' updates" checked />
                        <div className="space-y-2">
                            <label className="text-sm text-gray-400">Reply-To Address</label>
                            <input type="text" value="chase@advisoryai.demo" disabled className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-400" />
                        </div>
                    </div>
                </SettingSection>

                <SettingSection title="Policy Rules" icon={<Shield className="w-5 h-5" />}>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-300">Max Retries before Escalation</span>
                            <span className="font-mono text-white">3</span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-300">Standard Chase Interval</span>
                            <span className="font-mono text-white">7 days</span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-300">Urgent Chase Interval</span>
                            <span className="font-mono text-white">3 days</span>
                        </div>
                    </div>
                </SettingSection>

                <SettingSection title="Provider Profiles" icon={<UserCog className="w-5 h-5" />}>
                    <div className="space-y-3">
                        <ProviderProfile name="Aviva" speed="Slow" days={15} />
                        <ProviderProfile name="Scottish Widows" speed="Standard" days={10} />
                        <ProviderProfile name="Legal & General" speed="Fast" days={5} />
                    </div>
                </SettingSection>

                <SettingSection title="System" icon={<Sliders className="w-5 h-5" />}>
                    <div className="space-y-4">
                        <Toggle label="Strict Deterministic Mode" checked disabled />
                        <button className="text-sm text-rose-400 hover:text-rose-300 transition-colors">
                            Reset All Mock Data
                        </button>
                    </div>
                </SettingSection>
            </div>
        </div>
    );
}

function SettingSection({ title, icon, children }: any) {
    return (
        <div className="glass-card p-6">
            <div className="flex items-center gap-2 mb-4 text-white/90">
                {icon}
                <h3 className="font-medium">{title}</h3>
            </div>
            {children}
        </div>
    );
}

function Toggle({ label, checked, disabled }: any) {
    return (
        <div className={`flex items-center justify-between ${disabled ? 'opacity-50' : ''}`}>
            <span className="text-sm text-gray-300">{label}</span>
            <div className={`w-10 h-6 rounded-full relative transition-colors ${checked ? 'bg-emerald-600' : 'bg-white/10'}`}>
                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${checked ? 'left-5' : 'left-1'}`} />
            </div>
        </div>
    );
}

function ProviderProfile({ name, speed, days }: any) {
    const colors: any = { Slow: 'text-rose-400', Standard: 'text-amber-400', Fast: 'text-emerald-400' };
    return (
        <div className="flex items-center justify-between text-sm p-2 rounded-lg bg-white/5">
            <span className="text-gray-300">{name}</span>
            <div className="flex items-center gap-3">
                <span className={`text-xs ${colors[speed]}`}>{speed}</span>
                <span className="text-gray-500">{days}d</span>
            </div>
        </div>
    );
}
