from social_oauth.infrastructure.service.google_oauth2_service import (
    GoogleOAuth2Service,
    GetAccessTokenRequest,
    AccessToken,
)


class GoogleOAuth2UseCase:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            oauth2_service = GoogleOAuth2Service.getInstance()
            cls.__instance = cls(oauth2_service)
        return cls.__instance

    def __init__(self, oauth2_service: GoogleOAuth2Service):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.oauth2_service = oauth2_service
        self._initialized = True

    # 1) Authorization URL 반환
    def get_authorization_url(self) -> str:
        return self.oauth2_service.get_authorization_url()

    # 2) AccessToken 발급 기능
    def issue_access_token(self, state: str, code: str) -> AccessToken:
        req = GetAccessTokenRequest(state=state, code=code)
        return self.oauth2_service.refresh_access_token(req)
