from .base import BaseModel

import datetime
from sqlalchemy import (
    Integer,
    String,
    DateTime
)
from sqlalchemy.sql import (
    func,
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
)



class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) 
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at = Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self):
        return "<UserModel(id=%d, name=%s, telegram_id=%s, login=%s)>" % (
            self.id,
            self.name,
            self.telegram_id,
            self.login,
        )
