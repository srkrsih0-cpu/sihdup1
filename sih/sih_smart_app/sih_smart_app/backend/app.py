# File: backend/app.py
import os
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from deepface import DeepFace
from config import Config
from models import db, User, Institution, Branch, Semester, Subject, ClassSchedule, AttendanceRecord
from datetime import time, datetime, date
import google.generativeai as genai

# Add security imports
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from functools import wraps
import re
import secrets

UPLOAD_FOLDER = 'uploads'
KNOWN_FACES_DIR = 'known_faces'
for folder in [UPLOAD_FOLDER, KNOWN_FACES_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Add security configuration
    Talisman(app)
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["100 per hour"]
    )
    limiter.init_app(app)
    
    # Generate a secret key for CSRF protection
    app.secret_key = secrets.token_hex(16)
    
    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    
    # Add input validation functions
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def validate_phone(phone):
        pattern = r'^\+?[1-9]\d{1,14}$'
        return re.match(pattern, phone) is not None
        
    def validate_password(password):
        # Password should be at least 8 characters with at least one uppercase, one lowercase, one digit, and one special character
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True
        
    def validate_college_id(college_id):
        # College ID should be alphanumeric and 3-20 characters long
        pattern = r'^[a-zA-Z0-9]{3,20}$'
        return re.match(pattern, college_id) is not None

    # Add authentication decorator
    def require_admin(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple authentication check - in production, use proper JWT
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"message": "Missing authorization header"}), 401
            # In a real implementation, we would validate the token here
            return f(*args, **kwargs)
        return decorated_function

    def call_generative_ai(prompt):
        # IMPORTANT: Replace "YOUR_API_KEY_HERE" with your key from Google AI Studio
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCYPytGT-Qzj4WaDEKjwlBZw9VWDhS7d2U")
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
            print("WARNING: Using simulated AI. Please add your Gemini API Key.")
            return "1. Review notes from your weakest subject. 2. Do a 20-minute practice session."
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # Use the newer, more available model name
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            return response.text.replace('*', '').replace('#', '')
        except Exception as e:
            print("Error calling Gemini API: " + str(e))
            return "1. Error fetching AI suggestion. 2. Check API key and network."

    # --- ROUTES ---



    
    @app.route('/api/student/<int:user_id>/profile', methods=['POST'])
    def update_student_profile(user_id):
        user = User.query.get(user_id)
        if not user: 
            return jsonify({"message": "Student not found"}), 404
        data = request.get_json()
        
        # Validate input
        career_goal = data.get('career_goal')
        interests = data.get('interests')
        weak_subjects = data.get('weak_subjects')
        
        # Basic validation - ensure fields are not empty
        if not career_goal or not interests or not weak_subjects:
            return jsonify({"message": "All fields are required"}), 400
            
        # Length validation
        if len(career_goal) > 100:
            return jsonify({"message": "Career goal must be less than 100 characters"}), 400
        if len(interests) > 200:
            return jsonify({"message": "Interests must be less than 200 characters"}), 400
        if len(weak_subjects) > 200:
            return jsonify({"message": "Weak subjects must be less than 200 characters"}), 400
            
        user.career_goal = career_goal
        user.interests = interests
        user.weak_subjects = weak_subjects
        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200

    @app.route('/api/teacher/<int:teacher_id>/timetable/today', methods=['GET'])
    def get_teacher_timetable_today(teacher_id):
        today = date.today()
        todays_classes = ClassSchedule.query.filter_by(teacher_id=teacher_id, day_of_week=today.weekday()).order_by(ClassSchedule.start_time).all()
        classes_list = []
        for class_item in todays_classes:
            attendance_taken = AttendanceRecord.query.filter_by(class_id=class_item.id, date=today).first() is not None
            classes_list.append({
                "id": class_item.id, "title": class_item.subject.name, "course_code": class_item.subject.course_code,
                "room": class_item.room, "start_time": class_item.start_time.strftime("%I:%M %p"),
                "end_time": class_item.end_time.strftime("%I:%M %p"), "attendance_taken": attendance_taken
            })
        return jsonify(classes_list)

    @app.route('/api/class/<int:class_id>/roster', methods=['GET'])
    def get_class_roster(class_id):
        class_schedule = ClassSchedule.query.get(class_id)
        if not class_schedule: return jsonify({"message": "Class not found"}), 404
        students = class_schedule.subject.semester.students
        student_list = [{"id": s.id, "name": s.name, "college_id": s.college_id} for s in students]
        return jsonify(student_list)

    @app.route('/api/class/<int:class_id>/attendance', methods=['GET'])
    def get_attendance_record(class_id):
        today = date.today()
        records = AttendanceRecord.query.filter_by(class_id=class_id, date=today).all()
        if not records: return jsonify([]), 200
        attendance_list = [{"student_name": r.student.name, "college_id": r.student.college_id, "status": r.status} for r in records]
        return jsonify(attendance_list)

    @app.route('/api/mark_attendance', methods=['POST'])
    def mark_attendance():
        if 'attendance_photo' not in request.files: return jsonify({"message": "No photo sent"}), 400
        file = request.files['attendance_photo']
        if file.filename == '': return jsonify({"message": "No selected file"}), 400
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        try:
            dfs = DeepFace.find(img_path=filepath, db_path=KNOWN_FACES_DIR, enforce_detection=False)
            present_students = set()
            for df in dfs:
                if not df.empty:
                    best_match_path = df.iloc[0].identity
                    name = os.path.splitext(os.path.basename(best_match_path))[0]
                    present_students.add(name)
            return jsonify({"message": "Faces recognized!", "present": list(present_students)}), 200
        except Exception as e:
            return jsonify({"message": "Error during recognition: " + str(e)}), 500

    @app.route('/api/save_attendance', methods=['POST'])
    def save_attendance():
        data = request.get_json()
        class_id, attendance_data = data.get('class_id'), data.get('attendance')
        if not class_id or not attendance_data: return jsonify({"message": "Missing data"}), 400
        try:
            today = date.today()
            for student_name, is_present in attendance_data.items():
                student = User.query.filter_by(name=student_name).first()
                if not student: continue
                record = AttendanceRecord.query.filter_by(student_id=student.id, class_id=class_id, date=today).first()
                status = "present" if is_present else "absent"
                if record:
                    record.status, record.timestamp = status, datetime.utcnow()
                else:
                    db.session.add(AttendanceRecord(student_id=student.id, class_id=class_id, status=status, date=today))
            db.session.commit()
            return jsonify({"message": "Attendance saved!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "An error occurred: " + str(e)}), 500

    # CRUD operations for Institutions
    @app.route('/api/admin/institutions', methods=['GET'])
    @require_admin
    def get_institutions():
        institutions = Institution.query.all()
        return jsonify([{
            'id': inst.id,
            'name': inst.name
        } for inst in institutions])

    @app.route('/api/admin/institutions', methods=['POST'])
    @require_admin
    def create_institution():
        data = request.get_json()
        name = data.get('name')
        
        # Validate input
        if not name or len(name) < 3:
            return jsonify({"message": "Invalid institution name"}), 400
            
        institution = Institution(name=name)
        db.session.add(institution)
        db.session.commit()
        return jsonify({"message": "Institution created successfully", "id": institution.id}), 201

    @app.route('/api/admin/institutions/<int:id>', methods=['PUT'])
    @require_admin
    def update_institution(id):
        institution = Institution.query.get(id)
        if not institution:
            return jsonify({"message": "Institution not found"}), 404
            
        data = request.get_json()
        name = data.get('name')
        
        # Validate input
        if not name or len(name) < 3:
            return jsonify({"message": "Invalid institution name"}), 400
            
        institution.name = name
        db.session.commit()
        return jsonify({"message": "Institution updated successfully"})

    @app.route('/api/admin/institutions/<int:id>', methods=['DELETE'])
    @require_admin
    def delete_institution(id):
        institution = Institution.query.get(id)
        if not institution:
            return jsonify({"message": "Institution not found"}), 404
            
        db.session.delete(institution)
        db.session.commit()
        return jsonify({"message": "Institution deleted successfully"})

    # CRUD operations for Branches
    @app.route('/api/admin/branches', methods=['GET'])
    @require_admin
    def get_branches():
        institution_id = request.args.get('institution_id')
        if institution_id:
            branches = Branch.query.filter_by(institution_id=institution_id).all()
        else:
            branches = Branch.query.all()
            
        return jsonify([{
            'id': branch.id,
            'name': branch.name,
            'institution_id': branch.institution_id
        } for branch in branches])

    @app.route('/api/admin/branches', methods=['POST'])
    @require_admin
    def create_branch():
        data = request.get_json()
        name = data.get('name')
        institution_id = data.get('institution_id')
        
        # Validate input
        if not name or len(name) < 2:
            return jsonify({"message": "Invalid branch name"}), 400
        if not institution_id:
            return jsonify({"message": "Institution ID is required"}), 400
            
        branch = Branch(name=name, institution_id=institution_id)
        db.session.add(branch)
        db.session.commit()
        return jsonify({"message": "Branch created successfully", "id": branch.id}), 201

    @app.route('/api/admin/branches/<int:id>', methods=['PUT'])
    @require_admin
    def update_branch(id):
        branch = Branch.query.get(id)
        if not branch:
            return jsonify({"message": "Branch not found"}), 404
            
        data = request.get_json()
        name = data.get('name')
        institution_id = data.get('institution_id')
        
        # Validate input
        if not name or len(name) < 2:
            return jsonify({"message": "Invalid branch name"}), 400
        if not institution_id:
            return jsonify({"message": "Institution ID is required"}), 400
            
        branch.name = name
        branch.institution_id = institution_id
        db.session.commit()
        return jsonify({"message": "Branch updated successfully"})

    @app.route('/api/admin/branches/<int:id>', methods=['DELETE'])
    @require_admin
    def delete_branch(id):
        branch = Branch.query.get(id)
        if not branch:
            return jsonify({"message": "Branch not found"}), 404
            
        db.session.delete(branch)
        db.session.commit()
        return jsonify({"message": "Branch deleted successfully"})

    # CRUD operations for Semesters
    @app.route('/api/admin/semesters', methods=['GET'])
    @require_admin
    def get_semesters():
        branch_id = request.args.get('branch_id')
        if branch_id:
            semesters = Semester.query.filter_by(branch_id=branch_id).all()
        else:
            semesters = Semester.query.all()
            
        return jsonify([{
            'id': semester.id,
            'number': semester.number,
            'branch_id': semester.branch_id
        } for semester in semesters])

    @app.route('/api/admin/semesters', methods=['POST'])
    @require_admin
    def create_semester():
        data = request.get_json()
        number = data.get('number')
        branch_id = data.get('branch_id')
        
        # Validate input
        if not isinstance(number, int) or number < 1 or number > 10:
            return jsonify({"message": "Invalid semester number"}), 400
        if not branch_id:
            return jsonify({"message": "Branch ID is required"}), 400
            
        semester = Semester(number=number, branch_id=branch_id)
        db.session.add(semester)
        db.session.commit()
        return jsonify({"message": "Semester created successfully", "id": semester.id}), 201

    @app.route('/api/admin/semesters/<int:id>', methods=['PUT'])
    @require_admin
    def update_semester(id):
        semester = Semester.query.get(id)
        if not semester:
            return jsonify({"message": "Semester not found"}), 404
            
        data = request.get_json()
        number = data.get('number')
        branch_id = data.get('branch_id')
        
        # Validate input
        if not isinstance(number, int) or number < 1 or number > 10:
            return jsonify({"message": "Invalid semester number"}), 400
        if not branch_id:
            return jsonify({"message": "Branch ID is required"}), 400
            
        semester.number = number
        semester.branch_id = branch_id
        db.session.commit()
        return jsonify({"message": "Semester updated successfully"})

    @app.route('/api/admin/semesters/<int:id>', methods=['DELETE'])
    @require_admin
    def delete_semester(id):
        semester = Semester.query.get(id)
        if not semester:
            return jsonify({"message": "Semester not found"}), 404
            
        db.session.delete(semester)
        db.session.commit()
        return jsonify({"message": "Semester deleted successfully"})

    # CRUD operations for Subjects
    @app.route('/api/admin/subjects', methods=['GET'])
    @require_admin
    def get_subjects():
        semester_id = request.args.get('semester_id')
        if semester_id:
            subjects = Subject.query.filter_by(semester_id=semester_id).all()
        else:
            subjects = Subject.query.all()
            
        return jsonify([{
            'id': subject.id,
            'name': subject.name,
            'course_code': subject.course_code,
            'semester_id': subject.semester_id
        } for subject in subjects])

    @app.route('/api/admin/subjects', methods=['POST'])
    @require_admin
    def create_subject():
        data = request.get_json()
        name = data.get('name')
        course_code = data.get('course_code')
        semester_id = data.get('semester_id')
        
        # Validate input
        if not name or len(name) < 2:
            return jsonify({"message": "Invalid subject name"}), 400
        if not course_code or len(course_code) < 2:
            return jsonify({"message": "Invalid course code"}), 400
        if not semester_id:
            return jsonify({"message": "Semester ID is required"}), 400
            
        subject = Subject(name=name, course_code=course_code, semester_id=semester_id)
        db.session.add(subject)
        db.session.commit()
        return jsonify({"message": "Subject created successfully", "id": subject.id}), 201

    @app.route('/api/admin/subjects/<int:id>', methods=['PUT'])
    @require_admin
    def update_subject(id):
        subject = Subject.query.get(id)
        if not subject:
            return jsonify({"message": "Subject not found"}), 404
            
        data = request.get_json()
        name = data.get('name')
        course_code = data.get('course_code')
        semester_id = data.get('semester_id')
        
        # Validate input
        if not name or len(name) < 2:
            return jsonify({"message": "Invalid subject name"}), 400
        if not course_code or len(course_code) < 2:
            return jsonify({"message": "Invalid course code"}), 400
        if not semester_id:
            return jsonify({"message": "Semester ID is required"}), 400
            
        subject.name = name
        subject.course_code = course_code
        subject.semester_id = semester_id
        db.session.commit()
        return jsonify({"message": "Subject updated successfully"})

    @app.route('/api/admin/subjects/<int:id>', methods=['DELETE'])
    @require_admin
    def delete_subject(id):
        subject = Subject.query.get(id)
        if not subject:
            return jsonify({"message": "Subject not found"}), 404
            
        db.session.delete(subject)
        db.session.commit()
        return jsonify({"message": "Subject deleted successfully"})

    # CRUD operations for Class Schedules
    @app.route('/api/admin/schedules', methods=['GET'])
    @require_admin
    def get_schedules():
        subject_id = request.args.get('subject_id')
        teacher_id = request.args.get('teacher_id')
        
        query = ClassSchedule.query
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
            
        schedules = query.all()
            
        return jsonify([{
            'id': schedule.id,
            'subject_id': schedule.subject_id,
            'teacher_id': schedule.teacher_id,
            'room': schedule.room,
            'day_of_week': schedule.day_of_week,
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M')
        } for schedule in schedules])

    @app.route('/api/admin/schedules', methods=['POST'])
    @require_admin
    def create_schedule():
        data = request.get_json()
        subject_id = data.get('subject_id')
        teacher_id = data.get('teacher_id')
        room = data.get('room')
        day_of_week = data.get('day_of_week')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Validate input
        if not subject_id:
            return jsonify({"message": "Subject ID is required"}), 400
        if not teacher_id:
            return jsonify({"message": "Teacher ID is required"}), 400
        if not isinstance(day_of_week, int) or day_of_week < 0 or day_of_week > 6:
            return jsonify({"message": "Invalid day of week"}), 400
        if not start_time or not end_time:
            return jsonify({"message": "Start time and end time are required"}), 400
            
        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            return jsonify({"message": "Invalid time format. Use HH:MM"}), 400
            
        schedule = ClassSchedule(
            subject_id=subject_id,
            teacher_id=teacher_id,
            room=room,
            day_of_week=day_of_week,
            start_time=start_time_obj,
            end_time=end_time_obj
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify({"message": "Schedule created successfully", "id": schedule.id}), 201

    @app.route('/api/admin/schedules/<int:id>', methods=['PUT'])
    @require_admin
    def update_schedule(id):
        schedule = ClassSchedule.query.get(id)
        if not schedule:
            return jsonify({"message": "Schedule not found"}), 404
            
        data = request.get_json()
        subject_id = data.get('subject_id')
        teacher_id = data.get('teacher_id')
        room = data.get('room')
        day_of_week = data.get('day_of_week')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Validate input
        if not subject_id:
            return jsonify({"message": "Subject ID is required"}), 400
        if not teacher_id:
            return jsonify({"message": "Teacher ID is required"}), 400
        if not isinstance(day_of_week, int) or day_of_week < 0 or day_of_week > 6:
            return jsonify({"message": "Invalid day of week"}), 400
        if not start_time or not end_time:
            return jsonify({"message": "Start time and end time are required"}), 400
            
        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            return jsonify({"message": "Invalid time format. Use HH:MM"}), 400
            
        schedule.subject_id = subject_id
        schedule.teacher_id = teacher_id
        schedule.room = room
        schedule.day_of_week = day_of_week
        schedule.start_time = start_time_obj
        schedule.end_time = end_time_obj
        
        db.session.commit()
        return jsonify({"message": "Schedule updated successfully"})

    @app.route('/api/admin/schedules/<int:id>', methods=['DELETE'])
    @require_admin
    def delete_schedule(id):
        schedule = ClassSchedule.query.get(id)
        if not schedule:
            return jsonify({"message": "Schedule not found"}), 404
            
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"message": "Schedule deleted successfully"})

    # Bulk import for students
    @app.route('/api/admin/upload/students', methods=['POST'])
    @require_admin
    @limiter.limit("10 per hour")
    def upload_students():
        if 'file' not in request.files:
            return jsonify({"message": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file selected"}), 400
            
        # Check file extension
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            return jsonify({"message": "Invalid file format. Please upload CSV or Excel file"}), 400
            
        try:
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process file based on extension
            import pandas as pd
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
                
            # Validate required columns
            required_columns = ['college_id', 'name', 'email', 'phone', 'branch_code', 'semester_number', 'password']
            if not all(col in df.columns for col in required_columns):
                return jsonify({"message": "Missing required columns. Required: " + str(required_columns)}), 400
                
            # Process each row
            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Validate data
                    if not row['college_id'] or not row['name']:
                        errors.append("Row " + str(index+1) + ": Missing required fields")
                        continue
                        
                    # Check if student already exists
                    existing_student = User.query.filter_by(college_id=row['college_id'], role='student').first()
                    if existing_student:
                        errors.append(f"Row {index+1}: Student with college_id {row['college_id']} already exists")
                        continue
                        
                    # Find branch
                    branch = Branch.query.filter_by(name=row['branch_code']).first()
                    if not branch:
                        errors.append(f"Row {index+1}: Branch {row['branch_code']} not found")
                        continue
                        
                    # Find semester
                    semester = Semester.query.filter_by(branch_id=branch.id, number=row['semester_number']).first()
                    if not semester:
                        errors.append(f"Row {index+1}: Semester {row['semester_number']} not found for branch {row['branch_code']}")
                        continue
                        
                    # Create student
                    student = User(
                        college_id=row['college_id'],
                        name=row['name'],
                        password=row['password'],
                        role='student',
                        institution_id=branch.institution_id,
                        branch_id=branch.id,
                        current_semester_id=semester.id
                    )
                    
                    # Add email and phone if provided
                    if 'email' in row and row['email']:
                        student.email = row['email']
                    if 'phone' in row and row['phone']:
                        student.phone = row['phone']
                        
                    db.session.add(student)
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index+1}: {str(e)}")
                    
            db.session.commit()
            
            # Clean up temporary file
            os.remove(filepath)
            
            return jsonify({
                "message": f"Processed {len(df)} rows. Created {created_count} students.",
                "errors": errors
            }), 200
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500

    # Bulk import for teachers
    @app.route('/api/admin/upload/teachers', methods=['POST'])
    @require_admin
    @limiter.limit("10 per hour")
    def upload_teachers():
        if 'file' not in request.files:
            return jsonify({"message": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file selected"}), 400
            
        # Check file extension
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            return jsonify({"message": "Invalid file format. Please upload CSV or Excel file"}), 400
            
        try:
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process file based on extension
            import pandas as pd
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
                
            # Validate required columns
            required_columns = ['college_id', 'name', 'email', 'phone', 'department', 'designation', 'password']
            if not all(col in df.columns for col in required_columns):
                return jsonify({"message": f"Missing required columns. Required: {required_columns}"}), 400
                
            # Process each row
            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Validate data
                    if not row['college_id'] or not row['name']:
                        errors.append(f"Row {index+1}: Missing required fields")
                        continue
                        
                    # Check if teacher already exists
                    existing_teacher = User.query.filter_by(college_id=row['college_id'], role='teacher').first()
                    if existing_teacher:
                        errors.append(f"Row {index+1}: Teacher with college_id {row['college_id']} already exists")
                        continue
                        
                    # Find institution
                    institution = Institution.query.filter_by(name=row['department']).first()
                    if not institution:
                        errors.append(f"Row {index+1}: Institution {row['department']} not found")
                        continue
                        
                    # Create teacher
                    teacher = User(
                        college_id=row['college_id'],
                        name=row['name'],
                        password=row['password'],
                        role='teacher',
                        institution_id=institution.id
                    )
                    
                    # Add email and phone if provided
                    if 'email' in row and row['email']:
                        teacher.email = row['email']
                    if 'phone' in row and row['phone']:
                        teacher.phone = row['phone']
                    if 'designation' in row and row['designation']:
                        teacher.designation = row['designation']
                        
                    db.session.add(teacher)
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index+1}: {str(e)}")
                    
            db.session.commit()
            
            # Clean up temporary file
            os.remove(filepath)
            
            return jsonify({
                "message": f"Processed {len(df)} rows. Created {created_count} teachers.",
                "errors": errors
            }), 200
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500

    # Bulk import for timetable
    @app.route('/api/admin/upload/timetable', methods=['POST'])
    @require_admin
    @limiter.limit("10 per hour")
    def upload_timetable():
        if 'file' not in request.files:
            return jsonify({"message": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file selected"}), 400
            
        # Check file extension
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            return jsonify({"message": "Invalid file format. Please upload CSV or Excel file"}), 400
            
        try:
            # Save file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process file based on extension
            import pandas as pd
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
                
            # Validate required columns
            required_columns = ['subject_code', 'teacher_college_id', 'room', 'day_of_week', 'start_time', 'end_time']
            if not all(col in df.columns for col in required_columns):
                return jsonify({"message": f"Missing required columns. Required: {required_columns}"}), 400
                
            # Process each row
            created_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Validate data
                    if not row['subject_code'] or not row['teacher_college_id']:
                        errors.append(f"Row {index+1}: Missing required fields")
                        continue
                        
                    # Find subject
                    subject = Subject.query.filter_by(course_code=row['subject_code']).first()
                    if not subject:
                        errors.append(f"Row {index+1}: Subject with code {row['subject_code']} not found")
                        continue
                        
                    # Find teacher
                    teacher = User.query.filter_by(college_id=row['teacher_college_id'], role='teacher').first()
                    if not teacher:
                        errors.append(f"Row {index+1}: Teacher with college_id {row['teacher_college_id']} not found")
                        continue
                        
                    # Validate day of week
                    try:
                        day_of_week = int(row['day_of_week'])
                        if day_of_week < 0 or day_of_week > 6:
                            errors.append(f"Row {index+1}: Invalid day of week {row['day_of_week']}")
                            continue
                    except ValueError:
                        errors.append(f"Row {index+1}: Invalid day of week format {row['day_of_week']}")
                        continue
                        
                    # Validate time format
                    try:
                        start_time = datetime.strptime(row['start_time'], '%H:%M').time()
                        end_time = datetime.strptime(row['end_time'], '%H:%M').time()
                    except ValueError:
                        errors.append(f"Row {index+1}: Invalid time format. Use HH:MM")
                        continue
                        
                    # Create schedule
                    schedule = ClassSchedule(
                        subject_id=subject.id,
                        teacher_id=teacher.id,
                        room=row['room'] if 'room' in row and row['room'] else None,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time
                    )
                    
                    db.session.add(schedule)
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index+1}: {str(e)}")
                    
            db.session.commit()
            
            # Clean up temporary file
            os.remove(filepath)
            
            return jsonify({
                "message": f"Processed {len(df)} rows. Created {created_count} timetable entries.",
                "errors": errors
            }), 200
            
        except Exception as e:
            # Clean up temporary file if it exists
            if 'filepath' in locals() and os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"message": f"Error processing file: {str(e)}"}), 500

    # Rate limiting for login
    @app.route('/api/login', methods=['POST'])
    @limiter.limit("5 per minute")
    def login():
        data = request.get_json()
        
        # Validate input
        college_id = data.get('college_id')
        password = data.get('password')
        
        if not college_id or not password:
            return jsonify({"message": "College ID and password are required"}), 400
            
        # Validate college ID format
        if not validate_college_id(college_id):
            return jsonify({"message": "Invalid college ID format"}), 400
            
        # Validate password strength (for new registrations)
        # For existing users, we'll check the stored password
        user = User.query.filter_by(college_id=college_id).first()
        if user and user.password == password:
            response = {"message": "Welcome " + user.name + "!", "role": user.role, "user_id": user.id}
            if user.role == 'student':
                response['profile_completed'] = bool(user.career_goal)
            return jsonify(response), 200
        return jsonify({"message": "Invalid credentials"}), 401

    # Enhanced registration endpoint with input validation
    @app.route('/api/register_institution', methods=['POST'])
    @limiter.limit("3 per minute")
    def register_institution():
        data = request.get_json()
        
        # Validate input
        institution_name = data.get('institution_name')
        admin_id = data.get('admin_id')
        admin_name = data.get('admin_name')
        password = data.get('password')
        
        if not all([institution_name, admin_id, admin_name, password]):
            return jsonify({"message": "All fields are required"}), 400
            
        # Validate college ID format
        if not validate_college_id(admin_id):
            return jsonify({"message": "Invalid admin ID format"}), 400
            
        # Validate password strength
        if not validate_password(password):
            return jsonify({"message": "Password must be at least 8 characters with uppercase, lowercase, digit, and special character"}), 400
            
        # Check if institution already exists
        existing_institution = Institution.query.filter_by(name=institution_name).first()
        if existing_institution:
            return jsonify({"message": "Institution already exists"}), 400
            
        # Check if admin already exists
        existing_admin = User.query.filter_by(college_id=admin_id).first()
        if existing_admin:
            return jsonify({"message": "Admin ID already exists"}), 400
            
        new_institution = Institution(name=institution_name)
        db.session.add(new_institution)
        db.session.flush()
        new_admin = User(
            college_id=admin_id, 
            password=password,
            name=admin_name, 
            role='admin', 
            institution_id=new_institution.id
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"message": "Institution registered successfully!"}), 201

    # Assign teacher to subject for a semester
    @app.route('/api/admin/assign_teacher', methods=['POST'])
    @require_admin
    def assign_teacher():
        data = request.get_json()
        teacher_id = data.get('teacher_id')
        subject_id = data.get('subject_id')
        
        if not teacher_id or not subject_id:
            return jsonify({"message": "Teacher ID and Subject ID are required"}), 400
            
        # Find the subject
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({"message": "Subject not found"}), 404
            
        # Find the teacher
        teacher = User.query.get(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return jsonify({"message": "Teacher not found"}), 404
            
        # Update the subject's teacher
        subject.teacher_id = teacher_id
        db.session.commit()
        
        return jsonify({"message": "Teacher " + teacher.name + " assigned to subject " + subject.name})

    # Enroll student in semester
    @app.route('/api/admin/enroll_student', methods=['POST'])
    @require_admin
    def enroll_student():
        data = request.get_json()
        student_id = data.get('student_id')
        semester_id = data.get('semester_id')
        
        if not student_id or not semester_id:
            return jsonify({"message": "Student ID and Semester ID are required"}), 400
            
        # Find the student
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return jsonify({"message": "Student not found"}), 404
            
        # Find the semester
        semester = Semester.query.get(semester_id)
        if not semester:
            return jsonify({"message": "Semester not found"}), 404
            
        # Check if already enrolled
        if semester in student.semesters_enrolled:
            return jsonify({"message": "Student already enrolled in this semester"}), 400
            
        # Enroll student
        student.semesters_enrolled.append(semester)
        student.current_semester_id = semester_id
        db.session.commit()
        
        return jsonify({"message": "Student " + student.name + " enrolled in semester " + str(semester.number)})

    # Get student attendance analytics
    @app.route('/api/admin/student/<int:student_id>/analytics', methods=['GET'])
    @require_admin
    def get_student_analytics(student_id):
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return jsonify({"message": "Student not found"}), 404
            
        # Get all attendance records for this student
        attendance_records = AttendanceRecord.query.filter_by(student_id=student_id).all()
        
        # Group by subject
        subject_attendance = {}
        for record in attendance_records:
            class_schedule = record.class_schedule
            subject = class_schedule.subject
            subject_key = subject.name + " (" + subject.course_code + ")"
            
            if subject_key not in subject_attendance:
                subject_attendance[subject_key] = {"total": 0, "present": 0}
                
            subject_attendance[subject_key]["total"] += 1
            if record.status == "present":
                subject_attendance[subject_key]["present"] += 1
                
        # Calculate percentages
        for subject_key, data in subject_attendance.items():
            if data["total"] > 0:
                data["percentage"] = round((data["present"] / data["total"]) * 100, 2)
            else:
                data["percentage"] = 0
                
        return jsonify(subject_attendance)

    # Get teacher class analytics
    @app.route('/api/teacher/<int:teacher_id>/analytics', methods=['GET'])
    def get_teacher_analytics(teacher_id):
        teacher = User.query.get(teacher_id)
        if not teacher or teacher.role != 'teacher':
            return jsonify({"message": "Teacher not found"}), 404
            
        # Get all classes taught by this teacher
        classes = ClassSchedule.query.filter_by(teacher_id=teacher_id).all()
        
        # Get attendance records for all classes
        class_analytics = []
        for class_schedule in classes:
            subject = class_schedule.subject
            records = AttendanceRecord.query.filter_by(class_id=class_schedule.id).all()
            
            total_classes = len(set(record.date for record in records))
            student_attendance = {}
            
            for record in records:
                student_name = record.student.name
                if student_name not in student_attendance:
                    student_attendance[student_name] = {"total": 0, "present": 0}
                student_attendance[student_name]["total"] += 1
                if record.status == "present":
                    student_attendance[student_name]["present"] += 1
                    
            # Calculate percentages for each student
            for student_name, data in student_attendance.items():
                if data["total"] > 0:
                    data["percentage"] = round((data["present"] / data["total"]) * 100, 2)
                else:
                    data["percentage"] = 0
                    
            class_analytics.append({
                "subject": subject.name + " (" + subject.course_code + ")",
                "room": class_schedule.room,
                "total_classes": total_classes,
                "students": student_attendance
            })
            
        return jsonify(class_analytics)

    # Get attendance records for a specific class and date
    @app.route('/api/class/<int:class_id>/attendance/<date_string>', methods=['GET'])
    def get_class_attendance_by_date(class_id, date_string):
        # Parse the date string
        try:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
            
        class_schedule = ClassSchedule.query.get(class_id)
        if not class_schedule:
            return jsonify({"message": "Class not found"}), 404
            
        records = AttendanceRecord.query.filter_by(class_id=class_id, date=date_obj).all()
        attendance_list = []
        
        for record in records:
            attendance_list.append({
                "student_id": record.student_id,
                "student_name": record.student.name,
                "college_id": record.student.college_id,
                "status": record.status
            })
            
        return jsonify(attendance_list)

    # Get overall attendance statistics for a student
    @app.route('/api/student/<int:student_id>/attendance/stats', methods=['GET'])
    def get_student_attendance_stats(student_id):
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return jsonify({"message": "Student not found"}), 404
            
        # Get all attendance records for this student
        records = AttendanceRecord.query.filter_by(student_id=student_id).all()
        
        # Calculate overall statistics
        total_classes = len(records)
        present_classes = len([r for r in records if r.status == 'present'])
        
        if total_classes > 0:
            overall_percentage = round((present_classes / total_classes) * 100, 2)
        else:
            overall_percentage = 0
            
        # Calculate statistics by subject
        subject_stats = {}
        for record in records:
            subject = record.class_schedule.subject
            subject_key = f"{subject.name} ({subject.course_code})"
            
            if subject_key not in subject_stats:
                subject_stats[subject_key] = {"total": 0, "present": 0}
                
            subject_stats[subject_key]["total"] += 1
            if record.status == "present":
                subject_stats[subject_key]["present"] += 1
                
        # Calculate percentages for each subject
        for subject_key, stats in subject_stats.items():
            if stats["total"] > 0:
                stats["percentage"] = round((stats["present"] / stats["total"]) * 100, 2)
            else:
                stats["percentage"] = 0
                
        # Calculate classes needed to reach 75% attendance
        classes_needed = 0
        if overall_percentage < 75 and total_classes > 0:
            # Calculate how many more classes need to be attended to reach 75%
            current_present = present_classes
            current_total = total_classes
            target_percentage = 75
            
            # We need to find x such that (current_present + x) / (current_total + x) >= 0.75
            # Solving for x: x >= (0.75 * current_total - current_present) / (1 - 0.75)
            # x >= (0.75 * current_total - current_present) / 0.25
            numerator = (0.75 * current_total) - current_present
            if numerator > 0:
                classes_needed = int(numerator / 0.25) + 1
                
        return jsonify({
            "overall_percentage": overall_percentage,
            "total_classes": total_classes,
            "present_classes": present_classes,
            "classes_needed_for_75_percent": classes_needed,
            "subject_stats": subject_stats
        })

    # Get attendance history for a student
    @app.route('/api/student/<int:student_id>/attendance/history', methods=['GET'])
    def get_student_attendance_history(student_id):
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return jsonify({"message": "Student not found"}), 404
            
        # Get all attendance records for this student, ordered by date
        records = AttendanceRecord.query.filter_by(student_id=student_id).order_by(AttendanceRecord.date.desc()).all()
        
        attendance_history = []
        for record in records:
            attendance_history.append({
                "date": record.date.strftime('%Y-%m-%d'),
                "subject": f"{record.class_schedule.subject.name} ({record.class_schedule.subject.course_code})",
                "status": record.status,
                "class_time": f"{record.class_schedule.start_time.strftime('%H:%M')} - {record.class_schedule.end_time.strftime('%H:%M')}"
            })
            
        return jsonify(attendance_history)

    # Get dynamic AI-powered student routines based on real timetable data
    @app.route('/api/student/<int:user_id>/smart_routine', methods=['GET'])
    def get_smart_routine(user_id):
        user = User.query.get(user_id)
        if not user: 
            return jsonify({"message": "User not found"}), 404
            
        # Get student's attendance stats
        attendance_response = get_student_attendance_stats(user_id)
        attendance_data = attendance_response.get_json()
        
        today = date.today()
        student_classes = ClassSchedule.query.join(Subject).join(Semester).filter(
            Semester.id == user.current_semester_id,
            ClassSchedule.day_of_week == today.weekday()
        ).order_by(ClassSchedule.start_time).all()
        
        routine = [{"time": c.start_time, "title": c.subject.name, "type": "class"} for c in student_classes]
        
        # Create a more comprehensive prompt for the AI
        subject_stats_str = ""
        for subject, stats in attendance_data.get("subject_stats", {}).items():
            subject_stats_str += f"{subject}: {stats['percentage']}% ({stats['present']}/{stats['total']}), "
        
        prompt = (f"You are an academic advisor. A student's goal is '{user.career_goal}', they are weak in '{user.weak_subjects}', and interests are '{user.interests}'. "
                  f"Their current attendance statistics are: {subject_stats_str}. "
                  f"Today is {today.strftime('%A')}. "
                  f"Suggest 2-3 productive, short, numbered tasks for their free periods that will help them improve in weak subjects and achieve their career goals. "
                  f"Consider their attendance statistics and suggest study tasks if below 75%. "
                  f"Example: '1. Task one. 2. Task two.'")
        
        ai_suggestions = call_generative_ai(prompt)
        ai_tasks = [task.strip() for task in ai_suggestions.split('\n') if task and task[0].isdigit()]

        class_times = sorted([c.start_time for c in student_classes] + [c.end_time for c in student_classes])
        free_slots = [t for t in [time(h, 0) for h in range(9, 18)] if not any(class_times[i*2] <= t < class_times[i*2+1] for i in range(len(student_classes)))]
        
        for i, task_title in enumerate(ai_tasks):
            if i < len(free_slots):
                clean_title = '. '.join(task_title.split('. ')[1:]) if '. ' in task_title else task_title
                routine.append({"time": free_slots[i], "title": clean_title, "type": "task"})

        routine.sort(key=lambda x: x['time'])
        formatted_routine = [{"time": item['time'].strftime("%I:%M %p"), "title": item['title'], "type": item['type']} for item in routine]
        branch = Branch.query.get(user.branch_id)
        semester = Semester.query.get(user.current_semester_id)
        
        # Add attendance warning if needed
        warning_message = None
        if attendance_data.get("overall_percentage", 0) < 75:
            classes_needed = attendance_data.get("classes_needed_for_75_percent", 0)
            warning_message = f"Warning: Your overall attendance is {attendance_data['overall_percentage']}%. You need to attend {classes_needed} more classes to reach 75%."
        
        return jsonify({
            "branch": branch.name if branch else "N/A", 
            "semester": f"Semester {semester.number}" if semester else "N/A", 
            "routine": formatted_routine,
            "warning_message": warning_message
        })

    return app

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.first():
        print("Database is empty, creating complete dummy data...")
        try:
            inst = Institution(name="SRKR Engineering College")
            db.session.add(inst)
            db.session.commit()
            
            cs_branch = Branch(name="Computer Science", institution_id=inst.id)
            db.session.add(cs_branch)
            db.session.commit()

            admin = User(college_id='admin', password='password', name='SIH Admin', role='admin', institution_id=inst.id)
            teacher = User(college_id='teacher1', password='password', name='Dr. Smith', role='teacher', institution_id=inst.id)
            student = User(college_id='S001', password='password', name='Test Student', role='student', institution_id=inst.id, branch_id=cs_branch.id)
            db.session.add_all([admin, teacher, student])
            db.session.commit()

            sem5 = Semester(number=5, branch_id=cs_branch.id)
            db.session.add(sem5)
            db.session.commit()
            
            student.current_semester_id = sem5.id
            sem5.students.append(student)
            
            sub1 = Subject(name="Operating Systems", course_code="CS301", semester_id=sem5.id)
            sub2 = Subject(name="Databases", course_code="CS302", semester_id=sem5.id)
            db.session.add_all([sub1, sub2])
            db.session.commit()

            # Friday is weekday 4
            class_today = ClassSchedule(subject_id=sub1.id, teacher_id=teacher.id, room="301A", day_of_week=4, start_time=time(11,0), end_time=time(12,0))
            db.session.add(class_today)
            db.session.commit()

            print("Complete dummy data created successfully!")
        except Exception:
            print(f"!!!!!!!!!! AN ERROR OCCURRED DURING DATABASE SETUP !!!!!!!!!!!")
            print(traceback.format_exc())
            db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True)