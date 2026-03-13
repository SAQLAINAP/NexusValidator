-- ============================================================
-- NexusValidator – Academic Database (SQLite)
-- 12 tables, ~330 rows of sample data
-- Idempotent: safe to re-run (DROP TABLE IF EXISTS at top)
-- ============================================================

-- Drop tables in reverse dependency order for idempotent re-runs
DROP TABLE IF EXISTS BookLoan;
DROP TABLE IF EXISTS LibraryBook;
DROP TABLE IF EXISTS LabEquipment;
DROP TABLE IF EXISTS Submission;
DROP TABLE IF EXISTS Assignment;
DROP TABLE IF EXISTS Faculty;
DROP TABLE IF EXISTS Department;
DROP TABLE IF EXISTS Timetable;
DROP TABLE IF EXISTS Marks;
DROP TABLE IF EXISTS Subjects;
DROP TABLE IF EXISTS Semester;
DROP TABLE IF EXISTS Student;

-- ============================================================
-- Original 5 tables
-- ============================================================

CREATE TABLE Student (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    email VARCHAR(100),
    year INT CHECK (year BETWEEN 1 AND 4),
    semester INT CHECK (semester BETWEEN 1 AND 8),
    department VARCHAR(50)
);

CREATE TABLE Semester (
    semester_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INT CHECK (year BETWEEN 1 AND 4),
    semester INT CHECK (semester BETWEEN 1 AND 8),
    start_date DATE,
    end_date DATE
);

CREATE TABLE Subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    semester_id INT REFERENCES Semester(semester_id),
    credits INT
);

CREATE TABLE Marks (
    mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT REFERENCES Student(student_id),
    subject_id INT REFERENCES Subjects(subject_id),
    marks INT,
    grade CHAR(2),
    semester_id INT REFERENCES Semester(semester_id)
);

CREATE TABLE Timetable (
    timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INT REFERENCES Semester(semester_id),
    day VARCHAR(10),
    time TIME,
    subject_id INT REFERENCES Subjects(subject_id),
    room VARCHAR(20)
);

-- ============================================================
-- 7 new tables
-- ============================================================

CREATE TABLE Department (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    head_of_department VARCHAR(100),
    established_year INT
);

CREATE TABLE Faculty (
    faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    department VARCHAR(10) REFERENCES Department(code),
    designation VARCHAR(50),
    subject_id INT REFERENCES Subjects(subject_id)
);

CREATE TABLE Assignment (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    subject_id INT REFERENCES Subjects(subject_id),
    semester_id INT REFERENCES Semester(semester_id),
    type VARCHAR(20) CHECK (type IN ('homework', 'project', 'lab')),
    max_marks INT,
    due_date DATE
);

CREATE TABLE Submission (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT REFERENCES Student(student_id),
    assignment_id INT REFERENCES Assignment(assignment_id),
    submitted_date DATE,
    marks_obtained INT,
    status VARCHAR(20) CHECK (status IN ('on_time', 'late', 'missing'))
);

CREATE TABLE LibraryBook (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    isbn VARCHAR(20),
    department VARCHAR(10),
    copies_total INT,
    copies_available INT
);

CREATE TABLE BookLoan (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INT REFERENCES Student(student_id),
    book_id INT REFERENCES LibraryBook(book_id),
    borrow_date DATE,
    due_date DATE,
    return_date DATE,
    status VARCHAR(20) CHECK (status IN ('active', 'returned', 'overdue'))
);

CREATE TABLE LabEquipment (
    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(10),
    lab_room VARCHAR(20),
    quantity INT,
    status VARCHAR(20) CHECK (status IN ('available', 'in_use', 'maintenance'))
);

-- ============================================================
-- Sample data — original 5 tables (unchanged)
-- ============================================================

INSERT INTO Student (name, email, year, semester, department)
VALUES
    ('Alice', 'alice@dsc.edu', 1, 1, 'CSE'),
    ('Bob', 'bob@dsc.edu', 2, 3, 'AIML'),
    ('Charlie', 'charlie@dsc.edu', 1, 2, 'ECE'),
    ('David', 'david@dsc.edu', 3, 5, 'CSE'),
    ('Eve', 'eve@dsc.edu', 4, 7, 'IT'),
    ('Frank', 'frank@dsc.edu', 2, 4, 'MECH'),
    ('Grace', 'grace@dsc.edu', 3, 6, 'CIVIL'),
    ('Heidi', 'heidi@dsc.edu', 1, 1, 'AIML'),
    ('Ivan', 'ivan@dsc.edu', 2, 3, 'CSE'),
    ('Judy', 'judy@dsc.edu', 3, 5, 'ECE'),
    ('Ken', 'ken@dsc.edu', 4, 7, 'IT'),
    ('Laura', 'laura@dsc.edu', 1, 2, 'CSE'),
    ('Mallory', 'mallory@dsc.edu', 2, 4, 'AIML'),
    ('Niaj', 'niaj@dsc.edu', 3, 6, 'MECH'),
    ('Olivia', 'olivia@dsc.edu', 4, 8, 'CIVIL'),
    ('Peggy', 'peggy@dsc.edu', 1, 1, 'CSE'),
    ('Rupert', 'rupert@dsc.edu', 2, 3, 'IT'),
    ('Sybil', 'sybil@dsc.edu', 3, 5, 'ECE'),
    ('Trent', 'trent@dsc.edu', 4, 7, 'CSE'),
    ('Uma', 'uma@dsc.edu', 1, 2, 'AIML'),
    ('Victor', 'victor@dsc.edu', 2, 4, 'CSE'),
    ('Walter', 'walter@dsc.edu', 3, 6, 'IT'),
    ('Xavier', 'xavier@dsc.edu', 4, 8, 'MECH'),
    ('Yvonne', 'yvonne@dsc.edu', 2, 3, 'CIVIL'),
    ('Zara', 'zara@dsc.edu', 3, 5, 'CSE');

INSERT INTO Semester (year, semester, start_date, end_date)
VALUES
    (1, 1, '2025-01-10', '2025-05-10'),
    (1, 2, '2025-08-01', '2025-12-15'),
    (2, 3, '2025-01-10', '2025-05-10'),
    (2, 4, '2025-08-01', '2025-12-15'),
    (3, 5, '2025-01-10', '2025-05-10'),
    (3, 6, '2025-08-01', '2025-12-15'),
    (4, 7, '2025-01-10', '2025-05-10'),
    (4, 8, '2025-08-01', '2025-12-15');

INSERT INTO Subjects (name, semester_id, credits)
VALUES
    ('Math I', 1, 4),
    ('Programming Fundamentals', 1, 3),
    ('Physics I', 1, 4),
    ('Electronics I', 2, 3),
    ('Discrete Mathematics', 2, 4),
    ('Data Structures', 3, 4),
    ('Digital Logic', 3, 3),
    ('Operating Systems', 4, 4),
    ('Database Systems', 4, 4),
    ('Computer Networks', 5, 4),
    ('Machine Learning', 5, 3),
    ('Artificial Intelligence', 6, 3),
    ('Distributed Systems', 6, 3),
    ('Deep Learning', 7, 3),
    ('Cloud Computing', 7, 3),
    ('Big Data Analytics', 8, 3),
    ('Software Engineering', 2, 3),
    ('Linear Algebra', 2, 4),
    ('Numerical Methods', 3, 3),
    ('Computer Graphics', 6, 3);

INSERT INTO Marks (student_id, subject_id, marks, grade, semester_id)
VALUES
    (1, 1, 90, 'A', 1),
    (1, 2, 85, 'B', 1),
    (1, 3, 78, 'C', 1),
    (2, 1, 88, 'A', 1),
    (2, 2, 80, 'B', 1),
    (2, 3, 92, 'A', 1),
    (3, 4, 75, 'C', 2),
    (3, 5, 82, 'B', 2),
    (4, 6, 89, 'A', 3),
    (4, 7, 77, 'C', 3),
    (5, 8, 91, 'A', 4),
    (5, 9, 84, 'B', 4),
    (6, 10, 73, 'C', 5),
    (6, 11, 86, 'B', 5),
    (7, 12, 88, 'A', 6),
    (7, 13, 79, 'C', 6),
    (8, 1, 68, 'D', 1),
    (8, 2, 74, 'C', 1),
    (9, 6, 81, 'B', 3),
    (9, 7, 76, 'C', 3),
    (10, 8, 93, 'A', 4),
    (10, 9, 89, 'A', 4),
    (11, 10, 72, 'C', 5),
    (11, 11, 70, 'C', 5),
    (12, 12, 87, 'B', 6),
    (12, 13, 90, 'A', 6),
    (13, 4, 79, 'C', 2),
    (13, 5, 83, 'B', 2),
    (14, 6, 88, 'A', 3),
    (14, 7, 85, 'B', 3),
    (15, 8, 67, 'D', 4),
    (15, 9, 71, 'C', 4),
    (16, 1, 80, 'B', 1),
    (16, 2, 82, 'B', 1),
    (17, 10, 90, 'A', 5),
    (17, 11, 88, 'A', 5),
    (18, 12, 77, 'C', 6),
    (18, 13, 81, 'B', 6),
    (19, 14, 85, 'B', 7),
    (19, 15, 89, 'A', 7),
    (20, 16, 92, 'A', 8),
    (20, 17, 88, 'A', 2),
    (21, 18, 79, 'C', 3),
    (21, 19, 83, 'B', 3),
    (22, 6, 75, 'C', 3),
    (22, 7, 78, 'C', 3),
    (23, 8, 91, 'A', 4),
    (23, 9, 87, 'B', 4),
    (24, 10, 69, 'D', 5),
    (24, 11, 73, 'C', 5),
    (25, 12, 82, 'B', 6),
    (25, 13, 86, 'B', 6);

INSERT INTO Timetable (semester_id, day, time, subject_id, room)
VALUES
    (1, 'Monday', '09:00', 1, 'A101'),
    (1, 'Wednesday', '11:00', 2, 'A102'),
    (1, 'Friday', '14:00', 3, 'A103'),
    (2, 'Tuesday', '10:00', 4, 'B201'),
    (2, 'Thursday', '12:00', 5, 'B202'),
    (3, 'Monday', '09:00', 6, 'C301'),
    (3, 'Wednesday', '11:00', 7, 'C302'),
    (4, 'Tuesday', '10:00', 8, 'D401'),
    (4, 'Thursday', '12:00', 9, 'D402'),
    (5, 'Monday', '09:00', 10, 'E501'),
    (5, 'Wednesday', '11:00', 11, 'E502'),
    (6, 'Tuesday', '10:00', 12, 'F601'),
    (6, 'Thursday', '12:00', 13, 'F602'),
    (7, 'Monday', '09:00', 14, 'G701'),
    (7, 'Wednesday', '11:00', 15, 'G702'),
    (8, 'Tuesday', '10:00', 16, 'H801'),
    (2, 'Friday', '15:00', 17, 'B203'),
    (3, 'Friday', '15:00', 18, 'C303'),
    (4, 'Friday', '15:00', 19, 'D403'),
    (6, 'Friday', '15:00', 20, 'F603');

-- ============================================================
-- Sample data — 7 new tables
-- ============================================================

-- Department (6 rows)
INSERT INTO Department (code, name, head_of_department, established_year)
VALUES
    ('CSE', 'Computer Science and Engineering', 'Dr. Rajesh Kumar', 1995),
    ('AIML', 'Artificial Intelligence and Machine Learning', 'Dr. Priya Sharma', 2018),
    ('ECE', 'Electronics and Communication Engineering', 'Dr. Suresh Reddy', 1998),
    ('IT', 'Information Technology', 'Dr. Meena Gupta', 2001),
    ('MECH', 'Mechanical Engineering', 'Dr. Anil Patel', 1990),
    ('CIVIL', 'Civil Engineering', 'Dr. Kavitha Nair', 1988);

-- Faculty (15 rows)
INSERT INTO Faculty (name, email, department, designation, subject_id)
VALUES
    ('Dr. Rajesh Kumar', 'rajesh@dsc.edu', 'CSE', 'Professor', 6),
    ('Dr. Priya Sharma', 'priya@dsc.edu', 'AIML', 'Professor', 11),
    ('Dr. Suresh Reddy', 'suresh@dsc.edu', 'ECE', 'Professor', 4),
    ('Dr. Meena Gupta', 'meena@dsc.edu', 'IT', 'Professor', 10),
    ('Dr. Anil Patel', 'anil@dsc.edu', 'MECH', 'Professor', 3),
    ('Prof. Neha Singh', 'neha@dsc.edu', 'CSE', 'Associate Professor', 9),
    ('Prof. Arjun Das', 'arjun@dsc.edu', 'AIML', 'Associate Professor', 14),
    ('Prof. Lakshmi Iyer', 'lakshmi@dsc.edu', 'ECE', 'Associate Professor', 7),
    ('Prof. Vikram Joshi', 'vikram@dsc.edu', 'IT', 'Associate Professor', 15),
    ('Prof. Deepa Menon', 'deepa@dsc.edu', 'CIVIL', 'Associate Professor', 13),
    ('Dr. Ramesh Babu', 'ramesh@dsc.edu', 'CSE', 'Assistant Professor', 2),
    ('Dr. Sunita Rao', 'sunita@dsc.edu', 'AIML', 'Assistant Professor', 12),
    ('Dr. Karthik Nair', 'karthik@dsc.edu', 'ECE', 'Assistant Professor', 5),
    ('Dr. Pooja Verma', 'pooja@dsc.edu', 'CSE', 'Assistant Professor', 1),
    ('Dr. Sanjay Mishra', 'sanjay@dsc.edu', 'MECH', 'Assistant Professor', 19);

-- Assignment (30 rows)
INSERT INTO Assignment (title, subject_id, semester_id, type, max_marks, due_date)
VALUES
    ('Math I Problem Set 1', 1, 1, 'homework', 20, '2025-02-15'),
    ('Math I Problem Set 2', 1, 1, 'homework', 20, '2025-03-15'),
    ('Programming Lab 1', 2, 1, 'lab', 25, '2025-02-20'),
    ('Programming Lab 2', 2, 1, 'lab', 25, '2025-03-20'),
    ('Programming Mini Project', 2, 1, 'project', 50, '2025-04-15'),
    ('Physics Lab 1', 3, 1, 'lab', 25, '2025-02-25'),
    ('Electronics Lab 1', 4, 2, 'lab', 25, '2025-09-15'),
    ('Discrete Math HW 1', 5, 2, 'homework', 20, '2025-09-20'),
    ('Data Structures Lab 1', 6, 3, 'lab', 25, '2025-02-10'),
    ('Data Structures Lab 2', 6, 3, 'lab', 25, '2025-03-10'),
    ('Data Structures Project', 6, 3, 'project', 50, '2025-04-20'),
    ('Digital Logic Lab 1', 7, 3, 'lab', 25, '2025-02-15'),
    ('OS Assignment 1', 8, 4, 'homework', 20, '2025-09-10'),
    ('OS Lab 1', 8, 4, 'lab', 25, '2025-09-25'),
    ('DB Systems Project', 9, 4, 'project', 50, '2025-11-01'),
    ('Networks Lab 1', 10, 5, 'lab', 25, '2025-02-20'),
    ('Networks Lab 2', 10, 5, 'lab', 25, '2025-03-20'),
    ('ML Assignment 1', 11, 5, 'homework', 20, '2025-02-15'),
    ('ML Project', 11, 5, 'project', 50, '2025-04-10'),
    ('AI Assignment 1', 12, 6, 'homework', 20, '2025-09-15'),
    ('AI Project', 12, 6, 'project', 50, '2025-11-15'),
    ('Distributed Systems Lab', 13, 6, 'lab', 25, '2025-10-01'),
    ('Deep Learning Project', 14, 7, 'project', 50, '2025-04-01'),
    ('Cloud Computing Lab 1', 15, 7, 'lab', 25, '2025-02-28'),
    ('Cloud Computing Lab 2', 15, 7, 'lab', 25, '2025-03-28'),
    ('Big Data Project', 16, 8, 'project', 50, '2025-11-10'),
    ('Software Engg HW 1', 17, 2, 'homework', 20, '2025-09-10'),
    ('Linear Algebra HW 1', 18, 2, 'homework', 20, '2025-09-20'),
    ('Numerical Methods Lab', 19, 3, 'lab', 25, '2025-03-01'),
    ('Computer Graphics Project', 20, 6, 'project', 50, '2025-11-20');

-- Submission (80 rows)
INSERT INTO Submission (student_id, assignment_id, submitted_date, marks_obtained, status)
VALUES
    -- Alice (student 1) — semester 1 assignments
    (1, 1, '2025-02-14', 18, 'on_time'),
    (1, 2, '2025-03-14', 17, 'on_time'),
    (1, 3, '2025-02-19', 22, 'on_time'),
    (1, 4, '2025-03-21', 20, 'late'),
    (1, 5, '2025-04-14', 42, 'on_time'),
    (1, 6, '2025-02-25', 19, 'on_time'),
    -- Bob (student 2) — semester 1 assignments
    (2, 1, '2025-02-15', 16, 'on_time'),
    (2, 2, '2025-03-16', 14, 'late'),
    (2, 3, '2025-02-20', 23, 'on_time'),
    (2, 4, '2025-03-20', 21, 'on_time'),
    (2, 5, '2025-04-16', 38, 'late'),
    (2, 6, '2025-02-24', 20, 'on_time'),
    -- Charlie (student 3) — semester 2 assignments
    (3, 7, '2025-09-14', 21, 'on_time'),
    (3, 8, '2025-09-19', 18, 'on_time'),
    (3, 27, '2025-09-10', 16, 'on_time'),
    (3, 28, '2025-09-22', 15, 'late'),
    -- David (student 4) — semester 3 assignments
    (4, 9, '2025-02-09', 23, 'on_time'),
    (4, 10, '2025-03-10', 22, 'on_time'),
    (4, 11, '2025-04-19', 45, 'on_time'),
    (4, 12, '2025-02-14', 20, 'on_time'),
    (4, 29, '2025-03-01', 21, 'on_time'),
    -- Eve (student 5) — semester 4 assignments
    (5, 13, '2025-09-09', 18, 'on_time'),
    (5, 14, '2025-09-24', 22, 'on_time'),
    (5, 15, '2025-10-31', 44, 'on_time'),
    -- Frank (student 6) — semester 5 assignments
    (6, 16, '2025-02-19', 20, 'on_time'),
    (6, 17, '2025-03-21', 18, 'late'),
    (6, 18, '2025-02-14', 15, 'on_time'),
    (6, 19, '2025-04-12', 35, 'late'),
    -- Grace (student 7) — semester 6 assignments
    (7, 20, '2025-09-14', 17, 'on_time'),
    (7, 21, '2025-11-14', 40, 'on_time'),
    (7, 22, '2025-09-30', 22, 'on_time'),
    (7, 30, '2025-11-19', 43, 'on_time'),
    -- Heidi (student 8) — semester 1 assignments
    (8, 1, '2025-02-16', 12, 'late'),
    (8, 2, '2025-03-17', 10, 'late'),
    (8, 3, '2025-02-21', 18, 'late'),
    (8, 4, '2025-03-22', 15, 'late'),
    (8, 5, '2025-04-18', 30, 'late'),
    (8, 6, '2025-02-27', 14, 'late'),
    -- Ivan (student 9) — semester 3 assignments
    (9, 9, '2025-02-10', 21, 'on_time'),
    (9, 10, '2025-03-11', 19, 'late'),
    (9, 11, '2025-04-20', 40, 'on_time'),
    (9, 12, '2025-02-16', 18, 'late'),
    -- Judy (student 10) — semester 4 assignments
    (10, 13, '2025-09-10', 19, 'on_time'),
    (10, 14, '2025-09-25', 24, 'on_time'),
    (10, 15, '2025-11-01', 47, 'on_time'),
    -- Ken (student 11) — semester 5 assignments
    (11, 16, '2025-02-21', 17, 'late'),
    (11, 17, '2025-03-19', 19, 'on_time'),
    (11, 18, '2025-02-16', 13, 'late'),
    (11, 19, '2025-04-09', 32, 'on_time'),
    -- Laura (student 12) — semester 6 assignments
    (12, 20, '2025-09-16', 18, 'late'),
    (12, 21, '2025-11-16', 42, 'late'),
    (12, 22, '2025-10-02', 21, 'late'),
    -- Mallory (student 13) — semester 2 assignments
    (13, 7, '2025-09-16', 19, 'late'),
    (13, 8, '2025-09-21', 16, 'late'),
    (13, 27, '2025-09-11', 17, 'late'),
    -- Niaj (student 14) — semester 3 assignments
    (14, 9, '2025-02-10', 24, 'on_time'),
    (14, 10, '2025-03-09', 23, 'on_time'),
    (14, 11, '2025-04-18', 46, 'on_time'),
    -- Peggy (student 16) — semester 1 assignments
    (16, 1, '2025-02-14', 15, 'on_time'),
    (16, 2, '2025-03-14', 16, 'on_time'),
    (16, 3, '2025-02-19', 20, 'on_time'),
    (16, 5, '2025-04-14', 36, 'on_time'),
    -- Rupert (student 17) — semester 5 assignments
    (17, 16, '2025-02-20', 22, 'on_time'),
    (17, 18, '2025-02-15', 18, 'on_time'),
    (17, 19, '2025-04-10', 45, 'on_time'),
    -- Trent (student 19) — semester 7 assignments
    (19, 23, '2025-03-31', 41, 'on_time'),
    (19, 24, '2025-02-27', 22, 'on_time'),
    (19, 25, '2025-03-27', 21, 'on_time'),
    -- Olivia (student 15) — semester 8 assignments
    (15, 26, '2025-11-09', 38, 'on_time'),
    -- Victor (student 21) — semester 3 assignments
    (21, 9, '2025-02-11', 19, 'late'),
    (21, 10, '2025-03-12', 17, 'late'),
    (21, 29, '2025-03-02', 18, 'late'),
    -- Xavier (student 23) — semester 4 assignments
    (23, 13, '2025-09-11', 17, 'late'),
    (23, 14, '2025-09-26', 21, 'late'),
    (23, 15, '2025-11-02', 39, 'late'),
    -- Zara (student 25) — semester 6 assignments
    (25, 20, '2025-09-15', 19, 'on_time'),
    (25, 21, '2025-11-15', 44, 'on_time'),
    -- Extra rows to reach 80
    (20, 27, '2025-09-12', 17, 'late'),
    (22, 12, '2025-02-16', 19, 'late'),
    (24, 18, '2025-02-17', 14, 'late');

-- LibraryBook (25 rows)
INSERT INTO LibraryBook (title, author, isbn, department, copies_total, copies_available)
VALUES
    ('Introduction to Algorithms', 'Cormen et al.', '978-0262033848', 'CSE', 10, 4),
    ('Computer Networking', 'Kurose & Ross', '978-0133594140', 'CSE', 8, 3),
    ('Operating System Concepts', 'Silberschatz et al.', '978-1119800361', 'CSE', 6, 2),
    ('Database System Concepts', 'Silberschatz et al.', '978-0078022159', 'CSE', 7, 5),
    ('Deep Learning', 'Goodfellow et al.', '978-0262035613', 'AIML', 5, 1),
    ('Pattern Recognition and ML', 'Bishop', '978-0387310732', 'AIML', 4, 2),
    ('Artificial Intelligence: A Modern Approach', 'Russell & Norvig', '978-0134610993', 'AIML', 6, 3),
    ('Digital Design', 'Morris Mano', '978-0134549897', 'ECE', 8, 5),
    ('Signals and Systems', 'Oppenheim & Willsky', '978-0138147570', 'ECE', 5, 2),
    ('Electronic Devices', 'Floyd', '978-0132549868', 'ECE', 6, 4),
    ('Data Communications', 'Forouzan', '978-0073376226', 'IT', 5, 3),
    ('Web Technologies', 'Godbole & Kahate', '978-0070681781', 'IT', 4, 2),
    ('Software Engineering', 'Pressman', '978-0078022128', 'IT', 6, 4),
    ('Engineering Mechanics', 'Beer & Johnston', '978-0073398167', 'MECH', 7, 5),
    ('Thermodynamics', 'Cengel & Boles', '978-0073398174', 'MECH', 5, 3),
    ('Fluid Mechanics', 'White', '978-0073398273', 'MECH', 4, 2),
    ('Structural Analysis', 'Hibbeler', '978-0134610672', 'CIVIL', 6, 4),
    ('Geotechnical Engineering', 'Das', '978-1305635180', 'CIVIL', 4, 3),
    ('Surveying', 'Punmia', '978-8131806241', 'CIVIL', 5, 5),
    ('Discrete Mathematics', 'Rosen', '978-0073383095', 'CSE', 6, 3),
    ('Linear Algebra', 'Strang', '978-0980232714', 'CSE', 5, 4),
    ('Probability and Statistics', 'Walpole et al.', '978-0321831446', 'CSE', 4, 2),
    ('Machine Learning', 'Tom Mitchell', '978-0070428072', 'AIML', 5, 3),
    ('Cloud Computing', 'Buyya et al.', '978-0124114548', 'IT', 3, 1),
    ('Big Data Analytics', 'Bart Baesens', '978-1118876138', 'CSE', 4, 2);

-- BookLoan (40 rows)
INSERT INTO BookLoan (student_id, book_id, borrow_date, due_date, return_date, status)
VALUES
    (1, 1, '2025-01-20', '2025-02-20', '2025-02-18', 'returned'),
    (1, 2, '2025-03-01', '2025-04-01', '2025-03-28', 'returned'),
    (1, 20, '2025-04-10', '2025-05-10', NULL, 'active'),
    (2, 5, '2025-01-15', '2025-02-15', '2025-02-14', 'returned'),
    (2, 6, '2025-03-05', '2025-04-05', '2025-04-10', 'returned'),
    (2, 7, '2025-04-15', '2025-05-15', NULL, 'active'),
    (3, 8, '2025-08-10', '2025-09-10', '2025-09-08', 'returned'),
    (3, 9, '2025-10-01', '2025-11-01', NULL, 'overdue'),
    (4, 1, '2025-01-12', '2025-02-12', '2025-02-10', 'returned'),
    (4, 3, '2025-03-10', '2025-04-10', '2025-04-05', 'returned'),
    (4, 4, '2025-04-20', '2025-05-20', NULL, 'active'),
    (5, 3, '2025-01-15', '2025-02-15', '2025-02-12', 'returned'),
    (5, 4, '2025-03-20', '2025-04-20', '2025-04-18', 'returned'),
    (6, 10, '2025-01-20', '2025-02-20', '2025-02-22', 'returned'),
    (6, 11, '2025-03-15', '2025-04-15', NULL, 'overdue'),
    (7, 17, '2025-08-15', '2025-09-15', '2025-09-12', 'returned'),
    (7, 18, '2025-10-05', '2025-11-05', NULL, 'active'),
    (8, 1, '2025-01-25', '2025-02-25', '2025-03-05', 'returned'),
    (8, 5, '2025-03-10', '2025-04-10', NULL, 'overdue'),
    (9, 1, '2025-01-18', '2025-02-18', '2025-02-16', 'returned'),
    (9, 4, '2025-03-01', '2025-04-01', '2025-03-30', 'returned'),
    (10, 3, '2025-09-01', '2025-10-01', '2025-09-28', 'returned'),
    (10, 4, '2025-10-10', '2025-11-10', NULL, 'active'),
    (11, 11, '2025-01-20', '2025-02-20', '2025-02-19', 'returned'),
    (11, 24, '2025-03-15', '2025-04-15', NULL, 'active'),
    (12, 7, '2025-08-20', '2025-09-20', '2025-09-18', 'returned'),
    (12, 12, '2025-10-01', '2025-11-01', '2025-10-30', 'returned'),
    (13, 6, '2025-08-15', '2025-09-15', '2025-09-20', 'returned'),
    (13, 23, '2025-10-10', '2025-11-10', NULL, 'active'),
    (14, 14, '2025-01-15', '2025-02-15', '2025-02-13', 'returned'),
    (14, 15, '2025-03-10', '2025-04-10', '2025-04-08', 'returned'),
    (16, 1, '2025-01-22', '2025-02-22', '2025-02-20', 'returned'),
    (16, 21, '2025-03-05', '2025-04-05', NULL, 'active'),
    (17, 11, '2025-01-18', '2025-02-18', '2025-02-16', 'returned'),
    (17, 13, '2025-03-10', '2025-04-10', '2025-04-09', 'returned'),
    (19, 5, '2025-01-20', '2025-02-20', '2025-02-18', 'returned'),
    (19, 24, '2025-03-15', '2025-04-15', NULL, 'active'),
    (20, 25, '2025-08-20', '2025-09-20', NULL, 'overdue'),
    (25, 7, '2025-08-18', '2025-09-18', '2025-09-15', 'returned'),
    (25, 12, '2025-10-05', '2025-11-05', NULL, 'active');

-- LabEquipment (20 rows)
INSERT INTO LabEquipment (name, department, lab_room, quantity, status)
VALUES
    ('Desktop Computer', 'CSE', 'C301', 40, 'available'),
    ('Raspberry Pi 4', 'CSE', 'C302', 25, 'available'),
    ('Arduino Uno', 'ECE', 'B201', 30, 'available'),
    ('Oscilloscope', 'ECE', 'B202', 15, 'available'),
    ('Multimeter', 'ECE', 'B201', 20, 'available'),
    ('NVIDIA Jetson Nano', 'AIML', 'E501', 10, 'available'),
    ('GPU Server (RTX 3090)', 'AIML', 'E502', 4, 'in_use'),
    ('3D Printer', 'MECH', 'D401', 3, 'available'),
    ('CNC Machine', 'MECH', 'D402', 2, 'maintenance'),
    ('Lathe Machine', 'MECH', 'D403', 4, 'available'),
    ('Theodolite', 'CIVIL', 'F601', 8, 'available'),
    ('Total Station', 'CIVIL', 'F601', 3, 'in_use'),
    ('Network Switch (Cisco)', 'IT', 'G701', 10, 'available'),
    ('Network Router', 'IT', 'G701', 6, 'available'),
    ('Logic Analyzer', 'ECE', 'B202', 8, 'available'),
    ('Soldering Station', 'ECE', 'B203', 20, 'available'),
    ('Cloud Server Node', 'IT', 'G702', 5, 'in_use'),
    ('Robotic Arm', 'MECH', 'D401', 2, 'available'),
    ('Soil Testing Kit', 'CIVIL', 'F602', 10, 'available'),
    ('Drone (DJI Mavic)', 'CIVIL', 'F603', 2, 'maintenance');
