from .base import BaseModel

import datetime
from typing import get_args, Literal
from sqlalchemy import (
    Enum,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.sql import (
    func,
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
)


MessageStatus = Literal["new", "pending", "ready", "send"]


class MessageModel(BaseModel):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(Enum(
        *get_args(MessageStatus),
        name="messagestatus",
        create_constraint=True,
        validate_string=True,
    ))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    def __repr__(self):
        return "<MessageModel(user_id=%d, status=%s)>" % (self.user_id, self.status)
