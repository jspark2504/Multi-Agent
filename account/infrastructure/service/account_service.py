from typing import Optional

from account.application.port.account_repository_port import AccountRepositoryPort
from account.domain.account import Account
from account.infrastructure.repository.account_repository_impl import AccountRepositoryImpl


class AccountService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            repo = AccountRepositoryImpl()
            cls.__instance = cls(repo)
        return cls.__instance

    def __init__(self, account_repo: AccountRepositoryPort):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.account_repo = account_repo
        self._initialized = True

    def get_account_by_google_sub(self, google_sub: str) -> Optional[Account]:
        return self.account_repo.find_by_google_sub(google_sub)

    def is_nickname_available(self, nickname: str) -> bool:
        existing = self.account_repo.find_by_nickname(nickname)
        return existing is None

    def set_nickname_once(self, google_sub: str, nickname: str) -> Account:
        # 1) 닉네임 중복 체크
        existing_nick = self.account_repo.find_by_nickname(nickname)
        if existing_nick:
            raise ValueError("이미 사용 중인 닉네임입니다.")

        # 2) 계정 조회
        account = self.account_repo.find_by_google_sub(google_sub)

        # 이미 닉네임이 있는 경우 → 변경 불가
        if account and account.nickname:
            raise ValueError("이미 닉네임이 설정되어 있어 변경할 수 없습니다.")

        if account is None:
            account = Account(id=None, google_sub=google_sub, nickname=None)

        # 도메인 규칙 통해 닉네임 설정
        account.set_nickname(nickname)

        return self.account_repo.save(account)
