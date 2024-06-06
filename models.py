from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class TestCase(Base):
    __tablename__ = "test_case"
    id: Mapped[int] = mapped_column(primary_key=True)
    prob_id: Mapped[int] = mapped_column(ForeignKey("problem.id"))
    problem: Mapped["Problem"] = relationship(back_populates="test_cases")
    input: Mapped[str] = mapped_column(Text())
    output: Mapped[str] = mapped_column(Text())


class Problem(Base):
    __tablename__ = "problem"
    id: Mapped[int] = mapped_column(primary_key=True)
    prob_desc: Mapped[str] = mapped_column(Text())
    input_desc: Mapped[str] = mapped_column(Text())
    output_desc: Mapped[str] = mapped_column(Text())
    timeout: Mapped[int] = mapped_column(Integer())
    memory: Mapped[int] = mapped_column(Integer())
    test_cases: Mapped[List["TestCase"]] = relationship(back_populates="problem")


class Solution(Base):
    __tablename__ = "solution"
    id: Mapped[int] = mapped_column(primary_key=True)
    prob_id: Mapped[int] = mapped_column(ForeignKey("problem.id"))
    lang: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(Text())
    score: Mapped[int] = mapped_column(Integer())
