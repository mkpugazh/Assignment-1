import streamlit as st
import sqlite3
import pandas as pd
from faker import Faker
import random
import matplotlib.pyplot as plt

# Initialize Faker
fake = Faker()

# Database setup
def create_database():
    conn = sqlite3.connect('placement.db')
    cursor = conn.cursor()

    # Create Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            student_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            gender TEXT,
            email TEXT,
            phone TEXT,
            enrollment_year INTEGER,
            course_batch TEXT,
            city TEXT,
            graduation_year INTEGER
        )
    ''')

    # Create Programming Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Programming (
            programming_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            language TEXT,
            problems_solved INTEGER,
            assessments_completed INTEGER,
            mini_projects INTEGER,
            certifications_earned INTEGER,
            latest_project_score INTEGER,
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )
    ''')

    # Create Soft Skills Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SoftSkills (
            soft_skill_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            communication INTEGER,
            teamwork INTEGER,
            presentation INTEGER,
            leadership INTEGER,
            critical_thinking INTEGER,
            interpersonal_skills INTEGER,
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )
    ''')

    # Create Placements Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Placements (
            placement_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            mock_interview_score INTEGER,
            internships_completed INTEGER,
            placement_status TEXT,
            company_name TEXT,
            placement_package REAL,
            interview_rounds_cleared INTEGER,
            placement_date TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )
    ''')

    conn.commit()
    return conn

# Generate synthetic data
def generate_data(conn, num_students=100):
    cursor = conn.cursor()

    for _ in range(num_students):
        # Insert into Students Table
        student_data = (
            fake.name(),
            random.randint(18, 25),
            random.choice(['Male', 'Female', 'Other']),
            fake.email(),
            fake.phone_number(),
            random.randint(2018, 2023),
            random.choice(['Batch A', 'Batch B', 'Batch C']),
            fake.city(),
            random.randint(2022, 2025)
        )
        cursor.execute('''
            INSERT INTO Students (name, age, gender, email, phone, enrollment_year, course_batch, city, graduation_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', student_data)
        student_id = cursor.lastrowid

        # Insert into Programming Table
        programming_data = (
            student_id,
            random.choice(['Python', 'SQL', 'Java']),
            random.randint(0, 200),
            random.randint(0, 20),
            random.randint(0, 10),
            random.randint(0, 5),
            random.randint(0, 100)
        )
        cursor.execute('''
            INSERT INTO Programming (student_id, language, problems_solved, assessments_completed, mini_projects, certifications_earned, latest_project_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', programming_data)

        # Insert into Soft Skills Table
        soft_skills_data = (
            student_id,
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)
        )
        cursor.execute('''
            INSERT INTO SoftSkills (student_id, communication, teamwork, presentation, leadership, critical_thinking, interpersonal_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', soft_skills_data)

        # Insert into Placements Table
        placement_data = (
            student_id,
            random.randint(0, 100),
            random.randint(0, 3),
            random.choice(['Ready', 'Not Ready', 'Placed']),
            fake.company() if random.random() > 0.5 else None,
            random.randint(30000, 120000) if random.random() > 0.5 else None,
            random.randint(1, 5) if random.random() > 0.5 else None,
            fake.date_between(start_date='-1y', end_date='today') if random.random() > 0.5 else None
        )
        cursor.execute('''
            INSERT INTO Placements (student_id, mock_interview_score, internships_completed, placement_status, company_name, placement_package, interview_rounds_cleared, placement_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', placement_data)

    conn.commit()

# Function to view entire database
def view_database(conn):
    st.write("### Students Table")
    students_df = pd.read_sql_query("SELECT * FROM Students", conn)
    students_df.index = students_df.index + 1
    st.dataframe(students_df)

    st.write("### Programming Table")
    programming_df = pd.read_sql_query("SELECT * FROM Programming", conn)
    programming_df.index = programming_df.index + 1
    st.dataframe(programming_df)

    st.write("### Soft Skills Table")
    soft_skills_df = pd.read_sql_query("SELECT * FROM SoftSkills", conn)
    soft_skills_df.index = soft_skills_df.index + 1
    st.dataframe(soft_skills_df)

    st.write("### Placements Table")
    placements_df = pd.read_sql_query("SELECT * FROM Placements", conn)
    placements_df.index = placements_df.index + 1
    st.dataframe(placements_df)

# Function to run SQL queries and display insights
def display_insights(conn):
    st.write("### Insights from the Database")

    # Query 1: Average programming performance per batch
    st.write("#### 1. Average Programming Performance per Batch")
    query1 = '''
        SELECT s.course_batch, AVG(p.problems_solved) AS avg_problems_solved
        FROM Students s
        JOIN Programming p ON s.student_id = p.student_id
        GROUP BY s.course_batch
    '''
    avg_programming_performance = pd.read_sql_query(query1, conn)
    avg_programming_performance.index = avg_programming_performance.index + 1
    st.dataframe(avg_programming_performance)

    # Query 2: Top 5 students ready for placement
    st.write("#### 2. Top 5 Students Ready for Placement")
    query2 = '''
        SELECT s.name, p.problems_solved, ss.communication, ss.teamwork, pl.mock_interview_score
        FROM Students s
        JOIN Programming p ON s.student_id = p.student_id
        JOIN SoftSkills ss ON s.student_id = ss.student_id
        JOIN Placements pl ON s.student_id = pl.student_id
        WHERE pl.placement_status = 'Ready'
        ORDER BY (p.problems_solved + ss.communication + ss.teamwork + pl.mock_interview_score) DESC
        LIMIT 5
    '''
    top_students = pd.read_sql_query(query2, conn)
    top_students.index = top_students.index + 1
    st.dataframe(top_students)

    # Query 3: Distribution of soft skills scores
    st.write("#### 3. Distribution of Soft Skills Scores")
    query3 = '''
        SELECT communication, teamwork, presentation, leadership, critical_thinking, interpersonal_skills
        FROM SoftSkills
    '''
    soft_skills_distribution = pd.read_sql_query(query3, conn)
    soft_skills_distribution.index = soft_skills_distribution.index + 1

    # Plotting the distribution of soft skills scores
    fig, ax = plt.subplots()
    soft_skills_distribution.hist(ax=ax, bins=20, figsize=(10, 10))
    plt.tight_layout()
    st.pyplot(fig)

    # Query 4: Number of students placed per batch
    st.write("#### 4. Number of Students Placed per Batch")
    query4 = '''
        SELECT s.course_batch, COUNT(*) AS students_placed
        FROM Students s
        JOIN Placements pl ON s.student_id = pl.student_id
        WHERE pl.placement_status = 'Placed'
        GROUP BY s.course_batch
    '''
    students_placed = pd.read_sql_query(query4, conn)
    students_placed.index = students_placed.index + 1
    st.dataframe(students_placed)

    # Query 5: Average mock interview score per batch
    st.write("#### 5. Average Mock Interview Score per Batch")
    query5 = '''
        SELECT s.course_batch, AVG(pl.mock_interview_score) AS avg_mock_score
        FROM Students s
        JOIN Placements pl ON s.student_id = pl.student_id
        GROUP BY s.course_batch
    '''
    avg_mock_score = pd.read_sql_query(query5, conn)
    avg_mock_score.index = avg_mock_score.index + 1
    st.dataframe(avg_mock_score)

    # Query 6: Students with the highest number of problems solved
    st.write("#### 6. Students with the Highest Number of Problems Solved")
    query6 = '''
        SELECT s.name, p.problems_solved
        FROM Students s
        JOIN Programming p ON s.student_id = p.student_id
        ORDER BY p.problems_solved DESC
        LIMIT 10
    '''
    top_problem_solvers = pd.read_sql_query(query6, conn)
    top_problem_solvers.index = top_problem_solvers.index + 1
    st.dataframe(top_problem_solvers)

    # Query 7: Students with the highest soft skills scores
    st.write("#### 7. Students with the Highest Soft Skills Scores")
    query7 = '''
        SELECT s.name, (ss.communication + ss.teamwork + ss.presentation + ss.leadership + ss.critical_thinking + ss.interpersonal_skills) / 6 AS avg_soft_skills
        FROM Students s
        JOIN SoftSkills ss ON s.student_id = ss.student_id
        ORDER BY avg_soft_skills DESC
        LIMIT 10
    '''
    top_soft_skills = pd.read_sql_query(query7, conn)
    top_soft_skills.index = top_soft_skills.index + 1
    st.dataframe(top_soft_skills)

    # Query 8: Students with the highest placement packages
    st.write("#### 8. Students with the Highest Placement Packages")
    query8 = '''
        SELECT s.name, pl.placement_package
        FROM Students s
        JOIN Placements pl ON s.student_id = pl.student_id
        WHERE pl.placement_package IS NOT NULL
        ORDER BY pl.placement_package DESC
        LIMIT 10
    '''
    top_packages = pd.read_sql_query(query8, conn)
    top_packages.index = top_packages.index + 1
    st.dataframe(top_packages)

    # Query 9: Students who completed the most internships
    st.write("#### 9. Students Who Completed the Most Internships")
    query9 = '''
        SELECT s.name, pl.internships_completed
        FROM Students s
        JOIN Placements pl ON s.student_id = pl.student_id
        ORDER BY pl.internships_completed DESC
        LIMIT 10
    '''
    top_internships = pd.read_sql_query(query9, conn)
    top_internships.index = top_internships.index + 1
    st.dataframe(top_internships)

    # Query 10: Distribution of placement status
    st.write("#### 10. Distribution of Placement Status")
    query10 = '''
        SELECT placement_status, COUNT(*) AS count
        FROM Placements
        GROUP BY placement_status
    '''
    placement_status_distribution = pd.read_sql_query(query10, conn)
    placement_status_distribution.index = placement_status_distribution.index + 1
    st.dataframe(placement_status_distribution)

    # Plotting the distribution of placement status
    fig, ax = plt.subplots()
    placement_status_distribution.plot(kind='bar', x='placement_status', y='count', ax=ax, legend=False)
    st.pyplot(fig)

# Streamlit App
def main():
    st.title("Placement Eligibility Application")

    # Initialize database and generate data
    conn = create_database()
    generate_data(conn)

    # Sidebar options
    st.sidebar.header("Options")
    view_database_option = st.sidebar.checkbox("View Entire Database")
    view_insights_option = st.sidebar.checkbox("View Insights")

    if view_database_option:
        view_database(conn)
    elif view_insights_option:
        display_insights(conn)
    else:
        # User input for eligibility criteria
        st.sidebar.header("Eligibility Criteria")
        problems_solved = st.sidebar.slider("Minimum Problems Solved", 0, 200, 50)
        soft_skills_score = st.sidebar.slider("Minimum Soft Skills Score", 0, 100, 75)
        mock_interview_score = st.sidebar.slider("Minimum Mock Interview Score", 0, 100, 60)

        # Query to filter eligible students
        query = f'''
            SELECT s.name, s.email, s.phone, p.problems_solved, ss.communication, ss.teamwork, pl.mock_interview_score
            FROM Students s
            JOIN Programming p ON s.student_id = p.student_id
            JOIN SoftSkills ss ON s.student_id = ss.student_id
            JOIN Placements pl ON s.student_id = pl.student_id
            WHERE p.problems_solved >= {problems_solved}
            AND (ss.communication + ss.teamwork) / 2 >= {soft_skills_score}
            AND pl.mock_interview_score >= {mock_interview_score}
        '''
        eligible_students = pd.read_sql_query(query, conn)
        eligible_students.index = eligible_students.index + 1

        # Display results
        st.write("### Eligible Students")
        st.dataframe(eligible_students)

    # Close connection
    conn.close()

if __name__ == "__main__":
    main()