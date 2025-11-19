from account.infrastructure.service.account_service import AccountService
from account.adapter.input.web.response.account_me_response import AccountMeResponse
from account.adapter.input.web.response.nickname_set_response import NicknameSetResponse


class AccountUseCase:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            service = AccountService.getInstance()
            cls.__instance = cls(service)
        return cls.__instance

    def __init__(self, account_service: AccountService):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.account_service = account_service
        self._initialized = True

    def get_my_account(self, google_sub: str) -> AccountMeResponse:
        account = self.account_service.get_account_by_google_sub(google_sub)
        has_nickname = bool(account and account.nickname)

        return AccountMeResponse(
            nickname=account.nickname if account else None,
            has_nickname=has_nickname,
            can_set_nickname=not has_nickname,
        )

    def check_nickname_available(self, nickname: str) -> bool:
        return self.account_service.is_nickname_available(nickname)

    def set_my_nickname(self, google_sub: str, nickname: str) -> NicknameSetResponse:
        account = self.account_service.set_nickname_once(google_sub, nickname)
        return NicknameSetResponse(id=account.id, nickname=account.nickname)
