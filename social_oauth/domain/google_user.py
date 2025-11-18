from typing import Optional
from datetime import datetime

class GoogleUser:
    def __init__(self, sub: str, email: str, name: Optional[str] = None):
        self.sub: str = sub        # Google의 sub를 PK처럼 사용
        self.email = email
        self.name = name
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()

    def __repr__(self) -> str:
        return f"GoogleUser(sub={self.sub}, email={self.email}, name={self.name})"

    def update_name(self, name: str):
        self.name = name
        self.updated_at = datetime.utcnow()

    def update_email(self, email: str):
        self.email = email
        self.updated_at = datetime.utcnow()