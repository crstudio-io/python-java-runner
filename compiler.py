import os
import subprocess

from logger import get_logger


logger = get_logger("compiler")


def compile_java(java_fname: str) -> tuple:
    logger.debug(f"process file: {java_fname}")
    javac_cmd = os.getenv("JAVAC_CMD", "javac")
    command = f"{javac_cmd} {java_fname}"
    logger.debug(f"evaluated command: {command}")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    logger.debug(f"result return code: {result.returncode}")
    logger.debug(f"stderr: {result.stderr.strip()}")

    return result.returncode, result.stderr.strip()


if __name__ == '__main__':
    create = True
    test_file = "0/Main.java"
    test_classfile = os.path.splitext(test_file)[0] + ".class"
    test_packages = test_file.split("/")[:-1] if "/" in test_file else None

    if create:
        if test_packages:
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, "w") as f:
            f.write("""
            public class Main {
                public static void main(String[] args) {
                    System.out.println("Hello World!");
                }
            }
            """)

    result = compile_java(test_file)
    logger.debug(f"exit code: {result[0]}")
    logger.debug("stderr: " + result[1])
    if result[0] == 0:
        os.remove(test_classfile)
    os.remove(test_file)
