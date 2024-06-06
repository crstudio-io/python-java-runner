from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import TestCase, Problem, Solution

engine = create_engine("postgresql://tutor:password@localhost/tutor")

if __name__ == '__main__':
    SessionMaker = sessionmaker(autoflush=True, bind=engine)
    with SessionMaker() as session:
        statement = select(TestCase).where(TestCase.id.__eq__(1))
        print(session.scalar(statement).input)
        statement = select(Problem).where(Problem.id.__eq__(1))
        for test_case in session.scalar(statement).test_cases:
            print(test_case.input)
            print(test_case.output)
