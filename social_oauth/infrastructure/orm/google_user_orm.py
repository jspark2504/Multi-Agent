from sqlalchemy import Column, String, DateTime, func
from config.database.session import Base   # 네가 만든 Base import

class GoogleUserOrm(Base):
    __tablename__ = "google_user"   # 테이블 이름

    # sub을 PK처럼 쓴다고 했으니 그대로 PK로 사용
    sub = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
