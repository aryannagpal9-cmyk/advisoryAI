import { X, Mail } from 'lucide-react';
import { useEffect } from 'react';

interface ToastProps {
    message: string;
    subtext: string;
    onClose: () => void;
    onAction: () => void;
}

export function Toast({ message, subtext, onClose, onAction }: ToastProps) {
    useEffect(() => {
        const timer = setTimeout(onClose, 5000);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className="fixed top-24 right-8 z-50 animate-in fade-in slide-in-from-top-5 duration-300">
            <div className="bg-slate-900/80 backdrop-blur-xl border border-white/10 p-4 rounded-xl shadow-2xl w-80 relative overflow-hidden group">
                {/* Glow Effect */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-white/20 blur-lg rounded-full" />

                <button onClick={onClose} className="absolute top-2 right-2 text-white/40 hover:text-white transition-colors">
                    <X size={16} />
                </button>

                <div className="flex items-start gap-3 mb-3">
                    <div className="p-2 bg-white/10 rounded-lg text-white">
                        <Mail size={20} />
                    </div>
                    <div>
                        <h4 className="font-semibold text-white text-sm">{message}</h4>
                        <p className="text-xs text-white/60 mt-0.5">{subtext}</p>
                    </div>
                </div>

                <button
                    onClick={onAction}
                    className="w-full bg-white hover:bg-gray-200 text-black text-sm font-semibold py-2 rounded-lg transition-colors shadow-lg"
                >
                    Review
                </button>
            </div>
        </div>
    );
}
