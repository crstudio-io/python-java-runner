import time
from dataclasses import dataclass

from sqlalchemy import create_engine, select, ScalarResult
from sqlalchemy.orm import sessionmaker

from models import TestCase, Problem, Solution, SolutionCase
from logger import get_logger


logger = get_logger("repository")


def retry_options(tries=3, step=1):
    def decorator(func):
        def logic(*args, **kwargs):
            for i in range(tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warn(f"{e}, retry in {(i + 1) * 1}s")
                    time.sleep((i + 1) * step)

            raise Exception()

        return logic

    return decorator


class TutorRepo:
    def __init__(self, connection_str: str = None):
        engine = create_engine("postgresql://tutor:password@localhost/tutor" if connection_str is None else connection_str)
        self.session_maker = sessionmaker(
            autoflush=True,
            bind=engine
        )
        self.session = None

    def __call__(self):
        self.session = self.session_maker()
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session = None

    @retry_options(tries=3, step=1)
    def find_restrictions(self, prob_id: int) -> tuple:
        statement = select(Problem).where(Problem.id == prob_id)
        problem = self.session.scalar(statement)
        return problem.timeout, problem.memory

    @retry_options(tries=3, step=1)
    def find_test_cases(self, prob_id: int) -> ScalarResult[TestCase]:
        statement = select(TestCase).where(TestCase.prob_id == prob_id)
        test_cases = self.session.scalars(statement)
        return test_cases

    @retry_options(tries=3, step=1)
    def update_solution_status(self, sol_id: int, status: str):
        solution = self.session.scalar(select(Solution).where(Solution.id == sol_id))
        solution.status = status
        self.session.commit()

    @retry_options(tries=3, step=1)
    def update_solution(self, sol_id: int, score: int, status: str):
        solution = self.session.scalar(select(Solution).where(Solution.id == sol_id))
        solution.score = score
        solution.status = status
        self.session.commit()

    @dataclass
    class CaseResult:
        sol_id: int
        case_seq: int
        status: str
        details: str

    @retry_options(tries=3, step=1)
    def update_solution_results(self, sol_id: int, score: int, case_results: list[type(CaseResult)]):
        case_res_entities = []
        for case_res in case_results:
            case_res_entities.append(SolutionCase(
                sol_id=case_res.sol_id,
                case_seq=case_res.case_seq,
                status=case_res.status,
                details=case_res.details,
            ))

        solution = self.session.scalar(select(Solution).where(Solution.id == sol_id))
        solution.score = score
        solution.status = "SUCCESS" if score == 100 else "FAIL"
        self.session.add_all(case_res_entities)
        self.session.commit()


if __name__ == '__main__':
    tutor_repo = TutorRepo()
    with tutor_repo() as session:
        restrictions = session.find_restrictions(1)
        logger.debug(restrictions)

        for test_case in session.find_test_cases(1):
            logger.debug(test_case.input)
            logger.debug(test_case.output)
