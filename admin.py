import sqlite3
import os
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

    return render_template('view_user.html', user=user, user_id=user_id, note_count=note_count, file_count=file_count)

@admin_bp.route('/user/<int:user_id>/edit-username', methods=['POST'])
@admin_required
def edit_username(user_id):
    new_username = request.form['username']
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, user_id))
    conn.commit()
    conn.close()
    flash('Username updated successfully.', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/force-reset', methods=['POST'])
@admin_required
def force_password_reset(user_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('UPDATE users SET force_reset = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('User will be prompted to reset password on next login.', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/clear-storage', methods=['POST'])
@admin_required
def clear_storage(user_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('DELETE FROM files WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('User storage cleared.', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('DELETE FROM notes WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM files WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('User and all associated data deleted.', 'success')
    return redirect(url_for('admin.admin_dashboard'))
