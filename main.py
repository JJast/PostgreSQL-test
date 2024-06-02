import psycopg2
from faker import Faker
import random
import time
import matplotlib.pyplot as plt

# Initialize Faker
fake = Faker()

# Constants for the amounts of data to generate
NUM_USERS = 200
NUM_COURSES = 50
NUM_ENROLLMENTS_PER_USER = 2
NUM_LESSONS_PER_COURSE = 5
NUM_QUIZZES_PER_LESSON = 2
NUM_QUESTIONS_PER_QUIZ = 3

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port='5432',
    database="postgres",
    user="postgres",
    password="mysecretpassword"
)

# Create a cursor
cur = conn.cursor()

timings = []

def measure_time(operation_name, func):
    start_time = time.time()
    func()
    end_time = time.time()
    duration = end_time - start_time
    timings.append((operation_name, duration))
    print(f"{operation_name} took {duration:.2f} seconds")

def drop_tables():
    cur.execute("DROP TABLE IF EXISTS enrollments")
    cur.execute("DROP TABLE IF EXISTS quiz_questions")
    cur.execute("DROP TABLE IF EXISTS quizzes")
    cur.execute("DROP TABLE IF EXISTS lessons")
    cur.execute("DROP TABLE IF EXISTS courses")
    cur.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    print("Tables dropped successfully")

def create_tables():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255),
            role VARCHAR(255)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255),
            description TEXT,
            instructor VARCHAR(255)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id VARCHAR(255) PRIMARY KEY,
            course_id VARCHAR(255),
            title VARCHAR(255),
            content TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id VARCHAR(255) PRIMARY KEY,
            lesson_id VARCHAR(255),
            title VARCHAR(255),
            FOREIGN KEY (lesson_id) REFERENCES lessons(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id VARCHAR(255) PRIMARY KEY,
            quiz_id VARCHAR(255),
            text TEXT,
            correct_answer VARCHAR(255),
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255),
            course_id VARCHAR(255),
            enrollment_date DATE,
            progress VARCHAR(255),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    conn.commit()
    print("Tables created successfully")

def insert_users():
    for _ in range(NUM_USERS):
        sql = "INSERT INTO users (id, name, email, role) VALUES (%s, %s, %s, %s)"
        val = (fake.uuid4(), fake.name(), fake.email(), random.choice(["student", "instructor"]))
        cur.execute(sql, val)
    conn.commit()
    print("Users inserted successfully")

def retrieve_users():
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    print(f"{len(users)} users retrieved successfully")
    return users

def insert_courses(users):
    cur.execute("SELECT id FROM users WHERE role = 'instructor'")
    instructor_ids = cur.fetchall()
    for _ in range(NUM_COURSES):
        instructor_id = random.choice(instructor_ids)[0]
        sql = "INSERT INTO courses (id, title, description, instructor) VALUES (%s, %s, %s, %s)"
        val = (fake.uuid4(), fake.catch_phrase(), fake.text(), instructor_id)
        cur.execute(sql, val)
    conn.commit()
    print("Courses inserted successfully")

def retrieve_courses():
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    print(f"{len(courses)} courses retrieved successfully")
    return courses

def insert_lessons(courses):
    for course in courses:
        for _ in range(NUM_LESSONS_PER_COURSE):
            sql = "INSERT INTO lessons (id, course_id, title, content) VALUES (%s, %s, %s, %s)"
            val = (fake.uuid4(), course[0], fake.sentence(), fake.text())
            cur.execute(sql, val)
    conn.commit()
    print("Lessons inserted successfully")

def retrieve_lessons():
    cur.execute("SELECT * FROM lessons")
    lessons = cur.fetchall()
    print(f"{len(lessons)} lessons retrieved successfully")
    return lessons

def insert_quizzes(lessons):
    for lesson in lessons:
        for _ in range(NUM_QUIZZES_PER_LESSON):
            sql = "INSERT INTO quizzes (id, lesson_id, title) VALUES (%s, %s, %s)"
            val = (fake.uuid4(), lesson[0], fake.sentence())
            cur.execute(sql, val)
    conn.commit()
    print("Quizzes inserted successfully")

def retrieve_quizzes():
    cur.execute("SELECT * FROM quizzes")
    quizzes = cur.fetchall()
    print(f"{len(quizzes)} quizzes retrieved successfully")
    return quizzes

def insert_quiz_questions(quizzes):
    for quiz in quizzes:
        for _ in range(NUM_QUESTIONS_PER_QUIZ):
            sql = "INSERT INTO quiz_questions (id, quiz_id, text, correct_answer) VALUES (%s, %s, %s, %s)"
            val = (fake.uuid4(), quiz[0], fake.sentence(), fake.word())
            cur.execute(sql, val)
    conn.commit()
    print("Quiz questions inserted successfully")

def retrieve_quiz_questions():
    cur.execute("SELECT * FROM quiz_questions")
    quiz_questions = cur.fetchall()
    print(f"{len(quiz_questions)} quiz questions retrieved successfully")
    return quiz_questions

def generate_enrollments(users):
    for user in users:
        if user[3] == "student":
            cur.execute("SELECT id FROM courses ORDER BY random() LIMIT %s", (NUM_ENROLLMENTS_PER_USER,))
            course_ids = cur.fetchall()
            for course_id in course_ids:
                sql = "INSERT INTO enrollments (id, user_id, course_id, enrollment_date, progress) VALUES (%s, %s, %s, %s, %s)"
                val = (fake.uuid4(), user[0], course_id[0], fake.past_date(), f"{random.randint(0, 100)}%")
                cur.execute(sql, val)
    conn.commit()
    print("Enrollments generated successfully")

def retrieve_enrollments():
    cur.execute("SELECT * FROM enrollments")
    enrollments = cur.fetchall()
    print(f"{len(enrollments)} enrollments retrieved successfully")
    return enrollments

def main():
    measure_time("Drop Tables", drop_tables)
    measure_time("Create Tables", create_tables)
    measure_time("Insert Users", insert_users)
    users = []
    measure_time("Retrieve Users", lambda: users.extend(retrieve_users()))
    measure_time("Insert Courses", lambda: insert_courses(users))
    courses = []
    measure_time("Retrieve Courses", lambda: courses.extend(retrieve_courses()))
    measure_time("Insert Lessons", lambda: insert_lessons(courses))
    lessons = []
    measure_time("Retrieve Lessons", lambda: lessons.extend(retrieve_lessons()))
    measure_time("Insert Quizzes", lambda: insert_quizzes(lessons))
    quizzes = []
    measure_time("Retrieve Quizzes", lambda: quizzes.extend(retrieve_quizzes()))
    measure_time("Insert Quiz Questions", lambda: insert_quiz_questions(quizzes))
    quiz_questions = []
    measure_time("Retrieve Quiz Questions", lambda: quiz_questions.extend(retrieve_quiz_questions()))
    measure_time("Generate Enrollments", lambda: generate_enrollments(users))
    enrollments = []
    measure_time("Retrieve Enrollments", lambda: enrollments.extend(retrieve_enrollments()))

    # Plotting the results
    operations, durations = zip(*timings)
    plt.figure(figsize=(12, 8))
    plt.barh(operations, durations, color='skyblue')
    plt.xlabel('Time (seconds)')
    plt.title('Performance of PostgreSQL Database Operations')
    plt.grid(axis='x')
    plt.show()
    print('Performance test completed')

if __name__ == '__main__':
    main()
