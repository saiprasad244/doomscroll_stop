import os
import json
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database.connection import get_db_connection
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

COMPARISON_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models', 'model_comparison.json')

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    user_id = int(get_jwt_identity())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current time ranges
    today_str = datetime.now().strftime("%Y-%m-%d")
    week_ago_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago_str = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # 1. Total Daily Screen Time Today (sum of session_duration for social media, or max of screen_time)
    cursor.execute('''
        SELECT COALESCE(SUM(session_duration), 0) as total_duration, 
               COALESCE(MAX(screen_time), 0) as max_screen_time 
        FROM usage_logs 
        WHERE user_id = ? AND DATE(timestamp) = DATE('now', 'localtime')
    ''', (user_id,))
    today_data = cursor.fetchone()
    today_duration = round(today_data['total_duration'], 1)
    # If daily screen_time was logged, we use it as daily total, else fallback to sum of sessions
    today_screen_time = today_data['max_screen_time'] if today_data['max_screen_time'] > 0 else int(today_duration)
    
    # 2. Total Weekly Screen Time (sum of session durations over last 7 days)
    cursor.execute('''
        SELECT COALESCE(SUM(session_duration), 0) as weekly_duration 
        FROM usage_logs 
        WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-7 days', 'localtime')
    ''', (user_id,))
    weekly_screen_time = round(cursor.fetchone()['weekly_duration'], 1)
    
    # 3. Total Monthly Screen Time (sum of session durations over last 30 days)
    cursor.execute('''
        SELECT COALESCE(SUM(session_duration), 0) as monthly_duration 
        FROM usage_logs 
        WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-30 days', 'localtime')
    ''', (user_id,))
    monthly_screen_time = round(cursor.fetchone()['monthly_duration'], 1)
    
    # 4. Average Doomscrolling / Addiction Risk Score
    cursor.execute('''
        SELECT COALESCE(AVG(risk_score), 0) as avg_risk 
        FROM predictions 
        WHERE user_id = ?
    ''', (user_id,))
    avg_risk_score = round(cursor.fetchone()['avg_risk'], 1)
    
    # 5. Prediction category distribution (for Pie Chart)
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM predictions 
        WHERE user_id = ? 
        GROUP BY category
    ''', (user_id,))
    category_rows = cursor.fetchall()
    category_distribution = {row['category']: row['count'] for row in category_rows}
    for cat in ["Healthy", "Risky", "Severe"]:
        if cat not in category_distribution:
            category_distribution[cat] = 0
            
    # 6. Daily Screen Time trends (last 7 days - for Line Chart)
    cursor.execute('''
        SELECT DATE(timestamp) as log_date, SUM(session_duration) as daily_duration 
        FROM usage_logs 
        WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-6 days', 'localtime')
        GROUP BY DATE(timestamp)
        ORDER BY log_date ASC
    ''', (user_id,))
    trend_rows = cursor.fetchall()
    
    # Fill in missing days in the last 7 days trend
    trend_dict = {row['log_date']: round(row['daily_duration'], 1) for row in trend_rows}
    weekly_trend = []
    for i in range(7):
        day = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        weekly_trend.append({
            "date": day,
            "duration": trend_dict.get(day, 0.0)
        })
        
    # 7. Recent Sessions (last 5 logs)
    cursor.execute('''
        SELECT app_name, session_duration, scroll_count, timestamp 
        FROM usage_logs 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''', (user_id,))
    recent_sessions = [
        {
            "app_name": row['app_name'],
            "session_duration": row['session_duration'],
            "scroll_count": row['scroll_count'],
            "timestamp": row['timestamp']
        } for row in cursor.fetchall()
    ]
    
    # 8. Mood distribution (for Bar Chart)
    cursor.execute('''
        SELECT mood, COUNT(*) as count 
        FROM mood_logs 
        WHERE user_id = ? 
        GROUP BY mood
    ''', (user_id,))
    mood_rows = cursor.fetchall()
    mood_distribution = {row['mood']: row['count'] for row in mood_rows}
    for m in ["Happy", "Sad", "Stressed", "Tired"]:
        if m not in mood_distribution:
            mood_distribution[m] = 0
            
    # 9. Load ML Comparison data
    ml_comparison = {}
    if os.path.exists(COMPARISON_PATH):
        try:
            with open(COMPARISON_PATH, 'r') as f:
                ml_comparison = json.load(f)
        except Exception:
            pass
            
    conn.close()
    
    return jsonify({
        "stats": {
            "today_screen_time": today_screen_time,
            "weekly_screen_time": weekly_screen_time,
            "monthly_screen_time": monthly_screen_time,
            "avg_risk_score": avg_risk_score
        },
        "charts": {
            "category_distribution": category_distribution,
            "weekly_trend": weekly_trend,
            "mood_distribution": mood_distribution
        },
        "recent_sessions": recent_sessions,
        "ml_comparison": ml_comparison
    }), 200
