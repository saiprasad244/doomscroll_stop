import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from backend.database.connection import get_db_connection
from datetime import datetime, timedelta

def generate_weekly_report(user_id, output_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch user info
    cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    user_name = user['name'] if user else "User"
    
    # Fetch weekly statistics
    cursor.execute('''
        SELECT COALESCE(SUM(session_duration), 0) as total_duration,
               COALESCE(AVG(session_duration), 0) as avg_duration,
               COALESCE(MAX(screen_time), 0) as max_screen,
               COUNT(*) as total_sessions
        FROM usage_logs
        WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-7 days', 'localtime')
    ''', (user_id,))
    logs_stats = cursor.fetchone()
    
    # Fetch average risk score
    cursor.execute('''
        SELECT COALESCE(AVG(risk_score), 0) as avg_risk,
               COUNT(CASE WHEN category = 'Severe' THEN 1 END) as severe_count
        FROM predictions
        WHERE user_id = ? AND DATE(prediction_time) >= DATE('now', '-7 days', 'localtime')
    ''', (user_id,))
    pred_stats = cursor.fetchone()
    
    # Fetch mood counts
    cursor.execute('''
        SELECT mood, COUNT(*) as count 
        FROM mood_logs 
        WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-7 days', 'localtime')
        GROUP BY mood
        ORDER BY count DESC
    ''', (user_id,))
    mood_rows = cursor.fetchall()
    dominant_mood = mood_rows[0]['mood'] if mood_rows else "Unknown"
    
    # Get achievements count
    cursor.execute("SELECT COUNT(*) as count FROM achievements WHERE user_id = ?", (user_id,))
    badges_count = cursor.fetchone()['count']
    
    conn.close()
    
    # PDF setup
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    # Style definitions
    styles = getSampleStyleSheet()
    
    # Custom colors
    primary_color = colors.HexColor("#4F46E5") # Indigo
    secondary_color = colors.HexColor("#06B6D4") # Cyan
    text_color = colors.HexColor("#1F2937") # Gray-800
    bg_light = colors.HexColor("#F9FAFB") # Gray-50
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=6
    )
    
    # 1. Header
    story.append(Paragraph("DoomScroll Shield", title_style))
    story.append(Paragraph(f"Weekly Habit & Digital Well-being Report", ParagraphStyle('Sub', parent=body_style, fontSize=12, leading=16, textColor=secondary_color, spaceAfter=15)))
    story.append(Spacer(1, 0.1 * inch))
    
    # Metadata Block
    meta_data = [
        [Paragraph("<b>Prepared For:</b>", body_style), Paragraph(user_name, body_style)],
        [Paragraph("<b>Date Generated:</b>", body_style), Paragraph(datetime.now().strftime("%B %d, %Y"), body_style)],
        [Paragraph("<b>Reporting Period:</b>", body_style), Paragraph(f"{(datetime.now() - timedelta(days=7)).strftime('%m/%d/%Y')} - {datetime.now().strftime('%m/%d/%Y')}", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[1.5*inch, 4.5*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 0.25 * inch))
    
    # 2. Executive Summary Metrics Table
    story.append(Paragraph("Executive Summary Statistics", h2_style))
    
    total_screen_time_mins = int(logs_stats['total_duration'])
    avg_session_mins = round(logs_stats['avg_duration'], 1)
    avg_risk = round(pred_stats['avg_risk'], 1)
    severe_count = pred_stats['severe_count']
    
    summary_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Target / Benchmarking</b>", body_style)],
        [Paragraph("Weekly Screen Time", body_style), Paragraph(f"{total_screen_time_mins} mins", body_style), Paragraph("< 350 mins (50m/day)", body_style)],
        [Paragraph("Average Session Duration", body_style), Paragraph(f"{avg_session_mins} mins", body_style), Paragraph("< 15 mins per session", body_style)],
        [Paragraph("Average Addiction Risk Score", body_style), Paragraph(f"{avg_risk}%", body_style), Paragraph("< 35% (Healthy)", body_style)],
        [Paragraph("Severe Doomscroll Sessions", body_style), Paragraph(str(severe_count), body_style), Paragraph("0 sessions", body_style)],
        [Paragraph("Dominant Mood Logged", body_style), Paragraph(dominant_mood, body_style), Paragraph("Neutral / Positive", body_style)],
        [Paragraph("Shield Badges Earned", body_style), Paragraph(f"{badges_count} badges", body_style), Paragraph("Earn achievements weekly", body_style)]
    ]
    t_summary = Table(summary_data, colWidths=[2.2*inch, 1.5*inch, 2.3*inch])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
    ]))
    # Adjust top row text color for table header
    for i in range(3):
        summary_data[0][i].style.textColor = colors.white
    
    story.append(t_summary)
    story.append(Spacer(1, 0.25 * inch))
    
    # 3. Clinical Habits Analysis
    story.append(Paragraph("AI Behavioral Insights", h2_style))
    
    # Determine risk level description
    if avg_risk >= 65:
        risk_level = "Severe Addiction Risk"
        risk_desc = "Your usage demonstrates severe doomscrolling behavior. You regularly exceed 30 continuous minutes of social media interaction, which can lead to sleep depletion, anxiety, and screen dependency."
    elif avg_risk >= 35:
        risk_level = "Moderate Addiction Risk"
        risk_desc = "Your usage is moderate but bordering on dependency. You experience occasional severe sessions, especially during specific moods or late at night."
    else:
        risk_level = "Healthy Digital Habits"
        risk_desc = "Excellent work! Your digital habits are healthy. Your sessions are short, screen time is well managed, and you have low vulnerability to doomscrolling."
        
    story.append(Paragraph(f"<b>Overall Diagnosis:</b> {risk_level}", ParagraphStyle('BoldText', parent=body_style, fontName='Helvetica-Bold')))
    story.append(Paragraph(risk_desc, body_style))
    
    # Mood Insights
    if dominant_mood in ["Stressed", "Sad"]:
        mood_insight = f"Our AI correlations show you are highly likely to doomscroll when feeling <b>{dominant_mood}</b>. Using social media as an emotional coping mechanism often reinforces screen dependency."
    elif dominant_mood == "Tired":
        mood_insight = "You tend to scroll when Tired. This often manifests as late-night doomscrolling, which directly degrades sleep architecture."
    else:
        mood_insight = "Your mood logs show positive associations. Keep logging your mood to track behavioral shifts."
        
    story.append(Paragraph(f"<b>Emotional Trigger Analysis:</b>", ParagraphStyle('BoldText2', parent=body_style, fontName='Helvetica-Bold', spaceBefore=5)))
    story.append(Paragraph(mood_insight, body_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # 4. Action Plan / Suggestions
    story.append(Paragraph("Personalized Productivity Plan", h2_style))
    
    suggestions = []
    if total_screen_time_mins > 350:
        suggestions.append("<b>Set a strict App Limit:</b> Configure DoomScroll Shield to remind you after 15 minutes of social scrolling.")
    if severe_count > 2:
        suggestions.append("<b>Utilize Focus Mode:</b> Before opening social media, start a 25-minute Pomodoro focus block to prevent aimless drifting.")
    if dominant_mood in ["Stressed", "Tired"]:
        suggestions.append("<b>Emotional Regulation:</b> When feeling stressed, start the <i>Breathing Exercise</i> in DoomScroll Shield instead of opening apps.")
    
    suggestions.append("<b>Charge Outside Bedroom:</b> Charge your device in another room overnight to eliminate late-night scrolling.")
    suggestions.append("<b>Earn Achievements:</b> Challenge yourself to build a 3-day Focus Streak next week to level up!")
    
    for sug in suggestions:
        story.append(Paragraph(f"• {sug}", bullet_style))
        
    # Build Document
    doc.build(story)
