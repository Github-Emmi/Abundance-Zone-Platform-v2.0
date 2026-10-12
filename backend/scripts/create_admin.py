"""
Create Admin User in Production Database
Run this locally to create admin in production Neon database
Usage: python scripts/create_admin.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend directory to Python path (parent of scripts folder)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.infrastructure.database.models.user import UserModel
from app.domain.value_objects.enums import Role
from app.infrastructure.security.password_hasher import PasswordHasher


async def create_admin_user():
    """Create admin user in production database"""
    
    print("=" * 70)
    print("🚀 Creating Admin User in Production Database")
    print("=" * 70)
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("\nPlease ensure your .env file has DATABASE_URL set to production Neon URL")
        print("Example: DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb")
        print(f"\nSearched for .env at: {backend_dir / '.env'}")
        return False
    
    print(f"📡 Connecting to production database...")
    print(f"   Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'hidden'}")
    
    try:
        # Create async engine
        engine = create_async_engine(database_url, echo=False)
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            # Check if admin already exists
            print("\n🔍 Checking for existing admin user...")
            result = await session.execute(
                select(UserModel).where(UserModel.email == "admin@abundancezone.org")
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("\n✅ Admin user already exists!")
                print(f"   📧 Email: {existing_admin.email}")
                print(f"   👤 Name: {existing_admin.name}")
                print(f"   🛡️  Role: {existing_admin.role}")
                print(f"   ✉️  Email Verified: {existing_admin.is_email_verified}")
                print(f"   🔓 Active: {existing_admin.is_active}")
                return True
            
            # Create password hasher and hash password
            print("\n🔐 Hashing admin password...")
            hasher = PasswordHasher()
            hashed_password = hasher.hash_password("ChangeMe123!")
            
            # Create admin user
            print("👤 Creating admin user...")
            admin = UserModel(
                name="Platform Administrator",
                email="admin@abundancezone.org",
                password=hashed_password,
                phone="+2341234567890",
                role=Role.SUPER_ADMIN,
                is_email_verified=True,
                is_active=True
            )
            
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            
            print("\n" + "=" * 70)
            print("🎉 SUCCESS! Admin user created in production database")
            print("=" * 70)
            print(f"   📧 Email: {admin.email}")
            print(f"   🔑 Password: ChangeMe123!")
            print(f"   👤 User ID: {admin.id}")
            print(f"   🛡️  Role: {admin.role}")
            print(f"   📅 Created: {admin.created_at}")
            print("=" * 70)
            print("\n⚠️  IMPORTANT: Change the password immediately after first login!")
            print("\n✅ You can now login at:")
            print("   https://abundance-zone-platform-v2-0.onrender.com/api/v1/auth/login")
            print("=" * 70)
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create admin user")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"\nTroubleshooting:")
        print("   1. Verify DATABASE_URL in .env points to production Neon database")
        print("   2. Ensure database has all tables created (run migrations)")
        print("   3. Check network connectivity to Neon")
        return False


async def test_admin_login():
    """Test admin login after creation"""
    try:
        import httpx
    except ImportError:
        print("\n⚠️  httpx not installed, skipping login test")
        print("   Install with: pip install httpx")
        return None
    
    print("\n" + "=" * 70)
    print("🧪 Testing Admin Login...")
    print("=" * 70)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://abundance-zone-platform-v2-0.onrender.com/api/v1/auth/login",
                json={
                    "email": "admin@abundancezone.org",
                    "password": "ChangeMe123!"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Login successful!")
                print(f"   Access Token: {data['data']['access_token'][:50]}...")
                print(f"   User Role: {data['data']['user']['role']}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Login test failed: {str(e)}")
        return False


async def main():
    """Main execution"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║   Abundance Zone Platform v2.0 - Production Admin Creator        ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    # Create admin user
    success = await create_admin_user()
    
    if success:
        # Test login
        print("\nWaiting 2 seconds before testing login...")
        await asyncio.sleep(2)
        await test_admin_login()
    
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
