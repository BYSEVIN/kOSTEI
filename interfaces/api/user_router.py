import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from pymysql import Connection

from application.services.user_service import UserService
from infrastructure.db.mysql import mysql_conn
from .user_deps import check_session

router = APIRouter(prefix="/user", tags=["user"])

class LogIn(BaseModel):
    login: str
    password: str

@router.post("/login")
async def login(
    resp: Response,
    user: LogIn,
    conn: Connection = Depends(mysql_conn)
):
    service = UserService(conn)
    session_id = service.authorization(login=user.login, password=user.password)
    
    if session_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        expires=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    )
    return {"detail": "Successfully logged in"}

@router.get("/get_users")
async def get_users(
    limit: Optional[int] = 10, 
    page: Optional[int] = 1, 
    conn: Connection = Depends(mysql_conn), 
    session: str = Depends(check_session)
):
    service = UserService(conn)
    users = service.get_all_users()
    return {"users": users, "page": page, "limit": limit}

@router.get("/get_user_by_id/{user_id}")
async def get_user(
    user_id: int, 
    conn: Connection = Depends(mysql_conn), 
    session: str = Depends(check_session)
):
    service = UserService(conn)
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}