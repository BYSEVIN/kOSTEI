from fastapi import APIRouter
from .user_router import router as user_router

# Создаем главный роутер для всей папки api
router = APIRouter(prefix="/api", tags=["api"])

# Подключаем к нему роутер пользователей
router.include_router(user_router, tags=["user"])