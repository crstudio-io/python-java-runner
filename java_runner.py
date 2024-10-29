import os
import subprocess
from logger import get_logger
from runner import CodeRunner, RunResult

logger = get_logger("java_runner")


class JavaRunner(CodeRunner):
    def __init__(self, java_cmd: str, javac_cmd: str):
        super().__init__()
        self.java_cmd = java_cmd
        self.javac_cmd = javac_cmd

    def run(
            self,
            source: str,
            input_data: str,
            output_data: str,
            timeout: int = None,
            memory: int = None,
    ) -> RunResult:
        logger.debug(f"run target: {source}")
        command = f"{self.javac_cmd} {source}"
        logger.debug(f"compile command: {command}")
        compile_result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )
        logger.debug(f"result return code: {compile_result.returncode}")
        logger.debug(f"stderr: {compile_result.stderr.strip()}")
        if compile_result.returncode != 0:
            return RunResult.compile_err(
                stdout=compile_result.stdout.strip(),
                stderr=compile_result.stderr.strip()
            )

        return RunResult.success()


def run_java(
        java_class: str,
        classpath: list = None,
        input_file: str = None,
        input_data: str = None,
        timeout: int = None,
        memory: int = None,
) -> tuple:
    logger.debug(f"run target: {java_class}")
    java_cmd = os.getenv("JAVA_CMD", "java")
    command = f"{java_cmd} "
    if classpath is not None:
        classpath_str = "-cp "
        for path in classpath:
            classpath_str += str(path).strip() + "/"
        command += classpath_str[:-1] + " "
    if memory is not None:
        command += f"-Xmx{memory}m "
    command += java_class
    logger.debug(f"evaluated command: {command}")

    if not input_data and input_file:
        logger.debug("get input from file")
        with open(input_file) as fp:
            input_data = fp.read()
    else:
        logger.debug("get input from args")

    try:
        run_result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            input=input_data,
            timeout=timeout,
        )
        logger.debug(f"result stdout: {run_result.stdout.strip()}")
        logger.debug(f"result stderr: {run_result.stderr.strip()}")
        stdout, stderr = run_result.stdout.strip(), run_result.stderr.strip()
        report = stdout, stderr, "OUT OF MEMORY" if stderr.find("OutOfMemoryError") != -1 else "OK"
    except subprocess.TimeoutExpired:
        report = "", "", "TIMEOUT"

    return report


if __name__ == '__main__':
    create = True
    test_file = "build/0/Main.java"
    test_classfile = os.path.splitext(test_file)[0] + ".class"
    test_packages = test_file.split("/")[:-1] if "/" in test_file else None
    test_classname = test_classfile.split(".")[0]
    if test_packages:
        test_classname = test_classname.split("/")[-1]

    logger.debug(test_file)
    logger.debug(test_packages)
    logger.debug(test_classfile)
    logger.debug(test_classname)

    if create:
        if test_packages:
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, "w") as fp:
            fp.write("""
            import java.util.Scanner;
            
            public class Main {
                public static void main(String[] args) {
                    int[] arr = new int[1024 * 1024 * 32];
                    double[] dArr = new double[1024 * 1024 * 32];
                    String[] strs = new String[1024 * 1024 * 32];
                    Scanner scanner = new Scanner(System.in);
                    System.out.println(scanner.nextLine());
                }
            }
            """)

    java_runner = JavaRunner(java_cmd="java", javac_cmd="javac")
    run_result = java_runner.run(
        test_file,
        input_data=open("test_input.txt").read(),
        output_data="",
        timeout=1000,
        memory=1000,
    )
    logger.debug(f"result.stdout: {run_result.stdout}")
    logger.debug(f"result.stderr: {run_result.stderr}")
    logger.debug(f"result.status: {run_result.status}")
    os.remove(test_classfile)
    os.remove(test_file)
    # subprocess.run(f"{os.getenv('JAVAC_CMD', 'javac')} {test_file}", shell=True)
    # res = run_java(test_classname, classpath=test_packages, input_file="test_input.txt", timeout=1, memory=256)
    # logger.debug("stdout: " + res[0])
    # logger.debug("stderr: " + res[1])
