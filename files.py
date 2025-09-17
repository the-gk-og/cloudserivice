import os
import sqlite3
import secrets
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, current_app
from auth import login_required

files_bp = Blueprint('files', __name__)

# Configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'rar'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route('/files')
@login_required
def files():
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('''SELECT id, original_filename, file_size, uploaded_at 
                 FROM files WHERE user_id = ? ORDER BY uploaded_at DESC''', 
              (session['user_id'],))
    files_data = c.fetchall()
    conn.close()
    
    return render_template('files.html', files=files_data)

@files_bp.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate secure filename
            original_filename = file.filename
            filename = secure_filename(f"{session['user_id']}_{secrets.token_hex(8)}_{original_filename}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            # Save file info to database
            conn = sqlite3.connect('secure_app.db')
            c = conn.cursor()
            c.execute('''INSERT INTO files (user_id, filename, original_filename, file_path, file_size)
                         VALUES (?, ?, ?, ?, ?)''',
                     (session['user_id'], filename, original_filename, file_path, file_size))
            conn.commit()
            conn.close()
            
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('files.files'))
        else:
            flash('File type not allowed', 'error')
    
    return render_template('upload_file.html')

@files_bp.route('/download_file/<int:file_id>')
@login_required
def download_file(file_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('''SELECT file_path, original_filename FROM files 
                 WHERE id = ? AND user_id = ?''', (file_id, session['user_id']))
    file_data = c.fetchone()
    conn.close()
    
    if not file_data:
        flash('File not found', 'error')
        return redirect(url_for('files.files'))
    
    return send_file(file_data[0], as_attachment=True, download_name=file_data[1])

@files_bp.route('/delete_file/<int:file_id>')
@login_required
def delete_file(file_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('''SELECT file_path FROM files WHERE id = ? AND user_id = ?''', 
              (file_id, session['user_id']))
    file_data = c.fetchone()
    
    if file_data:
        # Delete physical file
        if os.path.exists(file_data[0]):
            os.remove(file_data[0])
        
        # Delete from database
        c.execute('DELETE FROM files WHERE id = ? AND user_id = ?', (file_id, session['user_id']))
        conn.commit()
        flash('File deleted successfully!', 'success')
    else:
        flash('File not found', 'error')
    
    conn.close()
    return redirect(url_for('files.files'))