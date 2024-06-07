import os
import subprocess

from logger import get_logger


logger = get_logger("runner")


def run_java(java_class: str, classpath: list = None, input_file: str = None, input_data: str = None) -> tuple:
    logger.debug(f"run target: {java_class}")
    command = "java "
    if classpath is not None:
        classpath_str = "-cp "
        for path in classpath:
            classpath_str += str(path).strip() + "/"
        command += classpath_str[:-1] + " "
    command += java_class
    logger.debug(f"evaluated command: {command}")

    if not input_data and input_file:
        logger.debug("get input from file")
        with open(input_file) as fp:
            input_data = fp.read()
    else:
        logger.debug("no input")

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        input=input_data
    )
    logger.debug(f"result stdout: {result.stdout.strip()}")
    logger.debug(f"result stderr: {result.stderr.strip()}")

    return result.stdout.strip(), result.stderr.strip()


if __name__ == '__main__':
    create = True
    test_file = "0/Main.java"
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
                    System.out.println("Hello World!");
                    Scanner scanner = new Scanner(System.in);
                    System.out.println(scanner.nextLine());
                    System.out.println(scanner.nextLine());
                    System.out.println(scanner.nextLine());
                    // throw new RuntimeException();
                }
            }
            """)
    subprocess.run(f"javac {test_file}", shell=True)
    res = run_java(test_classname, classpath=test_packages, input_file="test_input.txt")
    logger.debug("stdout: " + res[0])
    logger.debug("stderr: " + res[1])
    os.remove(test_classfile)
    os.remove(test_file)
