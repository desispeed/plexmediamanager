#!/usr/bin/env python3
"""
Railway Authentication Diagnostic Script
Run this on Railway to diagnose auth module issues
"""

import sys
import os

print("=" * 70)
print("RAILWAY AUTHENTICATION DIAGNOSTICS")
print("=" * 70)

# Test 1: Python Version
print("\n1. Python Version:")
print(f"   {sys.version}")
print(f"   Executable: {sys.executable}")

# Test 2: Check if auth.py exists
print("\n2. Checking if auth.py exists:")
auth_file = os.path.join(os.path.dirname(__file__), 'auth.py')
if os.path.exists(auth_file):
    print(f"   ✓ auth.py found at: {auth_file}")
    print(f"   ✓ File size: {os.path.getsize(auth_file)} bytes")
else:
    print(f"   ✗ auth.py NOT FOUND at: {auth_file}")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Files in directory: {os.listdir(os.path.dirname(__file__) or '.')}")

# Test 3: Check installed packages
print("\n3. Checking installed packages:")
required_packages = {
    'jwt': 'PyJWT',
    'pyotp': 'pyotp',
    'qrcode': 'qrcode',
    'PIL': 'Pillow',
    'bcrypt': 'bcrypt',
    'flask': 'Flask',
    'flask_cors': 'flask-cors'
}

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        print(f"   ✓ {package_name} is installed")
    except ImportError as e:
        print(f"   ✗ {package_name} is NOT installed: {e}")

# Test 4: Try importing auth module
print("\n4. Testing auth module import:")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from auth import auth_manager
    print(f"   ✓ Successfully imported auth_manager")
    print(f"   ✓ Type: {type(auth_manager).__name__}")
    print(f"   ✓ Has users: {hasattr(auth_manager, 'users')}")
except ImportError as e:
    print(f"   ✗ ImportError: {e}")
    print(f"   ✗ Module search path: {sys.path[:3]}")
except Exception as e:
    print(f"   ✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check environment variables
print("\n5. Environment variables:")
print(f"   PLEX_URL: {'Set' if os.getenv('PLEX_URL') else 'NOT SET'}")
print(f"   PLEX_TOKEN: {'Set' if os.getenv('PLEX_TOKEN') else 'NOT SET'}")
print(f"   JWT_SECRET: {'Set' if os.getenv('JWT_SECRET') else 'NOT SET (using default)'}")
print(f"   PORT: {os.getenv('PORT', 'NOT SET')}")

# Test 6: Check write permissions
print("\n6. Checking write permissions:")
try:
    test_file = 'test_write.tmp'
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print(f"   ✓ Can write files in current directory")
except Exception as e:
    print(f"   ✗ Cannot write files: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)
