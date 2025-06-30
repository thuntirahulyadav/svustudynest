from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, make_response
from flask_cors import CORS
import sqlite3
import os
from functools import wraps
import pandas as pd
import requests
from datetime import datetime
import traceback
import json




app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this-in-production'  # Change this in production
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app, supports_credentials=True)

# Set your OpenAI API key from environment variable
OPENROUTER_API_KEY = "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"  # Replace with your OpenRouter API key



def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

def export_to_excel():
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('SELECT * FROM login_activity ORDER BY time DESC', conn)
        excel_filename = 'login_activity.xlsx'
        df.to_excel(excel_filename, index=False)
        print(f"Login activity exported to {excel_filename}")
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
    finally:
        if conn:
            conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_roll' not in session:
            return redirect('/login.html')
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
            export_to_excel()  # Real-time export
            session['student_roll'] = roll
            session['student_name'] = student['name']
            session['student_branch'] = branch  # Store branch in session
            session['student_role'] = student['role'] if 'role' in student.keys() else 'student'
            conn.close()
            return jsonify({"success": True, "name": student['name']})
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
            export_to_excel()  # Real-time export
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
            "student_name": session['student_name']
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



@app.route('/dashboard.html')
@login_required
def dashboard():
    response = make_response(send_from_directory('templetes', 'dashboard.html'))
    return add_no_cache_headers(response)

@app.route('/semester4.html')
@login_required
def semester4():
    response = make_response(send_from_directory('cai_templetes', 'semester4.html'))
    return add_no_cache_headers(response)



@app.route('/os_page.html')
@login_required
def os_page():
    response = make_response(send_from_directory('cai_templetes', 'os_page.html'))
    return add_no_cache_headers(response)

@app.route('/daa_page.html')
@login_required
def daa_page():
    return send_from_directory('cai_templetes', 'daa_page.html')


@app.route('/bwd_page.html')
@login_required
def bwd_page():
    return send_from_directory('cai_templetes', 'bwd_page.html')


@app.route('/co_page.html')
@login_required
def co_page():
    return send_from_directory('cai_templetes', 'co_page.html')

@app.route('/conm_page.html')
@login_required
def conm_page():
    return send_from_directory('cai_templetes', 'conm_page.html')

@app.route('/mea_page.html')
@login_required
def mea_page():
    return send_from_directory('cai_templetes', 'mea_page.html')

@app.route('/ss_page.html')
@login_required
def ss_page():
    return send_from_directory('cai_templetes', 'ss_page.html')

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

@app.route('/export-excel', methods=['GET'])
def export_excel_endpoint():
    export_to_excel()
    return jsonify({"success": True, "message": "Excel file exported successfully"})

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
def admin_dashboard():
    response = make_response(send_from_directory(os.getcwd(), 'admin_dashboard.html'))
    return add_no_cache_headers(response)



@app.route('/chatgpt_test')
def chatgpt_test():
    return send_from_directory('cai_templetes', 'chatgpt_test.html')

@app.route('/api/openrouter', methods=['POST'])
def openrouter_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'reply': 'No message received.'}), 400

    payload = {
        "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
        # "X-Title": "<YOUR_SITE_NAME>",      # Optional
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        data = response.json()
        reply = data['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Error: {str(e)}'}), 500



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
        role TEXT DEFAULT 'student',
        mobileno TEXT,
        email_id TEXT,
        aadhar_no TEXT,
        address TEXT
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
    conn.close()
    app.run(debug=True)