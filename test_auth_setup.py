#!/usr/bin/env python3
"""
Test script to verify GRUMP authentication setup
"""

import os
import sys
from pathlib import Path

def check_file(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def check_env_var(var_name, required=True):
    """Check if environment variable is set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    value = os.getenv(var_name)
    if value:
        # Mask sensitive values
        if 'PASSWORD' in var_name or 'SECRET' in var_name:
            display_value = '*' * 8
        else:
            display_value = value[:30] + '...' if len(value) > 30 else value
        print(f"✅ {var_name}: {display_value}")
        return True
    else:
        status = "❌" if required else "⚠️ "
        print(f"{status} {var_name}: Not set")
        return not required

def check_whitelist():
    """Check whitelist configuration"""
    try:
        with open('allowed_people.txt', 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if lines:
                print(f"✅ Whitelist configured with {len(lines)} entries")
                return True
            else:
                print("⚠️  Whitelist file exists but no entries are uncommented")
                return False
    except FileNotFoundError:
        print("❌ allowed_people.txt not found")
        return False

def test_smtp_connection():
    """Test SMTP connection (optional)"""
    from dotenv import load_dotenv
    import smtplib
    
    load_dotenv()
    
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not all([smtp_server, smtp_user, smtp_password]):
        print("⚠️  SMTP credentials not configured - skipping connection test")
        return False
    
    try:
        print(f"🔌 Testing SMTP connection to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.quit()
        print("✅ SMTP connection successful!")
        return True
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🔐 GRUMP Authentication Setup Verification")
    print("=" * 60)
    print()
    
    all_checks = []
    
    # Check required files
    print("📁 Checking Required Files...")
    all_checks.append(check_file('auth_gate.py', 'Authentication gateway'))
    all_checks.append(check_file('login.html', 'Login page'))
    all_checks.append(check_file('allowed_people.txt', 'Email whitelist'))
    all_checks.append(check_file('.env', 'Environment configuration'))
    all_checks.append(check_file('index.html', 'Dashboard'))
    print()
    
    # Check directory structure
    print("📂 Checking Directories...")
    all_checks.append(check_file('logs', 'Logs directory'))
    print()
    
    # Check environment variables
    print("🔧 Checking Environment Variables...")
    try:
        all_checks.append(check_env_var('AUTH_COOKIE_SECRET', required=True))
        all_checks.append(check_env_var('SMTP_SERVER', required=True))
        all_checks.append(check_env_var('SMTP_PORT', required=True))
        all_checks.append(check_env_var('SMTP_USER', required=True))
        all_checks.append(check_env_var('SMTP_PASSWORD', required=True))
        all_checks.append(check_env_var('SMTP_FROM', required=False))
        all_checks.append(check_env_var('DASHBOARD_URL', required=False))
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        all_checks.append(False)
    print()
    
    # Check whitelist
    print("👥 Checking Whitelist Configuration...")
    all_checks.append(check_whitelist())
    print()
    
    # Test SMTP connection (optional)
    print("📧 Testing Email Configuration...")
    smtp_ok = test_smtp_connection()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    passed = sum(all_checks)
    total = len(all_checks)
    
    if passed == total and smtp_ok:
        print("🎉 All checks passed! Authentication system is ready.")
        print()
        print("Next steps:")
        print("1. Run: python3 auth_gate.py")
        print("2. Visit: http://localhost:38081")
        print("3. Login with an authorized email")
        return 0
    elif passed == total and not smtp_ok:
        print("⚠️  Setup is complete but SMTP connection failed.")
        print()
        print("Please verify your email credentials in .env file:")
        print("- For Gmail: Use an App Password (not regular password)")
        print("- Get one at: https://myaccount.google.com/apppasswords")
        print()
        print("You can still start the server:")
        print("  python3 auth_gate.py")
        return 1
    else:
        print(f"❌ {total - passed} check(s) failed. Please fix the issues above.")
        print()
        print("For help, see: AUTH_SETUP.md")
        return 1

if __name__ == '__main__':
    sys.exit(main())

