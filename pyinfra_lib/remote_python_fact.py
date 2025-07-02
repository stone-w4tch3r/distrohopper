from pyinfra import logger
from pyinfra.api import FactBase

from remote_python_util import InterpreterInfo, PythonVersion


class PythonInterpreters(FactBase[list[InterpreterInfo]]):
    """
    Returns information about Python interpreters available on the remote host.
    osX, linux and *BSD are supported.

    + additional_directories: Additional directories to search for Python interpreters
    """

    _directories_to_search = [
        # linux:
        "/usr/bin",
        "/usr/local/bin",
        "/opt/local/bin"
        # macos:
        # todo: check
        "/Library/Frameworks/Python.framework/Versions/*/bin",  # python.org
        "/System/Library/Frameworks/Python.framework/Versions/*/bin",  # apple
        "/xxx"  # brew?
    ]

    shell_executable = "sh"

    def command(self, additional_directories: list[str] = None):
        if additional_directories is None:
            additional_directories = []
        directories = " ".join(self._directories_to_search + additional_directories)
        return f"""
        directories="{directories}"

        for dir in $directories; do
            if [ -d "$dir" ]; then
                for python_interpreter in "$dir"/python*; do
                    version=$("$python_interpreter" --version 2>&1)
                    if echo "$version" | grep "^Python" >/dev/null; then
                        echo "$python_interpreter $version"
                    fi
                done
            fi
        done
        """

    @staticmethod
    def default() -> list[InterpreterInfo]:
        return []

    def process(self, output) -> list[InterpreterInfo]:
        pythons = []
        for line in output:
            path = line.split(" ")[0]
            version_str = line.split(" ")[-1]
            try:
                version = PythonVersion(version_str)
            except ValueError:
                logger.warning(f"Suspicious Python version [{version_str}] for [{path}]. Skipping.")
                continue

            pythons.append(InterpreterInfo(version, path))

        return pythons
