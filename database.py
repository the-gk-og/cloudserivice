import sqlite3

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  encryption_key TEXT NOT NULL,
<<<<<<< HEAD
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Add missing columns if needed
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if 'is_admin' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    if 'force_reset' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN force_reset INTEGER DEFAULT 0")

=======
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  is_admin BOOLEAN DEFAULT 0)''')
    
>>>>>>> ee3fdc1 (Release v2.0.0: Admin panel v2, half created passkey and totp system, and local network actcess)
    # Notes table
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Files table
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  filename TEXT NOT NULL,
                  original_filename TEXT NOT NULL,
                  file_path TEXT NOT NULL,
                  file_size INTEGER NOT NULL,
                  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # System logs table
    c.execute('''CREATE TABLE IF NOT EXISTS system_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  action TEXT NOT NULL,
                  details TEXT,
                  ip_address TEXT,
                  user_agent TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create default admin user if no users exist
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash
        from cryptography.fernet import Fernet
        
        admin_password = generate_password_hash('admin123')
        admin_key = Fernet.generate_key().decode()
        
        c.execute('''INSERT INTO users (username, password_hash, encryption_key, is_admin) 
                     VALUES (?, ?, ?, 1)''', ('admin', admin_password, admin_key))
        print("✅ Default admin user created: admin / admin123")
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect('secure_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = get_db_connection()
    try:
        if params:
            result = conn.execute(query, params)
        else:
            result = conn.execute(query)
        conn.commit()
        return result.fetchall()
    finally:
        conn.close()

def execute_single_query(query, params=None):
    """Execute a query and return a single result"""
    conn = get_db_connection()
    try:
        if params:
            result = conn.execute(query, params)
        else:
            result = conn.execute(query)
        conn.commit()
        return result.fetchone()
    finally:
        conn.close()

def log_action(user_id, action, details=None, ip_address=None, user_agent=None):
    """Log user actions for admin monitoring"""
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('''INSERT INTO system_logs (user_id, action, details, ip_address, user_agent)
                 VALUES (?, ?, ?, ?, ?)''', (user_id, action, details, ip_address, user_agent))
    conn.commit()
    conn.close()