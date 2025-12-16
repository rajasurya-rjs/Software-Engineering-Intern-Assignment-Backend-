import psycopg2
from psycopg2.extras import DictCursor

DATABASE_URL = "postgresql://neondb_owner:npg_QXgCAz3mUOM9@ep-sweet-union-adde35pm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def run_query(cur, title, sql, params=None):
    print(f"\n========== {title} ==========")
    cur.execute(sql, params or ())
    try:
        rows = cur.fetchall()
    except psycopg2.ProgrammingError:
        # e.g. CALL or commands without result sets
        print("Command executed (no result set).")
        return
    if not rows:
        print("No rows returned.")
        return
    # Print up to first 5 rows
    for row in rows[:5]:
        print(dict(row))

def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=DictCursor)

    # 1) Basic counts (COUNT)
    run_query(
        cur,
        "Total students / courses / enrollments",
        """
        SELECT
            (SELECT COUNT(*) FROM students) AS total_students,
            (SELECT COUNT(*) FROM courses) AS total_courses,
            (SELECT COUNT(*) FROM enrollments) AS total_enrollments;
        """
    )

    # 2) Aggregation: students per department (COUNT + GROUP BY)
    run_query(
        cur,
        "Students per department",
        """
        SELECT
            d.name AS department_name,
            COUNT(s.id) AS student_count
        FROM departments d
        LEFT JOIN students s ON s.department_id = d.id
        GROUP BY d.name
        ORDER BY student_count DESC;
        """
    )

    # 3) Aggregation: average grade per course (AVG over mapped grade points)
    run_query(
        cur,
        "Average grade per course (grade points)",
        """
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
        """
    )

    # 4) JOIN-heavy query: student ↔ enrollment ↔ course
    run_query(
        cur,
        "Sample student-enrollment-course rows",
        """
        SELECT
            s.id AS student_id,
            s.full_name,
            s.email,
            c.course_code,
            c.course_name,
            e.enrollment_date,
            e.grade
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c  ON e.course_id = c.id
        ORDER BY s.id, e.enrollment_date
        LIMIT 5;
        """
    )

    # 5) Duplicate detection: students by email
    run_query(
        cur,
        "Potential duplicate students by email",
        """
        SELECT
            email,
            COUNT(*) AS occurrences
        FROM students
        GROUP BY email
        HAVING COUNT(*) > 1;
        """
    )

    # 6) View: v_students_per_department
    run_query(
        cur,
        "View v_students_per_department",
        """
        SELECT * FROM v_students_per_department;
        """
    )

    # 7) View: v_course_grades_summary
    run_query(
        cur,
        "View v_course_grades_summary (first 5)",
        """
        SELECT * FROM v_course_grades_summary
        ORDER BY avg_grade_point DESC NULLS LAST
        LIMIT 5;
        """
    )

    # 8) Procedure + reporting table: refresh_course_enrollment_stats
    print("\n========== CALL refresh_course_enrollment_stats() ==========")
    cur.execute("CALL refresh_course_enrollment_stats();")
    conn.commit()
    run_query(
        cur,
        "Reporting table course_enrollment_stats (first 5)",
        "SELECT * FROM course_enrollment_stats ORDER BY total_enrollments DESC, course_id;"
    )

    # 9) EXPLAIN ANALYZE on a JOIN-heavy aggregation
    run_query(
        cur,
        "EXPLAIN ANALYZE - students vs course_count",
        """
        EXPLAIN ANALYZE
        SELECT
            s.id AS student_id,
            s.full_name,
            COUNT(e.id) AS course_count
        FROM students s
        LEFT JOIN enrollments e ON e.student_id = s.id
        GROUP BY s.id, s.full_name
        ORDER BY course_count DESC, s.full_name;
        """
    )

    cur.close()
    conn.close()
    print("\n✅ Task 5 SQL verification completed.\n")

if __name__ == "__main__":
    main()
