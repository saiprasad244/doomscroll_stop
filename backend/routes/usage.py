from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database.connection import get_db_connection
from datetime import datetime, timedelta

usage_bp = Blueprint('usage', __name__)

@usage_bp.route('/usage', methods=['POST'])
@jwt_required()
def log_usage():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    app_name = data.get('app_name')
    session_duration = data.get('session_duration') # in minutes
    scroll_count = data.get('scroll_count')
    screen_time = data.get('screen_time') # daily total in minutes
    app_opens = data.get('app_opens') # daily count
    night_usage = data.get('night_usage', 0)
    
    if not app_name or session_duration is None or scroll_count is None or screen_time is None or app_opens is None:
        return jsonify({"message": "app_name, session_duration, scroll_count, screen_time, and app_opens are required."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Save to usage_logs
    try:
        cursor.execute('''
            INSERT INTO usage_logs (user_id, app_name, session_duration, scroll_count, screen_time, app_opens, night_usage, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, app_name, float(session_duration), int(scroll_count), int(screen_time), int(app_opens), int(night_usage), datetime.now().isoformat()))
        conn.commit()
        
        # Check and award streak-based/action-based achievements
        new_badges = check_and_award_achievements(cursor, user_id)
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Usage session logged successfully.",
            "new_achievements": new_badges
        }), 201
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"message": f"Failed to log usage: {str(e)}"}), 500

def check_and_award_achievements(cursor, user_id):
    new_badges = []
    
    # Check all existing achievements
    cursor.execute("SELECT badge_name FROM achievements WHERE user_id = ?", (user_id,))
    existing_badges = {row['badge_name'] for row in cursor.fetchall()}
    
    # Helper to insert badge
    def award_badge(badge):
        if badge not in existing_badges:
            cursor.execute(
                "INSERT OR IGNORE INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)",
                (user_id, badge, datetime.now().isoformat())
            )
            new_badges.append(badge)
            
    # Achievement 1: First Log ("Shield Activated")
    cursor.execute("SELECT count(*) as count FROM usage_logs WHERE user_id = ?", (user_id,))
    total_logs = cursor.fetchone()['count']
    if total_logs >= 1:
        award_badge("Shield Activated")
        
    # Achievement 2: Mindful Scroller (Logged a session with < 30 scrolls and duration > 5 min)
    cursor.execute('''
        SELECT count(*) as count FROM usage_logs 
        WHERE user_id = ? AND scroll_count <= 30 AND session_duration >= 5
    ''', (user_id,))
    mindful_count = cursor.fetchone()['count']
    if mindful_count >= 1:
        award_badge("Mindful Scroller")
        
    # Achievement 3: 3 Days Focus Streak (Usage logged on 3 consecutive days)
    # Check consecutive days
    cursor.execute('''
        SELECT DATE(timestamp) as log_date FROM usage_logs 
        WHERE user_id = ? 
        GROUP BY DATE(timestamp) 
        ORDER BY log_date DESC
    ''', (user_id,))
    log_dates = [row['log_date'] for row in cursor.fetchall()]
    
    # Calculate current streak
    streak = 0
    if log_dates:
        # Convert to date objects
        dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in log_dates]
        today = datetime.now().date()
        
        # Check if latest log is today or yesterday to continue streak
        if dates[0] == today or dates[0] == (today - timedelta(days=1)):
            streak = 1
            for i in range(len(dates) - 1):
                if (dates[i] - dates[i+1]) == timedelta(days=1):
                    streak += 1
                elif (dates[i] - dates[i+1]) == timedelta(days=0):
                    continue
                else:
                    break
                    
    if streak >= 3:
        award_badge("3 Days Focus Streak")
    if streak >= 7:
        award_badge("7 Days Healthy Usage")
        
    # Achievement 4: Night Guardian (Session duration < 10 mins and night_usage = 1)
    cursor.execute('''
        SELECT count(*) as count FROM usage_logs 
        WHERE user_id = ? AND night_usage = 1 AND session_duration <= 10
    ''', (user_id,))
    night_guardian = cursor.fetchone()['count']
    if night_guardian >= 1:
        award_badge("Night Guardian")
        
    return new_badges
