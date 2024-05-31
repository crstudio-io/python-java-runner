import os
import subprocess


def run_java(java_class: str = "Main"):
    subprocess.run(f"java {java_class}", shell=True)


if __name__ == '__main__':
    with open("Main.java", "w") as f:
        f.write("""
        public class Main {
            public static void main(String[] args) {
                System.out.println("Hello World!");
            }
        }
        """)
    subprocess.run(f"javac Main.java", shell=True)
    run_java()
    os.remove("Main.class")
    os.remove("Main.java")
