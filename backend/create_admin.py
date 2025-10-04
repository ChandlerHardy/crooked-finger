#!/usr/bin/env python3
"""
Create an admin user for Crooked Finger
"""
import sys
from datetime import datetime
from passlib.context import CryptContext
from app.database.connection import get_db
from app.database.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(email: str, password: str):
    """Create an admin user in the database"""
    db = next(get_db())
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")

            # Ask if they want to make them admin
            response = input("Make this user an admin? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                existing_user.is_admin = True
                db.commit()
                print(f"✅ User {email} is now an admin!")
            return

        # Hash password
        hashed_password = pwd_context.hash(password)

        # Create new admin user
        admin_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            is_admin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   ID: {admin_user.id}")
        print(f"   Admin: {admin_user.is_admin}")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔐 Crooked Finger - Create Admin User")
    print("=" * 40)

    # Get email and password
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        email = input("Admin email: ")
        password = input("Admin password: ")

    if not email or not password:
        print("❌ Email and password are required!")
        sys.exit(1)

    create_admin_user(email, password)
