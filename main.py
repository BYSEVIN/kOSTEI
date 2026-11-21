from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from pymysql import Connection

from application.services.user_service import UserService
from infrastructure.db.mysql import mysql_conn

app = FastAPI(title="Kostey API")

# --- Модели Pydantic ---
class UserIn(BaseModel):
    first_name: str
    last_name: str
    login: str
    email: str
    password: str

class UserPatch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    login: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserOut(BaseModel):
    first_name: str
    last_name: str
    login: str
    email: str
    password: str

# --- Эндпоинты ---

@app.get("/users")
async def get_users(limit: Optional[int] = 10, page: Optional[int] = 1, conn: Connection = Depends(mysql_conn)):
    service = UserService(conn)
    users = service.get_all_users()
    return {"users": users, "page": page, "limit": limit}

@app.get("/user/{user_id}")
async def get_user(user_id: int, conn: Connection = Depends(mysql_conn)):
    service = UserService(conn)
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/user/create_user", response_model=UserOut, status_code=201, summary="Создаёт пользователя")
async def create_user(user: UserIn, conn: Connection = Depends(mysql_conn)):
    service = UserService(conn)
    created = service.create_user(user.first_name, user.last_name, user.login, user.email, user.password)
    return UserOut(**created)

@app.put("/user/{user_id}", response_model=UserOut, summary="Полное обновление пользователя")
async def update_user(user_id: int, user: UserIn, conn: Connection = Depends(mysql_conn)):
    service = UserService(conn)
    updated = service.update_user(user_id, user.first_name, user.last_name, user.login, user.email, user.password)
    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(**updated)

@app.patch("/user/{user_id}", response_model=UserOut, summary="Частичное обновление пользователя")
async def patch_user(user_id: int, user: UserPatch, conn: Connection = Depends(mysql_conn)):
    service = UserService(conn)
    updated = service.patch_user(user_id, user.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(**updated)

@app.delete("/user/{user_id}", status_code=204, summary="Удаление пользователя")
async def delete_user(user_id: int, conn: Connection = Depends(mysql_conn)):
    service = UserService(conn)
    deleted = service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None