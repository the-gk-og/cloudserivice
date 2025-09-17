#!/usr/bin/env python3
"""
Setup script for SecureVault Flask Application
This script will create necessary directories and files
"""

import os

def create_directory_structure():
    """Create necessary directories"""
    directories = [
        'templates',
        'templates/admin',
        'uploads',
        'static',
        'static/css',
        'static/js'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def create_template_files():
    """Create essential template files if they don't exist"""
    templates = {
        'templates/base.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SecureVault{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom styles for better input visibility */
        .input-field {
            background-color: rgba(255, 255, 255, 0.15) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: white !important;
        }
        
        .input-field:focus {
            background-color: rgba(255, 255, 255, 0.2) !important;
            border-color: rgb(59, 130, 246) !important;
            outline: none !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5) !important;
        }
        
        .input-field::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }
        
        /* Prevent input fields from disappearing */
        input[type="text"], input[type="password"], textarea {
            opacity: 1 !important;
            visibility: visible !important;
        }
    </style>
</head>
<body class="min-h-screen bg-gradient-to-br from-blue-900 to-purple-900">
    <nav class="bg-black/20 backdrop-blur-md border-b border-white/20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <a href="/" class="text-white text-xl font-bold hover:text-blue-300 transition-colors">🔒 SecureVault</a>
                <div class="flex space-x-4">
                    {% if session.user_id %}
                        <span class="text-white/70">Welcome, {{ session.username }}!</span>
                        <a href="/dashboard" class="text-white hover:text-blue-300 px-3 py-2 transition-colors">Dashboard</a>
                        <a href="/notes" class="text-white hover:text-blue-300 px-3 py-2 transition-colors">Notes</a>
                        <a href="/files" class="text-white hover:text-blue-300 px-3 py-2 transition-colors">Files</a>
                        {% if is_admin %}
                            <a href="/admin" class="text-yellow-300 hover:text-yellow-200 px-3 py-2 transition-colors font-medium">🛡️ Admin</a>
                        {% endif %}
                        <a href="/logout" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors">Logout</a>
                    {% else %}
                        <a href="/login" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded transition-colors">Login</a>
                        <a href="/register" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded transition-colors">Sign Up</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>
    
    <div class="container mx-auto px-4 py-8">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="mb-4 p-4 rounded-lg animate-pulse {% if category == 'error' %}bg-red-500/80 border border-red-400 text-white{% elif category == 'success' %}bg-green-500/80 border border-green-400 text-white{% else %}bg-blue-500/80 border border-blue-400 text-white{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>''',
        
        'templates/home.html': '''{% extends "base.html" %}
{% block content %}
<div class="text-center py-20">
    <h1 class="text-6xl font-bold text-white mb-6">Welcome to <span class="text-blue-300">SecureVault</span></h1>
    <p class="text-xl text-white/80 mb-12 max-w-3xl mx-auto">Your personal encrypted vault for secure note-taking and file storage.</p>
    {% if not session.user_id %}
        <div class="space-x-4">
            <a href="/login" class="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold">Sign In</a>
            <a href="/register" class="bg-green-500 hover:bg-green-600 text-white px-8 py-4 rounded-lg font-semibold">Get Started</a>
        </div>
    {% else %}
        <a href="/dashboard" class="bg-purple-500 hover:bg-purple-600 text-white px-8 py-4 rounded-lg font-semibold">Go to Dashboard</a>
    {% endif %}
</div>
{% endblock %}''',
        
        'templates/login.html': '''{% extends "base.html" %}
{% block content %}
<div class="max-w-md mx-auto bg-white/10 backdrop-blur-md rounded-xl p-8">
    <h2 class="text-2xl font-bold text-white mb-6 text-center">Login</h2>
    <form method="POST">
        <div class="mb-4">
            <label for="username" class="block text-white mb-2 font-medium">Username</label>
            <input type="text" id="username" name="username" required 
                   class="w-full px-4 py-3 bg-white/20 text-white rounded-lg border border-white/30 
                          focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 
                          placeholder:text-white/50 transition-all duration-200"
                   placeholder="Enter your username" autocomplete="username">
        </div>
        <div class="mb-6">
            <label for="password" class="block text-white mb-2 font-medium">Password</label>
            <input type="password" id="password" name="password" required 
                   class="w-full px-4 py-3 bg-white/20 text-white rounded-lg border border-white/30 
                          focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 
                          placeholder:text-white/50 transition-all duration-200"
                   placeholder="Enter your password" autocomplete="current-password">
        </div>
        <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-lg font-medium transition-colors duration-200">
            Sign In
        </button>
    </form>
    <p class="text-center text-white/70 mt-6">
        Don't have an account? 
        <a href="/register" class="text-blue-300 hover:text-blue-200 font-medium transition-colors">Register here</a>
    </p>
</div>
{% endblock %}''',
        
        'templates/register.html': '''{% extends "base.html" %}
{% block content %}
<div class="max-w-md mx-auto bg-white/10 backdrop-blur-md rounded-xl p-8">
    <h2 class="text-2xl font-bold text-white mb-6 text-center">Create Account</h2>
    <form method="POST">
        <div class="mb-4">
            <label for="username" class="block text-white mb-2 font-medium">Username</label>
            <input type="text" id="username" name="username" required 
                   class="w-full px-4 py-3 bg-white/20 text-white rounded-lg border border-white/30 
                          focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 
                          placeholder:text-white/50 transition-all duration-200"
                   placeholder="Choose a username" autocomplete="username">
        </div>
        <div class="mb-6">
            <label for="password" class="block text-white mb-2 font-medium">Password</label>
            <input type="password" id="password" name="password" required minlength="8" 
                   class="w-full px-4 py-3 bg-white/20 text-white rounded-lg border border-white/30 
                          focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 
                          placeholder:text-white/50 transition-all duration-200"
                   placeholder="Minimum 8 characters" autocomplete="new-password">
            <p class="text-white/60 text-sm mt-1">Password must be at least 8 characters long</p>
        </div>
        <button type="submit" class="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg font-medium transition-colors duration-200">
            Create Account
        </button>
    </form>
    <p class="text-center text-white/70 mt-6">
        Already have an account? 
        <a href="/login" class="text-green-300 hover:text-green-200 font-medium transition-colors">Sign in here</a>
    </p>
</div>
{% endblock %}''',
        
        'templates/dashboard.html': '''{% extends "base.html" %}
{% block content %}
<div class="text-center mb-8">
    <h1 class="text-4xl font-bold text-white mb-4">Welcome, {{ username }}!</h1>
    <p class="text-white/70">Your secure vault is ready</p>
</div>
<div class="grid md:grid-cols-2 gap-8">
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
        <h3 class="text-xl font-bold text-white mb-4">Encrypted Notes</h3>
        <p class="text-white/70 mb-4">Create and manage secure notes</p>
        <a href="/notes" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">Manage Notes</a>
    </div>
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
        <h3 class="text-xl font-bold text-white mb-4">Secure Files</h3>
        <p class="text-white/70 mb-4">Upload and store files securely</p>
        <a href="/files" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">Manage Files</a>
    </div>
</div>
{% endblock %}''',

        'templates/notes.html': '''{% extends "base.html" %}
{% block content %}
<div class="flex justify-between items-center mb-8">
    <h1 class="text-3xl font-bold text-white">My Notes</h1>
    <a href="/add_note" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">New Note</a>
</div>
{% if notes %}
    <div class="grid gap-4">
        {% for note in notes %}
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-4">
            <h3 class="text-white font-bold mb-2">{{ note[1] }}</h3>
            <p class="text-white/60 text-sm mb-2">{{ note[2] }}</p>
            <div class="flex space-x-2">
                <a href="/view_note/{{ note[0] }}" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm">View</a>
                <a href="/edit_note/{{ note[0] }}" class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm">Edit</a>
                <a href="/delete_note/{{ note[0] }}" onclick="return confirm('Delete this note?')" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm">Delete</a>
            </div>
        </div>
        {% endfor %}
    </div>
{% else %}
    <div class="text-center py-12">
        <p class="text-white/70 mb-4">No notes yet</p>
        <a href="/add_note" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded">Create Your First Note</a>
    </div>
{% endif %}
{% endblock %}''',

        'templates/add_note.html': '''{% extends "base.html" %}
{% block content %}
<div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-white mb-8">Add New Note</h1>
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-8">
        <form method="POST" class="space-y-6">
            <div>
                <label for="title" class="block text-white mb-2 font-medium">Note Title</label>
                <input type="text" id="title" name="title" required 
                       class="input-field w-full px-4 py-3 rounded-lg transition-all duration-200"
                       placeholder="Enter note title">
            </div>
            <div>
                <label for="content" class="block text-white mb-2 font-medium">Note Content</label>
                <textarea id="content" name="content" required rows="10" 
                          class="input-field w-full px-4 py-3 rounded-lg resize-vertical transition-all duration-200"
                          placeholder="Write your note here..."></textarea>
            </div>
            <div class="flex space-x-4 pt-4">
                <button type="submit" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    🔒 Save Encrypted Note
                </button>
                <a href="/notes" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    Cancel
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}''',

        'templates/view_note.html': '''{% extends "base.html" %}
{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">{{ title }}</h1>
        <div class="space-x-2">
            <a href="/edit_note/{{ request.view_args.note_id }}" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">Edit</a>
            <a href="/notes" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded">Back</a>
        </div>
    </div>
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-8">
        <div class="text-white whitespace-pre-wrap">{{ content }}</div>
        <div class="mt-4 pt-4 border-t border-white/20 text-white/60 text-sm">
            <p>Created: {{ created_at }}</p>
            {% if updated_at != created_at %}
            <p>Updated: {{ updated_at }}</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}''',

        'templates/edit_note.html': '''{% extends "base.html" %}
{% block content %}
<div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-white mb-8">Edit Note</h1>
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-8">
        <form method="POST" class="space-y-6">
            <div>
                <label for="title" class="block text-white mb-2 font-medium">Note Title</label>
                <input type="text" id="title" name="title" value="{{ title }}" required 
                       class="input-field w-full px-4 py-3 rounded-lg transition-all duration-200">
            </div>
            <div>
                <label for="content" class="block text-white mb-2 font-medium">Note Content</label>
                <textarea id="content" name="content" required rows="10" 
                          class="input-field w-full px-4 py-3 rounded-lg resize-vertical transition-all duration-200">{{ content }}</textarea>
            </div>
            <div class="flex space-x-4 pt-4">
                <button type="submit" class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    ✅ Save Changes
                </button>
                <a href="/notes" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    Cancel
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}''',

        'templates/files.html': '''{% extends "base.html" %}
{% block content %}
<div class="flex justify-between items-center mb-8">
    <h1 class="text-3xl font-bold text-white">My Files</h1>
    <a href="/upload_file" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">Upload File</a>
</div>
{% if files %}
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-6">
        <table class="w-full">
            <thead>
                <tr class="border-b border-white/20">
                    <th class="text-left py-2 text-white">File Name</th>
                    <th class="text-left py-2 text-white">Size</th>
                    <th class="text-left py-2 text-white">Uploaded</th>
                    <th class="text-center py-2 text-white">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for file in files %}
                <tr class="border-b border-white/10">
                    <td class="py-2 text-white">{{ file[1] }}</td>
                    <td class="py-2 text-white/70">{{ file[2] }} bytes</td>
                    <td class="py-2 text-white/70">{{ file[3] }}</td>
                    <td class="py-2 text-center">
                        <a href="/download_file/{{ file[0] }}" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm mr-2">Download</a>
                        <a href="/delete_file/{{ file[0] }}" onclick="return confirm('Delete this file?')" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
{% else %}
    <div class="text-center py-12">
        <p class="text-white/70 mb-4">No files uploaded yet</p>
        <a href="/upload_file" class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded">Upload Your First File</a>
    </div>
{% endif %}
{% endblock %}''',

        'templates/upload_file.html': '''{% extends "base.html" %}
{% block content %}
<div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold text-white mb-8">Upload File</h1>
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-8">
        <form method="POST" enctype="multipart/form-data" class="space-y-6">
            <div>
                <label for="file" class="block text-white mb-2 font-medium">Select File</label>
                <input type="file" id="file" name="file" required 
                       class="input-field w-full px-4 py-3 rounded-lg transition-all duration-200 
                              file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 
                              file:text-sm file:font-medium file:bg-blue-500 file:text-white 
                              hover:file:bg-blue-600 file:transition-colors">
                <p class="text-white/60 text-sm mt-2">
                    📁 Max size: 16MB<br>
                    📄 Supported: TXT, PDF, PNG, JPG, JPEG, GIF, DOC, DOCX, ZIP, RAR
                </p>
            </div>
            <div class="flex space-x-4 pt-4">
                <button type="submit" class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    📤 Upload File
                </button>
                <a href="/files" class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                    Cancel
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}''',

        'templates/admin/dashboard.html': '''{% extends "base.html" %}
{% block content %}
<div class="animate-fade-in">
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-4xl font-bold text-white mb-2">🛡️ Admin Dashboard</h1>
            <p class="text-white/70">System overview and management</p>
        </div>
        <div class="flex space-x-3">
            <a href="/admin/users" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors">👥 Users</a>
            <a href="/admin/system" class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg transition-colors">⚙️ System</a>
        </div>
    </div>
    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
            <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span class="text-white text-xl">👥</span>
            </div>
            <h3 class="text-2xl font-bold text-white mb-1">{{ stats.total_users if stats else 0 }}</h3>
            <p class="text-white/70">Total Users</p>
        </div>
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
            <div class="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span class="text-white text-xl">📝</span>
            </div>
            <h3 class="text-2xl font-bold text-white mb-1">{{ stats.total_notes if stats else 0 }}</h3>
            <p class="text-white/70">Notes</p>
        </div>
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
            <div class="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span class="text-white text-xl">📁</span>
            </div>
            <h3 class="text-2xl font-bold text-white mb-1">{{ stats.total_files if stats else 0 }}</h3>
            <p class="text-white/70">Files</p>
        </div>
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
            <div class="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span class="text-white text-xl">💾</span>
            </div>
            <h3 class="text-2xl font-bold text-white mb-1">{{ stats.total_file_size if stats else '0 B' }}</h3>
            <p class="text-white/70">Storage</p>
        </div>
    </div>
</div>
{% endblock %}''',

        'templates/admin/users.html': '''{% extends "base.html" %}
{% block content %}
<div class="animate-fade-in">
    <div class="flex justify-between items-center mb-8">
        <h1 class="text-4xl font-bold text-white">👥 User Management</h1>
        <a href="/admin" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors">← Back</a>
    </div>
    
    {% if users %}
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-white/20">
                            <th class="text-left py-4 text-white">User</th>
                            <th class="text-left py-4 text-white">Role</th>
                            <th class="text-left py-4 text-white">Content</th>
                            <th class="text-center py-4 text-white">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                            <tr class="border-b border-white/10">
                                <td class="py-4 text-white">{{ user[1] }}</td>
                                <td class="py-4">
                                    {% if user[3] %}
                                        <span class="bg-red-500/20 text-red-300 px-2 py-1 rounded text-xs">🛡️ Admin</span>
                                    {% else %}
                                        <span class="bg-blue-500/20 text-blue-300 px-2 py-1 rounded text-xs">👤 User</span>
                                    {% endif %}
                                </td>
                                <td class="py-4 text-white/70">{{ user[4] }} notes, {{ user[5] }} files</td>
                                <td class="py-4 text-center">
                                    <a href="/admin/users/{{ user[0] }}" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm mr-2">View</a>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    {% else %}
        <div class="text-center py-12">
            <p class="text-white/70">No users found</p>
        </div>
    {% endif %}
</div>
{% endblock %}''',

        'templates/admin/user_details.html': '''{% extends "base.html" %}
{% block content %}
<div class="animate-fade-in">
    <div class="flex justify-between items-center mb-8">
        <div>
            <h1 class="text-4xl font-bold text-white mb-2">👤 User Details</h1>
            <p class="text-white/70">Information for {{ user.username }}</p>
        </div>
        <a href="/admin/users" class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors">← Back</a>
    </div>

    <!-- User Profile -->
    <div class="bg-white/10 backdrop-blur-md rounded-xl p-8 mb-8">
        <div class="flex items-center space-x-6 mb-6">
            <div class="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span class="text-white font-bold text-2xl">{{ user.username[0].upper() }}</span>
            </div>
            <div>
                <h2 class="text-3xl font-bold text-white mb-2">{{ user.username }}</h2>
                <div class="flex items-center space-x-4">
                    {% if user.is_admin %}
                        <span class="bg-red-500/20 text-red-300 px-3 py-1 rounded-full text-sm">🛡️ Admin</span>
                    {% else %}
                        <span class="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm">👤 User</span>
                    {% endif %}
                    <span class="text-white/60 text-sm">Joined: {{ user.created_at }}</span>
                </div>
            </div>
        </div>

        <!-- Actions -->
        {% if user.id != session.user_id %}
            <div class="flex space-x-4 pt-6 border-t border-white/20">
                <form method="POST" action="/admin/users/{{ user.id }}/toggle_admin" class="inline">
                    <button type="submit" onclick="return confirm('Toggle admin status for {{ user.username }}?')"
                            class="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded transition-colors">
                        {% if user.is_admin %}Revoke Admin{% else %}Make Admin{% endif %}
                    </button>
                </form>
                <form method="POST" action="/admin/users/{{ user.id }}/delete" class="inline">
                    <button type="submit" onclick="return confirm('Delete {{ user.username }} and all their data?')"
                            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors">
                        Delete User
                    </button>
                </form>
            </div>
        {% endif %}
    </div>

    <!-- Stats -->
    <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
            <h3 class="text-2xl font-bold text-white mb-1">{{ user.notes|length }}</h3>
            <p class="text-white/70">Notes</p>
        </div>
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
            <h3 class="text-2xl font-bold text-white mb-1">{{ user.files|length }}</h3>
            <p class="text-white/70">Files</p>
        </div>
        <div class="bg-white/10 backdrop-blur-md rounded-xl p-6 text-center">
            <h3 class="text-2xl font-bold text-white mb-1">Active</h3>
            <p class="text-white/70">Status</p>
        </div>
    </div>
</div>
{% endblock %}'''
    }
    
    for filename, content in templates.items():
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✅ Created template: {filename}")
        else:
            print(f"📄 Template already exists: {filename}")

def main():
    print("🚀 Setting up SecureVault Flask Application...")
    print("=" * 50)
    
    create_directory_structure()
    print()
    create_template_files()
    
    print()
    print("✅ Setup complete!")
    print("📋 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt --break-system-packages")
    print("2. Run the application: python app.py")
    print("3. Visit: http://127.0.0.1:5000")

if __name__ == '__main__':
    main()