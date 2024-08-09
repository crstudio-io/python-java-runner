import os
import json
import pika

from compiler import compile_java
from runner import run_java
from repository import TutorRepo
from logger import get_logger

config = None
config_file = os.getenv("RUNNER_CONF_FILE")
if config_file and os.path.isfile(config_file):
    with open(config_file) as conf_json:
        config = json.load(conf_json)

tutor_repo = TutorRepo(config["db_connection_str"] if config else None)
logger = get_logger("mq_listener")


def callback(ch, method, _, body):
    logger.debug("decode message to json")
    payload = json.loads(body)
    solution_id = payload["id"]
    problem_id = payload["pid"]
    code_payload = payload["code"]

    with tutor_repo() as session:
        session.update_solution_status(solution_id, "GRADING")
        logger.info(f"{solution_id}: acknowledge start grading")
        ch.basic_ack(delivery_tag=method.delivery_tag)

        logger.debug(f"{solution_id}: save code for compilation")
        java_file = f"{solution_id}/Main.java"
        os.makedirs(os.path.dirname(java_file), exist_ok=True)
        with open(f"{solution_id}/Main.java", "w") as fp:
            fp.writelines(code_payload)

        logger.debug(f"{solution_id}: compile java")
        compile_result = compile_java(java_file)
        logger.info(f"{solution_id}: compilation exit code - {compile_result[0]}")
        if compile_result[0] != 0:
            logger.warning(f"{solution_id}: compile error")
            session.update_solution_status(solution_id, "ERROR")
            return

        logger.debug(f"{solution_id}: retrieve test cases")
        test_cases = session.find_test_cases(problem_id).all()
        total = len(test_cases)
        correct = 0
        for test_case in test_cases:
            input_data = test_case.input
            run_result = run_java("Main", [solution_id], input_data=input_data)
            logger.debug(f"{solution_id}: result: " + run_result[0].rstrip())
            logger.debug(f"{solution_id}: expected: " + str(test_case.output).rstrip())
            correct += 1 if run_result[0].rstrip() == str(test_case.output).rstrip() else 0
        score = int(correct / total * 100)
        logger.info(f"{solution_id}: score - {score}")
        session.update_solution_score(solution_id, score)


if __name__ == '__main__':
    rabbit_host = os.getenv("RABBIT_HOST", "localhost")
    rabbit_port = os.getenv("RABBIT_PORT", 5672)
    rabbit_user = os.getenv("RABBIT_PORT", "user")
    rabbit_password = os.getenv("RABBIT_PASSWORD", "password")
    rabbit_queue = os.getenv("RABBIT_QUEUE_NAME", "java_runner_queue")
    if config and "rabbitmq" in config.keys():
        logger.info("using config from file: " + config_file)
        rabbit_config = config["rabbitmq"]
        rabbit_host = rabbit_config.get("host", rabbit_host)
        rabbit_port = rabbit_config.get("port", rabbit_port)
        rabbit_user = rabbit_config.get("user", rabbit_user)
        rabbit_password = rabbit_config.get("password", rabbit_password)
        rabbit_queue = rabbit_config.get("queue_name", rabbit_queue)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbit_host,
        port=rabbit_port,
        credentials=pika.credentials.PlainCredentials(
            username=rabbit_user,
            password=rabbit_password,
        ),
    ))

    channel = connection.channel()
    channel.queue_declare(queue=rabbit_queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=rabbit_queue,
        on_message_callback=callback
    )

    try:
        logger.info("Start waiting for messages")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutdown")
        exit(0)
