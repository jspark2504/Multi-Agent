from datetime import datetime
from typing import Optional


class Account:
    def __init__(
        self,
        id: Optional[int],
        google_sub: str,
        nickname: Optional[str],
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.google_sub = google_sub
        self.nickname = nickname
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def set_nickname(self, nickname: str):
        # 한 번 설정되면 변경 불가 → 도메인에서 방어
        if self.nickname:
            raise ValueError("이미 닉네임이 설정되어 있습니다.")
        self.nickname = nickname
        self.updated_at = datetime.utcnow()
