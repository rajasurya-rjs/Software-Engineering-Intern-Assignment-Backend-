-- =============== BASIC COUNTS ===============

-- Total students
SELECT COUNT(*) AS total_students
FROM students;

-- Total courses
SELECT COUNT(*) AS total_courses
FROM courses;

-- Total enrollments
SELECT COUNT(*) AS total_enrollments
FROM enrollments;

-- ========== AGGREGATIONS (COUNT, AVG) ==========

-- Students per department
SELECT
    d.name AS department_name,
    COUNT(s.id) AS student_count
FROM departments d
LEFT JOIN students s ON s.department_id = d.id
GROUP BY d.name
ORDER BY student_count DESC;

-- Courses per department
SELECT
    d.name AS department_name,
    COUNT(c.id) AS course_count
FROM departments d
LEFT JOIN courses c ON c.department_id = d.id
GROUP BY d.name
ORDER BY course_count DESC;

-- Average grade per course (A=4, B=3, C=2, D=1, F=0)
WITH grade_points AS (
    SELECT
        e.course_id,
        CASE e.grade
            WHEN 'A'  THEN 4.0
            WHEN 'A-' THEN 3.7
            WHEN 'B+' THEN 3.3
            WHEN 'B'  THEN 3.0
            WHEN 'C'  THEN 2.0
            WHEN 'D'  THEN 1.0
            WHEN 'F'  THEN 0.0
            ELSE NULL
        END AS grade_point
    FROM enrollments e
)
SELECT
    c.course_code,
    c.course_name,
    AVG(g.grade_point) AS avg_grade_point,
    COUNT(g.grade_point) AS graded_enrollments
FROM courses c
LEFT JOIN grade_points g ON g.course_id = c.id
GROUP BY c.course_code, c.course_name
ORDER BY avg_grade_point DESC NULLS LAST;

-- ========== JOIN-HEAVY QUERIES ==========

-- Detailed student → enrollment → course view
SELECT
    s.id AS student_id,
    s.full_name,
    s.email,
    d.name AS department_name,
    c.course_code,
    c.course_name,
    e.enrollment_date,
    e.grade
FROM enrollments e
JOIN students s    ON e.student_id = s.id
JOIN courses c     ON e.course_id = c.id
JOIN departments d ON s.department_id = d.id
ORDER BY s.id, e.enrollment_date;

-- Students and how many courses they are enrolled in
SELECT
    s.id AS student_id,
    s.full_name,
    COUNT(e.id) AS course_count
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.id
GROUP BY s.id, s.full_name
ORDER BY course_count DESC, s.full
-- ========== DUPLICATES / INVALID ENTRIES ==========

-- Detect potential duplicate students by email
SELECT
    email,
    COUNT(*) AS occurrences
FROM students
GROUP BY email
HAVING COUNT(*) > 1;

-- Detect potential duplicate courses by course_code
SELECT
    course_code,
    COUNT(*) AS occurrences
FROM courses
GROUP BY course_code
HAVING COUNT(*) > 1;

-- Enrollments with missing grades
SELECT *
FROM enrollments
WHERE grade IS NULL;

-- Enrollments referencing non-existing students or courses (should be zero)
SELECT e.*
FROM enrollments e
LEFT JOIN students s ON e.student_id = s.id
LEFT JOIN courses c  ON e.course_id  = c.id
WHERE s.id IS NULL OR c.id IS NULL;
