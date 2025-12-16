from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from etl.utils.db import get_connection
from etl.utils.logger import get_logger
import psycopg2

app = FastAPI(title="Student Auto-Registration API")
logger = get_logger()

class StudentRegistration(BaseModel):
    full_name: str
    email: EmailStr
    department_name: str
    enrollment_year: int

def get_or_create_department(conn, dept_name: str) -> int:
    """Get department ID or create if it doesn't exist"""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM departments WHERE LOWER(name) = LOWER(%s)",
            (dept_name,)
        )
        result = cur.fetchone()
        if result:
            return result[0]
        
        # Create new department
        cur.execute(
            "INSERT INTO departments (name) VALUES (%s) RETURNING id",
            (dept_name,)
        )
        return cur.fetchone()[0]

@app.post("/register-student")
async def register_student(student: StudentRegistration):
    try:
        logger.info(f"Registering student: {student.full_name} ({student.email})")
        
        conn = get_connection()
        
        with conn.cursor() as cur:
            # Get or create department
            dept_id = get_or_create_department(conn, student.department_name)
            
            # Insert student (ignore if email exists)
            cur.execute("""
                INSERT INTO students (full_name, email, department_id, enrollment_year)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
            """, (student.full_name, student.email, dept_id, student.enrollment_year))
            
            result = cur.fetchone()
            
            if result:
                conn.commit()
                logger.info(f"Student registered successfully: ID {result[0]}")
                return {"status": "success", "message": "Student registered", "student_id": result[0]}
            else:
                logger.info(f"Student already exists: {student.email}")
                return {"status": "exists", "message": "Student already registered"}
                
    except Exception as e:
        logger.error(f"Registration failed for {student.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if 'conn' in locals():
            conn.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Auto-registration API ready"}
