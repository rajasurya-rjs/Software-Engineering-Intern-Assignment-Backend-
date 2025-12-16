-- Drop views if they exist
DROP VIEW IF EXISTS v_students_per_department;
DROP VIEW IF EXISTS v_course_grades_summary;
DROP VIEW IF EXISTS v_student_enrollments_detail;

-- Students per department view
CREATE VIEW v_students_per_department AS
SELECT
    d.id   AS department_id,
    d.name AS department_name,
    COUNT(s.id) AS student_count
FROM departments d
LEFT JOIN students s ON s.department_id = d.id
GROUP BY d.id, d.name;

-- Course grades summary view
CREATE VIEW v_course_grades_summary AS
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
    c.id AS course_id,
    c.course_code,
    c.course_name,
    AVG(g.grade_point) AS avg_grade_point,
    COUNT(g.grade_point) AS graded_enrollments
FROM courses c
LEFT JOIN grade_points g ON g.course_id = c.id
GROUP BY c.id, c.course_code, c.course_name;

-- Student enrollments detail view
CREATE VIEW v_student_enrollments_detail AS
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
JOIN departments d ON s.department_id = d.id;
