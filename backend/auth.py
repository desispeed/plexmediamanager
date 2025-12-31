#!/usr/bin/env python3
"""
Authentication module with MFA/TOTP support
Works with Microsoft Authenticator, Google Authenticator, etc.
"""

import os
import json
import jwt
import bcrypt
import pyotp
import qrcode
import io
import base64
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'change-this-secret-key-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
RESET_TOKEN_EXPIRATION_HOURS = 1

# Use environment variable for data directory, with fallback to current directory
DATA_DIR = os.getenv('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

class AuthManager:
    def __init__(self):
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from JSON file"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def create_user(self, username, password):
        """Create new user with hashed password and TOTP secret"""
        if username in self.users:
            return None, "User already exists"
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Generate TOTP secret
        totp_secret = pyotp.random_base32()
        
        self.users[username] = {
            'password_hash': password_hash.decode('utf-8'),
            'totp_secret': totp_secret,
            'totp_enabled': False,
            'created_at': datetime.now().isoformat()
        }
        
        self._save_users()
        return totp_secret, None
    
    def verify_password(self, username, password):
        """Verify username and password"""
        if username not in self.users:
            return False
        
        stored_hash = self.users[username]['password_hash'].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    
    def verify_totp(self, username, token):
        """Verify TOTP token"""
        if username not in self.users:
            return False
        
        totp_secret = self.users[username]['totp_secret']
        totp = pyotp.TOTP(totp_secret)
        return totp.verify(token, valid_window=1)  # Allow 1 step tolerance
    
    def enable_totp(self, username):
        """Enable TOTP for user after successful verification"""
        if username in self.users:
            self.users[username]['totp_enabled'] = True
            self._save_users()
            return True
        return False

    def generate_reset_token(self, username):
        """Generate a password reset token"""
        if username not in self.users:
            return None, "User not found"

        # Generate secure random token
        reset_token = secrets.token_urlsafe(32)

        # Store token with expiration
        self.users[username]['reset_token'] = reset_token
        self.users[username]['reset_token_expires'] = (
            datetime.now() + timedelta(hours=RESET_TOKEN_EXPIRATION_HOURS)
        ).isoformat()

        self._save_users()
        return reset_token, None

    def verify_reset_token(self, token):
        """Verify reset token and return username if valid"""
        for username, user_data in self.users.items():
            if user_data.get('reset_token') == token:
                # Check if token has expired
                expires_str = user_data.get('reset_token_expires')
                if expires_str:
                    expires = datetime.fromisoformat(expires_str)
                    if datetime.now() < expires:
                        return username
        return None

    def reset_password(self, token, new_password):
        """Reset password using valid token"""
        username = self.verify_reset_token(token)
        if not username:
            return False, "Invalid or expired reset token"

        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        # Update password and clear reset token
        self.users[username]['password_hash'] = password_hash.decode('utf-8')
        self.users[username].pop('reset_token', None)
        self.users[username].pop('reset_token_expires', None)

        self._save_users()
        return True, None
    
    def generate_qr_code(self, username):
        """Generate QR code for TOTP setup"""
        if username not in self.users:
            return None
        
        totp_secret = self.users[username]['totp_secret']
        
        # Create provisioning URI for Microsoft Authenticator
        totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
            name=username,
            issuer_name='Plex Manager'
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def generate_jwt(self, username):
        """Generate JWT token"""
        payload = {
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_jwt(self, token):
        """Verify JWT token and return username"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload['username']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def requires_auth(self, f):
        """Decorator to protect routes with authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            username = self.verify_jwt(token)
            if not username:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add username to request context
            request.username = username
            return f(*args, **kwargs)
        
        return decorated_function

# Global auth manager instance
auth_manager = AuthManager()
