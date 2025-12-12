-- ---------- USERS TABLE ----------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    fullname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- ---------- TASKS TABLE ----------
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    due_date TEXT,
    completed INTEGER DEFAULT 0,
    FOREIGN KEY (user_email) REFERENCES users(email)
);