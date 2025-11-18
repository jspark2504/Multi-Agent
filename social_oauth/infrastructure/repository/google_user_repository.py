from typing import Optional

from social_oauth.domain.google_user import GoogleUser

class GoogleUserRepository:

    def __init__(self):
        # { google_sub: GoogleUser 인스턴스 }
        self.users: dict[str, GoogleUser] = {}

    def find_by_google_sub(self, google_sub: str) -> Optional[GoogleUser]:
        return self.users.get(google_sub)

    def create(self, google_sub: str, email: str, name: Optional[str] = None) -> GoogleUser:
        google_user = GoogleUser(sub=google_sub, email=email, name=name)
        self.users[google_sub] = google_user
        return google_user