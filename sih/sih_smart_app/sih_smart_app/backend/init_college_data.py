#!/usr/bin/env python3
"""
Initialize the database with sample college data for testing and development.
This script creates sample institutions, branches, semesters, subjects, teachers, and students.
"""

import sys
import os

# Add the current directory to the path so we can import app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Institution, Branch, Semester, Subject, User

def init_college_data():
    """Initialize the database with sample college data."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables and create them fresh
        db.drop_all()
        db.create_all()
        
        # Create a sample institution
        institution = Institution(name="SRKR Engineering College")
        db.session.add(institution)
        db.session.commit()
        
        # Create branches
        cse_branch = Branch(name="Computer Science", institution_id=institution.id)
        ece_branch = Branch(name="Electronics & Communication", institution_id=institution.id)
        mech_branch = Branch(name="Mechanical Engineering", institution_id=institution.id)
        
        db.session.add_all([cse_branch, ece_branch, mech_branch])
        db.session.commit()
        
        # Create semesters for CSE
        semesters_cse = []
        for i in range(1, 9):
            semester = Semester(number=i, branch_id=cse_branch.id)
            semesters_cse.append(semester)
            
        db.session.add_all(semesters_cse)
        db.session.commit()
        
        # Create semesters for ECE
        semesters_ece = []
        for i in range(1, 9):
            semester = Semester(number=i, branch_id=ece_branch.id)
            semesters_ece.append(semester)
            
        db.session.add_all(semesters_ece)
        db.session.commit()
        
        # Create semesters for Mech
        semesters_mech = []
        for i in range(1, 9):
            semester = Semester(number=i, branch_id=mech_branch.id)
            semesters_mech.append(semester)
            
        db.session.add_all(semesters_mech)
        db.session.commit()
        
        # Create subjects for CSE Semester 5
        subjects_cse_sem5 = [
            Subject(name="Operating Systems", course_code="CS301", semester_id=semesters_cse[4].id),
            Subject(name="Databases", course_code="CS302", semester_id=semesters_cse[4].id),
            Subject(name="Computer Networks", course_code="CS303", semester_id=semesters_cse[4].id),
            Subject(name="Software Engineering", course_code="CS304", semester_id=semesters_cse[4].id),
            Subject(name="Mathematical Foundations", course_code="CS305", semester_id=semesters_cse[4].id)
        ]
        
        db.session.add_all(subjects_cse_sem5)
        db.session.commit()
        
        # Create subjects for CSE Semester 6
        subjects_cse_sem6 = [
            Subject(name="Machine Learning", course_code="CS351", semester_id=semesters_cse[5].id),
            Subject(name="Web Technologies", course_code="CS352", semester_id=semesters_cse[5].id),
            Subject(name="Mobile Computing", course_code="CS353", semester_id=semesters_cse[5].id),
            Subject(name="Cyber Security", course_code="CS354", semester_id=semesters_cse[5].id),
            Subject(name="Data Science", course_code="CS355", semester_id=semesters_cse[5].id)
        ]
        
        db.session.add_all(subjects_cse_sem6)
        db.session.commit()
        
        # Create admin user
        admin = User(
            college_id='ADMIN_CSE_001',
            password='admin123',
            name='SIH Admin',
            role='admin',
            institution_id=institution.id
        )
        db.session.add(admin)
        
        # Create sample teachers
        teachers = [
            User(
                college_id='TEA_001',
                password='teacher123',
                name='Dr. B M V Narasimha Raju',
                role='teacher',
                institution_id=institution.id,
                email='raju@srkrec.edu.in',
                phone='9876543210'
            ),
            User(
                college_id='TEA_002',
                password='teacher123',
                name='Smt. K Divya Bhavani',
                role='teacher',
                institution_id=institution.id,
                email='divya@srkrec.edu.in',
                phone='9876543211'
            ),
            User(
                college_id='TEA_003',
                password='teacher123',
                name='Dr. D N S Ravi Teja',
                role='teacher',
                institution_id=institution.id,
                email='raviteja@srkrec.edu.in',
                phone='9876543212'
            )
        ]
        
        db.session.add_all(teachers)
        db.session.commit()
        
        # Create sample students for CSE Semester 5
        students_cse_sem5 = [
            User(
                college_id='21B81A0501',
                password='student123',
                name='John Doe',
                role='student',
                institution_id=institution.id,
                branch_id=cse_branch.id,
                current_semester_id=semesters_cse[4].id,
                email='john@srkrec.edu.in',
                phone='9876543213',
                career_goal='Software Developer',
                interests='Web Development, AI',
                weak_subjects='Mathematics'
            ),
            User(
                college_id='21B81A0502',
                password='student123',
                name='Jane Smith',
                role='student',
                institution_id=institution.id,
                branch_id=cse_branch.id,
                current_semester_id=semesters_cse[4].id,
                email='jane@srkrec.edu.in',
                phone='9876543214',
                career_goal='Data Scientist',
                interests='Machine Learning, Statistics',
                weak_subjects='Networking'
            ),
            User(
                college_id='21B81A0503',
                password='student123',
                name='Robert Johnson',
                role='student',
                institution_id=institution.id,
                branch_id=cse_branch.id,
                current_semester_id=semesters_cse[4].id,
                email='robert@srkrec.edu.in',
                phone='9876543215',
                career_goal='Cyber Security Specialist',
                interests='Ethical Hacking, Network Security',
                weak_subjects='Database Systems'
            )
        ]
        
        db.session.add_all(students_cse_sem5)
        db.session.commit()
        
        # Enroll students in semester
        for student in students_cse_sem5:
            student.semesters_enrolled.append(semesters_cse[4])
            
        db.session.commit()
        
        print("✅ Database initialized successfully with sample data!")
        print("\n📊 Sample Data Created:")
        print(f"  • Institution: {institution.name}")
        print(f"  • Branches: {cse_branch.name}, {ece_branch.name}, {mech_branch.name}")
        print(f"  • Semesters: 8 semesters for each branch")
        print(f"  • Subjects: {len(subjects_cse_sem5)} for CSE Semester 5, {len(subjects_cse_sem6)} for CSE Semester 6")
        print(f"  • Admin: {admin.name} ({admin.college_id})")
        print(f"  • Teachers: {len(teachers)} faculty members")
        print(f"  • Students: {len(students_cse_sem5)} students in CSE Semester 5")
        
        print("\n🔐 Login Credentials:")
        print("  • Admin:")
        print("    - College ID: ADMIN_CSE_001")
        print("    - Password: admin123")
        print("  • Teachers:")
        print("    - College ID: TEA_001 to TEA_003")
        print("    - Password: teacher123")
        print("  • Students:")
        print("    - College ID: 21B81A0501 to 21B81A0503")
        print("    - Password: student123")

if __name__ == '__main__':
    init_college_data()