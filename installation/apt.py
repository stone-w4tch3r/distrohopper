from dataclasses import dataclass
from common import OS, URL
from installation.abstract import Installation

@dataclass(frozen=True)
class AptRepo:
    KeyUrl: str
    RepoSourceStr: str
    """apt source string, e.g. `deb https://download.virtualbox.org/virtualbox/debian bionic contrib`"""

    def __post_init__(self):
        if not URL.is_valid(self.KeyUrl):
            raise ValueError(f"Invalid URL [{self.KeyUrl}]")

@dataclass(frozen=True)
class AptPpa:
    PpaStr: str
    """ppa formatted string, e.g. `ppa:mozillateam/ppa`"""

@dataclass(frozen=True)
class Apt(Installation):
    PackageName: str
    RepoOrPpa: AptRepo | AptPpa | None = None
    Version: str | None = None

    @property
    def os(self) -> list[OS]:
        return [OS.ubuntu, OS.debian]

    @property
    def name(self) -> str:
        return self.PackageName
