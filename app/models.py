from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, func
from app.database import Base
from datetime import datetime

class URLMapper(Base):
    __tablename__ = "url_mapper"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_code: Mapped[str | None] = mapped_column(String(4), unique=True, index=True)
    long_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())