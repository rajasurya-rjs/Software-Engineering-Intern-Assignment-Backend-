-- =====================================================
-- Seed Data for Academic Management System
-- =====================================================

-- -----------------------
-- Departments
-- -----------------------
-- Clear existing data
TRUNCATE TABLE enrollments RESTART IDENTITY CASCADE;
TRUNCATE TABLE courses RESTART IDENTITY CASCADE;
TRUNCATE TABLE students RESTART IDENTITY CASCADE;
TRUNCATE TABLE departments RESTART IDENTITY CASCADE;

INSERT INTO departments (name) VALUES
('Computer Science'),
('Electrical Engineering'),
('Mechanical Engineering');

-- -----------------------
-- Students
-- -----------------------
INSERT INTO students (full_name, email, department_id, enrollment_year) VALUES
('Aarav Sharma', 'aarav.sharma@example.com', 1, 2023),
('Priya Verma', 'priya.verma@example.com', 1, 2022),
('Rohan Mehta', 'rohan.mehta@example.com', 2, 2023),
('Sneha Iyer', 'sneha.iyer@example.com', 3, 2021);

-- -----------------------
-- Courses
-- -----------------------
INSERT INTO courses (course_code, course_name, credits, department_id) VALUES
('CS101', 'Data Structures', 4, 1),
('CS102', 'Databases', 3, 1),
('EE101', 'Circuit Analysis', 4, 2),
('ME101', 'Thermodynamics', 4, 3);

-- -----------------------
-- Enrollments
-- -----------------------
INSERT INTO enrollments (student_id, course_id, enrollment_date, grade) VALUES
(1, 1, '2024-01-10', 'A'),
(1, 2, '2024-01-10', 'A-'),
(2, 1, '2023-01-12', 'B+'),
(3, 3, '2024-01-15', 'A'),
(4, 4, '2022-01-20', 'B');
