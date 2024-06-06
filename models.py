from sqlalchemy import BigInteger, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TestCase(Base):
    __tablename__ = "test_case"
    id: Mapped[int] = mapped_column(primary_key=True)
    prob_id: Mapped[int] = mapped_column(BigInteger())
    input: Mapped[str] = mapped_column(Text())
    output: Mapped[str] = mapped_column(Text())
