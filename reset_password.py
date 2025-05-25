from backend.database import SessionLocal
from backend.models.user import User
from backend.auth import get_password_hash

def reset_password(username, new_password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User {username} not found")
            return False
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        print(f"Password for {username} has been reset")
        return True
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    username = "testuser"
    new_password = "password123"
    reset_password(username, new_password)
