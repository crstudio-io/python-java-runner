# to convert code to json payload for testing
import json

target = """
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println(scanner.nextLine());
    }
}
"""

print(json.dumps({
    "id": 0,
    "pid": 0,
    "code": target
}))
