from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class TxtEdit:
    EditAction: Callable[[str], str]