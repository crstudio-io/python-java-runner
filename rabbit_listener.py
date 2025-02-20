import json
import os

import pika

from java_runner import JavaRunner
from logger import get_logger
from python_runner import PythonRunner
from repository import TutorRepo
from runner import Status

config = None
config_file = os.getenv("RUNNER_CONF_FILE")
if config_file and os.path.isfile(config_file):
    with open(config_file) as conf_json:
        config = json.load(conf_json)

tutor_repo = TutorRepo(config["db_connection_str"] if config else None)
case_result = TutorRepo.CaseResult
logger = get_logger("mq_listener")


code_runner = JavaRunner(
    java_cmd=os.getenv("JAVA_CMD", "java"),
    javac_cmd=os.getenv("JAVAC_CMD", "javac")
)
# code_runner = PythonRunner(
#     python_cmd="python3"
# )

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
        source_file = code_runner.save(f"build/{solution_id}", code_payload)
        if not code_runner.prep(source_file):
            logger.info(f"{solution_id}: compile error")
            session.update_solution(solution_id, 0, "ERROR")
            code_runner.cleanup(source_file)
            return

        logger.debug(f"{solution_id}: retrieve test cases")
        test_cases = session.find_test_cases(problem_id).all()
        restrictions = session.find_restrictions(problem_id)
        total = len(test_cases)
        correct = 0
        case_results = []
        for idx, test_case in enumerate(test_cases, 1):
            input_data = test_case.input
            logger.debug(input_data)
            run_result = code_runner.run(
                source=source_file,
                input_data=str(test_case.input),
                output_data=str(test_case.output),
                timeout=restrictions[0],
                memory=restrictions[1],
            )

            if run_result.status == Status.SUCCESS:
                correct += 1
            case_results.append(case_result(
                sol_id=solution_id,
                case_seq=idx,
                status=run_result.status.name,
                details=run_result.stderr,
            ))

        score = int(correct / total * 100)
        logger.info(f"{solution_id}: score - {score}")
        session.update_solution_results(solution_id, score, case_results)
        code_runner.cleanup(source_file)


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
