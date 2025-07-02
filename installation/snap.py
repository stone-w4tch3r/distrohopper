from dataclasses import dataclass
from common import OS

@dataclass(frozen=True)
class Snap:
    PackageName: str
    Version: str | None = None

    @property
    def os(self) -> list[OS]: return [OS.ubuntu, OS.debian, OS.fedora]

    @property
    def name(self) -> str: return self.PackageName
