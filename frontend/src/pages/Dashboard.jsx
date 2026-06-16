import React, { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement, 
  ArcElement, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Line, Pie, Bar } from 'react-chartjs-2';
import { 
  Tv, 
  MousePointerClick, 
  Flame, 
  Award, 
  Plus, 
  Clock, 
  AlertTriangle, 
  Moon, 
  BrainCircuit, 
  Smile, 
  CloudRain, 
  Activity, 
  TrendingUp 
} from 'lucide-react';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export function Dashboard({ tracker, onTriggerIntervention }) {
  const [dbStats, setDbStats] = useState(null);
  const [moodCorrelation, setMoodCorrelation] = useState([]);
  const [recentSessions, setRecentSessions] = useState([]);
  const [currentPrediction, setCurrentPrediction] = useState(null);
  const [projection, setProjection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [moodLoading, setMoodLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);

  // Fetch all dashboard data from API
  const fetchDashboardData = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
      // Fetch core dashboard details
      const response = await fetch('http://localhost:5000/api/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok) {
        setDbStats(data);
        setRecentSessions(data.recent_sessions || []);
      }
      
      // Fetch mood correlations
      const moodResponse = await fetch('http://localhost:5000/api/mood/correlation', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const moodData = await moodResponse.json();
      if (moodResponse.ok) {
        setMoodCorrelation(moodData);
      }
    } catch (err) {
      console.error("Failed to fetch dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Handle Mood log submit
  const handleLogMood = async (selectedMood) => {
    setMoodLoading(true);
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:5000/api/mood', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ mood: selectedMood })
      });
      if (response.ok) {
        await fetchDashboardData();
      }
    } catch (err) {
      console.error("Failed to log mood:", err);
    } finally {
      setMoodLoading(false);
    }
  };

  // Run AI Check with simulator/tracker variables
  const handleAICheck = async () => {
    setSimulating(true);
    const token = localStorage.getItem('token');
    
    // Log the usage session in the database first
    try {
      await fetch('http://localhost:5000/api/usage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          app_name: "Social Simulator",
          session_duration: tracker.sessionDuration,
          scroll_count: tracker.scrollCount,
          screen_time: tracker.dailyScreenTime,
          app_opens: tracker.appOpens,
          night_usage: tracker.nightUsage
        })
      });
      
      // Request model prediction
      const predictResponse = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_duration: tracker.sessionDuration,
          scroll_count: tracker.scrollCount,
          app_opens: tracker.appOpens,
          night_usage: tracker.nightUsage,
          screen_time: tracker.dailyScreenTime
        })
      });
      
      const predictData = await predictResponse.json();
      
      if (predictResponse.ok) {
        setCurrentPrediction(predictData.current_prediction);
        setProjection(predictData.future_7_day_projection);
        
        // Trigger modal pop-up intervention if Risky or Severe
        if (predictData.current_prediction.category === 'Severe' || predictData.current_prediction.category === 'Risky') {
          onTriggerIntervention(
            tracker.sessionDuration,
            tracker.scrollCount,
            predictData.current_prediction.risk_score
          );
        }
        
        // Refresh charts
        await fetchDashboardData();
      }
    } catch (err) {
      console.error("AI check error:", err);
    } finally {
      setSimulating(false);
    }
  };

  if (loading || !dbStats) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // --- Chart.js Data Formats ---

  // 1. Line Chart: Weekly Screen Time Trend
  const weeklyTrendData = {
    labels: dbStats.charts.weekly_trend.map(d => {
      const parts = d.date.split('-');
      return `${parts[1]}/${parts[2]}`; // MM/DD
    }),
    datasets: [
      {
        label: 'Daily Session Duration (mins)',
        data: dbStats.charts.weekly_trend.map(d => d.duration),
        fill: true,
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.15)',
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: '#8b5cf6',
        pointHoverRadius: 6,
      }
    ]
  };

  // 2. Pie Chart: AI Prediction Category counts
  const categoryDist = dbStats.charts.category_distribution;
  const pieChartData = {
    labels: ['Healthy', 'Risky', 'Severe'],
    datasets: [
      {
        data: [categoryDist.Healthy, categoryDist.Risky, categoryDist.Severe],
        backgroundColor: [
          'rgba(34, 197, 94, 0.75)', // Green
          'rgba(245, 158, 11, 0.75)', // Orange
          'rgba(239, 68, 68, 0.75)'  // Red
        ],
        borderWidth: 1,
        borderColor: 'rgba(255, 255, 255, 0.15)',
      }
    ]
  };

  // 3. Bar Chart: Mood distribution
  const moodDist = dbStats.charts.mood_distribution;
  const barChartData = {
    labels: ['Happy', 'Sad', 'Stressed', 'Tired'],
    datasets: [
      {
        label: 'Sessions Logged',
        data: [moodDist.Happy, moodDist.Sad, moodDist.Stressed, moodDist.Tired],
        backgroundColor: [
          'rgba(6, 182, 212, 0.7)',
          'rgba(168, 85, 247, 0.7)',
          'rgba(239, 68, 68, 0.7)',
          'rgba(245, 158, 11, 0.7)'
        ],
        borderRadius: 8,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#64748b' } },
      y: { grid: { color: 'rgba(148, 163, 184, 0.08)' }, ticks: { color: '#64748b' } }
    }
  };

  return (
    <div className="space-y-8 pb-10">
      {/* Header Greeting */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 dark:from-white dark:via-brand-200 dark:to-accent-200 bg-clip-text text-transparent">
          Analytics Dashboard
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
          Monitor your digital habits and run real-time AI doomscroll assessments.
        </p>
      </div>

      {/* Top 4 Stats Widgets */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 flex items-center gap-4">
          <div className="p-3 bg-brand-500/10 text-brand-500 rounded-xl">
            <Tv className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider">Today's Screen Time</span>
            <span className="text-xl font-bold">{dbStats.stats.today_screen_time} mins</span>
          </div>
        </div>

        <div className="glass-card p-5 flex items-center gap-4">
          <div className="p-3 bg-accent-500/10 text-accent-500 rounded-xl">
            <MousePointerClick className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider">Browser Scrolls</span>
            <span className="text-xl font-bold">{tracker.scrollCount}</span>
          </div>
        </div>

        <div className="glass-card p-5 flex items-center gap-4">
          <div className="p-3 bg-red-500/10 text-red-500 rounded-xl">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider">Current Streak</span>
            <span className="text-xl font-bold">3 Days</span> {/* Dynamic fallback */}
          </div>
        </div>

        <div className="glass-card p-5 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-500 rounded-xl">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <span className="block text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider">Average Risk</span>
            <span className="text-xl font-bold">{dbStats.stats.avg_risk_score}%</span>
          </div>
        </div>
      </div>

      {/* Primary Simulator & Real-time Check Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Scroll Simulator Control Panel */}
        <div className="xl:col-span-2 glass-card p-6 border-brand-500/10">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
            <BrainCircuit className="w-5 h-5 text-brand-500" />
            Live Doomscrolling Simulator
          </h2>
          <p className="text-slate-500 dark:text-slate-400 text-xs mb-6">
            Social media apps use behavioral psychology. Simulate usage increments to evaluate how our trained ML models predict addiction risks.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                  Session Duration: {tracker.sessionDuration} mins
                </label>
                <div className="flex gap-2">
                  <button 
                    onClick={() => tracker.simulateTime(5)}
                    className="flex-1 py-2 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-800"
                  >
                    +5 mins
                  </button>
                  <button 
                    onClick={() => tracker.simulateTime(15)}
                    className="flex-1 py-2 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-800"
                  >
                    +15 mins
                  </button>
                  <button 
                    onClick={() => tracker.simulateTime(30)}
                    className="flex-1 py-2 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-800"
                  >
                    +30 mins
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
                  Scroll Actions: {tracker.scrollCount}
                </label>
                <div className="flex gap-2">
                  <button 
                    onClick={() => tracker.simulateScroll(20)}
                    className="flex-1 py-2 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-800"
                  >
                    +20 scrolls
                  </button>
                  <button 
                    onClick={() => tracker.simulateScroll(50)}
                    className="flex-1 py-2 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-800"
                  >
                    +50 scrolls
                  </button>
                  <button 
                    onClick={() => tracker.simulateScroll(120)}
                    className="flex-1 py-2 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-800"
                  >
                    +120 scrolls
                  </button>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">App Opens</label>
                  <input
                    type="number"
                    value={tracker.appOpens}
                    onChange={(e) => tracker.setAppOpens(parseInt(e.target.value) || 1)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Daily Screen</label>
                  <input
                    type="number"
                    value={tracker.dailyScreenTime}
                    onChange={(e) => tracker.setDailyScreenTime(parseInt(e.target.value) || 30)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-100/50 dark:bg-slate-900/50 rounded-xl border border-slate-200/50 dark:border-slate-800/80">
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                  <Moon className="w-4 h-4 text-slate-400" />
                  Night Session Toggle
                </span>
                <input
                  type="checkbox"
                  checked={tracker.nightUsage === 1}
                  onChange={(e) => tracker.setNightUsage(e.target.checked ? 1 : 0)}
                  className="w-4 h-4 rounded text-brand-500 focus:ring-brand-500 bg-slate-200 border-slate-300"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleAICheck}
              disabled={simulating}
              className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-brand-600/10 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {simulating ? 'Analyzing...' : 'Trigger AI Classification Check'}
            </button>
            <button
              onClick={tracker.resetTracker}
              className="px-5 py-3.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium transition-colors"
            >
              Reset Session
            </button>
          </div>
        </div>

        {/* AI Predictor Live Results */}
        <div className="glass-card p-6 flex flex-col justify-between border-brand-500/10">
          <div>
            <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-accent-500" />
              Real-time Inference
            </h2>
            
            {currentPrediction ? (
              <div className="space-y-6">
                {/* Risk score gauge */}
                <div className="text-center py-6 border-b border-slate-200/50 dark:border-slate-800">
                  <div className="inline-block relative">
                    {/* Ring score */}
                    <div className="w-28 h-28 rounded-full border-4 border-slate-200 dark:border-slate-800 flex flex-col items-center justify-center">
                      <span className={`text-3xl font-extrabold ${
                        currentPrediction.category === 'Severe' ? 'text-red-500' :
                        currentPrediction.category === 'Risky' ? 'text-amber-500' : 'text-green-500'
                      }`}>
                        {currentPrediction.risk_score}%
                      </span>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Risk Score</span>
                    </div>
                  </div>
                  
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold mt-4 uppercase ${
                    currentPrediction.category === 'Severe' ? 'bg-red-500/10 text-red-500' :
                    currentPrediction.category === 'Risky' ? 'bg-amber-500/10 text-amber-500' : 'bg-green-500/10 text-green-500'
                  }`}>
                    {currentPrediction.category} Usage
                  </span>
                </div>

                {/* Model details */}
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Classifier Used:</span>
                    <span className="font-semibold">{currentPrediction.model_used}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Severe Probability:</span>
                    <span className="font-mono">{(currentPrediction.probabilities.Severe * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Risky Probability:</span>
                    <span className="font-mono">{(currentPrediction.probabilities.Risky * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-48 flex flex-col items-center justify-center text-center text-slate-400">
                <BrainCircuit className="w-10 h-10 text-slate-300 dark:text-slate-700 mb-3 animate-bounce" />
                <p className="text-xs">No active prediction.</p>
                <p className="text-[10px] text-slate-500 mt-1">Click the trigger button on the left to evaluate.</p>
              </div>
            )}
          </div>

          {/* 7-Day forecasting projection */}
          <div className="pt-4 border-t border-slate-200/50 dark:border-slate-800 mt-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5 mb-2">
              <TrendingUp className="w-4 h-4 text-accent-500" />
              7-Day Risk Projection
            </h3>
            {projection ? (
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold">{projection.status}</span>
                <span className={`text-sm font-bold ${
                  projection.risk_score >= 65 ? 'text-red-500' :
                  projection.risk_score >= 35 ? 'text-amber-500' : 'text-green-500'
                }`}>
                  {projection.risk_score}% Score
                </span>
              </div>
            ) : (
              <span className="text-slate-500 text-xs italic">Awaiting AI check run...</span>
            )}
          </div>
        </div>
      </div>

      {/* Charts Display Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly Screen Time Line Chart */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Weekly Screen Time Trend</h3>
          <div className="h-56 flex items-center justify-center">
            <Line data={weeklyTrendData} options={chartOptions} />
          </div>
        </div>

        {/* Prediction Category Count Pie Chart */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Doomscrolling Proportions</h3>
          <div className="h-56 flex items-center justify-center">
            <div className="w-48 h-48">
              <Pie data={pieChartData} options={{ responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#64748b', boxWidth: 12 } } } }} />
            </div>
          </div>
        </div>

        {/* Mood Distribution Bar Chart */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Mood Logs Counts</h3>
          <div className="h-56 flex items-center justify-center">
            <Bar data={barChartData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Advanced Mood Tracker & Recent Sessions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mood Tracker Widget */}
        <div className="glass-card p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-2">How are you feeling right now?</h3>
            <p className="text-slate-500 dark:text-slate-400 text-xs mb-6">
              Logging mood helps analyze emotional doomscroll triggers.
            </p>
            
            <div className="grid grid-cols-4 gap-3">
              {[
                { name: "Happy", icon: Smile, color: "text-cyan-500 bg-cyan-500/10 hover:bg-cyan-500/20" },
                { name: "Sad", icon: CloudRain, color: "text-purple-500 bg-purple-500/10 hover:bg-purple-500/20" },
                { name: "Stressed", icon: AlertTriangle, color: "text-red-500 bg-red-500/10 hover:bg-red-500/20" },
                { name: "Tired", icon: Moon, color: "text-amber-500 bg-amber-500/10 hover:bg-amber-500/20" }
              ].map((moodItem) => {
                const Icon = moodItem.icon;
                return (
                  <button
                    key={moodItem.name}
                    disabled={moodLoading}
                    onClick={() => handleLogMood(moodItem.name)}
                    className={`p-4 rounded-xl flex flex-col items-center gap-2 font-semibold text-xs transition-colors duration-200 border border-slate-200/40 dark:border-slate-800/40 ${moodItem.color}`}
                  >
                    <Icon className="w-6 h-6" />
                    {moodItem.name}
                  </button>
                );
              })}
            </div>
          </div>
          
          {/* Mood-Severe correlation analysis listing */}
          <div className="pt-6 border-t border-slate-200/50 dark:border-slate-800 mt-6">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">AI Mood Trigger Correlation</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              {moodCorrelation.length > 0 ? (
                moodCorrelation.map((corr) => (
                  <div key={corr.mood} className="flex justify-between p-2 rounded-lg bg-slate-50 dark:bg-slate-900/40">
                    <span className="font-semibold">{corr.mood}:</span>
                    <span className="text-red-500 font-mono">{corr.Severe_pct}% Severe</span>
                  </div>
                ))
              ) : (
                <span className="text-slate-500 italic">No mood data logged today.</span>
              )}
            </div>
          </div>
        </div>

        {/* Recent Usage Logs List */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Recent Logged Sessions</h3>
          {recentSessions.length > 0 ? (
            <div className="divide-y divide-slate-200/50 dark:divide-slate-800">
              {recentSessions.map((session, idx) => (
                <div key={idx} className="py-3 flex justify-between items-center text-sm first:pt-0 last:pb-0">
                  <div>
                    <span className="font-semibold block">{session.app_name}</span>
                    <span className="text-xs text-slate-400">{new Date(session.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold block">{session.session_duration} mins</span>
                    <span className="text-xs text-slate-400 font-mono">{session.scroll_count} scrolls</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-40 flex items-center justify-center text-slate-400 text-xs">
              No logged sessions.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
export default Dashboard;
