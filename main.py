from fastapi import FastAPI
from Todo.routes import todo_routes
from user.routes import user_routes

app = FastAPI()

app.include_router(todo_routes.router)
app.include_router(user_routes.router)
