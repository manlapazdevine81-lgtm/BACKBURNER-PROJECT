# app.py
from flask import Flask, render_template, request, redirect, flash, session, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "kalma_secret_key"

# Path to DB file next to app.py
BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, "users.db")

# ------- RESET DB (you chose RESET) -------
# This will remove existing users.db and create a fresh one when the app starts.
if os.path.exists(DATABASE):
    try:
        os.remove(DATABASE)
        app.logger.info("Removed old database (reset requested).")
    except Exception as e:
        app.logger.warning("Could not remove old database: %s", e)

# ------- DB helpers -------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    # users table + tasks table (persistent tasks)
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY(user_email) REFERENCES users(email)
        )
    ''')
    db.commit()
    db.close()

def get_user_by_email(email):
    db = get_db()
    try:
        return db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        db.close()

def create_user(fullname, email, password_plain):
    hashed = generate_password_hash(password_plain)
    db = get_db()
    try:
        db.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",
                   (fullname, email, hashed))
        db.commit()
    finally:
        db.close()

def check_credentials(email, password_plain):
    user = get_user_by_email(email)
    if not user:
        return False
    return check_password_hash(user["password"], password_plain)

def add_task_for_user(email, name, category, due_date):
    db = get_db()
    try:
        db.execute("INSERT INTO tasks (user_email, name, category, due_date, completed) VALUES (?, ?, ?, ?, 0)",
                   (email, name, category, due_date))
        db.commit()
    finally:
        db.close()

def get_tasks_for_user(email):
    db = get_db()
    try:
        rows = db.execute("SELECT * FROM tasks WHERE user_email = ? ORDER BY id DESC", (email,)).fetchall()
        return rows
    finally:
        db.close()

def set_task_completed(task_id):
    db = get_db()
    try:
        db.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        db.commit()
    finally:
        db.close()

def delete_task_by_id(task_id):
    db = get_db()
    try:
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
    finally:
        db.close()

# initialize new DB
init_db()

# ------- Routes -------
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
    return render_template('profile.html', title='Profile', user=user_email, tasks=tasks)

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

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
