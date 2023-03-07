import asyncio

from sqlalchemy import Column, Integer, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


PG_DSN = 'postgresql+asyncpg://postgres:1@localhost:5432/async_netology'

engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class SwapiPeople(Base):

    __tablename__ = 'swapi_people'

    id = Column(Integer, primary_key=True, autoincrement=True)
    json = Column(JSON)


if __name__ == '__main__':
    with Session() as session:
        for item in session.query(SwapiPeople).all():
            print(item)
