from config.database import SessionLocal, engine
from config.database import Base
from user.model.user_model import User
from Todo.model.todo_model import Todo
from passlib.context import CryptContext
from sqlalchemy import text

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_initial_data():
    db = SessionLocal()
    db.query(Todo).delete()
    db.query(User).delete()
    db.commit()
    admin = User(username="admin", email="admin@email.com",
                 hashed_password=pwd_context.hash("adminpass"), is_admin=True)
    db.add(admin)
    users = [User(username=f"user{i}", email=f"user{i}@email.com",
                  hashed_password=pwd_context.hash("userpass"), is_admin=False) for i in range(1, 4)]
    db.add_all(users)
    db.commit()
    todos = [Todo(title=f"Todo {i}", description=f"Description {i}", completed=(
        i % 2 == 0)) for i in range(1, 6)]
    db.add_all(todos)
    db.commit()
    db.close()


def add_admin_account():
    db = SessionLocal()
    admin = User(username="admin", email="admin@email.com",
                 hashed_password=pwd_context.hash("adminpass"), is_admin=True)
    db.add(admin)
    db.commit()
    db.close()


def add_dummy_users_and_todos():
    db = SessionLocal()
    users = [User(username=f"user{i}", email=f"user{i}@email.com",
                  hashed_password=pwd_context.hash("userpass"), is_admin=False) for i in range(1, 4)]
    db.add_all(users)
    db.commit()
    todos = [Todo(title=f"Todo {i}", description=f"Description {i}", completed=(
        i % 2 == 0)) for i in range(1, 6)]
    db.add_all(todos)
    db.commit()
    db.close()


def reset_db():
    db = SessionLocal()
    db.query(Todo).delete()
    db.query(User).delete()
    db.commit()
    db.close()


def drop_and_recreate_db():
    reset_db()
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate all tables
    Base.metadata.create_all(bind=engine)


def reset_and_seed_db():
    reset_db()
    seed_initial_data()


if __name__ == "__main__":
    seed_initial_data()
