from flask import Flask, render_template, request, jsonify, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os

# =========================================
# FLASK APP
# =========================================
app = Flask(__name__)

# SECRET KEY
app.secret_key = "job_portal_secret"

# =========================================
# DATABASE CONFIGURATION
# =========================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================================
# UPLOAD FOLDER
# =========================================
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')

# =========================================
# USER TABLE
# =========================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    user_type = db.Column(db.String(50))


# =========================================
# JOB TABLE
# =========================================
class PostedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(200))
    role = db.Column(db.String(200))
    skills = db.Column(db.String(500))
    experience = db.Column(db.String(100))
    location = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    description = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================
# LOAD CSV DATASET
# =========================================
jobs = pd.read_csv('jobs.csv')

jobs['combined'] = (
    jobs['Role'] + ' ' + jobs['Skills']
)

# =========================================
# HOME PAGE
# =========================================
@app.route('/')
def home():
    return redirect('/login')


# =========================================
# LOGIN PAGE
# =========================================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # CHECK EMAIL + PASSWORD ONLY
        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        # LOGIN SUCCESS
        if user:

            session['user'] = user.email
            session['username'] = user.username
            session['type'] = user.user_type

            # AUTO REDIRECT BASED ON DATABASE USER TYPE
            if user.user_type == "job_seeker":
                return redirect('/index')

            elif user.user_type == "recruiter":
                return redirect('/recruiter')

        return '''
        <h2>Invalid Email or Password</h2>
        <a href="/login">Try Again</a>
        '''

    return render_template('login.html')


# =========================================
# SIGNUP PAGE
# =========================================
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        # CHECK EMAIL ALREADY EXISTS
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return '''
            <h2>Email already registered</h2>
            <a href="/signup">Go Back</a>
            '''

        # SAVE USER TO DATABASE
        new_user = User(
            username=username,
            email=email,
            password=password,
            user_type=user_type
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('signup.html')


# =========================================
# JOB SEEKER PAGE
# =========================================
@app.route('/index')
def index():

    # LOGIN CHECK
    if 'user' not in session:
        return redirect('/login')

    # ONLY JOB SEEKER CAN ACCESS
    if session['type'] != 'job_seeker':
        return redirect('/recruiter')

    return render_template('index.html')


# =========================================
# RECRUITER PAGE
# =========================================
@app.route('/recruiter')
def recruiter():

    # LOGIN CHECK
    if 'user' not in session:
        return redirect('/login')

    # ONLY RECRUITER CAN ACCESS
    if session['type'] != 'recruiter':
        return redirect('/index')

    return render_template('recruiter.html')


# =========================================
# LOGOUT
# =========================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# =========================================
# POST JOB
# =========================================
@app.route('/post-job', methods=['POST'])
def post_job():

    # LOGIN CHECK
    if 'user' not in session:
        return redirect('/login')

    # ONLY RECRUITER CAN POST JOBS
    if session['type'] != 'recruiter':
        return redirect('/index')

    company = request.form['company']
    role = request.form['role']
    skills = request.form['skills']
    experience = request.form['experience']
    location = request.form['location']
    salary = request.form['salary']
    description = request.form['description']

    new_job = PostedJob(
        company=company,
        role=role,
        skills=skills,
        experience=experience,
        location=location,
        salary=salary,
        description=description
    )

    db.session.add(new_job)
    db.session.commit()

    return redirect('/recruiter')


# =========================================
# JOB RECOMMENDATION
# =========================================
@app.route('/recommend', methods=['POST'])
def recommend():

    data = request.json

    role = data['role'].lower()

    user_skills = [
        skill.strip().lower()
        for skill in data['skills'].split(',')
    ]

    results = []

    # =========================================
    # CSV JOBS
    # =========================================
    for index, row in jobs.iterrows():

        job_role = str(row['Role']).lower()

        job_skills = [
            skill.strip().lower()
            for skill in str(row['Skills']).split(',')
        ]

        role_score = 0

        if role in job_role:
            role_score = 50

        matched_skills = 0

        for skill in user_skills:
            if skill in job_skills:
                matched_skills += 1

        skill_score = (matched_skills / len(user_skills)) * 50
        total_score = role_score + skill_score

        if total_score >= 30:

            results.append({
                'company': row['Company'],
                'role': row['Role'],
                'skills': row['Skills'],
                'match': round(total_score, 2)
            })

    # =========================================
    # DATABASE JOBS
    # =========================================
    recruiter_jobs = PostedJob.query.all()

    for job in recruiter_jobs:

        job_role = job.role.lower()

        job_skills = [
            skill.strip().lower()
            for skill in job.skills.split(',')
        ]

        role_score = 0

        if role in job_role:
            role_score = 50

        matched_skills = 0

        for skill in user_skills:
            if skill in job_skills:
                matched_skills += 1

        skill_score = (matched_skills / len(user_skills)) * 50
        total_score = role_score + skill_score

        if total_score >= 30:

            results.append({
                'company': job.company,
                'role': job.role,
                'skills': job.skills,
                'match': round(total_score, 2)
            })

    results = sorted(
        results,
        key=lambda x: x['match'],
        reverse=True
    )

    return jsonify(results)


# =========================================
# CHATBOT
# =========================================
@app.route('/chat', methods=['POST'])
def chat():

    data = request.json
    message = data['message'].lower().strip()

    # GREETINGS
    if any(word in message for word in ['hi', 'hello', 'hey']):

        return jsonify({
            'reply': '''
            👋 Hello! Welcome to AI Job Portal

            <br><br>

            Tell me your skills like:
            ✔ python, sql
            ✔ java, spring boot
            ✔ machine learning
            '''
        })

    elif 'how are you' in message:
        return jsonify({'reply': '😊 I am doing great!'})

    elif 'thank' in message:
        return jsonify({'reply': '😊 You are welcome!'})

    elif 'bye' in message:
        return jsonify({'reply': '👋 Goodbye!'})

    # LATEST JOBS
    elif (
        'latest jobs' in message or
        'job updates' in message or
        'recent jobs' in message
    ):

        recent_jobs = PostedJob.query.order_by(
            PostedJob.date_posted.desc()
        ).limit(5).all()

        if not recent_jobs:
            return jsonify({'reply': 'No recruiter jobs posted yet.'})

        response = "<b>Latest Jobs:</b><br><br>"

        for job in recent_jobs:

            response += f"""
            🔹 <b>{job.company}</b><br>
            Role: {job.role}<br>
            Skills: {job.skills}<br>
            Location: {job.location}<br>
            Salary: {job.salary}<br><br>
            """

        return jsonify({'reply': response})

    # SKILL MATCHING
    else:

        user_skills = [
            skill.strip().lower()
            for skill in message.replace(',', ' ').split()
        ]

        matched_jobs = []

        # CSV MATCHING
        for _, row in jobs.iterrows():

            job_skills = str(row['Skills']).lower().split(',')

            matched_count = 0

            for skill in user_skills:
                if skill in job_skills:
                    matched_count += 1

            if matched_count > 0:

                matched_jobs.append({
                    'company': row['Company'],
                    'role': row['Role'],
                    'skills': row['Skills'],
                    'location': 'Not Mentioned',
                    'salary': 'Not Mentioned'
                })

        # DATABASE MATCHING
        recruiter_jobs = PostedJob.query.all()

        for job in recruiter_jobs:

            job_skills = job.skills.lower().split(',')

            matched_count = 0

            for skill in user_skills:
                if skill in job_skills:
                    matched_count += 1

            if matched_count > 0:

                matched_jobs.append({
                    'company': job.company,
                    'role': job.role,
                    'skills': job.skills,
                    'location': job.location,
                    'salary': job.salary
                })

        # REMOVE DUPLICATES
        unique_jobs = []
        seen = set()

        for job in matched_jobs:

            key = (job['company'], job['role'])

            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        # RESPONSE
        if unique_jobs:

            response = "<b>Matching Jobs for your skills:</b><br><br>"

            for job in unique_jobs:

                response += f"""
                🔹 <b>{job['company']}</b><br>
                Role: {job['role']}<br>
                Skills: {job['skills']}<br>
                Location: {job['location']}<br>
                Salary: {job['salary']}<br><br>
                """

            return jsonify({'reply': response})

        else:

            return jsonify({
                'reply': '''
                😅 No matching jobs found.

                <br><br>

                Try:
                ✔ python<br>
                ✔ sql<br>
                ✔ java<br>
                ✔ machine learning
                '''
            })


# =========================================
# RUN APP
# =========================================
if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)