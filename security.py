import sqlite3
import secrets
import base64
import json
from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from auth import login_required
import pyotp
import qrcode
from io import BytesIO
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import AuthenticatorSelectionCriteria, UserVerificationRequirement, ResidentKeyRequirement, AuthenticatorAttachment
from webauthn.helpers.cose import COSEAlgorithmIdentifier

security_bp = Blueprint('security', __name__)

# Configuration for WebAuthn/Passkeys
WEBAUTHN_RP_ID = "localhost"  # Change this to your domain in production
WEBAUTHN_RP_NAME = "SecureVault"
WEBAUTHN_ORIGIN = "http://localhost:5000"  # Change this to your URL in production

def init_security_db():
    """Initialize security-related database tables"""
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # TOTP secrets table
    c.execute('''CREATE TABLE IF NOT EXISTS user_totp
                 (user_id INTEGER PRIMARY KEY,
                  secret TEXT NOT NULL,
                  is_enabled BOOLEAN DEFAULT 0,
                  backup_codes TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Passkeys table
    c.execute('''CREATE TABLE IF NOT EXISTS user_passkeys
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  credential_id TEXT NOT NULL UNIQUE,
                  public_key TEXT NOT NULL,
                  sign_count INTEGER DEFAULT 0,
                  name TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_used TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Authentication sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS auth_sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  session_token TEXT NOT NULL UNIQUE,
                  challenge TEXT,
                  expires_at TIMESTAMP NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

def require_2fa_setup(f):
    """Decorator to check if 2FA is required but not set up"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Check if user has 2FA enabled
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT is_enabled FROM user_totp WHERE user_id = ?', (session['user_id'],))
        totp_enabled = c.fetchone()
        
        # Check if user has passkeys
        c.execute('SELECT COUNT(*) FROM user_passkeys WHERE user_id = ?', (session['user_id'],))
        passkey_count = c.fetchone()[0]
        
        conn.close()
        
        # If no 2FA is set up, redirect to setup
        if not (totp_enabled and totp_enabled[0]) and passkey_count == 0:
            if request.endpoint != 'security.setup_2fa':
                flash('Please set up two-factor authentication for enhanced security', 'warning')
                return redirect(url_for('security.setup_2fa'))
        
        return f(*args, **kwargs)
    return decorated_function

@security_bp.route('/security')
@login_required
def security_settings():
    """Security settings page"""
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Get TOTP status
    c.execute('SELECT is_enabled FROM user_totp WHERE user_id = ?', (session['user_id'],))
    totp_status = c.fetchone()
    totp_enabled = totp_status[0] if totp_status else False
    
    # Get passkeys
    c.execute('SELECT id, name, created_at, last_used FROM user_passkeys WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],))
    passkeys = c.fetchall()
    
    conn.close()
    
    return render_template('security/settings.html', 
                         totp_enabled=totp_enabled, 
                         passkeys=passkeys)

@security_bp.route('/security/setup-2fa')
@login_required
def setup_2fa():
    """2FA setup page"""
    return render_template('security/setup_2fa.html')

@security_bp.route('/security/setup-totp')
@login_required
def setup_totp():
    """TOTP setup page"""
    # Generate secret
    secret = pyotp.random_base32()
    
    # Store secret temporarily in session
    session['temp_totp_secret'] = secret
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=session['username'],
        issuer_name="SecureVault"
    )
    
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('security/setup_totp.html', 
                         secret=secret, 
                         qr_code=qr_code)

@security_bp.route('/security/verify-totp', methods=['POST'])
@login_required
def verify_totp():
    """Verify TOTP setup"""
    secret = session.get('temp_totp_secret')
    if not secret:
        flash('TOTP setup session expired. Please try again.', 'error')
        return redirect(url_for('security.setup_totp'))
    
    token = request.form.get('token')
    if not token:
        flash('Please enter the verification code', 'error')
        return redirect(url_for('security.setup_totp'))
    
    # Verify token
    totp = pyotp.TOTP(secret)
    if not totp.verify(token):
        flash('Invalid verification code. Please try again.', 'error')
        return redirect(url_for('security.setup_totp'))
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
    
    # Save to database
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Remove existing TOTP if any
    c.execute('DELETE FROM user_totp WHERE user_id = ?', (session['user_id'],))
    
    # Insert new TOTP
    c.execute('INSERT INTO user_totp (user_id, secret, is_enabled, backup_codes) VALUES (?, ?, 1, ?)',
              (session['user_id'], secret, json.dumps(backup_codes)))
    
    conn.commit()
    conn.close()
    
    # Clean up session
    session.pop('temp_totp_secret', None)
    
    flash('TOTP authentication enabled successfully!', 'success')
    return render_template('security/backup_codes.html', backup_codes=backup_codes)

@security_bp.route('/security/disable-totp', methods=['POST'])
@login_required
def disable_totp():
    """Disable TOTP authentication"""
    password = request.form.get('password')
    if not password:
        flash('Please enter your password to disable TOTP', 'error')
        return redirect(url_for('security.security_settings'))
    
    # Verify password
    from werkzeug.security import check_password_hash
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()
    
    if not user or not check_password_hash(user[0], password):
        flash('Invalid password', 'error')
        return redirect(url_for('security.security_settings'))
    
    # Disable TOTP
    c.execute('DELETE FROM user_totp WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    flash('TOTP authentication disabled', 'success')
    return redirect(url_for('security.security_settings'))

@security_bp.route('/security/setup-passkey')
@login_required
def setup_passkey():
    """Passkey setup page"""
    return render_template('security/setup_passkey.html')

@security_bp.route('/security/passkey/register-begin', methods=['POST'])
@login_required
def passkey_register_begin():
    """Begin passkey registration"""
    try:
        # Get user info
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],))
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate registration options
        options = generate_registration_options(
            rp_id=WEBAUTHN_RP_ID,
            rp_name=WEBAUTHN_RP_NAME,
            user_id=str(session['user_id']).encode(),
            user_name=user[0],
            user_display_name=user[0],
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSA_PSS_SHA_256,
            ]
        )
        
        # Store challenge in session
        session['passkey_challenge'] = options.challenge
        
        # Convert to dict for JSON serialization
        options_dict = {
            'rp': {'id': options.rp.id, 'name': options.rp.name},
            'user': {
                'id': base64.b64encode(options.user.id).decode(),
                'name': options.user.name,
                'displayName': options.user.display_name
            },
            'challenge': base64.b64encode(options.challenge).decode(),
            'pubKeyCredParams': [{'type': 'public-key', 'alg': alg.value} for alg in options.pub_key_cred_params],
            'timeout': options.timeout,
            'authenticatorSelection': {
                'authenticatorAttachment': options.authenticator_selection.authenticator_attachment.value if options.authenticator_selection.authenticator_attachment else None,
                'residentKey': options.authenticator_selection.resident_key.value,
                'userVerification': options.authenticator_selection.user_verification.value
            }
        }
        
        return jsonify(options_dict)
        
    except Exception as e:
        current_app.logger.error(f"Passkey registration begin error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@security_bp.route('/security/passkey/register-complete', methods=['POST'])
@login_required
def passkey_register_complete():
    """Complete passkey registration"""
    try:
        data = request.get_json()
        challenge = session.get('passkey_challenge')
        
        if not challenge:
            return jsonify({'error': 'No active challenge'}), 400
        
        # Verify registration response
        verification = verify_registration_response(
            credential=data,
            expected_challenge=challenge,
            expected_origin=WEBAUTHN_ORIGIN,
            expected_rp_id=WEBAUTHN_RP_ID
        )
        
        if verification.verified:
            # Store passkey in database
            passkey_name = data.get('name', f"Passkey {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            conn = sqlite3.connect('secure_app.db')
            c = conn.cursor()
            c.execute('''INSERT INTO user_passkeys 
                         (user_id, credential_id, public_key, name)
                         VALUES (?, ?, ?, ?)''',
                      (session['user_id'], 
                       base64.b64encode(verification.credential_id).decode(),
                       base64.b64encode(verification.credential_public_key).decode(),
                       passkey_name))
            conn.commit()
            conn.close()
            
            # Clear challenge
            session.pop('passkey_challenge', None)
            
            return jsonify({'verified': True})
        else:
            return jsonify({'error': 'Verification failed'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Passkey registration complete error: {e}")
        return jsonify({'error': 'Registration verification failed'}), 500

@security_bp.route('/security/passkey/delete/<int:passkey_id>', methods=['POST'])
@login_required
def delete_passkey(passkey_id):
    """Delete a passkey"""
    conn = sqlite3.connect('secure_app.db')
    c = conn.cursor()
    
    # Verify ownership and delete
    c.execute('DELETE FROM user_passkeys WHERE id = ? AND user_id = ?', 
              (passkey_id, session['user_id']))
    
    if c.rowcount > 0:
        flash('Passkey deleted successfully', 'success')
    else:
        flash('Passkey not found', 'error')
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('security.security_settings'))

@security_bp.route('/auth/2fa', methods=['GET', 'POST'])
def verify_2fa():
    """2FA verification page"""
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        token = request.form.get('token')
        backup_code = request.form.get('backup_code')
        
        conn = sqlite3.connect('secure_app.db')
        c = conn.cursor()
        c.execute('SELECT secret, backup_codes FROM user_totp WHERE user_id = ? AND is_enabled = 1', 
                  (session['pending_user_id'],))
        totp_data = c.fetchone()
        conn.close()
        
        verified = False
        
        if token and totp_data:
            # Verify TOTP token
            totp = pyotp.TOTP(totp_data[0])
            if totp.verify(token):
                verified = True
        
        elif backup_code and totp_data:
            # Verify backup code
            backup_codes = json.loads(totp_data[1])
            if backup_code.upper() in backup_codes:
                # Remove used backup code
                backup_codes.remove(backup_code.upper())
                conn = sqlite3.connect('secure_app.db')
                c = conn.cursor()
                c.execute('UPDATE user_totp SET backup_codes = ? WHERE user_id = ?',
                          (json.dumps(backup_codes), session['pending_user_id']))
                conn.commit()
                conn.close()
                verified = True
        
        if verified:
            # Complete login
            session['user_id'] = session.pop('pending_user_id')
            
            # Get username
            conn = sqlite3.connect('secure_app.db')
            c = conn.cursor()
            c.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],))
            user = c.fetchone()
            conn.close()
            
            if user:
                session['username'] = user[0]
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid verification code or backup code', 'error')
    
    return render_template('security/verify_2fa.html')

@security_bp.route('/auth/passkey-login', methods=['POST'])
def passkey_login():
    """Passkey authentication endpoint"""
    try:
        data = request.get_json()
        
        if data.get('action') == 'begin':
            # Begin passkey authentication
            options = generate_authentication_options(
                rp_id=WEBAUTHN_RP_ID,
                user_verification=UserVerificationRequirement.PREFERRED
            )
            
            session['passkey_auth_challenge'] = options.challenge
            
            options_dict = {
                'challenge': base64.b64encode(options.challenge).decode(),
                'timeout': options.timeout,
                'rpId': options.rp_id,
                'userVerification': options.user_verification.value
            }
            
            return jsonify(options_dict)
            
        elif data.get('action') == 'complete':
            # Complete passkey authentication
            challenge = session.get('passkey_auth_challenge')
            if not challenge:
                return jsonify({'error': 'No active challenge'}), 400
            
            # Find user by credential ID
            credential_id = data.get('id')
            conn = sqlite3.connect('secure_app.db')
            c = conn.cursor()
            c.execute('''SELECT user_id, public_key, sign_count FROM user_passkeys 
                         WHERE credential_id = ?''', (credential_id,))
            passkey_data = c.fetchone()
            
            if not passkey_data:
                return jsonify({'error': 'Passkey not found'}), 400
            
            user_id, public_key, sign_count = passkey_data
            
            # Verify authentication response
            verification = verify_authentication_response(
                credential=data,
                expected_challenge=challenge,
                expected_origin=WEBAUTHN_ORIGIN,
                expected_rp_id=WEBAUTHN_RP_ID,
                credential_public_key=base64.b64decode(public_key),
                credential_current_sign_count=sign_count
            )
            
            if verification.verified:
                # Update sign count
                c.execute('UPDATE user_passkeys SET sign_count = ?, last_used = CURRENT_TIMESTAMP WHERE credential_id = ?',
                          (verification.new_sign_count, credential_id))
                
                # Get username
                c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
                user = c.fetchone()
                conn.commit()
                conn.close()
                
                if user:
                    # Complete login
                    session['user_id'] = user_id
                    session['username'] = user[0]
                    session.pop('passkey_auth_challenge', None)
                    
                    return jsonify({'verified': True, 'redirect': url_for('dashboard')})
            
            conn.close()
            return jsonify({'error': 'Authentication failed'}), 400
            
    except Exception as e:
        current_app.logger.error(f"Passkey login error: {e}")
        return jsonify({'error': 'Authentication failed'}), 500