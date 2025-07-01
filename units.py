from abc import abstractmethod, ABC


class _IUnit(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
