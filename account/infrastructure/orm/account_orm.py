from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from config.database.session import Base


class AccountOrm(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, autoincrement=True)
    google_sub = Column(
        String(255),
        ForeignKey("google_user.sub"),
        nullable=False,
        unique=True,       # 한 구글 계정당 하나의 Account
    )
    nickname = Column(String(50), unique=True, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("nickname", name="uq_account_nickname"),
    )
