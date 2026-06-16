import os
import sqlite3
import hashlib
import binascii
from datetime import datetime, timedelta

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'doomscroll_shield.db'))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Usage Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            app_name TEXT NOT NULL,
            session_duration REAL NOT NULL, -- in minutes
            scroll_count INTEGER NOT NULL,
            screen_time INTEGER NOT NULL,     -- daily total screen time in minutes
            app_opens INTEGER NOT NULL,       -- daily count of app openings
            night_usage INTEGER DEFAULT 0,    -- 0 or 1
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            risk_score REAL NOT NULL,
            category TEXT NOT NULL,
            prediction_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_name TEXT NOT NULL,
            date_earned DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, badge_name)
        )
    ''')
    
    # Create Mood Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL, -- Happy, Sad, Stressed, Tired
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Check if table is empty to perform competitive seeding
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()['count'] == 0:
        print("Empty database detected. Seeding competitive leaderboard users...")
        hp = hash_password("password123")
        
        # 1. Alice Vance
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", ("Alice Vance", "alice@example.com", hp))
        u1_id = cursor.lastrowid
        # Alice has 9 consecutive days of healthy logging
        for i in range(9):
            log_time = (datetime.now() - timedelta(days=i)).isoformat()
            cursor.execute('''
                INSERT INTO usage_logs (user_id, app_name, session_duration, scroll_count, screen_time, app_opens, night_usage, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (u1_id, "Instagram", 12.0, 45, 120, 10, 0, log_time))
            cursor.execute('''
                INSERT INTO predictions (user_id, risk_score, category, prediction_time)
                VALUES (?, ?, ?, ?)
            ''', (u1_id, 20.0, "Healthy", log_time))
        cursor.execute("INSERT INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)", (u1_id, "Shield Activated", (datetime.now() - timedelta(days=8)).isoformat()))
        cursor.execute("INSERT INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)", (u1_id, "3 Days Focus Streak", (datetime.now() - timedelta(days=6)).isoformat()))
        cursor.execute("INSERT INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)", (u1_id, "7 Days Healthy Usage", (datetime.now() - timedelta(days=2)).isoformat()))

        # 2. Brad Pitt
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", ("Brad Pitt", "brad@example.com", hp))
        u2_id = cursor.lastrowid
        # Brad has 6 consecutive days of moderate logging
        for i in range(6):
            log_time = (datetime.now() - timedelta(days=i)).isoformat()
            cursor.execute('''
                INSERT INTO usage_logs (user_id, app_name, session_duration, scroll_count, screen_time, app_opens, night_usage, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (u2_id, "TikTok", 18.0, 80, 190, 15, 0, log_time))
            cursor.execute('''
                INSERT INTO predictions (user_id, risk_score, category, prediction_time)
                VALUES (?, ?, ?, ?)
            ''', (u2_id, 45.0, "Risky", log_time))
        cursor.execute("INSERT INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)", (u2_id, "Shield Activated", (datetime.now() - timedelta(days=5)).isoformat()))
        cursor.execute("INSERT INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)", (u2_id, "3 Days Focus Streak", (datetime.now() - timedelta(days=3)).isoformat()))

        # 3. Charlie Day
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", ("Charlie Day", "charlie@example.com", hp))
        u3_id = cursor.lastrowid
        # Charlie has 2 consecutive days of severe logging
        for i in range(2):
            log_time = (datetime.now() - timedelta(days=i)).isoformat()
            cursor.execute('''
                INSERT INTO usage_logs (user_id, app_name, session_duration, scroll_count, screen_time, app_opens, night_usage, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (u3_id, "Twitter", 40.0, 210, 310, 22, 1, log_time))
            cursor.execute('''
                INSERT INTO predictions (user_id, risk_score, category, prediction_time)
                VALUES (?, ?, ?, ?)
            ''', (u3_id, 85.0, "Severe", log_time))
        cursor.execute("INSERT INTO achievements (user_id, badge_name, date_earned) VALUES (?, ?, ?)", (u3_id, "Shield Activated", (datetime.now() - timedelta(days=1)).isoformat()))
        
    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

# ==========================================
# PASSWORD HASHING UTIL (PBKDF2)
# ==========================================

def hash_password(password: str) -> str:
    """Hash a password for storing in the database."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against a provided password."""
    salt = stored_password[:64].encode('ascii')
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_hash
