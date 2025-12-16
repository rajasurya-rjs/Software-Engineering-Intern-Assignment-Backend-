-- Drop objects if they exist
DROP TABLE IF EXISTS course_enrollment_stats;
DROP PROCEDURE IF EXISTS refresh_course_enrollment_stats;

-- Reporting table for course enrollment stats
CREATE TABLE course_enrollment_stats (
    course_id INT PRIMARY KEY,
    course_code VARCHAR(50),
    course_name VARCHAR(150),
    total_enrollments INT,
    last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Procedure to refresh stats
CREATE OR REPLACE PROCEDURE refresh_course_enrollment_stats()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Clear existing stats
    TRUNCATE TABLE course_enrollment_stats;

    -- Recalculate from current data
    INSERT INTO course_enrollment_stats (
        course_id,
        course_code,
        course_name,
        total_enrollments,
        last_refreshed
    )
    SELECT
        c.id,
        c.course_code,
        c.course_name,
        COUNT(e.id) AS total_enrollments,
        NOW()       AS last_refreshed
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    GROUP BY c.id, c.course_code, c.course_name;
END;
$$;
