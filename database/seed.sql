-- Users Table --
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE
);

INSERT INTO users (name, email, role) VALUES
('Juan Dela Cruz', 'juan@example.com', 'Student'),
('Maria Santos', 'maria@example.com', 'Student'),
('Pedro Reyes', 'pedro@example.com', 'Student'),
('Ana Lopez', 'ana@example.com', 'Teacher'),
('Luis Garcia', 'luis@example.com', 'Teacher'),
('Cathy Ramos', 'cathy@example.com', 'Student'),
('Mark Villanueva', 'mark@example.com', 'Student'),
('Ella Cruz', 'ella@example.com', 'Student'),
('John Paul', 'john@example.com', 'Teacher'),
('Grace Lim', 'grace@example.com', 'Student'),
('Rico Tan', 'rico@example.com', 'Student'),
('Lara Mae', 'lara@example.com', 'Student'),
('Kevin Ong', 'kevin@example.com', 'Student'),
('Joy Bautista', 'joy@example.com', 'Teacher'),
('Nico Santos', 'nico@example.com', 'Student'),
('Tina Lopez', 'tina@example.com', 'Student'),
('Carlo Reyes', 'carlo@example.com', 'Student'),
('Vina Dela Cruz', 'vina@example.com', 'Teacher'),
('Marco Tan', 'marco@example.com', 'Student'),
('Ella Mae', 'ellamae@example.com', 'Student');

-- Tasks Table --
CREATE TABLE IF NOT EXISTS tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    user_id INT,
    due_date DATE,
    status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO tasks (title, description, user_id, due_date, status) VALUES
('Finish Project Proposal', 'Complete the proposal for submission', 1, '2025-12-15', 'Pending'),
('Submit Assignment', 'Math assignment due', 2, '2025-12-12', 'Completed'),
('Prepare Presentation', 'Prepare slides for group presentation', 3, '2025-12-14', 'Pending'),
('Grade Exams', 'Grade student exams', 4, '2025-12-13', 'In Progress'),
('Research Topic', 'Research for final paper', 5, '2025-12-18', 'Pending'),
('Team Meeting', 'Discuss project updates', 6, '2025-12-10', 'Completed'),
('Update Database', 'Update records in system', 7, '2025-12-16', 'Pending'),
('Fix Bug', 'Resolve issue in app', 8, '2025-12-11', 'In Progress'),
('Design Logo', 'Create logo for project', 9, '2025-12-20', 'Pending'),
('Plan Event', 'Plan student event', 10, '2025-12-19', 'Pending'),
('Write Report', 'Complete report for project', 11, '2025-12-14', 'Completed'),
('Submit Exam Scores', 'Upload scores to portal', 12, '2025-12-12', 'Pending'),
('Prepare Quiz', 'Create quiz questions', 13, '2025-12-13', 'Pending'),
('Organize Files', 'Organize project files', 14, '2025-12-15', 'Completed'),
('Create Tutorial', 'Make tutorial video', 15, '2025-12-17', 'Pending'),
('Update Website', 'Update content on website', 16, '2025-12-16', 'In Progress'),
('Send Emails', 'Send reminder emails', 17, '2025-12-18', 'Pending'),
('Design Banner', 'Banner for school event', 18, '2025-12-19', 'Pending'),
('Record Video', 'Record instructional video', 19, '2025-12-20', 'Pending'),
('Prepare Survey', 'Survey for students', 20, '2025-12-21', 'Pending');

-- Courses Table -- 
CREATE TABLE IF NOT EXISTS courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(50) NOT NULL,
    instructor VARCHAR(50),
    start_date DATE,
    end_date DATE
);

INSERT INTO courses (course_name, instructor, start_date, end_date) VALUES
('Programming 101', 'Ana Lopez', '2025-09-01', '2025-12-15'),
('Math 101', 'Luis Garcia', '2025-09-01', '2025-12-15'),
('English 101', 'John Paul', '2025-09-01', '2025-12-15'),
('Science 101', 'Joy Bautista', '2025-09-01', '2025-12-15'),
('History 101', 'Vina Dela Cruz', '2025-09-01', '2025-12-15'),
('Art 101', 'Ana Lopez', '2025-09-01', '2025-12-15'),
('Music 101', 'Luis Garcia', '2025-09-01', '2025-12-15'),
('PE 101', 'John Paul', '2025-09-01', '2025-12-15'),
('IT 101', 'Joy Bautista', '2025-09-01', '2025-12-15'),
('Filipino 101', 'Vina Dela Cruz', '2025-09-01', '2025-12-15'),
('Economics 101', 'Ana Lopez', '2025-09-01', '2025-12-15'),
('Psychology 101', 'Luis Garcia', '2025-09-01', '2025-12-15'),
('Sociology 101', 'John Paul', '2025-09-01', '2025-12-15'),
('Philosophy 101', 'Joy Bautista', '2025-09-01', '2025-12-15'),
('Marketing 101', 'Vina Dela Cruz', '2025-09-01', '2025-12-15'),
('Finance 101', 'Ana Lopez', '2025-09-01', '2025-12-15'),
('Law 101', 'Luis Garcia', '2025-09-01', '2025-12-15'),
('Engineering 101', 'John Paul', '2025-09-01', '2025-12-15'),
('Design 101', 'Joy Bautista', '2025-09-01', '2025-12-15'),
('Statistics 101', 'Vina Dela Cruz', '2025-09-01', '2025-12-15');