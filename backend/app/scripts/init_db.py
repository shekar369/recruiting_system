"""
Database initialization script
Creates default admin user and sets up initial data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate


async def create_default_admin():
    """Create default admin user with username: admin, password: admin123"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin already exists
            existing_admin = await AuthService.get_user_by_username(db, "admin")
            if existing_admin:
                print("SUCCESS: Default admin user already exists")
                print(f"  Username: admin")
                print(f"  Email: {existing_admin.email}")
                print(f"  Role: {existing_admin.role.value}")
                return

            # Create admin user
            admin_data = UserCreate(
                username="admin",
                email="admin@example.com",
                password="Admin123",
                full_name="System Administrator",
                role=UserRole.ADMIN
            )

            admin_user = await AuthService.create_user(db, admin_data)

            # Set as superuser
            admin_user.is_superuser = True
            await db.commit()

            print("SUCCESS: Default admin user created successfully!")
            print(f"  Username: admin")
            print(f"  Password: Admin123")
            print(f"  Email: {admin_user.email}")
            print(f"  Role: {admin_user.role.value}")
            print(f"  Superuser: {admin_user.is_superuser}")
            print("\nIMPORTANT: Change the default password after first login!")

        except Exception as e:
            print(f"ERROR: Error creating admin user: {e}")
            await db.rollback()
            raise


async def init_database():
    """Initialize database with default data"""
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    print()

    # Create default admin
    await create_default_admin()

    print()
    print("=" * 60)
    print("Initialization Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(init_database())
