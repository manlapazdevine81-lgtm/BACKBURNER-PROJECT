from flask import Flask, render_template, request, redirect, flash, session, url_for
import os
import json
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()  

# ------- Supabase Configuration -------
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ------- Wellness Tips & Daily Quotes -------
WELLNESS_TIPS_MOOD = {
    "happy": [
        "😄 Nice!! Keep being happy and share the joy!",
        "🌟 Your positivity is contagious today!",
        "💌 Smile and make someone else’s day better!",
        "🎉 Celebrate the little wins, they matter!",
        "😊 Keep shining—your happiness inspires others!"
    ],
    "sad": [
        "🌈 It’s okay to feel sad. Take a deep breath and relax.",
        "🎵 Listen to your favorite song and let yourself feel.",
        "💛 Remember, small moments of joy can still happen today.",
        "🌿 Even a short walk can lift your spirits.",
        "🕊️ Be kind to yourself today; you’re doing your best."
    ],
    "stressed": [
        "🧘 Take a 5-minute break and breathe deeply.",
        "💧 Hydrate and stretch—your body will thank you!",
        "🌿 Focus on one small task at a time.",
        "⚡ Remember: pausing is productive too!",
        "🌸 Clear your mind with a few slow breaths."
    ],
    "tired": [
        "😴 A short rest can recharge your energy.",
        "☕ Have a warm drink and relax for a few minutes.",
        "🛋️ Light stretching might help you feel awake.",
        "🌙 Take it easy—you’ve earned a little break.",
        "💤 Close your eyes for a moment and refresh your mind."
    ],
    "anxious": [
        "🌸 Breathe in slowly and exhale calmly.",
        "📋 Focus on one thing you can control right now.",
        "💖 You are safe, and this feeling will pass.",
        "🕊️ Ground yourself: notice five things around you.",
        "🌿 Remind yourself: you’ve handled challenges before, you can handle this too."
    ]
}

DAILY_QUOTES = [
    "🌞 Every day is a fresh start.",
    "🚶 Small steps lead to big changes.",
    "💪 You are stronger than you think.",
    "💖 Your feelings are valid.",
    "🏆 Progress, not perfection."
]

# ------------------ App Configuration ------------------
app = Flask(__name__)
app.secret_key = "kalma_secret_key"

# ------------------ Database Configuration ------------------
DB_HOST = os.environ.get('DB_HOST',)
DB_NAME = os.environ.get('DB_NAME',)
DB_USER = os.environ.get('DB_USER',)
DB_PASS = os.environ.get('DB_PASS',)

# ------------------ Calendar Events File ------------------
EVENTS_FILE = os.path.join(os.path.dirname(__file__), "events.json")

# ------------------ Calendar Helpers ----------------------
def load_events():
    """Loads events from the JSON file."""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_event(date, title, desc):
    """Saves an event to the JSON file."""
    events = load_events()
    if date not in events:
        events[date] = []
    events[date].append({"title": title, "description": desc})
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=4)

# ------------------ Database Helpers (Supabase REST API) ------------------
def supabase_request(method, table, data=None, filters=None):
    """Make a request to Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {}
    if filters:
        for key, op, value in filters:
            params[key] = f"{op}.{value}"
    
    if method == "GET":
        r = requests.get(url, headers=HEADERS, params=params)
    elif method == "POST":
        r = requests.post(url, headers=HEADERS, json=data)
    elif method == "PATCH":
        r = requests.patch(url, headers=HEADERS, json=data, params=params)
    elif method == "DELETE":
        r = requests.delete(url, headers=HEADERS, params=params)
    
    if r.status_code >= 400:
        app.logger.error(f"Supabase API Error: {r.status_code} - {r.text}")
        return None
    
    return r.json() if r.text else None

def init_db():
    """Initialize tables via Supabase (create if not exists)."""
    # Try to create users table - check if exists first
    users = supabase_request("GET", "users", filters=[("email", "eq", "init_check")])
    if users is None:
        app.logger.info("Tables need to be created in Supabase dashboard")
    app.logger.info("Supabase connection ready.")

def get_user_by_email(email):
    """Fetches a single user record."""
    result = supabase_request("GET", "users", filters=[("email", "eq", email)])
    return result[0] if result else None

def create_user(fullname, email, password_plain):
    """Inserts a new user into the database."""
    hashed = generate_password_hash(password_plain)
    supabase_request("POST", "users", data={
        "fullname": fullname,
        "email": email,
        "password": hashed
    })

def check_credentials(email, password_plain):
    """Checks user password against the stored hash."""
    user = get_user_by_email(email)
    if not user:
        return False
    return check_password_hash(user["password"], password_plain)

def add_task_for_user(email, name, category, due_date):
    """Adds a new task for a specified user email."""
    supabase_request("POST", "tasks", data={
        "user_email": email,
        "name": name,
        "category": category,
        "due_date": due_date,
        "completed": False
    })

def get_tasks_for_user(email):
    """Retrieves all tasks for a specific user."""
    result = supabase_request("GET", "tasks", filters=[("user_email", "eq", email)])
    return result if result else []

def set_task_completed(task_id):
    """Marks a specific task as completed."""
    supabase_request("PATCH", "tasks", data={"completed": True}, filters=[("id", "eq", task_id)])

def delete_task_by_id(task_id):
    """Deletes a task by its ID."""
    supabase_request("DELETE", "tasks", filters=[("id", "eq", task_id)])

# Initialize database tables
init_db()

# ------------------ Routes ------------------
@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not fullname or not email or not password:
            flash("Please fill all required fields.")
            return redirect(url_for('register'))

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for('register'))

        if get_user_by_email(email):
            flash("Email already registered. Please login.")
            return redirect(url_for('login'))

        create_user(fullname, email, password)
        flash("Registration successful. Please login.")
        return redirect(url_for('login'))

    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if check_credentials(email, password):
            session['user'] = email
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.")
            return redirect(url_for('login'))

    return render_template('login.html', title='Login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_row = get_user_by_email(session['user'])
    fullname = user_row['fullname'] if user_row else session['user']
    return render_template(
        'dashboard.html', 
        title='Dashboard', 
        user=fullname,
        moods=list(WELLNESS_TIPS_MOOD.keys()),
        tips=WELLNESS_TIPS_MOOD,
        quotes=DAILY_QUOTES
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_email = session['user']

    if request.method == 'POST':
        task_name = request.form.get('task', '').strip()
        category = request.form.get('category', 'Personal')
        due_date = request.form.get('due_date', '').strip()
        if task_name:
            add_task_for_user(user_email, task_name, category, due_date)
            flash("Task added successfully!")
        return redirect(url_for('profile'))

    tasks = get_tasks_for_user(user_email)
    
    # NEW LOGIC: Calculate completed and pending tasks for the chart
    completed_tasks = sum(1 for t in tasks if t['completed'] == 1)
    pending_tasks = len(tasks) - completed_tasks
    
    return render_template(
        'profile.html', 
        title='Profile', 
        user=user_email, 
        tasks=tasks,
        # PASS THE NEW VARIABLES TO THE TEMPLATE
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )


@app.route('/wellness')
def wellness():
    return render_template(
        'wellness.html',
        moods=list(WELLNESS_TIPS_MOOD.keys()),
        tips=WELLNESS_TIPS_MOOD,
        quotes=DAILY_QUOTES
    )

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    set_task_completed(task_id)
    flash("Task marked as completed!")
    return redirect(url_for('profile'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    delete_task_by_id(task_id)
    flash("Task deleted successfully!")
    return redirect(url_for('profile'))

@app.route("/calendar")
def calendar():
    events = load_events()
    return render_template("calendar.html", events=load_events())


@app.route("/add_event", methods=["POST"])
def add_event():
    date = request.form["event_date"]
    title = request.form["event_title"]
    desc = request.form["event_description"]

    save_event(date, title, desc)

    return redirect(url_for("calendar"))

@app.route("/delete_event/<date>/<int:index>", methods=["POST"])
def delete_event(date, index):
    events = load_events()
    if date in events and 0 <= index < len(events[date]):
        events[date].pop(index)
        if len(events[date]) == 0:
            del events[date]
        with open(EVENTS_FILE, "w") as f:
            json.dump(events, f, indent=4)
    return ("", 204) 

@app.route('/simplegame')
def simplegame():
    return render_template('simplegame.html')

@app.route("/bubble")
def bubble():
    return render_template("bubble.html")

@app.route("/numbers")
def numbers():
    return render_template("numbers.html")

@app.route("/memory")
def memory():
    return render_template("memory.html")


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
