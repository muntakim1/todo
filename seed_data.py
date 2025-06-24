from config.database import SessionLocal
from user.model.user_model import User
from Todo.model.todo_model import Todo
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    db = SessionLocal()
    # Clear existing data
    db.query(Todo).delete()
    db.query(User).delete()
    db.commit()
    # Add admin
    admin = User(
        username="admin",
        email="admin@email.com",
        hashed_password=pwd_context.hash("adminpass"),
        is_admin=True
    )
    db.add(admin)
    # Add dummy users
    users = [
        User(username=f"user{i}", email=f"user{i}@email.com", hashed_password=pwd_context.hash("userpass"), is_admin=False)
        for i in range(1, 4)
    ]
    db.add_all(users)
    db.commit()
    # Add todos
    todos = [
        Todo(title=f"Todo {i}", description=f"Description {i}", completed=(i%2==0))
        for i in range(1, 6)
    ]
    db.add_all(todos)
    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
