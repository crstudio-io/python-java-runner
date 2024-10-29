import os
from abc import ABC, abstractmethod
from enum import Enum

from logger import get_logger

logger = get_logger("runner")


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
    def __init__(self, source_name: str,):
        self.source_name = source_name

    def save(self, build_dir: str, source_str: str,) -> str:
        os.makedirs(build_dir, exist_ok=True)
        filename = os.path.join(build_dir, self.source_name)
        filename = filename.replace("\\", "/")
        with open(filename, "w") as fp:
            fp.writelines(source_str)
        logger.info(f"save to: {filename}")
        return filename

    @abstractmethod
    def prep(self, source: str) -> bool:
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

    @abstractmethod
    def cleanup(self, source: str):
        pass
