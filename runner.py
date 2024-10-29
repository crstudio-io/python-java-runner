from abc import ABC, abstractmethod
from enum import Enum


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    COMPILE_ERROR = "COMPILE_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT = "TIMEOUT"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"

    def __str__(self):
        return self.name


class RunResult:
    def __init__(
            self,
            stdout: str = "",
            stderr: str = "",
            status: Status = Status.SUCCESS,
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.status = status

    @staticmethod
    def success():
        return RunResult(status=Status.SUCCESS)

    @staticmethod
    def fail():
        return RunResult(status=Status.FAIL)

    @staticmethod
    def compile_err(stdout: str = "", stderr: str = ""):
        return RunResult(stdout, stderr, Status.COMPILE_ERROR)

    @staticmethod
    def runtime_err(stderr: str = ""):
        return RunResult(stderr=stderr, status=Status.RUNTIME_ERROR)

    @staticmethod
    def timeout():
        return RunResult(status=Status.TIMEOUT)

    @staticmethod
    def oom():
        return RunResult(status=Status.OUT_OF_MEMORY)


class CodeRunner(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(
            self,
            source: str,
            input_data: str,
            output_data: str,
            timeout: int = None,
            memory: int = None,
    ) -> RunResult:
        pass
