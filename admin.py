import sqlite3
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from auth import login_required
from utils import format_file_size, format_date

admin_bp = Blueprint('admin', __name__)

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is admin
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
        
        if not user or not user[0]:
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with system overview"""
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Get statistics
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM notes')
    total_notes = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*), SUM(file_size) FROM files')
    file_stats = c.fetchone()
    total_files = file_stats[0]
    total_file_size = file_stats[1] or 0
    
    c.execute('SELECT COUNT(*) FROM users WHERE created_at > datetime("now", "-7 days")')
    new_users_week = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM notes WHERE created_at > datetime("now", "-7 days")')
    new_notes_week = c.fetchone()[0]
    
    # Recent activity
    c.execute('''SELECT u.username, COUNT(n.id) as note_count, MAX(n.created_at) as last_note
                 FROM users u LEFT JOIN notes n ON u.id = n.user_id 
                 GROUP BY u.id ORDER BY last_note DESC LIMIT 10''')
    recent_activity = c.fetchall()
    
    conn.close()
    
    stats = {
        'total_users': total_users,
        'total_notes': total_notes,
        'total_files': total_files,
        'total_file_size': format_file_size(total_file_size),
        'new_users_week': new_users_week,
        'new_notes_week': new_notes_week,
        'recent_activity': recent_activity
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/admin/users')
@admin_required
def manage_users():
    """User management page"""
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Build query
    base_query = '''SELECT u.id, u.username, u.created_at, u.is_admin,
                           COUNT(DISTINCT n.id) as note_count,
                           COUNT(DISTINCT f.id) as file_count,
                           SUM(COALESCE(f.file_size, 0)) as total_file_size
                    FROM users u 
                    LEFT JOIN notes n ON u.id = n.user_id
                    LEFT JOIN files f ON u.id = f.user_id'''
    
    where_clause = ""
    params = []
    
    if search:
        where_clause = " WHERE u.username LIKE ?"
        params.append(f'%{search}%')
    
    group_clause = " GROUP BY u.id ORDER BY u.created_at DESC"
    limit_clause = f" LIMIT {per_page} OFFSET {offset}"
    
    full_query = base_query + where_clause + group_clause + limit_clause
    c.execute(full_query, params)
    users = c.fetchall()
    
    # Get total count
    count_query = f"SELECT COUNT(*) FROM users u{where_clause}"
    c.execute(count_query, params)
    total_users = c.fetchone()[0]
    
    conn.close()
    
    total_pages = (total_users + per_page - 1) // per_page
    
    return render_template('admin/users.html', 
                         users=users, 
                         search=search,
                         page=page,
                         total_pages=total_pages,
                         total_users=total_users)

@admin_bp.route('/admin/users/<int:user_id>')
@admin_required
def user_details(user_id):
    """Detailed view of a specific user"""
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Get user info
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.manage_users'))
    
    # Get user's notes
    c.execute('SELECT id, title, created_at, updated_at FROM notes WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    notes = c.fetchall()
    
    # Get user's files
    c.execute('SELECT id, original_filename, file_size, uploaded_at FROM files WHERE user_id = ? ORDER BY uploaded_at DESC', (user_id,))
    files = c.fetchall()
    
    conn.close()
    
    user_data = {
        'id': user[0],
        'username': user[1],
        'created_at': user[4],
        'is_admin': user[5] if len(user) > 5 else False,
        'notes': notes,
        'files': files
    }
    
    return render_template('admin/user_details.html', user=user_data)

@admin_bp.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin status of a user"""
    if user_id == session['user_id']:
        flash('Cannot modify your own admin status', 'error')
        return redirect(url_for('admin.user_details', user_id=user_id))
    
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT username, is_admin FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin.manage_users'))
    
    new_admin_status = not user[1]
    c.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_admin_status, user_id))
    conn.commit()
    conn.close()
    
    action = 'granted' if new_admin_status else 'revoked'
    flash(f'Admin privileges {action} for user {user[0]}', 'success')
    
    return redirect(url_for('admin.user_details', user_id=user_id))

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user and all their data"""
    if user_id == session['user_id']:
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin.user_details', user_id=user_id))
    
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Get user info
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    
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
