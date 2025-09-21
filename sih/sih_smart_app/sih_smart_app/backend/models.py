# File: backend/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Association table for student enrollments in a specific semester
enrollments = db.Table('enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('semester_id', db.Integer, db.ForeignKey('semester.id'), primary_key=True)
)

class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True), nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    # Add missing fields
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    institution = db.relationship('Institution', foreign_keys=[institution_id], backref=db.backref('users', lazy=True))
    
    # Student-specific fields
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=True)
    current_semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=True)
    weak_subjects = db.Column(db.String(200), nullable=True)
    interests = db.Column(db.String(200), nullable=True)
    career_goal = db.Column(db.String(100), nullable=True)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    semesters = db.relationship('Semester', backref='branch', lazy=True)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    subjects = db.relationship('Subject', backref='semester', lazy=True)
    students = db.relationship('User', secondary=enrollments, backref=db.backref('semesters_enrolled', lazy='dynamic'))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_code = db.Column(db.String(50), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    classes = db.relationship('ClassSchedule', backref='subject', lazy=True)

class ClassSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room = db.Column(db.String(50), nullable=True)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    teacher = db.relationship('User', backref='classes_teaching')

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class_schedule.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('User', backref='attendance_records')
    class_schedule = db.relationship('ClassSchedule', backref='attendance')