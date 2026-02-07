import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
    componentName?: string;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error(`Uncaught error in ${this.props.componentName || 'component'}:`, error, errorInfo);
    }

    private handleReset = () => {
        this.setState({ hasError: false, error: null });
        window.location.reload();
    };

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="flex flex-col items-center justify-center p-12 glass rounded-[32px] border border-rose-500/20 text-center animate-reveal">
                    <div className="w-16 h-16 bg-rose-500/10 rounded-2xl flex items-center justify-center mb-6 shadow-glow-sm border border-rose-500/20">
                        <AlertTriangle className="text-rose-500" size={32} />
                    </div>
                    <h2 className="text-2xl font-black text-white mb-2 uppercase tracking-tight">Component Error</h2>
                    <p className="text-muted font-bold text-xs uppercase tracking-widest mb-8 max-w-md">
                        The {this.props.componentName || 'requested module'} encountered a critical failure.
                        Detailed technical logs have been generated.
                    </p>
                    <button
                        onClick={this.handleReset}
                        className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white px-6 py-3 rounded-xl border border-white/10 transition-all font-bold text-xs uppercase tracking-widest active:scale-95"
                    >
                        <RefreshCw size={14} className="text-primary-400" />
                        Reinitialize Module
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}
