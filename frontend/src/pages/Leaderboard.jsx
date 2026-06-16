import React, { useState, useEffect } from 'react';
import { 
  Trophy, 
  Flame, 
  Shield, 
  Clock, 
  Award, 
  Moon, 
  FileText, 
  Zap, 
  Download, 
  Lock 
} from 'lucide-react';

export function Leaderboard() {
  const [achievementsData, setAchievementsData] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  const fetchData = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      // Fetch user achievements & points
      const achResponse = await fetch('http://localhost:5000/api/achievements', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const achData = await achResponse.json();
      if (achResponse.ok) {
        setAchievementsData(achData);
      }

      // Fetch leaderboard
      const leadResponse = await fetch('http://localhost:5000/api/leaderboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const leadData = await leadResponse.json();
      if (leadResponse.ok) {
        setLeaderboard(leadData);
      }
    } catch (err) {
      console.error("Error fetching leaderboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDownloadReport = async () => {
    setDownloading(true);
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:5000/api/reports/weekly', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Weekly_Digital_Wellbeing_Report.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        alert("Failed to generate report. Make sure you have logged at least one session.");
      }
    } catch (err) {
      console.error("Report download failed:", err);
      alert("Error generating report.");
    } finally {
      setDownloading(false);
    }
  };

  // Map icon strings to Lucide React components
  const iconMap = {
    shield: Shield,
    clock: Clock,
    flame: Flame,
    award: Award,
    moon: Moon
  };

  if (loading || !achievementsData) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // Calculate XP Level percentage
  const totalXP = achievementsData.points;
  const level = achievementsData.level;
  const progressPercent = Math.min(100, Math.round(((200 - achievementsData.points_to_next_level) / 200) * 100));

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 dark:from-white dark:via-brand-200 dark:to-accent-200 bg-clip-text text-transparent">
          Streaks & Achievements
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
          Compete in healthy usage streaks and unlock specialized badges by maintaining focus.
        </p>
      </div>

      {/* Gamification progress tracker */}
      <div className="glass-card p-6 border-brand-500/10 grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        <div>
          <span className="block text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1 font-semibold">User Level</span>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-black text-brand-500">{level}</span>
            <span className="text-slate-400 dark:text-slate-500 text-sm font-semibold">({totalXP} XP Total)</span>
          </div>
        </div>
        
        {/* XP Progress Bar */}
        <div className="md:col-span-2 space-y-2">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-500 dark:text-slate-400">Level Progress</span>
            <span className="text-brand-400 font-mono">{progressPercent}% ({200 - achievementsData.points_to_next_level} / 200 XP)</span>
          </div>
          <div className="w-full h-3 bg-slate-200 dark:bg-slate-900 rounded-full overflow-hidden border border-slate-300/10">
            <div 
              style={{ width: `${progressPercent}%` }}
              className="h-full bg-gradient-to-r from-brand-600 to-accent-500 transition-all duration-500"
            ></div>
          </div>
          <span className="block text-[10px] text-slate-400 italic">Level up every 200 XP. Focus sessions and healthy habits award XP.</span>
        </div>
      </div>

      {/* Grid: Badges (left) and Leaderboard (right) */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Achievements Badge Grid */}
        <div className="xl:col-span-2 glass-card p-6 border-brand-500/10">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
            <Trophy className="w-5 h-5 text-amber-500" />
            Shield Badges Collection
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mb-6">
            Earn badges by logging short night sessions, keeping low scroll ratios, and maintaining streaks.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {achievementsData.achievements.map((ach) => {
              const Icon = iconMap[ach.icon] || Award;
              return (
                <div 
                  key={ach.name}
                  className={`p-4 rounded-xl border flex gap-4 transition-all duration-300 ${
                    ach.is_earned 
                      ? 'bg-slate-50/50 dark:bg-slate-900/50 border-brand-500/20 text-slate-800 dark:text-slate-200' 
                      : 'bg-slate-100/20 dark:bg-slate-950/20 border-slate-200 dark:border-slate-900 text-slate-400 dark:text-slate-600'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-sm shrink-0 ${
                    ach.is_earned 
                      ? 'bg-brand-500/10 border-brand-500/20 text-brand-500' 
                      : 'bg-slate-200/50 dark:bg-slate-900/50 border-slate-350 dark:border-slate-800/80'
                  }`}>
                    {ach.is_earned ? <Icon className="w-6 h-6 animate-pulse" /> : <Lock className="w-5 h-5" />}
                  </div>
                  <div>
                    <span className="block font-bold text-sm">{ach.name}</span>
                    <span className="block text-xs text-slate-400 mt-0.5 leading-normal">{ach.description}</span>
                    {ach.is_earned && (
                      <span className="block text-[10px] text-brand-400 font-semibold mt-1">
                        Earned: {new Date(ach.date_earned).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Global Streak Leaderboard */}
        <div className="glass-card p-6 border-brand-500/10">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
            <Flame className="w-5 h-5 text-red-500" />
            Competitive Standings
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mb-6">
            Compare consecutive digital well-being logging days.
          </p>

          <div className="space-y-3">
            {leaderboard.map((user) => (
              <div 
                key={user.user_id}
                className={`p-3 rounded-xl border flex items-center justify-between text-xs transition-colors ${
                  user.is_self 
                    ? 'bg-brand-500/10 border-brand-500/30' 
                    : 'bg-slate-50/50 dark:bg-slate-900/40 border-slate-200/40 dark:border-slate-850'
                }`}
              >
                <div className="flex items-center gap-3">
                  {/* Rank Circle */}
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs ${
                    user.rank === 1 ? 'bg-amber-500 text-white' :
                    user.rank === 2 ? 'bg-slate-400 text-white' :
                    user.rank === 3 ? 'bg-amber-700 text-white' :
                    'bg-slate-200 dark:bg-slate-800 text-slate-500'
                  }`}>
                    {user.rank}
                  </span>
                  <div>
                    <span className="font-bold block">
                      {user.name} {user.is_self && <span className="text-[9px] uppercase font-semibold text-brand-500 dark:text-brand-400 ml-1">(You)</span>}
                    </span>
                    <span className="text-[10px] text-slate-400">Level {user.level} • {user.points} XP</span>
                  </div>
                </div>

                <div className="flex items-center gap-1 font-bold text-red-500">
                  <Flame className="w-4 h-4" />
                  <span>{user.streak} days</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Weekly PDF Report Generation Card */}
      <div className="glass-card p-6 border-brand-500/10 bg-gradient-to-r from-brand-650/10 to-accent-650/10 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="p-4 bg-brand-500/10 border border-brand-500/20 text-brand-500 rounded-2xl shrink-0">
            <FileText className="w-8 h-8" />
          </div>
          <div>
            <h3 className="font-bold text-base">Generate Weekly Well-being PDF Report</h3>
            <p className="text-slate-500 dark:text-slate-400 text-xs mt-1">
              Download a comprehensive habit compilation with screen statistics, AI triggers analysis, and suggestions.
            </p>
          </div>
        </div>
        
        <button
          onClick={handleDownloadReport}
          disabled={downloading}
          className="w-full md:w-auto px-6 py-3.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-lg shadow-brand-600/15 transition-all active:scale-[0.98]"
        >
          {downloading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              Generating...
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              Download Report (PDF)
            </>
          )}
        </button>
      </div>
    </div>
  );
}
export default Leaderboard;
