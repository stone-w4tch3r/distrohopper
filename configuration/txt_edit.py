from typing import Callable
from pyinfra_lib import modify_file

class TxtEdit:
    def __init__(self, Path: str, EditAction: Callable[[str], str]):
        modify_file.modify_plaintext_file(
            path=Path,
            modify_action=EditAction
        )