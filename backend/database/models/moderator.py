from .base import BaseModel

import datetime
from typing import Optional
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



class ModeratorModel(BaseModel):
    __tablename__ = "moderators"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at = Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self):
        return "<ModeratorModel(id=%d, login=%s)" % (self.id, self.login)