from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative
from typing import Any

@as_declarative()
class Base:
    id: Any
    __name__: str

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
