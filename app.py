from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, make_response
from flask_cors import CORS
import sqlite3
import os
from functools import wraps
# import pandas as pd  # Removed Excel-related import
import requests
from datetime import datetime
import traceback
import json




app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration from environment (suitable for Render or other hosts)
# SECRET_KEY should be set in the environment in production
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production')
# Session cookie security can be configured via env (use 'True' in prod with HTTPS)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
CORS(app, supports_credentials=True)





def get_db_connection():
    # Allow configuring the database path via env var (Render uses writable tmp dirs)
    DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.getcwd(), 'students.db'))
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Removed export_to_excel function and its usage

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_roll' not in session:
            return redirect('/login.html')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_roll' not in session:
            return redirect('/login.html')
        if session.get('student_role') != 'admin':
            # JSON for API, redirect for pages
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "error": "Forbidden"}), 403
            return redirect('/dashboard.html')
        return f(*args, **kwargs)
    return decorated_function

def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    roll = data.get('roll')
    password = data.get('password')
    conn = get_db_connection()

    try:
        student = conn.execute('SELECT * FROM students WHERE roll = ? AND password = ?', (roll, password)).fetchone()

        if student:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            branch = student['branch'] if 'branch' in student.keys() and student['branch'] else ''
            conn.execute('''
                INSERT INTO login_activity (roll, name, branch, role, status, time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (roll, student['name'], branch, student['role'] if 'role' in student.keys() else 'student', 'LOGIN', current_time))
            conn.commit()
            # export_to_excel()  # Removed real-time export
            session['student_roll'] = roll
            session['student_name'] = student['name']
            session['student_branch'] = branch  # Store branch in session
            session['student_role'] = student['role'] if 'role' in student.keys() else 'student'
            user_role = student['role'] if 'role' in student.keys() else 'student'
            conn.close()
            return jsonify({
                "success": True,
                "name": student['name'],
                "branch": branch,
                "role": user_role
            })
        else:
            conn.close()
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        traceback.print_exc()
        if conn:
            conn.close()
        return jsonify({"success": False, "message": "Server error occurred"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    if 'student_roll' in session:
        try:
            conn = get_db_connection()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute('''
                INSERT INTO login_activity (roll, name, branch, role, status, time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session.get('student_roll', ''),
                session.get('student_name', ''),
                session.get('student_branch', ''),
                session.get('student_role', 'student'),
                'LOGOUT',
                current_time
            ))
            conn.commit()
            # export_to_excel()  # Removed real-time export
            conn.close()
        except Exception as e:
            traceback.print_exc()

    session.clear()
    response = jsonify({"success": True})
    return add_no_cache_headers(response)

@app.route('/check-auth', methods=['GET'])
def check_auth():
    if 'student_roll' in session:
        return jsonify({
            "authenticated": True,
            "student_roll": session['student_roll'],
            "student_name": session['student_name'],
            "student_branch": session.get('student_branch', ''),
            "student_role": session.get('student_role', 'student')
        })
    return jsonify({"authenticated": False}), 401

@app.route('/')
def index():
    response = make_response(send_from_directory('templetes', 'index.html'))
    return add_no_cache_headers(response)

@app.route('/login.html')
def login_page():
    response = make_response(send_from_directory('templetes', 'login.html'))
    return add_no_cache_headers(response)

@app.route('/auth.js')
def auth_js():
    response = make_response(send_from_directory(os.getcwd(), 'auth.js'))
    return add_no_cache_headers(response)



@app.route('/csedashboard.html')
@login_required
def caidashboard():
    response = make_response(send_from_directory('templetes', 'csedashboard.html'))
    return add_no_cache_headers(response)

@app.route('/ecedashboard.html')
@login_required
def csedashboard():
    response = make_response(send_from_directory('templetes', 'ecedashboard.html'))
    return add_no_cache_headers(response)

@app.route('/dashboard.html')
@login_required
def dashboard():
    # Redirect admin to admin dashboard
    if session.get('student_role') == 'admin':
        return redirect('/admin_dashboard.html')
    # Redirect to appropriate dashboard based on user's branch
    branch = (session.get('student_branch', '') or '')
    # Normalize branch mapping keywords
    if ('computer' in branch and 'ai' in branch) or ('Computer Science and Engineering' in branch):
        return redirect('/csedashboard.html')
    elif 'computer' in branch or 'Electronics and Communication Engineering' in branch:
        return redirect('/ecedashboard.html')
    else:
        # Default to CAI dashboard if branch is not specified
        return redirect('/csedashboard.html')

@app.route('/semester1.html')
@login_required
def semester1():
    response = make_response(send_from_directory('cse_templetes/semester1', 'semester1.html'))
    return add_no_cache_headers(response)

@app.route('/semester2.html')
@login_required
def semester2():
    response = make_response(send_from_directory('cse_templetes/semester2', 'semester2.html'))
    return add_no_cache_headers(response)

@app.route('/semester3.html')
@login_required
def semester3():
    response = make_response(send_from_directory('cse_templetes/semester3', 'semester3.html'))
    return add_no_cache_headers(response)

@app.route('/semester4.html')
@login_required
def semester4():
    response = make_response(send_from_directory('cse_templetes/semester4', 'semester4.html'))
    return add_no_cache_headers(response)

@app.route('/semester5.html')
@login_required
def semester5():
    response = make_response(send_from_directory('cse_templetes/semester5', 'semester5.html'))
    return add_no_cache_headers(response)

@app.route('/semester6.html')
@login_required
def semester6():
    response = make_response(send_from_directory('cse_templetes/semester6', 'semester6.html'))
    return add_no_cache_headers(response)

@app.route('/semester7.html')
@login_required
def semester7():
    response = make_response(send_from_directory('cse_templetes/semester7', 'semester7.html'))
    return add_no_cache_headers(response)

@app.route('/semester8.html')
@login_required
def semester8():
    response = make_response(send_from_directory('cse_templetes/semester8', 'semester8.html'))
    return add_no_cache_headers(response)

@app.route('/m1_page.html')
@login_required
def m1_page():
    response = make_response(send_from_directory('cse_templetes/semester1', 'm1_page.html'))
    return add_no_cache_headers(response)

@app.route('/mp_page.html')
@login_required
def mp_page():
    response = make_response(send_from_directory('cse_templetes/semester1', 'mp_page.html'))
    return add_no_cache_headers(response)

@app.route('/pas_page.html')
@login_required
def pas_page():
    response = make_response(send_from_directory('cse_templetes/semester1', 'pas_page.html'))
    return add_no_cache_headers(response)

@app.route('/pps_page.html')
@login_required
def pps_page():
    response = make_response(send_from_directory('cse_templetes/semester1', 'pps_page.html'))
    return add_no_cache_headers(response)

@app.route('/m2_page.html')
@login_required
def m2_page():
    response = make_response(send_from_directory('cse_templetes/semester2', 'm2_page.html'))
    return add_no_cache_headers(response)

@app.route('/che_page.html')
@login_required
def che_page():
    response = make_response(send_from_directory('cse_templetes/semester2', 'che_page.html'))
    return add_no_cache_headers(response)

@app.route('/ds_page.html')
@login_required
def ds_page():
    response = make_response(send_from_directory('cse_templetes/semester2', 'ds_page.html'))
    return add_no_cache_headers(response)

@app.route('/dslab_page.html')
@login_required
def dslab_page():
    response = make_response(send_from_directory('cse_templetes/semester2', 'dslab_page.html'))
    return add_no_cache_headers(response)

@app.route('/eng_page.html')
@login_required
def eng_page():
    response = make_response(send_from_directory('cse_templetes/semester2', 'eng_page.html'))
    return add_no_cache_headers(response)

@app.route('/bee_page.html')
@login_required
def bee_page():
    response = make_response(send_from_directory('cse_templetes/semester3', 'bee_page.html'))
    return add_no_cache_headers(response)

@app.route('/constitution_page.html')
@login_required
def constitution_page():
    response = make_response(send_from_directory('cse_templetes/semester3', 'constitution_page.html'))
    return add_no_cache_headers(response)

@app.route('/dbms_page.html')
@login_required
def dbms_page():
    response = make_response(send_from_directory('cse_templetes/semester3', 'dbms_page.html'))
    return add_no_cache_headers(response)

@app.route('/dms_page.html')
@login_required
def dms_page():
    response = make_response(send_from_directory('cse_templetes/semester3', 'dms_page.html'))
    return add_no_cache_headers(response)

@app.route('/ece_page.html')
@login_required
def ece_page():
    response = make_response(send_from_directory('cse_templetes/semester3', 'ece_page.html'))
    return add_no_cache_headers(response)

@app.route('/m3_page.html')
@login_required
def m3_page():
    response = make_response(send_from_directory('cse_templetes/semester3', 'm3_page.html'))
    return add_no_cache_headers(response)

@app.route('/python_page.html')
@login_required
def python_page():
    response = make_response(send_from_directory('cse_templetes/semester3', 'python_page.html'))
    return add_no_cache_headers(response)

@app.route('/deld_page.html')
@login_required
def deld_page():
    response = make_response(send_from_directory('cse_templetes/semester4', 'deld_page.html'))
    return add_no_cache_headers(response)

@app.route('/sm_page.html')
@login_required
def sm_page():
    response = make_response(send_from_directory('cse_templetes/semester4', 'sm_page.html'))
    return add_no_cache_headers(response)

@app.route('/daa_page.html')
@login_required
def daa_page():
    return send_from_directory('cse_templetes/semester4', 'daa_page.html')

@app.route('/bwd_page.html')
@login_required
def bwd_page():
    return send_from_directory('cse_templetes/semester4', 'bwd_page.html')

@app.route('/co_page.html')
@login_required
def co_page():
    return send_from_directory('cse_templetes/semester4', 'co_page.html')

@app.route('/conm_page.html')
@login_required
def conm_page():
    return send_from_directory('cse_templetes/semester4', 'conm_page.html')

@app.route('/mea_page.html')
@login_required
def mea_page():
    return send_from_directory('cse_templetes/semester4', 'mea_page.html')

@app.route('/ss_page.html')
@login_required
def ss_page():
    return send_from_directory('cse_templetes/semester4', 'ss_page.html')

@app.route('/os_page.html')
@login_required
def os_page():
    response = make_response(send_from_directory('cse_templetes/semester5', 'os_page.html'))
    return add_no_cache_headers(response)

@app.route('/cn_page.html')
@login_required
def cn_page():
    response = make_response(send_from_directory('cse_templetes/semester5', 'cn_page.html'))
    return add_no_cache_headers(response)

@app.route('/flat_page.html')
@login_required
def flat_page():
    response = make_response(send_from_directory('cse_templetes/semester5', 'flat_page.html'))
    return add_no_cache_headers(response)

@app.route('/se_page.html')
@login_required
def se_page():
    response = make_response(send_from_directory('cse_templetes/semester5', 'se_page.html'))
    return add_no_cache_headers(response)

@app.route('/uhv_page.html')
@login_required
def uhv_page():
    response = make_response(send_from_directory('cse_templetes/semester5', 'uhv_page.html'))
    return add_no_cache_headers(response)

@app.route('/es_page.html')
@login_required
def es_page():
    response = make_response(send_from_directory('cse_templetes/semester1', 'es_page.html'))
    return add_no_cache_headers(response)

@app.route('/eg_page.html')
@login_required
def eg_page():
    response = make_response(send_from_directory('cse_templetes/semester6', 'eg_page.html'))
    return add_no_cache_headers(response)


@app.route('/ai_page.html')
@login_required
def ai_page():
    response = make_response(send_from_directory('cse_templetes/semester6', 'ai_page.html'))
    return add_no_cache_headers(response)

@app.route('/cd_page.html')
@login_required
def cd_page():
    response = make_response(send_from_directory('cse_templetes/semester6', 'cd_page.html'))
    return add_no_cache_headers(response)


@app.route('/cg_page.html')
@login_required
def cg_page():
    response = make_response(send_from_directory('cse_templetes/semester6', 'cg_page.html'))
    return add_no_cache_headers(response)


@app.route('/cns_page.html')
@login_required
def cns_page():
    response = make_response(send_from_directory('cse_templetes/semester6', 'cns_page.html'))
    return add_no_cache_headers(response)


@app.route('/dm_page.html')
@login_required
def dm_page():
    response = make_response(send_from_directory('cse_templetes/semester6', 'dm_page.html'))
    return add_no_cache_headers(response)

@app.route('/ppslab_page.html')
@login_required
def ppslab_page():
    response = make_response(send_from_directory('cse_templetes/semester1', 'ppslab_page.html'))
    return add_no_cache_headers(response)

@app.route('/api/student/<roll>')
def get_student_by_roll(roll):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE roll = ?', (roll,)).fetchone()
    conn.close()
    if student:
        return jsonify(dict(student))
    return jsonify({"error": "Student not found"}), 404


@app.route('/images/<path:filename>')
def serve_images(filename):
    """Serve images from the images folder"""
    response = make_response(send_from_directory('images', filename))
    return add_no_cache_headers(response)

@app.route('/<path:filename>')
def serve_static(filename):
    # Serve CSS and JS files from root
    if filename.endswith(('.css', '.js')):
        response = make_response(send_from_directory(os.getcwd(), filename))
        return add_no_cache_headers(response)
    
    # For any other files, require authentication
    if 'student_roll' not in session:
        return redirect('/login.html')
    
    response = make_response(send_from_directory(os.getcwd(), filename))
    return add_no_cache_headers(response)

# Removed /export-excel endpoint

@app.route('/login-activity', methods=['GET'])
def get_login_activity():
    try:
        conn = get_db_connection()
        activities = conn.execute('SELECT * FROM login_activity ORDER BY time DESC LIMIT 100').fetchall()
        conn.close()
        activity_list = [dict(row) for row in activities]
        return jsonify({"success": True, "activities": activity_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin_dashboard.html')
@login_required
@admin_required
def admin_dashboard():
    response = make_response(send_from_directory('templetes', 'admin_dashboard.html'))
    return add_no_cache_headers(response)

@app.route('/admin_logins.html')
@login_required
@admin_required
def admin_logins():
    response = make_response(send_from_directory('templetes', 'admin_logins.html'))
    return add_no_cache_headers(response)

@app.route('/api/admin/stats', methods=['GET'])
@login_required
@admin_required
def admin_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        total_students = cur.execute("SELECT COUNT(*) FROM students WHERE role = 'student'").fetchone()[0]
        total_admins = cur.execute("SELECT COUNT(*) FROM students WHERE role = 'admin' ").fetchone()[0]
        total_logins = cur.execute("SELECT COUNT(*) FROM login_activity WHERE status = 'LOGIN' and role='student'").fetchone()[0]
        logins_today = cur.execute("SELECT COUNT(*) FROM login_activity WHERE date(time) = date('now') and status = 'LOGIN' and role='student' ").fetchone()[0]
        active_students = cur.execute("SELECT COUNT(*) FROM students WHERE status = 'active' and role = 'student'").fetchone()[0]
        deactive_students = cur.execute("SELECT COUNT(*) FROM students WHERE status = 'deactive'").fetchone()[0]

        # Logins last 7 days (including today)
        login_trend_rows = cur.execute(
            """
            SELECT date(time) AS day, COUNT(*) AS count
            FROM login_activity
            WHERE date(time) >= date('now','-6 day')
            GROUP BY date(time)
            ORDER BY day
            """
        ).fetchall()
        login_trend = [{"day": r[0], "count": r[1]} for r in login_trend_rows]

        # Students by branch (only active students, exclude admins)
        branch_rows = cur.execute(
            """
            SELECT COALESCE(NULLIF(TRIM(branch), ''), 'Unknown') AS branch, COUNT(*)
            FROM students
            WHERE role = 'student' AND status = 'active'
            GROUP BY branch
            ORDER BY COUNT(*) DESC
            """
        ).fetchall()
        by_branch = [{"branch": r[0], "count": r[1]} for r in branch_rows]

        conn.close()
        return jsonify({
            "success": True,
            "stats": {
                "total_students": total_students,
                "active_students": active_students,
                "deactive_students": deactive_students,
                "total_admins": total_admins,
                "total_logins": total_logins,
                "logins_today": logins_today,
                "login_trend": login_trend,
                "by_branch": by_branch
            }
        })
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/logins', methods=['GET'])
@login_required
@admin_required

def admin_logins_api():
    try:
        filter_type = request.args.get('filter', 'today')
        search = (request.args.get('search', '') or '').strip().lower()
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build base SQL for joining login_activity and students
        sql = '''
            SELECT la.id, la.roll, la.name, la.branch, la.role, la.status, la.time as login_time,
                   s.year, s.course, s.email_id, s.mobileno
            FROM login_activity la
            LEFT JOIN students s ON la.roll = s.roll
            WHERE 1=1
        '''
        params = []
        # Filter by date
        if filter_type == 'today':
            sql += " AND date(la.time) = date('now')"
        elif filter_type == 'month':
            sql += " AND strftime('%Y-%m', la.time) = strftime('%Y-%m', 'now')"
        elif filter_type == 'year':
            sql += " AND strftime('%Y', la.time) = strftime('%Y', 'now')"
        # Search filter
        if search:
            sql += " AND (lower(la.name) LIKE ? OR lower(la.roll) LIKE ? OR lower(s.email_id) LIKE ? OR lower(s.mobileno) LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like, like, like])
        sql += " ORDER BY la.id DESC LIMIT 200"
        rows = cursor.execute(sql, params).fetchall()
        logins = [dict(row) for row in rows]
        conn.close()
        return jsonify({"success": True, "logins": logins})
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500
@app.route('/api/admin/students', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_students():
    try:
        if request.method == 'GET':
            q = request.args.get('query', '').strip()
            filter_branch = request.args.get('branch', '').strip()
            filter_year = request.args.get('year', '').strip()
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            limit = max(1, min(limit, 200))
            offset = max(0, offset)

            conn = get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            base_sql = 'SELECT id, name, gender, roll, course, branch, year, role, status, mobileno, email_id, aadhar_no, address, date FROM students WHERE status = "active"'
            where_clauses = []
            params = []
            if q:
                like = f"%{q}%"
                where_clauses.append('(name LIKE ? OR roll LIKE ? OR branch LIKE ? OR email_id LIKE ?)')
                params.extend([like, like, like, like])
            if filter_branch:
                if filter_branch.lower() == 'unknown':
                    where_clauses.append("(branch IS NULL OR TRIM(branch) = '')")
                else:
                    where_clauses.append('branch = ?')
                    params.append(filter_branch)
            if filter_year:
                where_clauses.append('year = ?')
                params.append(filter_year)
            if where_clauses:
                base_sql += ' AND ' + ' AND '.join(where_clauses)
            base_sql += ' ORDER BY id DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])

            rows = cursor.execute(base_sql, params).fetchall()
            students = [dict(row) for row in rows]
            conn.close()
            return jsonify({"success": True, "students": students})

        # POST -> create student
        data = request.get_json(force=True)
        name = (data.get('name') or '').strip()
        roll = (data.get('roll') or '').strip()
        password = (data.get('password') or '').strip()
        gender = (data.get('gender') or '').strip()
        course = (data.get('course') or '').strip()
        branch = (data.get('branch') or '').strip()
        role = (data.get('role') or 'student').strip() or 'student'
        status = (data.get('status') or 'active').strip() or 'active'
        mobileno = (data.get('mobileno') or '').strip()
        email_id = (data.get('email_id') or '').strip()
        aadhar_no = (data.get('aadhar_no') or '').strip()
        address = (data.get('address') or '').strip()
        year = (data.get('year') or '').strip()

        # Require all fields to be non-empty for creation
        required_fields = {
            'name': name,
            'gender': gender,
            'roll': roll,
            'password': password,
            'course': course,
            'branch': branch,
            'year': year,
            'role': role,
            'status': status,
            'mobileno': mobileno,
            'email_id': email_id,
            'aadhar_no': aadhar_no,
            'address': address
        }
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(
                '''INSERT INTO students (name, gender, roll, password, course, branch, year, role, status, mobileno, email_id, aadhar_no, address, date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (name, gender, roll, password, course, branch, year, role, status, mobileno, email_id, aadhar_no, address, current_time)
            )
            conn.commit()
            new_id = cur.lastrowid
        except sqlite3.IntegrityError as ie:
            conn.rollback()
            # Likely UNIQUE constraint on roll
            return jsonify({"success": False, "error": "Roll already exists"}), 409
        finally:
            conn.close()

        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/api/admin/students/<int:student_id>', methods=['GET', 'PUT'])
@login_required
@admin_required
def admin_student_detail(student_id):
    try:
        conn = get_db_connection()
        if request.method == 'GET':
            student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
            if not student:
                return jsonify({"success": False, "error": "Student not found"}), 404
            student_dict = dict(student)
            # Ensure password is included in the returned data
            if 'password' not in student_dict:
                student_dict['password'] = ''
            return jsonify({"success": True, "student": student_dict})
        
        # PUT -> update student
        data = request.get_json(force=True)
        name = (data.get('name') or '').strip()
        roll = (data.get('roll') or '').strip()
        password = (data.get('password') or '').strip()
        gender = (data.get('gender') or '').strip()
        course = (data.get('course') or '').strip()
        branch = (data.get('branch') or '').strip()
        year = (data.get('year') or '').strip()
        role = (data.get('role') or 'student').strip() or 'student'
        status = (data.get('status') or 'active').strip() 
        mobileno = (data.get('mobileno') or '').strip()
        email_id = (data.get('email_id') or '').strip()
        aadhar_no = (data.get('aadhar_no') or '').strip()
        address = (data.get('address') or '').strip()

        # Require all fields to be non-empty for update (including password)
        required_fields = {
            'name': name,
            'gender': gender,
            'roll': roll,
            'password': password,
            'course': course,
            'branch': branch,
            'year': year,
            'role': role,
            'status': status,
            'mobileno': mobileno,
            'email_id': email_id,
            'aadhar_no': aadhar_no,
            'address': address
        }
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400

        cur = conn.cursor()
        try:
            cur.execute('''
                UPDATE students SET name=?, roll=?, password=?, gender=?, course=?, branch=?, year=?, role=?, status=?, mobileno=?, email_id=?, aadhar_no=?, address=?
                WHERE id=?
            ''', (name, roll, password, gender, course, branch, year, role, status, mobileno, email_id, aadhar_no, address, student_id))
            conn.commit()
        except sqlite3.IntegrityError as ie:
            conn.rollback()
            return jsonify({"success": False, "error": "Roll already exists"}), 409
        finally:
            conn.close()

        return jsonify({"success": True})
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        return jsonify({"success": False, "error": str(e)}), 500





if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT,
        roll TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        course TEXT,
        branch TEXT,
        year TEXT,
        role TEXT DEFAULT 'student',
        status TEXT DEFAULT 'active',
        mobileno TEXT,
        email_id TEXT,
        aadhar_no TEXT,
        address TEXT,
        date TEXT
    )
''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS login_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll TEXT,
            name TEXT,
            branch TEXT,
            role TEXT,
            status TEXT,
            time TEXT
        )
    ''')
    # Migration: Add missing columns to students table and backfill
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(students)")
        cols = [r[1] for r in cur.fetchall()]
        if 'status' not in cols:
            cur.execute("ALTER TABLE students ADD COLUMN status TEXT DEFAULT 'active'")
            conn.commit()
        cur.execute("UPDATE students SET status = 'active' WHERE status IS NULL OR TRIM(status) = ''")
        conn.commit()

        if 'year' not in cols:
            cur.execute("ALTER TABLE students ADD COLUMN year TEXT")
            conn.commit()

        if 'date' not in cols:
            cur.execute("ALTER TABLE students ADD COLUMN date TEXT")
            conn.commit()
            # Backfill with current timestamp for existing records
            cur.execute("UPDATE students SET date = datetime('now') WHERE date IS NULL OR TRIM(date) = ''")
            conn.commit()
    except Exception:
        pass
    conn.close()
    # For hosting platforms like Render, bind to 0.0.0.0 and read PORT from env
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug_mode)