import React from 'react';
import { AlertTriangle, Timer, Ban, RefreshCw } from 'lucide-react';

export function InterventionModal({ isOpen, sessionDuration, scrollCount, riskScore, onClose, onStartFocusMode }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md transition-all duration-300">
      <div className="relative w-full max-w-md p-8 glass-card border border-red-500/20 shadow-2xl text-center">
        {/* Glowing aura */}
        <div className="absolute inset-0 bg-gradient-to-b from-red-500/5 to-transparent rounded-2xl pointer-events-none"></div>

        {/* Warning Icon */}
        <div className="w-16 h-16 mx-auto mb-6 bg-red-500/10 border border-red-500/20 text-red-500 rounded-full flex items-center justify-center animate-bounce">
          <AlertTriangle className="w-8 h-8" />
        </div>

        <h2 className="text-2xl font-bold text-red-500 dark:text-red-400 mb-2">
          Severe Doomscrolling Detected!
        </h2>
        <p className="text-slate-600 dark:text-slate-300 text-sm mb-6">
          AI predicts a <span className="font-semibold text-red-500">{riskScore}% Risk Score</span>. You have been continuously scrolling for <span className="font-semibold">{sessionDuration} minutes</span> with <span className="font-semibold">{scrollCount} actions</span>.
        </p>

        {/* Informative Stats */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="p-3 bg-slate-100/60 dark:bg-slate-900/60 border border-slate-200/50 dark:border-slate-800 rounded-xl">
            <span className="block text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Scroll Count</span>
            <span className="text-lg font-bold text-slate-800 dark:text-white">{scrollCount}</span>
          </div>
          <div className="p-3 bg-slate-100/60 dark:bg-slate-900/60 border border-slate-200/50 dark:border-slate-800 rounded-xl">
            <span className="block text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">Session Duration</span>
            <span className="text-lg font-bold text-slate-800 dark:text-white">{sessionDuration}m</span>
          </div>
        </div>

        {/* Encouraging Quote */}
        <p className="italic text-slate-500 dark:text-slate-400 text-xs mb-8">
          "The best time to put down the screen was 10 minutes ago. The second best time is now."
        </p>

        {/* Actions */}
        <div className="flex flex-col gap-3">
          <button
            onClick={onStartFocusMode}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-brand-600/20 active:scale-[0.98] transition-all"
          >
            <Timer className="w-5 h-5" />
            Start Focus Mode
          </button>
          
          <button
            onClick={onClose}
            className="w-full py-3.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium active:scale-[0.98] transition-all"
          >
            Continue Anyway (Snooze 5m)
          </button>
        </div>
      </div>
    </div>
  );
}
export default InterventionModal;
