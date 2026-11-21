from infrastructure.db.mysql import mysql_conn

print("Пытаемся подключиться к базе данных...")

# Получаем генератор соединения
gen = mysql_conn()
try:
    # Достаем само соединение
    conn = next(gen)
    print("✅ Успешно подключено!")
    
    # Выполняем простой запрос для проверки таблицы
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()
        print(f"📊 Количество пользователей в таблице 'users': {count[0]}")
        
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
finally:
    # Закрываем соединение, чтобы не оставлять висящих процессов
    try:
        next(gen)
    except StopIteration:
        pass