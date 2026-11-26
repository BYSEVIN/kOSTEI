from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from pymysql import Connection

from application.services.menu_service import MenuService
from infrastructure.db.mysql import mysql_conn

router = APIRouter(prefix="/menu", tags=["menu"])


# --- Pydantic модели ---
class MenuItemCreate(BaseModel):
    menu_item_name: str
    menu_item_link: Optional[str] = None
    menu_item_order: int = 0
    menu_item_parent_id: Optional[int] = None
    icon_name: Optional[str] = None
    menu_item_is_hidden: bool = False
    menu_item_description: Optional[str] = None
    menu_item_sidebar_hidden: Optional[bool] = None


class MenuItemUpdate(BaseModel):
    menu_item_name: Optional[str] = None
    menu_item_link: Optional[str] = None
    menu_item_order: Optional[int] = None
    menu_item_parent_id: Optional[int] = None
    icon_name: Optional[str] = None
    menu_item_is_hidden: Optional[bool] = None
    menu_item_description: Optional[str] = None
    menu_item_sidebar_hidden: Optional[bool] = None


@router.get("/")
async def get_all_menu_items(conn: Connection = Depends(mysql_conn)):
    service = MenuService(conn)
    items = service.get_all_items()
    return {"items": items}


@router.post("/")
async def create_menu_item(item: MenuItemCreate, conn: Connection = Depends(mysql_conn)):
    service = MenuService(conn)
    new_item = service.create_item(item.model_dump())
    return {"item": new_item}


@router.put("/{item_id}")
async def update_menu_item(item_id: int, item: MenuItemUpdate, conn: Connection = Depends(mysql_conn)):
    service = MenuService(conn)
    # exclude_unset=True означает, что мы обновляем только те поля, которые были переданы
    updated = service.update_item(item_id, item.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"item": updated}


@router.delete("/{item_id}")
async def delete_menu_item(item_id: int, conn: Connection = Depends(mysql_conn)):
    service = MenuService(conn)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"detail": "Menu item deleted successfully"}