from sqlmodel import SQLModel, Field
from typing import Optional
from src.models.schemas.elements_enclosure.fav_create import FavCreate


class Fav(FavCreate, table=True):
    __tablename__="favs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int
    type: str