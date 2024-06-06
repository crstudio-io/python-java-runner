import os
import json
import pika

from compiler import compile_java
from runner import run_java
from repository import TutorRepo


tutor_repo = TutorRepo()


def callback(ch, method, properties, body):
    print("decode message to json")
    payload = json.loads(body)
    solution_id = payload["id"]
    problem_id = payload["pid"]
    code_payload = payload["code"]

    print("save code for compilation")
    java_file = f"{solution_id}/Main.java"
    os.makedirs(os.path.dirname(java_file), exist_ok=True)
    with open(f"{solution_id}/Main.java", "w") as fp:
        fp.writelines(code_payload)

    print("compile java")
    compile_result = compile_java(java_file)
    print(compile_result[0])

    with tutor_repo() as session:
        test_cases = session.find_test_cases(problem_id)
        correct = 0
        for test_case in test_cases:
            input_data = test_case.input
            run_result = run_java("Main", [solution_id], input_data=input_data)
            correct += 1 if run_result[0].rstrip() == str(test_case.output).rstrip() else 0
        print(correct)

    print("acknowledge")
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=pika.credentials.PlainCredentials(
            username="user",
            password="password",
        ),
    ))

    channel = connection.channel()
    channel.queue_declare(queue="java_runner_queue", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="java_runner_queue",
        on_message_callback=callback
    )

    try:
        print("Start waiting for messages")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Shutdown")
        exit(0)
