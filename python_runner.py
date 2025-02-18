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

    def prep(self, source: str) -> bool:
        logger.debug(f"check syntax error: {source}")
        try:
            py_compile.compile(source, doraise=True)
        except py_compile.PyCompileError:
            logger.debug("py_compile found syntax error")
            return False
        return True

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

    # FAIL
    logger.info("TEST: failure")
    with open(test_file, "w") as fp:
        fp.write("print('hello world')\n")

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

    # COMPILE
    logger.info("TEST: compile(syntax) error")
    with open(test_file, "w") as fp:
        fp.write("print(input()\n")

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

    # RUNTIME
    logger.info("TEST: runtime exception")
    with open(test_file, "w") as fp:
        fp.write("[0][1]\n")

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

    # TIMEOUT
    logger.info("TEST: timeout")
    with open(test_file, "w") as fp:
        fp.write("import time\nwhile True:\n    time.sleep(1000)\n")

    python_runner = PythonRunner(python_cmd="python3")
    if python_runner.prep(test_file):
        result = python_runner.run(
            test_file,
            input_data="hi\n",
            output_data="hi\n",
            timeout=1,
        )
        logger.debug(f"result.stdout: {result.stdout}")
        logger.debug(f"result.stderr: {result.stderr}")
        logger.info(f"result.status: {result.status}")
    else:
        logger.info("COMPILE_ERROR")

    # OOM
    # TODO
