from flask import Flask, render_template, request, redirect, flash, session, url_for
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

# Import Psycopg2 for PostgreSQL
import psycopg2 
from psycopg2 import extras # Used for dictionary-like rows

app = Flask(__name__)
app.secret_key = "kalma_secret_key"

# ------- Database Configuration for PostgreSQL -------
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'postgres')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'cutemochie')
# The SQLite database path is no longer needed
# BASE_DIR = os.path.dirname(__file__)
# DATABASE = os.path.join(BASE_DIR, "users.db")

# Removed the dangerous SQLite file removal logic:
# if os.path.exists(DATABASE): ...

# ------- Events File Configuration -------
EVENTS_FILE = os.path.join(os.path.dirname(__file__), "events.json")

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

# ------- DB helpers (Updated for PostgreSQL) -------
# ------- DB helpers (Updated for PostgreSQL) -------

def get_db_conn():
    """Establishes a connection to the PostgreSQL database."""
    try:
        # Use connection string or individual parameters
        conn = psycopg2.connect(
            host=DB_HOST, 
            database=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS
        )
        return conn
    except psycopg2.Error as e:
        app.logger.error("Could not connect to PostgreSQL: %s", e)
        # Re-raise the exception to inform the caller
        raise

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """A generic helper to execute a query, handling connection/cursor."""
    conn = None
    result = None
    try:
        conn = get_db_conn()
        # Use DictCursor for dictionary-like rows, similar to sqlite3.Row
        cur = conn.cursor(cursor_factory=extras.DictCursor) 
        cur.execute(query, params)

        if commit:
            conn.commit()
        
        if fetch_one:
            result = cur.fetchone()
        
        if fetch_all:
            result = cur.fetchall()
            
        cur.close()
        return result

    except psycopg2.Error as e:
        app.logger.error("DB Error: %s in query: %s with params: %s", e, query, params)
        if conn:
            conn.rollback() # Rollback on error
        # In a real application, you might want to return None/False on failure
        # or handle the exception more gracefully.
        raise 
    finally:
        if conn:
            conn.close()

def init_db():
    """Initializes the users and tasks tables using PostgreSQL syntax (SERIAL PK)."""
    # Create users table
    execute_query('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''', commit=True)
    # Create tasks table
    execute_query('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY(user_email) REFERENCES users(email)
        )
    ''', commit=True)
    app.logger.info("PostgreSQL tables checked/created.")

def get_user_by_email(email):
    """Fetches a single user record."""
    # Note the use of %s placeholder for PostgreSQL
    return execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch_one=True)

def create_user(fullname, email, password_plain):
    """Inserts a new user into the database."""
    hashed = generate_password_hash(password_plain)
    execute_query("INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)",
                   (fullname, email, hashed), commit=True)

def check_credentials(email, password_plain):
    """Checks user password against the stored hash."""
    user = get_user_by_email(email)
    if not user:
        return False
    # Psycopg2 DictCursor rows allow dictionary-like access
    return check_password_hash(user["password"], password_plain)

def add_task_for_user(email, name, category, due_date):
    """Adds a new task for a specified user email."""
    execute_query("INSERT INTO tasks (user_email, name, category, due_date, completed) VALUES (%s, %s, %s, %s, 0)",
                   (email, name, category, due_date), commit=True)

def get_tasks_for_user(email):
    """Retrieves all tasks for a specific user."""
    return execute_query("SELECT * FROM tasks WHERE user_email = %s ORDER BY id DESC", (email,), fetch_all=True)

def set_task_completed(task_id):
    """Marks a specific task as completed."""
    execute_query("UPDATE tasks SET completed = 1 WHERE id = %s", (task_id,), commit=True)

def delete_task_by_id(task_id):
    """Deletes a task by its ID."""
    execute_query("DELETE FROM tasks WHERE id = %s", (task_id,), commit=True)

# Initialize new DB (will create tables if they don't exist)
init_db()

# ------- Routes (No changes needed as they rely on updated DB helpers) -------
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
    return render_template('dashboard.html', title='Dashboard', user=fullname)

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

@app.route('/complete_task/<int:task_id>')
# ... (rest of app.py)

@app.route('/wellness')
def wellness():
    return render_template('wellness.html')

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

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
