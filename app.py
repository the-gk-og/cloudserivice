from flask import Flask, render_template, session
from auth import auth_bp, login_required
from notes import notes_bp
from files import files_bp
from admin import admin_bp
from security import security_bp, init_security_db
from database import init_db
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(files_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(security_bp)

# Template context processor for admin check
@app.context_processor
def inject_admin_status():
    is_admin = False
    if 'user_id' in session:
        import sqlite3
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
        is_admin = user[0] if user else False
    
    return dict(is_admin=is_admin)

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])

if __name__ == '__main__':
    init_db()
    init_security_db()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
def dashboard():
    return render_template('dashboard.html', username=session['username'])

if __name__ == '__main__':
    init_db()
    init_security_db()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
def dashboard():
    return render_template('dashboard.html', username=session['username'])

if __name__ == '__main__':
    init_db()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)