#!/usr/bin/env python3
"""
Set Fly.io secrets from .env file, properly handling multiline values like Firebase keys.
"""
import os
import subprocess
import sys
from pathlib import Path

def load_env_file(env_path: str = ".env") -> dict:
    """Load .env file and return as dictionary, handling multiline values."""
    env_vars = {}
    current_key = None
    current_value = []
    in_multiline = False
    
    with open(env_path, 'r') as f:
        for line in f:
            line_stripped = line.rstrip('\n')
            
            # Skip comments and empty lines (only when not in multiline)
            if not in_multiline and (line_stripped.startswith('#') or not line_stripped.strip()):
                continue
            
            # Check if line contains a key=value pair
            if '=' in line_stripped and not in_multiline:
                # Save previous key-value if exists
                if current_key:
                    env_vars[current_key] = ''.join(current_value)
                
                # Parse new key-value
                key, value = line_stripped.split('=', 1)
                current_key = key.strip()
                current_value = [value]
                
                # Check if value starts a multiline (quoted string)
                if value.startswith('"') and not value.endswith('"'):
                    in_multiline = True
                elif value.startswith('"') and value.endswith('"'):
                    # Remove surrounding quotes
                    current_value = [value[1:-1]]
            elif in_multiline:
                # Continue collecting multiline value
                current_value.append('\n' + line_stripped)
                if line_stripped.endswith('"'):
                    # End of multiline value
                    in_multiline = False
                    # Join and remove surrounding quotes
                    full_value = ''.join(current_value)
                    if full_value.startswith('"'):
                        full_value = full_value[1:]
                    if full_value.endswith('"'):
                        full_value = full_value[:-1]
                    current_value = [full_value]
        
        # Save last key-value
        if current_key:
            env_vars[current_key] = ''.join(current_value)
    
    return env_vars

def set_secrets_for_app(app_name: str, secrets: dict) -> bool:
    """Set secrets for a Fly.io app using flyctl."""
    print(f"\n🔐 Setting secrets for {app_name}...")
    
    # Build the command
    cmd = ['flyctl', 'secrets', 'set', '--app', app_name]
    
    for key, value in secrets.items():
        cmd.append(f"{key}={value}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Secrets set successfully for {app_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting secrets for {app_name}:")
        print(e.stderr)
        return False

def main():
    # Load environment variables
    print("📖 Loading .env file...")
    env_vars = load_env_file('.env')
    
    # Common secrets needed by all apps
    common_secrets = {
        'DATABASE_URL': env_vars.get('DATABASE_URL', ''),
        'REDIS_URL': env_vars.get('REDIS_URL', ''),
        'CELERY_BROKER_URL': env_vars.get('CELERY_BROKER_URL', ''),
        'CELERY_RESULT_BACKEND': env_vars.get('CELERY_RESULT_BACKEND', ''),
        'JWT_SECRET_KEY': env_vars.get('JWT_SECRET_KEY', ''),
        'JWT_REFRESH_SECRET_KEY': env_vars.get('JWT_REFRESH_SECRET_KEY', ''),
        'OPENAI_API_KEY': env_vars.get('OPENAI_API_KEY', ''),
        'GOOGLE_API_KEY': env_vars.get('GOOGLE_API_KEY', ''),
        'CLOUDINARY_CLOUD_NAME': env_vars.get('CLOUDINARY_CLOUD_NAME', ''),
        'CLOUDINARY_API_KEY': env_vars.get('CLOUDINARY_API_KEY', ''),
        'CLOUDINARY_API_SECRET': env_vars.get('CLOUDINARY_API_SECRET', ''),
        'RESEND_API_KEY': env_vars.get('RESEND_API_KEY', ''),
        'FIREBASE_PROJECT_ID': env_vars.get('FIREBASE_PROJECT_ID', ''),
        'FIREBASE_PRIVATE_KEY_ID': env_vars.get('FIREBASE_PRIVATE_KEY_ID', ''),
        'FIREBASE_PRIVATE_KEY': env_vars.get('FIREBASE_PRIVATE_KEY', ''),
        'FIREBASE_CLIENT_EMAIL': env_vars.get('FIREBASE_CLIENT_EMAIL', ''),
        'SENTRY_DSN': env_vars.get('SENTRY_DSN', ''),
        'ENVIRONMENT': 'production',
    }
    
    # Remove empty values
    common_secrets = {k: v for k, v in common_secrets.items() if v}
    
    # API-specific secrets
    api_secrets = {**common_secrets, 'PORT': '8000'}
    
    # Set secrets for each app
    apps = [
        ('abundance-zone-api', api_secrets),
        ('abundance-zone-worker', common_secrets),
        ('abundance-zone-beat', common_secrets),
    ]
    
    success_count = 0
    for app_name, secrets in apps:
        if set_secrets_for_app(app_name, secrets):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully configured {success_count}/{len(apps)} apps")
    print(f"{'='*60}\n")
    
    return 0 if success_count == len(apps) else 1

if __name__ == '__main__':
    sys.exit(main())
