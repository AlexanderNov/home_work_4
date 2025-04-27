from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import declarative_base, sessionmaker
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
Base = declarative_base()

engine = create_engine('sqlite:///products.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


class Item(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(String)
    item_url = Column(String)
    datetime = Column(String)


class ItemResponse(BaseModel):
    id: int
    name: str
    price: str
    item_url: str
    datetime: str

    class Config:
        from_attributes = True


def clean_price_column(column):
    # Удаляем из price все символы кроме цифр и точки
    price_clean = column
    for char in [' ', ',', '₽']:
        price_clean = func.replace(price_clean, char, '')
    return price_clean


@app.get("/items/", response_model=List[ItemResponse])
def get_items(
        skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
        limit: int = Query(10, ge=1, le=100, description="Лимит на количество записей"),
        name: Optional[str] = Query(None, description="Фильтр по названию (частичное совпадение)"),
        min_price: Optional[float] = Query(None, description="Минимальная цена"),
        max_price: Optional[float] = Query(None, description="Максимальная цена"),
        sort_by: Optional[str] = Query(None, pattern="^(name|price)$", description="Поле для сортировки"),
        order: Optional[str] = Query("asc", pattern="^(asc|desc)$", description="Порядок сортировки")
):
    """Получение списка товаров с возможностью фильтрации и сортировки."""
    db = SessionLocal()
    try:
        query = db.query(Item)

        # Фильтрация
        if name:
            query = query.filter(Item.name.contains(name))

        if min_price is not None or max_price is not None:
            # Преобразуем строковые цены в числа для фильтрации
            from sqlalchemy import cast, Float
            price_clean = clean_price_column(Item.price)
            price_as_float = cast(price_clean, Float)

            if min_price is not None:
                query = query.filter(price_as_float >= min_price)
            if max_price is not None:
                query = query.filter(price_as_float <= max_price)

        # Сортировка
        if sort_by:
            if order == "desc":
                query = query.order_by(getattr(Item, sort_by).desc())
            else:
                query = query.order_by(getattr(Item, sort_by))

        items = query.offset(skip).limit(limit).all()

        if not items:
            raise HTTPException(status_code=404, detail="Items not found")

        return items
    finally:
        db.close()


uvicorn.run(app, host='127.0.0.1', port=8000)
