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

    def prep(self, source: str):
        logger.debug(f"compile target: {source}")
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
        return compile_result.returncode == 0

    def run(
            self,
            source: str,
            input_data: str,
            output_data: str,
            timeout: int = None,
            memory: int = None,
    ) -> RunResult:
        logger.debug(f"run target: {source}")
        classname = os.path.splitext(source)[0].split("/")[-1]
        classpath = "/".join(source.split("/")[:-1]) if "/" in source else None
        logger.debug(classname)
        logger.debug(classpath)

        command = f"{self.java_cmd} -cp {classpath} "
        if memory is not None:
            command += f"-Xmx{memory}m "
        command += classname
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
        classname = os.path.splitext(source)[0] + ".class"
        os.remove(classname)
        os.rmdir(source[:source.rfind("/")])


if __name__ == '__main__':
    create = True
    test_file = "build/0/Main.java"
    test_classfile = os.path.splitext(test_file)[0] + ".class"
    test_packages = test_file.split("/")[:-1] if "/" in test_file else None
    test_classname = test_classfile.split(".")[0]
    if test_packages:
        test_classname = test_classname.split("/")[-1]
        os.makedirs(os.path.dirname(test_file), exist_ok=True)

    logger.debug(test_file)
    logger.debug(test_packages)
    logger.debug(test_classfile)
    logger.debug(test_classname)

    # SUCCESS
    logger.info("TEST: success")
    with open(test_file, "w") as fp:
        fp.write("""
        import java.util.Scanner;
        public class Main {
            public static void main(String[] args) {
                Scanner scanner = new Scanner(System.in);
                System.out.println(scanner.nextLine());
            }
        }
        """)
    java_runner = JavaRunner(java_cmd="java", javac_cmd="javac")
    if java_runner.prep(test_file):
        result = java_runner.run(
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
    if test_packages:
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w") as fp:
        fp.write("""
        public class Main {
            public static void main(String[] args) {
                System.out.println("hi");
                System.out.println("failed!!!!");
            }
        }
        """)
    java_runner = JavaRunner(java_cmd="java", javac_cmd="javac")
    if java_runner.prep(test_file):
        result = java_runner.run(
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
    logger.info("TEST: compile error")
    if test_packages:
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w") as fp:
        fp.write("""
        public class Main {
            public static void main(String[] args) {
                System.out.println("hi");
                System.out.println("failed!!!!");
            }
        
        """)
    java_runner = JavaRunner(java_cmd="java", javac_cmd="javac")
    if java_runner.prep(test_file):
        result = java_runner.run(
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
    if test_packages:
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w") as fp:
        fp.write("""
        public class Main {
            public static void main(String[] args) {
                int[] a = new int[1];
                a[1] = 10;
            }
        }
        """)
    java_runner = JavaRunner(java_cmd="java", javac_cmd="javac")
    if java_runner.prep(test_file):
        result = java_runner.run(
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
    if test_packages:
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w") as fp:
        fp.write("""
        import java.util.Scanner;

        public class Main {
            public static void main(String[] args) throws InterruptedException {
                while (true) {
                    Thread.sleep(2000);
                }
            }
        }
        """)
    java_runner = JavaRunner(java_cmd="java", javac_cmd="javac")
    if java_runner.prep(test_file):
        result = java_runner.run(
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
    logger.info("TEST: out of memory")
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
    if java_runner.prep(test_file):
        result = java_runner.run(
            test_file,
            input_data="hi\n",
            output_data="hi\n",
            memory=256,
        )
        logger.debug(f"result.stdout: {result.stdout}")
        logger.debug(f"result.stderr: {result.stderr}")
        logger.info(f"result.status: {result.status}")
    else:
        logger.info("COMPILE_ERROR")

    os.remove(test_classfile)
    os.remove(test_file)
