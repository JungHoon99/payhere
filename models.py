from sqlalchemy import Column, String, BigInteger, INTEGER, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable
from sqlalchemy import create_engine
from sqlalchemy import text


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    email = Column(String(50), nullable=False, unique=True)
    pw = Column(String(70), nullable=False)


class Account(Base):
    __tablename__ = "account"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    price = Column(INTEGER)
    memo = Column(String(200))
    date = Column(String(10))
    register_at = Column(DateTime(timezone=True), server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

class BlackList(Base):
    __tablename__ = "black_list"

    token = Column(String(200), nullable=False, primary_key=True)
    end_at = Column(DateTime, nullable=False, primary_key=True)

if __name__ == '__main__':
    
    DB_URL = 'mysql+pymysql://root:kmk20216*@127.0.0.1:3306/payhere'
    engine = create_engine(DB_URL, pool_recycle = 500)
    Base.metadata.create_all(engine)

    for table in Base.metadata.tables.values():
        _statements = CreateTable(table).compile(dialect=mysql.dialect())
        print(_statements)