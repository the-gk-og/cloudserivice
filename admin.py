import os
import sqlite3
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        result = c.fetchone()
        conn.close()
        if not result or result[0] != 1:
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('SELECT id, username, created_at, is_admin FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', users=users)

@admin_bp.route('/user/<int:user_id>')
@admin_required
def view_user(user_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('SELECT username, created_at, is_admin FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    c.execute('SELECT COUNT(*) FROM notes WHERE user_id = ?', (user_id,))
    note_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM files WHERE user_id = ?', (user_id,))
    file_count = c.fetchone()[0]
    conn.close()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('view_user.html', user=user, note_count=note_count, file_count=file_count)

@admin_bp.route('/stats')
@admin_required
def system_stats():
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM notes')
    total_notes = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM files')
    total_files = c.fetchone()[0]
    c.execute('SELECT SUM(file_size) FROM files')
    total_storage = c.fetchone()[0] or 0
    conn.close()
    return render_template('admin_stats.html', users=total_users, notes=total_notes,
                           files=total_files, storage=total_storage)
