import { useState, useEffect, useCallback } from 'react';

export function useScrollTracker() {
  const [scrollCount, setScrollCount] = useState(0);
  const [sessionStartTime] = useState(() => Date.now());
  const [sessionDuration, setSessionDuration] = useState(0); // in minutes
  const [appOpens, setAppOpens] = useState(1);
  const [nightUsage, setNightUsage] = useState(0);
  const [dailyScreenTime, setDailyScreenTime] = useState(45); // simulated baseline daily screen time in minutes

  // Calculate session duration dynamically in real-time (demo speed: 1 second = 1 minute of scrolling)
  // This allows the user to see the session duration increase without waiting 30 real minutes!
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionDuration(prev => {
        const nextVal = parseFloat((prev + 0.5).toFixed(1)); // Increment by 0.5 "minutes"
        // Also increment daily screen time accordingly
        setDailyScreenTime(t => t + 1);
        return nextVal;
      });
    }, 15000); // every 15 seconds, add 0.5 minutes (which represents 30 seconds of scaled time)

    return () => clearInterval(interval);
  }, []);

  // Track actual physical scrolling in the browser
  useEffect(() => {
    const handleScroll = () => {
      // Increment scroll count, but throttle slightly to avoid excessive state updates
      setScrollCount(prev => prev + 1);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Calculate if it is night usage (10 PM to 5 AM)
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour >= 22 || hour < 5) {
      setNightUsage(1);
    } else {
      setNightUsage(0);
    }
  }, []);

  const resetTracker = useCallback(() => {
    setScrollCount(0);
    setSessionDuration(0);
    setAppOpens(1);
    // Baseline screen time
    setDailyScreenTime(45);
  }, []);

  const incrementAppOpens = useCallback(() => {
    setAppOpens(prev => prev + 1);
  }, []);

  const simulateScroll = useCallback((amount) => {
    setScrollCount(prev => prev + amount);
  }, []);

  const simulateTime = useCallback((minutes) => {
    setSessionDuration(prev => parseFloat((prev + minutes).toFixed(1)));
    setDailyScreenTime(t => t + minutes);
  }, []);

  return {
    scrollCount,
    sessionDuration,
    appOpens,
    nightUsage,
    dailyScreenTime,
    setScrollCount,
    setSessionDuration,
    setAppOpens,
    setNightUsage,
    setDailyScreenTime,
    resetTracker,
    incrementAppOpens,
    simulateScroll,
    simulateTime
  };
}
export default useScrollTracker;
