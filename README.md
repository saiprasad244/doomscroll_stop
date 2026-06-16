# DoomScroll Shield 🛡️

DoomScroll Shield is a complete, production-ready full-stack application designed to help users combat doomscrolling and social media addiction. It monitors screen usage, scroll gestures, and daily mood, classifies sessions using a custom pure-Python Machine Learning pipeline (XGBoost Analogue, Random Forest, Logistic Regression), offers real-time interventions, hosts an AI Habit Coach, and provides gamified achievements.

---

## 🚀 Key Features

*   **AI Doomscroll Detection:** Detects excessive scrolling behaviors in real-time. Predicts **Healthy**, **Risky**, or **Severe Doomscrolling** with visual risk scores.
*   **Machine Learning Comparison:** Compares three classifiers (XGBoost Analogue, Random Forest, and Multiclass Logistic Regression) on accuracy, precision, recall, and F1 score, displaying comparisons in the dashboard.
*   **Smart Interventions:** Full-screen glassmorphic warnings prompt users to take a 5-minute break or switch to Focus Mode when severe scrolling patterns are detected.
*   **Focus Mode:** Integrated Pomodoro and Deep Work timers, simulated content blockers for distracting apps, and an interactive Breathing Exercise (4-4-4 rhythm) to ease impulses.
*   **AI Habit Coach:** Exposes a chat interface utilizing the OpenAI API to formulate custom schedules. Falls back to a local keyword-based heuristic advisor if no API key is present.
*   **Gamification & Streaks:** Tracks user levels, XP points, active usage logging streaks, and achievements (e.g. *Shield Activated*, *Mindful Scroller*, *Deep Worker*).
*   **Leaderboard:** Compares and ranks users based on active streaks and total XP. Comes pre-seeded with competitive synthetic users (*Alice Vance*, *Brad Pitt*, *Charlie Day*).
*   **Weekly PDF Wellbeing Reports:** Dynamically aggregates logs to construct a professional PDF report (using `reportlab`) detailing screen time summaries, mood associations, and personalized suggestions.

---

## 🛠️ Technology Stack

*   **Frontend:** React.js (Vite), Tailwind CSS (v3 with PostCSS), Lucide React Icons, Chart.js (`react-chartjs-2`).
*   **Backend:** Python Flask, Flask-JWT-Extended, SQLite (zero-config, portable database).
*   **AI/ML Pipeline:** Custom pure-Python implementations of Logistic Regression, Decision Trees, Random Forests, and Gradient Boosting Decision Trees (XGBoost analogue) ensuring 100% compilation-free execution on modern environments (e.g. Python 3.14 on Windows).

---

## 📁 Project Structure

```
doomscroll-stop/
├── backend/
│   ├── app.py                      # Flask main application initialization
│   ├── database/
│   │   └── connection.py           # SQLite manager, schemas, & PBKDF2 cryptography
│   ├── ml/
│   │   ├── pipeline.py             # Custom training pipeline & evaluation metrics
│   │   └── model_loader.py         # JSON-based model deserializer & inference engine
│   ├── models/
│   │   └── db_models.py            # SQLite helper wrappers (implicit models)
│   ├── routes/
│   │   ├── auth.py                 # POST /register, /login
│   │   ├── usage.py                # POST /usage logging
│   │   ├── predict.py              # POST /predict, /coach
│   │   ├── dashboard.py            # GET /dashboard
│   │   ├── achievements.py         # GET /achievements
│   │   ├── focus.py                # POST /focus-mode
│   │   ├── mood.py                 # POST /mood, GET /mood/correlation
│   │   ├── reports.py              # GET /reports/weekly (PDF Stream)
│   │   └── leaderboard.py          # GET /leaderboard
│   └── utils/
│       ├── jwt_helper.py
│       └── pdf_helper.py           # reportlab PDF template builder
├── dataset/
│   ├── generate_data.py            # Generates 1000+ synthetic session records
│   └── doomscroll_dataset.csv      # Output training data
├── saved_models/
│   ├── best_model.json             # Serialized best-model parameters (JSON)
│   └── model_comparison.json       # Metrics for all 3 models (JSON)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   └── AuthPage.jsx    # Login / Register forms
│   │   │   └── InterventionModal.jsx # Warning popup modal
│   │   ├── hooks/
│   │   │   ├── useScrollTracker.js # Scroll listeners and simulators
│   │   │   └── useTheme.js         # Light / Dark mode management
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx       # Charts, mood tracker, and scroll simulator
│   │   │   ├── FocusMode.jsx       # Pomodoro clock & Breathing circles
│   │   │   ├── HabitCoach.jsx      # AI Coach conversational interface
│   │   │   └── Leaderboard.jsx     # Badges grid, download report PDF button
│   │   ├── App.jsx                 # App shell navigation
│   │   └── main.jsx                # DOM mounter
│   ├── tailwind.config.js          # Tailwind configure directives
│   └── package.json
├── requirements.txt                # Python backend dependencies
└── README.md
```

---

## ⚡ Setup & Local Run Instructions

### 1. Backend Setup

1.  **Clone or navigate** to the workspace directory:
    ```bash
    cd doomscroll_stop
    ```
2.  **Install Python requirements**:
    ```bash
    python -m pip install -r requirements.txt
    ```
3.  *(Optional)* **Set OpenAI API Key** for the AI Habit Coach:
    *   **Windows (PowerShell)**:
        ```powershell
        $env:OPENAI_API_KEY="your_api_key_here"
        ```
    *   **Mac/Linux**:
        ```bash
        export OPENAI_API_KEY="your_api_key_here"
        ```
4.  **Run the ML training pipeline** (trains models, exports comparisons, saves best model):
    ```bash
    python backend/ml/pipeline.py
    ```
5.  **Run the Flask Server** (activates DB tables, feeds synthetic rankings, listens on port 5000):
    *   **Windows (PowerShell)**:
        ```powershell
        $env:PYTHONPATH="."
        python backend/app.py
        ```
    *   **Mac/Linux**:
        ```bash
        export PYTHONPATH="."
        python backend/app.py
        ```

### 2. Frontend Setup

1.  **Navigate to the frontend folder**:
    ```bash
    cd frontend
    ```
2.  **Install npm packages**:
    ```bash
    npm install
    ```
3.  **Start the React Vite Development Server**:
    ```bash
    npm run dev
    ```
4.  Open the web app in your browser (typically `http://localhost:5173`).

---

## 🏁 How to Verify & Demo the App

1.  **Authenticate**: Register a new user account on the login page.
2.  **Leaderboard Competitors**: Navigate to the **Streaks & Badges** tab. Notice the pre-seeded users (*Alice*, *Brad*, *Charlie*) ranked on the competitive board.
3.  **Scroll Simulator**:
    *   On the **Dashboard**, find the **Live Doomscrolling Simulator** card.
    *   Click **+30 mins** and **+120 scrolls** to increment your session variables.
    *   Toggle **Night Session** check.
    *   Click **Trigger AI Classification Check**.
    *   Our XGBoost / Random Forest classifier runs instantly. The risk gauge changes to **Severe (e.g. 93%)** and the glassmorphic **Intervention Warning Modal** will immediately slide down overlaying the screen.
4.  **Try Focus Mode**:
    *   On the popup warning, click **Start Focus Mode**.
    *   The app redirects you to the **Focus Mode** page.
    *   Toggle the app blockers, start a Pomodoro clock, or engage in the **Breathing Exercise** to watch the animated circle expand/contract.
5.  **Daily Mood Log**:
    *   Go back to the **Dashboard**. Click a mood button (e.g. *Stressed*).
    *   The database records your mood and aggregates the correlation chart in real-time.
6.  **AI Habit Coach**:
    *   Go to the **AI Habit Coach** tab. Ask a digital wellbeing question or click a quick prompt like *"How can I stop doomscrolling?"*.
    *   The Coach provides dynamic suggestions.
7.  **PDF Compilation**:
    *   Go to the **Streaks & Badges** tab.
    *   Click **Download Report (PDF)**.
    *   The server compiles your session metrics, risk scores, mood triggers, and outputs a professional PDF document.

---
