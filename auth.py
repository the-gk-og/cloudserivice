import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet

auth_bp = Blueprint('auth', __name__)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Encryption utilities
def generate_key():
    return Fernet.generate_key()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash, is_admin, force_reset FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[3]

            if user[4] == 1:
                session['force_reset'] = True
                flash('You must reset your password before continuing.', 'warning')
                return redirect(url_for('auth.reset_password'))

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        encryption_key = generate_key().decode()

        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()

        try:
            c.execute('INSERT INTO users (username, password_hash, encryption_key) VALUES (?, ?, ?)',
                      (username, password_hash, encryption_key))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
        finally:
            conn.close()

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'force_reset' not in session or 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form['new_password']

        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('reset_password.html')

        password_hash = generate_password_hash(new_password)

        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('UPDATE users SET password_hash = ?, force_reset = 0 WHERE id = ?', (password_hash, session['user_id']))
        conn.commit()
        conn.close()

        session.pop('force_reset', None)
        flash('Password reset successful. You may now continue.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('reset_password.html')
