from .base import BaseModel

import datetime
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import (
    func,
)
from sqlalchemy.orm import (
    Mapped, 
    mapped_column,
)


class GeneratedAnswerModel(BaseModel):
    __tablename__ = "generated_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey('messages.id'), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    def __repr__(self):
        return "<GeneratedAnswerModel(id=%d, message_id=%d)>" % (self.id, self.message_id)
