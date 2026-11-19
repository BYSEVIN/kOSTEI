from typing import Optional

from fastapi import FastAPI

app = FastAPI(title="Kostey")


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


