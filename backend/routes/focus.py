from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database.connection import get_db_connection
from datetime import datetime

focus_bp = Blueprint('focus', __name__)

@focus_bp.route('/focus-mode', methods=['POST'])
@jwt_required()
def log_focus_mode():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    focus_type = data.get('focus_type') # 'Pomodoro', 'Deep Work', or 'Breathing'
    duration = data.get('duration') # in minutes
    completed = data.get('completed', True)
    
    if not focus_type or duration is None:
        return jsonify({"message": "focus_type and duration are required."}), 400
        
    if not completed:
        return jsonify({"message": "Focus session was not completed. No points awarded."}), 200
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Fetch current badges to check if we should award a focus badge
        cursor.execute("SELECT badge_name FROM achievements WHERE user_id = ?", (user_id,))
        existing_badges = {row['badge_name'] for row in cursor.fetchall()}
        
        new_badges = []
        
        # Award Focus Badge if they completed a Deep Work or Pomodoro session of >= 25 mins
        if focus_type in ['Pomodoro', 'Deep Work'] and duration >= 25:
            badge_name = "Deep Worker"
            if badge_name not in existing_badges:
                cursor.execute(
                    "INSERT OR IGNORE INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)",
                    (user_id, badge_name, datetime.now().isoformat())
                )
                new_badges.append(badge_name)
                
        # Award Breathing Badge if they completed a breathing session
        if focus_type == 'Breathing' and duration >= 2:
            badge_name = "Mindful Zen"
            if badge_name not in existing_badges:
                cursor.execute(
                    "INSERT OR IGNORE INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)",
                    (user_id, badge_name, datetime.now().isoformat())
                )
                new_badges.append(badge_name)
                
        # To persist points, we can add a focus log. But since points are derived dynamically,
        # we can insert a record in usage_logs with a special app name "Focus Mode"
        # so that points are automatically aggregated! That's incredibly elegant!
        cursor.execute('''
            INSERT INTO usage_logs (user_id, app_name, session_duration, scroll_count, screen_time, app_opens, night_usage, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, f"Focus Mode: {focus_type}", float(duration), 0, 0, 0, 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": f"{focus_type} session of {duration} minutes recorded.",
            "points_earned": 20, # focus session is logged as a usage log, giving 20 points
            "new_achievements": new_badges
        }), 200
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"message": f"Failed to record focus session: {str(e)}"}), 500
