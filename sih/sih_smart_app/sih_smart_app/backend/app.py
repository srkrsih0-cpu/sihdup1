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

UPLOAD_FOLDER = 'uploads'
KNOWN_FACES_DIR = 'known_faces'
for folder in [UPLOAD_FOLDER, KNOWN_FACES_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)
    Migrate(app, db)
    CORS(app)

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
            print(f"Error calling Gemini API: {e}")
            return "1. Error fetching AI suggestion. 2. Check API key and network."

    # --- ROUTES ---
    @app.route('/api/register_institution', methods=['POST'])
    def register_institution():
        data = request.get_json()
        new_institution = Institution(name=data.get('institution_name'))
        db.session.add(new_institution)
        db.session.flush()
        new_admin = User(
            college_id=data.get('admin_id'), password=data.get('password'),
            name=data.get('admin_name'), role='admin', institution_id=new_institution.id
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"message": "Institution registered successfully!"}), 201

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = User.query.filter_by(college_id=data.get('college_id')).first()
        if user and user.password == data.get('password'):
            response = {"message": f"Welcome {user.name}!", "role": user.role, "user_id": user.id}
            if user.role == 'student':
                response['profile_completed'] = bool(user.career_goal)
            return jsonify(response), 200
        return jsonify({"message": "Invalid credentials"}), 401
    
    @app.route('/api/student/<int:user_id>/profile', methods=['POST'])
    def update_student_profile(user_id):
        user = User.query.get(user_id)
        if not user: return jsonify({"message": "Student not found"}), 404
        data = request.get_json()
        user.career_goal = data.get('career_goal')
        user.interests = data.get('interests')
        user.weak_subjects = data.get('weak_subjects')
        db.session.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200

    @app.route('/api/student/<int:user_id>/smart_routine', methods=['GET'])
    def get_smart_routine(user_id):
        user = User.query.get(user_id)
        if not user: return jsonify({"message": "User not found"}), 404
        today = date.today()
        student_classes = ClassSchedule.query.join(Subject).join(Semester).filter(
            Semester.id == user.current_semester_id,
            ClassSchedule.day_of_week == today.weekday()
        ).order_by(ClassSchedule.start_time).all()
        
        routine = [{"time": c.start_time, "title": c.subject.name, "type": "class"} for c in student_classes]
        prompt = (f"You are an academic advisor. A student's goal is '{user.career_goal}', they are weak in '{user.weak_subjects}', and interests are '{user.interests}'. "
                  f"Suggest two productive, short, numbered tasks for their free periods. Example: '1. Task one. 2. Task two.'")
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
        return jsonify({"branch": branch.name if branch else "N/A", "semester": f"Semester {semester.number}" if semester else "N/A", "routine": formatted_routine})
    
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
            return jsonify({"message": f"Error during recognition: {e}"}), 500

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
            return jsonify({"message": f"An error occurred: {e}"}), 500

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