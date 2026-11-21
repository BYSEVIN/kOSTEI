import pymysql
import argon2
from pymysql import Connection
from typing import Optional

class UserService:
    def __init__(self, conn: Connection):
        # Сохраняем соединение с БД, которое передаст FastAPI
        self.connection = conn
        # Инициализируем хешер паролей
        self.PH = argon2.PasswordHasher()

    # --- READ (Чтение) ---
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            SELECT
                user_first_name as first_name,
                user_last_name as last_name,
                user_login as login,
                user_email as email,
                user_password_hash as password
            FROM users
            WHERE user_id = %s
            """, (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        return user

    def get_all_users(self) -> list:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            SELECT
                user_first_name as first_name,
                user_last_name as last_name,
                user_login as login,
                user_email as email,
                user_password_hash as password
            FROM users
            """
        )
        users = cursor.fetchmany()
        cursor.close()
        return list(users)

    # --- CREATE (Создание) ---
    def create_user(self, first_name: str, last_name: str, login: str, email: str, password: str) -> dict:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        # Хешируем пароль перед сохранением
        password_hash = self.PH.hash(password)
        
        cursor.execute(
            """
            INSERT INTO users (user_first_name, user_last_name, user_login, user_email, user_password_hash)
            VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, login, email, password_hash)
        )
        self.connection.commit()
        
        # Получаем ID только что созданной записи
        new_id = cursor.lastrowid
        cursor.close()
        
        # Возвращаем созданного пользователя
        return self.get_user_by_id(new_id)

    # --- UPDATE (Полное обновление - PUT) ---
    def update_user(self, user_id: int, first_name: str, last_name: str, login: str, email: str, password: str) -> Optional[dict]:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        
        # Проверяем, существует ли пользователь
        if self.get_user_by_id(user_id) is None:
            cursor.close()
            return None
        
        password_hash = self.PH.hash(password)
        cursor.execute(
            """
            UPDATE users
            SET user_first_name = %s, user_last_name = %s, user_login = %s, user_email = %s, user_password_hash = %s
            WHERE user_id = %s
            """, (first_name, last_name, login, email, password_hash, user_id)
        )
        self.connection.commit()
        cursor.close()
        
        return self.get_user_by_id(user_id)

    # --- PATCH (Частичное обновление) ---
    def patch_user(self, user_id: int, fields: dict) -> Optional[dict]:
        # Оставляем только те поля, которые были переданы
        fields = {k: v for k, v in fields.items() if v is not None}
        
        if not fields:
            return self.get_user_by_id(user_id)
            
        if self.get_user_by_id(user_id) is None:
            return None

        # Маппинг полей из Python в колонки БД
        column_map = {
            "first_name": "user_first_name",
            "last_name": "user_last_name",
            "login": "user_login",
            "email": "user_email",
            "password": "user_password_hash",
        }

        set_parts = []
        values = []
        for key, value in fields.items():
            # Если меняем пароль — его тоже нужно захешировать
            if key == "password":
                value = self.PH.hash(value)
            set_parts.append(f"{column_map[key]} = %s")
            values.append(value)
            
        values.append(user_id)

        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        # Собираем динамический SQL-запрос только для изменяемых полей
        cursor.execute(f"UPDATE users SET {', '.join(set_parts)} WHERE user_id = %s", tuple(values))
        self.connection.commit()
        cursor.close()
        
        return self.get_user_by_id(user_id)

    # --- DELETE (Удаление) ---
    def delete_user(self, user_id: int) -> bool:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        self.connection.commit()
        
        # Если удалилась хотя бы одна строка (rowcount > 0), возвращаем True
        deleted = cursor.rowcount > 0
        cursor.close()
        return deleted