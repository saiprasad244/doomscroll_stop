from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database.connection import get_db_connection
from datetime import datetime

mood_bp = Blueprint('mood', __name__)

@mood_bp.route('/mood', methods=['POST'])
@jwt_required()
def log_mood():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    mood = data.get('mood')
    
    if not mood or mood not in ["Happy", "Sad", "Stressed", "Tired"]:
        return jsonify({"message": "Valid mood (Happy, Sad, Stressed, Tired) is required."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO mood_logs (user_id, mood, timestamp) VALUES (?, ?, ?)",
            (user_id, mood, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Mood logged successfully."}), 201
    except Exception as e:
        conn.close()
        return jsonify({"message": f"Failed to log mood: {str(e)}"}), 500

@mood_bp.route('/mood/correlation', methods=['GET'])
@jwt_required()
def get_mood_correlation():
    user_id = int(get_jwt_identity())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Analyze the relationship:
    # Find predictions and mood logs logged on the same calendar date.
    # Group by mood and count predicted categories.
    cursor.execute('''
        SELECT m.mood, p.category, COUNT(*) as count
        FROM mood_logs m
        JOIN predictions p ON m.user_id = p.user_id AND DATE(m.timestamp) = DATE(p.prediction_time)
        WHERE m.user_id = ?
        GROUP BY m.mood, p.category
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Organize data into a structured response
    correlation = {}
    for mood in ["Happy", "Sad", "Stressed", "Tired"]:
        correlation[mood] = {
            "Healthy": 0,
            "Risky": 0,
            "Severe": 0,
            "total_sessions": 0
        }
        
    for row in rows:
        m = row['mood']
        c = row['category']
        cnt = row['count']
        if m in correlation:
            correlation[m][c] = cnt
            correlation[m]["total_sessions"] += cnt
            
    # Calculate percentages for rendering
    formatted_correlation = []
    for mood, data in correlation.items():
        total = data["total_sessions"]
        formatted_correlation.append({
            "mood": mood,
            "total_sessions": total,
            "Healthy_pct": round((data["Healthy"] / total * 100), 1) if total > 0 else 0.0,
            "Risky_pct": round((data["Risky"] / total * 100), 1) if total > 0 else 0.0,
            "Severe_pct": round((data["Severe"] / total * 100), 1) if total > 0 else 0.0
        })
        
    return jsonify(formatted_correlation), 200
