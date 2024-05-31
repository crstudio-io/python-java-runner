import os
import subprocess


def run_java(java_class, packages: list = None, input_file: str = None) -> tuple:
    command = "java "
    if packages is not None:
        package_str = "-cp "
        for package in packages:
            package_str += str(package).strip() + "/"
        command += package_str[:-1] + " "
    command += java_class
    input_data = None
    if input_file:
        with open(input_file) as fp:
            input_data = fp.read()

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        input=input_data
    )

    return result.stdout.strip(), result.stderr.strip()


if __name__ == '__main__':
    create = True
    test_file = "Main.java"
    test_classfile = os.path.splitext(test_file)[0] + ".class"
    test_packages = test_file.split("/")[:-1] if "/" in test_file else None
    test_classname = test_classfile.split(".")[0]
    if test_packages:
        test_classname = test_classname.split("/")[-1]

    print(test_file)
    print(test_packages)
    print(test_classfile)
    print(test_classname)

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
    result = run_java(test_classname, packages=test_packages, input_file="test_input.txt")
    print("stdout: " + result[0])
    print("stderr: " + result[1])
    os.remove(test_classfile)
    os.remove(test_file)
