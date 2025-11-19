from typing import Optional

from social_oauth.domain.google_user import GoogleUser

class GoogleUserRepository:

    def find_by_google_sub(self, google_sub: str) -> Optional[GoogleUser]:
        raise NotImplementedError

    def create(self, google_sub: str, email: str, name: Optional[str] = None) -> GoogleUser:
        raise NotImplementedError