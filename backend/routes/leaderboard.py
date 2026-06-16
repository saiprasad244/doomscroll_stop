from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database.connection import get_db_connection
from datetime import datetime, timedelta

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    user_id = int(get_jwt_identity())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()
    
    leaderboard_data = []
    
    for u in users:
        curr_user_id = u['id']
        name = u['name']
        
        # Calculate points for this user
        cursor.execute("SELECT COUNT(*) as count FROM usage_logs WHERE user_id = ?", (curr_user_id,))
        logs_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT category, COUNT(*) as count FROM predictions WHERE user_id = ? GROUP BY category", (curr_user_id,))
        pred_counts = {row['category']: row['count'] for row in cursor.fetchall()}
        healthy_count = pred_counts.get('Healthy', 0)
        risky_count = pred_counts.get('Risky', 0)
        
        cursor.execute("SELECT COUNT(*) as count FROM achievements WHERE user_id = ?", (curr_user_id,))
        badges_count = cursor.fetchone()['count']
        
        points = (logs_count * 20) + (healthy_count * 50) + (risky_count * 15) + (badges_count * 100)
        level = 1 + int(points / 200)
        
        # Calculate streak
        cursor.execute('''
            SELECT DATE(timestamp) as log_date FROM usage_logs 
            WHERE user_id = ? 
            GROUP BY DATE(timestamp) 
            ORDER BY log_date DESC
        ''', (curr_user_id,))
        log_dates = [row['log_date'] for row in cursor.fetchall()]
        
        streak = 0
        if log_dates:
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
                        
        leaderboard_data.append({
            "user_id": curr_user_id,
            "name": name,
            "streak": streak,
            "points": points,
            "level": level,
            "is_self": curr_user_id == user_id
        })
        
    conn.close()
    
    # Sort leaderboard by streak DESC, then points DESC
    leaderboard_data.sort(key=lambda x: (x['streak'], x['points']), reverse=True)
    
    # Add rank index (1-based)
    for i, item in enumerate(leaderboard_data):
        item['rank'] = i + 1
        
    return jsonify(leaderboard_data), 200
