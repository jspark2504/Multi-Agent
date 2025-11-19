# infrastructure/repository/account_repository.py

from typing import Optional
from account.domain.account import Account


class AccountRepository:
    def find_by_google_sub(self, google_sub: str) -> Optional[Account]:
        raise NotImplementedError

    def find_by_nickname(self, nickname: str) -> Optional[Account]:
        raise NotImplementedError

    def save(self, account: Account) -> Account:
        raise NotImplementedError
