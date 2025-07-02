from abc import ABC, abstractmethod
from typing import List
from common import OS

class Installation(ABC):
    @property
    @abstractmethod
    def os(self) -> list[OS]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
