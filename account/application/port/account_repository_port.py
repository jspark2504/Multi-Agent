from abc import ABC, abstractmethod
from typing import Optional

from account.domain.account import Account


class AccountRepositoryPort(ABC):

    @abstractmethod
    def find_by_google_sub(self, google_sub: str) -> Optional[Account]:
        pass

    @abstractmethod
    def find_by_nickname(self, nickname: str) -> Optional[Account]:
        pass

    @abstractmethod
    def save(self, account: Account) -> Account:
        pass
