import os
import subprocess
from logger import get_logger


logger = get_logger("runner")


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
            """)
    subprocess.run(f"{os.getenv('JAVAC_CMD', 'javac')} {test_file}", shell=True)
    res = run_java(test_classname, classpath=test_packages, input_file="test_input.txt", timeout=1, memory=256)
    logger.debug("stdout: " + res[0])
    logger.debug("stderr: " + res[1])
    os.remove(test_classfile)
    os.remove(test_file)
