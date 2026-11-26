from typing import Optional, List
import pymysql
from pymysql import Connection


class MenuService:
    def __init__(self, conn: Connection):
        self.connection = conn

    def get_all_items(self) -> List[dict]:
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT menu_item_id, menu_item_name, menu_item_link, menu_item_order, 
                   menu_item_parent_id, icon_name, menu_item_is_hidden, 
                   menu_item_description, menu_item_sidebar_hidden 
            FROM menu_items 
            ORDER BY menu_item_order ASC
        """)
        items = cursor.fetchall()
        cursor.close()
        return list(items)

    def get_item_by_id(self, item_id: int) -> Optional[dict]:
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM menu_items WHERE menu_item_id = %s", (item_id,))
        item = cursor.fetchone()
        cursor.close()
        return item

    def create_item(self, data: dict) -> dict:
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            INSERT INTO menu_items (
                menu_item_name, menu_item_link, menu_item_order, 
                menu_item_parent_id, icon_name, menu_item_is_hidden, 
                menu_item_description, menu_item_sidebar_hidden
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("menu_item_name"), 
            data.get("menu_item_link"), 
            data.get("menu_item_order", 0),
            data.get("menu_item_parent_id"), 
            data.get("icon_name"), 
            int(data.get("menu_item_is_hidden", False)),
            data.get("menu_item_description"), 
            int(data.get("menu_item_sidebar_hidden", False)) if data.get("menu_item_sidebar_hidden") is not None else None
        ))
        self.connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return self.get_item_by_id(new_id)

    def update_item(self, item_id: int, data: dict) -> Optional[dict]:
        if self.get_item_by_id(item_id) is None:
            return None

        if not data:
            return self.get_item_by_id(item_id)

        set_parts = []
        values = []
        for key, value in data.items():
            if isinstance(value, bool):
                value = int(value)  # Конвертируем bool в int для базы
            set_parts.append(f"{key} = %s")
            values.append(value)
            
        values.append(item_id)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"UPDATE menu_items SET {', '.join(set_parts)} WHERE menu_item_id = %s", tuple(values))
        self.connection.commit()
        cursor.close()
        return self.get_item_by_id(item_id)

    def delete_item(self, item_id: int) -> bool:
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("DELETE FROM menu_items WHERE menu_item_id = %s", (item_id,))
        self.connection.commit()
        deleted = cursor.rowcount > 0
        cursor.close()
        return deleted