from flask import Flask, render_template, session
from auth import auth_bp, login_required
from notes import notes_bp
from files import files_bp
from admin import admin_bp  # ← Make sure this is imported
from database import init_db
import secrets
import os
import sqlite3 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register blueprints AFTER app is defined
app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(files_bp)
app.register_blueprint(admin_bp)  # ← This line was too early before

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])

@app.context_processor
def inject_admin_status():
    if 'user_id' in session:
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        result = c.fetchone()
        conn.close()
        return {'is_admin': result[0] if result else 0}
    return {'is_admin': 0}
if __name__ == '__main__':
    init_db()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)