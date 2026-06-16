import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database.connection import get_db_connection
from backend.ml.model_loader import predict_doomscroll
from datetime import datetime
from openai import OpenAI

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    session_duration = data.get('session_duration')
    scroll_count = data.get('scroll_count')
    app_opens = data.get('app_opens')
    night_usage = data.get('night_usage', 0)
    screen_time = data.get('screen_time')
    
    if session_duration is None or scroll_count is None or app_opens is None or screen_time is None:
        return jsonify({"message": "session_duration, scroll_count, app_opens, and screen_time are required."}), 400
        
    try:
        prediction = predict_doomscroll(session_duration, scroll_count, app_opens, night_usage, screen_time)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (user_id, risk_score, category, prediction_time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, prediction['risk_score'], prediction['category'], datetime.now().isoformat()))
        conn.commit()
        
        # 7-day projection
        cursor.execute('''
            SELECT risk_score, category FROM predictions 
            WHERE user_id = ? 
            ORDER BY prediction_time DESC 
            LIMIT 10
        ''', (user_id,))
        past_predictions = cursor.fetchall()
        
        if len(past_predictions) <= 1:
            future_risk_score = prediction['risk_score']
        else:
            avg_past_score = sum(row['risk_score'] for row in past_predictions) / len(past_predictions)
            future_risk_score = round((0.6 * avg_past_score) + (0.4 * prediction['risk_score']))
            
        if future_risk_score < 35:
            future_status = "Healthy Usage Forecast"
        elif future_risk_score < 65:
            future_status = "Moderate Risk Forecast"
        else:
            future_status = "High Addiction Risk Forecast"
            
        conn.close()
        
        return jsonify({
            "current_prediction": {
                "category": prediction['category'],
                "risk_score": prediction['risk_score'],
                "probabilities": prediction['probabilities'],
                "model_used": prediction['model_used']
            },
            "future_7_day_projection": {
                "risk_score": future_risk_score,
                "status": future_status
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Prediction failed: {str(e)}"}), 500

@predict_bp.route('/coach', methods=['POST'])
@jwt_required()
def habit_coach():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"message": "User query/message is required."}), 400
        
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are DoomScroll Shield's AI Habit Coach. You help users reduce social media addiction, stop doomscrolling, build focus, and design productive digital habits. Provide concise, actionable, and encouraging suggestions."
                    },
                    {"role": "user", "content": message}
                ],
                max_tokens=250,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            return jsonify({"reply": reply, "source": "openai"}), 200
        except Exception as e:
            # Fallback to local heuristic if API fails (e.g. rate limit, auth)
            pass
            
    # Local smart response system (fallback)
    message_lower = message.lower()
    
    if "reduce" in message_lower or "screen time" in message_lower or "limit" in message_lower:
        reply = (
            "Here is a 3-step plan to reduce screen time:\n\n"
            "1. **Define Screen-Free Zones:** Keep your phone out of the bedroom and dining area.\n"
            "2. **Implement the 20-20-20 Rule:** Every 20 minutes, take a 20-second break to look at something 20 feet away.\n"
            "3. **Use the Scroll Simulator:** Test your limits and observe how quickly risk escalates, then set an app lock for 15 minutes."
        )
    elif "doomscroll" in message_lower or "stop" in message_lower or "scroll" in message_lower:
        reply = (
            "To stop doomscrolling, try these behavioral hacks:\n\n"
            "• **Identify Triggers:** Notice if you scroll when stressed, bored, or tired. Stressed and Tired are high-risk triggers.\n"
            "• **Create Friction:** Put social apps in a hidden folder, or log out after each session.\n"
            "• **Activate Focus Mode:** Switch to breathing exercises or Pomodoro block when you feel the urge to scroll."
        )
    elif "productivity" in message_lower or "plan" in message_lower or "focus" in message_lower:
        reply = (
            "Here is your personalized productivity structure:\n\n"
            "• **Deep Work Blocks:** Work for 50 minutes, then take a 10-minute walk. Block all notifications.\n"
            "• **Pomodoro Cycles:** 25 minutes of pure work, followed by a 5-minute breathing exercise.\n"
            "• **Track Streaks:** Each focused session awards you 20 XP. Aim for the 'Deep Worker' badge!"
        )
    else:
        reply = (
            "Hello! I am your AI Habit Coach. I can help you with:\n\n"
            "• Setting daily screen time limits\n"
            "• Breaking doomscrolling cycles using mindfulness\n"
            "• Activating Focus Mode and breathing techniques\n\n"
            "What would you like to focus on today?"
        )
        
    return jsonify({"reply": reply, "source": "local_coach"}), 200
