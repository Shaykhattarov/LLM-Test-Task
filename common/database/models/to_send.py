from .base import BaseModel

import datetime
from typing import Optional
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



class ToSendModel(BaseModel):
    __tablename__ = "to_send"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("generated_answers.id"), nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    
    def __repr__(self):
        return "ToSendModel(id=%d, answer_id=%d)" % (self.id, self.answer_id)
