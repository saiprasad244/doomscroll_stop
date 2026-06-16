import React, { useState, useEffect } from 'react';
import useTheme from './hooks/useTheme';
import useScrollTracker from './hooks/useScrollTracker';
import AuthPage from './components/Auth/AuthPage';
import Dashboard from './pages/Dashboard';
import FocusMode from './pages/FocusMode';
import HabitCoach from './pages/HabitCoach';
import Leaderboard from './pages/Leaderboard';
import InterventionModal from './components/InterventionModal';
import { 
  Shield, 
  LayoutDashboard, 
  Timer, 
  BrainCircuit, 
  Trophy, 
  LogOut, 
  Sun, 
  Moon, 
  Menu, 
  X,
  User
} from 'lucide-react';

export function App() {
  const [user, setUser] = useState(null);
  const { theme, toggleTheme } = useTheme();
  const tracker = useScrollTracker();
  
  // Tab navigation: 'Dashboard', 'FocusMode', 'HabitCoach', 'Leaderboard'
  const [activeTab, setActiveTab] = useState('Dashboard');
  
  // Responsive sidebar drawer (mobile view)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Intervention warning popup state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalData, setModalData] = useState({ duration: 0, scrolls: 0, risk: 0 });

  // Load auth state from localStorage on launch
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    tracker.resetTracker();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    tracker.resetTracker();
    setActiveTab('Dashboard');
  };

  const triggerIntervention = (duration, scrolls, risk) => {
    setModalData({ duration, scrolls, risk });
    setModalOpen(true);
  };

  const handleStartFocusFromModal = () => {
    setModalOpen(false);
    setActiveTab('FocusMode');
  };

  // If user is not authenticated, show Auth Page
  if (!user) {
    return <AuthPage onAuthSuccess={handleAuthSuccess} />;
  }

  // Define sidebar items
  const menuItems = [
    { name: 'Dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { name: 'FocusMode', icon: Timer, label: 'Focus Mode' },
    { name: 'HabitCoach', icon: BrainCircuit, label: 'AI Habit Coach' },
    { name: 'Leaderboard', icon: Trophy, label: 'Streaks & Badges' },
  ];

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-300">
      
      {/* 1. MOBILE HEADER BAR */}
      <header className="md:hidden flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-900 bg-white/70 dark:bg-slate-950/70 backdrop-blur-md sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center text-white">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-extrabold text-sm tracking-wide">DoomScroll Shield</span>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-500 dark:text-slate-400"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          <button 
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-900"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* 2. PERSISTENT SIDEBAR DESKTOP & DRAWER MOBILE */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 p-5 flex flex-col justify-between
        bg-white/80 dark:bg-slate-950/80 backdrop-blur-lg border-r border-slate-200 dark:border-slate-900
        transform transition-transform duration-300 md:relative md:translate-x-0
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="space-y-6">
          {/* Logo & Close Drawer Button */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-tr from-brand-600 to-accent-500 rounded-xl flex items-center justify-center text-white shadow-md shadow-brand-500/10">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <span className="font-black text-sm tracking-wide block">DoomScroll Shield</span>
                <span className="text-[10px] text-brand-500 dark:text-brand-400 font-bold tracking-wider uppercase block">Core Protected</span>
              </div>
            </div>
            <button 
              onClick={() => setMobileMenuOpen(false)}
              className="md:hidden p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-900"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1 pt-4">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isSelected = activeTab === item.name;
              return (
                <button
                  key={item.name}
                  onClick={() => {
                    setActiveTab(item.name);
                    setMobileMenuOpen(false);
                  }}
                  className={`
                    w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200
                    ${isSelected 
                      ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/15' 
                      : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100/60 dark:hover:bg-slate-900/60'}
                  `}
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* User Card & Action Area */}
        <div className="space-y-4 pt-4 border-t border-slate-200/60 dark:border-slate-900">
          {/* User Profile */}
          <div className="flex items-center gap-3 px-2">
            <div className="w-9 h-9 rounded-full bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center">
              <User className="w-4 h-4 text-brand-500" />
            </div>
            <div className="overflow-hidden">
              <span className="block font-bold text-xs truncate">{user.name}</span>
              <span className="block text-[10px] text-slate-400 truncate">{user.email}</span>
            </div>
          </div>

          {/* Theme & Logout Button Controls */}
          <div className="flex gap-2">
            <button
              onClick={toggleTheme}
              className="flex-1 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200/50 dark:border-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-800 flex items-center justify-center text-slate-500 dark:text-slate-400"
              title="Toggle Light/Dark Theme"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>
            
            <button
              onClick={handleLogout}
              className="flex-1 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200/50 dark:border-slate-800/80 hover:bg-red-500/10 hover:text-red-500 flex items-center justify-center text-slate-500 dark:text-slate-400 transition-colors"
              title="Log Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* 3. MAIN WORKSPACE CONTENT */}
      <main className="flex-1 p-6 md:p-10 overflow-y-auto max-w-7xl mx-auto w-full">
        {activeTab === 'Dashboard' && (
          <Dashboard tracker={tracker} onTriggerIntervention={triggerIntervention} />
        )}
        {activeTab === 'FocusMode' && (
          <FocusMode />
        )}
        {activeTab === 'HabitCoach' && (
          <HabitCoach />
        )}
        {activeTab === 'Leaderboard' && (
          <Leaderboard />
        )}
      </main>

      {/* 4. OVERLAY SMART INTERVENTION POPUP */}
      <InterventionModal
        isOpen={modalOpen}
        sessionDuration={modalData.duration}
        scrollCount={modalData.scrolls}
        riskScore={modalData.risk}
        onClose={() => setModalOpen(false)}
        onStartFocusMode={handleStartFocusFromModal}
      />
    </div>
  );
}
export default App;
