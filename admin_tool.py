import sqlite3
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet

DB_PATH = 'secure_app.db'

def create_admin_user():
    username = input("Enter new admin username: ").strip()
    password = input("Enter password: ").strip()

    if len(password) < 8:
        print("❌ Password must be at least 8 characters.")
        return

    password_hash = generate_password_hash(password)
    encryption_key = Fernet.generate_key().decode()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO users (username, password_hash, encryption_key, is_admin)
                     VALUES (?, ?, ?, 1)''',
                  (username, password_hash, encryption_key))
        conn.commit()
        print(f"✅ Admin user '{username}' created.")
    except sqlite3.IntegrityError:
        print("❌ Username already exists.")
    finally:
        conn.close()

def promote_user_to_admin():
    username = input("Enter username to promote: ").strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET is_admin = 1 WHERE username = ?', (username,))
    if c.rowcount == 0:
        print("❌ User not found.")
    else:
        conn.commit()
        print(f"✅ User '{username}' promoted to admin.")
    conn.close()

def view_admins():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, created_at FROM users WHERE is_admin = 1 ORDER BY created_at DESC')
    admins = c.fetchall()
    conn.close()

    if not admins:
        print("⚠️ No admin users found.")
    else:
        print("\n🛡️ Admin Users:")
        for admin in admins:
            print(f" - ID: {admin[0]}, Username: {admin[1]}, Created: {admin[2]}")

def main_menu():
    while True:
        print("\n🔧 Admin Management Tool")
        print("1. Create new admin user")
        print("2. Promote existing user to admin")
        print("3. View all admin users")
        print("4. Exit")

        choice = input("Select an option (1–4): ").strip()

        if choice == '1':
            create_admin_user()
        elif choice == '2':
            promote_user_to_admin()
        elif choice == '3':
            view_admins()
        elif choice == '4':
            print("👋 Exiting admin tool.")
            break
        else:
            print("❌ Invalid choice. Please select 1–4.")

if __name__ == '__main__':
    main_menu()
