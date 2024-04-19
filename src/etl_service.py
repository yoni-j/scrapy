import datetime

from pydantic import BaseModel


class OrderItem(BaseModel):
    order_id: int
    order_date: datetime.datetime
    item_name: str
    item_id: int
    price: float
    quantity: float
