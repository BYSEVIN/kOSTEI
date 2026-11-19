from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Kostey")



class User(BaseModel):
    first_name: str
    last_name: str
    login: str
    email: str
    password: str



User.model_rebuild()


@app.get('/users')
async def get_users():
    return {
        "users": [],
        "page": 1,
        "limit": 20
    }


@app.get('/get_user/{user_id}')
async def get_user(user_id: int):
    return {
        "user_id": 1
    }


# Эндпоинт создания пользователя
@app.post("/user/create_user")
async def create_user(user: User):
    return user


# Эндпоинт обновления пользователя
@app.put("/user/update_user/{user_id}")
async def update_user(user_id: int, user: User):
    return user