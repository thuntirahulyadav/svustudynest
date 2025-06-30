# SVUSTUDYNEST

A comprehensive study hub and authentication system for Sri Venkateswara University students. This platform provides secure login, subject resources, and an integrated AI chatbot for academic support.

---

## 🚀 Features

- **Secure Login & Session Management** (Flask backend, SQLite)
- **Role-based Access** (Student/Admin)
- **Real-time Login Activity Export** (Excel)
- **Protected Educational Content** (Multiple subjects, units, PDFs, videos)
- **Integrated AI Chatbot** (OpenRouter API)
- **Modern UI** (Tailwind CSS, responsive design)

---

## 📁 File & Folder Structure

```
svu_eduhub/
├── app.py                # Main Flask backend
├── auth.js               # Frontend authentication logic
├── requirements.txt      # Python dependencies
├── students.db           # SQLite database
├── login_activity.xlsx   # Exported login activity
├── images/               # Subject and UI images
├── templetes/            # Main HTML templates (login, dashboard, index)
├── cai_templetes/        # Subject resource pages (OS, DAA, CO, BWD, MEA, SS, CONM, Semester4)
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
- **Chatbot:** Use the AI chatbot for academic queries
- **Logout:** Ends your session and logs activity

---

## 👨‍💻 For Developers

- **Add new subject pages:** Place HTML in `cai_templetes/`
- **Protect new pages:** Use Flask's `@login_required` decorator
- **Authentication logic:** See `auth.js` for frontend checks
- **API endpoints:**
  - `/login` (POST): Authenticate user
  - `/logout` (POST): Logout and log activity
  - `/check-auth` (GET): Session check
  - `/api/openrouter` (POST): Chatbot integration
  - `/login-activity` (GET): Recent login activity (admin)
  - `/export-excel` (GET): Export login activity to Excel

---

## 🔒 Security & Session

- Sessions managed via Flask (server-side, secure cookies)
- All content pages require authentication
- Login/logout activity is logged and exportable
- Session data is not stored in localStorage (except for display)

---

## 📚 Educational Content

- **Subjects:** Operating System, DAA, Computer Organization, BWD, MEA, SS, CONM
- **Each subject:**
  - Multiple units with notes (PDFs), important questions, and videos
  - Access via dashboard or direct subject links

---

## 🤖 Chatbot

- Access via `/chatgpt_test` page
- Uses OpenRouter API for AI-powered Q&A
- Modern chat UI with loading indicator and history

---

## 📝 Requirements

- Python 3.8+
- Flask, Flask-CORS, pandas, openpyxl, Werkzeug (see `requirements.txt`)
- Modern browser (for frontend)

---

## 📞 Support

For technical support or questions, please contact the development team or refer to the code comments in `app.py` and `auth.js`.

---

## 📢 Contribution

Pull requests and suggestions are welcome! Please open an issue or submit a PR for improvements. 
