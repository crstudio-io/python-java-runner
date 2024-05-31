import os
import subprocess


def compile_java(java_fname, packages: list = None):
    command = "javac "
    if packages is not None:
        package_str = ""
        for package in packages:
            package_str += str(package).strip() + "/"
        command += package_str

    command += java_fname
    print(command)

    subprocess.run(command, shell=True)


if __name__ == '__main__':
    create = True
    test_file = "Main.java"
    test_javafile = os.path.basename(test_file)
    test_classfile = os.path.splitext(test_file)[0] + ".class"
    test_packages = test_file.split("/")[:-1] if "/" in test_file else None

    print(test_file)
    print(test_classfile)
    print(test_packages)

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

    compile_java(test_javafile, test_packages)
    print(os.path.exists(test_classfile))
    os.remove(test_classfile)
    os.remove(test_file)
