# SVUSTUDYNEST

A comprehensive study hub and authentication system for Sri Venkateswara University students. This platform provides secure login, subject resources and academic support.

---

## 🚀 Features

- **Secure Login & Session Management** (Flask backend, SQLite)
- **Role-based Access** (Student/Admin)
- **Real-time Login Activity Export** (Excel)
- **Protected Educational Content** (Multiple subjects, units, PDFs, videos)
- **Modern UI** (Tailwind CSS, responsive design)
- **Admin Dashboard** (Student management, stats, edit/create)

---

## 📁 File & Folder Structure

```
svu_eduhub/
├── app.py                  # Main Flask backend
├── auth.js                 # Frontend authentication/session logic
├── requirements.txt        # Python dependencies
├── students.db             # SQLite database
├── templetes/              # Main HTML templates (login, dashboards, index, admin)
│   ├── index.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── admin_logins.html
│   ├── csedashboard.html
│   ├── ecedashboard.html
│   └── ...
├── cse_templetes/          # CSE subject resource pages (by semester)
│   ├── semester1/
│   ├── semester2/
│   ├── semester3/
│   ├── semester4/
│   ├── semester5/
│   ├── semester6/
│   ├── semester7/
│   └── semester8/
├── ece_templetes/          # ECE subject resource pages (by semester)
│   ├── semester1/
│   ├── semester2/
│   ├── semester3/
│   ├── semester4/
│   ├── semester5/
│   ├── semester6/
│   ├── semester7/
│   └── semester8/
├── images/                 # Subject and UI images
├── students.db             # Database file
├── chatbot.html            # Chatbot UI page
└── README.md               # Project documentation
```

---

## 🛠️ Setup & Installation

1. **Clone the repository**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Flask server:**
   ```bash
   python app.py
   ```
4. **Access the app:**
   - Open your browser at `http://localhost:5000`

---

## 👩‍🎓 For Students

- **Login:** Use your roll number and password
- **Browse:** Access protected subject resources (notes, videos, PDFs)
- **Logout:** Ends your session and logs activity

---

## 👨‍💻 For Admins/Developers

- **Student Management:** Add, edit, and view students via the admin dashboard
- **Branch & Year Filters:** Browse students by branch/year
- **Login Activity:** View recent login activity and stats
- **Add new subject pages:** Place HTML in `cse_templetes/` or `ece_templetes/`
- **Protect new pages:** Use Flask's `@login_required` decorator
- **Authentication logic:** See `auth.js` for frontend checks
- **API endpoints:**
  - `/login` (POST): Authenticate user
  - `/logout` (POST): Logout and log activity
  - `/check-auth` (GET): Session check
  - `/api/student/<roll>` (GET): Get student info
  - `/api/admin/stats` (GET): Admin dashboard stats
  - `/api/admin/students` (GET/POST): Student management
  - `/api/admin/students/<id>` (GET/PUT): Edit student
  - `/chat` (POST): Chatbot integration
  - `/login-activity` (GET): Recent login activity (admin)

---

## 🔒 Security & Session

- Sessions managed via Flask (server-side, secure cookies)
- All content pages require authentication
- Login/logout activity is logged
- Session data is not stored in localStorage (except for display)

---

## 📚 Educational Content

- **Subjects:** All CSE/ECE subjects by semester
- **Each subject:**
  - Multiple units with notes (PDFs), important questions, and videos
  - Access via dashboard or direct subject links

---

## 📝 Requirements

- Python 3.8+
- Flask, Flask-CORS, requests, sqlite3 (see `requirements.txt`)
- Modern browser (for frontend)

---

## 📞 Support

For technical support or questions, please contact the development team or refer to the code comments in `app.py` and `auth.js`.

---

## 📢 Contribution

Pull requests and suggestions are welcome! Please open an issue or submit a PR for improvements.
