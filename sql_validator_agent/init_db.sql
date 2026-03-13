-- Create tables
CREATE TABLE Student (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    year INT CHECK (year BETWEEN 1 AND 4),
    semester INT CHECK (semester BETWEEN 1 AND 8),
    department VARCHAR(50)
);

CREATE TABLE Semester (
    semester_id SERIAL PRIMARY KEY,
    year INT CHECK (year BETWEEN 1 AND 4),
    semester INT CHECK (semester BETWEEN 1 AND 8),
    start_date DATE,
    end_date DATE
);

CREATE TABLE Subjects (
    subject_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    semester_id INT REFERENCES Semester(semester_id),
    credits INT
);

CREATE TABLE Marks (
    mark_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES Student(student_id),
    subject_id INT REFERENCES Subjects(subject_id),
    marks INT,
    grade CHAR(2),
    semester_id INT REFERENCES Semester(semester_id)
);

CREATE TABLE Timetable (
    timetable_id SERIAL PRIMARY KEY,
    semester_id INT REFERENCES Semester(semester_id),
    day VARCHAR(10),
    time TIME,
    subject_id INT REFERENCES Subjects(subject_id),
    room VARCHAR(20)
);

-- Insert sample data (truncated for brevity)
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
