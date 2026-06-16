import React, { useState, useEffect, useRef } from 'react';
import { Timer, Play, Pause, RotateCcw, ShieldAlert, Wind, HelpCircle, CheckCircle } from 'lucide-react';

export function FocusMode() {
  // --- Timer State ---
  const [timerType, setTimerType] = useState('Pomodoro'); // 'Pomodoro' or 'Deep Work'
  const [secondsLeft, setSecondsLeft] = useState(25 * 60);
  const [isActive, setIsActive] = useState(false);
  const [timerLogged, setTimerLogged] = useState(false);
  const incrementInterval = useRef(null);

  // --- Blocker State ---
  const [blockInstagram, setBlockInstagram] = useState(true);
  const [blockTikTok, setBlockTikTok] = useState(true);
  const [blockTwitter, setBlockTwitter] = useState(true);

  // --- Breathing Exercise State ---
  const [isBreathing, setIsBreathing] = useState(false);
  const [breathePhase, setBreathePhase] = useState('Breathe In'); // 'Breathe In', 'Hold', 'Breathe Out'
  const [breatheSeconds, setBreatheSeconds] = useState(4);

  // Sync default durations on timer type switch
  useEffect(() => {
    setIsActive(false);
    setTimerLogged(false);
    if (timerType === 'Pomodoro') {
      setSecondsLeft(25 * 60);
    } else {
      setSecondsLeft(50 * 60);
    }
  }, [timerType]);

  // Countdown clock effect
  useEffect(() => {
    let interval = null;
    if (isActive && secondsLeft > 0) {
      interval = setInterval(() => {
        setSecondsLeft(prev => prev - 1);
      }, 1000);
    } else if (secondsLeft === 0 && isActive) {
      clearInterval(interval);
      setIsActive(false);
      logCompletedSession();
    }
    return () => clearInterval(interval);
  }, [isActive, secondsLeft]);

  // Breathing Exercise Cycle Effect
  useEffect(() => {
    let interval = null;
    if (isBreathing) {
      interval = setInterval(() => {
        setBreatheSeconds(prev => {
          if (prev <= 1) {
            // Switch phase
            setBreathePhase(current => {
              if (current === 'Breathe In') return 'Hold';
              if (current === 'Hold') return 'Breathe Out';
              return 'Breathe In';
            });
            return 4; // Reset phase clock
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      setBreathePhase('Breathe In');
      setBreatheSeconds(4);
    }
    return () => clearInterval(interval);
  }, [isBreathing]);

  // Log session to backend
  const logCompletedSession = async () => {
    if (timerLogged) return;
    const token = localStorage.getItem('token');
    const duration = timerType === 'Pomodoro' ? 25 : 50;
    
    try {
      const response = await fetch('http://localhost:5000/api/focus-mode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          focus_type: timerType,
          duration: duration,
          completed: true
        })
      });
      if (response.ok) {
        setTimerLogged(true);
        alert(`Congratulations! You completed a ${duration}-minute ${timerType} session. 20 XP awarded!`);
      }
    } catch (err) {
      console.error("Failed to log focus session:", err);
    }
  };

  const handleStartPause = () => {
    setIsActive(!isActive);
  };

  const handleReset = () => {
    setIsActive(false);
    setTimerLogged(false);
    setSecondsLeft(timerType === 'Pomodoro' ? 25 * 60 : 50 * 60);
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 dark:from-white dark:via-brand-200 dark:to-accent-200 bg-clip-text text-transparent">
          Focus Mode
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
          Block distractions, activate deep work timers, and re-center your attention.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Timer Card */}
        <div className="xl:col-span-2 glass-card p-8 flex flex-col items-center justify-center border-brand-500/10 text-center relative overflow-hidden">
          {/* Subtle timer glow */}
          {isActive && (
            <div className="absolute w-64 h-64 bg-brand-500/10 rounded-full blur-[80px] pointer-events-none animate-pulse"></div>
          )}

          {/* Selector */}
          <div className="flex gap-2 p-1.5 bg-slate-100 dark:bg-slate-900 border border-slate-200/50 dark:border-slate-800/80 rounded-xl mb-8 z-10">
            <button
              onClick={() => setTimerType('Pomodoro')}
              className={`px-4 py-2 text-xs font-bold rounded-lg transition-colors ${
                timerType === 'Pomodoro' 
                  ? 'bg-brand-500 text-white shadow-md' 
                  : 'text-slate-500 dark:text-slate-400 hover:bg-slate-200/50 dark:hover:bg-slate-800'
              }`}
            >
              Pomodoro (25m)
            </button>
            <button
              onClick={() => setTimerType('Deep Work')}
              className={`px-4 py-2 text-xs font-bold rounded-lg transition-colors ${
                timerType === 'Deep Work' 
                  ? 'bg-brand-500 text-white shadow-md' 
                  : 'text-slate-500 dark:text-slate-400 hover:bg-slate-200/50 dark:hover:bg-slate-800'
              }`}
            >
              Deep Work (50m)
            </button>
          </div>

          {/* Clock Display */}
          <div className="relative mb-8 z-10">
            <div className="text-6xl md:text-8xl font-black font-mono tracking-tight text-slate-800 dark:text-white drop-shadow-sm">
              {formatTime(secondsLeft)}
            </div>
            {timerLogged && (
              <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-bold text-green-500 flex items-center gap-1">
                <CheckCircle className="w-4 h-4" /> Logged!
              </span>
            )}
          </div>

          {/* Buttons */}
          <div className="flex gap-4 z-10">
            <button
              onClick={handleStartPause}
              className={`px-6 py-3 rounded-xl font-semibold flex items-center gap-2 text-sm shadow-md transition-all active:scale-[0.98] ${
                isActive 
                  ? 'bg-amber-500 hover:bg-amber-400 text-white shadow-amber-500/15' 
                  : 'bg-brand-600 hover:bg-brand-500 text-white shadow-brand-600/15'
              }`}
            >
              {isActive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isActive ? 'Pause Timer' : 'Start Focus Session'}
            </button>
            <button
              onClick={handleReset}
              className="px-5 py-3 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200/50 dark:border-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold text-sm transition-all flex items-center gap-1.5"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>

        {/* Content Blocker Card */}
        <div className="glass-card p-6 border-brand-500/10">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
            <ShieldAlert className="w-5 h-5 text-red-500" />
            Distraction App Blocker
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mb-6">
            Configure which domains to block during Focus Mode. Blocking simulates writing hosts/DNS files.
          </p>

          <div className="space-y-4">
            {[
              { id: 'instagram', name: 'Instagram', domain: 'instagram.com', checked: blockInstagram, setter: setBlockInstagram },
              { id: 'tiktok', name: 'TikTok', domain: 'tiktok.com', checked: blockTikTok, setter: setBlockTikTok },
              { id: 'twitter', name: 'Twitter / X', domain: 'twitter.com', checked: blockTwitter, setter: setBlockTwitter }
            ].map((app) => (
              <div 
                key={app.id} 
                className="flex items-center justify-between p-3.5 bg-slate-100/50 dark:bg-slate-900/50 border border-slate-200/40 dark:border-slate-850 rounded-xl"
              >
                <div>
                  <span className="block text-sm font-semibold">{app.name}</span>
                  <span className="block text-xs text-slate-400 font-mono">{app.domain}</span>
                </div>
                <input
                  type="checkbox"
                  checked={app.checked}
                  onChange={(e) => app.setter(e.target.checked)}
                  className="w-4 h-4 rounded text-brand-500 focus:ring-brand-500 bg-slate-200 border-slate-300"
                />
              </div>
            ))}
          </div>

          <div className="mt-6 p-3 bg-brand-500/5 border border-brand-500/10 rounded-xl text-center">
            <span className="text-[10px] uppercase font-bold tracking-wide text-brand-400 block mb-1">Blocker Status</span>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              {blockInstagram || blockTikTok || blockTwitter 
                ? 'Simulation: Distracting content blocked.' 
                : 'Warning: Blocker inactive. Distractions allowed.'}
            </span>
          </div>
        </div>
      </div>

      {/* Breathing Exercise Card */}
      <div className="glass-card p-8 border-brand-500/10 relative overflow-hidden">
        {/* Glowing breathing highlight */}
        {isBreathing && (
          <div className="absolute w-80 h-80 bg-accent-500/10 rounded-full blur-[100px] pointer-events-none top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
        )}

        <div className="max-w-xl mx-auto flex flex-col items-center text-center">
          <div className="w-12 h-12 bg-accent-500/10 text-accent-500 rounded-2xl flex items-center justify-center mb-4">
            <Wind className="w-6 h-6" />
          </div>
          
          <h2 className="text-xl font-bold mb-2">Mindful Breathing Exercise</h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mb-8">
            Feeling the urge to check social media? Take a 2-minute breathing break. This breaks the dopamine feedback loop.
          </p>

          {/* Breathing Circle Visualization */}
          <div className="w-48 h-48 flex items-center justify-center mb-8 relative">
            <div className={`w-32 h-32 rounded-full border border-accent-500/30 flex flex-col items-center justify-center ${
              isBreathing ? 'breathing-circle bg-accent-500/20' : 'bg-slate-100 dark:bg-slate-900'
            }`}>
              <span className="text-lg font-bold text-accent-500 dark:text-accent-400 transition-all duration-500">
                {isBreathing ? breathePhase : 'Idle'}
              </span>
              {isBreathing && (
                <span className="text-xs text-slate-400 font-semibold mt-1">
                  {breatheSeconds}s
                </span>
              )}
            </div>
          </div>

          <button
            onClick={() => {
              setIsBreathing(!isBreathing);
              if (!isBreathing) {
                // Log zen session of 2 minutes to award achievements dynamically
                setTimeout(async () => {
                  const token = localStorage.getItem('token');
                  try {
                    await fetch('http://localhost:5000/api/focus-mode', {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                      },
                      body: JSON.stringify({ focus_type: 'Breathing', duration: 2, completed: true })
                    });
                  } catch(e){}
                }, 120000); // 2 minutes (logs in background)
              }
            }}
            className="px-6 py-3 rounded-xl bg-accent-600 hover:bg-accent-500 text-white font-semibold text-sm shadow-lg shadow-accent-600/15 active:scale-[0.98] transition-all"
          >
            {isBreathing ? 'Stop Exercise' : 'Start 2-Minute Breathing'}
          </button>
        </div>
      </div>
    </div>
  );
}
export default FocusMode;
