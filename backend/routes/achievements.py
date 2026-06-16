from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database.connection import get_db_connection
from datetime import datetime

achievements_bp = Blueprint('achievements', __name__)

@achievements_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_achievements():
    user_id = int(get_jwt_identity())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch earned badges
    cursor.execute('''
        SELECT badge_name, date_earned 
        FROM achievements 
        WHERE user_id = ? 
        ORDER BY date_earned DESC
    ''', (user_id,))
    badges = [{"badge_name": row['badge_name'], "date_earned": row['date_earned']} for row in cursor.fetchall()]
    
    # 2. Calculate gamified points and levels
    # Count usage logs
    cursor.execute("SELECT COUNT(*) as count FROM usage_logs WHERE user_id = ?", (user_id,))
    logs_count = cursor.fetchone()['count']
    
    # Count predictions by category
    cursor.execute("SELECT category, COUNT(*) as count FROM predictions WHERE user_id = ? GROUP BY category", (user_id,))
    pred_counts = {row['category']: row['count'] for row in cursor.fetchall()}
    healthy_count = pred_counts.get('Healthy', 0)
    risky_count = pred_counts.get('Risky', 0)
    severe_count = pred_counts.get('Severe', 0)
    
    # Points breakdown:
    # - 20 pts per logged session
    # - 50 pts for Healthy sessions
    # - 15 pts for Risky sessions (logging awareness)
    # - 100 pts per badge earned
    points_from_logs = logs_count * 20
    points_from_predictions = (healthy_count * 50) + (risky_count * 15)
    points_from_badges = len(badges) * 100
    
    total_points = points_from_logs + points_from_predictions + points_from_badges
    current_level = 1 + int(total_points / 200) # Level up every 200 points
    points_to_next_level = 200 - (total_points % 200)
    
    # Calculate streak (re-use logic or fetch current streak)
    cursor.execute('''
        SELECT DATE(timestamp) as log_date FROM usage_logs 
        WHERE user_id = ? 
        GROUP BY DATE(timestamp) 
        ORDER BY log_date DESC
    ''', (user_id,))
    log_dates = [row['log_date'] for row in cursor.fetchall()]
    
    streak = 0
    if log_dates:
        from datetime import datetime, timedelta
        dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in log_dates]
        today = datetime.now().date()
        if dates[0] == today or dates[0] == (today - timedelta(days=1)):
            streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i+1]) == timedelta(days=1):
                    streak += 1
                elif (dates[i] - dates[i+1]) == timedelta(days=0):
                    continue
                else:
                    break
                    
    conn.close()
    
    # Pre-defined list of all possible achievements in the app to display progress
    all_achievements = [
        {"name": "Shield Activated", "description": "Log your first social media usage session.", "icon": "shield"},
        {"name": "Mindful Scroller", "description": "Log a session with under 30 scrolls lasting over 5 minutes.", "icon": "clock"},
        {"name": "3 Days Focus Streak", "description": "Maintain a 3-day streak of logging usage.", "icon": "flame"},
        {"name": "7 Days Healthy Usage", "description": "Maintain a 7-day streak of logging usage.", "icon": "award"},
        {"name": "Night Guardian", "description": "Log a late-night session under 10 minutes (avoiding late-night scrolling).", "icon": "moon"}
    ]
    
    earned_names = {b['badge_name'] for b in badges}
    achievements_status = []
    for ach in all_achievements:
        is_earned = ach['name'] in earned_names
        earned_date = next((b['date_earned'] for b in badges if b['badge_name'] == ach['name']), None)
        achievements_status.append({
            "name": ach['name'],
            "description": ach['description'],
            "icon": ach['icon'],
            "is_earned": is_earned,
            "date_earned": earned_date
        })
        
    return jsonify({
        "points": total_points,
        "level": current_level,
        "points_to_next_level": points_to_next_level,
        "streak": streak,
        "achievements": achievements_status
    }), 200
