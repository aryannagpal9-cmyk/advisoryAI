import React, { useState, useEffect } from 'react';
import { ExceptionFeed } from './components/ExceptionFeed';
import { Dashboard } from './components/Dashboard';
import { CaseList } from './components/CaseList';
import { CaseDetail } from './components/CaseDetail';
import { Settings } from './components/Settings';
import { NewCase } from './components/NewCase';
import ChatInterface from './components/ChatInterface';
import InsightsFeed from './components/InsightsFeed';
import { DataManagement } from './components/DataManagement';
import ActionItems from './components/ActionItems';
import { EmailList } from './components/EmailList';
import { MeetingList } from './components/MeetingList';
import {
  LayoutDashboard,
  ShieldAlert,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Bot,
  Briefcase,
  Calendar,
  Sparkles,
  CheckSquare,
  MessageSquare,
  Database,
  RotateCcw,
  Mail,
  Video,
  Activity,
  Plus,
  Loader2,
} from 'lucide-react';
import { Toast } from './components/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';


type Tab = 'dashboard' | 'exceptions' | 'cases' | 'settings' | 'insights' | 'actions' | 'data' | 'emails' | 'meetings';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [showNewCaseModal, setShowNewCaseModal] = useState(false);
  const [notification, setNotification] = useState<{ message: string, subtext: string } | null>(null);
  const [activeChases, setActiveChases] = useState(0);
  const [exceptionCount, setExceptionCount] = useState(0);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(Date.now());
  const [simulatedDate, setSimulatedDate] = useState<string | null>(null);

  React.useEffect(() => {
    // Fetch initial simulated date
    fetch('http://localhost:8000/api/dashboard/overview')
      .then(res => res.json())
      .then(data => {
        if (data.simulated_date) setSimulatedDate(data.simulated_date);
      });

    // WebSocket Connection with error handling
    let ws: WebSocket | null = null;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws');

        ws.onopen = () => {
          console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data);
            if (payload.type === 'NEW_EMAIL') {
              setNotification({
                message: "New Email Received",
                subtext: `From: ${payload.data.from}`
              });
            } else if (payload.type === 'ACTION_TAKEN') {
              // Refresh dashboard stats when agent takes an action
              fetchStats();

              // Show notification about the action
              const actionMessages: { [key: string]: string } = {
                'TASK_CREATED': `Task created: ${payload.data?.title || 'New task'}`,
                'MEETING_SCHEDULED': `Meeting scheduled: ${payload.data?.title || 'New meeting'}`,
                'CASE_CREATED': `Case created: ${payload.data?.title || 'New case'}`,
                'EMAIL_DRAFTED': `Email drafted: ${payload.data?.subject || 'New email'}`
              };

              const message = actionMessages[payload.action] || 'Action completed';
              setNotification({
                message: "AI Agent Action",
                subtext: message
              });
            }
          } catch (e) {
            console.error("WS Parse Error", e);
          }
        };

        ws.onerror = (error) => {
          console.log('WebSocket error (this is normal if backend is restarting):', error);
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
        };
      } catch (e) {
        console.error('Failed to create WebSocket:', e);
      }
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = () => {
    fetch('http://localhost:8000/api/dashboard/stats')
      .then(res => res.json())
      .then(data => {
        setActiveChases(data.pending_requests);
        setExceptionCount(data.blocked_items);
      })
      .catch(console.error);
  };

  const handleSimulateDay = async () => {
    setIsSimulating(true);
    try {
      const res = await fetch('http://localhost:8000/api/simulate/advance-day', {
        method: 'POST'
      });
      const data = await res.json();

      let summary = `${data.actions_taken} actions processed`;
      if (data.details && data.details.length > 0) {
        // Group by action type
        const counts: any = {};
        data.details.forEach((d: any) => {
          counts[d.action] = (counts[d.action] || 0) + 1;
        });

        // Create readable summary parts
        const parts = [];
        if (counts['EMAIL_SENT']) parts.push(`${counts['EMAIL_SENT']} Email${counts['EMAIL_SENT'] > 1 ? 's' : ''} Sent`);
        if (counts['TASK_CREATED']) parts.push(`${counts['TASK_CREATED']} Task${counts['TASK_CREATED'] > 1 ? 's' : ''} Created`);
        if (counts['DOCUMENT_RECEIVED']) parts.push(`${counts['DOCUMENT_RECEIVED']} Doc${counts['DOCUMENT_RECEIVED'] > 1 ? 's' : ''} Recv`);
        if (counts['EMAIL_RECEIVED']) parts.push(`${counts['EMAIL_RECEIVED']} Email${counts['EMAIL_RECEIVED'] > 1 ? 's' : ''} Recv`);
        if (counts['CASE_CREATED']) parts.push(`${counts['CASE_CREATED']} Case${counts['CASE_CREATED'] > 1 ? 's' : ''} Created`);
        if (counts['CHASE_SENT']) parts.push(`${counts['CHASE_SENT']} Chase${counts['CHASE_SENT'] > 1 ? 's' : ''} Sent`);
        if (counts['MEETING_SCHEDULED']) parts.push(`${counts['MEETING_SCHEDULED']} Meeting${counts['MEETING_SCHEDULED'] > 1 ? 's' : ''} Set`);
        if (counts['MEETING_COMPLETED']) parts.push(`${counts['MEETING_COMPLETED']} Meeting${counts['MEETING_COMPLETED'] > 1 ? 's' : ''} Finished`);
        if (counts['TIME_ADVANCED']) parts.push(`Date Advanced`);

        if (parts.length > 0) {
          summary = parts.join(' | ');
        }
      }

      setNotification({
        message: `Day Simulated Successfully`,
        subtext: summary
      });

      fetchStats();
      setLastUpdated(Date.now());
      if (data.simulated_date) {
        setSimulatedDate(data.simulated_date);
      }
    } catch (e) {
      console.error('Simulation failed:', e);
      setNotification({
        message: 'Simulation Failed',
        subtext: 'Please try again'
      });
    } finally {
      setIsSimulating(false);
    }
  };

  const handleResetSimulation = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/simulate/reset', {
        method: 'POST'
      });
      const data = await res.json();

      setSimulatedDate(data.simulated_date);
      setNotification({
        message: 'Simulation Reset',
        subtext: 'Returned to real-world current date'
      });

      fetchStats();
      setLastUpdated(Date.now());
    } catch (e) {
      console.error('Reset failed:', e);
    }
  };

  const handleCreateCase = async (data: any) => {
    try {
      const res = await fetch('http://localhost:8000/api/cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (res.ok) {
        await res.json();
        setShowNewCaseModal(false);
        setActiveTab('cases');
        setNotification({
          message: 'Case Created Successfully',
          subtext: `${data.title} for ${data.client_name}`
        });
        fetchStats();
      } else {
        setNotification({
          message: 'Failed to Create Case',
          subtext: 'Please try again'
        });
      }
    } catch (e) {
      console.error("Failed to create case", e);
      setNotification({
        message: 'Error Creating Case',
        subtext: 'Check your connection'
      });
    }
  };

  const handleSelectCase = (id: string) => {
    setSelectedCaseId(id);
    setActiveTab('cases');
  };

  const handleBackToCases = () => {
    setSelectedCaseId(null);
  }

  return (
    <div className="min-h-screen bg-background text-white flex">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 glass border-r border-white/5 flex flex-col items-center lg:items-stretch py-6 fixed h-full z-30 transition-all duration-500 group/sidebar overflow-hidden">
        <div className="absolute top-0 right-0 w-px h-full bg-gradient-to-b from-transparent via-primary-500/20 to-transparent" />

        <div className="px-6 mb-8 flex items-center gap-3 relative z-10">
          <div className="w-9 h-9 bg-primary-600 rounded-lg flex items-center justify-center shrink-0 shadow-glow transition-transform duration-500 group-hover/sidebar:scale-110">
            <Bot className="text-white w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-bold hidden lg:block tracking-tight text-white/90">AdvisoryAI</h1>
            {simulatedDate && (
              <div className="flex items-center gap-2 mt-0.5">
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-white/5 border border-white/10 rounded-md hidden lg:flex">
                  <span className="text-[10px] font-bold text-muted uppercase tracking-wider">
                    {new Date(simulatedDate).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                  </span>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); handleResetSimulation(); }}
                  className="p-1 hover:bg-white/10 rounded-md transition-colors hidden lg:block text-muted hover:text-white"
                >
                  <RotateCcw className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>
        </div>

        <nav className="space-y-1 px-3 flex-1 relative z-10">
          <NavItem
            icon={<LayoutDashboard />}
            label="Dashboard"
            active={activeTab === 'dashboard'}
            onClick={() => { setActiveTab('dashboard'); setSelectedCaseId(null); }}
          />
          <NavItem
            icon={<Sparkles />}
            label="AI Insights"
            active={activeTab === 'insights'}
            onClick={() => { setActiveTab('insights'); setSelectedCaseId(null); }}
          />
          <NavItem
            icon={<CheckSquare />}
            label="Actions"
            active={activeTab === 'actions'}
            onClick={() => { setActiveTab('actions'); setSelectedCaseId(null); }}
          />
          <NavItem
            icon={<ShieldAlert />}
            label="Exceptions"
            active={activeTab === 'exceptions'}
            count={exceptionCount}
            onClick={() => { setActiveTab('exceptions'); setSelectedCaseId(null); }}
          />
          <NavItem
            icon={<Briefcase />}
            label="Cases"
            active={activeTab === 'cases'}
            onClick={() => { setActiveTab('cases'); setSelectedCaseId(null); }}
          />
          <NavItem
            icon={<Mail />}
            label="Emails"
            active={activeTab === 'emails'}
            onClick={() => { setActiveTab('emails'); setSelectedCaseId(null); }}
          />
          <NavItem
            icon={<Video />}
            label="Meetings"
            active={activeTab === 'meetings'}
            onClick={() => { setActiveTab('meetings'); setSelectedCaseId(null); }}
          />

          <div className="py-2 px-4 opacity-50">
            <div className="h-px bg-white/10" />
          </div>

          <NavItem
            icon={<SettingsIcon />}
            label="Settings"
            active={activeTab === 'settings'}
            onClick={() => { setActiveTab('settings'); setSelectedCaseId(null); }}
          />
          <NavItem
            icon={<Database />}
            label="Data"
            active={activeTab === 'data'}
            onClick={() => { setActiveTab('data'); setSelectedCaseId(null); }}
          />
        </nav>

        {/* Chat toggle in sidebar */}
        <div className="px-3 mt-auto relative z-10 pb-6">
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className={`w-full flex items-center gap-3 p-3.5 rounded-xl transition-all duration-300 group relative overflow-hidden
                       ${isChatOpen ? 'bg-primary-500/10 text-primary-400' : 'text-muted hover:text-white glass border-white/5 hover:border-white/10'}`}
          >
            <MessageSquare size={20} className={`relative z-10 ${isChatOpen ? 'text-primary-400' : 'text-muted group-hover:text-white transition-colors'}`} />
            <span className="hidden lg:block relative z-10 font-bold text-xs uppercase tracking-wider">AI Chat</span>
            <div className="ml-auto relative z-10">
              <span className="flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-primary-500"></span>
              </span>
            </div>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-20 lg:ml-64 p-10 relative overflow-hidden min-h-screen animate-fade-in">
        {/* Background Effects */}
        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary-500/5 blur-[150px] pointer-events-none rounded-full" />
        <div className="absolute top-[20%] left-0 w-[400px] h-[400px] bg-purple-500/5 blur-[120px] pointer-events-none rounded-full" />

        <header className="flex justify-between items-center mb-12 relative z-20">
          <div className="flex items-center gap-6">
            <div className="h-12 w-1 bg-gradient-to-b from-primary-600 via-primary-400 to-transparent rounded-full" />
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight text-white mb-1">
                Protocol: <span className="text-gradient-blue">Aryan</span>
              </h1>
              <p className="text-muted font-mono text-xs uppercase tracking-widest flex items-center gap-2">
                <Activity className="w-3 h-3 text-primary-400" />
                System standard operation | {activeChases} active threads
              </p>
            </div>
          </div>
          <div className="flex gap-4">
            <button
              onClick={handleSimulateDay}
              disabled={isSimulating}
              className="glass-glow-white px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest hover:border-white/20 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 shadow-glow-sm active:scale-95"
            >
              {isSimulating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-primary-400" />
                  Processing...
                </>
              ) : (
                <>
                  <RotateCcw className="w-4 h-4 text-primary-400" />
                  Advance Cycle
                </>
              )}
            </button>
            <button
              onClick={() => setShowNewCaseModal(true)}
              className="bg-primary-600 text-white px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all duration-300 shadow-glow hover:bg-primary-500 flex items-center gap-3 active:scale-95"
            >
              <Plus className="w-5 h-5" /> New Protocol
            </button>
          </div>
        </header>

        <div className="relative z-10 space-y-6">
          {/* Dynamic Content based on Active Tab */}
          <div className="space-y-6">
            {activeTab === 'dashboard' && (
              <ErrorBoundary componentName="Dashboard">
                <Dashboard
                  refreshTrigger={lastUpdated}
                  onViewCase={handleSelectCase}
                  onNavigate={(tab: any) => { setActiveTab(tab as Tab); setSelectedCaseId(null); }}
                />
              </ErrorBoundary>
            )}

            {activeTab === 'insights' && (
              <ErrorBoundary componentName="AI Insights">
                <InsightsFeed refreshTrigger={lastUpdated} />
              </ErrorBoundary>
            )}
            {activeTab === 'actions' && (
              <ErrorBoundary componentName="Actions">
                <ActionItems refreshTrigger={lastUpdated} />
              </ErrorBoundary>
            )}
            {activeTab === 'exceptions' && (
              <ErrorBoundary componentName="Exceptions">
                <ExceptionFeed refreshTrigger={lastUpdated} onViewCase={handleSelectCase} />
              </ErrorBoundary>
            )}
            {activeTab === 'settings' && (
              <ErrorBoundary componentName="Settings">
                <Settings />
              </ErrorBoundary>
            )}
            {activeTab === 'data' && (
              <ErrorBoundary componentName="Data Management">
                <DataManagement />
              </ErrorBoundary>
            )}
            {activeTab === 'emails' && (
              <ErrorBoundary componentName="Emails">
                <EmailList refreshTrigger={lastUpdated} />
              </ErrorBoundary>
            )}
            {activeTab === 'meetings' && (
              <ErrorBoundary componentName="Meetings">
                <MeetingList refreshTrigger={lastUpdated} />
              </ErrorBoundary>
            )}

            {activeTab === 'cases' && !selectedCaseId && (
              <ErrorBoundary componentName="Case List">
                <CaseList refreshTrigger={lastUpdated} onSelectCase={handleSelectCase} />
              </ErrorBoundary>
            )}

            {activeTab === 'cases' && selectedCaseId && (
              <ErrorBoundary componentName="Case Detail">
                <CaseDetail caseId={selectedCaseId} onBack={handleBackToCases} />
              </ErrorBoundary>
            )}
          </div>
        </div>

        {showNewCaseModal && (
          <NewCase onClose={() => setShowNewCaseModal(false)} onSubmit={handleCreateCase} />
        )}

        {notification && (
          <Toast
            message={notification.message}
            subtext={notification.subtext}
            onClose={() => setNotification(null)}
            onAction={() => {
              setActiveTab('dashboard');
              setNotification(null);
            }}
          />
        )}
      </main>

      {/* Chat Interface */}
      <ChatInterface isOpen={isChatOpen} onToggle={() => setIsChatOpen(!isChatOpen)} />
    </div>
  );
}

function NavItem({ icon, label, active, count, onClick }: { icon: any, label: string, active?: boolean, count?: number, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-300 group relative overflow-hidden
                 ${active
          ? 'bg-primary-500/10 text-white font-bold'
          : 'text-muted hover:text-white glass border-transparent hover:border-white/5 hover:bg-white/[0.02]'}`}
    >
      <div className={`relative z-10 transition-all duration-300 ${active ? 'scale-105' : 'group-hover:scale-105'}`}>
        {React.cloneElement(icon, {
          size: 18,
          className: active ? 'text-primary-400' : 'text-muted group-hover:text-white transition-colors'
        })}
      </div>
      <span className={`hidden lg:block relative z-10 text-xs font-medium tracking-wide transition-all duration-300 ${active ? 'translate-x-0.5' : 'group-hover:translate-x-0.5'}`}>
        {label}
      </span>
      {count && (
        <span className="ml-auto relative z-10 bg-rose-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-md hidden lg:block">
          {count}
        </span>
      )}
      {active && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary-500 rounded-r-full shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
      )}
    </button>
  );
}

export default App;
