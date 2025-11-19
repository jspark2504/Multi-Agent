from typing import Optional
from config.redis_config import get_redis

redis_client = get_redis()

# 추후 리팩토링 대상 ☆
def get_google_sub_from_session(session_id: Optional[str]) -> Optional[str]:
    """
    쿠키에서 가져온 session_id로 Redis에서 google_sub 조회.
    - session_id 없으면 None
    - Redis에 session:{id} 없으면 None
    - 있으면 str(sub) 반환
    """
    if not session_id:
        return None

    session_key = f"session:{session_id}"
    google_sub = redis_client.get(session_key)

    if not google_sub:
        return None

    if isinstance(google_sub, bytes):
        google_sub = google_sub.decode()

    return google_sub
