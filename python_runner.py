import os
import py_compile
import subprocess

from logger import get_logger
from runner import CodeRunner, RunResult

logger = get_logger("python_runner")


class PythonRunner(CodeRunner):
    def __init__(self, python_cmd: str):
        super().__init__(source_name="main.py")
        self.python_cmd = python_cmd
        # self.py_compile = self.python_cmd + " -m py_compile"

    def prep(self, source: str) -> bool:
        logger.debug(f"check syntax error: {source}")
        try:
            py_compile.compile(source, doraise=True)
        except py_compile.PyCompileError:
            logger.debug("py_compile found syntax error")
            return False

        return True
        # command = f"{self.py_compile} {source}"
        # logger.debug(f"py_compile: {command}")
        # compile_result = subprocess.run(
        #     command.split(" "),
        #     shell=True,
        #     capture_output=True,
        #     text=True,
        # )
        # logger.debug(f"result return code: {compile_result.returncode}")
        # logger.debug(f"stderr: {compile_result.stderr.strip()}")
        # return compile_result.returncode == 0

    def run(
            self,
            source: str,
            input_data: str,
            output_data: str,
            timeout: int = None,
            memory: int = None
    ) -> RunResult:
        logger.debug(f"run target: {source}")
        command = []
        if memory is not None:
            command.extend([
                "prlimit",
                f"--as={memory * 1024 * 1024}",
                "--pid",
                "$$",
                "&&",
            ])
        command.append(self.python_cmd)
        command.append(source)
        logger.debug(f"run command: {command}")

        try:
            run_result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                input=input_data,
                timeout=timeout,
            )

            stdout, stderr = run_result.stdout.strip(), run_result.stderr.strip()
            logger.debug(f"result stdout: {stdout}")
            logger.debug(f"result stderr: {stderr}")
            if stderr.find("OutOfMemoryError") != -1:
                return RunResult.oom()
            if stderr:
                logger.debug(f"{stderr}")
                return RunResult.runtime_err(stderr=stderr)
            run_output = stdout, stderr
        except subprocess.TimeoutExpired:
            return RunResult.timeout()

        if run_output[0] != output_data.strip():
            logger.debug(f"stdin: {input_data}")
            logger.debug(f"stdout: {run_output[0]}")
            logger.debug(f"expected: {output_data.strip()}")
            return RunResult.fail()
        return RunResult.success()


    def cleanup(self, source: str):
        os.remove(source)
        os.rmdir(source[:source.rfind("/")])


if __name__ == '__main__':
    create = True
    test_file = "build/0/main.py"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)

    # SUCCESS
    logger.info("TEST: success")
    with open(test_file, "w") as fp:
        fp.write("print(input())\n")

    python_runner = PythonRunner(python_cmd="python3")
    if python_runner.prep(test_file):
        result = python_runner.run(
            test_file,
            input_data="hi\n",
            output_data="hi\n",
            timeout=5,
        )
        logger.debug(f"result.stdout: {result.stdout}")
        logger.debug(f"result.stderr: {result.stderr}")
        logger.info(f"result.status: {result.status}")
    else:
        logger.info("COMPILE_ERROR")

