from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from models import TestCase

engine = create_engine("postgresql://tutor:password@localhost/tutor")

if __name__ == '__main__':
    SessionMaker = sessionmaker(autoflush=True, bind=engine)
    with SessionMaker() as session:
        statement = select(TestCase).where(TestCase.id.__eq__(1))
        print(session.scalar(statement).input)

