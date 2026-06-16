import os
import csv
import random

def generate_synthetic_dataset(output_path, num_samples=1000):
    # Set seed for reproducibility
    random.seed(42)
    
    headers = ['session_duration', 'scroll_count', 'app_opens', 'night_usage', 'screen_time', 'risk_category']
    rows = []
    
    for _ in range(num_samples):
        # Session duration: 1.0 to 120.0 minutes
        # We model this using a skewed distribution: exponential-like or basic random ranges
        if random.random() < 0.7:
            session_duration = round(random.uniform(1.0, 30.0), 1)
        else:
            session_duration = round(random.uniform(30.0, 120.0), 1)
            
        # Scroll count: correlated with session duration (avg 4 to 8 scrolls/min)
        scroll_rate = random.uniform(3.0, 9.0)
        scroll_count = int(session_duration * scroll_rate) + random.randint(5, 40)
        
        # App opens: 1 to 60 times a day
        if random.random() < 0.6:
            app_opens = random.randint(1, 15)
        else:
            app_opens = random.randint(16, 60)
            
        # Night usage: binary (0 or 1)
        # Probability of night usage is higher for longer sessions
        night_prob = 0.2 if session_duration < 20 else (0.6 if session_duration < 45 else 0.85)
        night_usage = 1 if random.random() < night_prob else 0
        
        # Screen time: total daily screen time in minutes (must be >= session_duration)
        min_screen_time = int(session_duration) + 15
        if app_opens < 15:
            screen_time = min_screen_time + random.randint(15, 180)
        else:
            screen_time = min_screen_time + random.randint(180, 600)
        screen_time = min(screen_time, 720)
        
        # Determine the target class: Healthy, Risky, Severe
        # Rule-based calculation with noise
        score = 0
        if session_duration > 30:
            score += 25
        if scroll_count > 100:
            score += 25
        if app_opens > 20:
            score += 15
        if night_usage == 1:
            score += 10
        if screen_time > 240:
            score += 15
            
        # Add linear factors
        score += (session_duration * 0.3) + (scroll_count * 0.05) + (app_opens * 0.4) + (screen_time * 0.02)
        # Add random noise (-10 to 10)
        score += random.uniform(-10.0, 10.0)
        
        if score < 35:
            category = "Healthy"
        elif score < 65:
            category = "Risky"
        else:
            category = "Severe"
            
        rows.append([session_duration, scroll_count, app_opens, night_usage, screen_time, category])
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print(f"Generated synthetic dataset with {num_samples} samples at {output_path}")
    
    # Simple count check
    counts = {}
    for r in rows:
        cat = r[-1]
        counts[cat] = counts.get(cat, 0) + 1
    print("Class counts:", counts)

if __name__ == '__main__':
    generate_synthetic_dataset('dataset/doomscroll_dataset.csv', 1200)
