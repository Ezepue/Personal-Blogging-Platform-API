import sys
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import UserDB
from utils.auth_helpers import hash_password
from pydantic import SecretStr

def create_super_admin(username: str, email: str, password: str):
    db: Session = SessionLocal()
    hashed_pw = hash_password(SecretStr(password))  # Wrap the password in SecretStr


    existing_user = db.query(UserDB).filter(UserDB.email == email).first()
    if existing_user:
        print("User already exists.")
        return

    super_user = UserDB(username=username, email=email, hashed_password=hashed_pw, role="super_admin")
    db.add(super_user)
    db.commit()
    db.close()

    print(f"Super admin '{username}' created successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_super_admin.py <username> <email> <password>")
        sys.exit(1)

    create_super_admin(sys.argv[1], sys.argv[2], sys.argv[3])
