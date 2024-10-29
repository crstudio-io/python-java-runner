from abc import ABC, abstractmethod


class RunResult:
    def __init__(
            self,
            stdout: str,
            stderr: str,
            message: str,
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.message = message


class CodeRunner(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(
            self,
            source: str,
            input_data: str,
            timeout: int = None,
            memory: int = None,
    ) -> RunResult:
        pass
