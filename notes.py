import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet
from auth import login_required

notes_bp = Blueprint('notes', __name__)

# Encryption utilities
def encrypt_text(text, key):
    f = Fernet(key.encode())
    return f.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text, key):
    f = Fernet(key.encode())
    return f.decrypt(encrypted_text.encode()).decode()

@notes_bp.route('/notes')
@login_required
def notes():
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('''SELECT n.id, n.title, n.created_at, n.updated_at, u.encryption_key
                 FROM notes n JOIN users u ON n.user_id = u.id 
                 WHERE n.user_id = ? ORDER BY n.updated_at DESC''', (session['user_id'],))
    notes_data = c.fetchall()
    conn.close()
    
    return render_template('notes.html', notes=notes_data)

@notes_bp.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        # Get user's encryption key
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT encryption_key FROM users WHERE id = ?', (session['user_id'],))
        encryption_key = c.fetchone()[0]
        
        # Encrypt the content
        encrypted_content = encrypt_text(content, encryption_key)
        
        c.execute('INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)',
                 (session['user_id'], title, encrypted_content))
        conn.commit()
        conn.close()
        
        flash('Note added successfully!', 'success')
        return redirect(url_for('notes.notes'))
    
    return render_template('add_note.html')

@notes_bp.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        # Get user's encryption key
        c.execute('SELECT encryption_key FROM users WHERE id = ?', (session['user_id'],))
        encryption_key = c.fetchone()[0]
        
        # Encrypt the new content
        encrypted_content = encrypt_text(content, encryption_key)
        
        c.execute('''UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
                     WHERE id = ? AND user_id = ?''',
                 (title, encrypted_content, note_id, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Note updated successfully!', 'success')
        return redirect(url_for('notes.notes'))
    
    # Get note for editing
    c.execute('''SELECT n.title, n.content, u.encryption_key
                 FROM notes n JOIN users u ON n.user_id = u.id 
                 WHERE n.id = ? AND n.user_id = ?''', (note_id, session['user_id']))
    note_data = c.fetchone()
    conn.close()
    
    if not note_data:
        flash('Note not found', 'error')
        return redirect(url_for('notes.notes'))
    
    # Decrypt content for editing
    decrypted_content = decrypt_text(note_data[1], note_data[2])
    
    return render_template('edit_note.html', note_id=note_id, 
                         title=note_data[0], content=decrypted_content)

@notes_bp.route('/view_note/<int:note_id>')
@login_required
def view_note(note_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('''SELECT n.title, n.content, n.created_at, n.updated_at, u.encryption_key
                 FROM notes n JOIN users u ON n.user_id = u.id 
                 WHERE n.id = ? AND n.user_id = ?''', (note_id, session['user_id']))
    note_data = c.fetchone()
    conn.close()
    
    if not note_data:
        flash('Note not found', 'error')
        return redirect(url_for('notes.notes'))
    
    # Decrypt content for viewing
    decrypted_content = decrypt_text(note_data[1], note_data[4])
    
    return render_template('view_note.html', 
                         title=note_data[0], content=decrypted_content,
                         created_at=note_data[2], updated_at=note_data[3])

@notes_bp.route('/delete_note/<int:note_id>')
@login_required
def delete_note(note_id):
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes.notes'))